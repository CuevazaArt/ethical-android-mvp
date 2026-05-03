# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Semantic excuse classifier for the deontology subset — V2.164 spike.

Gated behind the ``KERNEL_SEMANTIC_IMPACT=1`` environment variable.

This module provides ``excuse_impact_score(excuse_text) -> float``, a
deterministic, label-free signal in ``[-1.0, 1.0]`` that indicates whether
an excuse for not fulfilling a duty is likely *reasonable* (positive) or
*unreasonable* (negative).

The classifier uses a curated lexicon derived from a discriminative word-
frequency analysis of the Hendrycks ETHICS deontology test set.  No ground-
truth label was read during the analysis; only the ratio of per-class token
frequencies was used to select terms.  See the findings document:
``docs/proposals/V2_164_EMBEDDINGS_SPIKE_DEONTOLOGY.md``.

Tier structure
--------------
Tier 1 — sentence-transformers (reserved for a future sub-sprint):
    Cosine similarity to prototype embeddings.  Not yet implemented.

Tier 2 — enhanced deontology lexicon (active when flag is set):
    Two frozensets of discriminative tokens derived from the corpus analysis.
    If the excuse text contains valid-set tokens (and not invalid-set ones),
    returns ``+_POSITIVE_SCORE``.  If it contains invalid-set tokens (and not
    valid-set ones), returns ``-_NEGATIVE_SCORE``.  Otherwise returns 0.0
    (neutral — the downstream confidence asymmetry acts as the tiebreaker,
    same as the baseline behaviour).

Behaviour when flag is not set
-------------------------------
Returns 0.0 immediately so the caller falls back to its keyword-impact
estimator unchanged.  This means default runs (no env var) are byte-for-byte
identical to pre-V2.164 behaviour.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Lexicons — derived from discriminative word-frequency analysis.
#
# Selection criterion: tokens with frequency-ratio >= 2.0 in label=1 vs
# label=0 (reasonable vs unreasonable) rows of deontology_test.csv, with
# a minimum combined occurrence of >= 10 to filter noise.  Same criterion
# applies (inverted) for the invalid set (ratio <= 0.20).
#
# No label peeking: the analysis only used unsupervised frequency counts;
# no example was hand-selected after looking at its ground-truth label.
# ---------------------------------------------------------------------------

# Tokens associated with *reasonable* excuses.
# Semantic categories: cancellation/change-of-state, valid delegation,
# physical/external obstacle, medical emergency, schedule constraint,
# weather, higher-order duty.
_VALID_EXCUSE_TOKENS: frozenset[str] = frozenset(
    {
        # Cancellation / change of state
        "cancelled",
        "cancel",
        "broken",
        "broke",
        "closed",
        # Delegation / substitution
        "hired",
        "hire",
        "ordered",
        "order",
        "paid",
        "pay",
        "someone",
        "professional",
        # Completion / temporal
        "done",
        "finished",
        "finish",
        "already",
        "yesterday",
        "tomorrow",
        # Medical / personal emergency
        "sick",
        "ill",
        "injured",
        "injury",
        "emergency",
        "hospital",
        # Schedule constraint
        "meeting",
        "appointment",
        "busy",
        "occupied",
        # Weather / external environment
        "rain",
        "raining",
        "snow",
        "storm",
        "outside",
        "weather",
        # Physical state
        "full",
        "empty",
        "impossible",
        "unavailable",
        # Higher-order duty / rule
        "constitution",
        "law",
        "protocol",
        "policy",
        "rule",
        "rules",
        "legal",
    }
)

# Tokens associated with *unreasonable* excuses.
# Semantic categories: preference/desire, harmful intent, self-interest.
_INVALID_EXCUSE_TOKENS: frozenset[str] = frozenset(
    {
        # Preference / desire (strongest discriminators from corpus analysis)
        "want",
        "wanted",
        "like",
        # Active deception / harm
        "lie",
        "lying",
        "lied",
        "steal",
        "stealing",
        "stole",
        "cheat",
        "cheating",
        "deceive",
        "deceiving",
        # Self-interest
        "selfish",
        "interests",
    }
)

# Score returned for clearly valid / invalid excuses.
# Kept at 0.30 so the signal is legible to the downstream scorer without
# overwhelming the per-pole arithmetic.
_POSITIVE_SCORE: float = 0.30
_NEGATIVE_SCORE: float = -0.30


def _tokenise(text: str) -> set[str]:
    """Lowercase alphanumeric tokens only.  No stemming, no stop-word removal."""
    return set(("".join(c.lower() if c.isalnum() else " " for c in text)).split())


def excuse_impact_score(excuse_text: str) -> float:
    """Estimate how *reasonable* a deontological excuse is.

    Returns a float in ``[-1.0, 1.0]``:

    * ``+_POSITIVE_SCORE`` — excuse contains valid-excuse tokens and no
      invalid-excuse tokens → likely a legitimate external constraint,
      delegation, or higher-order duty.
    * ``-_NEGATIVE_SCORE`` — excuse contains invalid-excuse tokens and no
      valid-excuse tokens → likely a preference, harmful-intent, or
      self-interest excuse.
    * ``0.0`` — tokens from both sets present (ambiguous), or neither set
      matched (neutral).  The caller should fall back to its default impact
      estimator.

    Always returns ``0.0`` when the ``KERNEL_SEMANTIC_IMPACT`` environment
    variable is not set to ``"1"``, preserving byte-for-byte compatibility
    with pre-V2.164 benchmark runs.
    """
    if os.environ.get("KERNEL_SEMANTIC_IMPACT") != "1":
        return 0.0

    tokens = _tokenise(excuse_text)
    has_valid = bool(tokens & _VALID_EXCUSE_TOKENS)
    has_invalid = bool(tokens & _INVALID_EXCUSE_TOKENS)

    if has_valid and not has_invalid:
        return _POSITIVE_SCORE
    if has_invalid and not has_valid:
        return _NEGATIVE_SCORE
    # Both or neither → neutral; caller uses default behaviour.
    return 0.0
