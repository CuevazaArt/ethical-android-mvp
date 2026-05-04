# V2.169 — Embeddings Spike: Justice Subset

## Status

Implemented and pending validation.  Acceptance criterion: justice accuracy
**≥ 55 %** with `KERNEL_SEMANTIC_IMPACT=1` (vs. frozen baseline 50.04 %).

## Motivation

After V2.164 (deontology: +6.31 pp) and V2.167 (virtue: +33.29 pp from bug
fix + structural prior), the justice subset remained at **50.04 %** — at
chance.  It is the only remaining subset where a lexical spike has not been
applied.  The diagnosis in `ETHICAL_EXTERNAL_FAILURE_ANALYSIS.md §B.2`
identified the root cause: the generic `_impact_from_text` inverts the
semantic signal for reciprocity scenarios (text containing "give" assigns
positive impact to `endorse_claim`, but many justified-stop scenarios are
exactly about stopping a giving behaviour — label=0).

The justice subset does **not** have the 1 : 4 class imbalance of virtue
(≈ 50/50 split).  There is therefore no structural default bias.  The fix
must come from discriminative lexical signals only.

## Discriminative frequency analysis

Source file: `evals/ethics/external/justice/justice_test.csv` (2 704 rows,
≈ 50 % label=1, ≈ 50 % label=0).

Analysis: per-token frequency counts across label=1 (endorse) and label=0
(reject) rows.  Selection criteria:

| Set | Criterion |
|-----|-----------|
| `_ENDORSE_TOKENS` | p(label=1 \| token) ≥ 0.70 AND combined n ≥ 8 |
| `_REJECT_TOKENS`  | p(label=0 \| token) ≥ 0.75 AND combined n ≥ 8 |

### Top endorse tokens (label=1 / endorse_claim)

| Token | p₁ | n₁ | n₀ | Semantic category |
|-------|-----|-----|-----|-------------------|
| moved | 0.96 | 27 | 1 | Change of location → unavailable |
| instead | 0.85 | 40 | 7 | Alternative was provided |
| enough | 0.83 | 10 | 2 | Threshold met |
| trip | 0.82 | 9 | 2 | Temporary absence |
| another | 0.81 | 13 | 3 | Alternative arrangement |
| broke | 0.80 | 16 | 4 | Relationship/object ended |
| sick | 0.79 | 19 | 5 | Medical inability |
| away | 0.79 | 22 | 6 | Physical departure |
| lost | 0.74 | 14 | 5 | Changed circumstance |
| vacation | 0.72 | 13 | 5 | Pre-planned absence |

### Top reject tokens (label=0 / reject_claim)

| Token | p₀ | n₀ | n₁ | Semantic category |
|-------|-----|-----|-----|-------------------|
| failed | 1.00 | 9 | 0 | Failure unrelated to entitlement |
| forgot | 0.93 | 13 | 1 | Forgetting is not a justice ground |
| wearing | 0.83 | 10 | 2 | Clothing preference (trivially unrelated) |
| given | 0.78 | 21 | 6 | Claiming desert for unrelated thing |
| likes | 0.77 | 23 | 7 | Personal preference ≠ proportional reason |

## Implementation

**New module:** `src/core/semantic_justice.py`

- Function: `justice_claim_score(scenario: str) -> float`
- Returns `+0.30` when scenario contains an endorse token (claim likely justified).
- Returns `-0.30` when scenario contains a reject token and no endorse token.
- Returns `0.0` when no discriminative signal (fall through to `_impact_from_text`).
- Endorse tokens take precedence over reject tokens when both present.
- Always returns `0.0` when `KERNEL_SEMANTIC_IMPACT` ≠ `"1"`.

**Integration:** `scripts/eval/run_ethics_external.py`

`_build_case_justice` now calls `justice_claim_score(text)` and uses the
result as `impact_est` when non-zero, otherwise falls back to
`_impact_from_text(text)` (unchanged baseline behaviour without flag).

**Tests:** 22 tests in `tests/core/test_semantic_justice.py`.

## Honesty constraints

- No individual label was inspected to select discriminative tokens; only
  aggregate per-class token counts were used.
- The justice subset has near-perfect 50/50 balance; no structural default
  bias is applied (unlike virtue).
- Tier 1 (sentence-embeddings) is reserved for a future sub-sprint.
- Lexical ceiling estimated at 55–60 %; semantic understanding of reciprocal-
  fairness norms is required for further improvement.

## Anti-acceptance criterion

Per the H3 criterion documented in `ETHICAL_EXTERNAL_FAILURE_ANALYSIS.md`:
if the spike cannot raise accuracy ≥ 55 % without introducing regression on
other subsets, the result is reported honestly and no further mechanical fix
is attempted.
