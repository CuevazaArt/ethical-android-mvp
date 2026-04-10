"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
Or: python -m src.runtime  (same server; see docs/RUNTIME_CONTRACT.md)

Checkpoint (optional): KERNEL_CHECKPOINT_PATH, KERNEL_CHECKPOINT_LOAD,
KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT, KERNEL_CHECKPOINT_EVERY_N_EPISODES — see src/persistence/checkpoint.py

Situated v8 (optional): KERNEL_SENSOR_FIXTURE (path to JSON), KERNEL_SENSOR_PRESET (name from
perceptual_abstraction.SENSOR_PRESETS) — merged before client ``sensor`` JSON; see PROPUESTA_ORGANISMO_SITUADO_V8.md.

Multimodal thresholds (optional): KERNEL_MULTIMODAL_AUDIO_STRONG, KERNEL_MULTIMODAL_VISION_SUPPORT,
KERNEL_MULTIMODAL_SCENE_SUPPORT, KERNEL_MULTIMODAL_VISION_CONTRADICT, KERNEL_MULTIMODAL_SCENE_CONTRADICT
— see README / multimodal_trust.thresholds_from_env.

Vitality (optional): KERNEL_VITALITY_CRITICAL_BATTERY, KERNEL_CHAT_INCLUDE_VITALITY — see vitality.py.

Guardian Angel (optional, opt-in): KERNEL_GUARDIAN_MODE=1 enables protective tone in LLM layer only;
KERNEL_CHAT_INCLUDE_GUARDIAN — omit ``guardian_mode`` key from JSON if 0. See guardian_mode.py,
PROPUESTA_ANGEL_DE_LA_GUARDIA.md.

Epistemic dissonance (v9.1): KERNEL_CHAT_INCLUDE_EPISTEMIC — omit ``epistemic_dissonance`` from JSON if 0.
Optional thresholds KERNEL_EPISTEMIC_AUDIO_MIN, KERNEL_EPISTEMIC_MOTION_MAX, KERNEL_EPISTEMIC_VISION_LOW.
See epistemic_dissonance.py, PROPUESTA_CAPACIDAD_AMPLIADA_V9.md.

Advisory telemetry (optional, Fase 1.3–1.4): KERNEL_ADVISORY_INTERVAL_S — positive seconds
spawns a read-only :func:`src.runtime.telemetry.advisory_loop` per WebSocket session (DriveArbiter only).

Privacy (robustez pilar 5): KERNEL_CHAT_EXPOSE_MONOLOGUE — if 0/false/no/off, the ``monologue``
field is omitted from content (empty string) and LLM embellishment is skipped.

Homeostasis UX (pilar 4): KERNEL_CHAT_INCLUDE_HOMEOSTASIS — if 0/false/no/off, omit
``affective_homeostasis`` (σ / strain / PAD advisory; does not change decisions).

Experience digest (pilar 3): KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST — if 0, omit
``experience_digest`` (semantic line from last Ψ Sleep; additive, not a policy change).
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import asdict
from typing import Any, Dict

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse

from .kernel import ChatTurnResult, EthicalKernel
from .modules.internal_monologue import compose_monologue_line
from .persistence.checkpoint import (
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
)
from .modules.affective_homeostasis import homeostasis_telemetry
from .modules.consequence_projection import qualitative_temporal_branches
from .modules.guardian_mode import is_guardian_mode_active
from .modules.perceptual_abstraction import snapshot_from_layers
from .real_time_bridge import RealTimeBridge
from .runtime.telemetry import advisory_interval_seconds_from_env, advisory_loop

app = FastAPI(title="Ethical Android Chat", version="1.0")


