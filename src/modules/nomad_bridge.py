import asyncio
import base64
import json
import logging
import math
import struct
import time
from typing import Any, Union, Optional
from .hardware_abstraction import HardwareContext, ComputeTier

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


class NomadBridge:
    """
    Nomad LAN bridge for smartphone peripherals (Module S).

    Async WebSocket listener for real-world sensor data (vision frames, audio, telemetry).
    Requires optional dependency ``fastapi`` (``pip install -e ".[runtime]"``) for ``app``.
    """

    def __init__(self) -> None:
        # Items: raw JPEG bytes or dict { raw_bytes, meta?, detections? } (see vision_adapter)
        self.vision_queue: asyncio.Queue[Union[bytes, dict[str, Any]]] = asyncio.Queue(maxsize=5)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=30)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        
        # Phase 10: L0 Dashboard Telemetry Broadcaster
        self.dashboard_queues: list[asyncio.Queue[dict[str, Any]]] = []
        self.last_rms = 0.0
        self._last_sensor_update = time.time()
        self._is_vessel_healthy = False
        
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
            return

        self.app = FastAPI(title="Nomad Bridge Sensor Endpoint")

        @self.app.websocket("/ws/nomad")
        async def websocket_nomad_endpoint(websocket: WebSocket) -> None:
            await self.handle_websocket(websocket)

    async def handle_websocket(self, websocket: WebSocket) -> None:
        """Handles a Nomad smartphone connection."""
        try:
            await websocket.accept()
            _log.info("Nomad Bridge: Handshake successful. Nomad Vessel is connected.")
        except Exception as e:
            _log.error("Nomad Bridge: Failed to accept connection: %s", e)
            return

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
            _log.info("Nomad Bridge: Nomad Vessel disconnected.")

    def broadcast_to_dashboards(self, msg: dict[str, Any]) -> None:
        """Sends a message to all connected dashboards (Module S / Phase 10)."""
        for q in self.dashboard_queues:
            try:
                if q.full():
                    q.get_nowait()
                q.put_nowait(msg)
            except Exception:
                pass

    def public_queue_stats(self) -> dict[str, Any]:
        """Returns key metrics and queue depths for the L0 health monitor."""
        return {
            "vision_queue_depth": self.vision_queue.qsize(),
            "audio_queue_depth": self.audio_queue.qsize(),
            "telemetry_queue_depth": self.telemetry_queue.qsize(),
            "charm_feedback_queue_depth": self.charm_feedback_queue.qsize(),
            "vessel_online": is_vessel_online(),
            "vessel_metadata": self.vessel_metadata,
            "vessel_context": self.vessel_context.to_public_dict(),
            "last_sensor_update_delta": round(time.time() - self._last_sensor_update, 2)
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
                            
                        self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                        
                        if self.vision_queue.full():
                            self.vision_queue.get_nowait()
                        
                        # Phase 14: Pass meta signals into the queue alongside raw bytes
                        combined_payload = {
                            "raw_bytes": raw_bytes,
                            "meta": payload.get("meta", {}), # Contains lip_movement, human_presence
                            "detections": payload.get("detections", [])
                        }
                        self.vision_queue.put_nowait(combined_payload)
                        self._last_sensor_update = time.time()
                        self._is_vessel_healthy = True

                    elif event_type == "audio_pcm":
                        if self.audio_queue.full():
                            self.audio_queue.get_nowait()
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
                                    rms = math.sqrt(sum_sq / len(shorts)) / 32768.0
                                    if math.isfinite(rms):
                                        self.last_rms = rms
                                        if self.dashboard_queues:
                                            self.broadcast_to_dashboards({
                                                "type": "audio_energy", 
                                                "payload": {"rms": rms}
                                            })
                            except (struct.error, ZeroDivisionError, ValueError) as e:
                                _log.debug("Nomad Bridge: Audio RMS failed: %s", e)
                                pass # Corrupted audio chunk or math error

                    elif event_type == "telemetry":
                        _log.debug("Nomad Bridge: Telemetry pulse")
                        # Update vessel metadata and context (S.1.1 / HAL v8)
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
                        self._is_vessel_healthy = True

                    elif event_type == "pong":
                        # Measure round-trip time (S.1.1)
                        sent_at = payload.get("timestamp", 0)
                        if sent_at > 0:
                            latency = (time.perf_counter() - sent_at) * 1000
                            if math.isfinite(latency):
                                self.vessel_metadata["latency_ms"] = int(latency)
                                _log.debug("Nomad Bridge: Pong received. Latency: %d ms", latency)

                    elif event_type in ("rtc_offer", "rtc_answer", "rtc_ice"):
                        # WebRTC Signaling Relay (S.1.1)
                        _log.info("Nomad Bridge: WebRTC signaling event: %s", event_type)
                        self.broadcast_to_dashboards({
                            "type": "rtc_signal",
                            "event": event_type,
                            "payload": payload
                        })

                except Exception as inner_e:
                    # Catch inner loop errors so the websocket connection doesn't drop due to one bad frame
                    _log.error("Nomad Bridge inner loop error: %s", inner_e)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error("Nomad Bridge read error: %s", e)

    async def _send_loop(self, ws: WebSocket) -> None:
        try:
            while True:
                try:
                    # Wait for real feedback or timeout after 10s to send a keep-alive ping
                    payload = await asyncio.wait_for(self.charm_feedback_queue.get(), timeout=10.0)
                    await ws.send_json({
                        "type": "charm_feedback",
                        "payload": payload,
                    })
                except asyncio.TimeoutError:
                    # Phase 12.2: Hardening - Send keep-alive ping and measure latency
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
    import time
    if time.time() - bridge._last_sensor_update > 5.0:
        bridge._is_vessel_healthy = False
        return False
    return bridge._is_vessel_healthy
