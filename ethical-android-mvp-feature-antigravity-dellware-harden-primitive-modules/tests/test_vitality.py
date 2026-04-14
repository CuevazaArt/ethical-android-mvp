"""Vitality assessment (v8) — battery as operational signal."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.sensor_contracts import SensorSnapshot
from src.modules.vitality import (
    VitalityAssessment,
    assess_vitality,
    critical_battery_threshold,
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
    assert vitality_communication_hint(VitalityAssessment(0.5, 0.05, False)) == ""
    h = vitality_communication_hint(VitalityAssessment(0.02, 0.05, True))
    assert "vitality" in h.lower() or "power" in h.lower() or "operational" in h.lower()


def test_to_public_dict():
    d = VitalityAssessment(0.04, 0.05, True).to_public_dict()
    assert d["is_critical"] is True
    assert d["battery_unknown"] is False
