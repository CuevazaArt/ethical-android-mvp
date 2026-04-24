"""
LAN Nomad bridge (Module S / PLAN_WORK_DISTRIBUTION_TREE Bloque S.1).

WebSocket JSON events (client → server):

- ``type: vision_frame``, ``payload: { "image_b64": "<base64 JPEG>" }``
- ``type: audio_pcm``, ``payload: { "audio_b64": "<base64 raw PCM>" }``
- ``type`` = ``telemetry``, ``payload``: flat sensor dict (accelerometer, battery, temperature, …)

Server → client: ``type: charm_feedback``, ``payload``: charm vector dict (from kernel).

``NomadVisionConsumer`` in ``vision_adapter.py`` drains ``vision_queue`` (``queue.Queue``, async via ``asyncio.to_thread``); audio adapter drains ``audio_queue``.
``vision_queue_threadsafe`` mirrors accepted JPEG bytes for ``VisionContinuousDaemon`` (``vision_inference.py``) so the kernel thread never contends with the event loop.

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
# Status: REAL

import asyncio
import base64
import hashlib
import hmac
import logging
import math
import os
import queue as std_queue
import struct
import threading
import time
from collections import deque
from collections.abc import Callable, Coroutine
from typing import Any

from src.modules.somatic.hardware_abstraction import ComputeTier, HardwareContext
from src.observability.metrics import record_nomad_bridge_connection

try:
    from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect, status

    _FASTAPI_AVAILABLE = True
except ImportError:

    class _WebSocketDisconnectStub(Exception):
        """Placeholder when FastAPI is not installed (WebSocket routes are disabled)."""

    WebSocketDisconnect = _WebSocketDisconnectStub  # type: ignore[misc, assignment]
    FastAPI = None  # type: ignore[misc, assignment]
    WebSocket = Any  # type: ignore[misc, assignment]
    Query = Any  # type: ignore[misc, assignment]
    status = Any  # type: ignore[misc, assignment]
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


def _nomad_charm_replay_maxlen() -> int:
    """Bounded deque for ``charm_feedback`` payloads to replay after a brief WS drop (Bloque 22.1)."""

    raw = _parse_positive_int_env("KERNEL_NOMAD_CHARM_REPLAY_MAX", 32)
    return max(4, min(128, raw))


_DEFAULT_WS_MAX_MESSAGE_BYTES = 4 * 1024 * 1024
_CAP_WS_MAX_MESSAGE_BYTES = 32 * 1024 * 1024
_MIN_WS_MAX_MESSAGE_BYTES = 64


def nomad_chat_text_queue_maxsize() -> int:
    """Bounded async queue for ``chat_text`` relay (Bloque 22.1); env ``KERNEL_NOMAD_CHAT_TEXT_QUEUE_MAX``."""

    raw = os.environ.get("KERNEL_NOMAD_CHAT_TEXT_QUEUE_MAX", "").strip()
    if not raw:
        return 128
    try:
        n = int(raw, 10)
    except ValueError:
        return 128
    return max(8, min(n, 512))


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

    def __init__(self) -> None:
        # Items: raw JPEG bytes or dict { raw_bytes, meta?, detections? } (see vision_adapter)
        # Phase 9: Tightened queues for real-time priority
        self.vision_queue: asyncio.Queue[bytes | dict[str, Any]] = asyncio.Queue(maxsize=2)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=20)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        # Bloque 13.1 / 22.1: relay queue for chat_text via /ws/nomad (wider cap for 4G/5G bursts)
        self.chat_text_queue: asyncio.Queue[str | dict[str, Any]] = asyncio.Queue(
            maxsize=nomad_chat_text_queue_maxsize()
        )
        # Bloque 22.1: last charm payloads to push immediately after a flaky reconnect.
        self._charm_feedback_replay: deque[dict[str, Any]] = deque(
            maxlen=_nomad_charm_replay_maxlen()
        )
        # Thread-safe mirror of JPEG bytes for VisionContinuousDaemon (docs + tests v4).
        self.vision_queue_threadsafe: std_queue.Queue[bytes] = std_queue.Queue(maxsize=8)

        # Phase 10: L0 Dashboard Telemetry Broadcaster
        self.dashboard_queues: list[asyncio.Queue[dict[str, Any]]] = []
        self.last_rms = 0.0
        self._last_sensor_update = time.time()
        self._is_vessel_healthy = False
        self._last_dash_frame: float = 0.0  # Throttling for dashboard (S.2.1)
        self._last_heartbeat = 0.0
        self._is_connected: bool = False
        self._telemetry_lock = threading.Lock()
        self._latest_telemetry: dict[str, Any] = {}
        # Bloque 13.1: VAD speaking state tracked server-side
        self.vad_speaking: bool = False

        # S.1.1 Hardening: Vessel State Tracking (HAL Aligned)
        self.vessel_context: HardwareContext = HardwareContext(
            device_label="none", compute_tier=ComputeTier.EDGE_MOBILE, battery_fraction=None
        )
        self.vessel_metadata: dict[str, Any] = {
            "thermal_state": "nominal",
            "connection_type": "unknown",
            "latency_ms": 0,
            "vessel_id": "none",
        }

        self.app: Any = None

        if not _FASTAPI_AVAILABLE or FastAPI is None:
            _log.warning(
                "Nomad Bridge: FastAPI not installed; queues work but HTTP/WebSocket app is disabled. "
                'Install with: pip install -e ".[runtime]"'
            )
        else:
            self.app = FastAPI(title="Nomad Bridge Sensor Endpoint")

            @self.app.get("/")
            async def nomad_root():
                return {
                    "status": "ok",
                    "bridge": "nomad",
                    "vessel_healthy": self._is_vessel_healthy,
                }

            @self.app.websocket("/ws/nomad")
            async def websocket_nomad_endpoint(
                websocket: WebSocket,
                timestamp: str | None = Query(None),
                signature: str | None = Query(None),
            ) -> None:
                # Phase 9: S.4 Cryptographic Handshake (HMAC)
                secret = os.environ.get("KERNEL_NOMAD_SECRET")
                if secret:
                    if not timestamp or not signature:
                        _log.warning(
                            "Nomad Bridge: Connection rejected. Missing HMAC query parameters."
                        )
                        record_nomad_bridge_connection("hmac_missing")
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return

                    # Prevent replay attacks (30 seconds window)
                    try:
                        ts_float = float(timestamp)
                        if abs(time.time() - ts_float) > 30.0:
                            _log.warning("Nomad Bridge: Connection rejected. Timestamp expired.")
                            record_nomad_bridge_connection("timestamp_expired")
                            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                            return
                    except ValueError:
                        record_nomad_bridge_connection("hmac_invalid")
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return

                    # Verify HMAC-SHA256 signature
                    expected_sig = hmac.new(
                        secret.encode(), timestamp.encode(), hashlib.sha256
                    ).hexdigest()
                    if not hmac.compare_digest(signature, expected_sig):
                        _log.warning("Nomad Bridge: Connection rejected. Invalid HMAC signature.")
                        record_nomad_bridge_connection("hmac_fail")
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return
                else:
                    _log.warning(
                        "KERNEL_NOMAD_SECRET not set. Nomad Bridge is operating in insecure mode!"
                    )
                    record_nomad_bridge_connection("secret_missing")

                await self.handle_websocket(websocket)

    async def handle_websocket(
        self,
        websocket: WebSocket,
        chat_text_callback: Callable[[str], Coroutine[Any, Any, None]] | None = None,
        session_ready_hook: Callable[[WebSocket], Coroutine[Any, Any, None]] | None = None,
    ) -> None:
        """Handles a Nomad smartphone connection after handshake.

        Args:
            websocket: The connected WebSocket client.
            chat_text_callback: Optional async callable invoked with each dequeued
                ``chat_text`` message.  When provided, a consumer task runs
                concurrently alongside the recv/send loops.
            session_ready_hook: Optional coroutine run once immediately after the
                socket is accepted (Bloque 22.2 — e.g. emit ``SYNC_IDENTITY``).
        """
        from starlette.websockets import WebSocketState

        try:
            if websocket.client_state == WebSocketState.CONNECTING:
                await websocket.accept()
            self._is_vessel_healthy = True
            self._is_connected = True
            self._last_heartbeat = time.time()
            record_nomad_bridge_connection("success")
            _log.info("Nomad Bridge: Handshake successful. Nomad Vessel is connected.")
        except Exception as e:
            _log.error("Nomad Bridge: Failed to accept connection: %s", e)
            return

        await self._flush_charm_feedback_replay(websocket)

        if session_ready_hook is not None:
            try:
                await session_ready_hook(websocket)
            except Exception as hook_e:
                _log.warning("Nomad Bridge: session_ready_hook error: %s", hook_e)

        tasks: list[asyncio.Task[Any]] = [
            asyncio.create_task(self._recv_loop(websocket)),
            asyncio.create_task(self._send_loop(websocket)),
        ]
        if chat_text_callback is not None:
            tasks.append(asyncio.create_task(self._chat_text_consumer(chat_text_callback)))

        try:
            _, pending = await asyncio.wait(
                tasks,
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()
        except Exception as e:
            _log.error("Nomad Bridge exception in handler: %s", e)
        finally:
            self._is_vessel_healthy = False
            self._is_connected = False
            _log.info("Nomad Bridge: Nomad Vessel disconnected.")

    @property
    def is_somatic_blind(self) -> bool:
        """True when the socket is marked connected but the heartbeat is stale (>5 s)."""
        if not self._is_connected:
            return False
        dt = time.time() - float(self._last_heartbeat)
        if not math.isfinite(dt):
            return False
        return dt > 5.0

    def public_queue_stats(self) -> dict[str, Any]:
        """Return observable queue depths and vessel health for /health endpoint (Module S.1/S.2.1)."""
        # Peek at the latest telemetry item without consuming it
        latest_tel: dict[str, Any] | None = None
        try:
            latest_tel = self.telemetry_queue.get_nowait()
            self.telemetry_queue.put_nowait(latest_tel)
        except asyncio.QueueEmpty:
            latest_tel = None

        lr = float(self.last_rms)
        if not math.isfinite(lr):
            lr = 0.0
        now = time.time()
        last_delta = now - float(self._last_sensor_update)
        if not math.isfinite(last_delta):
            last_delta = 0.0

        return {
            "schema": "nomad_bridge_queue_stats_v4",
            "vision_queue_depth": self.vision_queue.qsize(),
            "vision_sync_queued": self.vision_queue_threadsafe.qsize(),
            "audio_queue_depth": self.audio_queue.qsize(),
            "telemetry_queue_depth": self.telemetry_queue.qsize(),
            "charm_feedback_queue_depth": self.charm_feedback_queue.qsize(),
            "charm_feedback_queued": self.charm_feedback_queue.qsize(),
            "charm_feedback_max": self.charm_feedback_queue.maxsize,
            "chat_text_queue_depth": self.chat_text_queue.qsize(),
            "chat_text_queue_max": self.chat_text_queue.maxsize,
            "charm_feedback_replay_pending": len(self._charm_feedback_replay),
            "vessel_healthy": self._is_vessel_healthy,
            "vessel_online": bool(self._is_vessel_healthy),
            "last_rms": lr,
            "vad_speaking": bool(self.vad_speaking),
            "dashboard_subscribers": len(self.dashboard_queues),
            "vessel_metadata": dict(self.vessel_metadata),
            "vessel_context": self.vessel_context.to_public_dict(),
            "last_sensor_update_delta": round(last_delta, 3),
            "last_sensor_update_keys": ["_last_sensor_update"],
            "latest_telemetry_present": latest_tel is not None,
            "latest_telemetry_keys": list(latest_tel.keys()) if latest_tel else [],
            "limits": {
                "max_vision_frame_bytes": max_vision_frame_bytes(),
                "max_audio_pcm_bytes": max_audio_pcm_bytes(),
                "max_telemetry_keys": max_telemetry_dict_keys(),
                "max_ws_message_bytes": max_ws_inbound_message_bytes(),
            },
        }

    async def _chat_text_consumer(
        self,
        callback: Callable[[str], Coroutine[Any, Any, None]],
    ) -> None:
        """Bloque 13.1: drain chat_text_queue and invoke callback for each message.

        Runs concurrently with _recv_loop / _send_loop and is cancelled on disconnect.
        """
        try:
            while True:
                try:
                    msg = await self.chat_text_queue.get()
                    if isinstance(msg, dict):
                        text = str(msg.get("text", "")).strip()
                    else:
                        text = str(msg).strip() if msg else ""
                    if text:
                        try:
                            await callback(text)
                        except Exception as cb_e:
                            _log.warning("Nomad Bridge: chat_text_callback error: %s", cb_e)
                except asyncio.CancelledError:
                    raise
                except Exception as e:
                    _log.warning("Nomad Bridge: _chat_text_consumer error: %s", e)
                    await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass

    def broadcast_to_dashboards(self, msg: dict[str, Any]) -> None:
        """Sends a message to all connected dashboards (Module S / Phase 10)."""
        if not self.dashboard_queues:
            return

        for q in self.dashboard_queues:
            try:
                if q.full():
                    q.get_nowait()
                q.put_nowait(msg)
            except asyncio.QueueFull:
                _log.debug("Nomad Bridge: dashboard queue full; dropped oldest then retry skipped")
            except Exception as dash_e:
                _log.warning("Nomad Bridge: dashboard broadcast error: %s", dash_e)

        # Periodic debug log to ensure broadcast is reaching targets
        if time.time() - getattr(self, "_last_broadcast_log", 0) > 10.0:
            _log.info(
                "Nomad Bridge: Broadcasting to %d dashboard(s). Latest type: %s",
                len(self.dashboard_queues),
                msg.get("type"),
            )
            self._last_broadcast_log = time.time()

    async def _recv_loop(self, ws: WebSocket) -> None:
        frame_count = 0
        try:
            while True:
                try:
                    data = await ws.receive_json()
                    if not isinstance(data, dict):
                        _log.warning("Nomad Bridge: Hostile or malformed payload. Not a dict.")
                        continue

                    event_type = data.get("type")
                    payload = data.get("payload")

                    if event_type == "heartbeat":
                        self._last_heartbeat = time.time()
                        continue

                    if not event_type or not isinstance(payload, dict):
                        continue

                    if event_type == "vision_frame":
                        frame_count += 1
                        b64_img = payload.get("image_b64", "")

                        try:
                            raw_bytes = base64.b64decode(b64_img)
                        except Exception as e:
                            _log.error("Nomad Bridge: Invalid b64 image data: %s", e)
                            continue

                        if frame_count % 10 == 0:
                            _log.info("Nomad Bridge: Received 10 vision frames (Stream Active)")

                        # Throttled Dashboard Broadcast (Phase 10 Stability)
                        now = time.time()
                        if now - self._last_dash_frame > 0.05:  # Max 20fps for dashboard
                            self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                            self._last_dash_frame = now

                        # Phase 9: Zero-latency discard
                        while self.vision_queue.full():
                            self.vision_queue.get_nowait()

                        # Phase 14: Pass meta signals into the queue alongside raw bytes
                        combined_payload = {
                            "raw_bytes": raw_bytes,
                            "meta": payload.get("meta", {}),
                            "detections": payload.get("detections", []),
                        }
                        self.vision_queue.put_nowait(combined_payload)
                        try:
                            if isinstance(raw_bytes, bytes | bytearray) and len(raw_bytes) > 0:
                                if self.vision_queue_threadsafe.full():
                                    try:
                                        self.vision_queue_threadsafe.get_nowait()
                                    except std_queue.Empty:
                                        pass
                                self.vision_queue_threadsafe.put_nowait(bytes(raw_bytes))
                        except Exception as vts_e:
                            _log.debug("Nomad Bridge: vision threadsafe mirror skipped: %s", vts_e)
                        self._last_sensor_update = time.time()
                        self._is_vessel_healthy = True

                    elif event_type == "audio_pcm":
                        # Tightened audio queue management
                        if self.audio_queue.full():
                            for _ in range(5):
                                try:
                                    self.audio_queue.get_nowait()
                                except asyncio.QueueEmpty:
                                    break

                        b64_pcm = payload.get("audio_b64", "")

                        try:
                            pcm_bytes = base64.b64decode(b64_pcm)
                        except Exception as e:
                            _log.error("Nomad Bridge: Invalid b64 audio data: %s", e)
                            continue

                        self.audio_queue.put_nowait(pcm_bytes)

                        # Calculate very basic rms for dashboard audio bar and Thalamus
                        if pcm_bytes and len(pcm_bytes) >= 2:
                            try:
                                count = len(pcm_bytes) // 2
                                shorts = struct.unpack(f"<{count}h", pcm_bytes[: count * 2])
                                if shorts:
                                    sum_sq = sum(float(s) * s for s in shorts)
                                    rms = (math.sqrt(sum_sq / len(shorts)) / 32768.0) * 5.5
                                    rms = min(1.0, rms)
                                    if math.isfinite(rms):
                                        self.last_rms = rms
                                        self.broadcast_to_dashboards(
                                            {"type": "audio_energy", "payload": {"rms": rms}}
                                        )
                            except (struct.error, ZeroDivisionError, ValueError) as rms_e:
                                _log.debug("Nomad Bridge: RMS decode skipped: %s", rms_e)

                    elif event_type == "telemetry":
                        batt = payload.get("battery")
                        if batt is not None:
                            try:
                                val = float(batt)
                                if math.isfinite(val):
                                    self.vessel_context.battery_fraction = val
                            except (ValueError, TypeError):
                                pass

                        device_label = payload.get("device_label") or payload.get("vessel_id")
                        if device_label:
                            self.vessel_context.device_label = str(device_label)

                        self.vessel_metadata.update(
                            {
                                "thermal_state": payload.get(
                                    "thermal", self.vessel_metadata["thermal_state"]
                                ),
                                "connection_type": payload.get(
                                    "connection", self.vessel_metadata["connection_type"]
                                ),
                                "vessel_id": payload.get(
                                    "vessel_id", self.vessel_metadata["vessel_id"]
                                ),
                            }
                        )

                        self.broadcast_to_dashboards({"type": "telemetry", "payload": payload})
                        if self.telemetry_queue.full():
                            self.telemetry_queue.get_nowait()
                        self.telemetry_queue.put_nowait(payload)
                        with self._telemetry_lock:
                            self._latest_telemetry = dict(payload)
                        self._last_sensor_update = time.time()

                    elif event_type == "vad_event":
                        # Bloque 13.1: track VAD state server-side for situational awareness
                        try:
                            state = str(payload.get("state", "")).strip()
                            if state == "speech_start":
                                self.vad_speaking = True
                            elif state == "speech_end":
                                self.vad_speaking = False
                            self.broadcast_to_dashboards(
                                {
                                    "type": "vad_state",
                                    "payload": {"speaking": self.vad_speaking},
                                }
                            )
                        except Exception as vad_e:
                            _log.warning("Nomad Bridge: vad_event parse error: %s", vad_e)

                    elif event_type == "chat_text":
                        # Bloque 13.1: relay typed text from Nomad UI to the kernel chat queue
                        # (processed by chat_server.py with KERNEL_NOMAD_CHAT_TIMEOUT)
                        try:
                            text = str(payload.get("text", "")).strip()
                            if text:
                                if self.chat_text_queue.full():
                                    try:
                                        self.chat_text_queue.get_nowait()
                                    except asyncio.QueueEmpty:
                                        pass
                                self.chat_text_queue.put_nowait(text)
                                _log.debug("Nomad Bridge: chat_text queued (%d chars)", len(text))
                        except Exception as ct_e:
                            _log.warning("Nomad Bridge: chat_text parse error: %s", ct_e)

                    elif event_type == "pong":
                        sent_at = payload.get("timestamp", 0)
                        if sent_at > 0:
                            latency = (time.perf_counter() - sent_at) * 1000
                            if math.isfinite(latency):
                                self.vessel_metadata["latency_ms"] = int(latency)

                    elif event_type in ("rtc_offer", "rtc_answer", "rtc_ice"):
                        self.broadcast_to_dashboards(
                            {"type": "rtc_signal", "event": event_type, "payload": payload}
                        )

                except Exception as inner_e:
                    # Starlette/FastAPI: 'Cannot call "receive" once a disconnect message has been received.'
                    if "disconnect message has been received" in str(inner_e).lower():
                        _log.info("Nomad Bridge: Handshake loop detected client disconnect.")
                        break
                    _log.error("Nomad Bridge inner loop error: %s", inner_e)
                    # For other errors, break the loop to avoid spinning on a broken socket
                    break

        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge read error: {e}")

    def _remember_charm_for_replay(self, payload: dict[str, Any]) -> None:
        """Mirror last payloads for immediate post-handshake flush (mobile WS flicker)."""

        try:
            if isinstance(payload, dict):
                self._charm_feedback_replay.append(dict(payload))
        except Exception:
            pass

    async def _flush_charm_feedback_replay(self, ws: WebSocket) -> None:
        """Emit replay buffer before competing with live ``charm_feedback_queue`` consumers."""

        while self._charm_feedback_replay:
            p = self._charm_feedback_replay.popleft()
            try:
                await ws.send_json({"type": "charm_feedback", "payload": p})
            except Exception as exc:
                _log.warning("Nomad Bridge: charm replay flush failed: %s", exc)
                try:
                    self._charm_feedback_replay.appendleft(p)
                except Exception:
                    pass
                break

    async def _send_loop(self, ws: WebSocket) -> None:
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(self.charm_feedback_queue.get(), timeout=10.0)
                except TimeoutError:
                    payload = None

                if payload is not None:
                    try:
                        await ws.send_json(
                            {
                                "type": "charm_feedback",
                                "payload": payload,
                            }
                        )
                    except Exception as send_e:
                        _log.warning(
                            "Nomad Bridge: charm_feedback send failed, buffering replay: %s", send_e
                        )
                        self._remember_charm_for_replay(payload)
                        break
                else:
                    ping_start = time.perf_counter()
                    try:
                        await ws.send_json({"type": "ping", "payload": {"timestamp": ping_start}})
                    except Exception as ping_e:
                        _log.warning("Nomad Bridge: ping send failed: %s", ping_e)
                        break
        except asyncio.CancelledError:
            raise
        except Exception as e:
            _log.error("Nomad Bridge send error: %s", e)


# Global instance
_NOMAD_BRIDGE = NomadBridge()


def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE


def is_vessel_online() -> bool:
    """Returns True if a Nomad Vessel sent data in the last 5 seconds."""
    bridge = get_nomad_bridge()
    if time.time() - bridge._last_sensor_update > 5.0:
        return False
    return bridge._is_vessel_healthy
