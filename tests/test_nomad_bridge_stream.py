import asyncio
import base64

import pytest
from fastapi.testclient import TestClient
import numpy as np

from src.modules import nomad_bridge as nomad_bridge_mod
from src.modules.nomad_bridge import NomadBridge, get_nomad_bridge
from src.modules.sensor_contracts import SensorSnapshot
from src.modules.vitality import assess_vitality


@pytest.fixture
def nomad_client(monkeypatch):
    """
    Fresh :class:`NomadBridge` per test so asyncio queues bind to the TestClient loop.

    The module singleton is created at import time and can mismatch Starlette's event loop,
    which breaks ``_send_loop`` / ``_recv_loop`` and causes flaky queue reads.
    """
    bridge = NomadBridge()
    monkeypatch.setattr(nomad_bridge_mod, "_NOMAD_BRIDGE", bridge, raising=False)
    monkeypatch.setattr(nomad_bridge_mod, "get_nomad_bridge", lambda: bridge)
    with TestClient(bridge.app) as client:
        yield client
        
@pytest.mark.asyncio
async def test_peek_latest_telemetry_s2_1(nomad_client):
    """Module S.2.1 — mirror last telemetry for sync vitality merge."""
    bridge = get_nomad_bridge()
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json(
            {
                "type": "telemetry",
                "payload": {"battery_level": 0.71, "core_temperature": 36.5},
            }
        )
        await asyncio.sleep(0.15)
    peek = bridge.peek_latest_telemetry()
    assert peek is not None
    assert abs(float(peek["battery_level"]) - 0.71) < 1e-6
    assert float(peek["core_temperature"]) == 36.5


@pytest.mark.asyncio
async def test_nomad_bridge_websocket_handshake(nomad_client):
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        # Simulate smartphone sending telemetry
        payload = {
            "type": "telemetry",
            "payload": {
                "accelerometer_jerk": 0.9, # Extreme shock
                "core_temperature": 35.0,
                "battery_level": 0.8
            }
        }
        websocket.send_json(payload)
        
        # Test pulling from the queue within the bridge
        bridge = get_nomad_bridge()
        
        # Give event loop a tiny fraction to process the WS message
        await asyncio.sleep(0.1) 
        telemetry = bridge.telemetry_queue.get_nowait()
        assert telemetry is not None
        assert telemetry["accelerometer_jerk"] == 0.9

def test_vitality_impact_from_nomad_sensor():
    # Verify that the vitality component correctly penalizes high accelerometer jerk
    snap = SensorSnapshot(
        accelerometer_jerk=0.9,
        core_temperature=45.0,
        battery_level=0.9
    )
    vitality = assess_vitality(snap)
    
    assert vitality.is_impacted is True
    assert vitality.is_critical is True # Inherits from impacted
    
@pytest.mark.asyncio
async def test_nomad_audio_pcm_routing(nomad_client):
    dummy_pcm = np.zeros(1000, dtype=np.float32)
    b64_encoded = base64.b64encode(dummy_pcm.tobytes()).decode("utf-8")
    bridge = get_nomad_bridge()
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "audio_pcm", "payload": {"audio_b64": b64_encoded}})
        await asyncio.sleep(0.2)
        audio_bytes = bridge.audio_queue.get_nowait()
    assert len(audio_bytes) == len(dummy_pcm.tobytes())


@pytest.mark.asyncio
async def test_nomad_vision_frame_routing(nomad_client):
    """Frame bytes round-trip into vision_queue (S.1.1 → :class:`NomadVisionConsumer`)."""
    raw = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
        b"\xff\xdb\x00C\x00\xff\xd9"
    )
    b64_img = base64.b64encode(raw).decode("ascii")
    bridge = get_nomad_bridge()
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "vision_frame", "payload": {"image_b64": b64_img}})
        await asyncio.sleep(0.2)
        out = bridge.vision_queue.get_nowait()
    assert out == raw


def test_nomad_public_queue_stats_shape(nomad_client):
    stats = get_nomad_bridge().public_queue_stats()
    assert stats["schema"] == "nomad_bridge_queue_stats_v1"
    assert stats["vision_max"] == 5
    assert "vision_queued" in stats

def test_nomad_charm_feedback(nomad_client):
    bridge = get_nomad_bridge()
    bridge.charm_feedback_queue.put_nowait({
        "intimacy": 0.5,
        "warmth": 0.8,
        "playfulness": 0.2,
        "tension": 0.0
    })
    
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        response = websocket.receive_json()
        assert response["type"] == "charm_feedback"
        assert response["payload"]["warmth"] == 0.8
