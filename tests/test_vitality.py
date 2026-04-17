"""Vitality assessment (v8) — battery as operational signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import SensorSnapshot
from src.modules.vitality import (
    VitalityAssessment,
    assess_vitality,
    critical_battery_threshold,
    merge_nomad_telemetry_into_snapshot,
    vitality_communication_hint,
)


def test_assess_none_unknown():
    a = assess_vitality(None)
    assert not a.is_critical
    assert a.battery_level is None


def test_assess_critical_low():
    a = assess_vitality(SensorSnapshot(battery_level=0.02))
    assert a.is_critical
    assert a.battery_level == 0.02


def test_critical_threshold_env(monkeypatch):
    monkeypatch.setenv("KERNEL_VITALITY_CRITICAL_BATTERY", "0.2")
    assert critical_battery_threshold() == 0.2
    a = assess_vitality(SensorSnapshot(battery_level=0.15))
    assert a.is_critical


def test_vitality_hint_only_when_critical():
    assert (
        vitality_communication_hint(
            VitalityAssessment(0.5, 0.05, False, None, 80.0, False, False)
        )
        == ""
    )
    h = vitality_communication_hint(
        VitalityAssessment(0.02, 0.05, True, None, 80.0, False, False)
    )
    assert "vitality" in h.lower() or "power" in h.lower() or "operational" in h.lower()


def test_merge_nomad_fills_missing_battery():
    base = SensorSnapshot(battery_level=None, core_temperature=None)
    nomad = {"battery_level": 0.4, "core_temperature": 42.0}
    merged = merge_nomad_telemetry_into_snapshot(base, nomad)
    assert merged is not None
    assert merged.battery_level == 0.4
    assert merged.core_temperature == 42.0


def test_merge_prefers_existing_client_battery():
    base = SensorSnapshot(battery_level=0.9)
    nomad = {"battery_level": 0.1}
    merged = merge_nomad_telemetry_into_snapshot(base, nomad)
    assert merged.battery_level == 0.9


def test_merge_nomad_battery_alias():
    base = SensorSnapshot(battery_level=None)
    merged = merge_nomad_telemetry_into_snapshot(base, {"battery": 0.61})
    assert merged is not None
    assert merged.battery_level == 0.61


def test_merge_nomad_battery_percent_heuristic():
    """LAN clients often send 0–100; must not clamp to 1.0 via :meth:`SensorSnapshot.from_dict`."""
    base = SensorSnapshot(battery_level=None)
    merged = merge_nomad_telemetry_into_snapshot(base, {"battery": 72})
    assert merged is not None
    assert abs(merged.battery_level - 0.72) < 1e-6


def test_merge_nomad_temperature_and_jerk_aliases():
    base = SensorSnapshot(
        battery_level=None,
        core_temperature=None,
        accelerometer_jerk=None,
    )
    merged = merge_nomad_telemetry_into_snapshot(
        base,
        {"core_temperature_c": 38.2, "jerk": 0.05},
    )
    assert merged.core_temperature == 38.2
    assert merged.accelerometer_jerk == 0.05


def test_merge_nomad_input_dict_not_mutated():
    nomad = {"battery": 0.44}
    merge_nomad_telemetry_into_snapshot(None, nomad)
    assert set(nomad.keys()) == {"battery"}


def test_to_public_dict():
    d = VitalityAssessment(0.04, 0.05, True, None, 80.0, False, False).to_public_dict()
    assert d["is_critical"] is True
    assert d["battery_unknown"] is False
