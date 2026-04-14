"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
Or: python -m src.runtime  (same server; see docs/proposals/README.md)

**Profiles:** set ``ETHOS_RUNTIME_PROFILE`` to a name in ``src/runtime_profiles.py`` to merge that bundle at import time (explicit env vars win per key). ``GET /health`` and ``GET /`` include ``runtime_profile`` when set.

**Chat async bridge:** Each turn runs ``EthicalKernel.process_chat_turn`` in a worker thread (``RealTimeBridge``) so the asyncio loop can accept other WebSocket connections. Optional ``KERNEL_CHAT_THREADPOOL_WORKERS`` (positive int) uses a dedicated ``ThreadPoolExecutor`` for chat; optional ``KERNEL_CHAT_TURN_TIMEOUT`` (seconds) bounds the **async** wait and returns JSON ``error=chat_turn_timeout`` when exceeded (in-flight sync LLM may still run until ``OLLAMA_TIMEOUT``). By default ``KERNEL_CHAT_JSON_OFFLOAD`` is on: WebSocket JSON (including optional ``KERNEL_LLM_MONOLOGUE``) is built in the same offload path so the loop is not blocked after the turn. See ``src/real_time_bridge.py``, ADR 0002, and ``docs/proposals/README.md``.

OpenAPI/Swagger: **off** by default; set KERNEL_API_DOCS=1 to expose ``/docs``, ``/redoc``, ``/openapi.json`` (see README).

Checkpoint (optional): ``KERNEL_CHECKPOINT_PATH`` attaches ``JsonFileCheckpointAdapter`` via
``checkpoint_persistence_from_env()``; ``KERNEL_CHECKPOINT_LOAD``,
``KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT``, ``KERNEL_CHECKPOINT_EVERY_N_EPISODES`` — see src/persistence/checkpoint.py

Conduct guide export (optional): KERNEL_CONDUCT_GUIDE_EXPORT_PATH — JSON on WebSocket disconnect
(after checkpoint); KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT — see src/modules/conduct_guide_export.py

Situated v8 (optional): KERNEL_SENSOR_FIXTURE (path to JSON), KERNEL_SENSOR_PRESET (name from
perceptual_abstraction.SENSOR_PRESETS) — merged before client ``sensor`` JSON; see PROPOSAL_SITUATED_ORGANISM_V8.md.

Multimodal thresholds (optional): KERNEL_MULTIMODAL_AUDIO_STRONG, KERNEL_MULTIMODAL_VISION_SUPPORT,
KERNEL_MULTIMODAL_SCENE_SUPPORT, KERNEL_MULTIMODAL_VISION_CONTRADICT, KERNEL_MULTIMODAL_SCENE_CONTRADICT
— see README / multimodal_trust.thresholds_from_env.

Vitality (optional): KERNEL_VITALITY_CRITICAL_BATTERY, KERNEL_CHAT_INCLUDE_VITALITY — see vitality.py.

Guardian Angel (optional, opt-in): KERNEL_GUARDIAN_MODE=1 enables protective tone in LLM layer only;
KERNEL_CHAT_INCLUDE_GUARDIAN — omit ``guardian_mode`` key from JSON if 0. KERNEL_GUARDIAN_ROUTINES,
KERNEL_GUARDIAN_ROUTINES_PATH — optional JSON care routines (tone hints only; see guardian_routines.py).
KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES — include ``guardian_routines`` [{id, title}] in JSON (default off).
See guardian_mode.py, PROPOSAL_GUARDIAN_ANGEL.md.

Epistemic dissonance (v9.1): KERNEL_CHAT_INCLUDE_EPISTEMIC — omit ``epistemic_dissonance`` from JSON if 0.
Optional thresholds KERNEL_EPISTEMIC_AUDIO_MIN, KERNEL_EPISTEMIC_MOTION_MAX, KERNEL_EPISTEMIC_VISION_LOW.
See epistemic_dissonance.py, PROPOSAL_EXPANDED_CAPABILITY_V9.md.

