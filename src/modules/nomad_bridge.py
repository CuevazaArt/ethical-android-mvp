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

**Hardening (S.1.1):** ``KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES`` (default 8 MiB) caps UTF-8 inbound JSON
before ``json.loads``; ``KERNEL_NOMAD_MAX_VISION_DECODED_BYTES`` / ``KERNEL_NOMAD_MAX_AUDIO_DECODED_BYTES``
bound base64 decode size; ``KERNEL_NOMAD_MAX_TELEMETRY_KEYS`` trims flat telemetry dicts.
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

# Inbound WebSocket text (JSON) — larger than chat ``/ws/chat`` to allow single JPEG frames.
DEFAULT_NOMAD_WS_MAX_MESSAGE_BYTES = 8_388_608
DEFAULT_NOMAD_MAX_VISION_DECODED_BYTES = 6 * 1024 * 1024
DEFAULT_NOMAD_MAX_AUDIO_DECODED_BYTES = 2 * 1024 * 1024
DEFAULT_NOMAD_MAX_TELEMETRY_KEYS = 128


def _env_int(name: str, default: int) -> int:
    raw = (os.environ.get(name) or "").strip()
    if not raw:
        return default
    try:
        return max(0, int(raw))
    except ValueError:
        return default


def _ws_text_exceeds_utf8_byte_limit(text: str, max_bytes: int) -> bool:
    """True if UTF-8 encoding of ``text`` exceeds ``max_bytes`` (cheap bound when possible)."""
    if max_bytes <= 0:
        return False
    n = len(text)
    if n > max_bytes:
        return True
    if n * 4 <= max_bytes:
        return False
    return len(text.encode("utf-8")) > max_bytes


def _max_b64_chars_for_decode(max_decoded_bytes: int) -> int:
    """Upper bound on base64 *character* count that can decode to ``max_decoded_bytes``."""
    if max_decoded_bytes <= 0:
        return 2**31 - 1
    return 4 * ((max_decoded_bytes + 2) // 3)


def _trim_telemetry_dict(d: dict[str, Any], max_keys: int) -> dict[str, Any]:
    if max_keys <= 0 or len(d) <= max_keys:
        return dict(d)
    return dict(list(d.items())[:max_keys])


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
                [recv_task, send_task], return_when=asyncio.FIRST_COMPLETED
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
        }

    async def _recv_loop(self, ws: WebSocket):
        max_msg = _env_int("KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES", DEFAULT_NOMAD_WS_MAX_MESSAGE_BYTES)
        max_vis = _env_int(
            "KERNEL_NOMAD_MAX_VISION_DECODED_BYTES", DEFAULT_NOMAD_MAX_VISION_DECODED_BYTES
        )
        max_aud = _env_int(
            "KERNEL_NOMAD_MAX_AUDIO_DECODED_BYTES", DEFAULT_NOMAD_MAX_AUDIO_DECODED_BYTES
        )
        max_tel_keys = _env_int("KERNEL_NOMAD_MAX_TELEMETRY_KEYS", DEFAULT_NOMAD_MAX_TELEMETRY_KEYS)
        max_b64_vis = _max_b64_chars_for_decode(max_vis)
        max_b64_aud = _max_b64_chars_for_decode(max_aud)
        try:
            while True:
                raw_text = await ws.receive_text()
                if max_msg > 0 and _ws_text_exceeds_utf8_byte_limit(raw_text, max_msg):
                    _log.warning(
                        "Nomad Bridge: inbound message exceeds KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES"
                    )
                    continue
                try:
                    data = json.loads(raw_text)
                except json.JSONDecodeError:
                    continue
                if not isinstance(data, dict):
                    continue
                event_type = data.get("type")
                payload = data.get("payload")
                if not event_type or payload is None:
                    continue
                if not isinstance(payload, dict):
                    continue

                if event_type == "vision_frame":
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    b64_img = payload.get("image_b64", "")
                    if not isinstance(b64_img, str) or len(b64_img) > max_b64_vis:
                        continue
                    try:
                        raw = base64.b64decode(b64_img, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if max_vis > 0 and len(raw) > max_vis:
                        continue
                    if raw:
                        self.vision_queue.put_nowait(raw)

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                    b64_pcm = payload.get("audio_b64", "")
                    if not isinstance(b64_pcm, str) or len(b64_pcm) > max_b64_aud:
                        continue
                    try:
                        raw_audio = base64.b64decode(b64_pcm, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if max_aud > 0 and len(raw_audio) > max_aud:
                        continue
                    if raw_audio:
                        self.audio_queue.put_nowait(raw_audio)

                elif event_type == "telemetry":
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    tel = _trim_telemetry_dict(payload, max_tel_keys)
                    self.telemetry_queue.put_nowait(tel)
                    with self._telemetry_lock:
                        self._latest_telemetry = dict(tel)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge read error: {e}")

    async def _send_loop(self, ws: WebSocket):
        try:
            while True:
                charm_vector = await self.charm_feedback_queue.get()
                await ws.send_json({"type": "charm_feedback", "payload": charm_vector})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge send error: {e}")


# Global instance
_NOMAD_BRIDGE = NomadBridge()


def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE
