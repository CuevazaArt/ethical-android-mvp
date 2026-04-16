"""Epistemic dissonance (v9.1) — sensor consensus telemetry."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.epistemic_dissonance import (
    EpistemicDissonanceAssessment,
    assess_epistemic_dissonance,
)
from src.modules.multimodal_trust import MultimodalAssessment, evaluate_multimodal_trust
from src.modules.sensor_contracts import SensorSnapshot


def test_no_snapshot_inactive():
    assert assess_epistemic_dissonance(None, None) == EpistemicDissonanceAssessment(
        False, 0.0, "no_sensor_data", ""
    )


def test_empty_snapshot_inactive():
    assert assess_epistemic_dissonance(SensorSnapshot(), None).reason == "no_sensor_data"


def test_audio_weak_inactive():
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.2, "accelerometer_jerk": 0.05, "vision_emergency": 0.1}
    )
    r = assess_epistemic_dissonance(s, None)
    assert r.active is False
    assert r.reason == "no_strong_audio_claim"


def test_motion_high_inactive():
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.8, "vision_emergency": 0.1}
    )
    r = assess_epistemic_dissonance(s, None)
    assert r.active is False
    assert r.reason == "motion_consistent_with_alarm"


def test_vision_supports_inactive():
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.05, "vision_emergency": 0.55}
    )
    r = assess_epistemic_dissonance(s, None)
    assert r.active is False
    assert r.reason == "vision_supports_emergency"


def test_dissonance_active():
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.05, "vision_emergency": 0.1}
    )
    r = assess_epistemic_dissonance(s, None)
    assert r.active is True
    assert r.reason == "audio_high_motion_low_vision_weak"
    assert 0.0 < r.score <= 1.0
    assert r.communication_hint
    d = r.to_public_dict()
    assert d["active"] is True
    assert "score" in d


def test_multimodal_aligned_skips():
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.05, "vision_emergency": 0.1}
    )
    mm = MultimodalAssessment("aligned", "cross_modal_support", False)
    r = assess_epistemic_dissonance(s, mm)
    assert r.active is False
    assert r.reason == "multimodal_aligned"


def test_monkeypatch_thresholds(monkeypatch):
    monkeypatch.setenv("KERNEL_EPISTEMIC_AUDIO_MIN", "0.99")
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.05, "vision_emergency": 0.1}
    )
    r = assess_epistemic_dissonance(s, None)
    assert r.active is False


def test_evaluate_multimodal_doubt_coexists():
    """Dissonance and multimodal doubt are independent telemetry layers."""
    s = SensorSnapshot.from_dict(
        {"audio_emergency": 0.9, "accelerometer_jerk": 0.05, "vision_emergency": 0.1}
    )
    mm = evaluate_multimodal_trust(s)
    ed = assess_epistemic_dissonance(s, mm)
    assert mm.state == "doubt"
    assert ed.active is True
