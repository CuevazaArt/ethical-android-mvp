"""
Bayesian mixture averaging (BMA) over util/deon/virtue weights — **Level 1** of ADR 0012.

This does **not** change the default argmax path: it adds **Monte Carlo win probabilities**
under a Dirichlet prior over mixture weights. For symmetric Dirichlet(α,α,α), the **mean**
weight is the simplex center — the same point estimate as using ``(1/3,1/3,1/3)`` for the
linear score — so the chosen action usually matches; the value is the **distribution** over
winners, not a different winner.

Env (see ADR 0012):

- ``KERNEL_BMA_ENABLED`` — when truthy, ``EthicalKernel.process`` attaches BMA fields.
- ``KERNEL_BMA_ALPHA`` — single scalar (symmetric) or three comma-separated positives.
- ``KERNEL_BMA_SAMPLES`` — MC draws (default 5000).
"""

from __future__ import annotations

import os
from typing import Any

import numpy as np

from .weighted_ethics_scorer import WeightedEthicsScorer


def parse_bma_alpha_from_env() -> np.ndarray:
    """Return length-3 positive alpha vector for Dirichlet prior (symmetric or general)."""
    raw = os.environ.get("KERNEL_BMA_ALPHA", "3.0").strip()
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    if len(parts) == 1:
        a = float(parts[0])
        if a <= 0:
            raise ValueError("KERNEL_BMA_ALPHA must be positive")
        return np.array([a, a, a], dtype=np.float64)
    if len(parts) == 3:
        v = np.array([float(parts[0]), float(parts[1]), float(parts[2])], dtype=np.float64)
        if np.any(v <= 0):
            raise ValueError("KERNEL_BMA_ALPHA components must be positive")
        return v
    raise ValueError("KERNEL_BMA_ALPHA must be one number or three comma-separated numbers")


def bma_enabled() -> bool:
    return os.environ.get("KERNEL_BMA_ENABLED", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


def bma_n_samples() -> int:
    return max(100, int(os.environ.get("KERNEL_BMA_SAMPLES", "5000")))


def monte_carlo_win_probabilities(
    scorer: WeightedEthicsScorer,
    actions: list[Any],
    *,
    alpha: np.ndarray,
    n_samples: int,
    scenario: str,
    context: str,
    signals: dict[str, Any] | None,
    rng: np.random.Generator,
) -> dict[str, float]:
    """
    For each Dirichlet sample ``w``, set ``scorer.hypothesis_weights = w`` and run
    :meth:`WeightedEthicsScorer.evaluate`. Return empirical frequencies of each winning
    action name (viable candidates only).
    """
    saved = np.asarray(scorer.hypothesis_weights, dtype=np.float64).copy()
    alpha = np.asarray(alpha, dtype=np.float64)
    if alpha.shape != (3,) or np.any(alpha <= 0):
        raise ValueError("alpha must be length-3 positive")

    counts: dict[str, int] = {a.name: 0 for a in actions}
    try:
        for _ in range(int(n_samples)):
            w = rng.dirichlet(alpha)
            scorer.hypothesis_weights = w
            res = scorer.evaluate(
                actions,
                scenario=scenario,
                context=context,
                signals=signals,
            )
            counts[res.chosen_action.name] = counts.get(res.chosen_action.name, 0) + 1
    finally:
        scorer.hypothesis_weights = saved

    total = float(n_samples)
    return {k: round(v / total, 6) for k, v in sorted(counts.items())}


def analytic_expected_weights(alpha: np.ndarray) -> np.ndarray:
    """Posterior / prior mean of Dirichlet(α): E[w_i] = α_i / sum(α)."""
    a = np.asarray(alpha, dtype=np.float64)
    s = float(np.sum(a))
    return a / s
