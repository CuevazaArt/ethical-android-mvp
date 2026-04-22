"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
Or: python -m src.runtime  (same server; see docs/proposals/README.md)

**Profiles:** set ``ETHOS_RUNTIME_PROFILE`` to a name in ``src/runtime_profiles.py`` to merge that bundle at import time (explicit env vars win per key). ``GET /health`` and ``GET /`` include ``runtime_profile`` when set; ``GET /health`` also returns ``llm_degradation`` (resolved perception / verbal / monologue policies — see ``PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md``) and ``nomad_bridge`` (queue depths + telemetry **key names** from ``NomadBridge.public_queue_stats()`` — Module S.1 / S.2.1 observability).

**Inbound size cap:** ``KERNEL_CHAT_WS_MAX_MESSAGE_BYTES`` (default 2 MiB, cap 32 MiB) rejects oversize
WebSocket text frames with ``error=message_too_large`` before ``json.loads`` (Module 0.2.1 hardening).

**Chat async bridge:** WebSocket ``/ws/chat`` streams via ``RealTimeBridge.process_chat_stream`` → ``EthicalKernel.process_chat_turn_stream`` on the asyncio loop (see ``RealTimeBridge``). Non-WebSocket callers using ``RealTimeBridge.process_chat`` may run ``process_chat_turn`` in a worker thread unless ``KERNEL_CHAT_ASYNC_LLM_HTTP=1`` (or tri-lobe) selects ``process_chat_turn_async`` on the loop with async ``httpx``. The per-turn cancel ``Event`` binds cooperative LLM HTTP cancellation + ``llm_http_cancel`` scope for the thread that runs ``EthicalKernel.process`` when applicable (ADR 0002). Optional ``KERNEL_CHAT_THREADPOOL_WORKERS`` dedicates a ``ThreadPoolExecutor`` for chat offload. ``KERNEL_CHAT_TURN_TIMEOUT`` bounds each **async** wait on the next stream chunk and returns JSON ``error=chat_turn_timeout`` when exceeded (cancel ``Event``, stream ``aclose``, then ``abandon_chat_turn``). ``KERNEL_CHAT_JSON_OFFLOAD`` builds WebSocket JSON in the offload path so the loop stays responsive. See ``src/real_time_bridge.py``, ADR 0002, and ``docs/proposals/README.md``.

OpenAPI/Swagger: **off** by default; set KERNEL_API_DOCS=1 to expose ``/docs``, ``/redoc``, ``/openapi.json`` (see README).

Checkpoint (optional): ``KERNEL_CHECKPOINT_PATH`` attaches ``JsonFileCheckpointAdapter`` via
``checkpoint_persistence_from_env()``; ``KERNEL_CHECKPOINT_LOAD``,
``KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT``, ``KERNEL_CHECKPOINT_EVERY_N_EPISODES`` — see src/persistence/checkpoint.py

Conduct guide export (optional): KERNEL_CONDUCT_GUIDE_EXPORT_PATH — JSON on WebSocket disconnect
(after checkpoint); KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT — see src/modules/conduct_guide_export.py

Situated v8 (optional): KERNEL_SENSOR_FIXTURE (path to JSON), KERNEL_SENSOR_PRESET (name from
perceptual_abstraction.SENSOR_PRESETS) — merged before client ``sensor`` JSON; see PROPOSAL_SITUATED_ORGANISM_V8.md.
Optional ``KERNEL_SENSOR_INPUT_STRICT=1`` rejects unknown keys / bad types in the merged sensor object
(``error=sensor_payload_invalid`` on WebSocket); see PROPOSAL_SENSOR_FUSION_NORMALIZATION.md.

Multimodal thresholds (optional): KERNEL_MULTIMODAL_AUDIO_STRONG, KERNEL_MULTIMODAL_VISION_SUPPORT,
KERNEL_MULTIMODAL_SCENE_SUPPORT, KERNEL_MULTIMODAL_VISION_CONTRADICT, KERNEL_MULTIMODAL_SCENE_CONTRADICT
— see README / multimodal_trust.thresholds_from_env.

