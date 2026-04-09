"""EthicalReflection: second-order snapshot, no change to decision outcomes."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethical_reflection import EthicalReflection, reflection_to_llm_context
from src.modules.ethical_poles import EthicalPoles, PoleEvaluation, TripartiteMoral, Verdict
from src.modules.bayesian_engine import BayesianResult, CandidateAction
from src.kernel import EthicalKernel


def _make_moral(scores: list) -> TripartiteMoral:
    poles = ["compassionate", "conservative", "optimistic"]
    evs = []
    for pole, sc in zip(poles, scores):
        evs.append(PoleEvaluation(pole=pole, verdict=Verdict.GRAY_ZONE, score=sc, moral="m"))
    return TripartiteMoral(
        evaluations=evs,
        total_score=sum(scores) / 3,
        global_verdict=Verdict.GRAY_ZONE,
        narrative="n",
    )


def test_reflection_low_conflict_aligned_poles():
    er = EthicalReflection()
    moral = _make_moral([0.2, 0.25, 0.22])
    bayes = BayesianResult(
        chosen_action=CandidateAction("a", "d", 0.5, 0.8),
        expected_impact=0.5,
        uncertainty=0.2,
        decision_mode="D_delib",
        pruned_actions=[],
        reasoning="r",
    )
    r = er.reflect(moral, bayes, {"mode": "D_delib"})
    assert r.conflict_level == "low"
    assert r.pole_spread < 0.1
    assert r.strain_index >= 0.0


def test_reflection_high_conflict():
    er = EthicalReflection()
    moral = _make_moral([0.9, -0.8, 0.1])
    bayes = BayesianResult(
        chosen_action=CandidateAction("a", "d", 0.5, 0.8),
        expected_impact=0.5,
        uncertainty=0.5,
        decision_mode="gray_zone",
        pruned_actions=[],
        reasoning="r",
    )
    r = er.reflect(moral, bayes, {"mode": "gray_zone"})
    assert r.conflict_level == "high"
    assert r.pole_spread > 1.5


def test_reflection_to_llm_context_empty():
    assert reflection_to_llm_context(None) == ""


def test_kernel_populates_reflection():
    k = EthicalKernel(variability=False, seed=1)
    actions = [
        CandidateAction("act_civically", "x", estimated_impact=0.5, confidence=0.8),
        CandidateAction("observe", "y", estimated_impact=0.0, confidence=0.9),
    ]
    signals = {
        "risk": 0.1,
        "hostility": 0.0,
        "calm": 0.7,
        "vulnerability": 0.2,
        "legality": 1.0,
    }
    d = k.process(
        scenario="test",
        place="here",
        signals=signals,
        context="everyday",
        actions=actions,
    )
    assert not d.blocked
    assert d.reflection is not None
    assert d.reflection.conflict_level in ("low", "medium", "high")
    ctx = reflection_to_llm_context(d.reflection)
    assert d.reflection.conflict_level in ctx


def test_process_natural_passes_reflection_to_llm_local():
    k = EthicalKernel(variability=False, seed=2)
    decision, response, _ = k.process_natural(
        "Someone dropped a can on the sidewalk in front of me."
    )
    assert decision.reflection is not None
    assert "Reflection:" in response.inner_voice
    assert "Salience:" in response.inner_voice
