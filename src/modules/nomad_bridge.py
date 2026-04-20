import asyncio
import base64
import json
import logging
import math
import struct
import time
import hmac
import hashlib
import os
from typing import Any, Callable, Coroutine, Union, Optional
from .hardware_abstraction import HardwareContext, ComputeTier
from ..observability.metrics import record_nomad_bridge_connection

try:
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status
    _FASTAPI_AVAILABLE = True
except ImportError:
    class WebSocketDisconnect(Exception):
        """Placeholder when FastAPI is not installed (WebSocket routes are disabled)."""
    FastAPI = None  # type: ignore[misc, assignment]
    WebSocket = Any  # type: ignore[misc, assignment]
    Query = Any # type: ignore[misc, assignment]
    status = Any # type: ignore[misc, assignment]
    _FASTAPI_AVAILABLE = False

_log = logging.getLogger(__name__)


class NomadBridge:
    """
    Nomad LAN bridge for smartphone peripherals (Module S).

    Async WebSocket listener for real-world sensor data (vision frames, audio, telemetry).
    Requires optional dependency ``fastapi`` (``pip install -e ".[runtime]"``) for ``app``.
    """

    def __init__(self) -> None:
        # Items: raw JPEG bytes or dict { raw_bytes, meta?, detections? } (see vision_adapter)
        # Phase 9: Tightened queues for real-time priority
        self.vision_queue: asyncio.Queue[Union[bytes, dict[str, Any]]] = asyncio.Queue(maxsize=2)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=20)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        # Bloque 13.1: relay queue for chat_text messages arriving via /ws/nomad
        self.chat_text_queue: asyncio.Queue[str] = asyncio.Queue(maxsize=20)

        # Phase 10: L0 Dashboard Telemetry Broadcaster
        self.dashboard_queues: list[asyncio.Queue[dict[str, Any]]] = []
        self.last_rms = 0.0
        self._last_sensor_update = time.time()
        self._is_vessel_healthy = False
        self._last_dash_frame = 0  # Throttling for dashboard (S.2.1)
        self._last_heartbeat = 0.0
        # Bloque 13.1: VAD speaking state tracked server-side
        self.vad_speaking: bool = False
        
        # S.1.1 Hardening: Vessel State Tracking (HAL Aligned)
        self.vessel_context: HardwareContext = HardwareContext(
            device_label="none",
            compute_tier=ComputeTier.EDGE_MOBILE,
            battery_fraction=None
        )
        self.vessel_metadata: dict[str, Any] = {
            "thermal_state": "nominal",
            "connection_type": "unknown",
            "latency_ms": 0,
            "vessel_id": "none"
        }

        self.app: Any = None

        if not _FASTAPI_AVAILABLE or FastAPI is None:
            _log.warning(
                "Nomad Bridge: FastAPI not installed; queues work but HTTP/WebSocket app is disabled. "
                "Install with: pip install -e \".[runtime]\""
            )
        else:
            self.app = FastAPI(title="Nomad Bridge Sensor Endpoint")

            @self.app.get("/")
            async def nomad_root():
                return {"status": "ok", "bridge": "nomad", "vessel_healthy": self._is_vessel_healthy}

            @self.app.websocket("/ws/nomad")
            async def websocket_nomad_endpoint(
                websocket: WebSocket,
                timestamp: str | None = Query(None),
                signature: str | None = Query(None)
            ) -> None:
                # Phase 9: S.4 Cryptographic Handshake (HMAC)
                secret = os.environ.get("KERNEL_NOMAD_SECRET")
                if secret:
                    if not timestamp or not signature:
                        _log.warning("Nomad Bridge: Connection rejected. Missing HMAC query parameters.")
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
                    expected_sig = hmac.new(secret.encode(), timestamp.encode(), hashlib.sha256).hexdigest()
                    if not hmac.compare_digest(signature, expected_sig):
                        _log.warning("Nomad Bridge: Connection rejected. Invalid HMAC signature.")
                        record_nomad_bridge_connection("hmac_fail")
                        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
                        return
                else:
                    _log.warning("KERNEL_NOMAD_SECRET not set. Nomad Bridge is operating in insecure mode!")
                    record_nomad_bridge_connection("secret_missing")

                await self.handle_websocket(websocket)

    async def handle_websocket(
        self,
        websocket: WebSocket,
        chat_text_callback: Optional[Callable[[str], Coroutine[Any, Any, None]]] = None,
    ) -> None:
        """Handles a Nomad smartphone connection after handshake.

        Args:
            websocket: The connected WebSocket client.
            chat_text_callback: Optional async callable invoked with each dequeued
                ``chat_text`` message.  When provided, a consumer task runs
                concurrently alongside the recv/send loops.
        """
        try:
            await websocket.accept()
            self._is_vessel_healthy = True
            self._last_heartbeat = time.time()
            record_nomad_bridge_connection("success")
            _log.info("Nomad Bridge: Handshake successful. Nomad Vessel is connected.")
        except Exception as e:
            _log.error("Nomad Bridge: Failed to accept connection: %s", e)
            return

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
            _log.info("Nomad Bridge: Nomad Vessel disconnected.")

    def public_queue_stats(self) -> dict[str, Any]:
        """Return observable queue depths and vessel health for /health endpoint (Module S.1/S.2.1)."""
        return {
            "vision_queue_depth": self.vision_queue.qsize(),
            "audio_queue_depth": self.audio_queue.qsize(),
            "telemetry_queue_depth": self.telemetry_queue.qsize(),
            "charm_feedback_queue_depth": self.charm_feedback_queue.qsize(),
            "vessel_healthy": self._is_vessel_healthy,
            "last_sensor_update_keys": ["_last_sensor_update"],
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
                    if msg:
                        try:
                            # If msg is a dict (json), extract text; if string, use it directly.
                            text = msg.get("text", "") if isinstance(msg, dict) else str(msg)
                            if text:
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
            except Exception:
                pass
        
        # Periodic debug log to ensure broadcast is reaching targets
        if time.time() - getattr(self, "_last_broadcast_log", 0) > 10.0:
            _log.info("Nomad Bridge: Broadcasting to %d dashboard(s). Latest type: %s", len(self.dashboard_queues), msg.get("type"))
            self._last_broadcast_log = time.time()

    def public_queue_stats(self) -> dict[str, Any]:
        """Returns key metrics and queue depths for the L0 health monitor.

        Bloque 14.2: includes ``last_rms`` (float [0,1]) and ``vad_speaking`` (bool)
        so the clinical dashboard can render raw sensor floats without polling the
        audio broadcast separately.
        """
        rms = self.last_rms
        rms = rms if (isinstance(rms, float) and math.isfinite(rms)) else 0.0
        return {
            "vision_queue_depth": self.vision_queue.qsize(),
            "audio_queue_depth": self.audio_queue.qsize(),
            "telemetry_queue_depth": self.telemetry_queue.qsize(),
            "charm_feedback_queue_depth": self.charm_feedback_queue.qsize(),
            "vessel_online": is_vessel_online(),
            "vessel_metadata": self.vessel_metadata,
            "vessel_context": self.vessel_context.to_public_dict(),
            "last_sensor_update_delta": round(time.time() - self._last_sensor_update, 2),
            # Bloque 14.2 — clinical raw fields
            "last_rms": round(rms, 4),
            "vad_speaking": bool(self.vad_speaking),
        }

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
                        if now - self._last_dash_frame > 0.05: # Max 20fps for dashboard
                            self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                            self._last_dash_frame = now
                        
                        # Phase 9: Zero-latency discard
                        while self.vision_queue.full():
                            self.vision_queue.get_nowait()
                        
                        # Phase 14: Pass meta signals into the queue alongside raw bytes
                        combined_payload = {
                            "raw_bytes": raw_bytes,
                            "meta": payload.get("meta", {}), 
                            "detections": payload.get("detections", [])
                        }
                        self.vision_queue.put_nowait(combined_payload)
                        self._last_sensor_update = time.time()
                        self._is_vessel_healthy = True

                    elif event_type == "audio_pcm":
                        # Tightened audio queue management
                        if self.audio_queue.full():
                            for _ in range(5):
                                try: self.audio_queue.get_nowait()
                                except asyncio.QueueEmpty: break
                                
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
                                shorts = struct.unpack(f"<{count}h", pcm_bytes[:count * 2])
                                if shorts:
                                    sum_sq = sum(float(s) * s for s in shorts)
                                    rms = (math.sqrt(sum_sq / len(shorts)) / 32768.0) * 5.5 
                                    rms = min(1.0, rms)
                                    if math.isfinite(rms):
                                        self.last_rms = rms
                                        self.broadcast_to_dashboards({
                                            "type": "audio_energy", 
                                            "payload": {"rms": rms}
                                        })
                            except (struct.error, ZeroDivisionError, ValueError) as e:
                                pass

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

                        self.vessel_metadata.update({
                            "thermal_state": payload.get("thermal", self.vessel_metadata["thermal_state"]),
                            "connection_type": payload.get("connection", self.vessel_metadata["connection_type"]),
                            "vessel_id": payload.get("vessel_id", self.vessel_metadata["vessel_id"])
                        })
                        
                        self.broadcast_to_dashboards({"type": "telemetry", "payload": payload})
                        if self.telemetry_queue.full():
                            self.telemetry_queue.get_nowait()
                        self.telemetry_queue.put_nowait(payload)
                        self._last_sensor_update = time.time()

                    elif event_type == "vad_event":
                        # Bloque 13.1: track VAD state server-side for situational awareness
                        try:
                            state = str(payload.get("state", "")).strip()
                            if state == "speech_start":
                                self.vad_speaking = True
                            elif state == "speech_end":
                                self.vad_speaking = False
                            self.broadcast_to_dashboards({
                                "type": "vad_state",
                                "payload": {"speaking": self.vad_speaking},
                            })
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
                        self.broadcast_to_dashboards({
                            "type": "rtc_signal",
                            "event": event_type,
                            "payload": payload
                        })

                except Exception as inner_e:
                    _log.error("Nomad Bridge inner loop error: %s", inner_e)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error("Nomad Bridge read error: %s", e)

    async def _send_loop(self, ws: WebSocket) -> None:
        try:
            while True:
                try:
                    payload = await asyncio.wait_for(self.charm_feedback_queue.get(), timeout=10.0)
                    await ws.send_json({
                        "type": "charm_feedback", # Also known as somatic_feedback in Phase 9
                        "payload": payload,
                    })
                except asyncio.TimeoutError:
                    ping_start = time.perf_counter()
                    await ws.send_json({"type": "ping", "payload": {"timestamp": ping_start}})
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _log.error("Nomad Bridge send error: %s", e)


_NOMAD_BRIDGE = NomadBridge()

def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE


def is_vessel_online() -> bool:
    """Returns True if a Nomad Vessel sent data in the last 5 seconds."""
    bridge = get_nomad_bridge()
    if time.time() - bridge._last_sensor_update > 5.0:
        return False
    return bridge._is_vessel_healthy
