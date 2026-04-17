"""SalienceMap: read-only attention weights; no pipeline change."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.weighted_ethics_scorer import BayesianResult, CandidateAction
from src.modules.ethical_poles import EthicalPoles
from src.modules.ethical_reflection import EthicalReflection
from src.modules.salience_map import SalienceMap, salience_to_llm_context
from src.modules.sympathetic import InternalState
from src.modules.uchi_soto import SocialEvaluation, TrustCircle


def _social() -> SocialEvaluation:
    return SocialEvaluation(
        circle=TrustCircle.SOTO_NEUTRO,
        trust=0.5,
        dialectic_active=False,
        openness_level=0.5,
        caution_level=0.3,
        recommended_response="",
        reasoning="",
    )


def test_salience_weights_sum_to_one():
    sm = SalienceMap()
    state = InternalState(sigma=0.5, mode="neutral", energy=1.0)
    signals = {"risk": 0.2, "hostility": 0.1}
    ref = EthicalReflection().reflect(
        EthicalPoles().evaluate(
            "act",
            "everyday",
            {"risk": 0.2, "benefit": 0.3, "third_party_vulnerability": 0.0, "legality": 1.0},
        ),
        BayesianResult(
            chosen_action=CandidateAction("a", "d", 0.5, 0.8),
            expected_impact=0.5,
            uncertainty=0.25,
            decision_mode="D_delib",
            pruned_actions=[],
            reasoning="r",
        ),
        {"mode": "D_delib"},
    )
    snap = sm.compute(signals, state, _social(), ref)
    assert abs(sum(snap.weights.values()) - 1.0) < 1e-6
    assert snap.dominant_focus in snap.weights


def test_salience_to_llm_empty():
    assert salience_to_llm_context(None) == ""


def test_kernel_has_salience():
    k = EthicalKernel(variability=False, seed=3)
    actions = [
        CandidateAction("act_civically", "x", estimated_impact=0.5, confidence=0.8),
        CandidateAction("observe", "y", estimated_impact=0.0, confidence=0.9),
    ]
    signals = {
        "risk": 0.15,
        "hostility": 0.0,
        "calm": 0.8,
        "vulnerability": 0.1,
        "legality": 1.0,
    }
    d = k.process(
        scenario="test",
        place="here",
        signals=signals,
        context="everyday",
        actions=actions,
    )
    assert d.salience is not None
    assert "risk" in d.salience.weights
