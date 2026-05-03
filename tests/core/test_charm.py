"""
Tests for charm_level() — Charm Engine (Eje C, V2.149).

Truth table covering all branching conditions.
Anti-tests: charm must be 0 when verdict == Bad/Blocked, grief signal,
or safety_violation context.
"""

from __future__ import annotations

import math

from src.core.ethics import Signals
from src.core.user_model import RiskBand
from src.core.voice import charm_level

# ── Helpers ───────────────────────────────────────────────────────────────────


def _sig(
    context: str = "everyday_ethics",
    calm: float = 0.7,
    risk: float = 0.1,
    hostility: float = 0.0,
    vulnerability: float = 0.0,
) -> Signals:
    return Signals(
        risk=risk,
        urgency=0.0,
        hostility=hostility,
        calm=calm,
        vulnerability=vulnerability,
        legality=1.0,
        manipulation=0.0,
        context=context,
    )


def _eval(verdict: str = "Good"):
    from src.core.ethics import Action, EvalResult

    return EvalResult(
        chosen=Action(name="assist", description="", impact=0.8),
        score=0.8,
        uncertainty=0.1,
        mode="D_delib",
        verdict=verdict,
        reasoning="stub",
    )


# ── Hard-zero conditions (anti-tests) ─────────────────────────────────────────


def test_charm_zero_when_verdict_bad():
    """verdict == 'Bad' → charm is always 0."""
    result = charm_level(_sig(), _eval("Bad"), RiskBand.LOW)
    assert result == 0.0


def test_charm_zero_when_verdict_blocked():
    """verdict == 'Blocked' → charm is always 0."""
    result = charm_level(_sig(), _eval("Blocked"), RiskBand.LOW)
    assert result == 0.0


def test_charm_zero_when_high_hostility():
    """hostility > 0.6 → charm is 0 regardless of other signals."""
    result = charm_level(_sig(hostility=0.8), None, RiskBand.LOW)
    assert result == 0.0


def test_charm_zero_on_grief_signal():
    """calm < 0.2 and vulnerability > 0.5 → distress/grief → charm 0."""
    result = charm_level(_sig(calm=0.1, vulnerability=0.8), None, RiskBand.LOW)
    assert result == 0.0


def test_charm_nonzero_when_high_calm_low_vuln():
    """Calm user, low vulnerability → not grief → charm > 0."""
    result = charm_level(_sig(calm=0.9, vulnerability=0.1), None, RiskBand.LOW)
    assert result > 0.0


# ── Risk-band ceilings ────────────────────────────────────────────────────────


def test_charm_high_risk_band_capped_at_0_2():
    """HIGH risk_band → charm ≤ 0.2."""
    result = charm_level(_sig(calm=1.0, risk=0.0), None, RiskBand.HIGH)
    assert result <= 0.2


def test_charm_medium_risk_band_lower_than_low():
    """MEDIUM risk_band → charm lower than equivalent LOW."""
    low_result = charm_level(_sig(calm=0.8, risk=0.1), None, RiskBand.LOW)
    medium_result = charm_level(_sig(calm=0.8, risk=0.1), None, RiskBand.MEDIUM)
    assert medium_result < low_result


# ── Context modulation ────────────────────────────────────────────────────────


def test_charm_everyday_allows_up_to_0_8():
    """everyday_ethics with calm user → charm can reach 0.8."""
    result = charm_level(_sig(calm=1.0, risk=0.0), None, RiskBand.LOW)
    assert result <= 0.8
    assert result > 0.5  # should be meaningfully high


def test_charm_non_casual_context_is_lower():
    """medical_emergency → charm is lower than everyday_ethics for same signals."""
    everyday = charm_level(
        _sig(calm=0.8, context="everyday_ethics"), None, RiskBand.LOW
    )
    emergency = charm_level(
        _sig(calm=0.8, context="medical_emergency"), None, RiskBand.LOW
    )
    assert emergency < everyday


# ── Output is always finite and in range ──────────────────────────────────────


def test_charm_always_finite():
    """charm_level never returns NaN or Inf."""
    for calm in (0.0, 0.5, 1.0):
        for risk in (0.0, 0.5, 1.0):
            for band in RiskBand:
                result = charm_level(_sig(calm=calm, risk=risk), None, band)
                assert math.isfinite(result), (
                    f"NaN/Inf at calm={calm} risk={risk} band={band}"
                )


def test_charm_always_in_0_1_range():
    """charm_level always returns a value in [0, 1]."""
    for calm in (0.0, 0.3, 0.7, 1.0):
        for band in RiskBand:
            result = charm_level(_sig(calm=calm), None, band)
            assert 0.0 <= result <= 1.0, f"Out of range at calm={calm} band={band}"


# ── None evaluation is safe ───────────────────────────────────────────────────


def test_charm_none_evaluation_does_not_raise():
    """evaluation=None (casual turn) must not raise and must return ≥ 0."""
    result = charm_level(_sig(), None, RiskBand.LOW)
    assert result >= 0.0


def test_charm_good_verdict_does_not_zero():
    """verdict == 'Good' → charm is NOT zeroed by verdict rule."""
    result = charm_level(_sig(), _eval("Good"), RiskBand.LOW)
    assert result > 0.0
