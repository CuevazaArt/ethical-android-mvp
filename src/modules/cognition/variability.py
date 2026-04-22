"""
Bayesian Variability — Controlled noise for naturalness.

Introduces stochastic variability in evaluations so that
the android does not produce identical results every time, while
maintaining ethical consistency (the chosen action is robust, scores vary).

Principle: a human who would always help the elderly person but with
different levels of urgency depending on how they feel that day.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class VariabilityConfig:
    """
    Configuration for Bayesian noise parameters used in variability injection.

    Attributes:
        impact_noise (float): Sigma for estimated impact noise.
        confidence_noise (float): Sigma for confidence noise.
        sigma_noise (float): Sigma for sympathetic-parasympathetic noise.
        poles_noise (float): Sigma for ethical pole weight noise.
        seed (int | None): Random seed for reproducibility (None = random).
    """

    impact_noise: float = 0.05
    confidence_noise: float = 0.03
    sigma_noise: float = 0.02
    poles_noise: float = 0.04
    seed: int | None = None


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

    def __init__(self, config: VariabilityConfig = None) -> None:
        """
        Initialize the VariabilityEngine.

        Args:
            config (VariabilityConfig, optional): Configuration for noise parameters.
        """
        self.config: VariabilityConfig = config or VariabilityConfig()
        self.rng: np.random.Generator = np.random.default_rng(self.config.seed)
        self._active: bool = True

    def activate(self) -> None:
        """
        Activate variability (active by default).
        """
        self._active = True

    def deactivate(self) -> None:
        """
        Deactivate variability for deterministic tests.
        """
        self._active = False

    def perturb_impact(self, impact: float) -> float:
        """
        Perturb the estimated impact of an action.

        Args:
            impact (float): Original impact value.

        Returns:
            float: Perturbed impact value.
        """
        if not self._active:
            return impact
        noise = self.rng.normal(0, self.config.impact_noise)
        return float(np.clip(impact + noise, -1.0, 1.0))

    def perturb_confidence(self, confidence: float) -> float:
        """
        Perturb the confidence level.

        Args:
            confidence (float): Original confidence value.

        Returns:
            float: Perturbed confidence value.
        """
        if not self._active:
            return confidence
        noise = self.rng.normal(0, self.config.confidence_noise)
        return float(np.clip(confidence + noise, 0.05, 1.0))

    def perturb_sigma(self, sigma: float) -> float:
        """
        Perturb the sympathetic-parasympathetic state.

        Args:
            sigma (float): Original sigma value.

        Returns:
            float: Perturbed sigma value.
        """
        if not self._active:
            return sigma
        noise = self.rng.normal(0, self.config.sigma_noise)
        return float(np.clip(sigma + noise, 0.2, 0.8))

    def perturb_pole_weight(self, weight: float) -> float:
        """
        Perturb the weight of an ethical pole.

        Args:
            weight (float): Original pole weight.

        Returns:
            float: Perturbed pole weight.
        """
        if not self._active:
            return weight
        noise = self.rng.normal(0, self.config.poles_noise)
        return float(np.clip(weight + noise, 0.3, 0.9))

    def reset_seed(self, seed: int = None) -> None:
        """
        Reset the random generator with a new seed.

        Args:
            seed (int, optional): New seed for reproducibility.
        """
        self.rng = np.random.default_rng(seed)
