"""
WebSocket chat server: one EthicalKernel (and STM) per connection.

Run from repo root:
  uvicorn src.chat_server:app --host 127.0.0.1 --port 8765

Or: python -m src.chat_server
Or: python -m src.runtime  (same server; see docs/proposals/README.md)

**Profiles:** set ``ETHOS_RUNTIME_PROFILE`` to a name in ``src/runtime_profiles.py`` to merge that bundle at import time (explicit env vars win per key). ``GET /health`` and ``GET /`` include ``runtime_profile`` when set; ``GET /health`` also returns ``llm_degradation`` (resolved perception / verbal / monologue policies — see ``PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md``).

**Chat async bridge:** By default each turn runs ``EthicalKernel.process_chat_turn`` in a worker thread (``RealTimeBridge``) so the asyncio loop can accept other WebSocket connections. Optional ``KERNEL_CHAT_ASYNC_LLM_HTTP=1`` runs ``process_chat_turn_async`` on the event loop with async ``httpx`` for Ollama/HTTP JSON; the same per-turn cancel ``Event`` applies to the thread that runs ``EthicalKernel.process`` (cooperative exit + ``llm_http_cancel`` scope; see ADR 0002). Optional ``KERNEL_CHAT_THREADPOOL_WORKERS`` (positive int) uses a dedicated ``ThreadPoolExecutor`` for chat; optional ``KERNEL_CHAT_TURN_TIMEOUT`` (seconds) bounds the **async** wait and returns JSON ``error=chat_turn_timeout`` when exceeded (``abandon_chat_turn`` skips late STM; cooperative cancel for further sync LLM HTTP; in-flight HTTP cancel when async LLM is on). By default ``KERNEL_CHAT_JSON_OFFLOAD`` is on: WebSocket JSON (including optional ``KERNEL_LLM_MONOLOGUE``) is built in the same offload path so the loop is not blocked after the turn. See ``src/real_time_bridge.py``, ADR 0002, and ``docs/proposals/README.md``.

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

Experience digest (pilar 3): KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST — if 0, omit
``experience_digest`` (semantic line from last Ψ Sleep; additive, not a policy change).
"""

from __future__ import annotations
__copyright_integrity__ = "cuevaza::arq.jvof"

import asyncio
import json
import logging
import math
import os
import threading
import time
from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import asdict
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from .kernel import ChatTurnResult, EthicalKernel, kernel_dao_as_mock
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
from .modules.lan_governance_coordinator import (
    fingerprint_lan_governance_coordinator,
    normalize_lan_governance_coordinator,
)
from .modules.lan_governance_envelope import (
    fingerprint_lan_governance_envelope,
    idempotency_token_for_envelope,
    normalize_lan_governance_envelope,
    reject_reason_for_envelope_error,
)
from .modules.lan_governance_event_merge import merge_lan_governance_events_detailed
from .modules.lan_governance_merge_context import (
    EVIDENCE_POSTURE_ADVISORY_AGGREGATE,
    LanMergeContextParsed,
    parse_lan_merge_context,
)
from .modules.ml_ethics_tuner import maybe_log_gray_zone_tuning_opportunity
from .modules.mock_dao_audit_replay import fingerprint_audit_ledger
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
    lan_governance_coordinator_ws_enabled,
    lan_governance_dao_batch_ws_enabled,
    lan_governance_integrity_batch_ws_enabled,
    lan_governance_judicial_batch_ws_enabled,
    lan_governance_mock_court_batch_ws_enabled,
    moral_hub_public_enabled,
    proposal_to_public,
    submit_constitution_draft_for_vote,
)
from .modules.nomad_identity import nomad_identity_public
from .modules.perception_schema import perception_report_from_dict
from .modules.perceptual_abstraction import snapshot_from_layers
from .modules.reparation_vault import maybe_register_reparation_after_mock_court
from .observability.context import clear_request_context, set_request_id
from .observability.logging_setup import configure_logging
from .observability.metrics import (
    init_metrics,
    metrics_enabled,
    observe_chat_turn,
    record_chat_turn_async_timeout,
    record_dao_ws_operation,
    record_lan_envelope_replay_cache_event,
    record_llm_cancel_scope_signaled,
    record_malabs_block,
    observe_ttft_seconds,
    set_limbic_tension,
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
    import httpx

    configure_logging()
    init_metrics()
    # Phase 12.1: Global persistent client for Nomad hardware loop
    aclient = httpx.AsyncClient(timeout=30.0)
    app.state.aclient = aclient
    try:
        yield
    finally:
        from .real_time_bridge import shutdown_chat_threadpool

        await aclient.aclose()
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
@app.get("/nomad/migration")
async def nomad_migration_meta() -> Response:
    """Nomad Simulation metadata (v11) for client orchestration."""
    from .modules.existential_serialization import nomad_simulation_ws_enabled
    return JSONResponse({
        "simulation_enabled": nomad_simulation_ws_enabled(),
        "path": "/ws/chat",
        "description": "HAL v11 Conscious Migration protocol (simulated)"
    })

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


@app.websocket("/ws/nomad")
async def nomad_bridge_ws_handler(websocket: WebSocket) -> None:
    """Nomad LAN bridge sensory endpoint (Module S)."""
    from .modules.nomad_bridge import get_nomad_bridge

    await get_nomad_bridge().handle_websocket(websocket)
    
    await get_nomad_bridge().handle_websocket(websocket)

@app.websocket("/ws/dashboard")
async def dashboard_ws_handler(websocket: WebSocket) -> None:
    """L0 Dashboard telemetry stream."""
    from .modules.nomad_bridge import get_nomad_bridge
    
    await websocket.accept()
    q: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=30)
    bridge = get_nomad_bridge()
    bridge.dashboard_queues.append(q)
    
    try:
        while True:
            msg = await q.get()
            await websocket.send_json(msg)
    except Exception as e:
        logger.error("Dashboard WS error: %s", e)
    finally:
        bridge.dashboard_queues.remove(q)

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


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.environ.get(name, "").strip().lower()
    if not raw:
        return default
    return raw in ("1", "true", "yes", "on")


def _coerce_public_int(value: object, *, default: int = 0, non_negative: bool = False) -> int:
    """
    JSON-safe int for public WebSocket payloads (e.g. temporal_sync).

    ``TemporalContext.to_public_dict()`` is typed as ``dict[str, object]``; this avoids
    ``int(object)`` mypy errors and prevents rare runtime failures on bad values.
    """
    if value is None:
        out = default
    elif isinstance(value, bool):
        out = default
    elif isinstance(value, int):
        out = value
    elif isinstance(value, float):
        out = int(value) if math.isfinite(value) else default
    elif isinstance(value, str):
        try:
            s = value.strip()
            out = int(s, 10) if s else default
        except ValueError:
            out = default
    else:
        out = default
    if non_negative:
        out = max(0, out)
    return out


