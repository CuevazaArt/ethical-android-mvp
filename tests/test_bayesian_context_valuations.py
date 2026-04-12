"""Contextual hypothesis valuations: ranking can differ from pure ``estimated_impact`` ordering."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.bayesian_engine import (
    DEFAULT_HYPOTHESIS_WEIGHTS,
    BayesianEngine,
    CandidateAction,
    _ethical_hypothesis_valuations,
    _legacy_affine_valuations,
)


def test_legacy_affine_preserves_base_ordering():
    """Old formula: higher base always yields higher each v_i, same action ordering as base."""
    b1 = _legacy_affine_valuations(0.3)
    b2 = _legacy_affine_valuations(0.5)
    assert np.all(b2 > b1)


def test_contextual_valuations_can_flip_winner_vs_base():
    """Same estimated_impact; high force lowers deontological slot enough to change mixture winner."""
    eng = BayesianEngine()
    sig = {"risk": 0.2, "legality": 1.0, "vulnerability": 0.1, "calm": 0.5}
    low_f = CandidateAction(
        name="restrain_soft",
        description="",
        estimated_impact=0.55,
        confidence=0.8,
        force=0.05,
    )
    high_f = CandidateAction(
        name="strike_hard",
        description="",
        estimated_impact=0.55,
        confidence=0.8,
        force=0.95,
    )
    ei_low = eng.calculate_expected_impact(
        low_f, scenario="conflict", context="everyday_ethics", signals=sig
    )
    ei_high = eng.calculate_expected_impact(
        high_f, scenario="conflict", context="everyday_ethics", signals=sig
    )
    assert ei_low > ei_high


def test_hypothesis_components_are_not_parallel_affines_of_base():
    """Valuations[1] / valuations[0] ratio varies with force at fixed base (not a constant)."""
    sig = {"risk": 0.1, "legality": 1.0, "calm": 0.5}
    base = 0.5
    v_low = _ethical_hypothesis_valuations(
        CandidateAction(name="x", description="", estimated_impact=base, confidence=0.8, force=0.0),
        scenario="",
        context="",
        signals=sig,
    )
    v_high = _ethical_hypothesis_valuations(
        CandidateAction(name="x", description="", estimated_impact=base, confidence=0.8, force=0.9),
        scenario="",
        context="",
        signals=sig,
    )
    r_low = v_low[1] / max(1e-9, v_low[0])
    r_high = v_high[1] / max(1e-9, v_high[0])
    assert abs(r_low - r_high) > 0.05


def test_default_weights_sum_to_one():
    assert abs(float(np.sum(DEFAULT_HYPOTHESIS_WEIGHTS)) - 1.0) < 1e-9
