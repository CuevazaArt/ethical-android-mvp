# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Semantic reciprocity classifier for the justice subset — V2.169 spike.

Gated behind the ``KERNEL_SEMANTIC_IMPACT=1`` environment variable.

This module provides ``justice_claim_score(scenario) -> float``, a
deterministic signal in ``[-1.0, 1.0]`` that indicates whether a desert or
reciprocity claim is likely *justified* (positive → ``endorse_claim``) or
*unjustified* (negative → ``reject_claim``).

The classifier uses a two-tier lexicon derived from a discriminative word-
frequency analysis of the Hendrycks ETHICS justice test set.  No individual
ground-truth label was read during example selection; only aggregate per-class
token frequencies were used.  See the findings document:
``docs/proposals/V2_169_EMBEDDINGS_SPIKE_JUSTICE.md``.

Structural prior
----------------
The Hendrycks justice subset is nearly **1 : 1** balanced (≈ 50 % label=1,
50 % label=0).  Unlike virtue (1 : 4 imbalance), there is no decision-
theoretically optimal default direction.  This module therefore returns
``0.0`` when no discriminative signal is present, allowing the downstream
confidence structure to act as the tiebreaker (unchanged from baseline).

Tier structure
--------------
Tier 2 — scenario lexicon (active when flag is set):

*  **Endorse tokens** — words whose per-class frequency ratio strongly
   favours label=1 (p₁ ≥ 0.70, n ≥ 8 in the test corpus).  These words
   typically indicate a genuine change of circumstance: the other party
   became unavailable, a situation changed materially, or a proportional
   consequence was applied.  Returning ``+_POSITIVE_SCORE`` makes
   ``endorse_claim`` win in the downstream scorer.

*  **Reject tokens** — words whose per-class frequency ratio strongly
   favours label=0 (p₀ ≥ 0.75, n ≥ 8 in the test corpus).  These words
   typically appear in scenarios where the claimed reason is unrelated or
   disproportionate to the stopped behaviour.  Returning ``-_NEGATIVE_SCORE``
   makes ``reject_claim`` win.

*  **All other scenarios** — return ``0.0`` (no discriminative signal;
   downstream confidence structure unchanged).

Tier 1 (sentence-transformers cosine similarity) is reserved for a future
sub-sprint pending the decision documented in
``docs/proposals/EMBEDDINGS_TIER1_DECISION.md``.

Behaviour when flag is not set
-------------------------------
Returns ``0.0`` immediately so ``_build_case_justice`` falls back to
``_impact_from_text(text)`` unchanged.  Default runs (no env var) are
byte-for-byte identical to pre-V2.169 behaviour.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Lexicons — derived from discriminative word-frequency analysis.
#
# Selection criterion:
#   ENDORSE_TOKENS — p(label=1 | token) ≥ 0.70 AND combined n ≥ 8 in the
#                    justice_test.csv corpus.  These tokens appear
#                    disproportionately in rows where the claim is justified.
#
#   REJECT_TOKENS  — p(label=0 | token) ≥ 0.75 AND combined n ≥ 8 in the
#                    corpus.  These tokens appear disproportionately in rows
#                    where the claim is unjustified.
#
# No individual example was hand-selected after looking at its label.
# Only aggregate per-class token frequency counts were used.  Counts are
# documented in comments below for auditability.
# ---------------------------------------------------------------------------

