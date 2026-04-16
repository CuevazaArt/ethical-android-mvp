"""Cross-modal antispoof (v8) — no hardware required."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.multimodal_trust import (
    MultimodalThresholds,
    evaluate_multimodal_trust,
    owner_anchor_hint,
    suppress_stress_from_spoof_risk,
    thresholds_from_env,
)
from src.modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals


def test_no_claim_without_audio_emergency():
    s = SensorSnapshot(battery_level=0.5, vision_emergency=0.9)
    a = evaluate_multimodal_trust(s)
    assert a.state == "no_claim"


def test_aligned_audio_plus_vision():
    s = SensorSnapshot(audio_emergency=0.9, vision_emergency=0.9)
    a = evaluate_multimodal_trust(s)
    assert a.state == "aligned"
    assert not suppress_stress_from_spoof_risk(a)


def test_doubt_audio_only():
    s = SensorSnapshot(audio_emergency=0.9)
    a = evaluate_multimodal_trust(s)
    assert a.state == "doubt"
    assert a.requires_owner_anchor
    assert suppress_stress_from_spoof_risk(a)


def test_doubt_cross_modal_conflict():
    s = SensorSnapshot(audio_emergency=0.9, vision_emergency=0.1, scene_coherence=0.2)
    a = evaluate_multimodal_trust(s)
    assert a.state == "doubt"
    assert a.reason == "cross_modal_conflict"


def test_merge_suppresses_ambient_noise_when_doubt():
    base = {
        "risk": 0.5,
        "urgency": 0.5,
        "hostility": 0.0,
        "calm": 0.6,
        "vulnerability": 0.0,
    }
    snap = SensorSnapshot(
        audio_emergency=0.9,
        ambient_noise=0.95,
        biometric_anomaly=0.8,
    )
    doubt = evaluate_multimodal_trust(snap)
    assert doubt.state == "doubt"
    out = merge_sensor_hints_into_signals(base, snap, doubt)
    # Without suppression, ambient_noise would lower calm; doubt suppresses that path
    assert out["calm"] == base["calm"]


def test_merge_allows_ambient_when_aligned():
    base = {
        "risk": 0.5,
        "urgency": 0.5,
        "hostility": 0.0,
        "calm": 0.6,
        "vulnerability": 0.0,
    }
    snap = SensorSnapshot(
        audio_emergency=0.9,
        vision_emergency=0.9,
        ambient_noise=0.95,
    )
    aligned = evaluate_multimodal_trust(snap)
    assert aligned.state == "aligned"
    out = merge_sensor_hints_into_signals(base, snap, aligned)
    assert out["calm"] < base["calm"]


def test_owner_anchor_hint_nonempty_on_doubt():
    s = SensorSnapshot(audio_emergency=0.9)
    a = evaluate_multimodal_trust(s)
    assert a.state == "doubt"
    h = owner_anchor_hint(a)
    assert "owner" in h.lower() or "trusted" in h.lower()


def test_explicit_thresholds_align_without_env():
    s = SensorSnapshot(audio_emergency=0.5, vision_emergency=0.5)
    t = MultimodalThresholds(audio_strong=0.4, vision_support=0.45)
    a = evaluate_multimodal_trust(s, t)
    assert a.state == "aligned"


def test_env_audio_strong_raises_bar(monkeypatch):
    monkeypatch.setenv("KERNEL_MULTIMODAL_AUDIO_STRONG", "0.99")
    s = SensorSnapshot(audio_emergency=0.9)
    a = evaluate_multimodal_trust(s)
    assert a.state == "no_claim"


def test_env_invalid_float_uses_default(monkeypatch):
    monkeypatch.setenv("KERNEL_MULTIMODAL_AUDIO_STRONG", "not_a_number")
    assert thresholds_from_env().audio_strong == 0.65


def test_thresholds_from_env_parses_floats(monkeypatch):
    monkeypatch.setenv("KERNEL_MULTIMODAL_AUDIO_STRONG", "0.5")
    monkeypatch.setenv("KERNEL_MULTIMODAL_VISION_SUPPORT", "0.3")
    t = thresholds_from_env()
    assert t.audio_strong == 0.5
    assert t.vision_support == 0.3
