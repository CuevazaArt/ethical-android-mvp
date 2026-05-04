# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""V2.151: Tests for the innate-vs-learned boundary invariant.

The learned layer (FeedbackCalibrationLedger) must NEVER be able to modify
the innate weights (WEIGHTS / select_weights) directly.  Feedback can only
produce a bounded *nudge* on top of the innate score; it cannot rewrite
the atractor's weight dict.

Key invariants:
1. FeedbackCalibrationLedger.record() does not mutate WEIGHTS.
2. posterior_bias is capped at ±POSTERIOR_BIAS_CAP regardless of net signals.
3. Applying posterior_bias to an EthicalEvaluator does not change its
   .weights attribute.
4. select_weights produces deterministic output for a given Signals input;
   feedback events do not alter that output.
"""

from __future__ import annotations

import copy

import pytest

from src.core.ethics import WEIGHTS, Action, EthicalEvaluator, Signals, select_weights
from src.core.feedback import (
    POSTERIOR_BIAS_CAP,
    FeedbackCalibrationLedger,
)

# ---------------------------------------------------------------------------
# 1. FeedbackCalibrationLedger.record() never mutates WEIGHTS
# ---------------------------------------------------------------------------


def test_feedback_record_does_not_mutate_weights(tmp_path):
    weights_before = copy.deepcopy(WEIGHTS)
    ledger = FeedbackCalibrationLedger(path=tmp_path / "test.jsonl")

    for _ in range(100):
        ledger.record(turn_id="t1", action="respond_helpfully", signal=1)
    for _ in range(50):
        ledger.record(turn_id="t2", action="respond_helpfully", signal=-1)

    assert weights_before == WEIGHTS, (
        "WEIGHTS mutated by feedback ledger — innate violation!"
    )


# ---------------------------------------------------------------------------
# 2. posterior_bias is always bounded
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("net_signals", [1, 10, 100, 1000, -1, -10, -100, -1000])
def test_posterior_bias_never_exceeds_cap(tmp_path, net_signals: int):
    ledger = FeedbackCalibrationLedger(path=tmp_path / "test.jsonl")
    signal = 1 if net_signals > 0 else -1
    for _ in range(abs(net_signals)):
        ledger.record(turn_id="t", action="test_action", signal=signal)

    bias = ledger.posterior_bias("test_action")
    assert abs(bias) <= POSTERIOR_BIAS_CAP, (
        f"posterior_bias={bias} exceeds cap={POSTERIOR_BIAS_CAP} for net_signals={net_signals}"
    )


# ---------------------------------------------------------------------------
# 3. EthicalEvaluator.weights is not modified after evaluation
# ---------------------------------------------------------------------------


def test_evaluator_weights_unchanged_after_evaluation(tmp_path):
    ledger = FeedbackCalibrationLedger(path=tmp_path / "test.jsonl")
    for _ in range(200):
        ledger.record(turn_id="t", action="respond_helpfully", signal=1)

    evaluator = EthicalEvaluator(ledger=ledger)
    weights_snapshot = copy.deepcopy(evaluator.weights)

    actions = [
        Action(
            name="respond_helpfully", description="help", impact=0.5, confidence=0.8
        ),
        Action(
            name="refuse_politely", description="refuse", impact=0.3, confidence=0.7
        ),
    ]
    signals = Signals(risk=0.3, context="everyday_ethics")
    evaluator.evaluate(actions, signals)

    assert evaluator.weights == weights_snapshot, (
        "EthicalEvaluator.weights mutated during evaluation — innate violation!"
    )


# ---------------------------------------------------------------------------
# 4. select_weights is deterministic and independent of feedback events
# ---------------------------------------------------------------------------


def test_select_weights_deterministic_ignores_feedback(tmp_path):
    signals = Signals(
        risk=0.5, context="consistency_check", summary="duty must not lie"
    )

    weights_first = select_weights(signals)

    # Simulate extensive feedback ledger activity
    ledger = FeedbackCalibrationLedger(path=tmp_path / "test.jsonl")
    for _ in range(500):
        ledger.record(turn_id="t", action="de_escalate", signal=1)
    for _ in range(500):
        ledger.record(turn_id="t", action="respond_helpfully", signal=-1)

    weights_second = select_weights(signals)

    assert weights_first == weights_second, (
        "select_weights returned different result after feedback events — innate isolation broken!"
    )


# ---------------------------------------------------------------------------
# 5. MaturityStage.infant has the strictest (lowest) confidence ceiling
# ---------------------------------------------------------------------------


def test_infant_has_lowest_ceiling():
    from src.core.maturity import CONFIDENCE_CEILING, MaturityStage

    infant_ceiling = CONFIDENCE_CEILING[MaturityStage.infant]
    for stage in list(MaturityStage):
        assert CONFIDENCE_CEILING[stage] >= infant_ceiling, (
            f"{stage} has ceiling {CONFIDENCE_CEILING[stage]} < infant ceiling {infant_ceiling}"
        )
