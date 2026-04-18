import asyncio
import base64
import json
import logging
import time
import hmac
import hashlib
import os
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, status

from ..observability.metrics import record_nomad_bridge_connection

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
        # Phase 9: Tightened queues for real-time priority
        self.vision_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=1) # Only the freshest frame
        self.audio_queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=10) # 10 chunks ~ 1s
        self.telemetry_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=5)
        self.charm_feedback_queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=10)
        
        self.app = FastAPI(title="Nomad Bridge Sensor Endpoint")
        self._is_connected = False
        self._last_heartbeat = 0.0
        
        @self.app.websocket("/ws/nomad")
        async def websocket_nomad_endpoint(
            websocket: WebSocket,
            timestamp: str | None = Query(None),
            signature: str | None = Query(None)
        ):
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

            await websocket.accept()
            self._is_connected = True
            self._last_heartbeat = time.time()
            record_nomad_bridge_connection("success")
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
                    # Block S.2.2: Intelligent Discard. 
                    # If vision consumer is slow, we drop the incoming frame immediately.
                    # We only keep 1 frame in queue to ensure zero-latency relevance.
                    while self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    b64_img = payload.get("image_b64", "")
                    try:
                        self.vision_queue.put_nowait(base64.b64decode(b64_img))
                    except Exception:
                        pass
                        
                elif event_type == "audio_pcm":
                    # For audio, we allow a tiny buffer to avoid jitter, but still drop if too old.
                    if self.audio_queue.full():
                        # Drop 5 oldest chunks to clear space fast during burst
                        for _ in range(5):
                            try: self.audio_queue.get_nowait()
                            except asyncio.QueueEmpty: break
                    b64_pcm = payload.get("audio_b64", "")
                    try:
                        self.audio_queue.put_nowait(base64.b64decode(b64_pcm))
                    except Exception:
                        pass

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