def _chat_expose_monologue() -> bool:
    """If false, omit monologue from WebSocket JSON (privacy; skips LLM embellishment)."""
    v = os.environ.get("KERNEL_CHAT_EXPOSE_MONOLOGUE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_homeostasis() -> bool:
    """If false, omit affective_homeostasis (pilar 4 UX telemetry)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_HOMEOSTASIS", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_experience_digest() -> bool:
    """If false, omit experience_digest (pilar 3; updated in Ψ Sleep)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_user_model() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_USER_MODEL", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_chrono() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_CHRONO", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_premise() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_PREMISE", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_teleology() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_TELEOLOGY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_multimodal_trust() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_MULTIMODAL", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_vitality() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_VITALITY", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_guardian() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_GUARDIAN", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_include_epistemic() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_EPISTEMIC", "1").strip().lower()
    return v not in ("0", "false", "no", "off")


def _chat_turn_to_jsonable(r: ChatTurnResult, kernel: EthicalKernel) -> Dict[str, Any]:
    """Compact JSON-safe view (no full internal objects)."""
    idn = kernel.memory.identity
    out: Dict[str, Any] = {
        "blocked": r.blocked,
        "path": r.path,
        "block_reason": r.block_reason,
        "response": {
            "message": r.response.message,
            "tone": r.response.tone,
            "hax_mode": r.response.hax_mode,
            "inner_voice": r.response.inner_voice,
        },
        "identity": {
            **{k: float(v) if k != "episode_count" else int(v) for k, v in asdict(idn.state).items()},
            "ascription": idn.ascription_line(),
        },
        "drive_intents": [
            {"suggest": di.suggest, "reason": di.reason, "priority": di.priority}
            for di in kernel.drive_arbiter.evaluate(kernel)
        ],
    }
    if r.perception:
        p = r.perception
        out["perception"] = {
            "risk": p.risk,
            "urgency": p.urgency,
            "hostility": p.hostility,
            "calm": p.calm,
            "manipulation": p.manipulation,
            "suggested_context": p.suggested_context,
            "summary": p.summary,
        }
    if r.decision is not None:
        d = r.decision
        if _chat_expose_monologue():
            base_mono = compose_monologue_line(d, kernel._last_registered_episode_id)
            out["monologue"] = kernel.llm.optional_monologue_embellishment(base_mono)
        else:
            out["monologue"] = ""
        out["decision"] = {
            "final_action": d.final_action,
            "decision_mode": d.decision_mode,
            "blocked": d.blocked,
        }
        if d.moral:
            out["decision"]["verdict"] = d.moral.global_verdict.value
            out["decision"]["score"] = d.moral.total_score
        if d.affect:
            out["decision"]["affect"] = {
                "pad": list(d.affect.pad),
                "dominant_archetype": d.affect.dominant_archetype_id,
                "weights": d.affect.weights,
            }
        if d.reflection:
            out["decision"]["reflection"] = {
                "conflict_level": d.reflection.conflict_level,
                "pole_spread": d.reflection.pole_spread,
                "strain_index": d.reflection.strain_index,
                "uncertainty": d.reflection.uncertainty,
                "will_mode": d.reflection.will_mode,
                "note": d.reflection.note,
            }
        if d.salience:
            out["decision"]["salience"] = {
                "dominant_focus": d.salience.dominant_focus,
                "weights": d.salience.weights,
                "raw_scores": d.salience.raw_scores,
            }
        if _chat_include_homeostasis():
            out["affective_homeostasis"] = homeostasis_telemetry(d)
    if r.narrative:
        n = r.narrative
        out["narrative"] = {
            "compassionate": n.compassionate,
            "conservative": n.conservative,
            "optimistic": n.optimistic,
            "synthesis": n.synthesis,
        }
    if r.decision is None:
        out["monologue"] = ""
    if _chat_include_experience_digest():
        out["experience_digest"] = kernel.memory.experience_digest
    if _chat_include_user_model():
        out["user_model"] = kernel.user_model.to_public_dict()
    if _chat_include_chrono():
        out["chronobiology"] = kernel.subjective_clock.to_public_dict()
    if _chat_include_premise():
        pa = kernel._last_premise_advisory
        out["premise_advisory"] = {"flag": pa.flag, "detail": pa.detail}
    if _chat_include_multimodal_trust() and r.multimodal_trust is not None:
        mt = r.multimodal_trust
        out["multimodal_trust"] = {
            "state": mt.state,
            "reason": mt.reason,
            "requires_owner_anchor": mt.requires_owner_anchor,
        }
    if _chat_include_vitality():
        out["vitality"] = kernel._last_vitality_assessment.to_public_dict()
    if _chat_include_guardian():
        out["guardian_mode"] = is_guardian_mode_active()
    if _chat_include_epistemic() and r.epistemic_dissonance is not None:
        out["epistemic_dissonance"] = r.epistemic_dissonance.to_public_dict()
    if (
        _chat_include_teleology()
        and r.decision is not None
        and r.perception is not None
    ):
        v = (
            r.decision.moral.global_verdict.value
            if r.decision.moral
            else "Gray Zone"
        )
        out["teleology_branches"] = qualitative_temporal_branches(
            r.decision.final_action,
            v,
            r.perception.suggested_context,
        )
    return out


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": "ethical-android-chat",
            "websocket": "/ws/chat",
            "protocol": (
                "Send JSON: {\"text\": str, \"agent_id\"?: str, \"include_narrative\"?: bool, "
                "\"sensor\"?: {battery_level?, audio_emergency?, vision_emergency?, scene_coherence?, …}}. "
                "Responses include identity, drive_intents, monologue (when decision present), optional "
                "affective_homeostasis, experience_digest, user_model, chronobiology, premise_advisory, "
                "teleology_branches, multimodal_trust, vitality (see README KERNEL_CHAT_* / KERNEL_MULTIMODAL_* / "
                "KERNEL_VITALITY_*), guardian_mode (KERNEL_GUARDIAN_MODE), epistemic_dissonance (v9.1), decision, …"
            ),
        }
    )


