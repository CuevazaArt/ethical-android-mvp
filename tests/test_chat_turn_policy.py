"""Regression tests for ``kernel_lobes.chat_turn_policy`` (kernel chat-turn routing helpers)."""

from __future__ import annotations

import pytest

from src.kernel_lobes.chat_turn_policy import (
    candidate_actions_for_chat_turn,
    chat_turn_is_heavy,
    default_chat_light_actions,
    ethical_context_for_chat_turn,
    prioritized_principles_for_context,
)
from src.kernel_lobes.chat_turn_signal_routing import (
    coercion_uncertainty_raw,
    merge_chat_turn_signals_for_ethical_core,
)
from src.modules.llm_layer import LLMPerception


def _minimal_perception(
    *,
    risk: float = 0.1,
    suggested_context: str = "everyday",
) -> LLMPerception:
    return LLMPerception(
        risk=risk,
        urgency=0.1,
        hostility=0.1,
        calm=0.5,
        vulnerability=0.2,
        legality=0.7,
        manipulation=0.1,
        familiarity=0.5,
        social_tension=0.2,
        suggested_context=suggested_context,
        summary="unit",
    )


def test_null_perception_heavy_and_context_defensive() -> None:
    assert chat_turn_is_heavy(None) is False
    assert ethical_context_for_chat_turn(None, heavy=False) == "everyday"
    assert ethical_context_for_chat_turn(None, heavy=True) == "everyday"
    light = candidate_actions_for_chat_turn(None, heavy=False)
    assert light == default_chat_light_actions()
    heavy_actions = candidate_actions_for_chat_turn(None, heavy=True)
    assert heavy_actions == default_chat_light_actions()


def test_prioritized_principles_non_mapping_profile_falls_back() -> None:
    active = ["no_harm", "compassion"]
    profile, ordered = prioritized_principles_for_context(active, None)
    assert profile == "balanced"
    assert "no_harm" in ordered and "compassion" in ordered
    profile2, ordered2 = prioritized_principles_for_context(active, [])
    assert profile2 == "balanced"
    assert ordered2 == ordered


def test_candidate_actions_heavy_uses_scenario_list() -> None:
    p = _minimal_perception(
        risk=0.9,
        suggested_context="medical_emergency",
    )
    actions = candidate_actions_for_chat_turn(p, heavy=True)
    names = {a.name for a in actions}
    assert "assist_person" in names


def test_ethical_context_heavy_uses_suggested_context() -> None:
    p = _minimal_perception(suggested_context="violent_crime")
    assert ethical_context_for_chat_turn(p, heavy=True) == "violent_crime"
    assert ethical_context_for_chat_turn(p, heavy=False) == "everyday"


def test_merge_signals_injects_coercion_uncertainty() -> None:
    p = _minimal_perception()
    p.coercion_report = {"uncertainty": 0.42}
    base = {"urgency": 0.2, "perception_uncertainty": 0.1}
    out = merge_chat_turn_signals_for_ethical_core(base, p)
    assert out["perception_uncertainty"] == pytest.approx(0.42)
    assert coercion_uncertainty_raw(p) == 0.42


def test_merge_signals_temporal_eta_boost(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_TEMPORAL_ETA_MODULATION", "1")
    monkeypatch.setenv("KERNEL_TEMPORAL_REFERENCE_ETA_S", "300")

    class _TC:
        eta_seconds = 60.0
        battery_horizon_state = "nominal"

    p = _minimal_perception()
    p.temporal_context = _TC()
    base = {"urgency": 0.1}
    out = merge_chat_turn_signals_for_ethical_core(base, p)
    assert out["urgency"] > 0.1