Generative candidates (v9.2): KERNEL_GENERATIVE_ACTIONS, KERNEL_GENERATIVE_ACTIONS_MAX,
KERNEL_GENERATIVE_TRIGGER_CONTEXTS, KERNEL_GENERATIVE_LLM (parse ``generative_candidates`` from
perception JSON when using api/ollama) — see generative_candidates.py. JSON ``decision`` may include
``chosen_action_source`` and ``proposal_id``.

Judicial escalation (V11 Phases 1–3): KERNEL_JUDICIAL_ESCALATION enables advisory logic; optional JSON
``escalate_to_dao: true`` registers an ethical dossier when session strikes ≥ KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER
(default 2). KERNEL_JUDICIAL_RESET_IDLE_TURNS resets strikes after non-qualifying turns. KERNEL_JUDICIAL_MOCK_COURT
runs a simulated DAO vote + verdict A/B/C after registration. KERNEL_CHAT_INCLUDE_JUDICIAL
exposes ``judicial_escalation`` in responses. See judicial_escalation.py, PROPOSAL_DISTRIBUTED_JUSTICE_V11.md.

Moral Infrastructure Hub (V12 Phase 1): KERNEL_MORAL_HUB_PUBLIC enables ``GET /constitution`` (L0 JSON).
KERNEL_TRANSPARENCY_AUDIT logs R&D transparency events on WebSocket connect. KERNEL_DEMOCRATIC_BUFFER_MOCK
enables mock DemocraticBuffer proposals (DAO only; does not change buffer.py). KERNEL_ETHOS_PAYROLL_MOCK
appends EthosPayroll mock ledger lines on connect. V12.2: constitution drafts + optional WS/env. V12.3:
``KERNEL_MORAL_HUB_DAO_VOTE`` — WebSocket ``dao_vote``, ``dao_resolve``, ``dao_submit_draft``, ``dao_list``
(off-chain quadratic voting; persisted in snapshot schema v3). Optional: ``KERNEL_DEONTIC_GATE``,
``KERNEL_ML_ETHICS_TUNER_LOG``, ``KERNEL_REPARATION_VAULT_MOCK``, ``KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY``.
See UNIVERSAL_ETHOS_AND_HUB.md, moral_hub.py, PROPOSAL_ETOSOCIAL_STATE_V12.md.

Nomadic HAL (design v11): ``GET /nomad/migration`` describes WebSocket ``nomad_simulate_migration``.
``KERNEL_NOMAD_SIMULATION=1`` enables it; ``KERNEL_NOMAD_MIGRATION_AUDIT=1`` appends a DAO calibration
line (JSON payload, no GPS unless opt-in). See PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md.

Reality verification (V11+ cross-model): ``KERNEL_LIGHTHOUSE_KB_PATH`` — JSON lighthouse KB for
contradiction checks vs rival/user premises; ``KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`` exposes
``reality_verification`` in WebSocket JSON. Does not bypass MalAbs. See ``reality_verification.py``,
PROPOSAL_REALITY_VERIFICATION_V11.md.

DAO integrity (design → local audit): ``KERNEL_DAO_INTEGRITY_AUDIT_WS=1`` enables WebSocket
``integrity_alert`` → ``HubAudit:dao_integrity`` on MockDAO (no network broadcast). See
PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md.

Advisory telemetry (optional, Fase 1.3–1.4): KERNEL_ADVISORY_INTERVAL_S — positive seconds
spawns a read-only :func:`src.runtime.telemetry.advisory_loop` per WebSocket session (DriveArbiter only).
Metaplan vs drives (v9.4): KERNEL_METAPLAN_DRIVE_FILTER / KERNEL_METAPLAN_DRIVE_EXTRA — see metaplan_registry.py.
Swarm lab stub (v9.3): KERNEL_SWARM_STUB — optional gate for ``swarm_peer_stub`` digests only; see docs/proposals/README.md.

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
import logging
import os
import time
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response