Vitality (optional): KERNEL_VITALITY_CRITICAL_BATTERY, KERNEL_VITALITY_CRITICAL_TEMP, KERNEL_VITALITY_WARNING_TEMP,
KERNEL_VITALITY_THERMAL_HYSTERESIS, KERNEL_VITALITY_THERMAL_HYSTERESIS_C, KERNEL_CHAT_INCLUDE_VITALITY — see vitality.py.
Nomad S.2.1: ``KERNEL_NOMAD_TELEMETRY_VITALITY`` (default on) merges last Nomad ``telemetry`` into the sensor snapshot before vitality when fields are missing — see ``vitality.merge_nomad_telemetry_into_snapshot`` / ``vitality.apply_nomad_telemetry_if_enabled``.

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

LAN governance merge (Phase 2): ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` (with integrity audit on)
enables WebSocket ``lan_governance_integrity_batch`` — deterministic sort/dedupe via
``lan_governance_event_merge``, then one ledger row per merged event. DJ-BL-02.

LAN governance DAO batch (Phase 2): ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` (with DAO vote on)
enables WebSocket ``lan_governance_dao_batch`` — deterministic sort/dedupe via
``lan_governance_event_merge``, then applies ``dao_vote`` / ``dao_resolve`` on the session MockDAO. DJ-BL-05.

LAN governance judicial batch (Phase 2): ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` (with judicial escalation on)
enables WebSocket ``lan_governance_judicial_batch`` — deterministic sort/dedupe via
``lan_governance_event_merge``, then registers escalation dossiers on the session audit ledger. DJ-BL-06.

LAN governance mock court batch (Phase 2): ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` (with judicial+mock-court on)
enables WebSocket ``lan_governance_mock_court_batch`` — deterministic sort/dedupe via
``lan_governance_event_merge``, then runs simulated tribunal outcomes.

LAN governance envelope (Phase 2): optional ``lan_governance_envelope`` with
``schema=lan_governance_envelope_v1`` routes batch payloads by ``kind`` to the same handlers
(``integrity_batch``, ``dao_batch``, ``judicial_batch``, ``mock_court_batch``).

LAN governance coordinator (Phase 2): optional ``lan_governance_coordinator`` with
``schema=lan_governance_coordinator_v1`` carries multiple envelope payloads; the server sorts by
envelope fingerprint, dedupes identical envelopes, and applies each in order (hub / multi-node stub).

Advisory telemetry (optional, Fase 1.3–1.4): KERNEL_ADVISORY_INTERVAL_S — positive seconds
spawns a read-only :func:`src.runtime.telemetry.advisory_loop` per WebSocket session (DriveArbiter only).
Metaplan vs drives (v9.4): KERNEL_METAPLAN_DRIVE_FILTER / KERNEL_METAPLAN_DRIVE_EXTRA — see metaplan_registry.py.
Swarm lab stub (v9.3): KERNEL_SWARM_STUB — optional gate for ``swarm_peer_stub`` digests only; see docs/proposals/README.md.

Privacy (robustez pilar 5): KERNEL_CHAT_EXPOSE_MONOLOGUE — if 0/false/no/off, the ``monologue``
field is omitted from content (empty string) and LLM embellishment is skipped.

Homeostasis UX (pilar 4): KERNEL_CHAT_INCLUDE_HOMEOSTASIS — if 0/false/no/off, omit
``affective_homeostasis`` (σ / strain / PAD advisory; does not change decisions).

Embodied sociability S10: KERNEL_CHAT_INCLUDE_TRANSPARENCY_S10 — if 0/false/no/off, omit
``transparency_s10`` (S10.1 narration, S10.2 withdrawal / non-intervention hints, S10.3 discomfort throttle, S10.4 help-request codes; see ``src/modules/transparency_s10.py``). Optional signal key ``silence`` in the merged perception/sensor path refines S10.2 when present.

