"""User model Phase A: cognitive pattern, risk band, judicial tone lines."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.llm_layer import LLMPerception
from src.modules.social.user_model import (
    COGNITIVE_HOSTILE_ATTRIBUTION,
    COGNITIVE_PREMISE_RIGIDITY,
    COGNITIVE_URGENCY_AMPLIFICATION,
    RISK_HIGH,
    UserModelTracker,
)


def _p(**kwargs) -> LLMPerception:
    defaults = dict(
        risk=0.1,
        urgency=0.2,
        hostility=0.1,
        calm=0.6,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.1,
        familiarity=0.5,
        social_tension=0.0,
        suggested_context="everyday_ethics",
        summary="x",
    )
    defaults.update(kwargs)
    return LLMPerception(**defaults)


def test_premise_rigidity_pattern():
    m = UserModelTracker()
    m.note_premise_advisory("suspect_health_harm")
    m.note_premise_advisory("suspect_health_harm")
    m.note_judicial_escalation(0, 2)
    m.update(_p(), "neutral_soto", blocked=False, premise_flag="suspect_health_harm")
    assert m.cognitive_pattern == COGNITIVE_PREMISE_RIGIDITY


def test_hostile_attribution_pattern():
    m = UserModelTracker()
    m.note_judicial_escalation(0, 2)
    m.update(_p(hostility=0.7, calm=0.3), "distant_soto", blocked=False)
    m.update(_p(hostility=0.7, calm=0.3), "distant_soto", blocked=False)
    assert m.cognitive_pattern == COGNITIVE_HOSTILE_ATTRIBUTION


def test_urgency_amplification_pattern():
    m = UserModelTracker()
    m.note_judicial_escalation(0, 2)
    m.update(
        _p(urgency=0.7, manipulation=0.6, calm=0.4),
        "neutral_soto",
        blocked=False,
    )
    assert m.cognitive_pattern == COGNITIVE_URGENCY_AMPLIFICATION


def test_risk_high_from_judicial_strikes():
    m = UserModelTracker()
    m.note_judicial_escalation(1, 2)
    m.update(_p(hostility=0.1, calm=0.7), "neutral_soto", blocked=False)
    assert m.risk_band == RISK_HIGH


def test_guidance_order_risk_before_judicial():
    m = UserModelTracker()
    m.note_judicial_escalation(1, 2)
    m.update(_p(hostility=0.1, calm=0.7), "neutral_soto", blocked=False)
    g = m.guidance_for_communicate()
    assert "Risk profile" in g
    assert "Judicial escalation" in g
    assert g.index("Risk profile") < g.index("Judicial escalation")


def test_guidance_includes_cognitive_when_not_none():
    m = UserModelTracker()
    m.note_judicial_escalation(0, 2)
    m.update(
        _p(urgency=0.7, manipulation=0.6, calm=0.4),
        "neutral_soto",
        blocked=False,
    )
    g = m.guidance_for_communicate().lower()
    assert "interaction pattern" in g


def test_public_dict_enrichment_fields():
    m = UserModelTracker()
    m.note_judicial_escalation(0, 2)
    m.update(_p(), "trusted_uchi", blocked=False)
    d = m.to_public_dict()
    assert d["cognitive_pattern"] == "none"
    assert d["risk_band"] in ("low", "medium", "high")
    assert "escalation_strikes" in d
    assert "escalation_threshold" in d
    assert "judicial_phase" in d


def test_guidance_includes_deferred_tone_when_phase_set():
    m = UserModelTracker()
    m.note_judicial_escalation(1, 2)
    m.judicial_phase = "escalation_deferred"
    m.update(_p(hostility=0.1, calm=0.7), "neutral_soto", blocked=False)
    g = m.guidance_for_communicate().lower()
    assert "deferred" in g
    assert "procedural" in g
