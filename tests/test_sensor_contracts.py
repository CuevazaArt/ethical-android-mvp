"""Tests for situated sensor contracts (v8) — no hardware required."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.multimodal_trust import MultimodalAssessment
from src.modules.perceptual_abstraction import snapshot_from_layers
from src.modules.sensor_contracts import (
    DigitalActionIntent,
    SensorPayloadValidationError,
    SensorSnapshot,
    merge_sensor_hints_into_signals,
    validate_sensor_dict_strict,
)


def test_merge_none_returns_same_dict():
    base = {"risk": 0.5, "urgency": 0.5, "hostility": 0.0, "calm": 0.5, "vulnerability": 0.0}
    out = merge_sensor_hints_into_signals(base, None)
    assert out is base


def test_merge_empty_snapshot_returns_same_dict():
    base = {"risk": 0.5, "urgency": 0.5, "hostility": 0.0, "calm": 0.5, "vulnerability": 0.0}
    snap = SensorSnapshot()
    out = merge_sensor_hints_into_signals(base, snap)
    assert out is base


def test_merge_suppresses_audio_stress_nudges_when_multimodal_doubt():
    """SP-P1-02 — doubt skips audio-like stress paths in merge (antispoof)."""
    base = {
        "risk": 0.5,
        "urgency": 0.5,
        "hostility": 0.0,
        "calm": 0.5,
        "vulnerability": 0.0,
    }
    snap = SensorSnapshot(
        audio_emergency=0.95,
        vision_emergency=0.05,
        scene_coherence=0.05,
    )
    without_mm = merge_sensor_hints_into_signals(base, snap, None)
    doubt = MultimodalAssessment("doubt", "cross_modal_conflict", True)
    with_doubt = merge_sensor_hints_into_signals(base, snap, doubt)
    assert with_doubt["urgency"] <= without_mm["urgency"]


def test_low_battery_nudges_urgency():
    base = {
        "risk": 0.5,
        "urgency": 0.4,
        "hostility": 0.0,
        "calm": 0.6,
        "vulnerability": 0.0,
    }
    snap = SensorSnapshot(battery_level=0.03)
    out = merge_sensor_hints_into_signals(base, snap)
    assert out["urgency"] > base["urgency"]
    assert out["calm"] < base["calm"]


def test_from_dict_ignores_unknown_and_clamps():
    s = SensorSnapshot.from_dict(
        {
            "battery_level": 1.5,
            "place_trust": -0.1,
            "unknown_key": 99,
            "backup_just_completed": True,
            "audio_emergency": 0.8,
            "vision_emergency": 0.3,
            "scene_coherence": 0.5,
        }
    )
    assert s.battery_level == 1.0
    assert s.place_trust == 0.0
    assert s.backup_just_completed is True
    assert s.audio_emergency == 0.8
    assert s.scene_coherence == 0.5


def test_digital_action_intent_dataclass():
    d = DigitalActionIntent(action_id="pay", summary="transfer", requires_owner_approval=True)
    assert d.action_id == "pay"


def test_strict_mode_rejects_unknown_sensor_key():
    with pytest.raises(SensorPayloadValidationError, match="unknown sensor keys"):
        SensorSnapshot.from_dict({"not_a_real_sensor_field": 1.0}, strict=True)


def test_strict_mode_rejects_non_numeric_scalar():
    with pytest.raises(SensorPayloadValidationError, match="battery_level"):
        SensorSnapshot.from_dict({"battery_level": "high"}, strict=True)


def test_strict_mode_rejects_bool_for_float_slot():
    with pytest.raises(SensorPayloadValidationError, match="boolean"):
        SensorSnapshot.from_dict({"battery_level": True}, strict=True)


def test_validate_sensor_dict_strict_rejects_nan():
    with pytest.raises(SensorPayloadValidationError, match="nan"):
        validate_sensor_dict_strict({"battery_level": float("nan")})


def test_snapshot_from_layers_respects_kernel_sensor_input_strict_env(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_SENSOR_INPUT_STRICT", "1")
    with pytest.raises(SensorPayloadValidationError):
        snapshot_from_layers(client_dict={"typo": 0.5})


def test_strict_mode_accepts_known_keys():
    s = SensorSnapshot.from_dict({"battery_level": 0.42, "place_trust": 0.9}, strict=True)
    assert abs(s.battery_level - 0.42) < 1e-9
    assert abs(s.place_trust - 0.9) < 1e-9
