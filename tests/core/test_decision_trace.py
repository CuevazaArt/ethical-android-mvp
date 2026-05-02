"""V2.123 (C1): unit tests for the canonical decision trace helper."""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.core.chat import build_decision_trace
from src.core.ethics import Signals


@dataclass
class _StubAction:
    name: str


@dataclass
class _StubEvaluation:
    chosen: _StubAction
    score: float
    uncertainty: float
    mode: str
    verdict: str
    reasoning: str = ""


def _signals(context: str = "everyday_ethics") -> Signals:
    return Signals(
        risk=0.1,
        urgency=0.1,
        hostility=0.1,
        calm=0.6,
        vulnerability=0.1,
        legality=0.9,
        manipulation=0.0,
        context=context,
        summary="stub",
    )


def test_trace_pass_path_includes_required_keys() -> None:
    evaluation = _StubEvaluation(
        chosen=_StubAction("comfort_user"),
        score=0.42,
        uncertainty=0.1,
        mode="D_delib",
        verdict="Good",
    )
    trace = build_decision_trace(
        signals=_signals(),
        evaluation=evaluation,
        blocked=False,
    )
    for key in ("malabs", "context", "action", "mode", "score", "verdict", "weights"):
        assert key in trace, f"trace missing {key}"
    assert trace["malabs"] == "pass"
    assert trace["action"] == "comfort_user"
    assert trace["mode"] == "D_delib"
    assert trace["verdict"] == "Good"
    assert math.isfinite(trace["score"])
    assert isinstance(trace["weights"], list) and len(trace["weights"]) == 3


def test_trace_blocked_path_marks_safety_block_and_reason() -> None:
    trace = build_decision_trace(
        signals=None,
        evaluation=None,
        blocked=True,
        blocked_reason="lex_match",
    )
    assert trace["malabs"] == "blocked"
    assert trace["action"] == "safety_block"
    assert trace["mode"] == "blocked"
    assert trace["score"] == 0.0
    assert trace["verdict"] == "Blocked"
    assert trace["blocked_reason"] == "lex_match"


def test_trace_casual_chat_when_evaluation_is_none() -> None:
    trace = build_decision_trace(
        signals=_signals(),
        evaluation=None,
        blocked=False,
    )
    assert trace["action"] == "casual_chat"
    assert trace["mode"] == "casual"
    assert trace["verdict"] == "Neutral"
    assert trace["score"] == 0.0


def test_trace_score_clamps_non_finite_to_zero() -> None:
    evaluation = _StubEvaluation(
        chosen=_StubAction("x"),
        score=float("inf"),
        uncertainty=0.0,
        mode="D_fast",
        verdict="Bad",
    )
    trace = build_decision_trace(
        signals=_signals(),
        evaluation=evaluation,
        blocked=False,
    )
    assert trace["score"] == 0.0


def test_trace_uses_active_engine_weights_when_provided() -> None:
    evaluation = _StubEvaluation(
        chosen=_StubAction("x"),
        score=0.1,
        uncertainty=0.0,
        mode="D_delib",
        verdict="Good",
    )
    custom = {"util": 0.5, "deonto": 0.3, "virtue": 0.2}
    trace = build_decision_trace(
        signals=_signals(),
        evaluation=evaluation,
        blocked=False,
        weights=custom,
    )
    assert trace["weights"] == [0.5, 0.3, 0.2]
