"""
Bayesian Variability — Controlled noise for naturalness.

Introduces stochastic variability in evaluations so that
the android does not produce identical results every time, while
maintaining ethical consistency (the chosen action is robust, scores vary).

Principle: a human who would always help the elderly person but with
different levels of urgency depending on how they feel that day.
"""

import numpy as np
from dataclasses import dataclass
from typing import Optional


@dataclass
class VariabilityConfig:
    """Bayesian noise configuration."""
    impact_noise: float = 0.05      # sigma for estimated impact noise
    confidence_noise: float = 0.03  # sigma for confidence noise
    sigma_noise: float = 0.02       # sigma for sympathetic-parasympathetic noise
    poles_noise: float = 0.04       # sigma for ethical pole weight noise
    seed: Optional[int] = None      # None = real random, int = reproducible


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

    def __init__(self, config: VariabilityConfig = None):
        self.config = config or VariabilityConfig()
        self.rng = np.random.default_rng(self.config.seed)
        self._active = True

    def activate(self):
        """Activate variability (active by default)."""
        self._active = True

    def deactivate(self):
        """Deactivate for deterministic tests."""
        self._active = False

    def perturb_impact(self, impact: float) -> float:
        """Perturb the estimated impact of an action."""
        if not self._active:
            return impact
        noise = self.rng.normal(0, self.config.impact_noise)
        return float(np.clip(impact + noise, -1.0, 1.0))

    def perturb_confidence(self, confidence: float) -> float:
        """Perturb the confidence level."""
        if not self._active:
            return confidence
        noise = self.rng.normal(0, self.config.confidence_noise)
        return float(np.clip(confidence + noise, 0.05, 1.0))

    def perturb_sigma(self, sigma: float) -> float:
        """Perturb the sympathetic-parasympathetic state."""
        if not self._active:
            return sigma
        noise = self.rng.normal(0, self.config.sigma_noise)
        return float(np.clip(sigma + noise, 0.2, 0.8))

    def perturb_pole_weight(self, weight: float) -> float:
        """Perturb the weight of an ethical pole."""
        if not self._active:
            return weight
        noise = self.rng.normal(0, self.config.poles_noise)
        return float(np.clip(weight + noise, 0.3, 0.9))

    def reset_seed(self, seed: int = None):
        """Reset the generator with a new seed."""
        self.rng = np.random.default_rng(seed)
