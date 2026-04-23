"""Tests for ``kernel_lobes.perception_signals_policy`` and ``signal_coercion``."""

from __future__ import annotations

from src.kernel_lobes.perception_signals_policy import base_signals_from_llm_perception
from src.kernel_lobes.signal_coercion import safe_signal_scalar
from src.modules.llm_layer import LLMPerception


def test_safe_signal_scalar_invalid_defaults() -> None:
    assert safe_signal_scalar(None) == 0.0
    assert safe_signal_scalar("x") == 0.0
    assert safe_signal_scalar(float("nan")) == 0.0
    assert safe_signal_scalar(1.25) == 1.25


def test_base_signals_coerce_nan_perception_fields() -> None:
    p = LLMPerception(
        risk=float("nan"),
        urgency=0.2,
        hostility=0.1,
        calm=0.5,
        vulnerability=0.0,
        legality=0.5,
        manipulation=0.0,
        familiarity=0.5,
        social_tension=float("inf"),
        suggested_context="everyday",
        summary="x",
    )
    out = base_signals_from_llm_perception(p)
    assert out["risk"] == 0.0
    assert out["social_tension"] == 0.0
    assert out["urgency"] == 0.2
