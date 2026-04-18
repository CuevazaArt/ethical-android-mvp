"""
LAN Nomad bridge (Module S / PLAN_WORK_DISTRIBUTION_TREE Bloque S.1).

WebSocket JSON events (client → server):

- ``type: vision_frame``, ``payload: { "image_b64": "<base64 JPEG>" }``
- ``type: audio_pcm``, ``payload: { "audio_b64": "<base64 raw PCM>" }``
- ``type`` = ``telemetry``, ``payload``: flat sensor dict (accelerometer, battery, temperature, …)

Server → client: ``type: charm_feedback``, ``payload``: charm vector dict (from kernel).

``NomadVisionConsumer`` in ``vision_adapter.py`` drains ``vision_queue``; audio adapter drains ``audio_queue``.

When ``KERNEL_METRICS=1``, rejections and queue evictions are also mirrored to Prometheus
(``ethos_kernel_nomad_bridge_rejections_total``, ``ethos_kernel_nomad_bridge_queue_evictions_total``).

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
import math
import os
import struct
import threading
from typing import Any

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect

    _FASTAPI_AVAILABLE = True
except ImportError:

    class WebSocketDisconnect(Exception):
        """Placeholder when FastAPI is not installed (WebSocket routes are disabled)."""

    FastAPI = None  # type: ignore[misc, assignment]
    WebSocket = Any  # type: ignore[misc, assignment]
    _FASTAPI_AVAILABLE = False

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
        # Counters: recv loop (async) and /health (sync threadpool) — protect with a lock.
        self._stats_lock = threading.Lock()
        self._rejections: dict[str, int] = {
            "ws_oversize": 0,
            "invalid_json": 0,
            "invalid_envelope": 0,
            "vision_reject": 0,
            "audio_reject": 0,
            "telemetry_reject": 0,
        }
        self._queue_evictions: dict[str, int] = {
            "vision": 0,
            "audio": 0,
            "telemetry": 0,
        }

        # L0 dashboard subscribers (see ``chat_server``); optional audio RMS for Thalamus merge.
        self.dashboard_queues: list[asyncio.Queue[dict[str, Any]]] = []
        self.last_rms: float = 0.0

        self.app: Any = None

        if not _FASTAPI_AVAILABLE or FastAPI is None:
            _log.warning(
                "Nomad Bridge: FastAPI not installed; queues work but HTTP/WebSocket app is disabled. "
                'Install with: pip install -e ".[runtime]"'
            )
            return

        self.app = FastAPI(title="Ethos Nomad Bridge")

        @self.app.websocket("/ws/nomad")
        async def websocket_nomad_endpoint(websocket: WebSocket) -> None:
            await self.handle_websocket(websocket)

    async def handle_websocket(self, websocket: WebSocket) -> None:
        """Run recv/send loops for one Nomad smartphone WebSocket until disconnect."""
        await websocket.accept()
        _log.info("Nomad Bridge: client connected.")
        recv_task = asyncio.create_task(self._recv_loop(websocket))
        send_task = asyncio.create_task(self._send_loop(websocket))
        try:
            _, pending = await asyncio.wait(
                [recv_task, send_task],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        except Exception as e:
            _log.error("Nomad Bridge exception in handler: %s", e)
        finally:
            _log.info("Nomad Bridge: client disconnected.")

    def broadcast_to_dashboards(self, msg: dict[str, Any]) -> None:
        """Push a JSON-safe message to all registered L0 dashboard subscriber queues."""
        for q in self.dashboard_queues:
            if not q.full():
                q.put_nowait(msg)

    def peek_latest_telemetry(self) -> dict[str, Any] | None:
        """Thread-safe copy of the last ``telemetry`` payload (for vitality / kernel sync path)."""
        with self._telemetry_lock:
            if not self._latest_telemetry:
                return None
            return dict(self._latest_telemetry)

    def _bump_rejection(self, key: str) -> None:
        with self._stats_lock:
            self._rejections[key] = self._rejections.get(key, 0) + 1
        from ..observability.metrics import record_nomad_bridge_rejection

        record_nomad_bridge_rejection(key)

    def _bump_eviction(self, key: str) -> None:
        with self._stats_lock:
            self._queue_evictions[key] = self._queue_evictions.get(key, 0) + 1
        from ..observability.metrics import record_nomad_bridge_queue_eviction

        record_nomad_bridge_queue_eviction(key)

    def public_queue_stats(self) -> dict[str, Any]:
        """JSON-safe queue depths for operators (GET /metrics hooks, health dashboards).

        Includes **key names only** from the last ``telemetry`` payload (no values), for S.2.1
        vitality merge observability without leaking raw sensor readings in logs.

        ``limits`` echoes effective caps from ``KERNEL_NOMAD_MAX_*`` env (decoded bytes / dict keys).

        ``rejections`` / ``queue_evictions`` are monotonic counters since process start (S.1 observability).
        """
        peek = self.peek_latest_telemetry()
        tel_keys = sorted(peek.keys()) if peek else []
        with self._stats_lock:
            rejections = dict(self._rejections)
            evictions = dict(self._queue_evictions)
        return {
            "schema": "nomad_bridge_queue_stats_v3",
            "vision_queued": self.vision_queue.qsize(),
            "vision_max": self.vision_queue.maxsize,
            "audio_queued": self.audio_queue.qsize(),
            "audio_max": self.audio_queue.maxsize,
            "telemetry_queued": self.telemetry_queue.qsize(),
            "telemetry_max": self.telemetry_queue.maxsize,
            "charm_feedback_queued": self.charm_feedback_queue.qsize(),
            "charm_feedback_max": self.charm_feedback_queue.maxsize,
            "last_rms": self.last_rms,
            "dashboard_subscribers": len(self.dashboard_queues),
            "latest_telemetry_present": bool(peek),
            "latest_telemetry_keys": tel_keys,
            "rejections": rejections,
            "queue_evictions": evictions,
            "limits": {
                "max_vision_frame_bytes": max_vision_frame_bytes(),
                "max_audio_pcm_bytes": max_audio_pcm_bytes(),
                "max_telemetry_keys": max_telemetry_dict_keys(),
                "max_ws_message_bytes": max_ws_inbound_message_bytes(),
            },
        }

    async def _recv_loop(self, ws: WebSocket):
        frame_count = 0
        try:
            while True:
                text = await ws.receive_text()
                if len(text.encode("utf-8")) > max_ws_inbound_message_bytes():
                    self._bump_rejection("ws_oversize")
                    continue
                try:
                    data = json.loads(text)
                except json.JSONDecodeError:
                    self._bump_rejection("invalid_json")
                    continue
                if not isinstance(data, dict):
                    self._bump_rejection("invalid_envelope")
                    continue
                event_type = data.get("type")
                payload = data.get("payload")

                if not event_type or not payload:
                    self._bump_rejection("invalid_envelope")
                    continue

                if event_type == "vision_frame":
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                        self._bump_eviction("vision")
                    b64_img = payload.get("image_b64", "")
                    lim = max_vision_frame_bytes()
                    if not _b64_fits_decoded_limit(b64_img, lim):
                        self._bump_rejection("vision_reject")
                        continue
                    try:
                        jpeg_bytes = base64.b64decode(b64_img, validate=False)
                    except (binascii.Error, ValueError):
                        self._bump_rejection("vision_reject")
                        continue
                    if jpeg_bytes and len(jpeg_bytes) <= lim:
                        self.vision_queue.put_nowait(jpeg_bytes)
                        frame_count += 1
                        if frame_count % 10 == 0:
                            _log.debug("Nomad Bridge: received %d vision frames", frame_count)
                        self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                    else:
                        self._bump_rejection("vision_reject")

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                        self._bump_eviction("audio")
                    b64_pcm = payload.get("audio_b64", "")
                    lim_a = max_audio_pcm_bytes()
                    if not _b64_fits_decoded_limit(b64_pcm, lim_a):
                        self._bump_rejection("audio_reject")
                        continue
                    try:
                        raw_audio = base64.b64decode(b64_pcm, validate=False)
                    except (binascii.Error, ValueError):
                        self._bump_rejection("audio_reject")
                        continue
                    if raw_audio and len(raw_audio) <= lim_a:
                        self.audio_queue.put_nowait(raw_audio)
                        pcm = raw_audio[: (len(raw_audio) // 2) * 2]
                        if len(pcm) >= 2:
                            shorts = struct.unpack(f"<{len(pcm) // 2}h", pcm)
                            if shorts:
                                rms = math.sqrt(sum(s * s for s in shorts) / len(shorts)) / 32768.0
                                self.last_rms = rms
                                if self.dashboard_queues:
                                    self.broadcast_to_dashboards(
                                        {"type": "audio_energy", "payload": {"rms": rms}}
                                    )
                    else:
                        self._bump_rejection("audio_reject")

                elif event_type == "telemetry":
                    if not isinstance(payload, dict):
                        self._bump_rejection("telemetry_reject")
                        continue
                    if len(payload) > max_telemetry_dict_keys():
                        self._bump_rejection("telemetry_reject")
                        continue
                    self.broadcast_to_dashboards({"type": "telemetry", "payload": dict(payload)})
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                        self._bump_eviction("telemetry")
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
