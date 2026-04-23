"""Vitality assessment (v8) — battery as operational signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import SensorSnapshot
from src.modules.vitality import (
    VitalityAssessment,
    assess_vitality,
    critical_battery_threshold,
    critical_temperature_threshold,
    merge_nomad_telemetry_into_snapshot,
    thermal_warn_threshold,
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
            VitalityAssessment(0.5, 0.05, False, None, 80.0, False, False, False)
        )
        == ""
    )
    h = vitality_communication_hint(
        VitalityAssessment(0.02, 0.05, True, None, 80.0, False, False, False)
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


def test_merge_nomad_device_temp_alias():
    base = SensorSnapshot(battery_level=None, core_temperature=None)
    nomad = {"device_temp_c": 41.0}
    merged = merge_nomad_telemetry_into_snapshot(base, nomad)
    assert merged is not None
    assert merged.core_temperature == 41.0


def test_merge_nomad_passthrough_raw_jerk_matches_assess():
    """Jerk from Nomad must not be squashed to [0,1] before assess_vitality (Fase 15.2)."""
    base = SensorSnapshot(accelerometer_jerk=None, battery_level=1.0)
    merged = merge_nomad_telemetry_into_snapshot(base, {"shock": 1.2})
    assert merged is not None
    assert merged.accelerometer_jerk == 1.2
    a = assess_vitality(merged)
    assert a.is_impacted is True


def test_to_public_dict():
    d = VitalityAssessment(0.04, 0.05, True, None, 80.0, False, False, False).to_public_dict()
    assert d["is_critical"] is True
    assert d["battery_unknown"] is False


def test_assess_vitality_treats_non_finite_sensors_as_missing():
    import math

    a = assess_vitality(
        SensorSnapshot(
            battery_level=float("nan"),
            accelerometer_jerk=float("inf"),
            core_temperature=float("-inf"),
        )
    )
    assert a.battery_level is None
    assert a.is_impacted is False
    assert a.core_temperature is None
    assert a.thermal_critical is False
    assert a.thermal_elevated is False
    assert not math.isnan(float(a.critical_threshold))


def test_vitality_hint_nonfinite_trust_is_untrusted():
    crit = VitalityAssessment(0.02, 0.05, True, 99.0, 80.0, True, False, False)
    h_nan = vitality_communication_hint(crit, trust_level=float("nan"))
    h_zero = vitality_communication_hint(crit, trust_level=0.0)
    assert h_nan == h_zero


def test_assess_thermal_elevated_in_warn_band():
    a = assess_vitality(SensorSnapshot(core_temperature=75.0))
    assert a.thermal_elevated is True
    assert a.thermal_critical is False
    h = vitality_communication_hint(a, trust_level=1.0)
    assert "elevated" in h.lower() or "thermal" in h.lower()


def test_thermal_warn_coercion_when_mis_set(monkeypatch):
    """Warn must stay strictly below critical so the advisory band is non-empty."""
    monkeypatch.setenv("KERNEL_VITALITY_CRITICAL_TEMP", "50")
    monkeypatch.setenv("KERNEL_VITALITY_THERMAL_WARN_C", "90")
    assert critical_temperature_threshold() == 50.0
    assert thermal_warn_threshold() < critical_temperature_threshold()
    a = assess_vitality(SensorSnapshot(core_temperature=48.0))
    assert a.thermal_elevated is True
    assert a.thermal_critical is False
