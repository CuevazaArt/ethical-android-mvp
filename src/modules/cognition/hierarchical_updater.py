"""
Hierarchical context-dependent weight inference — **Level 3** of ADR 0013.

Maintains one :class:`FeedbackUpdater` per ``context_type`` plus a shared
**global** updater.  When operator feedback arrives for context ``C``:

1. The **global** updater processes it (shifts the shared prior for all contexts).
2. The **context-specific** updater for ``C`` processes it (shifts the local prior).

When a decision is needed for context ``C``:

- If ``context_counts[C] < KERNEL_HIERARCHICAL_MIN_LOCAL``: return the **global**
  posterior (Level 2 fallback — identical to pre-ADR-0013 behavior).
- Otherwise: blend global and local posterior means via the τ schedule::

      τ = τ_max · (1 − exp(−n_local / 3))
      posterior_mean(C) = (1 − τ) · global_mean + τ · local_mean(C)

  The blended mean is then projected to a Dirichlet α by multiplying by the
  global posterior concentration (Σ α_global).

**Context taxonomy** (from ADR 0013): ``resource_allocation``, ``promise_conflict``,
``confrontation``, ``emergency``, ``integrity``, ``relational``, ``general``.
Unknown context types are accepted and created on demand.

Env variables
-------------
- ``KERNEL_HIERARCHICAL_FEEDBACK`` — enable; default off.
- ``KERNEL_HIERARCHICAL_MIN_LOCAL`` — min feedback items per context before local
  posterior is used (default ``3``).
- ``KERNEL_HIERARCHICAL_TAU_MAX`` — ceiling blend fraction τ_max (default ``0.8``).

See also
--------
- :class:`~src.modules.feedback_mixture_updater.FeedbackUpdater` — Level 2 component.
- ADR 0013 — full design rationale and blending derivation.
"""

from __future__ import annotations

import math
import os
from dataclasses import dataclass
from typing import Any

from src.modules.cognition.feedback_mixture_updater import (
    FeedbackItem,
    FeedbackResult,
    FeedbackUpdater,
    build_scenario_candidates_map,
)

# ---------------------------------------------------------------------------
# Context taxonomy (ADR 0013 §Context type taxonomy)
# ---------------------------------------------------------------------------

KNOWN_CONTEXT_TYPES: frozenset[str] = frozenset(
    {
        "resource_allocation",
        "promise_conflict",
        "confrontation",
        "emergency",
        "integrity",
        "relational",
        "general",
    }
)

# Legacy context strings → canonical type (from ADR 0013 table)
CONTEXT_LEGACY_MAP: dict[str, str] = {
    "community": "resource_allocation",
    "everyday": "resource_allocation",
    "everyday_ethics": "relational",
    "integrity_loss": "promise_conflict",
    "hostile_interaction": "confrontation",
    "medical_emergency": "emergency",
    "android_damage": "integrity",
    "integrity": "integrity",
    "relational": "relational",
    "general": "general",
    "resource_allocation": "resource_allocation",
    "promise_conflict": "promise_conflict",
    "confrontation": "confrontation",
    "emergency": "emergency",
}


def canonical_context_type(raw: str | None) -> str:
    """Map a raw context string to its canonical bucket name.

    Falls back to ``"general"`` for ``None`` or unknown values.
    """
    if not raw:
        return "general"
    key = raw.strip().lower()
    return CONTEXT_LEGACY_MAP.get(key, key)  # accept novel types as-is


# ---------------------------------------------------------------------------
# τ blending schedule
# ---------------------------------------------------------------------------


def _tau(n_local: int, tau_max: float) -> float:
    """
    Sigmoid-like blend fraction increasing from 0 toward ``tau_max``.

    ``τ(n) = τ_max · (1 − exp(−n / 3))``

    At n=0: τ=0 (pure global).
    At n=3: τ≈0.50·τ_max.
    At n=10: τ≈0.96·τ_max.
    At n→∞: τ→τ_max (never fully ignores global).
    """
    return tau_max * (1.0 - math.exp(-n_local / 3.0))


def _blend_means(
    global_mean: list[float],
    local_mean: list[float],
    tau: float,
) -> list[float]:
    """Linear blend: ``(1-τ)·global + τ·local`` on the 3-simplex."""
    return [(1.0 - tau) * g + tau * loc for g, loc in zip(global_mean, local_mean)]


# ---------------------------------------------------------------------------
# HierarchicalUpdater
# ---------------------------------------------------------------------------


@dataclass
class HierarchicalSnapshot:
    """Serialisable state for :class:`HierarchicalUpdater`."""

    global_snapshot: dict[str, Any]
    context_snapshots: dict[str, dict[str, Any]]
    context_counts: dict[str, int]
    min_local_items: int
    tau_max: float
    initial_alpha: list[float]
    update_strength: float
    n_samples: int
    max_drift: float
    seed: int


