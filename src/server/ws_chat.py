"""Core WebSocket chat: ``/ws/chat`` and turn JSON (Bloque 34.4)."""

from __future__ import annotations

import asyncio
import json
import logging
import math
import os
import threading
import time
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ..kernel import ChatTurnResult, EthicalKernel
from ..kernel_utils import kernel_dao_as_mock
from src.modules.somatic.affective_homeostasis import homeostasis_telemetry
from src.modules.cognition.consequence_projection import qualitative_temporal_branches
from src.modules.safety.guardian_mode import (
    is_guardian_mode_active,
    public_routines_snapshot,
)
from ..modules.internal_monologue import compose_monologue_line
from src.modules.ethics.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from src.modules.governance.moral_hub import (
    add_constitution_draft,
    audit_transparency_event,
    constitution_draft_ws_enabled,
    ethos_payroll_record_mock,
)
from src.modules.governance.nomad_identity import nomad_identity_public
from src.modules.perception.perception_schema import perception_report_from_dict
from src.modules.perception.perceptual_abstraction import snapshot_from_layers
from src.modules.perception.sensor_contracts import SensorPayloadValidationError
from ..observability.context import clear_request_context, set_request_id
from ..observability.metrics import (
    observe_chat_turn,
    record_chat_turn_async_timeout,
    record_llm_cancel_scope_signaled,
    record_malabs_block,
)
from ..persistence.checkpoint import (
    checkpoint_persistence_from_env,
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
)
from ..real_time_bridge import RealTimeBridge
from ..runtime.chat_feature_flags import (
    chat_expose_monologue,
    chat_include_chrono,
    chat_include_constitution,
    chat_include_epistemic,
    chat_include_experience_digest,
    chat_include_guardian,
    chat_include_guardian_routines,
    chat_include_homeostasis,
    chat_include_judicial,
    chat_include_light_risk,
    chat_include_malabs_trace,
    chat_include_multimodal_trust,
    chat_include_nomad_identity,
    chat_include_premise,
    chat_include_reality_verification,
    chat_include_teleology,
    chat_include_transparency_s10,
    chat_include_user_model,
    chat_include_vitality,
    coerce_public_int,
    env_truthy,
)
from ..runtime.telemetry import advisory_interval_seconds_from_env, advisory_loop
from .identity_envelope import build_sync_identity_ws_message, identity_state_public_dict
from .lan_governance_ws import (
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
    DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    _merge_lan_governance_ws_payloads,
)
from .ws_governance import (
    _collect_dao_ws_actions,
    _collect_integrity_ws_action,
    _collect_lan_governance_coordinator,
    _collect_lan_governance_dao_batch,
    _collect_lan_governance_envelope,
    _collect_lan_governance_integrity_batch,
    _collect_lan_governance_judicial_batch,
    _collect_lan_governance_mock_court_batch,
    _collect_nomad_ws_actions,
)

logger = logging.getLogger(__name__)

router = APIRouter()


