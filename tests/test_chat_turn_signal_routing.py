"""Focused tests for ``kernel_lobes.chat_turn_signal_routing`` (Block 0.1.3 / 8.1.1)."""

from __future__ import annotations

import math

import pytest

from src.kernel_lobes.chat_turn_signal_routing import (
    coercion_uncertainty_raw,
    merge_chat_turn_signals_for_ethical_core,
)
from src.modules.llm_layer import LLMPerception


def _p() -> LLMPerception:
    return LLMPerception(
        risk=0.1,
        urgency=0.1,
        hostility=0.1,
        calm=0.5,
        vulnerability=0.2,
        legality=0.7,
        manipulation=0.1,
        familiarity=0.5,
        social_tension=0.2,
        suggested_context="everyday",
        summary="t",
    )


def test_coercion_uncertainty_raw_dict_rejects_invalid() -> None:
    p = _p()
    p.coercion_report = {"uncertainty": float("nan")}
    assert coercion_uncertainty_raw(p) is None
    p.coercion_report = {"uncertainty": None}
    assert coercion_uncertainty_raw(p) is None
    p.coercion_report = {"uncertainty": True}
    assert coercion_uncertainty_raw(p) is None


def test_coercion_uncertainty_raw_callable_object() -> None:
    class _CR:
        def uncertainty(self) -> float:
            return 0.35

    p = _p()
    p.coercion_report = _CR()
    assert coercion_uncertainty_raw(p) == pytest.approx(0.35)


def test_coercion_uncertainty_raw_callable_rejects_bool() -> None:
    class _CR:
        def uncertainty(self) -> bool:
            return True

    p = _p()
    p.coercion_report = _CR()
    assert coercion_uncertainty_raw(p) is None


def test_coercion_uncertainty_raw_callable_returns_non_finite() -> None:
    class _CR:
        def uncertainty(self) -> float:
            return float("inf")

    p = _p()
    p.coercion_report = _CR()
    assert coercion_uncertainty_raw(p) is None


def test_merge_clamps_urgency_when_temporal_boost_large(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_TEMPORAL_ETA_MODULATION", "1")
    monkeypatch.setenv("KERNEL_TEMPORAL_REFERENCE_ETA_S", "300")

    class _TC:
        eta_seconds = 1.0
        battery_horizon_state = "critical"

    p = _p()
    p.temporal_context = _TC()
    base = {"urgency": 0.95}
    out = merge_chat_turn_signals_for_ethical_core(base, p)
    assert out["urgency"] <= 1.0
    assert math.isfinite(out["urgency"])


def test_merge_coerces_non_numeric_signal_values() -> None:
    p = _p()
    out = merge_chat_turn_signals_for_ethical_core({"urgency": "not-a-float", "risk": 0.5}, p)
    assert out["urgency"] == 0.0
    assert out["risk"] == 0.5


def test_merge_preserves_rlhf_features_mapping() -> None:
    p = _p()
    rf = {"embedding_sim": 0.2, "lexical_score": 0.1, "perception_confidence": 0.9}
    out = merge_chat_turn_signals_for_ethical_core({"risk": 0.3, "rlhf_features": rf}, p)
    assert out["risk"] == 0.3
    assert out["rlhf_features"] == rf
    assert out["rlhf_features"] is not rf
