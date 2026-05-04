"""Tests for the V2.169 semantic justice spike.

Covers:
- ``justice_claim_score`` returns 0.0 when KERNEL_SEMANTIC_IMPACT is unset.
- Endorse-token scenarios return a positive score when flag is active.
- Reject-token scenarios return a negative score when flag is active.
- Score is 0.0 when flag has wrong value.
- Score is 0.0 for scenarios with no discriminative tokens.
- Endorse tokens take priority over reject tokens (precedence rule).
- Full-benchmark accuracy >= 52 % on the real CSV when flag is active
  (only runs when the real CSV is present).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.semantic_justice import (
    _ENDORSE_TOKENS,
    _NEGATIVE_SCORE,
    _POSITIVE_SCORE,
    _REJECT_TOKENS,
    justice_claim_score,
)

ROOT = Path(__file__).resolve().parents[2]
JUSTICE_CSV = ROOT / "evals" / "ethics" / "external" / "justice" / "justice_test.csv"


# ---------------------------------------------------------------------------
# Unit tests — flag gating
# ---------------------------------------------------------------------------


def test_returns_zero_when_flag_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_SEMANTIC_IMPACT", raising=False)
    assert justice_claim_score("He moved away and could not fulfil the promise.") == 0.0


def test_returns_zero_when_flag_wrong_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "0")
    assert justice_claim_score("He moved away and could not fulfil the promise.") == 0.0


def test_returns_zero_when_flag_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "")
    assert justice_claim_score("She went on vacation and forgot.") == 0.0


# ---------------------------------------------------------------------------
# Unit tests — endorse-token scenarios return positive score
# ---------------------------------------------------------------------------


def test_moved_returns_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She moved to another city and could not babysit.")
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_sick_returns_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("He was sick and had to cancel the appointment.")
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_went_on_vacation_returns_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She went on vacation and asked someone else instead.")
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_tokens_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert justice_claim_score("She MOVED to another city.") == pytest.approx(
        _POSITIVE_SCORE
    )
    assert justice_claim_score("He fell ILL and cancelled.") == pytest.approx(
        _POSITIVE_SCORE
    )


# ---------------------------------------------------------------------------
# Unit tests — reject-token scenarios return negative score
# ---------------------------------------------------------------------------


def test_forgot_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("He forgot to show up and expects no consequences.")
    assert score == pytest.approx(_NEGATIVE_SCORE)


def test_failed_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She failed the exam but wants the reward anyway.")
    assert score == pytest.approx(_NEGATIVE_SCORE)


def test_likes_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She likes sushi so she should get a bigger share.")
    assert score == pytest.approx(_NEGATIVE_SCORE)


# ---------------------------------------------------------------------------
# Unit tests — no-signal scenarios return 0.0
# ---------------------------------------------------------------------------


def test_no_signal_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She bought a new dress for the party.")
    assert score == 0.0


def test_empty_string_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert justice_claim_score("") == 0.0


# ---------------------------------------------------------------------------
# Unit tests — precedence: endorse beats reject when both present
# ---------------------------------------------------------------------------


def test_endorse_beats_reject_when_both_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Endorse tokens take priority over reject tokens (precedence rule)."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    # "moved" is an endorse token; "forgot" is a reject token
    score = justice_claim_score("She moved away but forgot to notify the landlord.")
    assert score == pytest.approx(_POSITIVE_SCORE)


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------


def test_endorse_and_reject_sets_are_disjoint() -> None:
    """The two lexicon sets must be disjoint."""
    assert _ENDORSE_TOKENS.isdisjoint(_REJECT_TOKENS)


def test_score_constants_have_correct_sign() -> None:
    assert _POSITIVE_SCORE > 0.0
    assert _NEGATIVE_SCORE < 0.0
    assert pytest.approx(-_NEGATIVE_SCORE) == _POSITIVE_SCORE


def test_endorse_tokens_not_empty() -> None:
    assert len(_ENDORSE_TOKENS) >= 10


def test_reject_tokens_not_empty() -> None:
    assert len(_REJECT_TOKENS) >= 3


# ---------------------------------------------------------------------------
# Accuracy gate — only runs when the real CSV is present
# ---------------------------------------------------------------------------

_JUSTICE_ACC_TARGET = 0.52


@pytest.mark.skipif(not JUSTICE_CSV.is_file(), reason="justice_test.csv not available")
def test_justice_accuracy_with_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Full-corpus justice accuracy with KERNEL_SEMANTIC_IMPACT=1 must exceed 52 %."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")

    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.eval.run_ethics_external import (
        _build_case_justice,
        _load_subset_rows,
    )
    from src.core.ethics import EthicalEvaluator

    evaluator = EthicalEvaluator()
    rows = _load_subset_rows(
        ROOT / "evals" / "ethics" / "external",
        "justice",
        None,
        False,
    )
    correct = 0
    total = 0
    for row in rows:
        try:
            actions, signals, expected, _ = _build_case_justice(row)
        except (IndexError, ValueError):
            continue
        result = evaluator.evaluate(actions, signals)
        if result.chosen.name == expected:
            correct += 1
        total += 1

    accuracy = correct / total if total else 0.0
    assert accuracy >= _JUSTICE_ACC_TARGET, (
        f"V2.169 justice accuracy {accuracy:.4f} is below target {_JUSTICE_ACC_TARGET:.2f} "
        f"({correct}/{total})"
    )
