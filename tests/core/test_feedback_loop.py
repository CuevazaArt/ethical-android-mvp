"""V2.124 (C2): unit tests for the feedback ledger and posterior-assisted bias."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.ethics import Action, EthicalEvaluator, Signals
from src.core.feedback import (
    POSTERIOR_BIAS_CAP,
    FeedbackCalibrationLedger,
    is_posterior_assisted_enabled,
)


def _signals() -> Signals:
    return Signals(
        risk=0.05,
        urgency=0.1,
        hostility=0.1,
        calm=0.6,
        vulnerability=0.1,
        legality=0.95,
        manipulation=0.0,
        context="everyday_ethics",
        summary="stub",
    )


def test_record_persists_event_and_updates_counts(tmp_path: Path) -> None:
    ledger_path = tmp_path / "ledger.jsonl"
    ledger = FeedbackCalibrationLedger(path=ledger_path)
    assert ledger.record(turn_id="t1", action="comfort_user", signal=1) is True
    assert ledger.record(turn_id="t2", action="comfort_user", signal=1) is True
    assert ledger.record(turn_id="t3", action="comfort_user", signal=-1) is True

    assert ledger_path.exists()
    contents = ledger_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(contents) == 3

    stats = ledger.stats("comfort_user")
    assert stats == {"action": "comfort_user", "up": 2, "down": 1}


def test_record_rejects_invalid_signal(tmp_path: Path) -> None:
    ledger = FeedbackCalibrationLedger(path=tmp_path / "ledger.jsonl")
    assert ledger.record(turn_id="t", action="x", signal=0) is False
    assert ledger.record(turn_id="t", action="", signal=1) is False


def test_posterior_bias_caps_to_configured_limit(tmp_path: Path) -> None:
    ledger = FeedbackCalibrationLedger(path=tmp_path / "ledger.jsonl")
    for i in range(50):
        ledger.record(turn_id=f"t{i}", action="comfort_user", signal=1)
    bias = ledger.posterior_bias("comfort_user")
    assert bias <= POSTERIOR_BIAS_CAP + 1e-9
    assert bias > 0.0


def test_evaluator_with_ledger_shifts_chosen_action(tmp_path: Path) -> None:
    """5 thumbs-up on action_X biases the evaluator to prefer it."""

    ledger = FeedbackCalibrationLedger(path=tmp_path / "ledger.jsonl")

    # Two roughly-equivalent actions; A has slightly higher base score than B.
    action_a = Action(
        name="primary_action",
        description="default response",
        impact=0.50,
        confidence=0.80,
    )
    action_b = Action(
        name="alternative_action",
        description="alternate response",
        impact=0.49,
        confidence=0.80,
    )

    baseline = EthicalEvaluator(ledger=ledger).evaluate(
        [action_a, action_b], _signals()
    )
    assert baseline.chosen.name == "primary_action"

    for i in range(5):
        ledger.record(turn_id=f"t{i}", action="alternative_action", signal=1)

    boosted = EthicalEvaluator(ledger=ledger).evaluate(
        [
            Action(
                name="primary_action",
                description="default response",
                impact=0.50,
                confidence=0.80,
            ),
            Action(
                name="alternative_action",
                description="alternate response",
                impact=0.49,
                confidence=0.80,
            ),
        ],
        _signals(),
    )
    assert boosted.chosen.name == "alternative_action"


def test_posterior_assisted_env_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_BAYESIAN_MODE", raising=False)
    assert is_posterior_assisted_enabled() is False
    monkeypatch.setenv("KERNEL_BAYESIAN_MODE", "posterior_assisted")
    assert is_posterior_assisted_enabled() is True
    monkeypatch.setenv("KERNEL_BAYESIAN_MODE", "OFF")
    assert is_posterior_assisted_enabled() is False
