"""Charm layer: finite bounded inputs before style + gesture metadata (MOCK/EXPERIMENTAL)."""

from __future__ import annotations

import math

from src.modules.charm_engine import CharmEngine, StyleParametrizer, _as_nonneg_int_streak, _as_unit01
from src.modules.uchi_soto import InteractionProfile, TrustCircle
from src.modules.user_model import UserModelTracker


def _profile() -> InteractionProfile:
    return InteractionProfile(agent_id="t", circle=TrustCircle.SOTO_NEUTRO, intimacy_level=0.0)


def test_as_unit01_rejects_bool_and_nonfinite() -> None:
    assert _as_unit01(True) == 0.5
    assert _as_unit01(float("nan")) == 0.5
    assert _as_unit01(float("inf")) == 0.5
    assert _as_unit01(0.25) == 0.25
    assert _as_unit01(1.5) == 1.0


def test_as_nonneg_int_streak_sanitizes_caution_correlates() -> None:
    assert _as_nonneg_int_streak(0) == 0
    assert _as_nonneg_int_streak(4) == 4
    assert _as_nonneg_int_streak(-1) == 0
    assert _as_nonneg_int_streak(float("nan")) == 0
    assert _as_nonneg_int_streak(float("inf")) == 0
    assert _as_nonneg_int_streak("2") == 2
    assert _as_nonneg_int_streak("x") == 0
    # float too large to convert to int: defensive path (Pragmatismo V4.0)
    assert _as_nonneg_int_streak(1e400) == 0


def test_charm_apply_produces_finite_vector_with_poisoned_caution() -> None:
    eng = CharmEngine()
    p = _profile()
    tr = UserModelTracker()
    for bad in (float("nan"), float("inf"), float("-inf")):
        out = eng.apply("x", "utilitarian", p, tr, bad, False)
        for v in out.charm_vector.values():
            assert math.isfinite(v)
        for g in out.gesture_plan:
            assert math.isfinite(float(g.get("intensity", 0.0)))


def test_parametrize_clamps_intimacy_when_caution_high() -> None:
    p = _profile()
    p.intimacy_level = 0.9
    tr = UserModelTracker()
    z = StyleParametrizer().parametrize("block", p, tr, 0.9)
    assert math.isfinite(z.warmth) and z.warmth >= 0.0
    assert p.intimacy_level == 0.5