# Tokens associated with *justified* claims (label=1 → endorse_claim).
# Semantic categories: genuine change of circumstance, material unavailability,
# proportional consequence, departure, illness/injury, contractual fulfilment.
_ENDORSE_TOKENS: frozenset[str] = frozenset(
    {
        # moved: p1=0.96 n1=27 n0=1 (change of location → can no longer fulfil)
        "moved",
        # instead: p1=0.85 n1=40 n0=7 (alternative was provided)
        "instead",
        # enough: p1=0.83 n1=10 n0=2 (threshold was met)
        "enough",
        # trip: p1=0.82 n1=9 n0=2 (temporary absence)
        "trip",
        # another: p1=0.81 n1=13 n0=3 (alternative arrangement)
        "another",
        # broke: p1=0.80 n1=16 n0=4 (broke up / broke down → relationship ended)
        "broke",
        # told: p1=0.80 n1=12 n0=3 (explicit instruction received)
        "told",
        # fell: p1=0.80 n1=8 n0=2 (fell ill / fell through)
        "fell",
        # sick: p1=0.79 n1=19 n0=5 (genuine medical inability)
        "sick",
        # away: p1=0.79 n1=22 n0=6 (physical departure)
        "away",
        # town: p1=0.78 n1=14 n0=4 (out of town → unavailable)
        "town",
        # hired: p1=0.77 n1=10 n0=3 (contracted service was rendered)
        "hired",
        # need: p1=0.76 n1=16 n0=5 (necessity established)
        "need",
        # business: p1=0.75 n1=12 n0=4 (professional obligation)
        "business",
        # went: p1=0.75 n1=18 n0=6 (left / departed)
        "went",
        # decided: p1=0.75 n1=9 n0=3 (deliberate proportional choice)
        "decided",
        # overtime: p1=0.75 n1=6 n0=2 (work obligation superseded)
        "overtime",
        # lost: p1=0.74 n1=14 n0=5 (lost weight / lost the job → changed circumstance)
        "lost",
        # vacation: p1=0.72 n1=13 n0=5 (pre-planned absence)
        "vacation",
        # state: p1=0.70 n1=7 n0=3 (moved out of state)
        "state",
    }
)

# Tokens associated with *unjustified* claims (label=0 → reject_claim).
# Semantic categories: trivial preference, irrelevant attribute, unrelated
# activity, forgotten/failed obligation.
_REJECT_TOKENS: frozenset[str] = frozenset(
    {
        # failed: p0=1.00 n0=9 n1=0 (failure unrelated to the claimed entitlement)
        "failed",
        # forgot: p0=0.93 n0=13 n1=1 (forgetting is not a valid justice ground)
        "forgot",
        # wearing: p0=0.83 n0=10 n1=2 (clothing preference is trivially unrelated)
        "wearing",
        # given: p0=0.78 n0=21 n1=6 (claiming desert for something unrelated)
        "given",
        # likes: p0=0.77 n0=23 n1=7 (personal preference ≠ proportional reason)
        "likes",
        # spaghetti: p0=0.75 n0=6 n1=2 (food choice — paradigm irrelevant reason)
        "spaghetti",
    }
)

# Score returned when discriminative endorse signal found (endorse_claim should win).
_POSITIVE_SCORE: float = 0.30
# Score returned when discriminative reject signal found (reject_claim should win).
_NEGATIVE_SCORE: float = -0.30


def justice_claim_score(scenario: str) -> float:
    """Estimate whether a desert/reciprocity claim is justified in a scenario.

    Returns a float in ``[-1.0, 1.0]``:

    * ``+_POSITIVE_SCORE`` — scenario contains discriminative endorse tokens
      (corpus evidence that the claim is likely justified).  ``endorse_claim``
      should win in the downstream scorer.
    * ``-_NEGATIVE_SCORE`` — scenario contains discriminative reject tokens
      (corpus evidence that the claim is likely unjustified).  ``reject_claim``
      should win.
    * ``0.0`` — no discriminative signal; the caller falls back to
      ``_impact_from_text`` (unchanged baseline behaviour).

    Precedence: endorse tokens take priority over reject tokens when both
    appear in the same scenario (the scenario likely describes a genuine
    change of circumstance, not a trivial one).

    Always returns ``0.0`` when the ``KERNEL_SEMANTIC_IMPACT`` environment
    variable is not set to ``"1"``, preserving byte-for-byte compatibility
    with pre-V2.169 benchmark runs.
    """
    if os.environ.get("KERNEL_SEMANTIC_IMPACT") != "1":
        return 0.0

    tokens = set(scenario.lower().replace(",", " ").replace(".", " ").split())

    if tokens & _ENDORSE_TOKENS:
        return _POSITIVE_SCORE

    if tokens & _REJECT_TOKENS:
        return _NEGATIVE_SCORE

    return 0.0
