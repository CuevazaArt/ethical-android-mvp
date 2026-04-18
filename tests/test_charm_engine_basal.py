"""Basal-ganglia EMA optional path on the charm layer (MER Block 10.3)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.charm_engine import (
    CharmEngine,
    clear_charm_engine_basal_singleton_for_tests,
)
from src.modules.uchi_soto import InteractionProfile, TrustCircle
from src.modules.user_model import UserModelTracker


def _profile() -> InteractionProfile:
    return InteractionProfile(agent_id="u1", circle=TrustCircle.SOTO_NEUTRO, trust_score=0.6)


def test_basal_smoothing_off_by_default() -> None:
    clear_charm_engine_basal_singleton_for_tests()
    e = CharmEngine()
    p = _profile()
    u = UserModelTracker()
    r0 = e.apply("Hello", "converse_with_care", p, u, 0.2, False)
    clear_charm_engine_basal_singleton_for_tests()
    e2 = CharmEngine()
    r1 = e2.apply("Hello", "converse_with_care", p, u, 0.2, False)
    assert r0.charm_vector["warmth"] == r1.charm_vector["warmth"]


def test_basal_smoothing_runs_without_error_when_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_charm_engine_basal_singleton_for_tests()
    monkeypatch.setenv("KERNEL_BASAL_GANGLIA_SMOOTHING", "1")
    e = CharmEngine()
    p = _profile()
    u = UserModelTracker()
    r = e.apply("Hello", "converse_with_care", p, u, 0.2, False)
    assert "warmth" in r.charm_vector
    assert 0.0 <= r.charm_vector["warmth"] <= 1.0
    e.apply("Hi again", "converse_with_care", p, u, 0.2, False)
