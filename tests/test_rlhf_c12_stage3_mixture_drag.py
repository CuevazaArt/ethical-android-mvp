"""Plan C.1.2 — RLHF metrics measurably drag Stage-3 (Bayesian mixture) scoring."""

from __future__ import annotations

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.bayesian_engine import BayesianInferenceEngine, BayesianMode
from src.modules.weighted_ethics_scorer import CandidateAction


def test_rlhf_modulation_changes_applied_mixture_weights_in_stage3(monkeypatch):
    """
    After MalAbs-shaped RLHF features nudge Dirichlet mass, ``evaluate`` must expose different
    ``applied_mixture_weights`` (kernel Stage 3), proving downstream pole inputs can diverge.
    """
    monkeypatch.setenv("KERNEL_RLHF_MODULATE_BAYESIAN", "1")
    monkeypatch.setenv("KERNEL_RLHF_MODULATION_SCALE", "4.0")
    eng = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
    actions = [
        CandidateAction(
            name="cooperate",
            description="Aid a neighbor within policy",
            estimated_impact=0.72,
            confidence=0.88,
        ),
        CandidateAction(
            name="defer",
            description="Wait for more information",
            estimated_impact=0.68,
            confidence=0.88,
        ),
    ]
    r0 = eng.evaluate(actions, scenario="c12_rlhf", context="unit", signals={})
    w0 = r0.applied_mixture_weights
    assert w0 is not None

    eng.maybe_modulate_from_malabs_rlhf_features(
        {
            "embedding_sim": 0.97,
            "lexical_score": 0.96,
            "perception_confidence": 1.0,
            "is_ambiguous": False,
            "category_id": 2,
        }
    )

    r1 = eng.evaluate(actions, scenario="c12_rlhf", context="unit", signals={})
    w1 = r1.applied_mixture_weights
    assert w1 is not None
    assert w0 != w1
    assert not np.allclose(np.array(w0, dtype=np.float64), np.array(w1, dtype=np.float64), atol=1e-5)


def test_rlhf_modulation_no_drag_when_flag_off(monkeypatch):
    monkeypatch.delenv("KERNEL_RLHF_MODULATE_BAYESIAN", raising=False)
    eng = BayesianInferenceEngine(mode=BayesianMode.POSTERIOR_DRIVEN)
    actions = [
        CandidateAction(name="a", description="x", estimated_impact=0.5, confidence=0.8),
    ]
    w0 = eng.evaluate(actions, scenario="s", context="c", signals={}).applied_mixture_weights
    eng.maybe_modulate_from_malabs_rlhf_features(
        {
            "embedding_sim": 1.0,
            "lexical_score": 1.0,
            "perception_confidence": 1.0,
            "is_ambiguous": False,
            "category_id": 1,
        }
    )
    w1 = eng.evaluate(actions, scenario="s", context="c", signals={}).applied_mixture_weights
    assert w0 == w1
