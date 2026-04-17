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

import logging
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

_logger = logging.getLogger(__name__)

# Env name for BI-P0-01 — see `CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`.
ENV_KERNEL_BAYESIAN_MODE = "KERNEL_BAYESIAN_MODE"


class BayesianMode(Enum):
    DISABLED = "disabled"
    TELEMETRY_ONLY = "telemetry_only"
    POSTERIOR_ASSISTED = "posterior_assisted"
    POSTERIOR_DRIVEN = "posterior_driven"


def resolve_kernel_bayesian_mode(raw: str | None) -> BayesianMode:
    """
    Resolve ``KERNEL_BAYESIAN_MODE`` to a :class:`BayesianMode`.

    - Empty / unset → :data:`BayesianMode.DISABLED`.
    - Case-insensitive; hyphens map to underscores (``posterior-driven`` → ``posterior_driven``).
    - A few aliases: ``off`` / ``none`` / ``0`` / ``false`` → ``disabled``.
    - Unknown values → ``disabled`` and a **warning** log (no silent mis-parse).
    """
    if raw is None:
        return BayesianMode.DISABLED
    s = str(raw).strip()
    if not s:
        return BayesianMode.DISABLED
    v = s.lower().replace("-", "_")
    aliases = frozenset({"off", "none", "0", "false", "no"})
    if v in aliases:
        return BayesianMode.DISABLED
    try:
        return BayesianMode(v)
    except ValueError:
        _logger.warning(
            "Invalid %s=%r; using %r. Valid: %s",
            ENV_KERNEL_BAYESIAN_MODE,
            raw,
            BayesianMode.DISABLED.value,
            ", ".join(m.value for m in BayesianMode),
        )
        return BayesianMode.DISABLED


class BayesianInferenceEngine:
    """
    Coordinator for ethical inference.
    Wraps a WeightedEthicsScorer and applies Bayesian updates/telemetry.
    """

    def __init__(self, mode: str | BayesianMode = BayesianMode.DISABLED, variability=None):
        if isinstance(mode, BayesianMode):
            self.mode = mode
        else:
            self.mode = resolve_kernel_bayesian_mode(str(mode))
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


# Backward compatibility aliases (ADR 0009 requires deprecating these in docs)
BayesianEngine = BayesianInferenceEngine
BayesianResult = EthicsMixtureResult
CandidateAction = CandidateAction