class HierarchicalUpdater:
    """
    Level-3 hierarchical Dirichlet posterior over ethical mixture weights.

    Composes :class:`FeedbackUpdater` instances (one global + one per context
    type) and blends their posterior means when making decisions.

    Parameters
    ----------
    initial_alpha :
        Starting Dirichlet prior for all updaters.
    min_local_items :
        Minimum feedback items in a context bucket before the local posterior
        is blended in.  Below this count the global posterior is used as-is.
    tau_max :
        Upper bound on the blend fraction τ ∈ [0, τ_max].
    update_strength :
        Passed to each :class:`FeedbackUpdater`.
    n_samples :
        Inner MC samples per feedback item.
    max_drift :
        Genome guard: max L∞ drift of normalised posterior mean per axis.
    seed :
        Base RNG seed; context updaters use ``seed + hash(context_type) % 2^16``.
    """

    def __init__(
        self,
        initial_alpha: list[float] | None = None,
        *,
        min_local_items: int | None = None,
        tau_max: float | None = None,
        update_strength: float = 3.0,
        n_samples: int = 20_000,
        max_drift: float = 0.30,
        seed: int = 42,
    ) -> None:
        self._initial_alpha: list[float] = list(initial_alpha or [3.0, 3.0, 3.0])
        self.min_local_items: int = (
            min_local_items
            if min_local_items is not None
            else _env_int("KERNEL_HIERARCHICAL_MIN_LOCAL", 3)
        )
        self.tau_max: float = (
            tau_max if tau_max is not None else _env_float("KERNEL_HIERARCHICAL_TAU_MAX", 0.8)
        )
        self._update_strength = update_strength
        self._n_samples = n_samples
        self._max_drift = max_drift
        self._seed = seed

        self._global: FeedbackUpdater = self._make_updater(seed)
        self._contexts: dict[str, FeedbackUpdater] = {}
        self.context_counts: dict[str, int] = {}

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_updater(self, seed: int) -> FeedbackUpdater:
        return FeedbackUpdater(
            initial_alpha=list(self._initial_alpha),
            max_drift=self._max_drift,
            update_strength=self._update_strength,
            n_samples=self._n_samples,
            seed=seed,
        )

    def _context_updater(self, ctype: str) -> FeedbackUpdater:
        """Return (creating if needed) the local updater for ``ctype``."""
        if ctype not in self._contexts:
            # Deterministic seed per context type for reproducibility
            ctx_seed = (self._seed + abs(hash(ctype))) % (2**16)
            self._contexts[ctype] = self._make_updater(ctx_seed)
            self.context_counts[ctype] = 0
        return self._contexts[ctype]

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def ingest_feedback(
        self,
        feedbacks: list[FeedbackItem],
        scenario_candidates: dict[int, dict[str, dict[str, float]]],
        *,
        stop_on_infeasible: bool = False,
    ) -> FeedbackResult:
        """
        Process each feedback item through the global updater **and** through
        the local updater for its ``context_type``.

        Returns the :class:`FeedbackResult` from the **global** updater
        (canonical posterior for reporting and kernel integration).  Per-context
        posteriors are stored internally and available via
        :meth:`active_alpha_for_context`.

        Parameters
        ----------
        feedbacks :
            Ordered list of operator feedback items.
        scenario_candidates :
            ``{scenario_id: {action_name: {util, deon, virtue}}}``.
        stop_on_infeasible :
            If True, abort on first infeasible global update.
        """
        global_result = self._global.ingest_feedback(
            feedbacks, scenario_candidates, stop_on_infeasible=stop_on_infeasible
        )

        for fb in feedbacks:
            ctype = canonical_context_type(fb.context_type)
            local_u = self._context_updater(ctype)
            cands = scenario_candidates.get(fb.scenario_id)
            if cands is None:
                continue
            local_u.update_from_feedback(fb, cands)
            self.context_counts[ctype] = self.context_counts.get(ctype, 0) + 1

        return global_result

    def active_alpha_for_context(
        self,
        context_type: str | None,
    ) -> list[float]:
        """
        Return the blended Dirichlet α for the given raw context string.

        If the canonical context has fewer than ``min_local_items`` feedback
        items the **global** alpha is returned unchanged.  Otherwise the
        τ-blended mean is projected back to α by preserving global concentration.
        """
        ctype = canonical_context_type(context_type)
        n_local = self.context_counts.get(ctype, 0)

        if n_local < self.min_local_items or ctype not in self._contexts:
            return list(self._global.alpha)

        tau = _tau(n_local, self.tau_max)
        global_mean = self._global.posterior_mean()
        local_mean = self._contexts[ctype].posterior_mean()
        blended_mean = _blend_means(global_mean, local_mean, tau)

        # Normalise (blended_mean may not sum to 1.0 due to float rounding)
        total_mean = sum(blended_mean)
        if total_mean <= 0.0:
            return list(self._global.alpha)
        blended_norm = [m / total_mean for m in blended_mean]

        # Project to Dirichlet α: preserve global concentration (Σ α_global)
        global_concentration = sum(self._global.alpha)
        return [m * global_concentration for m in blended_norm]

    def active_posterior_mean(self, context_type: str | None) -> list[float]:
        """Normalised posterior mean for the given context (for kernel weight setting)."""
        alpha = self.active_alpha_for_context(context_type)
        total = sum(alpha)
        if total <= 0.0:
            return [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]
        return [a / total for a in alpha]

    def context_summary(self) -> dict[str, Any]:
        """Per-context stats useful for diagnostics and audit."""
        rows: list[dict[str, Any]] = []
        for ctype, n in sorted(self.context_counts.items()):
            alpha = self.active_alpha_for_context(ctype)
            total = sum(alpha)
            tau = _tau(n, self.tau_max) if n >= self.min_local_items else 0.0
            rows.append(
                {
                    "context_type": ctype,
                    "n_feedback": n,
                    "active": n >= self.min_local_items,
                    "tau": round(tau, 4),
                    "posterior_mean": [round(a / total, 4) for a in alpha],
                }
            )
        return {
            "global_alpha": [round(a, 4) for a in self._global.alpha],
            "global_mean": [round(m, 4) for m in self._global.posterior_mean()],
            "min_local_items": self.min_local_items,
            "tau_max": self.tau_max,
            "contexts": rows,
        }

    # ------------------------------------------------------------------
    # Persistence — snapshot / restore
    # ------------------------------------------------------------------

    def snapshot(self) -> dict[str, Any]:
        """Return a JSON-serialisable snapshot of the full hierarchical state."""
        return {
            "schema": "hierarchical_updater_v1",
            "global_snapshot": self._global.snapshot(),
            "context_snapshots": {k: u.snapshot() for k, u in self._contexts.items()},
            "context_counts": dict(self.context_counts),
            "min_local_items": self.min_local_items,
            "tau_max": self.tau_max,
            "initial_alpha": list(self._initial_alpha),
            "update_strength": self._update_strength,
            "n_samples": self._n_samples,
            "max_drift": self._max_drift,
            "seed": self._seed,
        }

    @classmethod
    def restore(cls, data: dict[str, Any]) -> HierarchicalUpdater:
        """Reconstruct from a :meth:`snapshot` dict."""
        obj = cls(
            initial_alpha=data["initial_alpha"],
            min_local_items=data["min_local_items"],
            tau_max=data["tau_max"],
            update_strength=data["update_strength"],
            n_samples=int(data.get("n_samples", 20_000)),
            max_drift=data["max_drift"],
            seed=data["seed"],
        )
        obj._global = FeedbackUpdater.restore(data["global_snapshot"])
        for ctype, snap in data["context_snapshots"].items():
            obj._contexts[ctype] = FeedbackUpdater.restore(snap)
        obj.context_counts = dict(data["context_counts"])
        return obj

    # ------------------------------------------------------------------
    # Environment helpers
    # ------------------------------------------------------------------

    @staticmethod
    def enabled_from_env() -> bool:
        """True when ``KERNEL_HIERARCHICAL_FEEDBACK`` is truthy."""
        v = os.environ.get("KERNEL_HIERARCHICAL_FEEDBACK", "").strip().lower()
        return v in ("1", "true", "yes", "on")


