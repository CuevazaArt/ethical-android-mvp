"""Nomad vision pipeline (Module S.1 — consumer env gate)."""

import pytest

from src.modules.sensor_contracts import SensorSnapshot, merge_nomad_vision_into_snapshot
from src.modules.vision_adapter import VisionInference


def test_start_nomad_vision_consumer_respects_env_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without KERNEL_NOMAD_VISION_CONSUMER, no background consumer is registered."""
    import src.modules.vision_adapter as vision_adapter

    monkeypatch.delenv("KERNEL_NOMAD_VISION_CONSUMER", raising=False)
    vision_adapter._nomad_vision_consumer = None
    assert vision_adapter.start_nomad_vision_consumer_from_env() is None


def test_merge_nomad_vision_into_snapshot_noop_without_consumer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_NOMAD_VISION_CONSUMER", "1")
    import src.modules.vision_adapter as vision_adapter

    vision_adapter._nomad_vision_consumer = None
    assert merge_nomad_vision_into_snapshot(None) is None


def test_merge_nomad_vision_into_snapshot_fuses_latest_inference(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_NOMAD_VISION_CONSUMER", "1")
    import src.modules.vision_adapter as vision_adapter

    class _Stub:
        latest_inference = VisionInference(
            primary_label="ambulance",
            confidence=0.92,
            detected_objects=["ambulance"],
            raw_scores={"ambulance": 0.92},
        )

    vision_adapter._nomad_vision_consumer = _Stub()

    snap = merge_nomad_vision_into_snapshot(None)
    assert snap is not None
    assert snap.image_metadata is not None
    assert snap.image_metadata.get("nomad", {}).get("primary_label") == "ambulance"
    assert snap.vision_emergency is not None and snap.vision_emergency > 0.4

    snap2 = merge_nomad_vision_into_snapshot(
        SensorSnapshot(vision_emergency=0.1, battery_level=0.5)
    )
    assert snap2.battery_level == 0.5
    assert snap2.vision_emergency is not None and snap2.vision_emergency >= snap.vision_emergency
