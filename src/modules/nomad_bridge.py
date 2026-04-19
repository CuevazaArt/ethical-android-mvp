import asyncio
import base64
import json
import logging
import time
from typing import Any, Union

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

        self.app: Any = None

        if not _FASTAPI_AVAILABLE or FastAPI is None:
            _log.warning(
                "Nomad Bridge: FastAPI not installed; queues work but HTTP/WebSocket app is disabled. "
                "Install with: pip install -e \".[runtime]\""
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
            _log.info("Nomad Bridge: Nomad Vessel disconnected.")

    def broadcast_to_dashboards(self, msg: dict[str, Any]) -> None:
        """Push a message to all connected L0 dashboards."""
        for q in self.dashboard_queues:
            if not q.full():
                q.put_nowait(msg)

    async def _recv_loop(self, ws: Any) -> None:
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
                    frame_count += 1
                    b64_img = payload.get("image_b64", "")
                    
                    if frame_count % 10 == 0:
                        _log.info("Nomad Bridge: Received 10 vision frames (Stream Active)")
                        
                    self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                    
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    
                    # Phase 14: Pass meta signals into the queue alongside raw bytes
                    # Combined payload for the VisionContinuousDaemon
                    combined_payload = {
                        "raw_bytes": base64.b64decode(b64_img),
                        "meta": payload.get("meta", {}), # Contains lip_movement, human_presence
                        "detections": payload.get("detections", [])
                    }
                    self.vision_queue.put_nowait(combined_payload)
                    self._last_sensor_update = time.time()
                    self._is_vessel_healthy = True

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                        self._bump_eviction("audio")
                    b64_pcm = payload.get("audio_b64", "")
                    pcm_bytes = base64.b64decode(b64_pcm)
                    self.audio_queue.put_nowait(pcm_bytes)
                    
                    # Calculate very basic rms for dashboard audio bar and Thalamus
                    if pcm_bytes and len(pcm_bytes) >= 2:
                        import struct
                        import math
                        shorts = struct.unpack(f"<{len(pcm_bytes)//2}h", pcm_bytes[:(len(pcm_bytes)//2)*2])
                        rms = math.sqrt(sum(s*s for s in shorts) / len(shorts)) / 32768.0
                        self.last_rms = rms
                        if self.dashboard_queues:
                            self.broadcast_to_dashboards({"type": "audio_energy", "payload": {"rms": rms}})

                elif event_type == "telemetry":
                    _log.debug("Nomad Bridge: Telemetry pulse")
                    self.broadcast_to_dashboards({"type": "telemetry", "payload": payload})
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    self.telemetry_queue.put_nowait(payload)
                    self._last_sensor_update = time.time()
                    self._is_vessel_healthy = True

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

def is_vessel_online() -> bool:
    """Returns True if a Nomad Vessel sent data in the last 5 seconds."""
    bridge = get_nomad_bridge()
    import time
    if time.time() - bridge._last_sensor_update > 5.0:
        bridge._is_vessel_healthy = False
        return False
    return bridge._is_vessel_healthy
