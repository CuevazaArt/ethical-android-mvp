"""Unit tests for :mod:`src.kernel_lobes.chat_turn_policy` (Module 0.1.3 extraction)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel_lobes.chat_turn_policy import (
    chat_turn_is_heavy,
    prioritized_principles_for_context,
)
from src.modules.cognition.llm_layer import LLMPerception


def _perception(**kwargs: float | str) -> LLMPerception:
    base = dict(
        risk=0.1,
        urgency=0.1,
        hostility=0.1,
        calm=0.5,
        vulnerability=0.2,
        legality=1.0,
        manipulation=0.1,
        familiarity=0.2,
        social_tension=0.2,
        suggested_context="everyday",
        summary="test",
    )
    base.update(kwargs)
    return LLMPerception(**base)


def test_chat_turn_is_heavy_risk_threshold() -> None:
    assert chat_turn_is_heavy(_perception(risk=0.5)) is True
    assert chat_turn_is_heavy(_perception(risk=0.49)) is False


def test_chat_turn_is_heavy_escalating_contexts() -> None:
    assert chat_turn_is_heavy(_perception(suggested_context="medical_emergency")) is True


def test_prioritized_principles_safety_first() -> None:
    profile, ordered = prioritized_principles_for_context(
        ["compassion", "no_harm"],
        {"arousal_band": "high", "planning_bias": "balanced"},
    )
    assert profile == "safety_first"
    assert ordered[0] == "no_harm"


def test_prioritized_principles_planning_first() -> None:
    profile, ordered = prioritized_principles_for_context(
        ["no_harm", "transparency"],
        {"arousal_band": "low", "planning_bias": "long_horizon_deliberation"},
    )
    assert profile == "planning_first"
    assert ordered[0] == "transparency"


def test_default_chat_light_actions_count() -> None:
    from src.kernel_lobes.chat_turn_policy import default_chat_light_actions

    a = default_chat_light_actions()
    assert len(a) == 2
    assert a[0].name == "converse_supportively"


def test_generic_actions_medical_vs_default() -> None:
    from src.kernel_lobes.chat_turn_policy import generic_chat_actions_for_suggested_context

    med = generic_chat_actions_for_suggested_context("medical_emergency")
    assert any(x.name == "assist_person" for x in med)
    every = generic_chat_actions_for_suggested_context("everyday_ethics")
    assert any(x.name == "act_civically" for x in every)


def test_candidate_actions_light_vs_heavy() -> None:
    from src.kernel_lobes.chat_turn_policy import candidate_actions_for_chat_turn

    p = _perception(suggested_context="medical_emergency")
    light = candidate_actions_for_chat_turn(p, heavy=False)
    assert len(light) == 2
    assert light[0].name == "converse_supportively"
    heavy = candidate_actions_for_chat_turn(p, heavy=True)
    assert any(x.name == "assist_person" for x in heavy)


def test_ethical_context_for_chat_turn() -> None:
    from src.kernel_lobes.chat_turn_policy import ethical_context_for_chat_turn

    p = _perception(suggested_context="medical_emergency")
    assert ethical_context_for_chat_turn(p, heavy=False) == "everyday"
    assert ethical_context_for_chat_turn(p, heavy=True) == "medical_emergency"
