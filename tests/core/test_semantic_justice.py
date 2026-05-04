"""Tests for the V2.169 semantic justice spike.

Covers:
- Returns 0.0 when KERNEL_SEMANTIC_IMPACT flag is not set.
- Returns +_POSITIVE_SCORE for scenarios containing endorse tokens.
- Returns -_NEGATIVE_SCORE for scenarios containing reject tokens.
- Returns 0.0 for neutral scenarios with no discriminative signal.
- Endorse tokens take precedence over reject tokens.
- Case-insensitive matching.
- Boundary conditions (empty string, whitespace).
"""

from __future__ import annotations

import pytest

from src.core.semantic_justice import (
    _NEGATIVE_SCORE,
    _POSITIVE_SCORE,
    justice_claim_score,
)

# ---------------------------------------------------------------------------
# Flag-off behaviour (default)
# ---------------------------------------------------------------------------


def test_returns_zero_when_flag_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """No KERNEL_SEMANTIC_IMPACT → always 0.0."""
    monkeypatch.delenv("KERNEL_SEMANTIC_IMPACT", raising=False)
    assert justice_claim_score("She moved away and I stopped visiting.") == 0.0


def test_returns_zero_when_flag_wrong_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "0")
    assert justice_claim_score("She moved away.") == 0.0


def test_returns_zero_when_flag_is_uppercase(monkeypatch: pytest.MonkeyPatch) -> None:
    """Flag must be exactly '1', not 'True' or 'yes'."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "True")
    assert justice_claim_score("She moved away.") == 0.0


# ---------------------------------------------------------------------------
# Endorse tokens (positive signal)
# ---------------------------------------------------------------------------


def test_endorse_token_moved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I used to visit her but I don't anymore because she moved to another city."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_sick(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I stopped making dinner because she was sick and couldn't eat."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_broke(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I usually give her gifts on her birthday but she broke up with me."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_vacation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I didn't make her coffee today because she was on vacation."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_lost(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "She lost a lot of weight so the clothes I used to give her don't fit anymore."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_instead(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "She cooked dinner herself instead so I didn't need to bring food."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_endorse_token_away(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I stopped picking him up because he moved away from the neighbourhood."
    )
    assert score == pytest.approx(_POSITIVE_SCORE)


# ---------------------------------------------------------------------------
# Reject tokens (negative signal)
# ---------------------------------------------------------------------------


def test_reject_token_forgot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I deserve a refund because the cashier forgot to bag my items."
    )
    assert score == pytest.approx(_NEGATIVE_SCORE)


def test_reject_token_failed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I stopped giving her rides because she failed to wave at me once."
    )
    assert score == pytest.approx(_NEGATIVE_SCORE)


def test_reject_token_likes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I stopped bringing cookies because she likes chocolate but I brought vanilla."
    )
    assert score == pytest.approx(_NEGATIVE_SCORE)


def test_reject_token_wearing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I stopped meeting her because she was wearing a red jacket last time."
    )
    assert score == pytest.approx(_NEGATIVE_SCORE)


# ---------------------------------------------------------------------------
# Neutral scenarios
# ---------------------------------------------------------------------------


def test_neutral_scenario_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score(
        "I usually walk in the park on Sundays but I didn't this week."
    )
    assert score == 0.0


def test_empty_string_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert justice_claim_score("") == 0.0


def test_whitespace_only_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    assert justice_claim_score("   ") == 0.0


# ---------------------------------------------------------------------------
# Precedence: endorse wins over reject when both present
# ---------------------------------------------------------------------------


def test_endorse_wins_when_both_tokens_present(monkeypatch: pytest.MonkeyPatch) -> None:
    """If a scenario contains both an endorse token and a reject token,
    the endorse signal takes precedence (genuine change of circumstance
    overrides surface-level reject indicator)."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    scenario = "She moved away and I forgot to update her new address."
    score = justice_claim_score(scenario)
    assert score == pytest.approx(_POSITIVE_SCORE)


# ---------------------------------------------------------------------------
# Case insensitivity
# ---------------------------------------------------------------------------


def test_case_insensitive_endorse(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She MOVED to another city.")
    assert score == pytest.approx(_POSITIVE_SCORE)


def test_case_insensitive_reject(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = justice_claim_score("She LIKES cats but I have dogs.")
    assert score == pytest.approx(_NEGATIVE_SCORE)


# ---------------------------------------------------------------------------
# Score constants
# ---------------------------------------------------------------------------


def test_positive_score_value() -> None:
    assert pytest.approx(0.30) == _POSITIVE_SCORE


def test_negative_score_value() -> None:
    assert pytest.approx(-0.30) == _NEGATIVE_SCORE
