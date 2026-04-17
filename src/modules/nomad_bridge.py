"""
LAN Nomad bridge (Module S / PLAN_WORK_DISTRIBUTION_TREE Bloque S.1).

WebSocket JSON events (client → server):

- ``type: vision_frame``, ``payload: { "image_b64": "<base64 JPEG>" }``
- ``type: audio_pcm``, ``payload: { "audio_b64": "<base64 raw PCM>" }``
- ``type`` = ``telemetry``, ``payload``: flat sensor dict (accelerometer, battery, temperature, …)

Server → client: ``type: charm_feedback``, ``payload``: charm vector dict (from kernel).

``NomadVisionConsumer`` in ``vision_adapter.py`` drains ``vision_queue``; audio adapter drains ``audio_queue``.
"""

import asyncio
import base64
import binascii
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

_log = logging.getLogger(__name__)


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

    def public_queue_stats(self) -> dict[str, Any]:
        """JSON-safe queue depths for operators (GET /metrics hooks, health dashboards)."""
        return {
            "schema": "nomad_bridge_queue_stats_v1",
            "vision_queued": self.vision_queue.qsize(),
            "vision_max": self.vision_queue.maxsize,
            "audio_queued": self.audio_queue.qsize(),
            "audio_max": self.audio_queue.maxsize,
            "telemetry_queued": self.telemetry_queue.qsize(),
            "telemetry_max": self.telemetry_queue.maxsize,
            "charm_feedback_queued": self.charm_feedback_queue.qsize(),
            "charm_feedback_max": self.charm_feedback_queue.maxsize,
        }

    async def _recv_loop(self, ws: WebSocket):
        try:
            while True:
                data = await ws.receive_json()
                event_type = data.get("type")
                payload = data.get("payload")
                
                if not event_type or not payload:
                    continue
                    
                if event_type == "vision_frame":
                    if self.vision_queue.full():
                        self.vision_queue.get_nowait()
                    b64_img = payload.get("image_b64", "")
                    try:
                        raw = base64.b64decode(b64_img, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if raw:
                        self.vision_queue.put_nowait(raw)

                elif event_type == "audio_pcm":
                    if self.audio_queue.full():
                        self.audio_queue.get_nowait()
                    b64_pcm = payload.get("audio_b64", "")
                    try:
                        raw_audio = base64.b64decode(b64_pcm, validate=False)
                    except (binascii.Error, ValueError):
                        continue
                    if raw_audio:
                        self.audio_queue.put_nowait(raw_audio)

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
