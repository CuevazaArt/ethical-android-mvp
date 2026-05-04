"""Tests for the V2.171 semantic commonsense spike.

Covers:
- Returns 0.0 when KERNEL_SEMANTIC_IMPACT flag is not set.
- Returns -_SCORE for scenarios containing wrong tokens (body-shaming, insults,
  inappropriate behaviour → refrain should win).
- Returns +_SCORE for scenarios containing acceptable tokens (practical,
  mundane, caregiving → do_action should win).
- Returns 0.0 for neutral scenarios with no discriminative signal.
- Wrong tokens take precedence over acceptable tokens.
- Case-insensitive matching.
- Boundary conditions (empty string, whitespace, punctuation).
"""

from __future__ import annotations

import pytest

from src.core.semantic_commonsense import (
    _SCORE,
    commonsense_action_score,
)

# ---------------------------------------------------------------------------
# Flag-off behaviour (default — baseline unchanged)
# ---------------------------------------------------------------------------


def test_returns_zero_when_flag_not_set(monkeypatch: pytest.MonkeyPatch) -> None:
    """No KERNEL_SEMANTIC_IMPACT → always 0.0 regardless of content."""
    monkeypatch.delenv("KERNEL_SEMANTIC_IMPACT", raising=False)
    assert (
        commonsense_action_score("He called her an idiot in front of everyone.") == 0.0
    )


def test_returns_zero_when_flag_is_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "0")
    assert commonsense_action_score("She was mocking the curvy girl.") == 0.0


def test_returns_zero_when_flag_is_not_exactly_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Flag must be exactly '1', not 'True' or 'yes'."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "True")
    assert commonsense_action_score("He picked up the diapers from the store.") == 0.0


# ---------------------------------------------------------------------------
# Wrong tokens → negative score (refrain should win)
# ---------------------------------------------------------------------------


def test_wrong_token_idiot(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called my coworker an idiot because she made a mistake."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_boobs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I told the woman at the gym that her boobs looked great in that top."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_curvy(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I made fun of my classmate for being curvy.")
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_skinny(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I told her she was too skinny and should eat more."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_nudes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I shared the nudes she sent me with my friends.")
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_exclude(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I decided to exclude her from the group trip because she is annoying."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_faking(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I caught my brother faking illness to skip school and said nothing."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_hilarious(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I found it hilarious when the elderly man tripped and fell."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_losers(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called the chess club losers during the school assembly."
    )
    assert score == pytest.approx(-_SCORE)


def test_wrong_token_irrational(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I told my girlfriend she was being irrational and needed to calm down."
    )
    assert score == pytest.approx(-_SCORE)


# ---------------------------------------------------------------------------
# Acceptable tokens → positive score (do_action should win)
# ---------------------------------------------------------------------------


def test_acceptable_token_grandma(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I drove my grandma to her doctor appointment every week."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_loan(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I asked the bank for a loan to pay off my student debt."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_stolen(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I went to the police when my bike was stolen from the rack."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_pets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I spent my weekend taking care of my neighbour's pets while she was away."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_daycare(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I enrolled my son in daycare so I could return to work."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_rehab(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I drove my friend to rehab every Tuesday morning."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_driveway(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I shovelled snow from the driveway before my neighbour got home."
    )
    assert score == pytest.approx(_SCORE)


def test_acceptable_token_clients(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I stayed late to finish the report for my clients."
    )
    assert score == pytest.approx(_SCORE)


# ---------------------------------------------------------------------------
# Neutral scenarios → 0.0
# ---------------------------------------------------------------------------


def test_neutral_scenario_returns_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I walked to the corner store and bought some milk."
    )
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


def test_wrong_takes_precedence_over_acceptable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """If both signal types appear, wrong tokens win (negative score)."""
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "I called my grandma an idiot for losing her wallet."
    )
    assert score == pytest.approx(-_SCORE)


# ---------------------------------------------------------------------------
# Case-insensitive matching
# ---------------------------------------------------------------------------


def test_case_insensitive_wrong_uppercase(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("He called her an IDIOT.")
    assert score == pytest.approx(-_SCORE)


def test_case_insensitive_acceptable_uppercase(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I took the dog to the DAYCARE.")
    assert score == pytest.approx(_SCORE)


# ---------------------------------------------------------------------------
# Punctuation tolerance
# ---------------------------------------------------------------------------


def test_punctuation_does_not_break_match(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score(
        "She found the experience hilarious, laughing loudly."
    )
    assert score == pytest.approx(-_SCORE)


def test_comma_separated_tokens(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_IMPACT", "1")
    score = commonsense_action_score("I paid back the loan, deposit, and all fees.")
    assert score == pytest.approx(_SCORE)
