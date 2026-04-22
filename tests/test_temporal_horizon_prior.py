"""Temporal horizon prior → Bayesian mixture nudge (ADR 0005)."""

import os
import sys
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.narrative import NarrativeMemory
from src.modules.narrative_types import BodyState, NarrativeEpisode
from src.modules.temporal_horizon_prior import (
    TemporalHorizonSignals,
    _parse_ts,
    apply_horizon_prior_to_engine,
    compute_horizon_signals,
)
from src.modules.weighted_ethics_scorer import BayesianEngine


def _declining_episodes_synthetic(n: int = 6) -> list[NarrativeEpisode]:
    """
    In-memory ``NarrativeEpisode`` list (declining ``ethical_score``) for horizon tests.

    Do not use :meth:`NarrativeMemory.register` here: it performs Ollama HTTP embedding fetches
    and persistence, so suite runtime would be dominated by network timeouts when Ollama is down.
    """
    out: list[NarrativeEpisode] = []
    for i in range(n):
        days_ago = n - 1 - i
        t = (datetime.now(UTC) - timedelta(days=days_ago)).replace(microsecond=0)
        ts = t.strftime("%Y-%m-%dT%H:%M:%SZ")
        out.append(
            NarrativeEpisode(
                id=f"EP-{i:04d}",
                timestamp=ts,
                place="p",
                event_description="d",
                body_state=BodyState(),
                action_taken="act_civically",
                morals={},
                verdict="Good",
                ethical_score=0.85 - i * 0.12,
                decision_mode="D_delib",
                sigma=0.5,
                context="everyday",
            )
        )
    return out


def test_parse_ts_invalid_and_z_suffix() -> None:
    assert _parse_ts(SimpleNamespace(timestamp="totally not iso")) is None
    assert _parse_ts(SimpleNamespace(timestamp=object())) is None
    dt = _parse_ts(SimpleNamespace(timestamp="2024-06-01T12:00:00Z"))
    assert dt is not None
    assert dt.tzinfo is not None


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


def test_registered_episodes_produce_nonzero_signal() -> None:
    mem = NarrativeMemory()
    mem.episodes = _declining_episodes_synthetic(6)
    s = compute_horizon_signals(mem, "everyday", "act")
    assert s.long_term_stability > 0.0


def test_apply_prior_nonfinite_combined_skips_nudge(monkeypatch) -> None:
    """Defense in depth: poisoned signals must not NaN-poison hypothesis_weights (ADR 0005)."""
    eng = BayesianEngine()
    w0 = eng.hypothesis_weights.copy()
    mem = NarrativeMemory()
    monkeypatch.setattr(
        "src.modules.temporal_horizon_prior.compute_horizon_signals",
        lambda *a, **k: TemporalHorizonSignals(0.0, 0.5, float("nan")),
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


def test_compute_horizon_signals_all_nan_scores_falls_back() -> None:
    def _ts(days_ago: int) -> str:
        t = datetime.now(UTC) - timedelta(days=days_ago)
        return t.replace(microsecond=0).strftime("%Y-%m-%dT%H:%M:%SZ")

    mem = NarrativeMemory()
    # Three episodes in the default recent window with NaN scores → NaN trajectory / combined; must fall back (Harden-In-Place).
    # (Fixed 2024 timestamps fall outside the 21d window in 2026+; :func:`compute_horizon_signals` also caps *weeks_days* to 120.)
    mem.episodes = [
        NarrativeEpisode(
            id="EP-1",
            timestamp=_ts(3),
            place="p",
            event_description="d",
            body_state=BodyState(),
            action_taken="a",
            morals={},
            verdict="Good",
            ethical_score=float("nan"),
            decision_mode="D_delib",
            sigma=0.5,
            context="everyday",
        ),
        NarrativeEpisode(
            id="EP-2",
            timestamp=_ts(2),
            place="p",
            event_description="d",
            body_state=BodyState(),
            action_taken="a",
            morals={},
            verdict="Good",
            ethical_score=float("nan"),
            decision_mode="D_delib",
            sigma=0.5,
            context="everyday",
        ),
        NarrativeEpisode(
            id="EP-3",
            timestamp=_ts(1),
            place="p",
            event_description="d",
            body_state=BodyState(),
            action_taken="a",
            morals={},
            verdict="Good",
            ethical_score=float("nan"),
            decision_mode="D_delib",
            sigma=0.5,
            context="everyday",
        ),
    ]
    s = compute_horizon_signals(mem, "everyday", "")
    assert s.weeks_trend == 0.0
    assert s.long_term_stability == 0.5
    assert s.combined == 0.0
