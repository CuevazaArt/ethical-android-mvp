"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
Or: python -m src.runtime  (same server; see docs/RUNTIME_CONTRACT.md)

OpenAPI/Swagger: **off** by default; set KERNEL_API_DOCS=1 to expose ``/docs``, ``/redoc``, ``/openapi.json`` (see README).

Checkpoint (optional): KERNEL_CHECKPOINT_PATH, KERNEL_CHECKPOINT_LOAD,
KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT, KERNEL_CHECKPOINT_EVERY_N_EPISODES — see src/persistence/checkpoint.py

Conduct guide export (optional): KERNEL_CONDUCT_GUIDE_EXPORT_PATH — JSON on WebSocket disconnect
(after checkpoint); KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT — see src/modules/conduct_guide_export.py

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

Generative candidates (v9.2): KERNEL_GENERATIVE_ACTIONS, KERNEL_GENERATIVE_ACTIONS_MAX,
KERNEL_GENERATIVE_TRIGGER_CONTEXTS, KERNEL_GENERATIVE_LLM (parse ``generative_candidates`` from
perception JSON when using api/ollama) — see generative_candidates.py. JSON ``decision`` may include
``chosen_action_source`` and ``proposal_id``.

Judicial escalation (V11 Phases 1–3): KERNEL_JUDICIAL_ESCALATION enables advisory logic; optional JSON
``escalate_to_dao: true`` registers an ethical dossier when session strikes ≥ KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER
(default 2). KERNEL_JUDICIAL_RESET_IDLE_TURNS resets strikes after non-qualifying turns. KERNEL_JUDICIAL_MOCK_COURT
runs a simulated DAO vote + verdict A/B/C after registration. KERNEL_CHAT_INCLUDE_JUDICIAL
exposes ``judicial_escalation`` in responses. See judicial_escalation.py, PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md.

Moral Infrastructure Hub (V12 Phase 1): KERNEL_MORAL_HUB_PUBLIC enables ``GET /constitution`` (L0 JSON).
KERNEL_TRANSPARENCY_AUDIT logs R&D transparency events on WebSocket connect. KERNEL_DEMOCRATIC_BUFFER_MOCK
enables mock DemocraticBuffer proposals (DAO only; does not change buffer.py). KERNEL_ETHOS_PAYROLL_MOCK
appends EthosPayroll mock ledger lines on connect. V12.2: constitution drafts + optional WS/env. V12.3:
``KERNEL_MORAL_HUB_DAO_VOTE`` — WebSocket ``dao_vote``, ``dao_resolve``, ``dao_submit_draft``, ``dao_list``
(off-chain quadratic voting; persisted in snapshot schema v3). Optional: ``KERNEL_DEONTIC_GATE``,
``KERNEL_ML_ETHICS_TUNER_LOG``, ``KERNEL_REPARATION_VAULT_MOCK``, ``KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY``.
See UNIVERSAL_ETHOS_AND_HUB.md, moral_hub.py, PROPUESTA_ESTADO_ETOSOCIAL_V12.md.

Nomadic HAL (design v11): ``GET /nomad/migration`` describes WebSocket ``nomad_simulate_migration``.
``KERNEL_NOMAD_SIMULATION=1`` enables it; ``KERNEL_NOMAD_MIGRATION_AUDIT=1`` appends a DAO calibration
line (JSON payload, no GPS unless opt-in). See PROPUESTA_CONCIENCIA_NOMADA_HAL.md.

Reality verification (V11+ cross-model): ``KERNEL_LIGHTHOUSE_KB_PATH`` — JSON lighthouse KB for
contradiction checks vs rival/user premises; ``KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`` exposes
``reality_verification`` in WebSocket JSON. Does not bypass MalAbs. See ``reality_verification.py``,
PROPUESTA_VERIFICACION_REALIDAD_V11.md.

DAO integrity (design → local audit): ``KERNEL_DAO_INTEGRITY_AUDIT_WS=1`` enables WebSocket
``integrity_alert`` → ``HubAudit:dao_integrity`` on MockDAO (no network broadcast). See
PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md.

