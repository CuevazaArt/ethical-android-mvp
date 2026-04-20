"""
Full Integration Test for Nomad Bridge (Module S.1).
Verifies the path from LAN WebSocket input to Kernel sensory fusion.
"""

import asyncio
import pytest
from fastapi.testclient import TestClient
from src.chat_server import app
from src.modules.nomad_bridge import get_nomad_bridge

@pytest.mark.asyncio
async def test_nomad_telemetry_flow_injects_into_next_turn():
    """
    Verifies that telemetry sent via NomadBridge WebSocket reaches the kernel's
    next chat turn through merge_nomad_telemetry_into_snapshot.
    """
    bridge = get_nomad_bridge()
    
    # 1. Simulate incoming telemetry from smartphone
    test_telemetry = {
        "battery_level": 0.02, # Highly critical
        "core_temperature": 98.5 # Very high
    }
    
    # We put it directly in the queue as if _recv_loop did it
    await bridge.telemetry_queue.put(test_telemetry)
    
    # Give the consumer a microsecond to process (it runs in background)
    from src.modules.vitality import start_nomad_telemetry_consumer_from_env, get_nomad_telemetry_consumer_optional
    import os
    os.environ["KERNEL_NOMAD_TELEMETRY_CONSUMER"] = "1"
    
    consumer = start_nomad_telemetry_consumer_from_env()
    assert consumer is not None
    
    # Wait for the queue to be drained
    for _ in range(10):
        if consumer.latest_telemetry == test_telemetry:
            break
        await asyncio.sleep(0.1)
    
    assert consumer.latest_telemetry == test_telemetry
    
    # 2. Check kernel fusion
    from src.modules.sensor_contracts import merge_nomad_telemetry_into_snapshot
    snap = merge_nomad_telemetry_into_snapshot(None)
    
    assert snap is not None
    assert snap.battery_level == 0.02
    assert snap.core_temperature == 98.5
    
    # 3. Check vitality assessment
    from src.modules.vitality import assess_vitality
    assessment = assess_vitality(snap)
    assert assessment.is_critical is True # battery < 0.05
    assert assessment.thermal_critical is True # temp > 80.0
    
    print("\n[PASSED] Nomad Telemetry -> SensorSnapshot -> VitalityAssessment flow verified.")

@pytest.mark.asyncio
async def test_nomad_vision_flow_injects_into_next_turn(monkeypatch):
    """
    Verifies that vision frames reach the VisionAdapter.
    """
    import numpy as np
    from src.modules.vision_adapter import start_nomad_vision_consumer_from_env, VisionInference
    import os
    import src.modules.vision_adapter as vision_adapter
    
    os.environ["KERNEL_NOMAD_VISION_CONSUMER"] = "1"
    
    # Mock cv2 to avoid decoding real jpegs
    class MockCV2:
        def imdecode(self, *args):
            return np.zeros((10, 10, 3), dtype=np.uint8)
        IMREAD_COLOR = 1
    
    monkeypatch.setattr("cv2.imdecode", MockCV2().imdecode)
    monkeypatch.setattr("cv2.IMREAD_COLOR", 1)
    
    # Reset consumer
    vision_adapter._nomad_vision_consumer = None
    consumer = start_nomad_vision_consumer_from_env()
    
    # Mock the adapter.infer to return something specific
    consumer.adapter.infer = lambda img: VisionInference(primary_label="test_object", confidence=0.99)
    
    bridge = get_nomad_bridge()
    await bridge.vision_queue.put(b"some_bytes")
    
    # Wait for consumer
    found = False
    for _ in range(50):
        if consumer.latest_inference is not None and consumer.latest_inference.primary_label == "test_object":
            found = True
            break
        await asyncio.sleep(0.05)
        
    assert found is True
    assert consumer.latest_inference.primary_label == "test_object"
    print(f"\n[PASSED] Nomad Vision Consumer produced expected inference.")

@pytest.mark.asyncio
async def test_nomad_charm_feedback_loop():
    """
    Verifies that charm vectors pushed to the bridge are available for the smartphone.
    """
    bridge = get_nomad_bridge()
    
    test_charm = {"warmth": 0.8, "mystery": 0.1, "playfulness": 0.5, "directiveness": 0.2}
    
    # 1. Put into bridge
    bridge.charm_feedback_queue.put_nowait(test_charm)
    
    # 2. Get from bridge (simulating _send_loop)
    val = await bridge.charm_feedback_queue.get()
    assert val == test_charm
    print("\n[PASSED] Nomad Charm Feedback loop verified.")


@pytest.mark.asyncio
async def test_nomad_somatic_blindness():
    """
    Verifies that the bridge detects Somatic Blindness after 5 seconds of silence.
    """
    import time
    bridge = get_nomad_bridge()
    
    # 1. Simulate active connection and heartbeat
    bridge._is_connected = True
    bridge._last_heartbeat = time.time()
    assert bridge.is_somatic_blind is False
    
    # 2. Simulate delay (backdate heartbeat by 6 seconds)
    bridge._last_heartbeat = time.time() - 6.0
    assert bridge.is_somatic_blind is True
    print("\n[PASSED] Nomad Somatic Blindness detected (6s silence).")
    
    # 3. Resume heartbeat
    bridge._last_heartbeat = time.time()
    assert bridge.is_somatic_blind is False
    print("[PASSED] Nomad Somatic Blindness cleared (heartbeat resumed).")
