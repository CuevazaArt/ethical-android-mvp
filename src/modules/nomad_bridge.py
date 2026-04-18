import asyncio
import base64
import json
import logging
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


class NomadBridge:
    """
    Nomad LAN bridge for smartphone peripherals (Module S).

    Async WebSocket listener for real-world sensor data (vision frames, audio, telemetry).
    Requires optional dependency ``fastapi`` (``pip install -e ".[runtime]"``) for ``app``.
    """

    def __init__(self) -> None:
        self.vision_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=5)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=30)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        
        # Phase 10: L0 Dashboard Telemetry Broadcaster
        self.dashboard_queues: list[asyncio.Queue[dict[str, Any]]] = []

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
        await websocket.accept()
        _log.info("Nomad Bridge: Handshake successful. Nomad Smartphone is connected.")

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
            _log.info("Nomad Bridge: Nomad Smartphone disconnected.")

    def broadcast_to_dashboards(self, msg: dict[str, Any]) -> None:
        """Push a message to all connected L0 dashboards."""
        for q in self.dashboard_queues:
            if not q.full():
                q.put_nowait(msg)

    async def _recv_loop(self, ws: Any) -> None:
        frame_count = 0
        try:
            while True:
                data = await ws.receive_json()
                event_type = data.get("type")
                payload = data.get("payload")

                if not event_type or not payload:
                    continue

                if event_type == "vision_frame":
                    frame_count += 1
                    b64_img = payload.get("image_b64", "")
                    
                    if frame_count % 10 == 0:
                        _log.info("Nomad Bridge: Received 10 vision frames (Stream Active)")
                        
                    self.broadcast_to_dashboards({"type": "frame", "payload": payload})
                    
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    self.vision_queue.put_nowait(base64.b64decode(b64_img))

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                    b64_pcm = payload.get("audio_b64", "")
                    pcm_bytes = base64.b64decode(b64_pcm)
                    self.audio_queue.put_nowait(pcm_bytes)
                    
                    # Calculate very basic rms for dashboard audio bar
                    if pcm_bytes and len(pcm_bytes) >= 2 and self.dashboard_queues:
                        import struct
                        import math
                        shorts = struct.unpack(f"<{len(pcm_bytes)//2}h", pcm_bytes[:(len(pcm_bytes)//2)*2])
                        rms = math.sqrt(sum(s*s for s in shorts) / len(shorts)) / 32768.0
                        self.broadcast_to_dashboards({"type": "audio_energy", "payload": {"rms": rms}})

                elif event_type == "telemetry":
                    _log.debug("Nomad Bridge: Telemetry pulse")
                    self.broadcast_to_dashboards({"type": "telemetry", "payload": payload})
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    self.telemetry_queue.put_nowait(payload)

        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error("Nomad Bridge read error: %s", e)

    async def _send_loop(self, ws: Any) -> None:
        try:
            while True:
                charm_vector = await self.charm_feedback_queue.get()
                await ws.send_json(
                    {
                        "type": "charm_feedback",
                        "payload": charm_vector,
                    }
                )
        except asyncio.CancelledError:
            pass
        except Exception as e:
            _log.error("Nomad Bridge send error: %s", e)


_NOMAD_BRIDGE = NomadBridge()


def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE
