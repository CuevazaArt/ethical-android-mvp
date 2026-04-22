"""Module 9.1 — VisionContinuousDaemon and JPEG inference path."""

import queue
import time

import pytest


def _drain_threadsafe_vision() -> None:
    from src.modules.nomad_bridge import get_nomad_bridge

    q = get_nomad_bridge().vision_queue_threadsafe
    while True:
        try:
            q.get_nowait()
        except queue.Empty:
            break


def test_analyze_jpeg_bytes_stub_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_VISION_JPEG_STUB_LABEL", "rifle")
    from src.modules.vision_inference import VisionInferenceEngine

    eng = VisionInferenceEngine()
    dets = eng.analyze_jpeg_bytes(b"not-a-real-jpeg")
    assert len(dets) == 1
    assert dets[0].label == "rifle"
    assert dets[0].is_prohibited is True


def test_vision_continuous_daemon_emits_episode(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_VISION_JPEG_STUB_LABEL", "knife")
    from src.modules.nomad_bridge import get_nomad_bridge
    from src.modules.vision_inference import VisionContinuousDaemon, VisionInferenceEngine

    _drain_threadsafe_vision()
    absorbed: list = []

    def cb(ep) -> None:
        absorbed.append(ep)

    eng = VisionInferenceEngine()
    d = VisionContinuousDaemon(eng, cb)
    d.polling_rate = 0.02
    get_nomad_bridge().vision_queue_threadsafe.put(b"\xff\xd8")
    d.start()
    time.sleep(0.35)
    d.stop()
    assert any("knife" in e.vision_entities for e in absorbed)


def test_public_queue_stats_includes_vision_sync_queued() -> None:
    from src.modules.nomad_bridge import get_nomad_bridge

    stats = get_nomad_bridge().public_queue_stats()
    assert stats.get("schema") == "nomad_bridge_queue_stats_v4"
    assert "vision_sync_queued" in stats


def test_vision_continuous_daemon_env_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.kernel_lobes import perception_lobe as pl

    monkeypatch.setenv("KERNEL_VISION_CONTINUOUS_DAEMON", "0")
    assert pl._vision_continuous_daemon_enabled() is False
    monkeypatch.setenv("KERNEL_VISION_CONTINUOUS_DAEMON", "1")
    assert pl._vision_continuous_daemon_enabled() is True
