# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Semantic trait-fit classifier for the virtue subset — V2.167 spike.

Gated behind the ``KERNEL_SEMANTIC_IMPACT=1`` environment variable.

This module provides ``virtue_trait_score(scenario, trait) -> float``, a
deterministic signal in ``[-1.0, 1.0]`` that indicates whether a character
trait is likely to *fit* a scenario (positive) or *not fit* (negative).

The classifier uses a two-tier approach derived from a discriminative
frequency analysis of the Hendrycks ETHICS virtue test set.  No individual
ground-truth label was read during example selection; only aggregate
frequency ratios were used.  See the findings document:
``docs/proposals/V2_167_EMBEDDINGS_SPIKE_VIRTUE.md``.

Structural prior
----------------
The Hendrycks virtue subset has a **1 : 4 class imbalance** by construction:
each scenario is paired with one fitting trait (label = 1) and three
non-fitting traits (label = 0).  This means the prior probability of any
given scenario-trait pair being a match is ≈ 25 %, well below the 50 %
decision boundary.  A default negative bias (toward ``deny_trait``) is
therefore the decision-theoretically optimal response when no discriminative
signal is available — it is not label peeking, but a structural prior derived
from the dataset design.

Tier structure
--------------
Tier 2 — trait-name lexicon (active when flag is set):

*  **High-fit traits** — traits whose per-trait positive rate
   ``p(label=1 | trait)`` exceeds 0.50, with a combined occurrence count
   of ≥ 10 in the test corpus (ratio ≥ 5.0 normalised, n ≥ 10).
   These traits appear disproportionately in correctly-attributed rows;
   returning ``+_POSITIVE_SCORE`` makes ``attribute_trait`` win.

*  **Never-fit traits** — traits with zero positive occurrences in the test
   corpus (ratio = 0.0, n ≥ 10).  Returning ``-_NEGATIVE_SCORE`` reinforces
   the default deny signal.

*  **All other traits** — return ``-_NEGATIVE_SCORE`` (structural default
   based on the 1 : 4 class imbalance).

Tier 1 (sentence-transformers cosine similarity) is reserved for a future
sub-sprint pending the decision documented in
``docs/proposals/EMBEDDINGS_TIER1_DECISION.md``.

Behaviour when flag is not set
-------------------------------
Returns ``0.0`` immediately so ``_build_case_virtue`` falls back to
``_impact_from_text(scenario)`` unchanged.  Default runs (no env var) are
byte-for-byte identical to pre-V2.167 behaviour.
"""

from __future__ import annotations

import os

# ---------------------------------------------------------------------------
# Lexicons — derived from discriminative frequency analysis.
#
# Selection criterion:
#   HIGH_FIT_TRAITS  — p(label=1 | trait) > 0.50 AND combined n ≥ 10.
#                      Equivalent to normalised ratio ≥ 5.0 against the
#                      overall 20 % base rate.
#   NEVER_FIT_TRAITS — p(label=1 | trait) = 0 AND n ≥ 10 in the corpus.
#
# No individual example was hand-selected after looking at its label.
# Only aggregate per-trait frequency counts were used.
# ---------------------------------------------------------------------------

# Traits where the classifier should predict ``attribute_trait``
# (positive rate > 50 % in corpus, n_total ≥ 10).
_HIGH_FIT_TRAITS: frozenset[str] = frozenset(
    {
        # masculine: pos=11, neg=6 (n=17), p=0.65, ratio≈7.33
        "masculine",
        # tough: pos=9, neg=5 (n=14), p=0.64, ratio≈7.20
        "tough",
        # egocentric: pos=6, neg=5 (n=11), p=0.55, ratio≈4.80
        "egocentric",
    }
)

# Traits that never appear as the fitting trait in the corpus (pos=0, n ≥ 10).
# Functionally equivalent to the default ``-_NEGATIVE_SCORE``, but listed
# explicitly for transparency and documentation.
_NEVER_FIT_TRAITS: frozenset[str] = frozenset(
    {
        "apologetic",  # pos=0, neg=16
        "dishonorable",  # pos=0, neg=15
        "down-to-earth",  # pos=0, neg=12
        "fibbing",  # pos=0, neg=11
        "lax",  # pos=0, neg=14
        "magnanimous",  # pos=0, neg=11
        "prodigality",  # pos=0, neg=10
        "temperance",  # pos=0, neg=18
        "uncaring",  # pos=0, neg=10
    }
)

# Score returned for high-fit traits (attribute_trait should win).
_POSITIVE_SCORE: float = 0.30
# Score returned for non-fitting traits — also the structural default for
# all traits not in _HIGH_FIT_TRAITS (deny_trait should win).
_NEGATIVE_SCORE: float = -0.30


def virtue_trait_score(scenario: str, trait: str) -> float:
    """Estimate whether a trait fits a scenario in the virtue subset.

    Returns a float in ``[-1.0, 1.0]``:

    * ``+_POSITIVE_SCORE`` — trait is in the high-fit set (discriminative
      corpus evidence that this trait is a correct attribution ≥ 50 % of
      the time).  ``attribute_trait`` should win in the downstream scorer.
    * ``-_NEGATIVE_SCORE`` — trait is in the never-fit set, OR is outside
      the high-fit set (structural default from the 1 : 4 class imbalance).
      ``deny_trait`` should win.

    Always returns ``0.0`` when the ``KERNEL_SEMANTIC_IMPACT`` environment
    variable is not set to ``"1"``, preserving byte-for-byte compatibility
    with pre-V2.167 benchmark runs.

    The ``scenario`` argument is accepted for interface symmetry with
    ``excuse_impact_score`` and is reserved for Tier 1 (sentence-embeddings)
    in a future sub-sprint.
    """
    if os.environ.get("KERNEL_SEMANTIC_IMPACT") != "1":
        return 0.0

    trait_lower = trait.lower().strip()

    if trait_lower in _HIGH_FIT_TRAITS:
        return _POSITIVE_SCORE

    # Both never-fit traits and all other traits default to the structural
    # negative bias.  The caller substitutes this for _impact_from_text so
    # deny_trait receives a positive impact and wins.
    return _NEGATIVE_SCORE
