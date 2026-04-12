"""
Compatibility shim for :mod:`weighted_ethics_scorer`.

The implementation lives in ``weighted_ethics_scorer``; this module re-exports it so older
imports (``from src.modules.bayesian_engine import …``) keep working.

**Naming:** ``BayesianEngine`` / ``BayesianResult`` are **aliases** of the weighted mixture
scorer — not full Bayesian inference. Prefer importing from ``weighted_ethics_scorer`` in new
code. See [ADR 0009](../docs/adr/0009-ethical-mixture-scorer-naming.md).
"""

from __future__ import annotations

from .weighted_ethics_scorer import (
    DEFAULT_HYPOTHESIS_WEIGHTS,
    BayesianEngine,
    BayesianResult,
    CandidateAction,
    EthicsMixtureResult,
    PreArgmaxContextChannels,
    WeightedEthicsScorer,
    context_hypothesis_multipliers,
    pole_hypothesis_multipliers,
)

__all__ = [
    "DEFAULT_HYPOTHESIS_WEIGHTS",
    "BayesianEngine",
    "BayesianResult",
    "CandidateAction",
    "EthicsMixtureResult",
    "PreArgmaxContextChannels",
    "WeightedEthicsScorer",
    "context_hypothesis_multipliers",
    "pole_hypothesis_multipliers",
]