@app.websocket("/ws/chat")
async def ws_chat(ws: WebSocket) -> None:
    """
    One kernel per connection so WorkingMemory stays isolated per session.

    Client → server (JSON text):
      {"text": "...", "agent_id": "optional", "include_narrative": false,
       "sensor": "optional object — see SensorSnapshot / README (v8 situated hints)"}

    Server → client:
      JSON object from _chat_turn_to_jsonable (see GET /).
    """
    await ws.accept()
    kernel = EthicalKernel(
        variability=os.environ.get("KERNEL_VARIABILITY", "1") not in ("0", "false", "False"),
        llm_mode=os.environ.get("LLM_MODE"),
    )
    try_load_checkpoint(kernel)
    session_ckpt = init_session_checkpoint_state(kernel)
    bridge = RealTimeBridge(kernel)

    interval = advisory_interval_seconds_from_env()
    advisory_stop: asyncio.Event | None = None
    advisory_task: asyncio.Task[None] | None = None
    if interval > 0:
        advisory_stop = asyncio.Event()
        advisory_task = asyncio.create_task(
            advisory_loop(kernel, interval_s=interval, stop=advisory_stop)
        )

    try:
        while True:
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"error": "invalid_json", "hint": "send JSON with a \"text\" field"})
                continue

            text = (data.get("text") or "").strip()
            if not text:
                await ws.send_json({"error": "empty_text"})
                continue

            agent_id = data.get("agent_id") or "user"
            include_narrative = bool(data.get("include_narrative", False))

            sensor_raw = data.get("sensor")
            client = sensor_raw if isinstance(sensor_raw, dict) else None
            fixture = os.environ.get("KERNEL_SENSOR_FIXTURE", "").strip() or None
            preset = os.environ.get("KERNEL_SENSOR_PRESET", "").strip() or None
            sensor_snapshot = snapshot_from_layers(
                fixture_path=fixture,
                preset_name=preset,
                client_dict=client,
            )

            result = await bridge.process_chat(
                text,
                agent_id=agent_id,
                place="chat",
                include_narrative=include_narrative,
                sensor_snapshot=sensor_snapshot,
            )
            await ws.send_json(_chat_turn_to_jsonable(result, kernel))
            maybe_autosave_episodes(kernel, session_ckpt)
    except WebSocketDisconnect:
        pass
    finally:
        if advisory_stop is not None and advisory_task is not None:
            advisory_stop.set()
            try:
                await asyncio.wait_for(advisory_task, timeout=5.0)
            except (asyncio.TimeoutError, asyncio.CancelledError):
                advisory_task.cancel()
                try:
                    await advisory_task
                except asyncio.CancelledError:
                    pass
        on_websocket_session_end(kernel)


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment (CHAT_HOST, CHAT_PORT)."""
    host = os.environ.get("CHAT_HOST", "127.0.0.1")
    port = int(os.environ.get("CHAT_PORT", "8765"))
    return host, port


def run_chat_server() -> None:
    """Start uvicorn with this module's ``app`` (blocking)."""
    import uvicorn

    host, port = get_uvicorn_bind()
    uvicorn.run(app, host=host, port=port, reload=False)


def main() -> None:
    run_chat_server()


if __name__ == "__main__":
    main()
