"""Canonical weighted mixture module + compatibility shim."""

from src.modules import bayesian_engine as shim
from src.modules import weighted_ethics_scorer as canonical


def test_bayesian_engine_is_alias_of_weighted_ethics_scorer():
    assert canonical.BayesianEngine is canonical.WeightedEthicsScorer
    assert canonical.BayesianResult is canonical.EthicsMixtureResult


def test_bayesian_engine_shim_reexports_canonical():
    assert shim.BayesianEngine is canonical.WeightedEthicsScorer
    assert shim.BayesianResult is canonical.EthicsMixtureResult
    assert shim.CandidateAction is canonical.CandidateAction
    assert shim.DEFAULT_HYPOTHESIS_WEIGHTS is canonical.DEFAULT_HYPOTHESIS_WEIGHTS
