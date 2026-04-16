"""
Hierarchical context-dependent Bayesian weight inference for ethical mixture scorer (ADR 0013 Level 3).

Maintains **per-context** Dirichlet posteriors, each updated independently from operator feedback.
Global posterior (Level 2) is always updated; context-specific posteriors are created on demand.

**Blending rule**: For context type C with n local feedback items:
- If n < min_local_items (default 3): return global posterior
- Otherwise: blend global_mean and local_mean via τ-weighted schedule, re-concentrate

**τ schedule**: τ(n) = τ_max × (1 - exp(-n/3))
- n=0: τ=0 (pure global)
- n=3: τ≈0.50
- n→∞: τ→τ_max (default 0.8, never fully ignores global)

Environment variables:
- KERNEL_HIERARCHICAL_FEEDBACK: Enable Level 3 (default off)
- KERNEL_HIERARCHICAL_MIN_LOCAL: Min items before blending (default 3)
- KERNEL_HIERARCHICAL_TAU_MAX: Max blend fraction (default 0.8)
"""

from __future__ import annotations

import logging
import math
import os
from dataclasses import dataclass, field
from typing import Any

from .feedback_mixture_updater import FeedbackItem, FeedbackUpdater

logger = logging.getLogger(__name__)

# Canonical context types (from ADR 0013)
KNOWN_CONTEXT_TYPES = frozenset({
    "resource_allocation",
    "promise_conflict",
    "confrontation",
    "emergency",
    "integrity",
    "relational",
    "general",
})

# Legacy context name mappings → canonical
CONTEXT_LEGACY_MAP: dict[str, str] = {
    "community": "resource_allocation",
    "everyday": "relational",
    "collaborative": "relational",
    "hostile_interaction": "confrontation",
    "hostile": "confrontation",
    "crisis": "emergency",
    "deliberation": "promise_conflict",
    "pedagogical": "promise_conflict",
}


def canonical_context_type(raw: str | None) -> str:
    """Map raw context name → canonical type. Defaults to 'general'."""
    if not raw:
        return "general"
    raw_lower = raw.lower().strip()
    if raw_lower in KNOWN_CONTEXT_TYPES:
        return raw_lower
    if raw_lower in CONTEXT_LEGACY_MAP:
        return CONTEXT_LEGACY_MAP[raw_lower]
    return "general"


def _tau(n: int, tau_max: float = 0.8) -> float:
    """Blending schedule: τ(n) = τ_max × (1 - exp(-n/3))."""
    if n <= 0:
        return 0.0
    return tau_max * (1.0 - math.exp(-n / 3.0))


def _blend_means(global_mean: list[float], local_mean: list[float], tau: float) -> list[float]:
    """Blend posterior means: (1-τ)×global + τ×local."""
    return [(1.0 - tau) * g + tau * l for g, l in zip(global_mean, local_mean)]


def _reproject_to_alpha(blended_mean: list[float], global_concentration: float) -> list[float]:
    """Re-concentrate blended mean to match global concentration."""
    total = sum(blended_mean)
    if total <= 0:
        return [global_concentration / 3.0] * 3
    normalized = [m / total for m in blended_mean]
    return [n * global_concentration for n in normalized]


@dataclass
class HierarchicalFeedbackResult:
    """Result of hierarchical feedback update."""
    global_alpha: list[float]
    context_alphas: dict[str, list[float]]  # per-context posteriors
    active_context_type: str  # canonical type for this tick
    active_alpha: list[float]  # blended α for active context
    global_consistency: str  # "compatible" | "contradictory" | "insufficient"
    per_context_satisfaction: dict[str, float]  # p(all satisfied) per context
    context_counts: dict[str, int]  # feedback items per context
    n_feedback_items: int
    log: list[dict[str, Any]] = field(default_factory=list)


