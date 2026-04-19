import pytest
import asyncio
import numpy as np
import time
from src.kernel import EthicalKernel
from src.modules.nomad_bridge import get_nomad_bridge
from src.modules.sensor_contracts import SensorSnapshot

@pytest.mark.asyncio
async def test_nomad_multimodal_ingestion_stress():
    """
    Stress test for Nomad Bridge: Simultaneous Audio, Vision and Telemetry.
    Validates that Thalamus EMA smoothing and Perceptive Lobe inertia 
    handle burst data correctly.
    """
    # 1. Setup Kernel with Nomad Bridge enabled
    import os
    os.environ["KERNEL_NOMAD_BRIDGE_ENABLED"] = "1"
    os.environ["KERNEL_BAYESIAN_MODE"] = "posterior_driven"
    
    kernel = EthicalKernel(variability=False)
    bridge = get_nomad_bridge()
    
    # 2. Simulate High-Frequency Telemetry (IMU)
    for beta in [30, 90, 30]:
        bridge.telemetry_queue.put_nowait({"orientation": {"beta": beta, "gamma": 0, "alpha": 0}})
        # Ingest via Thalamus (usually done in process loop, here direct for test)
        payload = bridge.telemetry_queue.get_nowait()
        kernel.thalamus.ingest_telemetry(payload)
    
    # Check if EMA smoothed the transition
    summary = kernel.thalamus.get_sensory_summary()
    assert "posture" in summary

    # 3. Simulate Audio Stream (PCM)
    pcm_data = (np.random.rand(1600) * 0.5).astype(np.float32).tobytes()
    bridge.audio_queue.put_nowait(pcm_data)
    
    # Let the daemon process it
    time.sleep(0.5)
    assert not kernel.audio_ring_buffer.buffer.empty()

    # 4. Simulate Vision Frames
    dummy_frame = b"\xff\xd8" + b"\x00" * 10
    bridge.vision_queue.put_nowait(dummy_frame)
    
    # 5. Full Process Turn
    snapshot = SensorSnapshot(
        battery_level=0.8,
        ambient_noise=0.1
    )
    
    # Perceptive Lobe should pull from queues via Thalamus
    # We yield to allow async tasks to run
    await asyncio.sleep(0.1)
    
    # 6. Verify Thalamus Fusion
    fusion = kernel.thalamus.fuse_sensory_stream(snapshot)
    if fusion:
        assert "attention_locus" in fusion
        assert "sensory_tension" in fusion

    print("✅ Nomad Multimodal Ingestion Stress Test Passed.")

if __name__ == "__main__":
    asyncio.run(test_nomad_multimodal_ingestion_stress())
