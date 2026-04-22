"""Nomad HAL, clinical telemetry, and related HTTP routes (Bloque 34.1).

Split from :mod:`src.chat_server` to keep the monolith slimmer while preserving
the same URL graph and JSON contracts (``/nomad/migration``, ``/nomad/clinical``).
"""

from __future__ import annotations

import math
import time
from typing import Any

from fastapi import APIRouter

from src.modules.governance.existential_serialization import nomad_simulation_ws_enabled
from src.modules.perception.nomad_bridge import get_nomad_bridge

router = APIRouter(tags=["nomad"])


@router.get("/nomad/migration")
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


@router.get("/nomad/clinical")
def nomad_clinical() -> dict[str, Any]:
    """Bloque 14.2: Clinical telemetry snapshot — raw scalars for operator dashboards."""
    nb = get_nomad_bridge()
    meta = nb.vessel_metadata
    ctx = nb.vessel_context

    battery: float | None = None
    try:
        battery = float(ctx.battery_fraction) if ctx.battery_fraction is not None else None
    except (TypeError, ValueError):
        battery = None

    latency_ms: int = 0
    try:
        latency_ms = int(meta.get("latency_ms", 0))
    except (TypeError, ValueError):
        latency_ms = 0

    rms = nb.last_rms
    rms_safe = rms if (isinstance(rms, float) and math.isfinite(rms)) else 0.0

    return {
        "schema": "nomad_clinical_v1",
        "vessel_online": bool(nb._is_vessel_healthy),
        "vad_speaking": bool(nb.vad_speaking),
        "rms_audio": rms_safe,
        "latency_ms": latency_ms,
        "battery_fraction": battery,
        "thermal_state": str(meta.get("thermal_state", "unknown")),
        "connection_type": str(meta.get("connection_type", "unknown")),
        "vessel_id": str(meta.get("vessel_id", "none")),
        "device_label": str(ctx.device_label),
        "queues": {
            "vision_depth": nb.vision_queue.qsize(),
            "audio_depth": nb.audio_queue.qsize(),
            "telemetry_depth": nb.telemetry_queue.qsize(),
            "charm_feedback_depth": nb.charm_feedback_queue.qsize(),
            "chat_text_depth": nb.chat_text_queue.qsize(),
        },
        "last_sensor_update_delta_s": round(time.time() - nb._last_sensor_update, 3),
    }
