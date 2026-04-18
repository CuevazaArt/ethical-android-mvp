import asyncio
import base64
import json
import logging
import time
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

_log = logging.getLogger(__name__)

class NomadBridge:
    """
    Nomad LAN Bridge Server for Smartphone (Módulo S).
    
    Establishes an asynchronous WebSocket listener for incoming real-world peripheral data:
    - vision: JPEG compressed frames
    - audio: PCM or Base64 audio blobs
    - telemetry: Accelerometer (XYZ), Battery Temp
    
    Acts as the conduit between the physical world and the Ethos Kernel sensory stack.
    """
    
    def __init__(self):
        # Queues to buffer sensor inputs, maxsize enforces throttling against memory OOM
        self.vision_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=5)
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=30)
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        
        self.app = FastAPI(title="Nomad Bridge Sensor Endpoint")
        self._is_connected = False
        self._last_heartbeat = 0.0
        
        @self.app.websocket("/ws/nomad")
        async def websocket_nomad_endpoint(websocket: WebSocket):
            await websocket.accept()
            self._is_connected = True
            self._last_heartbeat = time.time()
            _log.info("Nomad Bridge: Handshake successful. Nomad Smartphone is connected.")
            
            # Start full-duplex execution
            recv_task = asyncio.create_task(self._recv_loop(websocket))
            send_task = asyncio.create_task(self._send_loop(websocket))
            
            done, pending = await asyncio.wait(
                [recv_task, send_task], 
                return_when=asyncio.FIRST_COMPLETED
            )
            
            for task in pending:
                task.cancel()
            
            self._is_connected = False
            _log.info("Nomad Bridge: Nomad Smartphone disconnected.")

    @property
    def is_connected(self) -> bool:
        return self._is_connected

    @property
    def is_somatic_blind(self) -> bool:
        """
        Calculates if the kernel is currently 'somatically blind' (Module S.1.2).
        True if Nomad was active but heartbeat is older than 5 seconds.
        """
        if not self._is_connected:
            return False
        return (time.time() - self._last_heartbeat) > 5.0
    
    async def _recv_loop(self, ws: WebSocket):
        try:
            while True:
                data = await ws.receive_json()
                event_type = data.get("type")
                payload = data.get("payload")
                
                if not event_type or not payload:
                    if event_type == "heartbeat":
                        self._last_heartbeat = time.time()
                    continue
                    
                if event_type == "vision_frame":
                    # Drop older frames if buffer is full (Throttle Lock implemented as requested)
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    b64_img = payload.get("image_b64", "")
                    self.vision_queue.put_nowait(base64.b64decode(b64_img))
                        
                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                    b64_pcm = payload.get("audio_b64", "")
                    self.audio_queue.put_nowait(base64.b64decode(b64_pcm))

                elif event_type == "telemetry":
                    if self.telemetry_queue.full():
                        self.telemetry_queue.get_nowait()
                    self.telemetry_queue.put_nowait(payload)
                        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            _log.error(f"Nomad Bridge read error: {e}")

    async def _send_loop(self, ws: WebSocket):
        try:
            while True:
                # Acceptance of enriched feedback (Charm Vector + Gesture Plan)
                feedback = await self.charm_feedback_queue.get()
                await ws.send_json({
                    "type": "somatic_feedback",
                    "payload": feedback
                })
        except Exception as e:
            _log.error(f"Nomad Bridge send error: {e}")

# Global instance
_NOMAD_BRIDGE = NomadBridge()

def get_nomad_bridge() -> NomadBridge:
    return _NOMAD_BRIDGE
