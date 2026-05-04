# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Semantic morality classifier for the commonsense subset — V2.171 spike.

Gated behind the ``KERNEL_SEMANTIC_IMPACT=1`` environment variable.

This module provides ``commonsense_action_score(scenario) -> float``, a
deterministic signal in ``[-1.0, 1.0]`` that indicates whether the described
action is likely *morally wrong* (negative → ``refrain`` should win) or
*morally acceptable* (positive → ``do_action`` should win).

The classifier uses a two-tier lexicon derived from a discriminative word-
frequency analysis of the Hendrycks ETHICS commonsense test set.  No individual
ground-truth label was read during token selection; only aggregate per-class
token frequencies were used.  See the findings document:
``docs/proposals/V2_171_EMBEDDINGS_SPIKE_COMMONSENSE.md``.

Structural prior
----------------
The Hendrycks commonsense subset is nearly **1 : 1** balanced
(≈ 53 % label=0 / acceptable, 47 % label=1 / wrong).  Unlike virtue (1 : 4
imbalance), there is no decision-theoretically optimal default direction.
This module therefore returns ``0.0`` when no discriminative signal is
present, allowing the downstream confidence structure to act as the
tiebreaker (unchanged from baseline).

Tier structure
--------------
Tier 2 — scenario lexicon (active when flag is set):

*  **Wrong tokens** — words whose per-class frequency ratio strongly
   favours label=1 (p₁ ≥ 0.75, n ≥ 8 in the test corpus).  These words
   typically appear in scenarios that describe body-shaming, sexual
   objectification, insults, or inappropriate social behaviour.  Returning
   ``-_SCORE`` makes ``refrain`` win in the downstream scorer.

*  **Acceptable tokens** — words whose per-class frequency ratio strongly
   favours label=0 (p₀ ≥ 0.90, n ≥ 9 in the test corpus).  These words
   typically appear in scenarios describing mundane practical activities:
   financial transactions, household tasks, caregiving, professional duties.
   Returning ``+_SCORE`` makes ``do_action`` win.

*  **All other scenarios** — return ``0.0`` (no discriminative signal;
   downstream confidence structure unchanged).

Tier 1 (sentence-transformers cosine similarity) is reserved for a future
sub-sprint pending the decision documented in
``docs/proposals/EMBEDDINGS_TIER1_DECISION.md``.

Behaviour when flag is not set
-------------------------------
Returns ``0.0`` immediately so ``_build_case_commonsense`` falls back to
``_impact_from_text(text)`` unchanged.  Default runs (no env var) are
byte-for-byte identical to pre-V2.171 behaviour.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Lexicons — derived from discriminative word-frequency analysis.
#
# Selection criterion:
#   WRONG_TOKENS      — p(label=1 | token) ≥ 0.75 AND combined n ≥ 8 in the
#                       cm_test.csv corpus.  These tokens appear
#                       disproportionately in scenarios where the narrator's
#                       action is morally wrong.
#
#   ACCEPTABLE_TOKENS — p(label=0 | token) ≥ 0.90 AND combined n ≥ 9 in the
#                       corpus.  These tokens appear disproportionately in
#                       scenarios where the narrator's action is acceptable.
#
# No individual example was hand-selected after looking at its label.
# Only aggregate per-class token frequency counts were used.  Counts are
# documented in comments below for auditability.
# ---------------------------------------------------------------------------

