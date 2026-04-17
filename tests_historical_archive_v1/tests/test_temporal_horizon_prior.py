"""Temporal horizon prior → Bayesian mixture nudge (ADR 0005)."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.narrative import NarrativeMemory
from src.modules.temporal_horizon_prior import (
    TemporalHorizonSignals,
    apply_horizon_prior_to_engine,
    compute_horizon_signals,
)
from src.modules.weighted_ethics_scorer import BayesianEngine


def _fill_memory_declining(mem: NarrativeMemory, n: int = 6) -> None:
    for i in range(n):
        mem.register(
            place="p",
            description="d",
            action="act_civically",
            morals={},
            verdict="Good",
            score=0.85 - i * 0.12,
            mode="D_delib",
            sigma=0.5,
            context="everyday",
        )


def test_compute_horizon_signals_empty_memory():
    mem = NarrativeMemory()
    s = compute_horizon_signals(mem, "everyday", "")
    assert s.weeks_trend == 0.0
    assert s.combined == 0.0


def test_apply_prior_raises_deontological_weight_when_combined_negative(monkeypatch):
    eng = BayesianEngine()
    w0 = eng.hypothesis_weights.copy()
    mem = NarrativeMemory()

    monkeypatch.setattr(
        "src.modules.temporal_horizon_prior.compute_horizon_signals",
        lambda *a, **k: TemporalHorizonSignals(-0.4, 0.6, -0.5),
    )
    apply_horizon_prior_to_engine(
        eng,
        mem,
        "everyday",
        "",
        genome_weights=(0.4, 0.35, 0.25),
        max_drift=0.25,
    )
    assert eng.hypothesis_weights[1] >= w0[1]


def test_apply_prior_noop_when_combined_zero(monkeypatch):
    eng = BayesianEngine()
    w0 = eng.hypothesis_weights.copy()
    mem = NarrativeMemory()
    monkeypatch.setattr(
        "src.modules.temporal_horizon_prior.compute_horizon_signals",
        lambda *a, **k: TemporalHorizonSignals(0.0, 0.5, 0.0),
    )
    apply_horizon_prior_to_engine(
        eng,
        mem,
        "everyday",
        "",
        genome_weights=(0.4, 0.35, 0.25),
        max_drift=0.15,
    )
    assert np.allclose(eng.hypothesis_weights, w0, atol=1e-9)


def test_registered_episodes_produce_nonzero_signal():
    mem = NarrativeMemory()
    _fill_memory_declining(mem)
    s = compute_horizon_signals(mem, "everyday", "act")
    assert s.long_term_stability > 0.0
