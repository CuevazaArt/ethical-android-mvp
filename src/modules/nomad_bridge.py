"""
LAN Nomad bridge (Module S / PLAN_WORK_DISTRIBUTION_TREE Bloque S.1).

WebSocket JSON events (client → server):

- ``type: vision_frame``, ``payload: { "image_b64": "<base64 JPEG>" }``
- ``type: audio_pcm``, ``payload: { "audio_b64": "<base64 raw PCM>" }``
- ``type`` = ``telemetry``, ``payload``: flat sensor dict (accelerometer, battery, temperature, …)

Server → client: ``type: charm_feedback``, ``payload``: charm vector dict (from kernel).

``NomadVisionConsumer`` in ``vision_adapter.py`` drains ``vision_queue``; audio adapter drains ``audio_queue``.

Latest ``telemetry`` payloads are mirrored for synchronous readers (Module S.2.1 — vitality merge in
``vitality.merge_nomad_telemetry_into_snapshot`` / ``KERNEL_NOMAD_TELEMETRY_VITALITY``).
That merge step normalizes common mobile key aliases (e.g. ``battery``, ``core_temperature_c``, ``jerk``)
onto :class:`~src.modules.sensor_contracts.SensorSnapshot` field names before parsing.

**Inbound WebSocket frame cap:** ``KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES`` (default 4 MiB UTF-8, hard cap 32 MiB)
rejects oversize text frames before ``json.loads`` (aligned with chat server hardening).

**Decoded size caps (LAN hardening):** ``KERNEL_NOMAD_MAX_VISION_FRAME_BYTES`` (default 5 MiB) and
``KERNEL_NOMAD_MAX_AUDIO_PCM_BYTES`` (default 1 MiB) bound base64 payloads before they enter bounded queues.

**Telemetry shape:** ``payload`` must be a **flat JSON object**; ``KERNEL_NOMAD_MAX_TELEMETRY_KEYS`` (default 128)
drops oversized dicts before they hit the queue or ``peek_latest_telemetry``.
"""

import asyncio
import base64
import binascii
import json
import logging
import os
import threading
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

_log = logging.getLogger(__name__)


def _parse_positive_int_env(name: str, default: int) -> int:
    raw = os.environ.get(name, "").strip()
    if not raw:
        return default
    try:
        v = int(raw, 10)
        return default if v <= 0 else v
    except ValueError:
        return default


def max_vision_frame_bytes() -> int:
    """Upper bound on decoded JPEG bytes accepted from ``vision_frame`` (env override)."""

    return _parse_positive_int_env("KERNEL_NOMAD_MAX_VISION_FRAME_BYTES", 5_242_880)


def max_audio_pcm_bytes() -> int:
    """Upper bound on decoded PCM chunk bytes from ``audio_pcm`` (env override)."""

    return _parse_positive_int_env("KERNEL_NOMAD_MAX_AUDIO_PCM_BYTES", 1_048_576)


def max_telemetry_dict_keys() -> int:
    """Maximum key count accepted on a ``telemetry`` ``payload`` object (env override)."""

    return _parse_positive_int_env("KERNEL_NOMAD_MAX_TELEMETRY_KEYS", 128)


_DEFAULT_WS_MAX_MESSAGE_BYTES = 4 * 1024 * 1024
_CAP_WS_MAX_MESSAGE_BYTES = 32 * 1024 * 1024
_MIN_WS_MAX_MESSAGE_BYTES = 64


def max_ws_inbound_message_bytes() -> int:
    """
    Max UTF-8 size of one inbound WebSocket text message (JSON envelope) before parse.

    Base64 vision/audio payloads need headroom versus ``KERNEL_CHAT_WS_MAX_MESSAGE_BYTES``;
    invalid or tiny env values fall back to the default.
    """
    raw = os.environ.get("KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES", "").strip()
    if not raw:
        return _DEFAULT_WS_MAX_MESSAGE_BYTES
    try:
        n = int(raw, 10)
    except ValueError:
        return _DEFAULT_WS_MAX_MESSAGE_BYTES
    if n < _MIN_WS_MAX_MESSAGE_BYTES:
        return _DEFAULT_WS_MAX_MESSAGE_BYTES
    return min(n, _CAP_WS_MAX_MESSAGE_BYTES)


def _decoded_upper_bound_from_b64_len(n: int) -> int:
    """RFC 4648 — maximum possible decoded length from a base64 string of character length ``n``."""

    if n <= 0:
        return 0
    return (n * 3 + 3) // 4


def _b64_fits_decoded_limit(b64_s: str, max_raw: int) -> bool:
    if max_raw <= 0 or not isinstance(b64_s, str):
        return False
    return _decoded_upper_bound_from_b64_len(len(b64_s)) <= max_raw


