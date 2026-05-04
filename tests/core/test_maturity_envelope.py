# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""V2.151: Tests for the maturity stage confidence envelope.

Invariant: confidence_displayed ≤ confidence_ceiling(current_stage)
"""

from __future__ import annotations

import pytest

from src.core.maturity import (
    CONFIDENCE_CEILING,
    MaturityStage,
    apply_confidence_ceiling,
    current_stage,
)

# ---------------------------------------------------------------------------
# MaturityStage ordering
# ---------------------------------------------------------------------------


def test_stage_ordering_is_correct():
    assert MaturityStage.infant < MaturityStage.child
    assert MaturityStage.child < MaturityStage.adolescent
    assert MaturityStage.adolescent < MaturityStage.young_adult


def test_stage_string_values():
    assert MaturityStage.infant.value == "infant"
    assert MaturityStage.young_adult.value == "young_adult"


# ---------------------------------------------------------------------------
# Confidence ceiling invariant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("stage", list(MaturityStage))
def test_confidence_ceiling_defined_for_all_stages(stage: MaturityStage):
    assert stage in CONFIDENCE_CEILING
    ceiling = CONFIDENCE_CEILING[stage]
    assert 0.0 < ceiling <= 1.0


@pytest.mark.parametrize("stage", list(MaturityStage))
def test_apply_confidence_ceiling_never_exceeds_ceiling(
    stage: MaturityStage,
    monkeypatch,
):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", stage.value)
    ceiling = CONFIDENCE_CEILING[stage]
    for raw in [0.0, 0.5, 0.9, 1.0, 1.5, float("inf"), float("nan")]:
        displayed = apply_confidence_ceiling(raw)
        assert displayed <= ceiling, (
            f"stage={stage}, raw={raw}, displayed={displayed}, ceiling={ceiling}"
        )


def test_apply_confidence_ceiling_clamps_non_finite(monkeypatch):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "infant")
    # NaN → 0.0
    assert apply_confidence_ceiling(float("nan")) == 0.0
    # Inf → ceiling (because 0.0 is min, then min with ceiling)
    assert (
        apply_confidence_ceiling(float("inf"))
        <= CONFIDENCE_CEILING[MaturityStage.infant]
    )


def test_apply_confidence_ceiling_is_monotone_in_input(monkeypatch):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "child")
    displayed_low = apply_confidence_ceiling(0.1)
    displayed_high = apply_confidence_ceiling(0.9)
    assert displayed_low <= displayed_high


# ---------------------------------------------------------------------------
# current_stage env override (no file I/O)
# ---------------------------------------------------------------------------


def test_current_stage_env_override_infant(monkeypatch):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "infant")
    assert current_stage() == MaturityStage.infant


def test_current_stage_env_override_child(monkeypatch):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "child")
    assert current_stage() == MaturityStage.child


def test_current_stage_invalid_env_override_falls_back(monkeypatch, tmp_path):
    """An unrecognised env value falls back to ledger / infant default."""
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "enlightened_god")
    # No ledger → defaults to infant
    stage = current_stage(force_reload=True)
    assert stage in list(MaturityStage)


# ---------------------------------------------------------------------------
# decision_trace contains the three maturity fields
# ---------------------------------------------------------------------------


def test_decision_trace_contains_maturity_fields(monkeypatch):
    """build_decision_trace must always include maturity_stage,
    confidence_internal, and confidence_displayed (V2.151)."""
    from src.core.chat import build_decision_trace
    from src.core.ethics import Action, EvalResult, Signals

    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "infant")

    action = Action(
        name="respond_helpfully", description="help", impact=0.5, confidence=0.9
    )
    eval_result = EvalResult(
        chosen=action,
        score=0.5,
        uncertainty=0.1,
        mode="D_fast",
        verdict="Good",
        reasoning="test",
    )
    signals = Signals()
    trace = build_decision_trace(signals=signals, evaluation=eval_result, blocked=False)

    assert "maturity_stage" in trace
    assert "confidence_internal" in trace
    assert "confidence_displayed" in trace

    ceiling = CONFIDENCE_CEILING[MaturityStage.infant]
    assert trace["confidence_displayed"] <= ceiling
    assert trace["confidence_internal"] == pytest.approx(0.9)


def test_decision_trace_blocked_has_maturity_fields(monkeypatch):
    monkeypatch.setenv("KERNEL_MATURITY_STAGE_OVERRIDE", "infant")
    from src.core.chat import build_decision_trace

    trace = build_decision_trace(
        signals=None, evaluation=None, blocked=True, blocked_reason="test"
    )
    assert "maturity_stage" in trace
    assert trace["confidence_displayed"] == 0.0
    assert trace["confidence_internal"] == 0.0