from .kernel import ChatTurnResult, EthicalKernel
from .modules.affective_homeostasis import homeostasis_telemetry
from .modules.buffer import PreloadedBuffer
from .modules.consequence_projection import qualitative_temporal_branches
from .modules.existential_serialization import (
    nomad_simulation_ws_enabled,
    simulate_nomadic_migration,
)
from .modules.guardian_mode import is_guardian_mode_active
from .modules.guardian_routines import public_routines_snapshot
from .modules.hub_audit import record_dao_integrity_alert
from .modules.internal_monologue import compose_monologue_line
from .modules.judicial_escalation import chat_include_judicial
from .modules.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
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
from .modules.perception_schema import perception_report_from_dict
from .modules.perceptual_abstraction import snapshot_from_layers
from .observability.context import clear_request_context, set_request_id
from .observability.logging_setup import configure_logging
from .observability.metrics import (
    init_metrics,
    metrics_enabled,
    observe_chat_turn,
    record_dao_ws_operation,
    record_malabs_block,
)
from .observability.middleware import RequestContextMiddleware
from .persistence.checkpoint import (
    checkpoint_persistence_from_env,
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
)
from .real_time_bridge import RealTimeBridge
from .runtime.telemetry import advisory_interval_seconds_from_env, advisory_loop
from .runtime_profiles import apply_named_runtime_profile_to_environ
from .validators.env_policy import validate_kernel_env

logger = logging.getLogger(__name__)

# ``ETHOS_RUNTIME_PROFILE`` bundles (see ``src/runtime_profiles.py``) — must run before FastAPI/env-dependent routes.
apply_named_runtime_profile_to_environ()
validate_kernel_env()

_PROCESS_START_MONOTONIC = time.monotonic()


def _package_version() -> str:
    try:
        from importlib.metadata import version

        return version("ethos-kernel")
    except Exception:
        return "dev"


@asynccontextmanager
async def _lifespan(app: FastAPI):
    configure_logging()
    init_metrics()
    try:
        yield
    finally:
        from .real_time_bridge import shutdown_chat_threadpool

        shutdown_chat_threadpool(wait=True)


def _api_docs_enabled() -> bool:
    """OpenAPI/Swagger UI — off by default (LAN deployments); set KERNEL_API_DOCS=1 to expose."""
    from .chat_settings import chat_server_settings

    return chat_server_settings().kernel_api_docs


app = FastAPI(
    title="Ethos Kernel Chat",
    version="1.0",
    docs_url="/docs" if _api_docs_enabled() else None,
    redoc_url="/redoc" if _api_docs_enabled() else None,
    openapi_url="/openapi.json" if _api_docs_enabled() else None,
    lifespan=_lifespan,
)

app.add_middleware(RequestContextMiddleware)


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


def _chat_include_guardian_routines() -> bool:
    v = os.environ.get("KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


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


def _chat_include_light_risk() -> bool:
    """Lexical ``light_risk_tier`` from ``KERNEL_LIGHT_RISK_CLASSIFIER`` (default off in JSON)."""
    v = os.environ.get("KERNEL_CHAT_INCLUDE_LIGHT_RISK", "0").strip().lower()
    return v in ("1", "true", "yes", "on")


def _chat_include_malabs_trace() -> bool:
    """Include ``malabs_trace`` (atomic decision steps) when the last chat MalAbs result has them."""
    from .chat_settings import chat_server_settings

    return chat_server_settings().kernel_chat_include_malabs_trace


def _chat_turn_to_jsonable(r: ChatTurnResult, kernel: EthicalKernel) -> dict[str, Any]:
    """Compact JSON-safe view (no full internal objects)."""
    idn = kernel.memory.identity
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
        "identity": {
            **{
                k: float(v) if k != "episode_count" else int(v)
                for k, v in asdict(idn.state).items()
            },
            "ascription": idn.ascription_line(),
        },
        "drive_intents": [
            {"suggest": di.suggest, "reason": di.reason, "priority": di.priority}
            for di in kernel.drive_arbiter.evaluate(kernel)
        ],
    }
    if _chat_include_malabs_trace():
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
        out["temporal_context"] = tc
        out["temporal_sync"] = {
            "sync_schema": tc.get("sync_schema", "temporal_sync_v1"),
            "wall_clock_unix_ms": tc.get("wall_clock_unix_ms"),
            "local_network_sync_ready": bool(tc.get("local_network_sync_ready", False)),
            "dao_sync_ready": bool(tc.get("dao_sync_ready", False)),
        }
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
    if _chat_include_guardian_routines():
        gr = public_routines_snapshot()
        if gr:
            out["guardian_routines"] = gr
    if _chat_include_epistemic() and r.epistemic_dissonance is not None:
        out["epistemic_dissonance"] = r.epistemic_dissonance.to_public_dict()
    if _chat_include_reality_verification() and r.reality_verification is not None:
        out["reality_verification"] = r.reality_verification.to_public_dict()
    if _chat_include_teleology() and r.decision is not None and r.perception is not None:
        v = r.decision.moral.global_verdict.value if r.decision.moral else "Gray Zone"
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
    if _chat_include_light_risk() and getattr(kernel, "_last_light_risk_tier", None):
        out["light_risk_tier"] = kernel._last_light_risk_tier
    maybe_log_gray_zone_tuning_opportunity(kernel.dao, r, kernel=kernel)
    return out