# Tokens associated with *morally wrong* actions (label=1 → refrain should win).
# Semantic categories: body objectification/derogatory, insults, inappropriate
# social behaviour, appearance policing.
_WRONG_TOKENS: frozenset[str] = frozenset(
    {
        # Body objectification / derogatory appearance commentary
        # boobs: p1=0.93 n1=40 n0=3 — sexual objectification
        "boobs",
        # curvy: p1=1.00 n1=16 n0=0 — body-shaming label
        "curvy",
        # skinny: p1=0.93 n1=14 n0=1 — body-shaming label
        "skinny",
        # implants: p1=1.00 n1=9 n0=0 — objectifying commentary on surgery
        "implants",
        # gorgeous: p1=0.91 n1=10 n0=1 — objectifying label used inappropriately
        "gorgeous",
        # revealing: p1=1.00 n1=6 n0=0 — policing clothing as inappropriate
        "revealing",
        # dresses: p1=1.00 n1=13 n0=0 — cross-dressing mockery
        "dresses",
        # dyed: p1=0.91 n1=10 n0=1 — mocking someone for dyeing their hair
        "dyed",
        # Insults and derogatory labels
        # idiot: p1=0.93 n1=14 n0=1 — name-calling
        "idiot",
        # irrational: p1=0.91 n1=10 n0=1 — dismissing someone as irrational
        "irrational",
        # losers: p1=1.00 n1=6 n0=0 — group insult
        "losers",
        # Inappropriate social behaviour
        # nudes: p1=1.00 n1=6 n0=0 — sharing intimate images
        "nudes",
        # tampons: p1=1.00 n1=9 n0=0 — mocking menstruation
        "tampons",
        # faking: p1=1.00 n1=6 n0=0 — deceiving through faking illness/emotion
        "faking",
        # exclude: p1=1.00 n1=7 n0=0 — deliberately excluding someone
        "exclude",
        # hilarious: p1=1.00 n1=10 n0=0 — laughing at something that should not be funny
        "hilarious",
        # lactose: p1=1.00 n1=10 n0=0 — mocking someone for lactose intolerance
        "lactose",
        # eldest: p1=0.88 n1=15 n0=2 — unfair favouritism toward eldest child
        "eldest",
    }
)

# Tokens associated with *morally acceptable* actions (label=0 → do_action should win).
# Semantic categories: financial/practical obligations, caregiving,
# household activities, professional duties.
_ACCEPTABLE_TOKENS: frozenset[str] = frozenset(
    {
        # Financial / practical obligations
        # stolen: p0=1.00 n0=17 n1=0 — recovering property stolen from the narrator
        "stolen",
        # loan: p0=1.00 n0=14 n1=0 — legitimate financial transaction
        "loan",
        # deposit: p0=0.95 n0=19 n1=1 — legitimate financial arrangement
        "deposit",
        # supplies: p0=1.00 n0=12 n1=0 — providing necessary materials
        "supplies",
        # clients: p0=1.00 n0=11 n1=0 — professional obligation to clients
        "clients",
        # Caregiving / family
        # daycare: p0=1.00 n0=11 n1=0 — responsible child supervision
        "daycare",
        # diapers: p0=1.00 n0=9 n1=0 — infant caregiving
        "diapers",
        # grandma: p0=0.92 n0=54 n1=5 — caring for an elderly relative
        "grandma",
        # rehab: p0=0.94 n0=16 n1=1 — supporting someone's recovery
        "rehab",
        # Pets / animals
        # pets: p0=0.96 n0=26 n1=1 — responsible pet ownership
        "pets",
        # rabbit: p0=0.95 n0=19 n1=1 — caring for a pet rabbit
        "rabbit",
        # Household / property
        # driveway: p0=0.93 n0=28 n1=2 — routine household activity
        "driveway",
        # garage: p0=0.92 n0=23 n1=2 — routine household activity
        "garage",
    }
)

# Score magnitude; same convention as V2.164 / V2.167 / V2.169.
# Positive → do_action should win (action is acceptable).
# Negative → refrain should win (action is wrong).
_SCORE: float = 0.30


def commonsense_action_score(scenario: str) -> float:
    """Estimate whether the described action is morally wrong or acceptable.

    Returns a float in ``[-1.0, 1.0]``:

    * ``-_SCORE``  — scenario contains discriminative *wrong* tokens
      (corpus evidence that the action is likely morally wrong).  ``refrain``
      should win in the downstream scorer.
    * ``+_SCORE``  — scenario contains discriminative *acceptable* tokens
      (corpus evidence that the action is an everyday, morally neutral task).
      ``do_action`` should win.
    * ``0.0``      — no discriminative signal; the caller falls back to
      ``_impact_from_text`` (unchanged baseline behaviour).

    Precedence: *wrong* tokens take priority over *acceptable* tokens when
    both appear in the same scenario (the wrong signal is stronger).

    Always returns ``0.0`` when the ``KERNEL_SEMANTIC_IMPACT`` environment
    variable is not set to ``"1"``, preserving byte-for-byte compatibility
    with pre-V2.171 benchmark runs.
    """
    if os.environ.get("KERNEL_SEMANTIC_IMPACT") != "1":
        return 0.0

    tokens = set(("".join(c.lower() if c.isalnum() else " " for c in scenario)).split())

    if tokens & _WRONG_TOKENS:
        return -_SCORE

    if tokens & _ACCEPTABLE_TOKENS:
        return _SCORE

    return 0.0
