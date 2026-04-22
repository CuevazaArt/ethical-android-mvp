"""
Ethos Kernel ASGI Application (Bloque 34.5 final).

This module centralizes the construction, middleware, and route mounting of the
FastAPI application, enabling ``uvicorn src.server.app:app``.
"""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from src.observability.middleware import RequestContextMiddleware
from src.runtime.chat_feature_flags import coerce_public_int
from src.runtime.chat_lifecycle import api_docs_enabled, chat_lifespan
from src.runtime_profiles import apply_named_runtime_profile_to_environ
from src.server.routes_field_control import router as field_control_http_router
from src.server.routes_governance import router as governance_http_router
from src.server.routes_health import router as health_http_router
from src.server.routes_nomad import router as nomad_http_router
from src.server.ws_chat import router as ws_chat_router
from src.server.ws_sidecar import router as ws_sidecar_router
from src.validators.env_policy import validate_kernel_env

logger = logging.getLogger(__name__)

# ══ Runtime Setup ══
# Profiles and env validation must run before FastAPI instantiation to ensure correct defaults.
apply_named_runtime_profile_to_environ()
validate_kernel_env()

# ══ App Construction ══
app = FastAPI(
    title="Ethos Kernel Chat",
    version="1.0",
    docs_url="/docs" if api_docs_enabled() else None,
    redoc_url="/redoc" if api_docs_enabled() else None,
    openapi_url="/openapi.json" if api_docs_enabled() else None,
    lifespan=chat_lifespan,
)

# ══ Middleware ══
app.add_middleware(RequestContextMiddleware)

# ══ Sub-App Mounting ══
from src.modules.nomad_bridge import get_nomad_bridge
app.mount("/nomad_bridge", get_nomad_bridge().app)

# ══ Route Inclusion ══
app.include_router(health_http_router)
app.include_router(governance_http_router)
app.include_router(nomad_http_router)
app.include_router(field_control_http_router)
app.include_router(ws_sidecar_router)
app.include_router(ws_chat_router)

# ══ Static File Mounting (PWA, Dashboard, etc.) ══
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Nomad PWA
nomad_pwa_path = os.path.join(base_dir, "clients", "nomad_pwa")
if os.path.exists(nomad_pwa_path):
    app.mount("/nomad", StaticFiles(directory=nomad_pwa_path, html=True), name="nomad_pwa")
    logger.info("Nomad PWA Interface mounted at /nomad/")

# Prometheus Metrics
try:
    if os.environ.get("KERNEL_METRICS", "1").strip().lower() in ("1", "true", "on"):
        from prometheus_client import make_asgi_app
        metrics_app = make_asgi_app()
        app.mount("/metrics", metrics_app)
        logger.info("Prometheus metrics endpoint mounted at /metrics")
except ImportError:
    logger.warning("prometheus_client not installed, skipping /metrics")

# L0 Dashboard
dashboard_path = os.path.join(base_dir, "static", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/dashboard", StaticFiles(directory=dashboard_path, html=True), name="l0_dashboard")
    logger.info("L0 Dashboard mounted at /dashboard/")

# Clinical UI
clinical_path = os.path.join(base_dir, "static", "clinical")
if os.path.exists(clinical_path):
    app.mount("/clinical", StaticFiles(directory=clinical_path, html=True), name="clinical_ui")
    logger.info("Clinical UI mounted at /clinical/")

# Master Orchestrator
master_path = os.path.join(base_dir, "static", "master")
if os.path.exists(master_path):
    app.mount("/master", StaticFiles(directory=master_path, html=True), name="master_orchestrator")
    logger.info("Master Orchestrator mounted at /master/")

__all__ = ["app"]
