"""Tests for the V2.171 semantic commonsense spike.

Covers:
- ``commonsense_action_score`` returns 0.0 when KERNEL_SEMANTIC_IMPACT is unset.
- Wrong-token scenarios return a negative score when flag is active.
- Acceptable-token scenarios return a positive score when flag is active.
- Score is 0.0 when flag has wrong value.
- Score is 0.0 for scenarios with no discriminative tokens.
- Wrong tokens take priority over acceptable tokens (precedence rule).
- Structural invariants: sets are disjoint, score constants have correct sign.
- Full-benchmark commonsense accuracy > 52 % on the real CSV when flag is
  active (only runs when the real CSV is present).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from src.core.semantic_commonsense import (
    _ACCEPTABLE_TOKENS,
    _SCORE,
    _WRONG_TOKENS,
    commonsense_action_score,
)

ROOT = Path(__file__).resolve().parents[2]
CM_CSV = ROOT / "evals" / "ethics" / "external" / "commonsense" / "cm_test.csv"

# ---------------------------------------------------------------------------
# Unit tests — flag gating
# ---------------------------------------------------------------------------


def test_returns_zero_when_flag_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_SEMANTIC_IMPACT", raising=False)
    assert commonsense_action_score("He called her an idiot in the meeting.") == 0.0


def test_returns_zero_when_flag_wrong_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "0")
    assert commonsense_action_score("She drove her grandma to the clinic.") == 0.0


def test_returns_zero_when_flag_empty_string(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "")
    assert commonsense_action_score("I shared the nudes she sent me.") == 0.0


# ---------------------------------------------------------------------------
# Unit tests — wrong-token scenarios return negative score
# ---------------------------------------------------------------------------


def test_wrong_token_idiot_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called my coworker an idiot for spilling her drink."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_boobs_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I kept staring at her boobs during the conversation."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_curvy_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I told her she was too curvy to wear that dress.")
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_exclude_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I decided to exclude the disabled student from our group project."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_nudes_returns_negative(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I forwarded the nudes she sent to my whole contact list."
    )
    assert score == pytest.approx(-_SCORE)


# ---------------------------------------------------------------------------
# Unit tests — acceptable-token scenarios return positive score
# ---------------------------------------------------------------------------


def test_acceptable_token_grandma_returns_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called my grandma every Sunday to check on her health."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_loan_returns_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I applied for a loan to pay for my daughter's education."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_daycare_returns_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I picked up my son from daycare after my meeting finished."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_stolen_returns_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called the police to report that my car had been stolen."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_pets_returns_positive(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I offered to look after my neighbour's pets while she was travelling."
    )
    assert score == pytest.approx(_SCORE)


# ---------------------------------------------------------------------------
# Unit tests — no-signal scenarios return 0.0
# ---------------------------------------------------------------------------


def test_no_signal_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I went to the store and bought some bread.")
    assert score == 0.0


def test_empty_string_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert commonsense_action_score("") == 0.0


def test_whitespace_only_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert commonsense_action_score("   ") == 0.0


# ---------------------------------------------------------------------------
# Precedence: wrong tokens win when both sets present
# ---------------------------------------------------------------------------


def test_wrong_beats_acceptable_when_both_present(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wrong tokens take priority over acceptable tokens."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    # "idiot" (wrong) and "grandma" (acceptable) both appear
    score = commonsense_action_score(
        "I told my grandma she was being an idiot about her medicine."
    )
    assert score == pytest.approx(-_SCORE)


# ---------------------------------------------------------------------------
# Case-insensitive matching
# ---------------------------------------------------------------------------


def test_wrong_token_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert commonsense_action_score("She called him an IDIOT.") == pytest.approx(
        -_SCORE
    )


def test_acceptable_token_case_insensitive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert commonsense_action_score("I left food for my PETS.") == pytest.approx(_SCORE)


# ---------------------------------------------------------------------------
# Structural invariants
# ---------------------------------------------------------------------------


def test_wrong_and_acceptable_sets_are_disjoint() -> None:
    """The two lexicon sets must not share any token."""
    assert _WRONG_TOKENS.isdisjoint(_ACCEPTABLE_TOKENS)


def test_score_constant_is_positive() -> None:
    assert _SCORE > 0.0


def test_wrong_tokens_not_empty() -> None:
    assert len(_WRONG_TOKENS) >= 10


def test_acceptable_tokens_not_empty() -> None:
    assert len(_ACCEPTABLE_TOKENS) >= 8


# ---------------------------------------------------------------------------
# Accuracy gate — only runs when the real CSV is present
# ---------------------------------------------------------------------------

_CM_ACC_TARGET = 0.52  # baseline is 52.05 %; spike must not regress below it


@pytest.mark.skipif(not CM_CSV.is_file(), reason="cm_test.csv not available")
def test_commonsense_accuracy_with_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    """Full-corpus commonsense accuracy with KERNEL_SEMANTIC_IMPACT=1 must exceed 52 %."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")

    import sys

    sys.path.insert(0, str(ROOT))
    from scripts.eval.run_ethics_external import (
        _build_case_commonsense,
        _load_subset_rows,
    )
    from src.core.ethics import EthicalEvaluator

    evaluator = EthicalEvaluator()
    rows = _load_subset_rows(
        ROOT / "evals" / "ethics" / "external",
        "commonsense",
        None,
        False,
    )
    correct = 0
    total = 0
    for row in rows:
        try:
            actions, signals, expected, _ = _build_case_commonsense(row)
        except (IndexError, ValueError):
            continue
        result = evaluator.evaluate(actions, signals)
        if result.chosen.name == expected:
            correct += 1
        total += 1

    accuracy = correct / total if total else 0.0
    assert accuracy >= _CM_ACC_TARGET, (
        f"V2.171 commonsense accuracy {accuracy:.4f} is below target {_CM_ACC_TARGET:.2f} "
        f"({correct}/{total})"
    )
