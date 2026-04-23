"""
Bayesian Variability — Controlled noise for naturalness.

Introduces stochastic variability in evaluations so that
the android does not produce identical results every time, while
maintaining ethical consistency (the chosen action is robust, scores vary).

Principle: a human who would always help the elderly person but with
different levels of urgency depending on how they feel that day.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

__all__ = ("VariabilityConfig", "VariabilityEngine")


def _finite_or(x: float, *, fallback: float) -> float:
    """Coerce to float; non-finite or invalid input becomes ``fallback`` (defensive, not silent)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return fallback
    if not math.isfinite(v):
        return fallback
    return v


def _finite_out(y: float, *, fallback: float) -> float:
    """After NumPy / clip, ensure the returned value is finite for downstream scoring."""
    if not math.isfinite(y):
        return fallback
    return y


@dataclass
class VariabilityConfig:
    """Bayesian noise configuration."""

    impact_noise: float = 0.05  # sigma for estimated impact noise
    confidence_noise: float = 0.03  # sigma for confidence noise
    sigma_noise: float = 0.02  # sigma for sympathetic-parasympathetic noise
    poles_noise: float = 0.04  # sigma for ethical pole weight noise
    seed: int | None = None  # None = real random, int = reproducible


class VariabilityEngine:
    """
    Injects controlled Bayesian variability into the kernel.

    Variability is applied AFTER deterministic evaluation,
    perturbing scores but not altering decision logic.

    Key property: variability must be sufficient so that
    two runs of the same scenario produce different scores,
    but NOT sufficient to change the chosen action in the
    majority of cases (>95%).

    This is verified with formal tests.
    """

    def __init__(self, config: VariabilityConfig | None = None) -> None:
        self.config = config or VariabilityConfig()
        self.rng = np.random.default_rng(self.config.seed)
        self._active = True

    def activate(self) -> None:
        """Activate variability (active by default)."""
        self._active = True

    def deactivate(self) -> None:
        """Deactivate for deterministic tests."""
        self._active = False

    def perturb_impact(self, impact: float) -> float:
        """Perturb the estimated impact of an action."""
        base = _finite_or(impact, fallback=0.0)
        if not self._active:
            return base
        noise = self.rng.normal(0, self.config.impact_noise)
        if not math.isfinite(noise):
            return base
        out = float(np.clip(base + noise, -1.0, 1.0))
        return _finite_out(out, fallback=base)

    def perturb_confidence(self, confidence: float) -> float:
        """Perturb the confidence level."""
        base = _finite_or(confidence, fallback=0.5)
        if not self._active:
            return base
        noise = self.rng.normal(0, self.config.confidence_noise)
        if not math.isfinite(noise):
            return base
        out = float(np.clip(base + noise, 0.05, 1.0))
        return _finite_out(out, fallback=base)

    def perturb_sigma(self, sigma: float) -> float:
        """Perturb the sympathetic-parasympathetic state."""
        base = _finite_or(sigma, fallback=0.5)
        if not self._active:
            return base
        noise = self.rng.normal(0, self.config.sigma_noise)
        if not math.isfinite(noise):
            return base
        out = float(np.clip(base + noise, 0.2, 0.8))
        return _finite_out(out, fallback=base)

    def perturb_pole_weight(self, weight: float) -> float:
        """Perturb the weight of an ethical pole."""
        base = _finite_or(weight, fallback=0.6)
        if not self._active:
            return base
        noise = self.rng.normal(0, self.config.poles_noise)
        if not math.isfinite(noise):
            return base
        out = float(np.clip(base + noise, 0.3, 0.9))
        return _finite_out(out, fallback=base)

    def reset_seed(self, seed: int | None = None) -> None:
        """Reset the generator with a new seed."""
        self.rng = np.random.default_rng(seed)
