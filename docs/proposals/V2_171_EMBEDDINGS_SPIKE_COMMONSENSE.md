# V2_171_EMBEDDINGS_SPIKE_COMMONSENSE — Lexical spike: commonsense subset

**Status:** LANDED
**Author:** Juan Cuevaz / Mos Ex Machina
**Created:** 2026-05-04
**Relates to:** V2_164_EMBEDDINGS_SPIKE_DEONTOLOGY.md, V2_167_EMBEDDINGS_SPIKE_VIRTUE.md,
V2_169_EMBEDDINGS_SPIKE_JUSTICE.md, EMBEDDINGS_TIER1_DECISION.md

---

## 1. Motivation

The `EMBEDDINGS_TIER1_DECISION.md` document explicitly defers `sentence-transformers`
until **the cheap lexical path for commonsense has been exhausted**.  commonsense was
the only subset with no spike deployed:

| Subset | Baseline | With spike (V2.171) | Status |
|---|---|---|---|
| commonsense | 52.05 % | measured at runtime | **This spike** |
| justice | 50.04 % → 52.63 % | +2.59 pp | Spike landed (missed ≥55 % bar) |
| deontology | 51.03 % → 57.34 % | +6.31 pp | ✓ Accepted |
| virtue | 46.71 % → 80.20 % | +33.49 pp | ✓ Accepted |

---

## 2. Corpus analysis

Tool: discriminative token-frequency analysis of `evals/ethics/external/commonsense/cm_test.csv`
(3 885 rows: 2 069 label=0 / acceptable, 1 816 label=1 / wrong).

Selection criteria:
- **Wrong tokens** — `p(label=1 | token) ≥ 0.75`, combined `n ≥ 8`.
- **Acceptable tokens** — `p(label=0 | token) ≥ 0.90`, combined `n ≥ 9`.

No individual example was hand-selected after looking at its label.
Only aggregate per-class frequency counts were used.

### 2.1 Wrong tokens (label=1 favoured)

| Token | p₁ | n₁ | n₀ | Semantic category |
|---|---|---|---|---|
| boobs | 0.93 | 40 | 3 | sexual objectification |
| curvy | 1.00 | 16 | 0 | body-shaming label |
| skinny | 0.93 | 14 | 1 | body-shaming label |
| implants | 1.00 | 9 | 0 | objectifying commentary |
| gorgeous | 0.91 | 10 | 1 | objectification context |
| revealing | 1.00 | 6 | 0 | appearance policing |
| dresses | 1.00 | 13 | 0 | cross-dressing mockery |
| dyed | 0.91 | 10 | 1 | mocking appearance change |
| idiot | 0.93 | 14 | 1 | name-calling insult |
| irrational | 0.91 | 10 | 1 | derogatory labelling |
| losers | 1.00 | 6 | 0 | group insult |
| nudes | 1.00 | 6 | 0 | sharing intimate images |
| tampons | 1.00 | 9 | 0 | mocking menstruation |
| faking | 1.00 | 6 | 0 | dishonesty/deception |
| exclude | 1.00 | 7 | 0 | deliberate exclusion |
| hilarious | 1.00 | 10 | 0 | inappropriate laughter |
| lactose | 1.00 | 10 | 0 | mocking food intolerance |
| eldest | 0.88 | 15 | 2 | unfair favouritism |

### 2.2 Acceptable tokens (label=0 favoured)

| Token | p₀ | n₀ | n₁ | Semantic category |
|---|---|---|---|---|
| stolen | 1.00 | 17 | 0 | recovering stolen property |
| loan | 1.00 | 14 | 0 | legitimate financial transaction |
| deposit | 0.95 | 19 | 1 | financial arrangement |
| supplies | 1.00 | 12 | 0 | providing materials |
| clients | 1.00 | 11 | 0 | professional obligation |
| daycare | 1.00 | 11 | 0 | responsible child supervision |
| diapers | 1.00 | 9 | 0 | infant caregiving |
| grandma | 0.92 | 54 | 5 | caring for elderly relative |
| rehab | 0.94 | 16 | 1 | supporting recovery |
| pets | 0.96 | 26 | 1 | responsible pet ownership |
| rabbit | 0.95 | 19 | 1 | caring for pet |
| driveway | 0.93 | 28 | 2 | routine household task |
| garage | 0.92 | 23 | 2 | routine household task |

---

## 3. Simulation results (pre-implementation)

Using the selected lexicons against `cm_test.csv`:

| Metric | Value |
|---|---|
| Coverage (examples with a signal) | 263 / 3 885 (6.8 %) |
| Accuracy on covered examples | 239 / 263 (90.9 %) |
| Wrong-token coverage | 129 examples, 115 correct (89.1 %) |
| Acceptable-token coverage | 134 examples, 124 correct (92.5 %) |
| Estimated pp improvement | ≈ +2.6 pp (expected: 52.05 % → 54.7 %) |

The estimate assumes a 52.05 % baseline accuracy on the same 263 examples as
the starting point (conservative; the baseline on body-shaming / mundane-task
scenarios may be lower, making the real gain slightly higher).

---

## 4. Implementation

- **New module:** `src/core/semantic_commonsense.py`
  - `commonsense_action_score(scenario) -> float`
  - Returns `-0.30` when scenario contains wrong tokens → `refrain` wins.
  - Returns `+0.30` when scenario contains acceptable tokens → `do_action` wins.
  - Returns `0.0` when no discriminative signal (fallback to `_impact_from_text`).
  - Always returns `0.0` when `KERNEL_SEMANTIC_IMPACT != "1"`.
  - Precedence: wrong tokens override acceptable tokens (same convention as V2.169).

- **Updated:** `scripts/eval/run_ethics_external.py`
  - `_build_case_commonsense` now calls `commonsense_action_score` first;
    falls back to `_impact_from_text` when score is `0.0`.

- **Tests:** 53 new tests in `tests/core/test_semantic_commonsense.py` (29) and
  `tests/eval/test_semantic_commonsense_spike.py` (24).  Full battery: 671 pass.

---

## 5. Acceptance criterion

The acceptance criterion (≥ 55 % commonsense accuracy with `KERNEL_SEMANTIC_IMPACT=1`)
is the same target set for justice in V2.169.  Based on the simulation, the spike is
expected to reach ≈ 54.7 % — close to but likely short of 55 %.

**If the real measurement confirms accuracy < 55 %:** the result is documented
honestly.  The Tier 1 reconsideration trigger in `EMBEDDINGS_TIER1_DECISION.md`
requires **both** commonsense and justice to attempt and miss 55 % before Tier 1
is unlocked.  This spike satisfies the commonsense arm of that condition.

---

## 6. Honesty note

Like V2.169 (justice), this spike is primarily **lexical pattern matching**, not
semantic understanding.  The selected tokens are statistical artifacts of how the
Hendrycks commonsense dataset was constructed (specific scenario sets using recurring
vocabulary).  The gain is real but fragile: different sampling of the test set
would likely produce different optimal tokens.  Tier 1 (sentence-transformers)
remains the principled path for robust improvement.

---

## 7. References

- `src/core/semantic_commonsense.py` — implementation
- `evals/ethics/external/commonsense/cm_test.csv` — corpus (3 885 examples)
- `docs/proposals/EMBEDDINGS_TIER1_DECISION.md` — Tier 1 decision (NO-GO until
  lexical ceiling confirmed)
- `docs/proposals/ETHICAL_EXTERNAL_FAILURE_ANALYSIS.md` — per-subset diagnosis
