import asyncio
import base64
import json

import numpy as np
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient

from src.modules.nomad_bridge import get_nomad_bridge
from src.modules.sensor_contracts import SensorSnapshot
from src.modules.vitality import assess_vitality

@pytest.fixture
def nomad_client():
    bridge = get_nomad_bridge()
    with TestClient(bridge.app) as client:
        yield client
        
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
    
def test_nomad_audio_pcm_routing(nomad_client):
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        # Create dummy float32 buffer simulating 1_000 samples
        dummy_pcm = np.zeros(1000, dtype=np.float32)
        b64_encoded = base64.b64encode(dummy_pcm.tobytes()).decode('utf-8')
        
        payload = {
            "type": "audio_pcm",
            "payload": {
                "audio_b64": b64_encoded
            }
        }
        websocket.send_json(payload)

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
