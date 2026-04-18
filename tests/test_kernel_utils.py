"""Unit tests for :mod:`src.kernel_utils` (Module 0.1.3 extractions)."""

import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel_utils import (
    apply_temporal_eta_urgency_to_signals,
    coercion_uncertainty_from_perception,
    enrich_chat_turn_signals_for_bayesian,
    kernel_decision_event_payload,
    kernel_env_float,
    kernel_env_truthy,
    merge_perception_uncertainty_into_signals,
)


def test_kernel_decision_event_payload_minimal() -> None:
    d = SimpleNamespace(
        scenario="hello world " * 100,
        place="p",
        final_action="a",
        decision_mode="m",
        blocked=True,
        block_reason="r",
        moral=SimpleNamespace(global_verdict=SimpleNamespace(value="Gray"), total_score=0.42),
    )
    p = kernel_decision_event_payload(d, context="ctx")
    assert p["place"] == "p"
    assert p["context"] == "ctx"
    assert p["verdict"] == "Gray"
    assert p["score"] == pytest.approx(0.42)
    assert len(p["scenario"]) <= 500


def test_kernel_decision_event_payload_no_moral() -> None:
    d = SimpleNamespace(
        scenario="s",
        place="p",
        final_action="a",
        decision_mode="m",
        blocked=False,
        block_reason="",
        moral=None,
    )
    p = kernel_decision_event_payload(d, context="c")
    assert p["verdict"] is None
    assert p["score"] is None


def test_kernel_env_truthy() -> None:
    import os

    old = os.environ.get("KUT_TEST_X")
    try:
        os.environ["KUT_TEST_X"] = "1"
        assert kernel_env_truthy("KUT_TEST_X") is True
        del os.environ["KUT_TEST_X"]
        assert kernel_env_truthy("KUT_TEST_X") is False
    finally:
        if old is not None:
            os.environ["KUT_TEST_X"] = old
        elif "KUT_TEST_X" in os.environ:
            del os.environ["KUT_TEST_X"]


def test_coercion_uncertainty_from_perception_dict() -> None:
    p = SimpleNamespace(coercion_report={"uncertainty": 0.4})
    assert coercion_uncertainty_from_perception(p) == pytest.approx(0.4)


class _U:
    def uncertainty(self) -> float:
        return 0.6


def test_coercion_uncertainty_from_perception_callable() -> None:
    p = SimpleNamespace(coercion_report=_U())
    assert coercion_uncertainty_from_perception(p) == pytest.approx(0.6)


def test_merge_perception_uncertainty_into_signals() -> None:
    s = {"perception_uncertainty": 0.1}
    out = merge_perception_uncertainty_into_signals(s, 0.5)
    assert isinstance(out, dict)
    assert out["perception_uncertainty"] == pytest.approx(0.5)
    s2: dict = {}
    assert merge_perception_uncertainty_into_signals(s2, None) is s2
    assert merge_perception_uncertainty_into_signals(s2, 0.0) is s2


def test_enrich_chat_turn_i3_i5() -> None:
    old_t = os.environ.get("KERNEL_TEMPORAL_ETA_MODULATION")
    old_ref = os.environ.get("KERNEL_TEMPORAL_REFERENCE_ETA_S")
    try:
        os.environ["KERNEL_TEMPORAL_ETA_MODULATION"] = "1"
        os.environ["KERNEL_TEMPORAL_REFERENCE_ETA_S"] = "300"
        p = SimpleNamespace(
            coercion_report={"uncertainty": 0.25},
            temporal_context=SimpleNamespace(eta_seconds=100.0, battery_horizon_state="nominal"),
        )
        base = {"urgency": 0.1, "perception_uncertainty": 0.0}
        out = enrich_chat_turn_signals_for_bayesian(base, p)
        assert isinstance(out, dict)
        assert out["perception_uncertainty"] == pytest.approx(0.25)
        assert out["urgency"] > 0.1
    finally:
        if old_t is not None:
            os.environ["KERNEL_TEMPORAL_ETA_MODULATION"] = old_t
        elif "KERNEL_TEMPORAL_ETA_MODULATION" in os.environ:
            del os.environ["KERNEL_TEMPORAL_ETA_MODULATION"]
        if old_ref is not None:
            os.environ["KERNEL_TEMPORAL_REFERENCE_ETA_S"] = old_ref
        elif "KERNEL_TEMPORAL_REFERENCE_ETA_S" in os.environ:
            del os.environ["KERNEL_TEMPORAL_REFERENCE_ETA_S"]


def test_apply_temporal_eta_urgency_disabled_returns_same() -> None:
    old = os.environ.get("KERNEL_TEMPORAL_ETA_MODULATION")
    try:
        if "KERNEL_TEMPORAL_ETA_MODULATION" in os.environ:
            del os.environ["KERNEL_TEMPORAL_ETA_MODULATION"]
        s = {"urgency": 0.2}
        p = SimpleNamespace(
            temporal_context=SimpleNamespace(eta_seconds=50.0, battery_horizon_state="nominal")
        )
        out = apply_temporal_eta_urgency_to_signals(s, p)
        assert out is s
    finally:
        if old is not None:
            os.environ["KERNEL_TEMPORAL_ETA_MODULATION"] = old


def test_kernel_env_float_clamp() -> None:
    assert kernel_env_float("_MISSING_XX", 3.0, min_v=1.0, max_v=10.0) == 3.0
    old = os.environ.get("KUT_FLOAT_X")
    try:
        os.environ["KUT_FLOAT_X"] = "not_a_number"
        assert kernel_env_float("KUT_FLOAT_X", 2.0, min_v=1.0, max_v=5.0) == 2.0
        os.environ["KUT_FLOAT_X"] = "9999"
        assert kernel_env_float("KUT_FLOAT_X", 1.0, min_v=1.0, max_v=10.0) == 10.0
    finally:
        if old is not None:
            os.environ["KUT_FLOAT_X"] = old
        elif "KUT_FLOAT_X" in os.environ:
            del os.environ["KUT_FLOAT_X"]


def test_merge_perception_uncertainty_tolerates_garbage_signal() -> None:
    s = {"perception_uncertainty": "nope"}
    out = merge_perception_uncertainty_into_signals(s, 0.3)
    assert out["perception_uncertainty"] == pytest.approx(0.3)


def test_apply_temporal_skips_non_finite_eta() -> None:
    old = os.environ.get("KERNEL_TEMPORAL_ETA_MODULATION")
    try:
        os.environ["KERNEL_TEMPORAL_ETA_MODULATION"] = "1"
        s = {"urgency": 0.1}
        p = SimpleNamespace(
            temporal_context=SimpleNamespace(eta_seconds=float("nan"), battery_horizon_state="nominal")
        )
        out = apply_temporal_eta_urgency_to_signals(s, p)
        assert out is s
    finally:
        if old is not None:
            os.environ["KERNEL_TEMPORAL_ETA_MODULATION"] = old
        elif "KERNEL_TEMPORAL_ETA_MODULATION" in os.environ:
            del os.environ["KERNEL_TEMPORAL_ETA_MODULATION"]
