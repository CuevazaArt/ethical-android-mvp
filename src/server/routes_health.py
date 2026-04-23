"""Liveness, metrics, and service root (Bloque 34.1). ``/discovery/nomad`` → ``routes_governance``."""

from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response

from ..chat_settings import chat_server_settings
from src.modules.cognition.llm_touchpoint_policies import (
    ENV_LLM_GLOBAL_DEFAULT_POLICY,
    raw_global_default_policy,
    resolve_monologue_llm_backend_policy,
)
from src.modules.cognition.llm_verbal_backend_policy import resolve_verbal_llm_backend_policy
from src.modules.perception.nomad_bridge import get_nomad_bridge
from src.modules.perception.nomad_discovery import (
    nomad_discovery_service_name,
    nomad_discovery_service_type,
)
from src.modules.perception.perception_backend_policy import resolve_perception_backend_policy
from ..observability.decision_log import decision_log_enabled
from ..observability.metrics import metrics_enabled
from ..runtime.chat_feature_flags import env_truthy
from ..runtime_profiles import applied_runtime_profile
from .meta import package_version, uptime_seconds_rounded

router = APIRouter(tags=["health"])


@router.get("/metrics")
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


@router.get("/health")
def health(request: Request) -> Response:
    """Liveness + operator-facing observability flags (JSON for dashboards and probes)."""
    log_json = os.environ.get("KERNEL_LOG_JSON", "").strip().lower() in ("1", "true", "yes", "on")
    prom_client = "ok"
    try:
        import prometheus_client  # noqa: F401
    except ImportError:
        prom_client = "missing"

    st = chat_server_settings()
    env_validation = os.environ.get("KERNEL_ENV_VALIDATION", "").strip().lower() or "strict"
    out: dict[str, Any] = {
        "status": "ok",
        "service": "ethos-kernel-chat",
        "version": package_version(),
        "uptime_seconds": uptime_seconds_rounded(),
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
            "kernel_chat_ws_max_message_bytes": st.kernel_chat_ws_max_message_bytes,
        },
        "safety_defaults": {
            "kernel_env_validation_mode": env_validation,
            "semantic_chat_gate_enabled": env_truthy("KERNEL_SEMANTIC_CHAT_GATE", True),
            "semantic_embed_hash_fallback_enabled": env_truthy(
                "KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", True
            ),
            "perception_failsafe_enabled": env_truthy("KERNEL_PERCEPTION_FAILSAFE", True),
            "perception_parallel_enabled": env_truthy("KERNEL_PERCEPTION_PARALLEL", False),
        },
    }
    prof = applied_runtime_profile()
    if prof:
        out["runtime_profile"] = prof

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

    out["nomad_bridge"] = get_nomad_bridge().public_queue_stats()
    announcer = getattr(request.app.state, "nomad_discovery_announcer", None)
    out["nomad_discovery"] = {
        "enabled": bool(announcer is not None),
        "mdns_registered": bool(getattr(announcer, "registered", False)),
        "service_name": nomad_discovery_service_name(),
        "service_type": nomad_discovery_service_type(),
        "endpoint": "/discovery/nomad",
    }

    req_id = request.headers.get("x-request-id")
    response = JSONResponse(content=out)
    if req_id:
        response.headers["x-request-id"] = req_id
    return response


@router.get("/")
def root() -> JSONResponse:
    from ..runtime_profiles import applied_runtime_profile as _prof

    body: dict[str, Any] = {
        "service": "ethos-kernel-chat",
        "websocket": "/ws/chat",
        "nomad_discovery": "/discovery/nomad (LAN auto-discovery payload + mDNS metadata)",
        "nomad_clinical": "/nomad/clinical (Bloque 14.2 — raw Float/Boolean clinical telemetry snapshot)",
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
    return JSONResponse(body)


@router.get("/test/llm")
async def test_llm():
    """Debug route to test Ollama connectivity directly from the kernel layer."""
    from src.modules.cognition.llm_layer import LLMModule
    
    llm = LLMModule()
    try:
        # Simple non-streaming call for sanity check
        res = await llm.acommunicate(
            action="test_vocal",
            mode="D_fast",
            state="neutral",
            sigma=0.5,
            circle="inner_soto",
            verdict="safe",
            score=1.0,
            scenario="Say 'Kernel test successful' in Spanish.",
            stream_callback=None,
        )
        return {"status": "ok", "provider": llm.mode, "response": res.message}
    except Exception as e:
        import traceback
        return {"status": "error", "error": str(e), "traceback": traceback.format_exc()}
