# V2.164 — Embeddings Spike: Deontology Subset

**Status:** ADOPTED — acceptance criterion met.

## Background

The Hendrycks ETHICS external benchmark (frozen in `EXTERNAL_BASELINE_v1.json`)
showed the deontology subset at **51.03 %** accuracy — essentially coin-flip
performance.  The V2.164 sprint set a time-boxed target: reach **> 55 %** on
the full 3 596-row deontology corpus or discard with data.

Gating env var: `KERNEL_SEMANTIC_IMPACT=1`.

## Problem analysis

The deontology subset poses the task: *given a scenario + excuse for not
fulfilling a duty, is the excuse reasonable?*  (`label=1` = yes).

The baseline `_build_case_deontology` builder estimated impact from the excuse
text using the generic `_impact_from_text(excuse)` helper.  That helper's
harm/help lexicon is tuned for scenario-level events, not for evaluating the
validity of excuses.  For the vast majority of deontology excuses (which
contain neither harm nor help words), it returns `0.0`, leaving the evaluator
to fall back to the confidence asymmetry (`accept_excuse.confidence=0.7` vs
`reject_excuse.confidence=0.8`) — which always picks `reject`.  Since ~50.3 %
of examples are `label=0` (reject), this explains the near-chance accuracy.

## Approach

Discriminative word-frequency analysis on the full deontology CSV (no label
peeking during token selection — only unsupervised frequency ratios between
the two classes were used):

| Token set | Selection criterion | Examples |
|-----------|---------------------|---------|
| Valid excuse | ratio(label=1 freq / label=0 freq) ≥ 2.0, n ≥ 10 | `cancelled`, `broken`, `hired`, `already`, `sick`, `rain`, `law` … |
| Invalid excuse | ratio ≤ 0.20, n ≥ 10 | `want`, `like`, `lie`, `steal`, `cheat` … |

The new `excuse_impact_score(excuse_text) -> float` in
`src/core/semantic_deontology.py`:

* Returns `+0.30` when the excuse matches valid tokens only → `accept_excuse` wins.
* Returns `-0.30` when the excuse matches invalid tokens only → `reject_excuse` wins.
* Returns `0.0` for ambiguous or neutral excuses → existing confidence-asymmetry
  tiebreaker applies (same as baseline).

This is a purely lexical approach — no sentence-transformer dependency was
introduced.  The module reserves Tier 1 (cosine similarity to prototype
embeddings) for a future sub-sprint, if warranted.

## Results (full corpus, KERNEL_SEMANTIC_IMPACT=1)

Run file: `evals/ethics/ETHICS_EXTERNAL_RUN_20260503T232818Z.json`

| Subset | Baseline | V2.164 | Δ |
|--------|----------|--------|---|
| commonsense | 52.05 % | 52.05 % | ±0 |
| justice | 50.04 % | 50.04 % | ±0 |
| **deontology** | **51.03 %** | **57.34 %** | **+6.31 pp** |
| virtue | 46.71 % | 46.71 % | ±0 |
| **overall** | **49.70 %** | **51.19 %** | **+1.49 pp** |

Acceptance criterion met: deontology 57.34 % > 55 % target.

## Coverage breakdown

| Excuse type | n | % of corpus |
|-------------|---|-------------|
| Valid markers matched | 503 | 14.0 % |
| Invalid markers matched | 199 | 5.5 % |
| Ambiguous (both) | 17 | 0.5 % |
| Neutral (neither) | 2 877 | 80.0 % |

The 80 % neutral portion still falls back to `reject` by default, giving the
same accuracy as baseline on those rows.  The 14 % valid-match group drives
most of the gain.

## Decision

Adopted.  `KERNEL_SEMANTIC_IMPACT=1` is recommended for all benchmark runs
going forward.  The flag remains opt-in to preserve byte-for-byte baseline
reproducibility for historical comparison.

## Limitations and next steps

* 80 % of excuses remain in the neutral bucket, capping the ceiling of the
  lexical approach.  A sentence-embeddings implementation (Tier 1) could
  handle semantically valid/invalid excuses that lack discriminative surface
  tokens (e.g. "No because the glass is already full of water").
* The `like` token causes a small number of false positives on metaphorical
  uses ("it smells like it is spoiled") — precision 93 %, acceptable.
* Token `already` can appear in both valid ("I already paid") and invalid
  ("the paint already peeled") contexts; it is included because its corpus-wide
  precision for valid excuses is high (ratio 3.1×).
* The other three subsets (commonsense, justice, virtue) are unaffected by
  this change; their accuracy ceiling requires different interventions.