Advisory telemetry (optional, Fase 1.3–1.4): KERNEL_ADVISORY_INTERVAL_S — positive seconds
spawns a read-only :func:`src.runtime.telemetry.advisory_loop` per WebSocket session (DriveArbiter only).
Metaplan vs drives (v9.4): KERNEL_METAPLAN_DRIVE_FILTER / KERNEL_METAPLAN_DRIVE_EXTRA — see metaplan_registry.py.
Swarm lab stub (v9.3): KERNEL_SWARM_STUB — optional gate for ``swarm_peer_stub`` digests only; see docs/SWARM_P2P_THREAT_MODEL.md.

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
from .modules.judicial_escalation import chat_include_judicial
from .modules.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from .modules.hub_audit import record_dao_integrity_alert
from .modules.moral_hub import (
    add_constitution_draft,
    apply_proposal_resolution_to_constitution_drafts,
    audit_transparency_event,
    chat_include_constitution,
    constitution_draft_ws_enabled,
    constitution_snapshot,
    dao_governance_api_enabled,
    dao_integrity_audit_ws_enabled,
    ethos_payroll_record_mock,
    moral_hub_public_enabled,
    proposal_to_public,
    submit_constitution_draft_for_vote,
)
from .modules.nomad_identity import nomad_identity_public
from .modules.existential_serialization import (
    nomad_simulation_ws_enabled,
    simulate_nomadic_migration,
)
from .modules.buffer import PreloadedBuffer
from .real_time_bridge import RealTimeBridge
from .runtime.telemetry import advisory_interval_seconds_from_env, advisory_loop

