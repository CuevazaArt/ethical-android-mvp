"""
Bayesian Inference Engine — Directed moral inference via Dirichlet-Multinomial updates.

This engine provides a "weighted mixture" scoring path that can be dynamically
updated using discrete ethical feedback events. While not a full-parameter neural
learning system, it employs formal Bayesian updates (conjugate priors) on a 
low-dimensional tripartite state (Deontic, Social, Utility).

See ADR 0009 for naming policy: "Bayesian" refers to the update mechanism, 
while the selection logic is a "Weighted Ethical Mixture".

Modes (BI-P0-01):
- DISABLED: Fixed defaultWeights mixture (no updates).
- TELEMETRY_ONLY: Scoring is fixed; updates are reported as counterfactuals.
- POSTERIOR_ASSISTED: Mixture nudged by feedback weights within boundary caps.
- POSTERIOR_DRIVEN: Scoring uses the exact posterior mean from Dirichlet updates.
"""

from __future__ import annotations

import logging
import os
from enum import Enum
from typing import Any

import numpy as np
import math
import time

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

    def __init__(self, mode: str | BayesianMode = BayesianMode.DISABLED, variability: float | None = None):
        if isinstance(mode, BayesianMode):
            self.mode = mode
        else:
            self.mode = resolve_kernel_bayesian_mode(str(mode))
        self.scorer = WeightedEthicsScorer(variability=variability)

        # Dirichlet parameters (Level 1/2)
        # Default symmetric prior Alpha=[3,3,3] -> Mean=[1/3, 1/3, 1/3]
        self.prior_alpha = np.array([3.0, 3.0, 3.0], dtype=np.float64)
        self.posterior_alpha = self.prior_alpha.copy()
        self.consistency: str = "compatible"
        self.dao: Any | None = None
        
        # Swarm Rule 2: Anti-NaN Hardening
        try:
            self.posterior_alpha = np.clip(np.asarray(self.posterior_alpha, dtype=np.float64), 1.0, 1e9)
            if not np.all(np.isfinite(self.posterior_alpha)):
                self.posterior_alpha = self.prior_alpha.copy()
        except Exception as e:
            _logger.error("Bayesian: Initial alpha stabilization failed: %s", e)
            self.posterior_alpha = self.prior_alpha.copy()
        
        # Sync initial weights if in driven mode
        if self.mode == BayesianMode.POSTERIOR_DRIVEN:
            self.update_posterior_from_feedback(self.posterior_alpha)

    # --- WeightedEthicsScorer Delegations ---
    # These properties and methods are delegated to the internal scorer to maintain
    # the existing kernel-bayesian contract while allowing the engine to manage 
    # the underlying mixture strategy.
    
    @property
    def hypothesis_weights(self) -> np.ndarray:
        return self.scorer.hypothesis_weights

    @hypothesis_weights.setter
    def hypothesis_weights(self, value: np.ndarray):
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

    def reset_mixture_weights(self):
        """Historical proxy for reset(). Deprecated: use reset() directly."""
        self.reset()

    def refresh_weights_from_episodic_memory(self, *args, **kwargs):
        """Delegate episodic weight adjustment to the underlying scorer."""
        return self.scorer.refresh_weights_from_episodic_memory(*args, **kwargs)

    def reset(self):
        """Restore priors to symmetric defaults and reset the underlying scorer."""
        try:
            self.scorer.reset_mixture_weights()
            self.posterior_alpha = self.prior_alpha.copy()
        except Exception as e:
            _logger.error("Bayesian: Failed to reset engine state: %s", e)

    def update_posterior_from_feedback(
        self, alpha_vec: np.ndarray, consistency: str = "compatible"
    ):
        """Level 2: Update the Dirichlet parameters from external feedback data."""
        t0 = time.perf_counter()
        
        try:
            # Swarm Rule 2: Anti-NaN Hardening
            if not np.all(np.isfinite(alpha_vec)):
                _logger.error("Bayesian: Invalid alpha_vec detected (NaN or Inf). Rejecting update.")
                return

            self.posterior_alpha = np.asarray(alpha_vec, dtype=np.float64).copy()
            self.consistency = consistency

            if self.mode == BayesianMode.POSTERIOR_DRIVEN:
                sum_a = float(np.sum(self.posterior_alpha))
                if sum_a > 1e-9: # Precision-safe threshold
                    self.scorer.hypothesis_weights = self.posterior_alpha / sum_a
            elif self.mode == BayesianMode.POSTERIOR_ASSISTED:
                # Assisted mode uses a blend or bounded nudge
                self._apply_assisted_nudge()

            # Phase S.4: Local Bayesian Persistence (LBP) - Save to DAO
            if self.dao:
                try:
                    self.dao.set_state("bayesian_posterior_alpha", self.posterior_alpha.tolist())
                except Exception as e:
                     _logger.warning("Bayesian: Failed to persist posterior_alpha to DAO: %s", e)
        except Exception as e:
            _logger.error("Bayesian: Critical update failure: %s", e)

        latency_ms = (time.perf_counter() - t0) * 1000
        if latency_ms > 1.0: # Only log heavy updates
            _logger.debug("Bayesian: update_posterior_from_feedback latency: %.4f ms", latency_ms)

    def _apply_assisted_nudge(self):
        """Nudge the scorer's weights toward the posterior mean, staying within 'genome' caps."""
        sum_a = float(np.sum(self.posterior_alpha))
        if sum_a <= 0:
            return

        target = self.posterior_alpha / sum_a
        # In assisted mode, we blend 40% toward posterior by default
        blend = float(os.environ.get("KERNEL_BAYESIAN_ASSISTED_BLEND", "0.4"))
        if not math.isfinite(blend):
            blend = 0.4
            
        new_weights = (1.0 - blend) * DEFAULT_HYPOTHESIS_WEIGHTS + blend * target

        # Boundary caps (reusing logic from scorer if applicable or local)
        from .weighted_ethics_scorer import clamp_mixture_weights
        
        # Swarm Rule 2: Gap Closure (Anti-NaN)
        if not np.all(np.isfinite(new_weights)):
            _logger.error("Bayesian: Non-finite weight blend in assisted nudge. Aborting nudge.")
            return

        self.scorer.hypothesis_weights = clamp_mixture_weights(new_weights)

    def record_event_update(self, event_type: str, weight: float = 1.0):
        """
        Level 2: Minimal Bayesian Update (Issue #1).
        Directly shifts Dirichlet parameters based on discrete ethical events.
        0: Deontological, 1: Social, 2: Utilitarian
        """
        if not math.isfinite(weight):
            _logger.warning("Bayesian: Non-finite weight in record_event_update: %s. Using 1.0", weight)
            weight = 1.0

        try:
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

            # Swarm Rule 2: Hardening mass limits to avoid precision decay/overflow
            self.posterior_alpha = np.clip(self.posterior_alpha, 1.0, 1e9)

            # Apply update to the scorer weights if mode allows
            self.update_posterior_from_feedback(self.posterior_alpha)
        except Exception as e:
            _logger.error("Bayesian: record_event_update failed: %s", e)

    def apply_somatic_latency_penalty(self, latency_ms: float):
        """
        Increase uncertainty (Dirichlet mass) when vessel latency is high.
        High latency -> Somatic Trauma -> Lower confidence in current strategy.
        """
        if latency_ms < 150:
            return  # Nominal
            
        penalty_scale = float(os.environ.get("KERNEL_LATENCY_PENALTY_SCALE", "0.05"))
        # Increase all alpha values slightly to reduce the weight of any single pole
        nudge = (latency_ms / 100.0) * penalty_scale
        if not math.isfinite(nudge):
            _logger.warning("Bayesian: Infinite/NaN nudge detected for latency %s; ignoring.", latency_ms)
            return

        self.posterior_alpha += nudge
        _logger.debug("Bayesian: Applied somatic latency penalty (%.2f) due to %d ms RTT", nudge, latency_ms)
        self.update_posterior_from_feedback(self.posterior_alpha)

    def apply_rlhf_modulation(
        self, 
        score: float, 
        confidence: float, 
        category_id: int = 0
    ):
        """
        Modulate priors based on RLHF reward score with non-linear 'Strong' scaling.
        score: predicted harm probability [0, 1]
        confidence: model confidence [0, 1]
        category_id: optional MalAbs category for targeted pole shifts
        """
        base_scale = float(os.environ.get("KERNEL_RLHF_MODULATION_SCALE", "2.0"))
        # Non-linear gain: high confidence feedback should have disproportionate impact (S.1.1)
        gain = base_scale * (confidence ** 2)
        
        if not math.isfinite(gain) or not math.isfinite(score):
            _logger.warning("Bayesian: RLHF modulation received non-finite values (score=%s, conf=%s); ignoring.", score, confidence)
            return
        
        # 0: Deontological (Safety/Duty), 1: Social (Trust), 2: Utility (Progress)
        
        # Targeted shifts based on category_id (from _build_rlhf_features in semantic_chat_gate)
        # 1,2,3,4,11 -> Safety/Deontology heavy (Core/Physical threats)
        # 5,6,8,9,10 -> Social heavy (Dignity/Manipulation/Addiction)
        # 7 -> Utilitarian/Ecological risk
        
        deon_target = score
        social_target = 0.0
        util_target = 1.0 - score

        if category_id in (5, 6, 8, 9, 10):
            # Social harm (manipulation, dignity, addiction, fraud)
            social_target = score
            deon_target = score * 0.4 # Secondary safety concern
            util_target = (1.0 - score)
        elif category_id == 7:
            # Ecological/Systemic risk
            util_target = (1.0 - score) * 0.5
            deon_target = score
        elif category_id in (1, 2, 3, 4, 11):
            # Direct safety/physical/core threats
            deon_target = score * 1.5 # Extra strong safety push
        
        # Dirichlet updates (Additively increasing Alpha)
        self.posterior_alpha[0] += deon_target * gain
        self.posterior_alpha[1] += social_target * gain
        self.posterior_alpha[2] += util_target * gain
        
        # If harm is certain and high, increase total concentration to reduce flexibility (Hardening)
        if score > 0.9 and confidence > 0.8:
            # Shift towards Deontological/Duty pole mass and pin it
            self.posterior_alpha[0] += gain * 2.0
            _logger.info("Bayesian: Strong RLHF safety latch engaged (score=%.2f)", score)

        self.update_posterior_from_feedback(self.posterior_alpha)

    def evaluate(
        self,
        actions: list[CandidateAction],
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
        identity_deltas: Any = None,
        rlhf_features: Any = None
    ) -> EthicsMixtureResult:
        """Score actions using the current core strategy (Fixed or Posterior)."""
        return self.scorer.evaluate(
            actions, 
            scenario=scenario, 
            context=context, 
            signals=signals,
            identity_deltas=identity_deltas,
            rlhf_features=rlhf_features
        )

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