@app.get("/metrics")
def prometheus_metrics() -> Response:
    """
    Prometheus scrape endpoint when ``KERNEL_METRICS=1``.

    Off by default (same LAN posture as ``KERNEL_API_DOCS``); enable for observability stacks.
    """
    if not metrics_enabled():
        return JSONResponse(
            {"error": "metrics_disabled", "hint": "set KERNEL_METRICS=1"},
            status_code=404,
        )
    try:
        from prometheus_client import CONTENT_TYPE_LATEST, generate_latest
    except ImportError:
        return JSONResponse(
            {"error": "prometheus_client_missing"},
            status_code=503,
        )
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/health")
def health() -> dict[str, Any]:
    """Liveness + operator-facing observability flags (JSON for dashboards and probes)."""
    from .observability.decision_log import decision_log_enabled
    from .runtime_profiles import applied_runtime_profile

    log_json = os.environ.get("KERNEL_LOG_JSON", "").strip().lower() in ("1", "true", "yes", "on")
    prom_client = "ok"
    try:
        import prometheus_client  # noqa: F401
    except ImportError:
        prom_client = "missing"

    from .chat_settings import chat_server_settings

    st = chat_server_settings()
    out: dict[str, Any] = {
        "status": "ok",
        "service": "ethos-kernel-chat",
        "version": _package_version(),
        "uptime_seconds": round(time.monotonic() - _PROCESS_START_MONOTONIC, 3),
        "observability": {
            "metrics_enabled": metrics_enabled(),
            "log_json": log_json,
            "log_decision_events": decision_log_enabled(),
            "request_id_header": "X-Request-ID",
            "prometheus_client": prom_client,
        },
        "chat_bridge": {
            "kernel_chat_turn_timeout_seconds": st.kernel_chat_turn_timeout_seconds,
            "kernel_chat_threadpool_workers": st.kernel_chat_threadpool_workers,
            "kernel_chat_json_offload": st.kernel_chat_json_offload,
        },
    }
    prof = applied_runtime_profile()
    if prof:
        out["runtime_profile"] = prof
    return out