def _tri_lobe_chat_ws_contract_defaults(kernel: EthicalKernel) -> dict[str, Any]:
    """
    When the tri-lobe path returns a sparse :class:`~src.kernel.ChatTurnResult` (no ``decision``
    graph), preserve the WebSocket JSON contract expected by integration tests and dashboards.
    """
    limb = kernel.limbic_system
    sym = getattr(limb, "sympathetic", None)
    try:
        sigma = float(getattr(sym, "sigma", 0.5) or 0.5)
    except (TypeError, ValueError):
        sigma = 0.5
    if not math.isfinite(sigma):
        sigma = 0.5
    sigma = max(0.0, min(1.0, sigma))

    sc = getattr(getattr(kernel, "sensory_cortex", None), "subjective_clock", None)
    chrono: dict[str, Any]
    if sc is not None and hasattr(sc, "to_public_dict"):
        chrono = dict(sc.to_public_dict())
    else:
        chrono = {"turn_index": 1}
    chrono.setdefault("turn_index", 1)

    now_ms = int(time.time() * 1000)
    turn_idx = coerce_public_int(chrono.get("turn_index"), default=1, non_negative=True)
    temporal: dict[str, Any] = {
        "sync_schema": "temporal_sync_v1",
        "turn_index": turn_idx,
        "wall_clock_unix_ms": now_ms,
        "processor_elapsed_ms": 0,
        "turn_delta_ms": 0,
        "local_network_sync_ready": False,
        "dao_sync_ready": False,
    }

    return {
        "affective_homeostasis": {
            "state": "within_range",
            "sigma": round(sigma, 4),
            "strain_index": None,
            "pad_max_component": None,
            "hint": "advisory_only_no_policy_change",
        },
        "user_model": {
            "frustration_streak": 0,
            "premise_concern_streak": 0,
            "turns_observed": 0,
            "cognitive_pattern": "tri_lobe_contract_stub",
            "risk_band": "low",
            "judicial_phase": "",
            "last_circle": "",
        },
        "chronobiology": chrono,
        "premise_advisory": {"flag": "none", "detail": ""},
        "multimodal_trust": {"state": "no_claim", "reason": "", "requires_owner_anchor": False},
        "vitality": {"is_critical": False, "critical_threshold": 0.15},
        "guardian_mode": False,
        "epistemic_dissonance": {"active": False},
        "decision": {
            "final_action": "tri_lobe_turn",
            "decision_mode": "light",
            "blocked": False,
            "chosen_action_source": "builtin",
        },
        "support_buffer": {
            "source": "local_preloaded_buffer",
            "context": "everyday",
            "active_principles": [],
            "priority_profile": "balanced",
        },
        "limbic_perception": {
            "arousal_band": "medium",
            "threat_load": 0.0,
            "regulation_gap": 0.0,
            "planning_bias": "balanced",
            "multimodal_mismatch": False,
            "vitality_critical": False,
            "context": "everyday",
        },
        "temporal_context": dict(temporal),
        "temporal_sync": dict(temporal),
        "teleology_branches": qualitative_temporal_branches("converse", "Gray Zone", "everyday"),
        "perception_confidence": {"band": "medium", "score": 0.5},
        "perception_observability": {"confidence_band": "medium", "confidence_score": 0.5},
    }


def _trim_tri_lobe_ws_contract_fill(fill: dict[str, Any]) -> None:
    """Strip tri-lobe contract stubs when presentation env says to omit those keys."""
    if not chat_include_homeostasis():
        fill.pop("affective_homeostasis", None)
    if not chat_include_user_model():
        fill.pop("user_model", None)
    if not chat_include_chrono():
        fill.pop("chronobiology", None)
    if not chat_include_premise():
        fill.pop("premise_advisory", None)
    if not chat_include_teleology():
        fill.pop("teleology_branches", None)
    if not chat_include_multimodal_trust():
        fill.pop("multimodal_trust", None)
    if not chat_include_vitality():
        fill.pop("vitality", None)
    if not chat_include_guardian():
        fill.pop("guardian_mode", None)
    if not chat_include_epistemic():
        fill.pop("epistemic_dissonance", None)


