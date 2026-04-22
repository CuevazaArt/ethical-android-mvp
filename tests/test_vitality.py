"""Vitality assessment (v8) — battery as operational signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.perception.sensor_contracts import SensorSnapshot
from src.modules.somatic.vitality import (
    VitalityAssessment,
    apply_nomad_telemetry_if_enabled,
    assess_vitality,
    critical_battery_threshold,
    impact_jerk_threshold,
    normalize_nomad_telemetry_for_sensor_merge,
    reset_thermal_interrupt_latch_for_tests,
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
            VitalityAssessment(0.5, 0.05, False, 40.0, 80.0, False, False, False)
        )
        == ""
    )
    h = vitality_communication_hint(
        VitalityAssessment(0.02, 0.05, True, 40.0, 80.0, False, False, False)
    )
    assert "vitality" in h.lower() or "power" in h.lower() or "operational" in h.lower()


def test_to_public_dict():
    d = VitalityAssessment(0.04, 0.05, True, 40.0, 80.0, False, False, False).to_public_dict()
    assert d["is_critical"] is True
    assert d["battery_unknown"] is False
    assert "thermal_elevated" in d


def test_thermal_elevated_band(monkeypatch):
    monkeypatch.setenv("KERNEL_VITALITY_WARNING_TEMP", "70")
    monkeypatch.setenv("KERNEL_VITALITY_CRITICAL_TEMP", "80")
    monkeypatch.setenv("KERNEL_VITALITY_THERMAL_HYSTERESIS", "0")
    reset_thermal_interrupt_latch_for_tests()
    a = assess_vitality(SensorSnapshot(core_temperature=75.0))
    assert a.thermal_elevated is True
    assert a.thermal_critical is False


def test_thermal_hysteresis_latch(monkeypatch):
    monkeypatch.setenv("KERNEL_VITALITY_CRITICAL_TEMP", "80")
    monkeypatch.setenv("KERNEL_VITALITY_THERMAL_HYSTERESIS_C", "4")
    monkeypatch.setenv("KERNEL_VITALITY_THERMAL_HYSTERESIS", "1")
    reset_thermal_interrupt_latch_for_tests()
    assert assess_vitality(SensorSnapshot(core_temperature=82.0)).thermal_critical is True
    assert assess_vitality(SensorSnapshot(core_temperature=79.0)).thermal_critical is True
    assert assess_vitality(SensorSnapshot(core_temperature=75.0)).thermal_critical is False


def test_normalize_nomad_skin_temp_alias():
    raw = normalize_nomad_telemetry_for_sensor_merge({"skin_temperature": 42.0})
    assert raw.get("core_temperature") == 42.0


def test_apply_nomad_telemetry_fills_battery_when_missing(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_TELEMETRY_VITALITY", "1")
    from src.modules.perception.nomad_bridge import get_nomad_bridge

    reset_thermal_interrupt_latch_for_tests()
    bridge = get_nomad_bridge()
    with bridge._telemetry_lock:
        bridge._latest_telemetry = {"battery": 0.02}
    snap = apply_nomad_telemetry_if_enabled(None)
    assert snap is not None
    assert snap.battery_level == 0.02
    assert assess_vitality(snap).is_critical
    with bridge._telemetry_lock:
        bridge._latest_telemetry = None


def test_apply_nomad_telemetry_respects_explicit_battery(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_TELEMETRY_VITALITY", "1")
    from src.modules.perception.nomad_bridge import get_nomad_bridge

    bridge = get_nomad_bridge()
    with bridge._telemetry_lock:
        bridge._latest_telemetry = {"battery": 0.99}
    snap = apply_nomad_telemetry_if_enabled(SensorSnapshot(battery_level=0.02))
    assert snap.battery_level == 0.02
    with bridge._telemetry_lock:
        bridge._latest_telemetry = None


def test_apply_nomad_telemetry_disabled(monkeypatch):
    monkeypatch.setenv("KERNEL_NOMAD_TELEMETRY_VITALITY", "0")
    from src.modules.perception.nomad_bridge import get_nomad_bridge

    bridge = get_nomad_bridge()
    with bridge._telemetry_lock:
        bridge._latest_telemetry = {"battery": 0.99}
    assert apply_nomad_telemetry_if_enabled(None) is None
    with bridge._telemetry_lock:
        bridge._latest_telemetry = None


def test_impact_jerk_threshold_env(monkeypatch):
    monkeypatch.setenv("KERNEL_VITALITY_IMPACT_JERK_THRESHOLD", "0.5")
    assert impact_jerk_threshold() == 0.5
    reset_thermal_interrupt_latch_for_tests()
    a = assess_vitality(SensorSnapshot(accelerometer_jerk=0.6))
    assert a.is_impacted
    assert a.is_critical
