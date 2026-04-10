"""Tests for situated sensor contracts (v8) — no hardware required."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import (
    DigitalActionIntent,
    SensorSnapshot,
    merge_sensor_hints_into_signals,
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
        }
    )
    assert s.battery_level == 1.0
    assert s.place_trust == 0.0
    assert s.backup_just_completed is True


def test_digital_action_intent_dataclass():
    d = DigitalActionIntent(action_id="pay", summary="transfer", requires_owner_approval=True)
    assert d.action_id == "pay"
