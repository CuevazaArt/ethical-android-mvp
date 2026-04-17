"""Subjective clock (cronobiología MVP)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMPerception
from src.modules.subjective_time import SubjectiveClock


def _p() -> LLMPerception:
    return LLMPerception(
        risk=0.1,
        urgency=0.2,
        hostility=0.1,
        calm=0.7,
        vulnerability=0.0,
        legality=1.0,
        manipulation=0.1,
        familiarity=0.5,
        suggested_context="everyday_ethics",
        summary="hi",
    )


def test_clock_ticks_and_exposes_json():
    c = SubjectiveClock()
    c.tick(_p())
    d = c.to_public_dict()
    assert d["turn_index"] == 1
    assert "stimulus_ema" in d
    assert "boredom_hint" in d
