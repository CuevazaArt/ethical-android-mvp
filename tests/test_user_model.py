"""User model (ToM light) tracker."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMPerception
from src.modules.user_model import UserModelTracker


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
        suggested_context="everyday_ethics",
        summary="x",
    )
    defaults.update(kwargs)
    return LLMPerception(**defaults)


def test_frustration_streak_rises_on_hostility():
    m = UserModelTracker()
    for _ in range(4):
        m.update(_p(hostility=0.7, calm=0.2), "distant_soto", blocked=False)
    assert m.frustration_streak >= 3
    assert "tension" in m.guidance_for_communicate().lower()


def test_public_dict_has_circle():
    m = UserModelTracker()
    m.update(_p(), "trusted_uchi", blocked=False)
    d = m.to_public_dict()
    assert d["last_circle"] == "trusted_uchi"


def test_premise_concern_streak_and_guidance():
    m = UserModelTracker()
    m.note_premise_advisory("none")
    assert m.premise_concern_streak == 0
    m.note_premise_advisory("suspect_health_harm")
    m.note_premise_advisory("suspect_health_harm")
    assert m.premise_concern_streak == 2
    g = m.guidance_for_communicate().lower()
    assert "epistemic" in g or "premise" in g
    m.note_premise_advisory("none")
    assert m.premise_concern_streak == 1


def test_public_dict_includes_premise_streak():
    m = UserModelTracker()
    m.note_premise_advisory("suspect_chemical_harm")
    d = m.to_public_dict()
    assert d["premise_concern_streak"] == 1
