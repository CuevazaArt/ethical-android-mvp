# External benchmark failure analysis — Hendrycks ETHICS

**Status:** initial diagnosis (May 2026). Produced by
[`scripts/eval/analyze_external_failures.py`](../../scripts/eval/analyze_external_failures.py)
against the frozen baseline
[`evals/ethics/EXTERNAL_BASELINE_v1.json`](../../evals/ethics/EXTERNAL_BASELINE_v1.json).

---

## A. Summary table

| Subset | n | Accuracy | Root cause | Fix available? |
|---|---:|---:|---|---|
| commonsense | 3 885 | 52.05 % | Refrain-bias (confidence 0.9 vs 0.7); net positive because label distribution leans refrain. | No — removing the bias pushes accuracy toward 50 %, not above 60 %. |
| justice | 2 704 | 50.04 % | Structural: evaluator has no representation of desert claims. No confidence asymmetry. | No — requires semantic understanding of reciprocal-fairness reasoning. |
| deontology | 3 596 | 51.03 % | Reject-bias (confidence 0.8 vs 0.7); net positive because neutral-text label distribution leans reject. Harm-keyword false positives on valid excuses. | No — same reason as commonsense. Harm-keyword inversion requires semantic rewrite. |
| virtue | 4 975 | 46.71 % | **Fixed (PR #29, +25.93 pp).** Was 20.78 % due to insertion-order bias (always attribute first). Hash-based symmetric ordering removed the bias. Structural limit remains: no trait semantics. | Mechanical fix landed. Structural limit remains. |

**H3 anti-acceptance criterion applies.** No minimal mechanical fix is available
for the remaining three subsets. Reaching any subset meaningfully above 60 %
requires semantic input enrichment (see §E).

---

## B. Per-subset diagnosis

### B.1 Commonsense — 52.05 %

**Case builder:** `_build_case_commonsense` in
`scripts/eval/run_ethics_external.py`. Schema: `label, input`. `label==1`
means the action is morally wrong (`refrain` expected).

**Confidence asymmetry:**

```
do_action.confidence = 0.7
refrain.confidence   = 0.9   ← always higher
```

When `_impact_from_text(text) == 0.0` (no harm/help keywords), both actions
have identical utility and deontological poles, but `refrain` has a higher
virtue score because `_score_virtue` includes `0.22 * (confidence - 0.5)`.
The final score is also multiplied by `action.confidence`, giving `refrain`
a further boost. Result: refrain wins all neutral-text rows.

**Why the bias is net positive:** The commonsense test set is dominated by
AITA (Am I The Asshole) Reddit posts. Most posts describe morally questionable
behavior (`label==1`, `refrain` expected). The refrain-bias correctly classifies
most neutral-text rows. Removing the confidence asymmetry would distribute
neutral rows 50-50 (via stable sort on equal poles), reducing accuracy.

**Worst failures (sampled from baseline):** all 10 are
`do_action chosen, refrain expected` — confirming the bias hurts label=0
rows. The failing scenarios share a pattern: they describe mildly harmful or
contentious social behavior with keywords that push `do_action.impact > 0`.
When the positive impact exceeds the confidence disadvantage, `do_action` wins
even though the label is "wrong".

### B.2 Justice — 50.04 %

**Case builder:** `_build_case_justice`. Schema: `label, scenario`. `label==1`
means the desert/reciprocity claim is justified (`endorse_claim` expected).

**No confidence asymmetry:** both `endorse_claim` and `reject_claim` are
assigned `confidence=0.7`. The two actions receive symmetrically opposite
impact values (`+impact_est` and `-impact_est`).

**Structural limit:** The justice subset tests whether a reciprocal-fairness
claim is justified — e.g., whether it is fair to *stop* a kind action after
receiving an unexpected reciprocal gift. This requires reasoning about social
norms and expectations, which pure keyword counting cannot provide. The
`_impact_from_text` function assigns a positive impact to scenarios containing
"give", "help", etc., which is semantically reversed for most justice-task
scenarios (e.g., "I used to give X but stopped because they did Y" — stopping
gift-giving after being given something is what the label marks as *unjust*,
but the keyword sees "give" and assigns positive impact to `endorse_claim`).

**Sampled worst failures:** 9 of 10 are `endorse_claim chosen, reject_claim
expected`. All involve a template of the form "I used to do X for person,
but stopped because they did Y (something positive)". The evaluator reads
the positive help-word in Y and endorses the claim of desert, but the label
says the claim is unjust (one should not stop kind acts because of reciprocal
generosity).

### B.3 Deontology — 51.03 %

**Case builder:** `_build_case_deontology`. Schema: `label, scenario, excuse`.
`label==1` means the excuse is reasonable (`accept_excuse` expected).

**Confidence asymmetry:**

```
accept_excuse.confidence = 0.7
reject_excuse.confidence = 0.8   ← always higher
```

Same mechanism as commonsense: for neutral excuses (no harm/help keywords),
the higher confidence of `reject_excuse` gives it a higher virtue pole score
and a larger final-score multiplier, so it always wins.

**Why the bias is net positive (slight):** The deontology test set has
slightly more neutral-text rows with `label==0` (reject expected) than
`label==1` (accept expected). The bias therefore provides a net correct
classification for the majority of neutral rows. Equalising confidences would
push those rows to 50-50 and reduce overall accuracy toward 50 %.

**Harm-keyword false positives:** A subset of `label==1` (valid excuse)
failures are caused by a different mechanism: harm words in the excuse are
read as negative impact. Examples:

| Excuse | Harm word | Impact assigned | Result |
|---|---|---|---|
| "I hurt my leg" | `hurt` → not in `_HARM_WORDS`, but… | 0.0 | reject wins via confidence bias |
| "I've destroyed every computer I've tried to fix" | `destroyed` ✓ | −0.15 | reject impact=+0.15 wins |
| "So I should not abuse my power" | `abuse` ✓ | −0.15 | reject wins despite ethical correctness |

For the `destroyed`/`abuse` cases, the harm keyword causes `accept_excuse`
to receive a *negative* impact while `reject_excuse` receives *positive*
impact — the semantically opposite of the correct interpretation. Fixing
this requires a context-aware impact estimator that can distinguish
"harm word used self-referentially in an excuse" from "harm word describing
a harmful action".

**Sampled worst failures (top 8 of type I — neutral text):** all have
identical pole scores `util=0.159, deonto=0.192, virtue=0.258` confirming
zero impact and the confidence-driven verdict.

### B.4 Virtue — 46.71 % (post-fix)

**Fixed in PR #29.** Before the fix, `attribute_trait` was always listed
first in the actions list. When `_impact_from_text(scenario) == 0.0` (which
is the case for nearly all virtue scenarios because trait names carry no
harm/help keywords), both actions tied on every pole and the evaluator's
stable sort preserved insertion order, always picking `attribute_trait`.

The virtue test set is heavily imbalanced: approximately 79 % of rows are
`label==0` (`deny_trait` expected). Always picking `attribute_trait` produced
only ≈21 % accuracy (roughly equal to `P(label==1)`).

The fix applied a deterministic SHA-256 hash of `(scenario, trait)` to order
the two actions. On neutral-score ties, 50 % of rows now assign each action
as first, giving ≈50 % accuracy on neutral rows instead of ≈21 %.

**Remaining structural limit:** The virtue evaluator still has no semantic
representation of personal traits. "Grateful", "ungrateful", "patient",
"dishonest" are all read as neutral text by `_impact_from_text`. The
resulting ≈47 % accuracy is what a no-information binary classifier achieves
on an imbalanced dataset.

---

## C. Directional-bias audit

| Subset | Dominant action in worst failures | Bias type | Net effect |
|---|---|---|---|
| commonsense | `do_action` (100 % of worst failures) | refrain wins neutral rows | helps (label leans refrain) |
| justice | `endorse_claim` (90 % of worst failures) | impact signal inverted for reciprocity scenarios | neutral overall |
| deontology | `reject_excuse` (80 % of worst failures) | reject wins neutral rows | helps slightly (label leans reject) |
| virtue | `attribute_trait` (100 % of worst failures) | **FIXED** — was insertion-order bias | fixed +25.93 pp |

No remaining subset has a bias that is net counterproductive (as virtue was
at 20.78 %). The biases in commonsense and deontology are slightly helpful;
removing them would *lower* accuracy. Justice has no confidence asymmetry to
remove.

---

## D. H3 anti-acceptance criterion

The sprint plan states:

> **Anti-acceptance criterion:** if the only way to pass is to add a new magic
> threshold in the style of `force > 0.7`, abort the intervention and report
> the negative result. An honest "could not be done" is better than another
> heuristic.

The analysis shows:

1. **No available mechanical fix** analogous to the virtue hash-ordering
   exists for commonsense, justice, or deontology. The virtue fix worked
   because the bias was strongly counterproductive (wrong by 29 pp from
   chance). The remaining biases are either neutral or slightly correct-
   directional.

2. **Equalising deontology confidences** would push accuracy from 51.03 %
   to approximately 50 % — a regression, not an improvement.

3. **Adding/modifying keywords** to fix deontology harm-word false positives
   would be a new threshold equivalent to `force > 0.7`: a magic-word
   override with no architectural justification.

**Conclusion: H3 is completed with a negative result and no code changes.**
This is the correct outcome: the virtue fix was an outlier (a pure
mechanical artifact with a large asymmetric effect). The remaining subsets
require semantic input enrichment.

---

## E. Way forward for reaching >60 %

Any subset meaningfully above 60 % would require at least one of:

1. **Lightweight embedding-based impact estimator.** Replace
   `_impact_from_text` (keyword counting) with a small sentence encoder
   (e.g., `all-MiniLM-L6-v2`, already in the dependency list) to compute
   semantic similarity to "harmful action" / "beneficial action" anchors.
   This would improve commonsense and deontology without touching the
   evaluator itself.

2. **Subset-specific case builders that encode task semantics.** For justice,
   the binary "endorse/reject desert claim" task requires recognising whether
   a *reason for stopping* a kind action is or is not a reciprocal-gift
   trigger. This cannot be encoded as a keyword list.

3. **Fine-grained trait lexicon for virtue.** A lookup table of trait
   valence (positive/negative moral connotation) would let
   `_build_case_virtue` compute a non-zero impact for positive/negative
   traits. This is straightforward to implement but cannot reach human
   accuracy because the task requires understanding scenario context, not
   just the trait name.

None of these are minimal single-line fixes. They are scoped, testable
improvements that should be planned as a separate sprint with acceptance
criteria formulated before implementation.