class NomadBridge:
    """
    FastAPI WebSocket endpoint that buffers smartphone LAN streams into bounded asyncio queues.

    Drops oldest items when a queue is full to cap memory (frame/audio throttle).
    """

    def __init__(self):
        # Bounded queues throttle bursty mobile uplinks
        self.vision_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=5)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=30)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self._telemetry_lock = threading.Lock()
        self._latest_telemetry: dict[str, Any] | None = None
        
        self.app = FastAPI(title="Ethos Nomad Bridge")
        
        @self.app.websocket("/ws/nomad")
        async def websocket_nomad_endpoint(websocket: WebSocket):
            await websocket.accept()
            _log.info("Nomad Bridge: client connected.")
            
            # Start full-duplex execution
            recv_task = asyncio.create_task(self._recv_loop(websocket))
            send_task = asyncio.create_task(self._send_loop(websocket))
            
            done, pending = await asyncio.wait(
                [recv_task, send_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
                
            _log.info("Nomad Bridge: client disconnected.")

    def peek_latest_telemetry(self) -> dict[str, Any] | None:
        """Thread-safe copy of the last ``telemetry`` payload (for vitality / kernel sync path)."""
        with self._telemetry_lock:
            if not self._latest_telemetry:
                return None
            return dict(self._latest_telemetry)

    def public_queue_stats(self) -> dict[str, Any]:
        """JSON-safe queue depths for operators (GET /metrics hooks, health dashboards).

        Includes **key names only** from the last ``telemetry`` payload (no values), for S.2.1
        vitality merge observability without leaking raw sensor readings in logs.

        ``limits`` echoes effective caps from ``KERNEL_NOMAD_MAX_*`` env (decoded bytes / dict keys).
        """
        peek = self.peek_latest_telemetry()
        tel_keys = sorted(peek.keys()) if peek else []
        return {
            "schema": "nomad_bridge_queue_stats_v2",
            "vision_queued": self.vision_queue.qsize(),
            "vision_max": self.vision_queue.maxsize,
            "audio_queued": self.audio_queue.qsize(),
            "audio_max": self.audio_queue.maxsize,
            "telemetry_queued": self.telemetry_queue.qsize(),
            "telemetry_max": self.telemetry_queue.maxsize,
            "charm_feedback_queued": self.charm_feedback_queue.qsize(),
            "charm_feedback_max": self.charm_feedback_queue.maxsize,
            "latest_telemetry_present": bool(peek),
            "latest_telemetry_keys": tel_keys,
            "limits": {
                "max_vision_frame_bytes": max_vision_frame_bytes(),
                "max_audio_pcm_bytes": max_audio_pcm_bytes(),
                "max_telemetry_keys": max_telemetry_dict_keys(),
                "max_ws_message_bytes": max_ws_inbound_message_bytes(),
            },
        }

    async def _recv_loop(self, ws: WebSocket):
        try:
            while True:
                raw = await ws.receive_text()
                if len(raw.encode("utf-8")) > max_ws_inbound_message_bytes():
                    continue
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, dict):
                    continue
                event_type = data.get("type")
                payload = data.get("payload")
                
                if not event_type or not payload:
                    continue
                    
                if event_type == "vision_frame":
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    b64_img = payload.get("image_b64", "")
                    lim = max_vision_frame_bytes()
                    if not _b64_fits_decoded_limit(b64_img, lim):
                        continue
                    try:
                        raw = base64.b64decode(b64_img, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if raw and len(raw) <= lim:
                        self.vision_queue.put_nowait(raw)

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                    b64_pcm = payload.get("audio_b64", "")
                    lim_a = max_audio_pcm_bytes()
                    if not _b64_fits_decoded_limit(b64_pcm, lim_a):
                        continue
                    try:
                        raw_audio = base64.b64decode(b64_pcm, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if raw_audio and len(raw_audio) <= lim_a:
                        self.audio_queue.put_nowait(raw_audio)

                elif event_type == "telemetry":
                    if not isinstance(payload, dict):
                        continue
                    if len(payload) > max_telemetry_dict_keys():
                        continue
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    self.telemetry_queue.put_nowait(payload)
                    with self._telemetry_lock:
                        self._latest_telemetry = dict(payload)
                        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge read error: {e}")

    async def _send_loop(self, ws: WebSocket):
        try:
            while True:
                charm_vector = await self.charm_feedback_queue.get()
                await ws.send_json({
                    "type": "charm_feedback",
                    "payload": charm_vector
                })
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge send error: {e}")

# Global instance
_NOMAD_BRIDGE = NomadBridge()

def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE
