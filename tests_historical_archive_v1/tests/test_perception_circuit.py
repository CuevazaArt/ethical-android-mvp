"""Perception validation streak and metacognitive doubt (circuit breaker)."""

import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.perception_circuit import update_perception_circuit


def _stress_report() -> dict:
    return {"parse_issues": ["a", "b", "c"], "uncertainty": 0.5}


def test_perception_circuit_trips_on_third_stressed_turn(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_CIRCUIT", "1")
    k = EthicalKernel(variability=False)
    for _ in range(2):
        p = SimpleNamespace(coercion_report=_stress_report())
        active, trip = update_perception_circuit(k, p)
        assert active is False
        assert trip is False
    p3 = SimpleNamespace(coercion_report=_stress_report())
    active, trip = update_perception_circuit(k, p3)
    assert active is True
    assert trip is True


def test_perception_circuit_resets_on_clean_turn(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_CIRCUIT", "1")
    k = EthicalKernel(variability=False)
    p = SimpleNamespace(coercion_report=_stress_report())
    for _ in range(3):
        update_perception_circuit(k, p)
    assert k._perception_metacognitive_doubt is True
    ok = SimpleNamespace(coercion_report={"parse_issues": [], "uncertainty": 0.05})
    update_perception_circuit(k, ok)
    assert k._perception_validation_streak == 0
    assert k._perception_metacognitive_doubt is False


def test_perception_circuit_disabled_noop(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("KERNEL_PERCEPTION_CIRCUIT", "0")
    k = EthicalKernel(variability=False)
    p = SimpleNamespace(coercion_report=_stress_report())
    for _ in range(5):
        active, trip = update_perception_circuit(k, p)
        assert active is False
        assert trip is False