class HierarchicalUpdater:
    """
    Maintains hierarchical Dirichlet posteriors: one global, one per context type.

    Each FeedbackUpdater updates independently. When a decision is needed for context C:
    - If C has < min_local_items feedback: use global α
    - Otherwise: blend global α + local α via τ-weighted schedule
    """

    def __init__(
        self,
        initial_alpha: list[float] | None = None,
        max_drift: float = 0.30,
        update_strength: float = 3.0,
        n_samples: int = 20_000,
        seed: int = 42,
        min_local_items: int = 3,
        tau_max: float = 0.8,
    ):
        """
        Initialize global + per-context updaters.

        Args:
            initial_alpha: Dirichlet prior for all updaters (default [3,3,3])
            max_drift: Max drift per axis for drift guard
            update_strength: Multiplier for α nudges from feedback
            n_samples: Monte Carlo sample count per update
            seed: RNG seed
            min_local_items: Min feedback items for context before blending (default 3)
            tau_max: Max blending fraction τ (default 0.8)
        """
        self.global_updater = FeedbackUpdater(
            initial_alpha=initial_alpha,
            max_drift=max_drift,
            update_strength=update_strength,
            n_samples=n_samples,
            seed=seed,
        )
        self.context_updaters: dict[str, FeedbackUpdater] = {
            ctx_type: FeedbackUpdater(
                initial_alpha=initial_alpha,
                max_drift=max_drift,
                update_strength=update_strength,
                n_samples=n_samples,
                seed=seed + i,  # Different seed per context
            )
            for i, ctx_type in enumerate(sorted(KNOWN_CONTEXT_TYPES))
        }
        self.context_counts: dict[str, int] = {ctx_type: 0 for ctx_type in KNOWN_CONTEXT_TYPES}
        self.min_local_items = min_local_items
        self.tau_max = tau_max
        self._seed = int(seed)
        self._feedback_log: list[dict[str, Any]] = []

    def ingest_feedback(
        self,
        feedbacks: list[FeedbackItem],
        scenario_candidates: dict[int, dict[str, dict[str, float]]],
        *,
        stop_on_infeasible: bool = True,
    ) -> HierarchicalFeedbackResult:
        """
        Update both global and per-context Dirichlet posteriors.

        Args:
            feedbacks: List of feedback items (each with scenario_id, preferred_action, context_type)
            scenario_candidates: Map of scenario_id → {action_name: {util, deon, virtue}}
            stop_on_infeasible: Stop on first infeasible feedback

        Returns:
            HierarchicalFeedbackResult with global α, per-context αs, and satisfaction metrics
        """
        log: list[dict[str, Any]] = []

        # Update global updater (Level 2)
        global_result = self.global_updater.ingest_feedback(
            feedbacks,
            scenario_candidates,
            stop_on_infeasible=stop_on_infeasible,
        )
        log.append({"global_update": global_result.consistency})

        # Segregate feedbacks by canonical context type
        context_feedbacks: dict[str, list[FeedbackItem]] = {ctx_type: [] for ctx_type in KNOWN_CONTEXT_TYPES}
        for fb in feedbacks:
            ctx_type = canonical_context_type(fb.context_type)
            context_feedbacks[ctx_type].append(fb)
            self.context_counts[ctx_type] += 1

        # Update per-context updaters (only those with feedback)
        per_context_satisfaction: dict[str, float] = {}
        for ctx_type, ctx_items in context_feedbacks.items():
            if not ctx_items:
                continue
            ctx_result = self.context_updaters[ctx_type].ingest_feedback(
                ctx_items,
                scenario_candidates,
                stop_on_infeasible=stop_on_infeasible,
            )
            per_context_satisfaction[ctx_type] = float(ctx_result.p_all_satisfied)
            log.append({
                "context": ctx_type,
                "update": ctx_result.consistency,
                "p_satisfied": ctx_result.p_all_satisfied,
                "n_items": len(ctx_items),
            })

        # Prepare per-context alphas for output
        context_alphas: dict[str, list[float]] = {
            ctx_type: list(self.context_updaters[ctx_type].alpha)
            for ctx_type in KNOWN_CONTEXT_TYPES
        }

        self._feedback_log.extend(log)

        return HierarchicalFeedbackResult(
            global_alpha=list(self.global_updater.alpha),
            context_alphas=context_alphas,
            active_context_type="general",  # Placeholder; set by caller if needed
            active_alpha=list(self.global_updater.alpha),  # Placeholder; use active_alpha_for_context()
            global_consistency=global_result.consistency,
            per_context_satisfaction=per_context_satisfaction,
            context_counts=dict(self.context_counts),
            n_feedback_items=len(feedbacks),
            log=log,
        )

    def active_alpha_for_context(self, context_type: str | None) -> list[float]:
        """
        Return blended α for given context type.

        If context has < min_local_items feedback: return global α.
        Otherwise: blend global_mean + local_mean via τ schedule, re-concentrate.

        Args:
            context_type: Raw context type (will be canonicalized)

        Returns:
            Blended Dirichlet α for this context
        """
        canonical_type = canonical_context_type(context_type)
        n_local = self.context_counts.get(canonical_type, 0)

        # Fallback: not enough local feedback
        if n_local < self.min_local_items:
            return list(self.global_updater.alpha)

        # Compute blending
        global_mean = self.global_updater.posterior_mean()
        local_mean = self.context_updaters[canonical_type].posterior_mean()
        tau = _tau(n_local, tau_max=self.tau_max)
        blended_mean = _blend_means(global_mean, local_mean, tau)
        global_concentration = self.global_updater.posterior_concentration()

        # Re-project to alpha preserving global concentration
        blended_alpha = _reproject_to_alpha(blended_mean, global_concentration)
        return blended_alpha

    def snapshot(self) -> dict[str, Any]:
        """Serialize state for persistence."""
        return {
            "global_updater": self.global_updater.snapshot(),
            "context_updaters": {
                ctx_type: updater.snapshot()
                for ctx_type, updater in self.context_updaters.items()
            },
            "context_counts": dict(self.context_counts),
            "min_local_items": self.min_local_items,
            "tau_max": self.tau_max,
            "feedback_log": list(self._feedback_log),
        }

    @classmethod
    def restore(cls, data: dict[str, Any]) -> HierarchicalUpdater:
        """Deserialize from snapshot."""
        instance = cls(
            initial_alpha=[3.0, 3.0, 3.0],  # Defaults; will be overwritten
            min_local_items=data.get("min_local_items", 3),
            tau_max=data.get("tau_max", 0.8),
        )
        # Restore global updater
        instance.global_updater = FeedbackUpdater.restore(data["global_updater"])
        # Restore per-context updaters
        for ctx_type in KNOWN_CONTEXT_TYPES:
            if ctx_type in data.get("context_updaters", {}):
                instance.context_updaters[ctx_type] = FeedbackUpdater.restore(
                    data["context_updaters"][ctx_type]
                )
        # Restore context counts
        instance.context_counts = dict(data.get("context_counts", {ctx_type: 0 for ctx_type in KNOWN_CONTEXT_TYPES}))
        instance._feedback_log = list(data.get("feedback_log", []))
        return instance