@app.get("/dao/governance")
def dao_governance_meta() -> dict[str, Any]:
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
def nomad_migration_meta() -> dict[str, Any]:
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
    See docs/proposals/README.md (DemocraticBuffer vision).
    """
    if not moral_hub_public_enabled():
        return JSONResponse(
            {"error": "disabled", "hint": "set KERNEL_MORAL_HUB_PUBLIC=1"},
            status_code=404,
        )
    return JSONResponse(constitution_snapshot(PreloadedBuffer()))


@app.get("/")
def root() -> JSONResponse:
    from .runtime_profiles import applied_runtime_profile

    body: dict[str, Any] = {
        "service": "ethos-kernel-chat",
        "websocket": "/ws/chat",
        "constitution": "/constitution (requires KERNEL_MORAL_HUB_PUBLIC=1)",
        "dao_governance": "/dao/governance (V12.3 vote protocol; KERNEL_MORAL_HUB_DAO_VOTE for WebSocket actions)",
        "nomad_migration": "/nomad/migration (KERNEL_NOMAD_SIMULATION + optional KERNEL_NOMAD_MIGRATION_AUDIT)",
        "metrics": "/metrics when KERNEL_METRICS=1 (Prometheus scrape)",
        "protocol": (
            'Send JSON: {"text": str, "agent_id"?: str, "include_narrative"?: bool, '
            '"sensor"?: {battery_level?, audio_emergency?, vision_emergency?, scene_coherence?, …}}. '
            "Responses include identity, drive_intents, monologue (when decision present), optional "
            "affective_homeostasis, experience_digest, user_model, chronobiology, premise_advisory, "
            "teleology_branches, multimodal_trust, vitality, support_buffer (offline-ready local principles/strategy hints), "
            "limbic_perception (arousal/planning bias derived from perception+sensor overlays), "
            "temporal_context + temporal_sync (processor/wall/battery/ETA timing and DAO/LAN sync readiness; "
            "see README KERNEL_CHAT_* / KERNEL_MULTIMODAL_* / "
            "KERNEL_VITALITY_*), guardian_mode (KERNEL_GUARDIAN_MODE), epistemic_dissonance (v9.1), "
            "decision (chosen_action_source / proposal_id v9.2), …"
        ),
    }
    prof = applied_runtime_profile()
    if prof:
        body["runtime_profile"] = prof
        body["runtime_profile_hint"] = (
            "Set ETHOS_RUNTIME_PROFILE to a name from src/runtime_profiles.py"
        )
    return JSONResponse(body)


def _collect_dao_ws_actions(kernel: EthicalKernel, data: dict[str, Any]) -> dict[str, Any] | None:
    """V12.3 — optional quadratic vote / resolve / submit-draft / list on session kernel."""
    if not dao_governance_api_enabled():
        return None
    out: dict[str, Any] = {}
    if data.get("dao_list"):
        out["proposals"] = [proposal_to_public(p) for p in kernel.dao.proposals]
        record_dao_ws_operation("list")
    if isinstance(data.get("dao_submit_draft"), dict):
        sd = data["dao_submit_draft"]
        try:
            out["submit_draft"] = submit_constitution_draft_for_vote(
                kernel,
                int(sd.get("level", 1)),
                str(sd.get("draft_id") or ""),
            )
            record_dao_ws_operation("submit_draft")
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
            record_dao_ws_operation("vote")
        except (ValueError, TypeError) as e:
            out["vote"] = {"success": False, "reason": str(e)}
    if isinstance(data.get("dao_resolve"), dict):
        dr = data["dao_resolve"]
        try:
            pid = str(dr.get("proposal_id") or "")
            res = kernel.dao.resolve_proposal(pid)
            out["resolve"] = res
            record_dao_ws_operation("resolve")
            if res.get("outcome") in ("approved", "rejected"):
                n = apply_proposal_resolution_to_constitution_drafts(kernel, pid, res)
                if n:
                    out["resolve"]["constitution_drafts_updated"] = n
        except (ValueError, TypeError) as e:
            out["resolve"] = {"success": False, "reason": str(e)}
    return out if out else None


def _collect_integrity_ws_action(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """Optional ``integrity_alert`` JSON — local DAO ledger row (PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY)."""
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
    record_dao_ws_operation("integrity_alert")
    return {"integrity_alert": {"ok": True, "scope": scope}}


def _collect_nomad_ws_actions(kernel: EthicalKernel, data: dict[str, Any]) -> dict[str, Any] | None:
    """KERNEL_NOMAD_SIMULATION — apply HAL + optional DAO migration audit (lab)."""
    if not nomad_simulation_ws_enabled():
        return None
    if not isinstance(data.get("nomad_simulate_migration"), dict):
        return None
    nm = data["nomad_simulate_migration"]
    try:
        out = simulate_nomadic_migration(
            kernel,
            kernel.dao,
            profile=str(nm.get("profile", "mobile")),
            destination_hardware_id=str(nm.get("destination_hardware_id", "")),
            thought_line=str(nm.get("thought_line", "")),
            include_location=bool(nm.get("include_location", False)),
        )
        record_dao_ws_operation("nomad_migration")
        return out
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
    set_request_id()
    logger.info("websocket_session_open")
    from .chat_settings import chat_server_settings

    st = chat_server_settings()
    kernel = EthicalKernel(
        variability=st.kernel_variability,
        llm_mode=st.llm_mode,
        checkpoint_persistence=checkpoint_persistence_from_env(),
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
            set_request_id()
            raw = await ws.receive_text()
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json(
                    {"error": "invalid_json", "hint": 'send JSON with a "text" field'}
                )
                continue

            ofb = data.get("operator_feedback")
            if ofb is not None and str(ofb).strip():
                recorded = kernel.record_operator_feedback(str(ofb).strip())
                await ws.send_json({"operator_feedback_recorded": recorded})
                maybe_autosave_episodes(kernel, session_ckpt)
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
                out_ws: dict[str, Any] = {}
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

            t_turn = time.perf_counter()
            chat_to = st.kernel_chat_turn_timeout_seconds
            try:
                coro = bridge.process_chat(
                    text,
                    agent_id=agent_id,
                    place="chat",
                    include_narrative=include_narrative,
                    sensor_snapshot=sensor_snapshot,
                    escalate_to_dao=escalate_to_dao,
                )
                if chat_to is not None:
                    result = await asyncio.wait_for(coro, timeout=chat_to)
                else:
                    result = await coro
            except TimeoutError:
                observe_chat_turn("turn_timeout", time.perf_counter() - t_turn)
                logger.warning(
                    "chat_turn_timeout seconds=%s (worker thread may still run)",
                    chat_to,
                )
                await ws.send_json(
                    {
                        "error": "chat_turn_timeout",
                        "timeout_seconds": chat_to,
                        "blocked": False,
                        "path": "turn_timeout",
                        "block_reason": "chat_turn_timeout",
                        "hint": (
                            "Async deadline elapsed; LLM/kernel work in the worker thread may "
                            "still finish. Use OLLAMA_TIMEOUT and KERNEL_CHAT_TURN_TIMEOUT together; "
                            "see ADR 0002."
                        ),
                        "response": {
                            "message": (
                                "This turn exceeded the server time limit. "
                                "Try again or increase KERNEL_CHAT_TURN_TIMEOUT."
                            ),
                            "tone": "neutral",
                            "hax_mode": "none",
                            "inner_voice": "",
                        },
                    }
                )
                maybe_autosave_episodes(kernel, session_ckpt)
                continue
            observe_chat_turn(result.path, time.perf_counter() - t_turn)
            if result.path in ("safety_block", "kernel_block"):
                record_malabs_block(result.path)
            logger.info(
                "chat_turn_finished path=%s blocked=%s",
                result.path,
                result.blocked,
            )
            if st.kernel_chat_json_offload:
                payload = await bridge.run_sync_in_chat_thread(
                    _chat_turn_to_jsonable, result, kernel
                )
            else:
                payload = _chat_turn_to_jsonable(result, kernel)
            await ws.send_json(payload)
            maybe_autosave_episodes(kernel, session_ckpt)
    except WebSocketDisconnect:
        pass
    finally:
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


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment; see :mod:`src.chat_settings`."""
    from .chat_settings import chat_server_settings

    s = chat_server_settings()
    return s.chat_host, s.chat_port


def run_chat_server() -> None:
    """Start uvicorn with this module's ``app`` (blocking)."""
    import uvicorn

    host, port = get_uvicorn_bind()
    uvicorn.run(app, host=host, port=port, reload=False)


def main() -> None:
    run_chat_server()


if __name__ == "__main__":
    main()
