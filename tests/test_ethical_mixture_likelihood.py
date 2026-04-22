"""Tests for Plackett-Luce / IS posterior in ``ethical_mixture_likelihood``."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest
from src.modules.ethics.ethical_mixture_likelihood import (
    FeedbackObservation,
    calibrate_beta,
    importance_sampling_posterior,
    joint_log_likelihood,
    posterior_predictive_probability,
    sequential_posterior_update,
    softmax_choice_log_likelihood,
    softmax_choice_probability,
)
from src.modules.cognition.feedback_mixture_updater import FeedbackUpdater, build_scenario_candidates_map


def test_softmax_log_likelihood_sums() -> None:
    cands = {
        "a": {"util": 0.8, "deon": 0.1, "virtue": 0.1},
        "b": {"util": 0.2, "deon": 0.5, "virtue": 0.3},
    }
    w = np.array([1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0], dtype=np.float64)
    p = softmax_choice_probability("a", cands, w, beta=5.0)
    q = softmax_choice_probability("b", cands, w, beta=5.0)
    assert abs(p + q - 1.0) < 1e-9


def test_log_likelihood_monotonic_in_beta() -> None:
    cands = {
        "x": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
        "y": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
    }
    w = np.array([0.9, 0.05, 0.05], dtype=np.float64)
    ll_low = softmax_choice_log_likelihood("x", cands, w, beta=1.0)
    ll_high = softmax_choice_log_likelihood("x", cands, w, beta=50.0)
    assert ll_high > ll_low


def test_joint_log_likelihood_two_obs() -> None:
    o1 = FeedbackObservation(
        1,
        "a",
        {
            "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
            "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
        },
    )
    o2 = FeedbackObservation(
        2,
        "b",
        {
            "a": {"util": 0.5, "deon": 0.5, "virtue": 0.0},
            "b": {"util": 0.4, "deon": 0.6, "virtue": 0.0},
        },
    )
    w = np.array([1.0 / 3.0] * 3, dtype=np.float64)
    j = joint_log_likelihood([o1, o2], w, beta=10.0)
    assert j < 0.0


def test_importance_sampling_posterior_shape() -> None:
    obs = [
        FeedbackObservation(
            1,
            "a",
            {
                "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
                "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
            },
        )
    ]
    alpha = np.array([3.0, 3.0, 3.0], dtype=np.float64)
    rng = np.random.default_rng(0)
    r = importance_sampling_posterior(obs, alpha, beta=15.0, n_samples=2000, rng=rng)
    assert r.posterior_mean.shape == (3,)
    assert r.projected_alpha.shape == (3,)
    assert r.effective_sample_size > 0


def test_sequential_update_runs() -> None:
    obs = [
        FeedbackObservation(
            1,
            "a",
            {
                "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
                "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
            },
        ),
        FeedbackObservation(
            1,
            "b",
            {
                "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
                "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
            },
        ),
    ]
    alpha0 = np.array([3.0, 3.0, 3.0], dtype=np.float64)
    rng = np.random.default_rng(1)
    final_a, slog = sequential_posterior_update(
        obs, alpha0, beta=12.0, n_samples=1500, rng=rng, max_drift=0.4
    )
    assert final_a.shape == (3,)
    assert len(slog) == 2


def test_posterior_predictive() -> None:
    held = FeedbackObservation(
        1,
        "a",
        {
            "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
            "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
        },
    )
    alpha = np.array([6.0, 6.0, 6.0], dtype=np.float64)
    rng = np.random.default_rng(2)
    p = posterior_predictive_probability(held, alpha, beta=8.0, n_samples=3000, rng=rng)
    assert 0.0 < p <= 1.0


def test_calibrate_beta_grid() -> None:
    obs = [
        FeedbackObservation(
            1,
            "a",
            {
                "a": {"util": 1.0, "deon": 0.0, "virtue": 0.0},
                "b": {"util": 0.0, "deon": 1.0, "virtue": 0.0},
            },
        )
    ]
    alpha = np.array([3.0, 3.0, 3.0], dtype=np.float64)
    rng = np.random.default_rng(3)
    best, scores = calibrate_beta(
        obs, alpha, beta_candidates=[5.0, 10.0, 20.0], n_samples=1500, rng=rng
    )
    assert best in (5.0, 10.0, 20.0)
    assert len(scores) == 3


def test_feedback_updater_softmax_is_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("KERNEL_FEEDBACK_LIKELIHOOD", "softmax_is")
    monkeypatch.setenv("KERNEL_FEEDBACK_SOFTMAX_BETA", "12.0")
    cmap = build_scenario_candidates_map([17])
    assert cmap is not None
    p = tmp_path / "fb.json"
    p.write_text(
        json.dumps([{"scenario_id": 17, "preferred_action": "distribute_by_need"}]),
        encoding="utf-8",
    )
    items = FeedbackUpdater.load_feedback_file(p)
    u = FeedbackUpdater(n_samples=800, seed=2, update_strength=2.0)
    fr = u.ingest_feedback(items, cmap)
    assert fr.consistency in ("compatible", "insufficient", "contradictory")
    assert len(fr.posterior_alpha) == 3
    assert fr.consistency != "insufficient" or fr.n_feedback_items >= 1
