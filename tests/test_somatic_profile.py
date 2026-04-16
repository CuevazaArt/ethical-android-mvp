"""
Tests for the Somatic Profile (Thermal Tension & Battery Drain) prototype.
Verifies that critical temperatures trigger correct ethical nudges and LLM hints.
"""

import pytest
from src.modules.sensor_contracts import SensorSnapshot, merge_sensor_hints_into_signals
from src.modules.vitality import assess_vitality, vitality_communication_hint

def test_somatic_profile_thermal_critical():
    # 1. Simulate an overheated snapshot
    snapshot = SensorSnapshot(core_temperature=85.0, battery_level=0.4)
    assert not snapshot.is_empty()
    
    # 2. Assess vitality
    assessment = assess_vitality(snapshot)
    assert assessment.core_temperature == 85.0
    assert assessment.thermal_critical is True
    assert assessment.is_critical is False # battery is fine
    
    # 3. Verify LLM communication hint
    hint = vitality_communication_hint(assessment)
    assert "internal core temperature is critically high" in hint
    assert "thermal tension" in hint
    
    # 4. Verify signal nudging
    base_signals = {"risk": 0.2, "urgency": 0.1, "vulnerability": 0.1, "calm": 0.8}
    merged_signals = merge_sensor_hints_into_signals(base_signals, snapshot)
    
    assert merged_signals["urgency"] == pytest.approx(0.45)  # 0.1 + 0.35
    assert merged_signals["vulnerability"] == pytest.approx(0.60)  # 0.1 + 0.50
    assert merged_signals["risk"] == pytest.approx(0.40)  # 0.2 + 0.20
    assert merged_signals["calm"] == pytest.approx(0.40)  # 0.8 - 0.40


def test_somatic_profile_normal_conditions():
    snapshot = SensorSnapshot(core_temperature=35.0, battery_level=0.9)
    assessment = assess_vitality(snapshot)
    
    assert not assessment.thermal_critical
    assert not assessment.is_critical
    
    hint = vitality_communication_hint(assessment)
    assert hint == ""
    
    base_signals = {"risk": 0.2, "urgency": 0.1}
    merged_signals = merge_sensor_hints_into_signals(base_signals, snapshot)
    
    assert merged_signals["urgency"] == pytest.approx(0.1)
    assert merged_signals["risk"] == pytest.approx(0.2)

def test_somatic_profile_fallback_limits():
    # Empty snapshot shouldn't fail
    assessment = assess_vitality(None)
    assert assessment.core_temperature is None
    assert assessment.thermal_critical is False
    assert assessment.is_critical is False
