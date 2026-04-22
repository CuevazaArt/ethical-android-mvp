"""
Nomad + Thalamus field path (tri-lobe kernel): real ``ThalamusLobe`` APIs — no legacy ring buffer.

Replaces v12-only mocks against ``audio_ring_buffer`` (removed in EthosKernel V13).
"""

from __future__ import annotations

from src.kernel import EthicalKernel
from src.modules.perception.nomad_bridge import get_nomad_bridge
from src.modules.perception.sensor_contracts import SensorSnapshot


def test_fuse_sensory_stream_none_is_safe() -> None:
    """Guard path: fusion may run before any snapshot exists (B.5 hardening)."""
    kernel = EthicalKernel(mode="office_2")
    out = kernel.thalamus.fuse_sensory_stream(None)
    assert isinstance(out, dict)
    assert "sensory_tension" in out
    assert "attention_locus" in out


def test_nomad_multimodal_bridge_and_thalamus_fusion() -> None:
    kernel = EthicalKernel(mode="office_2")
    bridge = get_nomad_bridge()

    for beta in (30.0, 90.0, 30.0):
        kernel.thalamus.ingest_telemetry(
            {"orientation": {"beta": beta, "gamma": 0.0, "alpha": 0.0}}
        )

    summary = kernel.thalamus.get_sensory_summary()
    assert "posture" in summary
    assert summary["posture"] in ("engaged", "speaking", "idle")

    pcm = b"\x01\x02" * 800
    if not bridge.audio_queue.full():
        bridge.audio_queue.put_nowait(pcm)
    assert bridge.audio_queue.qsize() >= 1

    if not bridge.vision_queue.full():
        bridge.vision_queue.put_nowait(b"\xff\xd8" + b"\x00" * 8)
    assert bridge.vision_queue.qsize() >= 1

    snapshot = SensorSnapshot(
        battery_level=0.8,
        ambient_noise=0.1,
        rms_audio=0.4,
        image_metadata={"lip_movement": 0.4, "human_presence": 0.6},
    )
    fusion = kernel.thalamus.fuse_sensory_stream(snapshot)
    assert fusion
    assert "attention_locus" in fusion
    assert "sensory_tension" in fusion
