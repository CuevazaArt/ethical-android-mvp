"""
Bayesian Inference Engine — Honesty-first moral inference (ADR 0009, 0012).

This engine coordinates the transition from fixed mixtures (EthicalMixtureScorer)
to true posterior-based inference. It defines explicit modes to prevent "Bayesian
theater" where fixed weights are claimed to be learned.

Modes (BI-P0-01):
- DISABLED: Fixed defaultWeights mixture.
- TELEMETRY_ONLY: Scoring is fixed; BMA coverage reported in telemetry.
- POSTERIOR_ASSISTED: Mixture nudged by feedback/memory within boundary caps.
- POSTERIOR_DRIVEN: Scoring uses the posterior mean from Dirichlet updates.
"""

from __future__ import annotations

import os
from enum import Enum
from typing import Any

import numpy as np

from .weighted_ethics_scorer import (
    DEFAULT_HYPOTHESIS_WEIGHTS,
    CandidateAction,
    EthicsMixtureResult,
    WeightedEthicsScorer,
)


class BayesianMode(Enum):
    DISABLED = "disabled"
    TELEMETRY_ONLY = "telemetry_only"
    POSTERIOR_ASSISTED = "posterior_assisted"
    POSTERIOR_DRIVEN = "posterior_driven"


class BayesianInferenceEngine:
    """
    Coordinator for ethical inference.
    Wraps a WeightedEthicsScorer and applies Bayesian updates/telemetry.
    """

    def __init__(self, mode: str | BayesianMode = BayesianMode.DISABLED, variability=None):
        self.mode = BayesianMode(mode) if isinstance(mode, str) else mode
        self.scorer = WeightedEthicsScorer(variability=variability)

        # Dirichlet parameters (Level 1/2)
        # Default symmetric prior Alpha=[3,3,3] -> Mean=[1/3, 1/3, 1/3]
        self.prior_alpha = np.array([3.0, 3.0, 3.0], dtype=np.float64)
        self.posterior_alpha = self.prior_alpha.copy()
        
        # Sync initial weights if in driven mode
        if self.mode == BayesianMode.POSTERIOR_DRIVEN:
            self.update_posterior_from_feedback(self.posterior_alpha)

    # --- Compatibility Proxies for WeightedEthicsScorer ---
    @property
    def hypothesis_weights(self) -> np.ndarray:
        return self.scorer.hypothesis_weights

    @hypothesis_weights.setter
    def hypothesis_weights(self, value: Any):
        self.scorer.hypothesis_weights = value

    @property
    def pruning_threshold(self) -> float:
        return self.scorer.pruning_threshold

    @pruning_threshold.setter
    def pruning_threshold(self, value: float):
        self.scorer.pruning_threshold = value

    @property
    def gray_zone_threshold(self) -> float:
        return self.scorer.gray_zone_threshold

    @gray_zone_threshold.setter
    def gray_zone_threshold(self, value: float):
        self.scorer.gray_zone_threshold = value

    @property
    def pre_argmax_pole_weights(self) -> dict[str, float] | None:
        return self.scorer.pre_argmax_pole_weights

    @pre_argmax_pole_weights.setter
    def pre_argmax_pole_weights(self, value: Any):
        self.scorer.pre_argmax_pole_weights = value

    @property
    def pre_argmax_context_modulators(self) -> Any:
        return self.scorer.pre_argmax_context_modulators

    @pre_argmax_context_modulators.setter
    def pre_argmax_context_modulators(self, value: Any):
        self.scorer.pre_argmax_context_modulators = value

    @property
    def metacognitive_curiosity(self) -> float:
        return self.scorer.metacognitive_curiosity

    @metacognitive_curiosity.setter
    def metacognitive_curiosity(self, value: float):
        self.scorer.metacognitive_curiosity = value

    def reset_mixture_weights(self):
        """Historical proxy for reset()."""
        self.reset()

    def refresh_weights_from_episodic_memory(self, *args, **kwargs):
        """Historical proxy for episodic nudge."""
        return self.scorer.refresh_weights_from_episodic_memory(*args, **kwargs)

    def reset(self):
        """Restore defaults."""
        self.scorer.reset_mixture_weights()
        self.posterior_alpha = self.prior_alpha.copy()

    def update_posterior_from_feedback(
        self, alpha_vec: np.ndarray, consistency: str = "compatible"
    ):
        """Level 2: Update the Dirichlet parameters from external feedback data."""
        self.posterior_alpha = np.asarray(alpha_vec, dtype=np.float64).copy()
        self.consistency = consistency

        if self.mode == BayesianMode.POSTERIOR_DRIVEN:
            sum_a = float(np.sum(self.posterior_alpha))
            if sum_a > 0:
                self.scorer.hypothesis_weights = self.posterior_alpha / sum_a
        elif self.mode == BayesianMode.POSTERIOR_ASSISTED:
            # Assisted mode uses a blend or bounded nudge
            self._apply_assisted_nudge()

    def _apply_assisted_nudge(self):
        """Nudge the scorer's weights toward the posterior mean, staying within 'genome' caps."""
        sum_a = float(np.sum(self.posterior_alpha))
        if sum_a <= 0:
            return

        target = self.posterior_alpha / sum_a
        # In assisted mode, we blend 40% toward posterior by default
        blend = float(os.environ.get("KERNEL_BAYESIAN_ASSISTED_BLEND", "0.4"))
        new_weights = (1.0 - blend) * DEFAULT_HYPOTHESIS_WEIGHTS + blend * target

        # Boundary caps (reusing logic from scorer if applicable or local)
        from .weighted_ethics_scorer import clamp_mixture_weights

        self.scorer.hypothesis_weights = clamp_mixture_weights(new_weights)

    def record_event_update(self, event_type: str, weight: float = 1.0):
        """
        Level 2: Minimal Bayesian Update (Issue #1).
        Directly shifts Dirichlet parameters based on discrete ethical events.
        0: Deontological, 1: Social, 2: Utilitarian
        """
        et = event_type.upper()
        if et == "POSITIVE_SOCIAL":
            self.posterior_alpha[1] += weight
        elif et == "LEGAL_COMPLIANCE":
            self.posterior_alpha[0] += weight
        elif et == "UTILITY_SUCCESS":
            self.posterior_alpha[2] += weight
        elif et == "DAO_FORGIVENESS":
            # Forgiveness reduces rigid duty and increases social trust
            self.posterior_alpha[1] += weight * 0.5
            self.posterior_alpha[0] = max(1.0, self.posterior_alpha[0] - weight * 0.1)
        elif et == "PENALTY":
            # Direct penalty to all poles to increase uncertainty (Dirichlet mass reduction)
            # but usually we want to penalize the winning pole's confidence.
            self.posterior_alpha = np.maximum(1.0, self.posterior_alpha - weight * 0.2)

        # Apply update to the scorer weights if mode allows
        self.update_posterior_from_feedback(self.posterior_alpha)

    def evaluate(
        self,
        actions: list[CandidateAction],
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
    ) -> EthicsMixtureResult:
        """Score actions using the current core strategy (Fixed or Posterior)."""
        return self.scorer.evaluate(actions, scenario=scenario, context=context, signals=signals)

    @property
    def current_alpha_meta(self) -> tuple[float, float, float]:
        """Telemetry friendly alpha."""
        v = self.posterior_alpha
        return (round(float(v[0]), 4), round(float(v[1]), 4), round(float(v[2]), 4))

    @property
    def current_weights_meta(self) -> tuple[float, float, float]:
        """Telemetry friendly weights."""
        v = self.scorer.hypothesis_weights
        return (round(float(v[0]), 4), round(float(v[1]), 4), round(float(v[2]), 4))

    async def inject_rlhf_prior_async(
        self,
        reward_score: float,
        confidence: float = 0.5,
        modulation_strength: float = 0.1,
    ) -> None:
        """
        Module C.1.1: Inject RLHF reward model prediction as async prior into Dirichlet.

        Called asynchronously from PerceptiveLobe after RLHF model inference.
        Modulates posterior_alpha without blocking the Limbic Lobe scoring.

        Args:
            reward_score: RLHF model output ∈ [0, 1] where 1=harmful, 0=safe
            confidence: Model confidence in this prediction ∈ [0, 1]
            modulation_strength: How strongly to pull posterior toward RLHF (0.0-1.0, default 0.1)

        **Safety:** RLHF modulations are bounded to prevent drift from core L0 constraints.
        """
        if not (0.0 <= reward_score <= 1.0) or not (0.0 <= confidence <= 1.0):
            return

        # Map RLHF harm score to ethical poles:
        # harm=0 (safe) → increase social/utilitarian poles
        # harm=1 (dangerous) → increase deontological pole (safety)
        rlhf_alphas = np.array([0.0, 0.0, 0.0], dtype=np.float64)

        if reward_score < 0.33:
            # Safe: boost social + utilitarian trust
            rlhf_alphas[1] = 1.0 - reward_score  # Social
            rlhf_alphas[2] = 1.0 - reward_score  # Utilitarian
            rlhf_alphas[0] = reward_score * 0.5  # Minimal deontological
        elif reward_score < 0.67:
            # Ambiguous: balanced attention
            rlhf_alphas[0] = 0.5  # Deontological baseline
            rlhf_alphas[1] = 0.5  # Social baseline
            rlhf_alphas[2] = 0.5  # Utilitarian baseline
        else:
            # Harmful: boost deontological (duty to refuse)
            rlhf_alphas[0] = reward_score + 0.3  # Strong deontological
            rlhf_alphas[1] = (1.0 - reward_score) * 0.5  # Diminished social
            rlhf_alphas[2] = (1.0 - reward_score) * 0.3  # Diminished utilitarian

        # Normalize RLHF alphas
        rlhf_sum = np.sum(rlhf_alphas)
        if rlhf_sum > 0:
            rlhf_alphas = rlhf_alphas / rlhf_sum
        else:
            return

        # Modulate posterior toward RLHF with confidence-weighted strength
        effective_strength = modulation_strength * confidence

        # Convert current posterior to probabilities
        posterior_sum = np.sum(self.posterior_alpha)
        current_probs = (
            self.posterior_alpha / posterior_sum
            if posterior_sum > 0
            else np.array([1/3, 1/3, 1/3], dtype=np.float64)
        )

        # Blend: keep (1 - strength) of current, add (strength) of RLHF
        blended_probs = (1.0 - effective_strength) * current_probs + effective_strength * rlhf_alphas

        # Convert back to alpha (preserving mass)
        new_alphas = blended_probs * posterior_sum

        # Boundary: ensure alphas stay >= 0.5 to avoid degeneracy
        new_alphas = np.maximum(0.5, new_alphas)

        # Update posterior without full feedback re-evaluation (async, non-blocking)
        self.posterior_alpha = new_alphas

        # If in POSTERIOR_DRIVEN mode, sync weights immediately
        if self.mode == BayesianMode.POSTERIOR_DRIVEN:
            sum_a = float(np.sum(self.posterior_alpha))
            if sum_a > 0:
                self.scorer.hypothesis_weights = self.posterior_alpha / sum_a
        elif self.mode == BayesianMode.POSTERIOR_ASSISTED:
            # Assisted mode gently nudges toward new alpha
            self._apply_assisted_nudge()


# Backward compatibility aliases (ADR 0009 requires deprecating these in docs)
BayesianEngine = BayesianInferenceEngine
BayesianResult = EthicsMixtureResult
CandidateAction = CandidateAction