# ---------------------------------------------------------------------------
# Module-level convenience
# ---------------------------------------------------------------------------


def _env_int(name: str, default: int) -> int:
    try:
        return max(0, int(os.environ.get(name, str(default)).strip()))
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)).strip())
    except ValueError:
        return default


def hierarchical_enabled() -> bool:
    """Convenience alias for :meth:`HierarchicalUpdater.enabled_from_env`."""
    return HierarchicalUpdater.enabled_from_env()


def load_hierarchical_updater_from_feedback(
    feedback_items: list[FeedbackItem],
    scenario_ids: list[int],
    *,
    initial_alpha: list[float] | None = None,
    update_strength: float = 3.0,
    n_samples: int = 20_000,
    max_drift: float = 0.30,
    seed: int = 42,
    min_local_items: int | None = None,
    tau_max: float | None = None,
) -> tuple[HierarchicalUpdater, FeedbackResult | None]:
    """
    Build and populate a :class:`HierarchicalUpdater` from a list of feedback
    items.  Returns ``(updater, None)`` if scenario candidates cannot be
    resolved (no ``hypothesis_override`` on all candidates).

    This is the **offline** entry point used by the LOO calibration script
    and operator tooling.
    """
    cmap = build_scenario_candidates_map(scenario_ids)
    if cmap is None:
        return HierarchicalUpdater(
            initial_alpha=initial_alpha,
            min_local_items=min_local_items,
            tau_max=tau_max,
            update_strength=update_strength,
            n_samples=n_samples,
            max_drift=max_drift,
            seed=seed,
        ), None

    updater = HierarchicalUpdater(
        initial_alpha=initial_alpha,
        min_local_items=min_local_items,
        tau_max=tau_max,
        update_strength=update_strength,
        n_samples=n_samples,
        max_drift=max_drift,
        seed=seed,
    )
    result = updater.ingest_feedback(feedback_items, cmap)
    return updater, result


__all__ = [
    "CONTEXT_LEGACY_MAP",
    "KNOWN_CONTEXT_TYPES",
    "HierarchicalUpdater",
    "HierarchicalSnapshot",
    "canonical_context_type",
    "hierarchical_enabled",
    "load_hierarchical_updater_from_feedback",
]
