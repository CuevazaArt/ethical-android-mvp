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
