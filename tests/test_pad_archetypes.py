"""PAD + archetype mixture: numeric bounds and kernel wiring."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src.modules.bayesian_engine import CandidateAction
from src.modules.locus import LocusEvaluation
from src.modules.pad_archetypes import (
    PADArchetypeEngine,
    activation_from_sigma,
    dominance_from_locus,
    valence_from_moral_score,
)


def test_pad_components_clamped():
    assert 0.0 <= activation_from_sigma(0.2) <= 1.0
    assert 0.0 <= activation_from_sigma(0.8) <= 1.0
    assert 0.0 <= valence_from_moral_score(-1.0) <= 1.0
    assert 0.0 <= valence_from_moral_score(1.0) <= 1.0
    loc = LocusEvaluation(
        alpha=1.0,
        beta=1.0,
        dominant_locus="internal",
        action_confidence=0.5,
        attribution="",
        recommended_adjustment="",
    )
    assert dominance_from_locus(loc) == 1.0


def test_softmax_weights_sum_to_one():
    eng = PADArchetypeEngine(beta=4.0)
    loc = LocusEvaluation(
        alpha=1.0,
        beta=1.0,
        dominant_locus="balanced",
        action_confidence=0.5,
        attribution="",
        recommended_adjustment="",
    )
    out = eng.project(sigma=0.5, total_score=0.1, locus_eval=loc)
    s = sum(out.weights.values())
    assert abs(s - 1.0) < 1e-9
    assert out.dominant_archetype_id in out.weights


def test_kernel_populates_affect():
    kernel = EthicalKernel(variability=False, seed=42)
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
    d = kernel.process(
        scenario="test",
        place="here",
        signals=signals,
        context="everyday",
        actions=actions,
    )
    assert not d.blocked
    assert d.affect is not None
    assert len(d.affect.pad) == 3
    ep = kernel.memory.episodes[-1]
    assert ep.affect_pad == d.affect.pad
    assert ep.affect_weights == d.affect.weights
