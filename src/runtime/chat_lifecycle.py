"""
Chat Lifecycle Management — Startup and shutdown routines for the FastAPI app.

Single source of truth for ASGI startup/shutdown (Bloque 32.1). ``src.chat_server``
wires ``lifespan=chat_lifespan`` on the FastAPI constructor only — no duplicate
lifespan handlers elsewhere.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from src.chat_settings import chat_server_settings
from src.modules.perception.nomad_discovery import (
    NomadDiscoveryAnnouncer,
    nomad_discovery_service_name,
    nomad_discovery_service_type,
)
from src.observability.logging_setup import configure_logging
from src.observability.metrics import init_metrics
from src.settings import kernel_settings

logger = logging.getLogger(__name__)


def api_docs_enabled() -> bool:
    """OpenAPI/Swagger UI — off by default (LAN deployments); set KERNEL_API_DOCS=1 to expose."""
    return kernel_settings().kernel_api_docs


@asynccontextmanager
async def chat_lifespan(app: FastAPI) -> AsyncIterator[None]:
    configure_logging()
    init_metrics()

    # Phase 9: Nomad hardware loop consumers (Hardened Embodiment)
    from src.modules.perception.audio_adapter import (
        get_shared_audio_capture,
        start_nomad_audio_consumer_from_env,
        stop_nomad_audio_consumer_async,
    )
    from src.modules.perception.vision_adapter import (
        start_nomad_vision_consumer_from_env,
        stop_nomad_vision_consumer_async,
    )
    from src.modules.somatic.vitality import (
        start_nomad_telemetry_consumer_from_env,
        stop_nomad_telemetry_consumer_async,
    )

    start_nomad_vision_consumer_from_env()
    start_nomad_telemetry_consumer_from_env()

    capture = get_shared_audio_capture()
    if capture:
        start_nomad_audio_consumer_from_env(capture.ring_buffer)

    # Phase 12.1: Global persistent client for Nomad hardware loop
    aclient = httpx.AsyncClient(timeout=30.0)
    app.state.aclient = aclient

    # Bloque 14.1: optional mDNS/Zeroconf advertisement for Nomad auto-discovery.
    cst = chat_server_settings()
    announcer = NomadDiscoveryAnnouncer(
        bind_host=cst.chat_host,
        bind_port=cst.chat_port,
        service_name=nomad_discovery_service_name(),
        service_type=nomad_discovery_service_type(),
    )
    announcer.start()
    app.state.nomad_discovery_announcer = announcer

    try:
        yield
    finally:
        # Phase 9: Graceful shutdown of consumers
        await stop_nomad_vision_consumer_async()
        await stop_nomad_telemetry_consumer_async()
        await stop_nomad_audio_consumer_async()

        from src.real_time_bridge import shutdown_chat_threadpool

        try:
            announcer.stop()
        except Exception:
            logger.debug("nomad_discovery_announcer.stop failed (ignored)", exc_info=True)

        await aclient.aclose()
        shutdown_chat_threadpool(wait=True)