def _chat_turn_to_jsonable(r: ChatTurnResult, kernel: EthicalKernel) -> dict[str, Any]:
    """Compact JSON-safe view (no full internal objects)."""
    # Tri-lobe EthosKernel returns a slim ChatTurnResult without legacy v12 graph fields.
    if not hasattr(r, "metacognitive_doubt"):
        out_min: dict[str, Any] = {
            "blocked": r.blocked,
            "path": r.path,
            "block_reason": r.block_reason,
            "response": {
                "message": r.response.message,
                "tone": r.response.tone,
                "hax_mode": getattr(r.response, "hax_mode", ""),
                "inner_voice": getattr(r.response, "inner_voice", ""),
            },
            "identity": identity_state_public_dict(kernel),
            "drive_intents": [
                {"suggest": di.suggest, "reason": di.reason, "priority": di.priority}
                for di in kernel.drive_arbiter.evaluate(kernel)
            ],
            "monologue": "",
        }
        if chat_include_experience_digest():
            out_min["experience_digest"] = kernel.memory.experience_digest
        return out_min

    out: dict[str, Any] = {
        "blocked": r.blocked,
        "path": r.path,
        "block_reason": r.block_reason,
        "response": {
            "message": r.response.message,
            "tone": r.response.tone,
            "hax_mode": r.response.hax_mode,
            "inner_voice": r.response.inner_voice,
        },
        "identity": identity_state_public_dict(kernel),
        "drive_intents": [
            {"suggest": di.suggest, "reason": di.reason, "priority": di.priority}
            for di in kernel.drive_arbiter.evaluate(kernel)
        ],
    }
    if chat_include_malabs_trace():
        m = getattr(kernel, "_last_chat_malabs", None)
        if m is not None and getattr(m, "decision_trace", None):
            out["malabs_trace"] = list(m.decision_trace)
    if r.metacognitive_doubt:
        out["metacognitive_doubt"] = True
    if r.support_buffer:
        out["support_buffer"] = {
            "source": r.support_buffer.get("source", "local_preloaded_buffer"),
            "context": r.support_buffer.get("context", "everyday"),
            "active_principles": list(r.support_buffer.get("active_principles") or []),
            "priority_profile": r.support_buffer.get("priority_profile", "balanced"),
            "priority_principles": list(r.support_buffer.get("priority_principles") or []),
            "planning_bias": r.support_buffer.get("planning_bias", "balanced"),
            "strategy_hint": r.support_buffer.get("strategy_hint") or "",
            "offline_ready": bool(r.support_buffer.get("offline_ready", True)),
        }
    if r.limbic_profile:
        out["limbic_perception"] = {
            "arousal_band": r.limbic_profile.get("arousal_band", "medium"),
            "threat_load": float(r.limbic_profile.get("threat_load", 0.0)),
            "regulation_gap": float(r.limbic_profile.get("regulation_gap", 0.0)),
            "planning_bias": r.limbic_profile.get("planning_bias", "balanced"),
            "multimodal_mismatch": bool(r.limbic_profile.get("multimodal_mismatch", False)),
            "vitality_critical": bool(r.limbic_profile.get("vitality_critical", False)),
            "context": r.limbic_profile.get("context", "everyday"),
        }
    if r.temporal_context is not None:
        tc = r.temporal_context.to_public_dict()
        tc["turn_index"] = coerce_public_int(tc.get("turn_index"), default=0, non_negative=True)
        out["temporal_context"] = tc
        out["temporal_sync"] = {
            "sync_schema": tc.get("sync_schema", "temporal_sync_v1"),
            "turn_index": coerce_public_int(tc.get("turn_index"), default=0, non_negative=True),
            "wall_clock_unix_ms": tc.get("wall_clock_unix_ms"),
            "processor_elapsed_ms": coerce_public_int(
                tc.get("processor_elapsed_ms"), default=0, non_negative=True
            ),
            "turn_delta_ms": coerce_public_int(
                tc.get("turn_delta_ms"), default=0, non_negative=True
            ),
            "local_network_sync_ready": bool(tc.get("local_network_sync_ready", False)),
            "dao_sync_ready": bool(tc.get("dao_sync_ready", False)),
        }
    if r.perception_confidence is not None:
        pc = r.perception_confidence.to_public_dict()
        out["perception_confidence"] = pc
        po = out.get("perception_observability")
        if isinstance(po, dict):
            po["confidence_band"] = pc.get("band", "unknown")
            po["confidence_score"] = float(pc.get("score", 0.0))
    if r.verbal_llm_degradation_events:
        out["verbal_llm_observability"] = {
            "degraded": True,
            "events": r.verbal_llm_degradation_events,
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
        # Stable observability contract: always emit canonical coercion-report keys.
        cr = perception_report_from_dict(getattr(p, "coercion_report", None)).to_public_dict()
        out["perception"]["coercion_report"] = cr
        if cr.get("session_banner_recommended"):
            out["perception_backend_banner"] = True
        out["perception_observability"] = {
            "uncertainty": float(cr.get("uncertainty") or 0.0),
            "dual_high_discrepancy": bool(cr.get("perception_dual_high_discrepancy")),
            "backend_degraded": bool(cr.get("backend_degraded")),
            "metacognitive_doubt": bool(r.metacognitive_doubt),
        }
        if r.perception_confidence is not None:
            out["perception_observability"]["confidence_band"] = out["perception_confidence"].get(
                "band", "unknown"
            )
            out["perception_observability"]["confidence_score"] = float(
                out["perception_confidence"].get("score", 0.0)
            )
    if r.decision is not None:
        d = r.decision
        if chat_expose_monologue():
            base_mono = compose_monologue_line(
                d, getattr(kernel, "_last_registered_episode_id", None)
            )
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
        if chat_include_homeostasis():
            out["affective_homeostasis"] = homeostasis_telemetry(d)
        if chat_include_transparency_s10():
            from src.modules.safety.transparency_s10 import build_transparency_s10_bundle

            sig: dict[str, Any] = {}
            if r.perception:
                p = r.perception
                sig = {
                    "risk": float(getattr(p, "risk", 0.0) or 0.0),
                    "hostility": float(getattr(p, "hostility", 0.0) or 0.0),
                    "calm": float(getattr(p, "calm", 0.5) or 0.5),
                    "manipulation": float(getattr(p, "manipulation", 0.0) or 0.0),
                    "silence": float(getattr(p, "silence", 0.0) or 0.0),
                }
            pc_score = None
            if r.perception_confidence is not None:
                pc_score = float(r.perception_confidence.to_public_dict().get("score", 0.0))
            out["transparency_s10"] = build_transparency_s10_bundle(
                d,
                signals=sig,
                perception=r.perception,
                verbal_degraded=bool(r.verbal_llm_degradation_events),
                metacognitive_doubt=bool(r.metacognitive_doubt),
                perception_confidence_score=pc_score,
            )
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
    if chat_include_experience_digest():
        out["experience_digest"] = kernel.memory.experience_digest
    if chat_include_user_model():
        um = getattr(kernel, "user_model", None)
        if um is not None and hasattr(um, "to_public_dict"):
            out["user_model"] = um.to_public_dict()
    if chat_include_chrono():
        sc = getattr(kernel, "subjective_clock", None)
        if sc is not None and hasattr(sc, "to_public_dict"):
            out["chronobiology"] = sc.to_public_dict()
    if chat_include_premise():
        pa = getattr(kernel, "_last_premise_advisory", None)
        if pa is not None and hasattr(pa, "flag") and hasattr(pa, "detail"):
            out["premise_advisory"] = {"flag": pa.flag, "detail": pa.detail}
    if chat_include_multimodal_trust() and r.multimodal_trust is not None:
        mt = r.multimodal_trust
        out["multimodal_trust"] = {
            "state": mt.state,
            "reason": mt.reason,
            "requires_owner_anchor": mt.requires_owner_anchor,
        }
    if chat_include_vitality():
        va = getattr(kernel, "_last_vitality_assessment", None)
        if va is not None and hasattr(va, "to_public_dict"):
            out["vitality"] = va.to_public_dict()
    if chat_include_guardian():
        out["guardian_mode"] = is_guardian_mode_active()
    if chat_include_guardian_routines():
        gr = public_routines_snapshot()
        if gr:
            out["guardian_routines"] = gr
    if chat_include_epistemic() and r.epistemic_dissonance is not None:
        out["epistemic_dissonance"] = r.epistemic_dissonance.to_public_dict()
    if chat_include_reality_verification() and r.reality_verification is not None:
        out["reality_verification"] = r.reality_verification.to_public_dict()
    if chat_include_teleology() and r.decision is not None and r.perception is not None:
        v = r.decision.moral.global_verdict.value if r.decision.moral else "Gray Zone"
        out["teleology_branches"] = qualitative_temporal_branches(
            r.decision.final_action,
            v,
            r.perception.suggested_context,
        )
    if chat_include_judicial() and r.judicial_escalation is not None:
        out["judicial_escalation"] = r.judicial_escalation.to_public_dict()
    if chat_include_constitution():
        snap = getattr(kernel, "get_constitution_snapshot", None)
        if callable(snap):
            out["constitution"] = snap()
    if chat_include_nomad_identity():
        out["nomad_identity"] = nomad_identity_public(kernel)
    if chat_include_light_risk() and hasattr(kernel, "_last_light_risk_tier"):
        lrt = kernel._last_light_risk_tier
        if lrt:
            out["light_risk_tier"] = lrt
    if r.decision is None and r.path == "nervous_bus":
        fill = _tri_lobe_chat_ws_contract_defaults(kernel)
        _trim_tri_lobe_ws_contract_fill(fill)
        for k, v in fill.items():
            if k not in out:
                out[k] = v
    maybe_log_gray_zone_tuning_opportunity(kernel_dao_as_mock(kernel.dao), r, kernel=kernel)
    return out


@router.websocket("/ws/chat")
async def ws_chat(ws: WebSocket) -> None:
    """
    One kernel per connection so WorkingMemory stays isolated per session.

    Client → server (JSON text):
      {"text": "...", "agent_id": "optional", "include_narrative": false,
       "sensor": "optional object — see SensorSnapshot / README (v8 situated hints)"}

    Server → client:
      Immediately after accept: ``build_sync_identity_ws_message`` (Bloque 22.2): ``type`` =
      ``[SYNC_IDENTITY]``, ``payload.gestalt_snapshot``, narrative rows, manifest, and
      ``narrative_tail``. Then streaming / ``_chat_turn_to_jsonable`` (see GET /).
    """
    await ws.accept()
    set_request_id()
    logger.info("websocket_session_open")
    from ..settings import kernel_settings

    st = kernel_settings()
    kernel = EthicalKernel(
        variability=st.kernel_variability,
        llm_mode=st.llm_mode,
        checkpoint_persistence=checkpoint_persistence_from_env(),
    )
    try_load_checkpoint(kernel)
    session_ckpt = init_session_checkpoint_state(kernel)
    _session_dao = kernel_dao_as_mock(kernel.dao)
    audit_transparency_event(
        _session_dao,
        "websocket_session_open",
        "moral_hub V12 Phase 1 — R&D transparency audit hook",
    )
    ethos_payroll_record_mock(
        _session_dao,
        "session_start channel=websocket (EthosPayroll mock ledger line)",
    )
    try:
        await kernel.start()
    except Exception as exc:
        logger.warning("websocket kernel_start failed: %s", exc)

    bridge = RealTimeBridge(kernel)
    chat_turn_seq = 0

    if env_truthy("KERNEL_CHAT_WS_SYNC_IDENTITY", True):
        try:
            await ws.send_json(build_sync_identity_ws_message(kernel))
        except Exception as exc:
            logger.warning("websocket sync_identity send failed: %s", exc)

    interval = advisory_interval_seconds_from_env()
    advisory_stop: asyncio.Event | None = None
    advisory_task: asyncio.Task[None] | None = None
    lan_envelope_replay_cache: dict[str, dict[str, Any]] = {}
    lan_envelope_replay_cache_stats: dict[str, int] = {
        "hits": 0,
        "misses": 0,
        "evicted_ttl": 0,
        "evicted_lru": 0,
    }
    lan_envelope_replay_cache_ttl_ms = coerce_public_int(
        os.environ.get("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS"),
        default=DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
        non_negative=True,
    )
    lan_envelope_replay_cache_max_entries = max(
        1,
        coerce_public_int(
            os.environ.get("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES"),
            default=DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
            non_negative=True,
        ),
    )
    if interval > 0:
        advisory_stop = asyncio.Event()
        advisory_task = asyncio.create_task(
            advisory_loop(kernel, interval_s=interval, stop=advisory_stop)
        )

    try:
        current_turn_task: asyncio.Task | None = None
        current_cancel_ev: threading.Event | None = None

        async def run_turn(data_in: dict[str, Any], turn_id: int):
            nonlocal current_cancel_ev
            t_turn_start = time.perf_counter()
            set_request_id()

            try:
                text = (data_in.get("text") or "").strip()
                agent_id = data_in.get("agent_id") or "user"
                include_narrative = bool(data_in.get("include_narrative", False))
                escalate_to_dao = bool(data_in.get("escalate_to_dao", False))

                # Situated v8 sensors
                sensor_raw = data_in.get("sensor")
                client = sensor_raw if isinstance(sensor_raw, dict) else None

                # Phase 10: Inject Nomad Bridge Live Data
                from src.modules.perception.nomad_bridge import get_nomad_bridge

                nb = get_nomad_bridge()
                if client is None:
                    client = {}

                # Drain telemetry_queue to get the LATEST entry (S.2.1 Calibration)
                live_t = {}
                while not nb.telemetry_queue.empty():
                    try:
                        live_t = nb.telemetry_queue.get_nowait()
                    except asyncio.QueueEmpty:
                        break

                if live_t:
                    client.update(live_t)

                client["rms_audio"] = nb.last_rms

                fixture = os.environ.get("KERNEL_SENSOR_FIXTURE", "").strip() or None
                preset = os.environ.get("KERNEL_SENSOR_PRESET", "").strip() or None
                sensor_snapshot = snapshot_from_layers(
                    fixture_path=fixture,
                    preset_name=preset,
                    client_dict=client,
                )

                chat_to = st.kernel_chat_turn_timeout_seconds

                result: ChatTurnResult | None = None
                gen = bridge.process_chat_stream(
                    text,
                    agent_id=agent_id,
                    place="chat",
                    include_narrative=include_narrative,
                    sensor_snapshot=sensor_snapshot,
                    escalate_to_dao=escalate_to_dao,
                    cancel_event=current_cancel_ev,
                    chat_turn_id=turn_id,
                )
                stream_closed = False

                async def _ensure_stream_closed() -> None:
                    """Close the async generator so in-flight asyncio work (e.g. httpx) is torn down."""
                    nonlocal stream_closed
                    if stream_closed:
                        return
                    try:
                        await gen.aclose()
                    except Exception:
                        pass
                    stream_closed = True

                try:
                    if chat_to is not None:
                        # Timeout-aware stream consumption; on timeout, aclose cancels pending awaits.
                        it = gen.__aiter__()
                        while True:
                            try:
                                event = await asyncio.wait_for(it.__anext__(), timeout=chat_to)
                                if event["event_type"] == "turn_finished":
                                    result = event["payload"]["result"]
                                    break
                                await ws.send_json(event)
                            except StopAsyncIteration:
                                break
                    else:
                        async for event in gen:
                            if event["event_type"] == "turn_finished":
                                result = event["payload"]["result"]
                            else:
                                await ws.send_json(event)

                    if result:
                        observe_chat_turn(result.path, time.perf_counter() - t_turn_start)
                        if result.path in ("safety_block", "kernel_block"):
                            record_malabs_block(result.path)

                        logger.info("chat_turn_finished id=%s path=%s", turn_id, result.path)

                        if st.kernel_chat_json_offload:
                            payload = await bridge.run_sync_in_chat_thread(
                                _chat_turn_to_jsonable, result, kernel
                            )
                        else:
                            payload = _chat_turn_to_jsonable(result, kernel)

                        await ws.send_json({"event_type": "turn_finished", "payload": payload})

                        # NOTE: kernel_voice removed — turn_finished already triggers TTS in the PWA client.

                        haptic_plan = payload.get("limbic_profile", {}).get("haptic_plan", [])
                        if haptic_plan:
                            await ws.send_json(
                                {"type": "haptic_feedback", "payload": {"haptics": haptic_plan}}
                            )

                        maybe_autosave_episodes(kernel, session_ckpt)

                except TimeoutError:
                    if current_cancel_ev is not None:
                        current_cancel_ev.set()
                        record_llm_cancel_scope_signaled()
                    await _ensure_stream_closed()
                    _abandon = getattr(kernel, "abandon_chat_turn", None)
                    if callable(_abandon):
                        _abandon(turn_id)
                    observe_chat_turn("turn_timeout", time.perf_counter() - t_turn_start)
                    record_chat_turn_async_timeout()

                    await ws.send_json(
                        {
                            "error": "chat_turn_timeout",
                            "timeout_seconds": chat_to,
                            "path": "turn_timeout",
                            "response": {
                                "message": "El turno excedió el límite de tiempo del servidor.",
                                "tone": "neutral",
                            },
                        }
                    )
                finally:
                    await _ensure_stream_closed()
            except asyncio.CancelledError:
                logger.info("chat_turn_cancelled id=%s", turn_id)
                _abandon = getattr(kernel, "abandon_chat_turn", None)
                if callable(_abandon):
                    _abandon(turn_id)
                if current_cancel_ev:
                    current_cancel_ev.set()
            except Exception as e:
                logger.exception("chat_turn_error id=%s: %s", turn_id, e)
                try:
                    await ws.send_json({"error": "internal_error", "message": str(e)})
                except Exception:
                    pass

        while True:
            set_request_id()
            raw = await ws.receive_text()
            if len(raw.encode("utf-8")) > st.kernel_chat_ws_max_message_bytes:
                await ws.send_json(
                    {
                        "error": "message_too_large",
                        "max_bytes": st.kernel_chat_ws_max_message_bytes,
                    }
                )
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"error": "invalid_json"})
                continue

            # ══ Control Messages ══
            if "control" in data:
                ctrl = data["control"]
                if ctrl == "abort":
                    if current_turn_task and not current_turn_task.done():
                        current_turn_task.cancel()
                        if current_cancel_ev:
                            current_cancel_ev.set()
                        await ws.send_json({"control_ack": "aborted", "turn_id": chat_turn_seq})
                    else:
                        await ws.send_json({"control_ack": "no_active_turn"})
                continue

            # ══ Operator Feedback ══
            ofb = data.get("operator_feedback")
            if ofb is not None and str(ofb).strip():
                recorded = kernel.record_operator_feedback(str(ofb).strip())
                await ws.send_json({"operator_feedback_recorded": recorded})
                maybe_autosave_episodes(kernel, session_ckpt)
                continue

            # ══ Integrity & Governance Payloads (Non-text) ══
            text_preview = (data.get("text") or "").strip()

            # Check for non-text payloads
            dao_payload = _collect_dao_ws_actions(kernel, data)
            nomad_payload = _collect_nomad_ws_actions(kernel, data)
            integrity_payload = _collect_integrity_ws_action(kernel, data)
            lan_batch_payload = _collect_lan_governance_integrity_batch(kernel, data)
            lan_dao_payload = _collect_lan_governance_dao_batch(kernel, data)
            lan_judicial_payload = _collect_lan_governance_judicial_batch(kernel, data)
            lan_mock_court_payload = _collect_lan_governance_mock_court_batch(kernel, data)
            lan_envelope_payload = _collect_lan_governance_envelope(
                kernel,
                data,
                replay_cache=lan_envelope_replay_cache,
                replay_cache_stats=lan_envelope_replay_cache_stats,
                replay_cache_ttl_ms=lan_envelope_replay_cache_ttl_ms,
                replay_cache_max_entries=lan_envelope_replay_cache_max_entries,
            )
            lan_coordinator_payload = _collect_lan_governance_coordinator(
                kernel,
                data,
                replay_cache=lan_envelope_replay_cache,
                replay_cache_stats=lan_envelope_replay_cache_stats,
                replay_cache_ttl_ms=lan_envelope_replay_cache_ttl_ms,
                replay_cache_max_entries=lan_envelope_replay_cache_max_entries,
            )
            lan_governance_merged = _merge_lan_governance_ws_payloads(
                lan_batch_payload,
                lan_dao_payload,
                lan_judicial_payload,
                lan_mock_court_payload,
                lan_envelope_payload,
                lan_coordinator_payload,
            )

            if dao_payload or nomad_payload or integrity_payload or lan_governance_merged:
                out_ws: dict[str, Any] = {}
                if dao_payload:
                    out_ws["dao"] = dao_payload
                if nomad_payload:
                    out_ws["nomad"] = nomad_payload
                if integrity_payload:
                    out_ws["integrity"] = integrity_payload
                if lan_governance_merged:
                    out_ws["lan_governance"] = lan_governance_merged
                await ws.send_json(out_ws)
                if not text_preview:
                    maybe_autosave_episodes(kernel, session_ckpt)
                    continue

            # ══ Constitution Drafts etc ══
            cd = data.get("constitution_draft")
            if isinstance(cd, dict) and constitution_draft_ws_enabled():
                draft_ok = False
                try:
                    add_constitution_draft(
                        kernel,
                        int(cd.get("level", 1)),
                        str(cd.get("title") or ""),
                        str(cd.get("body") or ""),
                        str(cd.get("proposer") or data.get("agent_id") or "user"),
                    )
                    draft_ok = True
                except Exception:
                    pass
                # Always ack so clients see draft result; combined text+draft messages still run
                # the chat turn below without losing this feedback.
                await ws.send_json({"constitution_draft": {"ok": draft_ok}})
                maybe_autosave_episodes(kernel, session_ckpt)
                if not text_preview:
                    continue

            sensor_raw = data.get("sensor")
            client = sensor_raw if isinstance(sensor_raw, dict) else None
            fixture = os.environ.get("KERNEL_SENSOR_FIXTURE", "").strip() or None
            preset = os.environ.get("KERNEL_SENSOR_PRESET", "").strip() or None
            try:
                snapshot_from_layers(
                    fixture_path=fixture,
                    preset_name=preset,
                    client_dict=client,
                )
            except SensorPayloadValidationError as e:
                await ws.send_json({"error": "sensor_payload_invalid", "detail": str(e)})
                continue

            if not text_preview:
                continue

            # Start new turn, cancelling previous if necessary (Serial Turns)
            if current_turn_task and not current_turn_task.done():
                logger.warning("auto_cancelling_previous_turn_due_to_new_text id=%s", chat_turn_seq)
                current_turn_task.cancel()
                if current_cancel_ev:
                    current_cancel_ev.set()

            chat_turn_seq += 1
            current_cancel_ev = threading.Event()
            current_turn_task = asyncio.create_task(run_turn(data, chat_turn_seq))

    except WebSocketDisconnect:
        pass
    finally:
        if current_turn_task and not current_turn_task.done():
            current_turn_task.cancel()
            if current_cancel_ev:
                current_cancel_ev.set()
        clear_request_context()
        if advisory_stop is not None and advisory_task is not None:
            advisory_stop.set()
            try:
                await asyncio.wait_for(advisory_task, timeout=5.0)
            except (TimeoutError, asyncio.CancelledError):
                advisory_task.cancel()
                try:
                    await advisory_task
                except asyncio.CancelledError:
                    pass
        await bridge.run_sync_in_chat_thread(on_websocket_session_end, kernel)
        try:
            await kernel.stop()
        except Exception:
            pass