Experience digest (pilar 3): KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST — if 0, omit
``experience_digest`` (semantic line from last Ψ Sleep; additive, not a policy change).
"""

from __future__ import annotations

__copyright_integrity__ = "cuevaza::arq.jvof"

import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .observability.middleware import RequestContextMiddleware
from .runtime.chat_feature_flags import coerce_public_int
from .runtime.chat_lifecycle import api_docs_enabled, chat_lifespan
from .runtime_profiles import apply_named_runtime_profile_to_environ
from .server.routes_field_control import router as field_control_http_router
from .server.routes_governance import router as governance_http_router
from .server.routes_health import router as health_http_router
from .server.routes_nomad import router as nomad_http_router
from .server.ws_chat import (  # noqa: F401
    _chat_turn_to_jsonable,  # re-exported for `from src.chat_server import ...` in tests
)
from .server.ws_chat import (
    router as ws_chat_router,
)
from .server.ws_sidecar import router as ws_sidecar_router
from .validators.env_policy import validate_kernel_env

# Alias for tests / temporal JSON helpers (implementation: ``coerce_public_int``).
_coerce_public_int = coerce_public_int

logger = logging.getLogger(__name__)

# ``ETHOS_RUNTIME_PROFILE`` bundles (see ``src/runtime_profiles.py``) — must run before FastAPI/env-dependent routes.
apply_named_runtime_profile_to_environ()
validate_kernel_env()

app = FastAPI(
    title="Ethos Kernel Chat",
    version="1.0",
    docs_url="/docs" if api_docs_enabled() else None,
    redoc_url="/redoc" if api_docs_enabled() else None,
    openapi_url="/openapi.json" if api_docs_enabled() else None,
    lifespan=chat_lifespan,
)

# Mounting Nomad Bridge (Fase 8+ / Módulo S)
from .modules.nomad_bridge import get_nomad_bridge

app.mount("/nomad_bridge", get_nomad_bridge().app)

app.add_middleware(RequestContextMiddleware)

app.include_router(health_http_router)
app.include_router(governance_http_router)
app.include_router(nomad_http_router)
app.include_router(field_control_http_router)
app.include_router(ws_sidecar_router)
app.include_router(ws_chat_router)

# Phase 10: Mount the Nomad PWA Client directly to bypass external web servers.
nomad_pwa_path = os.path.join(os.path.dirname(__file__), "clients", "nomad_pwa")
if os.path.exists(nomad_pwa_path):
    app.mount("/nomad", StaticFiles(directory=nomad_pwa_path, html=True), name="nomad_pwa")
    logger.info("Nomad PWA Interface mounted at /nomad/")
else:
    logger.warning("Nomad PWA Interface not found at %s. Skipping mount.", nomad_pwa_path)

# Phase 12: Mount Prometheus Metrics if enabled
try:
    if os.environ.get("KERNEL_METRICS", "1").strip().lower() in ("1", "true", "on"):
        from prometheus_client import make_asgi_app

        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        logger.info("Prometheus metrics endpoint mounted at /metrics")
except ImportError:
    logger.warning("prometheus_client not installed, skipping /metrics")

# Phase 10 (V2): Mount the L0 Visual Dashboard
dashboard_path = os.path.join(os.path.dirname(__file__), "static", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="l0_dashboard")
    logger.info("L0 Dashboard mounted at /dashboard/")
else:
    logger.warning("L0 Dashboard not found at %s. Skipping mount.", dashboard_path)

# Phase 13.1: Mount Clinical UI
clinical_path = os.path.join(os.path.dirname(__file__), "static", "clinical")
if os.path.exists(clinical_path):
    app.mount("/clinical", StaticFiles(directory=clinical_path, html=True), name="clinical_ui")
    logger.info("Clinical UI mounted at /clinical/")

# Phase 13.2: Mount Master Orchestrator (Mission Control)
master_path = os.path.join(os.path.dirname(__file__), "static", "master")
if os.path.exists(master_path):
    app.mount("/master", StaticFiles(directory=master_path, html=True), name="master_orchestrator")
    logger.info("Master Orchestrator mounted at /master/")


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment; see :mod:`src.chat_settings`."""
    from .settings import kernel_settings

    s = kernel_settings()
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