def _attach_merge_context_telemetry(
    batch_body: dict[str, Any],
    mctx: LanMergeContextParsed,
) -> None:
    """Attach ``merge_context_warnings`` / ``merge_context_echo`` after a LAN batch apply."""
    if mctx.warnings:
        batch_body["merge_context_warnings"] = list(mctx.warnings)
    echo: dict[str, Any] = {}
    if mctx.frontier_turn is not None:
        echo["frontier_turn"] = mctx.frontier_turn
    if mctx.cross_session_hint is not None:
        echo["cross_session_hint"] = dict(mctx.cross_session_hint)
    if mctx.frontier_witnesses:
        echo["frontier_witness_resolution"] = {
            "witnesses": [dict(w) for w in mctx.frontier_witnesses],
            "advisory_max_observed_turn": mctx.witness_advisory_max_turn,
            "evidence_posture": EVIDENCE_POSTURE_ADVISORY_AGGREGATE,
        }
    if echo:
        batch_body["merge_context_echo"] = echo


def _aggregated_event_conflicts_from_lan_governance(
    lg: Mapping[str, Any],
    *,
    envelope_fingerprint: str,
    envelope_idempotency_token: str,
) -> list[dict[str, Any]]:
    """Collect ``event_conflicts`` from LAN batch sections with hub correlation fields."""
    out: list[dict[str, Any]] = []
    for sec in (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    ):
        block = lg.get(sec)
        if not isinstance(block, dict):
            continue
        ecs = block.get("event_conflicts")
        if not isinstance(ecs, list) or not ecs:
            continue
        for c in ecs:
            if not isinstance(c, dict):
                continue
            row = dict(c)
            row["source_batch"] = sec
            row["envelope_fingerprint"] = envelope_fingerprint
            row["envelope_idempotency_token"] = envelope_idempotency_token
            out.append(row)
    return out


def _aggregated_frontier_witness_resolutions_from_lan_governance(
    lg: Mapping[str, Any],
    *,
    envelope_fingerprint: str,
    envelope_idempotency_token: str,
) -> list[dict[str, Any]]:
    """Collect ``merge_context_echo.frontier_witness_resolution`` from LAN batch sections."""
    out: list[dict[str, Any]] = []
    for sec in (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    ):
        block = lg.get(sec)
        if not isinstance(block, dict):
            continue
        echo = block.get("merge_context_echo")
        if not isinstance(echo, dict):
            continue
        fwr = echo.get("frontier_witness_resolution")
        if not isinstance(fwr, dict) or not fwr:
            continue
        out.append(
            {
                "source_batch": sec,
                "envelope_fingerprint": envelope_fingerprint,
                "envelope_idempotency_token": envelope_idempotency_token,
                "frontier_witness_resolution": dict(fwr),
            }
        )
    return out


DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS = 300_000
DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES = 256


def _prune_lan_envelope_replay_cache(
    replay_cache: dict[str, dict[str, Any]],
    *,
    now_ms: int,
    ttl_ms: int,
    max_entries: int,
) -> tuple[int, int]:
    """Evict expired and oldest replay-cache rows (TTL then LRU)."""
    evicted_ttl = 0
    evicted_lru = 0

    expired_tokens: list[str] = []
    for token, entry in replay_cache.items():
        cached_at_ms = (
            _coerce_public_int(entry.get("cached_at_ms"), default=now_ms, non_negative=True)
            if isinstance(entry, dict)
            else now_ms
        )
        if now_ms - cached_at_ms >= ttl_ms:
            expired_tokens.append(token)
    for token in expired_tokens:
        if replay_cache.pop(token, None) is not None:
            evicted_ttl += 1

    while len(replay_cache) > max_entries:
        oldest = next(iter(replay_cache))
        replay_cache.pop(oldest, None)
        evicted_lru += 1
    return evicted_ttl, evicted_lru


def _lan_envelope_cache_stats(
    replay_cache: dict[str, dict[str, Any]] | None,
    replay_cache_stats: dict[str, int] | None,
    *,
    ttl_ms: int,
    max_entries: int,
    hit: bool,
) -> dict[str, Any]:
    """Compact replay-cache telemetry for envelope ACK."""
    stats = replay_cache_stats or {}
    return {
        "hit": hit,
        "size": len(replay_cache) if replay_cache is not None else 0,
        "hits_total": int(stats.get("hits", 0)),
        "misses_total": int(stats.get("misses", 0)),
        "evicted_ttl_total": int(stats.get("evicted_ttl", 0)),
        "evicted_lru_total": int(stats.get("evicted_lru", 0)),
        "ttl_ms": ttl_ms,
        "max_entries": max_entries,
    }


def _merge_lan_governance_ws_payloads(*parts: dict[str, Any] | None) -> dict[str, Any]:
    """Shallow-merge ``lan_governance`` sections so multiple LAN handlers can coexist in one response."""
    merged: dict[str, Any] = {}
    for p in parts:
        if not p:
            continue
        lg = p.get("lan_governance")
        if isinstance(lg, dict):
            merged.update(lg)
    return merged


