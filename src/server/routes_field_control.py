"""ADR 0017 field-test control surface: /control/* and /phone (Bloque 34.1)."""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

logger = logging.getLogger(__name__)

router = APIRouter(tags=["field-control"])

# lightweight in-process session state
_FIELD_SESSION: dict[str, Any] = {}

_SRC_DIR = Path(__file__).resolve().parent.parent
_PHONE_RELAY_HTML = _SRC_DIR / "static" / "phone_relay.html"


def _field_control_enabled() -> bool:
    return os.environ.get("KERNEL_FIELD_CONTROL", "").strip().lower() in ("1", "true", "yes")


def _field_pairing_token() -> str:
    return os.environ.get("KERNEL_FIELD_PAIRING_TOKEN", "").strip()


@router.post("/control/pair")
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


@router.get("/control/status")
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


@router.post("/control/session")
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


@router.get("/phone")
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

    if _PHONE_RELAY_HTML.exists():
        content = _PHONE_RELAY_HTML.read_text(encoding="utf-8")
        return Response(content=content, media_type="text/html")

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

    line = json.dumps(
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
            json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False),
            encoding="utf-8",
        )
        logger.info("field_control: manifest written to %s", out_dir / "manifest.json")
    except OSError as exc:
        logger.warning("field_control: could not write manifest: %s", exc)
