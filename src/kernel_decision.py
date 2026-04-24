"""
Batch moral-cycle result envelope (pre–tri-lobe ``KernelDecision`` shape).

Kept in a small module so formatters, audit, and the monolithic :mod:`src.ethical_kernel_batch`
graph share one definition without a ``kernel_legacy`` filename.
"""

from __future__ import annotations

from dataclasses import dataclass

from .modules.cognition.salience_map import SalienceSnapshot
from .modules.ethics.absolute_evil import AbsoluteEvilResult
from .modules.ethics.ethical_poles import TripartiteMoral
from .modules.ethics.ethical_reflection import ReflectionSnapshot
from .modules.ethics.pad_archetypes import AffectProjection
from .modules.ethics.weighted_ethics_scorer import EthicsMixtureResult
from .modules.safety.locus import LocusEvaluation
from .modules.social.uchi_soto import SocialEvaluation
from .modules.somatic.sympathetic import InternalState


@dataclass
class KernelDecision:
    """Complete result of a kernel decision (batch / ``process`` / ``aprocess``)."""

    # Identity
    scenario: str
    place: str

    # Pre-checks
    absolute_evil: AbsoluteEvilResult

    # Internal state
    sympathetic_state: InternalState

    # Additional modules
    social_evaluation: SocialEvaluation | None
    locus_evaluation: LocusEvaluation | None

    # Evaluation
    bayesian_result: EthicsMixtureResult | None
    moral: TripartiteMoral | None

    # Final decision
    final_action: str
    decision_mode: str
    blocked: bool = False
    block_reason: str = ""
    affect: AffectProjection | None = None
    reflection: ReflectionSnapshot | None = None
    salience: SalienceSnapshot | None = None

    # ADR 0012 — optional Bayesian mixture reporting (does not replace final_action by default)
    bma_win_probabilities: dict[str, float] | None = None
    bma_dirichlet_alpha: tuple[float, float, float] | None = None
    bma_n_samples: int | None = None
    mixture_posterior_alpha: tuple[float, float, float] | None = None
    feedback_consistency: str | None = None
    mixture_context_key: str | None = None  # ADR 0012 Level 3 — which context bucket α came from
    l0_integrity_hash: str | None = None  # Issue 6 — fingerprint of PreloadedBuffer
    l0_stable: bool = True  # Issue 6 — True if fingerprint matches boot state
    hierarchical_context_key: str | None = (
        None  # ADR 0013 — canonical context type used by hierarchical updater
    )
    applied_mixture_weights: tuple[float, float, float] | None = (
        None  # weights actually used in evaluate()
    )
    episode_id: str | None = None