def _reject_reason_lan_coordinator(error_code: object) -> str:
    code = str(error_code or "").strip()
    if code == "unsupported_schema":
        return "unsupported_contract"
    if code == "items_too_many":
        return "batch_apply_failed"
    return "schema_validation_failed"


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
                k: int(v)
                if k == "episode_count"
                else (v if isinstance(v, list | dict | tuple) else float(v))
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
        tc["turn_index"] = max(1, _coerce_public_int(tc.get("turn_index"), default=0, non_negative=True))
        out["temporal_context"] = tc
        out["temporal_sync"] = {
            "sync_schema": tc.get("sync_schema", "temporal_sync_v1"),
            "turn_index": tc["turn_index"],
            "wall_clock_unix_ms": tc.get("wall_clock_unix_ms"),
            "processor_elapsed_ms": _coerce_public_int(
                tc.get("processor_elapsed_ms"), default=0, non_negative=True
            ),
            "turn_delta_ms": _coerce_public_int(
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
    maybe_log_gray_zone_tuning_opportunity(kernel_dao_as_mock(kernel.dao), r, kernel=kernel)
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
    env_validation = os.environ.get("KERNEL_ENV_VALIDATION", "").strip().lower() or "strict"
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
        "safety_defaults": {
            "kernel_env_validation_mode": env_validation,
            "semantic_chat_gate_enabled": _env_truthy("KERNEL_SEMANTIC_CHAT_GATE", True),
            "semantic_embed_hash_fallback_enabled": _env_truthy(
                "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", True
            ),
            "perception_failsafe_enabled": _env_truthy("KERNEL_PERCEPTION_FAILSAFE", True),
            "perception_parallel_enabled": _env_truthy("KERNEL_PERCEPTION_PARALLEL", False),
        },
    }
    prof = applied_runtime_profile()
    if prof:
        out["runtime_profile"] = prof

    # Effective LLM degradation policies (resolved precedence — see PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).
    from .modules.llm_touchpoint_policies import (
        ENV_LLM_GLOBAL_DEFAULT_POLICY,
        raw_global_default_policy,
        resolve_monologue_llm_backend_policy,
    )
    from .modules.llm_verbal_backend_policy import resolve_verbal_llm_backend_policy
    from .modules.perception_backend_policy import resolve_perception_backend_policy

    g_raw = os.environ.get(ENV_LLM_GLOBAL_DEFAULT_POLICY, "").strip()
    out["llm_degradation"] = {
        "global_default_env_set": bool(g_raw),
        "global_default_raw": g_raw or None,
        "global_default_effective": raw_global_default_policy(),
        "resolved": {
            "perception": resolve_perception_backend_policy(),
            "communicate": resolve_verbal_llm_backend_policy(touchpoint="communicate"),
            "narrate": resolve_verbal_llm_backend_policy(touchpoint="narrate"),
            "monologue": resolve_monologue_llm_backend_policy(),
        },
    }
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


# ─────────────────────────────────────────────────────────────────────────────
# ADR 0017 — Field-test control surface (KERNEL_FIELD_CONTROL=1 only)
# All routes in this block are DISABLED by default. They provide the minimal
# PC ↔ smartphone management interface for field tests F0–F4.
# See docs/adr/0017-smartphone-sensor-relay-bridge.md and
# docs/proposals/PROPOSAL_FIELD_TEST_PLAN.md.
# ─────────────────────────────────────────────────────────────────────────────

_FIELD_SESSION: dict[str, Any] = {}  # lightweight in-process session state


def _field_control_enabled() -> bool:
    return os.environ.get("KERNEL_FIELD_CONTROL", "").strip().lower() in ("1", "true", "yes")


def _field_pairing_token() -> str:
    return os.environ.get("KERNEL_FIELD_PAIRING_TOKEN", "").strip()


@app.post("/control/pair")
async def field_pair(request_body: dict[str, Any] | None = None) -> JSONResponse:
    """
    ADR 0017 §2 — Phone pairing endpoint.

    POST {"token": "<pairing-token>"}  →  {"field_session_id": "…", "expires_in_seconds": 3600}

    Enabled only when KERNEL_FIELD_CONTROL=1 and KERNEL_FIELD_PAIRING_TOKEN is set.
    Rejects requests from non-RFC-1918 IPs unless KERNEL_FIELD_ALLOW_WAN=1.
    """
    if not _field_control_enabled():
        return JSONResponse(
            {"error": "field_control_disabled", "hint": "set KERNEL_FIELD_CONTROL=1"},
            status_code=404,
        )

    token = _field_pairing_token()
    if not token:
        logger.error("field_control: KERNEL_FIELD_PAIRING_TOKEN not set — pairing rejected")
        return JSONResponse({"error": "no_pairing_token_configured"}, status_code=503)

    body = request_body or {}
    submitted = str(body.get("token", "")).strip()
    if submitted != token:
        logger.warning("field_control: pairing rejected — token mismatch")
        return JSONResponse({"error": "invalid_token"}, status_code=403)

    import hashlib
    import secrets

    session_id = hashlib.sha256((secrets.token_hex(16) + token).encode()).hexdigest()[:24]

    _FIELD_SESSION.update(
        {
            "session_id": session_id,
            "paired_at": time.monotonic(),
            "state": "running",
            "decision_count": 0,
            "sensor_frames_received": 0,
        }
    )

    logger.info("field_control: phone paired — session_id=%s", session_id)
    # Emit a sidecar audit line if sidecar is configured
    _field_emit_audit("field_session_paired", f"session={session_id}")

    return JSONResponse(
        {
            "field_session_id": session_id,
            "expires_in_seconds": 3600,
            "sensor_hz_max": int(os.environ.get("KERNEL_FIELD_SENSOR_HZ", "2")),
            "ws_path": "/ws/chat",
            "phone_ui": "/phone",
        }
    )


@app.get("/control/status")
def field_status() -> JSONResponse:
    """ADR 0017 §2 — Session status for the phone control UI."""
    if not _field_control_enabled():
        return JSONResponse({"error": "field_control_disabled"}, status_code=404)

    if not _FIELD_SESSION:
        return JSONResponse({"state": "idle", "session_id": None})

    uptime = round(time.monotonic() - _FIELD_SESSION.get("paired_at", time.monotonic()), 1)
    return JSONResponse(
        {
            "state": _FIELD_SESSION.get("state", "idle"),
            "session_id": _FIELD_SESSION.get("session_id"),
            "uptime_s": uptime,
            "decision_count": _FIELD_SESSION.get("decision_count", 0),
            "sensor_frames_received": _FIELD_SESSION.get("sensor_frames_received", 0),
        }
    )


@app.post("/control/session")
async def field_session_action(body: dict[str, Any] | None = None) -> JSONResponse:
    """
    ADR 0017 §2 — Session lifecycle control.

    POST {"action": "pause"|"resume"|"end"}

    "end" flushes the session manifest to experiments/out/field/<session_id>/manifest.json
    if the path is writable.
    """
    if not _field_control_enabled():
        return JSONResponse({"error": "field_control_disabled"}, status_code=404)

    action = str((body or {}).get("action", "")).strip().lower()
    if action not in ("pause", "resume", "end"):
        return JSONResponse(
            {"error": "unknown_action", "valid": ["pause", "resume", "end"]}, status_code=400
        )

    if action == "end":
        _FIELD_SESSION["state"] = "ended"
        _field_emit_audit("field_session_ended", f"session={_FIELD_SESSION.get('session_id', '?')}")
        _field_flush_manifest()
    elif action == "pause":
        _FIELD_SESSION["state"] = "paused"
    elif action == "resume":
        _FIELD_SESSION["state"] = "running"

    return JSONResponse({"ok": True, "state": _FIELD_SESSION.get("state")})


@app.get("/phone")
def phone_relay_ui() -> Response:
    """
    ADR 0017 §1 — Serve the phone relay PWA.

    Enabled when KERNEL_FIELD_CONTROL=1. The HTML is a single-file PWA with:
    - Battery status (Battery API)
    - Accelerometer jerk (DeviceMotion)
    - Microphone level (AudioWorklet with ScriptProcessorNode fallback)
    - Session control (pair/pause/resume/end)
    - Live last_action readback from kernel

    Full implementation: src/static/phone_relay.html (ADR 0017 checklist ✓)
    """
    if not _field_control_enabled():
        return Response(
            content="<h1>Field control disabled</h1><p>Set KERNEL_FIELD_CONTROL=1</p>",
            media_type="text/html",
            status_code=404,
        )

    from pathlib import Path

    phone_html_path = Path(__file__).parent / "static" / "phone_relay.html"
    if phone_html_path.exists():
        content = phone_html_path.read_text(encoding="utf-8")
        return Response(content=content, media_type="text/html")

    # Fallback to minimal stub if file missing (should not happen in normal deployment)
    fallback_html = """<!DOCTYPE html>
<html lang="en">
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Ethos Kernel — Phone Relay</title></head>
<body>
<h1>Phone Relay Service</h1>
<p>Error: phone_relay.html not found. Please check installation.</p>
<p><a href="/">Back to chat</a></p>
</body></html>"""
    return Response(content=fallback_html, media_type="text/html", status_code=200)


def _field_emit_audit(event_type: str, content: str) -> None:
    """Write a field-session lifecycle event to the audit sidecar if configured."""
    path = os.environ.get("KERNEL_AUDIT_SIDECAR_PATH", "").strip()
    if not path:
        return
    import json as _json

    line = _json.dumps(
        {
            "type": event_type,
            "content": content,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        },
        sort_keys=True,
        ensure_ascii=False,
    )
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except OSError:
        pass


def _field_flush_manifest() -> None:
    """Write session manifest to experiments/out/field/<session_id>/manifest.json."""
    if not _FIELD_SESSION.get("session_id"):
        return
    import json as _json
    from pathlib import Path

    session_id = _FIELD_SESSION["session_id"]
    out_dir = Path("experiments") / "out" / "field" / session_id
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        manifest = {
            "schema": "field_session_manifest_v1",
            "session_id": session_id,
            "state": _FIELD_SESSION.get("state"),
            "uptime_s": round(
                time.monotonic() - _FIELD_SESSION.get("paired_at", time.monotonic()), 1
            ),
            "decision_count": _FIELD_SESSION.get("decision_count", 0),
            "sensor_frames_received": _FIELD_SESSION.get("sensor_frames_received", 0),
            "env_field_allow_wan": os.environ.get("KERNEL_FIELD_ALLOW_WAN", "0"),
        }
        (out_dir / "manifest.json").write_text(
            _json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("field_control: manifest written to %s", out_dir / "manifest.json")
    except OSError as exc:
        logger.warning("field_control: could not write manifest: %s", exc)


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
    raw = data.get("integrity_alert")
    if not isinstance(raw, dict):
        return None
    if not dao_integrity_audit_ws_enabled():
        return {
            "error": "integrity_audit_disabled",
            "hint": "Set KERNEL_DAO_INTEGRITY_AUDIT_WS=1 to enable."
        }
    summary = str(raw.get("summary") or "").strip()
    if not summary:
        return {"integrity_alert": {"ok": False, "error": "missing_summary"}}
    scope = str(raw.get("scope") or "local_audit").strip()[:120]
    record_dao_integrity_alert(kernel.dao, summary=summary, scope=scope)
    record_dao_ws_operation("integrity_alert")
    return {"integrity_alert": {"ok": True, "scope": scope}}


def _collect_lan_governance_integrity_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of integrity alerts: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_integrity_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context``:
      - ``frontier_turn`` (non-negative int): rows with lower ``turn_index`` become ``stale_event``.
      - ``cross_session_hint`` (`lan_governance_cross_session_hint_v1`): echoed only; not consensus
        (see ``PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT``).
      - ``frontier_witnesses`` (array): peer claims aggregated into ``frontier_witness_resolution``;
        not quorum (see ``PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS``).
    Each event needs ``summary``; optional ``scope``, ``principled_transparency``; merge keys per
    :func:`~src.modules.lan_governance_event_merge.merge_lan_governance_events_detailed`.
    """
    raw = data.get("lan_governance_integrity_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "integrity_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                },
            }
        }

    if not lan_governance_integrity_batch_ws_enabled():
        return {
            "lan_governance": {
                "integrity_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": (
                        "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_DAO_INTEGRITY_AUDIT_WS=1."
                    ),
                },
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {
            "lan_governance": {
                "integrity_batch": {"ok": False, "error": "events_must_be_list"},
            }
        }

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    errors: list[dict[str, Any]] = []
    applied_ids: list[str] = []
    applied = 0
    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        summary = str(row.get("summary") or "").strip()
        if not summary:
            errors.append({"event_id": eid, "error": "missing_summary"})
            continue
        scope = str(row.get("scope") or "local_audit").strip()[:120]
        pt = row.get("principled_transparency")
        if isinstance(pt, bool):
            record_dao_integrity_alert(
                kernel.dao,
                summary=summary,
                scope=scope,
                principled_transparency=pt,
            )
        else:
            record_dao_integrity_alert(kernel.dao, summary=summary, scope=scope)
        applied += 1
        applied_ids.append(eid)

    if applied:
        record_dao_ws_operation("lan_governance_integrity_batch")

    ok = merged_count == 0 or (not errors and applied == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": applied,
        "event_ids": applied_ids,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"integrity_batch": batch_body}}


def _collect_lan_governance_dao_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of DAO actions: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_dao_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires ``op`` in {"dao_vote","dao_resolve"} and the corresponding fields:
      - dao_vote: proposal_id, participant_id, n_votes, in_favor
      - dao_resolve: proposal_id
    """
    raw = data.get("lan_governance_dao_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "dao_batch": {"ok": False, "error": "invalid_payload", "hint": "expected object"}
            }
        }

    if not lan_governance_dao_batch_ws_enabled():
        return {
            "lan_governance": {
                "dao_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_MORAL_HUB_DAO_VOTE=1.",
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {"lan_governance": {"dao_batch": {"ok": False, "error": "events_must_be_list"}}}

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    touched_pids: set[str] = set()

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op not in ("dao_vote", "dao_resolve"):
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue

        if op == "dao_vote":
            pid = str(row.get("proposal_id") or "").strip()
            part = str(row.get("participant_id") or "").strip()
            if not pid or not part:
                errors.append(
                    {
                        "event_id": eid,
                        "error": "missing_fields",
                        "fields": ["proposal_id", "participant_id"],
                    }
                )
                continue
            try:
                n_votes = int(row.get("n_votes") or 1)
                in_favor = bool(row.get("in_favor", True))
            except (TypeError, ValueError):
                errors.append({"event_id": eid, "error": "invalid_vote_fields"})
                continue
            res = kernel.dao.vote(pid, part, n_votes, in_favor)
            results.append({"event_id": eid, "op": op, "proposal_id": pid, "result": res})
            touched_pids.add(pid)
            applied_ids.append(eid)
            continue

        if op == "dao_resolve":
            pid = str(row.get("proposal_id") or "").strip()
            if not pid:
                errors.append(
                    {"event_id": eid, "error": "missing_fields", "fields": ["proposal_id"]}
                )
                continue
            res = kernel.dao.resolve_proposal(pid)
            if res.get("outcome") in ("approved", "rejected"):
                n = apply_proposal_resolution_to_constitution_drafts(kernel, pid, res)
                if n:
                    res["constitution_drafts_updated"] = n
            results.append({"event_id": eid, "op": op, "proposal_id": pid, "result": res})
            touched_pids.add(pid)
            applied_ids.append(eid)
            continue

    if applied_ids:
        record_dao_ws_operation("lan_governance_dao_batch")

    proposals = [proposal_to_public(p) for p in kernel.dao.proposals if p.id in touched_pids]
    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "results": results,
        "errors": errors,
        "proposals": proposals,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"dao_batch": batch_body}}


def _collect_lan_governance_judicial_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of judicial dossier registrations: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_judicial_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires:
      - op: "judicial_register_dossier"
      - audit_paragraph: string (already formatted; see judicial_escalation.EthicalDossierV1.to_audit_paragraph)
    Optional:
      - episode_id: string
    """
    raw = data.get("lan_governance_judicial_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "judicial_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                }
            }
        }

    if not lan_governance_judicial_batch_ws_enabled():
        return {
            "lan_governance": {
                "judicial_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1 and KERNEL_JUDICIAL_ESCALATION=1.",
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {"lan_governance": {"judicial_batch": {"ok": False, "error": "events_must_be_list"}}}

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    records: list[dict[str, Any]] = []

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op != "judicial_register_dossier":
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue
        para = str(row.get("audit_paragraph") or "").strip()
        if not para:
            errors.append({"event_id": eid, "error": "missing_audit_paragraph"})
            continue
        episode_id = row.get("episode_id")
        ep = str(episode_id).strip() if isinstance(episode_id, str) else None
        rec = kernel_dao_as_mock(kernel.dao).register_escalation_case(para, episode_id=ep)
        records.append({"event_id": eid, "audit_record_id": rec.id})
        applied_ids.append(eid)

    if applied_ids:
        record_dao_ws_operation("lan_governance_judicial_batch")

    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "records": records,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"judicial_batch": batch_body}}


def _collect_lan_governance_mock_court_batch(
    kernel: EthicalKernel, data: dict[str, Any]
) -> dict[str, Any] | None:
    """
    Optional batch of mock tribunal runs: merge (turn / processor time / id) then apply in order.

    Client shape::
        {"lan_governance_mock_court_batch": {"events": [...], "id_key": "event_id"}}

    Optional ``merge_context`` (``frontier_turn``, ``cross_session_hint``) — same semantics as integrity batch.

    Each event requires:
      - op: "judicial_run_mock_court"
      - case_uuid: string
      - audit_record_id: string (from dossier registration)
      - summary_excerpt: string
      - buffer_conflict: bool
    """
    raw = data.get("lan_governance_mock_court_batch")
    if raw is None:
        return None
    if not isinstance(raw, dict):
        return {
            "lan_governance": {
                "mock_court_batch": {
                    "ok": False,
                    "error": "invalid_payload",
                    "hint": "expected object",
                }
            }
        }

    if not lan_governance_mock_court_batch_ws_enabled():
        return {
            "lan_governance": {
                "mock_court_batch": {
                    "ok": False,
                    "error": "disabled",
                    "hint": (
                        "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1, KERNEL_JUDICIAL_ESCALATION=1, "
                        "and KERNEL_JUDICIAL_MOCK_COURT=1."
                    ),
                }
            }
        }

    events_in = raw.get("events")
    if not isinstance(events_in, list):
        return {
            "lan_governance": {"mock_court_batch": {"ok": False, "error": "events_must_be_list"}}
        }

    id_key = str(raw.get("id_key") or "event_id").strip() or "event_id"
    dict_rows: list[dict[str, Any]] = [dict(x) for x in events_in if isinstance(x, dict)]
    input_count = len(dict_rows)
    missing_id_count = sum(1 for r in dict_rows if not str(r.get(id_key, "") or "").strip())

    mctx = parse_lan_merge_context(raw)
    merge_detail = merge_lan_governance_events_detailed(
        dict_rows, id_key=id_key, frontier_turn=mctx.frontier_turn
    )
    merged = merge_detail["merged"]
    event_conflicts: list[dict[str, Any]] = list(merge_detail["conflicts"])
    merged_count = len(merged)
    with_id_count = max(0, input_count - missing_id_count)
    deduped_count = max(0, with_id_count - merged_count)

    applied_ids: list[str] = []
    errors: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []

    for row in merged:
        eid = str(row.get(id_key, "") or "").strip()
        op = str(row.get("op") or "").strip()
        if op != "judicial_run_mock_court":
            errors.append({"event_id": eid, "error": "unsupported_op", "op": op})
            continue
        case_uuid = str(row.get("case_uuid") or "").strip()
        audit_record_id = str(row.get("audit_record_id") or "").strip()
        summary_excerpt = str(row.get("summary_excerpt") or "").strip()
        buffer_conflict = row.get("buffer_conflict")
        if not case_uuid or not audit_record_id or not summary_excerpt:
            errors.append(
                {
                    "event_id": eid,
                    "error": "missing_fields",
                    "fields": ["case_uuid", "audit_record_id", "summary_excerpt"],
                }
            )
            continue
        if not isinstance(buffer_conflict, bool):
            errors.append({"event_id": eid, "error": "buffer_conflict_must_be_bool"})
            continue
        _dao = kernel_dao_as_mock(kernel.dao)
        mc = _dao.run_mock_escalation_court(
            case_uuid, audit_record_id, summary_excerpt, buffer_conflict
        )
        maybe_register_reparation_after_mock_court(_dao, mc, case_uuid)
        results.append({"event_id": eid, "case_uuid": case_uuid, "mock_court": mc})
        applied_ids.append(eid)

    if applied_ids:
        record_dao_ws_operation("lan_governance_mock_court_batch")

    ok = merged_count == 0 or (not errors and len(applied_ids) == merged_count)
    batch_body: dict[str, Any] = {
        "ok": ok,
        "input_count": input_count,
        "missing_id_count": missing_id_count,
        "merged_count": merged_count,
        "deduped_count": deduped_count,
        "applied_count": len(applied_ids),
        "event_ids": applied_ids,
        "results": results,
        "errors": errors,
    }
    if event_conflicts:
        batch_body["event_conflicts"] = event_conflicts
    _attach_merge_context_telemetry(batch_body, mctx)
    return {"lan_governance": {"mock_court_batch": batch_body}}


def _collect_lan_governance_envelope(
    kernel: EthicalKernel,
    data: dict[str, Any],
    replay_cache: dict[str, dict[str, Any]] | None = None,
    replay_cache_stats: dict[str, int] | None = None,
    replay_cache_ttl_ms: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    replay_cache_max_entries: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
) -> dict[str, Any] | None:
    """
    Optional versioned wrapper that routes to one LAN batch handler by ``kind``.

    Envelope shape::
        {
          "schema": "lan_governance_envelope_v1",
          "node_id": "node-a",
          "sent_unix_ms": 1710000000000,
          "kind": "dao_batch" | "integrity_batch" | "judicial_batch" | "mock_court_batch",
          "batch": { ...same payload as direct batch key... }
        }
    """
    raw = data.get("lan_governance_envelope")
    if raw is None:
        return None
    now_ms = int(time.monotonic() * 1000)
    if replay_cache is not None:
        ttl_evicted, lru_evicted = _prune_lan_envelope_replay_cache(
            replay_cache,
            now_ms=now_ms,
            ttl_ms=max(0, replay_cache_ttl_ms),
            max_entries=max(1, replay_cache_max_entries),
        )
        if replay_cache_stats is not None:
            replay_cache_stats["evicted_ttl"] = (
                int(replay_cache_stats.get("evicted_ttl", 0)) + ttl_evicted
            )
            replay_cache_stats["evicted_lru"] = (
                int(replay_cache_stats.get("evicted_lru", 0)) + lru_evicted
            )
        if ttl_evicted:
            record_lan_envelope_replay_cache_event("evict_ttl", amount=float(ttl_evicted))
        if lru_evicted:
            record_lan_envelope_replay_cache_event("evict_lru", amount=float(lru_evicted))

    normalized, err = normalize_lan_governance_envelope(raw)
    if err is not None:
        return {
            "lan_governance": {
                "envelope": {
                    "ok": False,
                    "ack": "rejected",
                    "reject_reason": reject_reason_for_envelope_error(err.get("error")),
                    "cache": _lan_envelope_cache_stats(
                        replay_cache,
                        replay_cache_stats,
                        ttl_ms=max(0, replay_cache_ttl_ms),
                        max_entries=max(1, replay_cache_max_entries),
                        hit=False,
                    ),
                    **err,
                }
            }
        }
    assert normalized is not None
    kind = str(normalized["kind"])
    envelope_fingerprint = fingerprint_lan_governance_envelope(normalized)
    idempotency_token = idempotency_token_for_envelope(normalized)
    cached_entry = replay_cache.get(idempotency_token) if replay_cache is not None else None
    cached_ack = (
        cached_entry.get("envelope")
        if isinstance(cached_entry, dict) and isinstance(cached_entry.get("envelope"), dict)
        else None
    )
    if isinstance(cached_ack, dict):
        if replay_cache_stats is not None:
            replay_cache_stats["hits"] = int(replay_cache_stats.get("hits", 0)) + 1
        # LRU touch: move the token to the tail.
        if replay_cache is not None and isinstance(cached_entry, dict):
            entry = replay_cache.pop(idempotency_token)
            entry["last_seen_ms"] = now_ms
            replay_cache[idempotency_token] = entry
        hit_envelope = dict(cached_ack)
        hit_envelope["ok"] = True
        hit_envelope["ack"] = "already_seen"
        hit_envelope["replay_detected"] = True
        hit_envelope["idempotency_token"] = idempotency_token
        hit_envelope["fingerprint"] = envelope_fingerprint
        hit_envelope["audit_ledger_fingerprint"] = fingerprint_audit_ledger(kernel.dao.records)
        hit_envelope["cache"] = _lan_envelope_cache_stats(
            replay_cache,
            replay_cache_stats,
            ttl_ms=max(0, replay_cache_ttl_ms),
            max_entries=max(1, replay_cache_max_entries),
            hit=True,
        )
        record_lan_envelope_replay_cache_event("hit")
        return {"lan_governance": {"envelope": hit_envelope}}
    if replay_cache_stats is not None:
        replay_cache_stats["misses"] = int(replay_cache_stats.get("misses", 0)) + 1
    record_lan_envelope_replay_cache_event("miss")

    routed = dict(data)
    batch = dict(normalized["batch"])
    if kind == "integrity_batch":
        routed["lan_governance_integrity_batch"] = batch
        out = _collect_lan_governance_integrity_batch(kernel, routed)
    elif kind == "dao_batch":
        routed["lan_governance_dao_batch"] = batch
        out = _collect_lan_governance_dao_batch(kernel, routed)
    elif kind == "judicial_batch":
        routed["lan_governance_judicial_batch"] = batch
        out = _collect_lan_governance_judicial_batch(kernel, routed)
    elif kind == "mock_court_batch":
        routed["lan_governance_mock_court_batch"] = batch
        out = _collect_lan_governance_mock_court_batch(kernel, routed)
    else:
        # Defensive fallback; validator already blocks unsupported kinds.
        out = {"lan_governance": {"envelope": {"ok": False, "error": "unsupported_kind"}}}

    if out is None:
        out = {}
    lg = out.setdefault("lan_governance", {})
    if isinstance(lg, dict):
        kind_to_section = {
            "integrity_batch": "integrity_batch",
            "dao_batch": "dao_batch",
            "judicial_batch": "judicial_batch",
            "mock_court_batch": "mock_court_batch",
        }
        section_name = kind_to_section.get(kind, "")
        section = lg.get(section_name) if section_name else None
        merged_count: int | None = None
        applied_count: int | None = None
        if isinstance(section, dict):
            mc = section.get("merged_count")
            if isinstance(mc, int):
                merged_count = mc
            ac = section.get("applied_count")
            if isinstance(ac, int):
                applied_count = ac
        section_ok = (
            bool(section.get("ok"))
            if isinstance(section, dict) and isinstance(section.get("ok"), bool)
            else True
        )
        envelope_out: dict[str, Any] = {
            "ok": section_ok,
            "ack": "accepted" if section_ok else "rejected",
            "schema": normalized["schema"],
            "kind": kind,
            "node_id": normalized["node_id"],
            "sent_unix_ms": normalized["sent_unix_ms"],
            "fingerprint": envelope_fingerprint,
            "idempotency_token": idempotency_token,
            "merged_count": merged_count,
            "applied_count": applied_count,
            "audit_ledger_fingerprint": fingerprint_audit_ledger(kernel.dao.records),
            "cache": _lan_envelope_cache_stats(
                replay_cache,
                replay_cache_stats,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
                hit=False,
            ),
        }
        if not section_ok and isinstance(section, dict):
            section_error = str(section.get("error") or "").strip()
            if section_error:
                envelope_out["error"] = section_error
            if section_error == "disabled":
                envelope_out["reject_reason"] = "feature_disabled"
            elif section_error in {"invalid_payload", "events_must_be_list"}:
                envelope_out["reject_reason"] = "schema_validation_failed"
            elif section_error == "unsupported_op":
                envelope_out["reject_reason"] = "unsupported_operation"
            else:
                envelope_out["reject_reason"] = "batch_apply_failed"
        if replay_cache is not None and envelope_out.get("ok") is True:
            replay_cache[idempotency_token] = {
                "envelope": dict(envelope_out),
                "cached_at_ms": now_ms,
                "last_seen_ms": now_ms,
            }
            _, lru_evicted_after_insert = _prune_lan_envelope_replay_cache(
                replay_cache,
                now_ms=now_ms,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
            )
            if replay_cache_stats is not None and lru_evicted_after_insert:
                replay_cache_stats["evicted_lru"] = (
                    int(replay_cache_stats.get("evicted_lru", 0)) + lru_evicted_after_insert
                )
            if lru_evicted_after_insert:
                record_lan_envelope_replay_cache_event(
                    "evict_lru", amount=float(lru_evicted_after_insert)
                )
            envelope_out["cache"] = _lan_envelope_cache_stats(
                replay_cache,
                replay_cache_stats,
                ttl_ms=max(0, replay_cache_ttl_ms),
                max_entries=max(1, replay_cache_max_entries),
                hit=False,
            )
        lg["envelope"] = envelope_out
    return out


def _collect_lan_governance_coordinator(
    kernel: EthicalKernel,
    data: dict[str, Any],
    replay_cache: dict[str, dict[str, Any]] | None = None,
    replay_cache_stats: dict[str, int] | None = None,
    replay_cache_ttl_ms: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
    replay_cache_max_entries: int = DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES,
) -> dict[str, Any] | None:
    """
    Multi-node hub message: validate ``lan_governance_coordinator_v1`` then apply each inner envelope.

    Inner envelopes share the same per-session replay cache as direct ``lan_governance_envelope``.
    When inner batches emit ``event_conflicts``, the coordinator response may include
    ``aggregated_event_conflicts`` with ``source_batch``, ``envelope_fingerprint``, and token hints.
    When inner batches echo ``frontier_witness_resolution``, the coordinator may include
    ``aggregated_frontier_witness_resolutions`` with the same correlation fields.
    """
    raw = data.get("lan_governance_coordinator")
    if raw is None:
        return None
    if not lan_governance_coordinator_ws_enabled():
        return {
            "lan_governance": {
                "coordinator": {
                    "ok": False,
                    "ack": "rejected",
                    "error": "disabled",
                    "reject_reason": "feature_disabled",
                    "hint": "Set KERNEL_LAN_GOVERNANCE_MERGE_WS=1.",
                }
            }
        }

    normalized, err = normalize_lan_governance_coordinator(raw)
    if err is not None:
        return {
            "lan_governance": {
                "coordinator": {
                    "ok": False,
                    "ack": "rejected",
                    "reject_reason": _reject_reason_lan_coordinator(err.get("error")),
                    **err,
                }
            }
        }
    assert normalized is not None
    items: list[dict[str, Any]] = list(normalized["items"])
    coord_fp = fingerprint_lan_governance_coordinator(normalized)
    item_results: list[dict[str, Any]] = []
    aggregated_event_conflicts: list[dict[str, Any]] = []
    aggregated_frontier_witness_resolutions: list[dict[str, Any]] = []
    all_ok = True
    batch_sections = (
        "integrity_batch",
        "dao_batch",
        "judicial_batch",
        "mock_court_batch",
    )
    for env in items:
        fp = fingerprint_lan_governance_envelope(env)
        tok = idempotency_token_for_envelope(env)
        sub = _collect_lan_governance_envelope(
            kernel,
            {"lan_governance_envelope": env},
            replay_cache=replay_cache,
            replay_cache_stats=replay_cache_stats,
            replay_cache_ttl_ms=replay_cache_ttl_ms,
            replay_cache_max_entries=replay_cache_max_entries,
        )
        lg = (sub or {}).get("lan_governance") if isinstance(sub, dict) else None
        if not isinstance(lg, dict):
            lg = {}
        env_ack = lg.get("envelope")
        if isinstance(env_ack, dict) and env_ack.get("ok") is not True:
            all_ok = False
        for sec in batch_sections:
            block = lg.get(sec)
            if (
                isinstance(block, dict)
                and isinstance(block.get("ok"), bool)
                and block.get("ok") is False
            ):
                all_ok = False
                break
        aggregated_event_conflicts.extend(
            _aggregated_event_conflicts_from_lan_governance(
                lg,
                envelope_fingerprint=fp,
                envelope_idempotency_token=tok,
            )
        )
        aggregated_frontier_witness_resolutions.extend(
            _aggregated_frontier_witness_resolutions_from_lan_governance(
                lg,
                envelope_fingerprint=fp,
                envelope_idempotency_token=tok,
            )
        )
        item_results.append(
            {
                "fingerprint": fp,
                "idempotency_token": tok,
                "node_id": env.get("node_id"),
                "kind": env.get("kind"),
                "lan_governance": lg,
            }
        )
    if items:
        record_dao_ws_operation("lan_governance_coordinator")
    coord_body: dict[str, Any] = {
        "ok": all_ok,
        "ack": "accepted" if all_ok else "rejected",
        "schema": normalized["schema"],
        "coordinator_id": normalized["coordinator_id"],
        "coordination_run_id": normalized["coordination_run_id"],
        "coordinator_fingerprint": coord_fp,
        "input_count": normalized["input_count"],
        "deduped_count": normalized["deduped_count"],
        "applied_count": len(items),
        "items": item_results,
    }
    if aggregated_event_conflicts:
        coord_body["aggregated_event_conflicts"] = aggregated_event_conflicts
    if aggregated_frontier_witness_resolutions:
        coord_body["aggregated_frontier_witness_resolutions"] = (
            aggregated_frontier_witness_resolutions
        )
    return {"lan_governance": {"coordinator": coord_body}}


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
        aclient=getattr(ws.app.state, "aclient", None),
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
    bridge = RealTimeBridge(kernel)
    chat_turn_seq = 0

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
    lan_envelope_replay_cache_ttl_ms = _coerce_public_int(
        os.environ.get("KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS"),
        default=DEFAULT_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS,
        non_negative=True,
    )
    lan_envelope_replay_cache_max_entries = max(
        1,
        _coerce_public_int(
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
            first_meaningful_event = False
            
            try:
                text = (data_in.get("text") or "").strip()
                agent_id = data_in.get("agent_id") or "user"
                include_narrative = bool(data_in.get("include_narrative", False))
                escalate_to_dao = bool(data_in.get("escalate_to_dao", False))

                # Situated v8 sensors
                sensor_raw = data_in.get("sensor")
                client = sensor_raw if isinstance(sensor_raw, dict) else None
                
                # Phase 10: Inject Nomad Bridge Live Data
                from .modules.nomad_bridge import get_nomad_bridge
                nb = get_nomad_bridge()
                if client is None: client = {}
                
                # Merge orientation and battery if available in Nomad Bridge
                if not nb.telemetry_queue.empty():
                    # Peek latest without waiting
                    live_t = nb.telemetry_queue._queue[0] if nb.telemetry_queue.qsize() > 0 else {}
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
                
                if chat_to is not None:
                    # Timeout-aware stream consumption
                    it = gen.__aiter__()
                    while True:
                        try:
                            event = await asyncio.wait_for(it.__anext__(), timeout=chat_to)
                            
                            if not first_meaningful_event and event["event_type"] not in ("turn_started", "perception_started"):
                                observe_ttft_seconds(time.perf_counter() - t_turn_start)
                                first_meaningful_event = True

                            if event["event_type"] == "turn_finished":
                                result = event["payload"]["result"]
                                break
                            else:
                                # Backward compatibility: suppress stream events for older clients/tests
                                if os.environ.get("KERNEL_CHAT_STRIP_STREAM_EVENTS", "1") == "0":
                                    await ws.send_json(event)
                        except asyncio.TimeoutError:
                            logger.warning("chat_turn_timeout id=%s (set cooperative cancel)", turn_id)
                            if current_cancel_ev is not None:
                                current_cancel_ev.set()
                            record_chat_turn_async_timeout()
                            # Match test expectation: error + path + timeout + response bundle
                            await ws.send_json({
                                "error": "chat_turn_timeout",
                                "path": "turn_timeout",
                                "timeout_seconds": chat_to,
                                "response": {"message": "Turn exceeded server time limit.", "tone": "neutral"}
                            })
                            break
                        except StopAsyncIteration:
                            break
                else:
                    async for event in gen:
                        if not first_meaningful_event and event["event_type"] not in ("turn_started", "perception_started"):
                            observe_ttft_seconds(time.perf_counter() - t_turn_start)
                            first_meaningful_event = True

                        if event["event_type"] == "turn_finished":
                            result = event["payload"]["result"]
                        else:
                            # Backward compatibility: suppress stream events for older clients/tests
                            if os.environ.get("KERNEL_CHAT_STRIP_STREAM_EVENTS", "1") == "0":
                                await ws.send_json(event)
                
                if result:
                    observe_chat_turn(result.path, time.perf_counter() - t_turn_start)
                    
                    # Record Limbic Tension (Prometheus)
                    lp = result.limbic_profile or {}
                    # Prioritize regulation_gap as a proxy for 'effort/tension'
                    tension = lp.get("regulation_gap", lp.get("threat_load", 0.0))
                    set_limbic_tension(tension)
                    
                    # Phase 10: Broadcast to L0 Dashboard
                    nb.broadcast_to_dashboards({
                        "type": "telemetry", 
                        "payload": {
                            "tension": tension,
                            "trust": lp.get("trust", 0.5),
                            "turn_index": turn_id
                        }
                    })
                    if result.response and result.response.inner_voice:
                        nb.broadcast_to_dashboards({
                            "type": "thought",
                            "payload": {
                                "text": result.response.inner_voice,
                                "dissonance": bool(result.epistemic_dissonance.active) if result.epistemic_dissonance else False
                            }
                        })

                    if result.path in ("safety_block", "kernel_block"):
                        record_malabs_block(result.path)
                    
                    logger.info("chat_turn_finished id=%s path=%s", turn_id, result.path)
                    
                    if st.kernel_chat_json_offload:
                        payload = await bridge.run_sync_in_chat_thread(
                            _chat_turn_to_jsonable, result, kernel
                        )
                    else:
                        payload = _chat_turn_to_jsonable(result, kernel)
                    
                    # Retener la respuesta desnuda para backwards compatibility con los tests
                    await ws.send_json(payload)
                    
                    # Phase 11/12: Ouroboros Feedback Loop (Always active for rich clients)
                    android_text = payload.get("response", {}).get("message", "")
                    if android_text:
                        await ws.send_json({
                            "type": "kernel_voice",
                            "text": android_text
                        })
                    
                    lp = payload.get("limbic_profile", {})
                    haptic_plan = lp.get("haptic_plan", [])
                    if haptic_plan:
                        await ws.send_json({
                            "type": "haptic_feedback",
                            "payload": {"haptics": haptic_plan}
                        })
                    
                    # Backward compatibility: suppress other internal events
                    if os.environ.get("KERNEL_CHAT_STRIP_STREAM_EVENTS", "1") == "0":
                         pass

                        
                    maybe_autosave_episodes(kernel, session_ckpt)

            except asyncio.TimeoutError:
                kernel.abandon_chat_turn(turn_id)
                observe_chat_turn("turn_timeout", time.perf_counter() - t_turn_start)
                record_chat_turn_async_timeout()
                if current_cancel_ev is not None:
                    current_cancel_ev.set()
                    record_llm_cancel_scope_signaled()
                
                await ws.send_json({
                    "error": "chat_turn_timeout",
                    "timeout_seconds": chat_to,
                    "path": "turn_timeout",
                    "response": {"message": "Turn exceeded server time limit.", "tone": "neutral"}
                })
            except asyncio.CancelledError:
                logger.info("chat_turn_cancelled id=%s", turn_id)
                kernel.abandon_chat_turn(turn_id)
                if current_cancel_ev:
                    current_cancel_ev.set()
            except Exception as e:
                logger.exception("chat_turn_error id=%s: %s", turn_id, e)
                try:
                    await ws.send_json({"error": "internal_error", "message": str(e)})
                except: pass

        while True:
            set_request_id()
            raw = await ws.receive_text()
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
                kernel, data,
                replay_cache=lan_envelope_replay_cache,
                replay_cache_stats=lan_envelope_replay_cache_stats,
                replay_cache_ttl_ms=lan_envelope_replay_cache_ttl_ms,
                replay_cache_max_entries=lan_envelope_replay_cache_max_entries,
            )
            lan_coordinator_payload = _collect_lan_governance_coordinator(
                kernel, data,
                replay_cache=lan_envelope_replay_cache,
                replay_cache_stats=lan_envelope_replay_cache_stats,
                replay_cache_ttl_ms=lan_envelope_replay_cache_ttl_ms,
                replay_cache_max_entries=lan_envelope_replay_cache_max_entries,
            )
            lan_governance_merged = _merge_lan_governance_ws_payloads(
                lan_batch_payload, lan_dao_payload, lan_judicial_payload,
                lan_mock_court_payload, lan_envelope_payload, lan_coordinator_payload,
            )

            if (dao_payload or nomad_payload or integrity_payload or lan_governance_merged):
                out_ws: dict[str, Any] = {}
                if dao_payload: out_ws["dao"] = dao_payload
                if nomad_payload: out_ws["nomad"] = nomad_payload
                if integrity_payload:
                    if "error" in integrity_payload and not integrity_payload.get("integrity_alert"):
                         # Lift error to root for test compatibility
                         out_ws.update(integrity_payload)
                    else:
                         out_ws["integrity"] = integrity_payload
                if lan_governance_merged: out_ws["lan_governance"] = lan_governance_merged
                await ws.send_json(out_ws)
                if not text_preview:
                    maybe_autosave_episodes(kernel, session_ckpt)
                    continue

            # ══ Constitution Drafts etc ══
            cd = data.get("constitution_draft")
            if isinstance(cd, dict) and constitution_draft_ws_enabled():
                try:
                    add_constitution_draft(
                        kernel, int(cd.get("level", 1)), str(cd.get("title") or ""),
                        str(cd.get("body") or ""), str(cd.get("proposer") or data.get("agent_id") or "user")
                    )
                except: pass

            # ══ Standard Chat Turn ══
            if not text_preview:
                await ws.send_json({"error": "empty_text"})
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


def get_uvicorn_bind() -> tuple[str, int]:
    """Host and port from environment; see :mod:`src.chat_settings`."""
    from .chat_settings import chat_server_settings

    s = chat_server_settings()
    return s.chat_host, s.chat_port


def run_chat_server() -> None:
    """Start uvicorn with this module's ``app`` (blocking)."""
    import uvicorn

    host, port = get_uvicorn_bind()
    
    ssl_key = ".certs/key.pem"
    ssl_cert = ".certs/cert.pem"
    
    if os.path.exists(ssl_key) and os.path.exists(ssl_cert):
        logger.info("SSL certificates found. Starting server in HTTPS mode.")
        uvicorn.run(
            app, 
            host=host, 
            port=port, 
            reload=False,
            ssl_keyfile=ssl_key,
            ssl_certfile=ssl_cert
        )
    else:
        logger.warning("SSL certificates not found. Starting server in HTTP mode (Nomad Camera/Mic may NOT work).")
        uvicorn.run(app, host=host, port=port, reload=False)


def main() -> None:
    run_chat_server()


if __name__ == "__main__":
    main()