def _api_docs_enabled() -> bool:
    """OpenAPI/Swagger UI — off by default (LAN deployments); set KERNEL_API_DOCS=1 to expose."""
    v = os.environ.get("KERNEL_API_DOCS", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


app = FastAPI(
    title="Ethos Kernel Chat",
    version="1.0",
    docs_url="/docs" if _api_docs_enabled() else None,
    redoc_url="/redoc" if _api_docs_enabled() else None,
    openapi_url="/openapi.json" if _api_docs_enabled() else None,
)


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


def _chat_include_reality_verification() -> bool:
    """Lighthouse KB vs asserted premises — ``reality_verification`` in JSON (default off)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _chat_include_judicial() -> bool:
    """V11 Phase 1 — include judicial_escalation when KERNEL_CHAT_INCLUDE_JUDICIAL is on."""
    return chat_include_judicial()


def _chat_include_constitution() -> bool:
    """V12 — include full constitution JSON (L0 + L1/L2 drafts) on WebSocket payloads."""
    return chat_include_constitution()


def _chat_include_nomad_identity() -> bool:
    """Include NomadIdentity / immortality bridge summary (see UNIVERSAL_ETHOS_AND_HUB.md)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


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
        if d.bayesian_result is not None:
            ca = d.bayesian_result.chosen_action
            out["decision"]["chosen_action_source"] = ca.source
            if ca.proposal_id:
                out["decision"]["proposal_id"] = ca.proposal_id
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
    if _chat_include_reality_verification() and r.reality_verification is not None:
        out["reality_verification"] = r.reality_verification.to_public_dict()
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
    if _chat_include_judicial() and r.judicial_escalation is not None:
        out["judicial_escalation"] = r.judicial_escalation.to_public_dict()
    if _chat_include_constitution():
        out["constitution"] = kernel.get_constitution_snapshot()
    if _chat_include_nomad_identity():
        out["nomad_identity"] = nomad_identity_public(kernel)
    maybe_log_gray_zone_tuning_opportunity(kernel.dao, r, kernel=kernel)
    return out


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/dao/governance")
def dao_governance_meta() -> Dict[str, Any]:
    """V12.3 — whether DAO vote pipeline is enabled and which WebSocket JSON keys to use."""
    return {
        "enabled": dao_governance_api_enabled(),
        "transport": "websocket",
        "path": "/ws/chat",
        "env": "KERNEL_MORAL_HUB_DAO_VOTE",
        "messages": {
            "dao_list": True,
            "dao_submit_draft": {"level": 1, "draft_id": "uuid"},
            "dao_vote": {
                "proposal_id": "PROP-0001",
                "participant_id": "community_01",
                "n_votes": 1,
                "in_favor": True,
            },
            "dao_resolve": {"proposal_id": "PROP-0001"},
        },
        "note": "Governance runs on the per-connection kernel; use participants from MockDAO (e.g. community_01).",
    }


@app.get("/nomad/migration")
def nomad_migration_meta() -> Dict[str, Any]:
    """Nomadic HAL simulation — WebSocket ``nomad_simulate_migration`` when KERNEL_NOMAD_SIMULATION=1."""
    return {
        "simulation_enabled": nomad_simulation_ws_enabled(),
        "migration_audit_env": "KERNEL_NOMAD_MIGRATION_AUDIT",
        "transport": "websocket",
        "path": "/ws/chat",
        "message": {
            "nomad_simulate_migration": {
                "profile": "mobile",
                "destination_hardware_id": "device-id-or-empty",
                "thought_line": "optional monologue bound",
                "include_location": False,
            }
        },
    }


@app.get("/constitution")
def constitution_public() -> JSONResponse:
    """
    Read-only Level-0 ethical principles (current PreloadedBuffer) as JSON.

    Enabled when KERNEL_MORAL_HUB_PUBLIC=1. Does not expose L1/L2 drafts until governance exists.
    See docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md (DemocraticBuffer vision).
    """
    if not moral_hub_public_enabled():
        return JSONResponse(
            {"error": "disabled", "hint": "set KERNEL_MORAL_HUB_PUBLIC=1"},
            status_code=404,
        )
    return JSONResponse(constitution_snapshot(PreloadedBuffer()))


@app.get("/")
def root() -> JSONResponse:
    return JSONResponse(
        {
            "service": "ethos-kernel-chat",
            "websocket": "/ws/chat",
            "constitution": "/constitution (requires KERNEL_MORAL_HUB_PUBLIC=1)",
            "dao_governance": "/dao/governance (V12.3 vote protocol; KERNEL_MORAL_HUB_DAO_VOTE for WebSocket actions)",
            "nomad_migration": "/nomad/migration (KERNEL_NOMAD_SIMULATION + optional KERNEL_NOMAD_MIGRATION_AUDIT)",
            "protocol": (
                "Send JSON: {\"text\": str, \"agent_id\"?: str, \"include_narrative\"?: bool, "
                "\"sensor\"?: {battery_level?, audio_emergency?, vision_emergency?, scene_coherence?, …}}. "
                "Responses include identity, drive_intents, monologue (when decision present), optional "
                "affective_homeostasis, experience_digest, user_model, chronobiology, premise_advisory, "
                "teleology_branches, multimodal_trust, vitality (see README KERNEL_CHAT_* / KERNEL_MULTIMODAL_* / "
                "KERNEL_VITALITY_*), guardian_mode (KERNEL_GUARDIAN_MODE), epistemic_dissonance (v9.1), "
                "decision (chosen_action_source / proposal_id v9.2), …"
            ),
        }
    )


def _collect_dao_ws_actions(kernel: EthicalKernel, data: Dict[str, Any]) -> Dict[str, Any] | None:
    """V12.3 — optional quadratic vote / resolve / submit-draft / list on session kernel."""
    if not dao_governance_api_enabled():
        return None
    out: Dict[str, Any] = {}
    if data.get("dao_list"):
        out["proposals"] = [proposal_to_public(p) for p in kernel.dao.proposals]
    if isinstance(data.get("dao_submit_draft"), dict):
        sd = data["dao_submit_draft"]
        try:
            out["submit_draft"] = submit_constitution_draft_for_vote(
                kernel,
                int(sd.get("level", 1)),
                str(sd.get("draft_id") or ""),
            )
        except (ValueError, TypeError) as e:
            out["submit_draft"] = {"ok": False, "error": str(e)}
    if isinstance(data.get("dao_vote"), dict):
        dv = data["dao_vote"]
        try:
            out["vote"] = kernel.dao.vote(
                str(dv.get("proposal_id") or ""),
                str(dv.get("participant_id") or "user"),
                int(dv.get("n_votes") or 1),
                bool(dv.get("in_favor", True)),
            )
        except (ValueError, TypeError) as e:
            out["vote"] = {"success": False, "reason": str(e)}
    if isinstance(data.get("dao_resolve"), dict):
        dr = data["dao_resolve"]
        try:
            pid = str(dr.get("proposal_id") or "")
            res = kernel.dao.resolve_proposal(pid)
            out["resolve"] = res
            if res.get("outcome") in ("approved", "rejected"):
                n = apply_proposal_resolution_to_constitution_drafts(kernel, pid, res)
                if n:
                    out["resolve"]["constitution_drafts_updated"] = n
        except (ValueError, TypeError) as e:
            out["resolve"] = {"success": False, "reason": str(e)}
    return out if out else None


def _collect_integrity_ws_action(kernel: EthicalKernel, data: Dict[str, Any]) -> Dict[str, Any] | None:
    """Optional ``integrity_alert`` JSON — local DAO ledger row (PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA)."""
    if not dao_integrity_audit_ws_enabled():
        return None
    raw = data.get("integrity_alert")
    if not isinstance(raw, dict):
        return None
    summary = str(raw.get("summary") or "").strip()
    if not summary:
        return {"integrity_alert": {"ok": False, "error": "missing_summary"}}
    scope = str(raw.get("scope") or "local_audit").strip()[:120]
    record_dao_integrity_alert(kernel.dao, summary=summary, scope=scope)
    return {"integrity_alert": {"ok": True, "scope": scope}}


def _collect_nomad_ws_actions(kernel: EthicalKernel, data: Dict[str, Any]) -> Dict[str, Any] | None:
    """KERNEL_NOMAD_SIMULATION — apply HAL + optional DAO migration audit (lab)."""
    if not nomad_simulation_ws_enabled():
        return None
    if not isinstance(data.get("nomad_simulate_migration"), dict):
        return None
    nm = data["nomad_simulate_migration"]
    try:
        return simulate_nomadic_migration(
            kernel,
            kernel.dao,
            profile=str(nm.get("profile", "mobile")),
            destination_hardware_id=str(nm.get("destination_hardware_id", "")),
            thought_line=str(nm.get("thought_line", "")),
            include_location=bool(nm.get("include_location", False)),
        )
    except (TypeError, ValueError) as e:
        return {"error": str(e)}


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
    audit_transparency_event(
        kernel.dao,
        "websocket_session_open",
        "moral_hub V12 Phase 1 — R&D transparency audit hook",
    )
    ethos_payroll_record_mock(
        kernel.dao,
        "session_start channel=websocket (EthosPayroll mock ledger line)",
    )
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

            text_preview = (data.get("text") or "").strip()
            if (
                isinstance(data.get("integrity_alert"), dict)
                and not dao_integrity_audit_ws_enabled()
                and not text_preview
            ):
                await ws.send_json(
                    {
                        "error": "integrity_audit_disabled",
                        "hint": "Set KERNEL_DAO_INTEGRITY_AUDIT_WS=1 on the server.",
                    }
                )
                continue

            dao_payload = _collect_dao_ws_actions(kernel, data)
            nomad_payload = _collect_nomad_ws_actions(kernel, data)
            integrity_payload = _collect_integrity_ws_action(kernel, data)
            if dao_payload or nomad_payload or integrity_payload:
                out_ws: Dict[str, Any] = {}
                if dao_payload:
                    out_ws["dao"] = dao_payload
                if nomad_payload:
                    out_ws["nomad"] = nomad_payload
                if integrity_payload:
                    out_ws["integrity"] = integrity_payload
                await ws.send_json(out_ws)

            text = text_preview
            if not text:
                if dao_payload or nomad_payload or integrity_payload:
                    maybe_autosave_episodes(kernel, session_ckpt)
                    continue
                await ws.send_json({"error": "empty_text"})
                continue

            agent_id = data.get("agent_id") or "user"
            include_narrative = bool(data.get("include_narrative", False))
            escalate_to_dao = bool(data.get("escalate_to_dao", False))

            cd = data.get("constitution_draft")
            if isinstance(cd, dict) and constitution_draft_ws_enabled():
                try:
                    add_constitution_draft(
                        kernel,
                        int(cd.get("level", 1)),
                        str(cd.get("title") or ""),
                        str(cd.get("body") or ""),
                        str(cd.get("proposer") or agent_id),
                    )
                except (ValueError, TypeError):
                    pass

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
                escalate_to_dao=escalate_to_dao,
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
