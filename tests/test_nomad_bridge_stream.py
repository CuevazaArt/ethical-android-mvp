import asyncio
import base64
import json

import numpy as np
import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient
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
    assert stats["schema"] == "nomad_bridge_queue_stats_v3"
    assert stats["vision_max"] == 5
    assert "vision_queued" in stats
    assert stats["latest_telemetry_present"] is False
    assert stats["latest_telemetry_keys"] == []
    lim = stats["limits"]
    assert lim["max_vision_frame_bytes"] > 0
    assert lim["max_audio_pcm_bytes"] > 0
    assert lim["max_telemetry_keys"] > 0
    assert lim["max_ws_message_bytes"] == 4 * 1024 * 1024
    rej = stats["rejections"]
    assert rej["ws_oversize"] == 0
    assert "queue_evictions" in stats
    assert stats["queue_evictions"]["vision"] == 0
    assert stats["charm_feedback_max"] == 10
    assert stats["charm_feedback_queued"] == 0
    assert stats["last_rms"] == 0.0
    assert stats["dashboard_subscribers"] == 0


@pytest.mark.asyncio
async def test_nomad_public_queue_stats_telemetry_keys(nomad_client):
    bridge = get_nomad_bridge()
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json(
            {
                "type": "telemetry",
                "payload": {"battery": 0.42, "core_temperature_c": 41.0, "noise": "x"},
            }
        )
        await asyncio.sleep(0.15)
    st = bridge.public_queue_stats()
    assert st["latest_telemetry_present"] is True
    assert set(st["latest_telemetry_keys"]) == {"battery", "core_temperature_c", "noise"}

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


@pytest.mark.asyncio
async def test_nomad_vision_skipped_when_decoded_exceeds_limit(monkeypatch, nomad_client):
    monkeypatch.setenv("KERNEL_NOMAD_MAX_VISION_FRAME_BYTES", "64")
    bridge = get_nomad_bridge()
    raw_big = b"z" * 200
    b64 = base64.b64encode(raw_big).decode("ascii")
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "vision_frame", "payload": {"image_b64": b64}})
        await asyncio.sleep(0.25)
    assert bridge.vision_queue.empty()


@pytest.mark.asyncio
async def test_nomad_audio_skipped_when_decoded_exceeds_limit(monkeypatch, nomad_client):
    monkeypatch.setenv("KERNEL_NOMAD_MAX_AUDIO_PCM_BYTES", "40")
    bridge = get_nomad_bridge()
    raw_big = np.zeros(500, dtype=np.float32)
    b64 = base64.b64encode(raw_big.tobytes()).decode("utf-8")
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "audio_pcm", "payload": {"audio_b64": b64}})
        await asyncio.sleep(0.25)
    assert bridge.audio_queue.empty()


@pytest.mark.asyncio
async def test_nomad_telemetry_rejected_over_key_limit(monkeypatch, nomad_client):
    monkeypatch.setenv("KERNEL_NOMAD_MAX_TELEMETRY_KEYS", "3")
    bridge = get_nomad_bridge()
    payload = {"a": 1, "b": 2, "c": 3, "d": 4}
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "telemetry", "payload": payload})
        await asyncio.sleep(0.2)
    assert bridge.peek_latest_telemetry() is None
    assert bridge.telemetry_queue.empty()


@pytest.mark.asyncio
async def test_nomad_telemetry_non_dict_ignored(nomad_client):
    bridge = get_nomad_bridge()
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_json({"type": "telemetry", "payload": [1, 2, 3]})
        await asyncio.sleep(0.15)
    assert bridge.peek_latest_telemetry() is None


@pytest.mark.asyncio
async def test_nomad_ws_rejects_oversized_text_frame(monkeypatch, nomad_client):
    """S.1 — skip parse when UTF-8 envelope exceeds KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES."""
    monkeypatch.setenv("KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES", "120")
    bridge = get_nomad_bridge()
    huge = json.dumps(
        {"type": "telemetry", "payload": {"x": "y" * 500}},
    )
    assert len(huge.encode("utf-8")) > 120
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_text(huge)
        await asyncio.sleep(0.2)
    assert bridge.telemetry_queue.empty()
    assert bridge.peek_latest_telemetry() is None
    assert bridge.public_queue_stats()["rejections"]["ws_oversize"] >= 1


@pytest.mark.asyncio
async def test_nomad_invalid_json_increments_counter(nomad_client):
    bridge = get_nomad_bridge()
    before = bridge.public_queue_stats()["rejections"]["invalid_json"]
    with nomad_client.websocket_connect("/ws/nomad") as websocket:
        websocket.send_text("not-json{")
        await asyncio.sleep(0.15)
    after = bridge.public_queue_stats()["rejections"]["invalid_json"]
    assert after > before
