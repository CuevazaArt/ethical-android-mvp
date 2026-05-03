# Ethical benchmark — external validation vs. circular self-score

**Status:** implementation landed (May 2026). The original policy section
below is preserved for historical context; the new sections at the top
report the first external measurement.

**Related:** [`scripts/eval/run_ethics_external.py`](../../scripts/eval/run_ethics_external.py),
[`evals/ethics/EXTERNAL_BASELINE_v1.json`](../../evals/ethics/EXTERNAL_BASELINE_v1.json),
[`evals/ethics/external/README.md`](../../evals/ethics/external/README.md),
[`tests/eval/test_run_ethics_external.py`](../../tests/eval/test_run_ethics_external.py),
[ETHICAL_BENCHMARK_BASELINE.md](ETHICAL_BENCHMARK_BASELINE.md) (in-house
30-dilemma suite).

---

## A. Why this exists

The in-house suite at [`evals/ethics/dilemmas_v1.json`](../../evals/ethics/dilemmas_v1.json)
was authored by the same team that tunes the evaluator's pole weights
and contextual rules. Reaching 30/30 on it shows internal consistency,
not generalisation. Until the evaluator was measured against an
externally-published corpus, every downstream claim — operator sign-off,
v1.0 tag, audio hardware budget — was being built on top of an
unverified component.

This document records the first such measurement, the dataset chosen,
the mapping decisions, the result, and an honest reading of what the
number does and does not mean.

## B. Dataset chosen

**Hendrycks et al. ETHICS** — *"Aligning AI With Shared Human Values"*,
ICLR 2021 (<https://arxiv.org/abs/2008.02275>). Distributed under MIT
license at <https://github.com/hendrycks/ethics>; tarball at
<https://people.eecs.berkeley.edu/~hendrycks/ethics.tar>.

Reasons:

- **Externally authored.** No overlap with this project's contributors.
- **De-facto NLP ethics benchmark.** A number on it is interpretable by
  the wider community.
- **Five well-defined subsets** (Commonsense, Justice, Deontology,
  Virtue, Utilitarianism). Four map onto the binary "is this action
  ethically endorsed?" question the evaluator answers.
- **MIT licensed**, so subsets can be vendored or redistributed.

**Excluded:** the `Utilitarianism` subset, which is a pairwise
*ranking* task (rank scenarios by pleasantness). Forcing it through a
binary classifier would distort the result rather than measure it.

## C. Mapping decisions

For each example the runner constructs **two candidate `Action`s** ("do
the thing" vs. "refrain") and one `Signals` block, then asks the
evaluator to choose between them. Per-subset action names are listed in
`SUBSET_ACTIONS` at the top of
[`run_ethics_external.py`](../../scripts/eval/run_ethics_external.py).

The single most important property of the mapping is that **the label
is never read while building the input**. A regression test
(`test_mapping_does_not_peek_at_label`) enforces this: two rows whose
only difference is the label must produce identical actions and
signals.

Features used:

| Feature | How it is computed | Why this choice |
|---|---|---|
| `action.impact` | `0.15 * (#help_words − #harm_words)` clamped to `[-1, 1]`. Lexicons in `_HARM_WORDS` / `_HELP_WORDS`. | A real deployment uses an LLM to estimate impact. We need a deterministic stand-in that does not consult the label. Keyword counting is intentionally crude. |
| `action.force` | `0.5 * #force_words` clamped to `[0, 1]`. | Triggers the existing `force > 0.7` deontological-boost branch in `EthicalEvaluator.score_action`. |
| `action.confidence` | Fixed: `0.7` for "do", `0.9` for "refrain". | Refraining is treated as the higher-confidence baseline. |
| `signals.risk` | `0.4 * #harm_words`, capped at 1.0. | Same lexicon as `impact`; documented coupling. |
| `signals.urgency` / `vulnerability` | Binary on keyword presence. | Triggers existing stake multipliers in `_score_utilitarian`. |
| `signals.legality` | `0.3` if any `_ILLEGAL_WORDS` present, else `1.0`. | Triggers the deontological `legality_gap` penalty. |
| `signals.summary` | First 200 chars of the scenario. | Feeds `select_weights` (the contextual `_ABSOLUTE_RULE_MARKERS` / `_AGGREGATE_MARKERS` rule). |
| `signals.context` | Always `everyday_ethics`. | We have no labels for context; using a single value avoids implicit calibration. |

Per-subset specifics:

- **Commonsense** (`label, input`): "do_action" vs. "refrain". Expected
  action is `refrain` when `label == 1` (the scenario is wrong).
- **Justice** (`label, scenario`): "endorse_claim" vs. "reject_claim".
  Both actions get the same `|impact|` with opposite sign.
- **Deontology** (`label, scenario, excuse`): "accept_excuse" vs.
  "reject_excuse". Impact estimated from the excuse text only.
- **Virtue** (`label, scenario, trait`): "attribute_trait" vs.
  "deny_trait". Impact estimated from the scenario; the trait is
  surfaced in the action description but not in any feature.

## D. Result on the full Hendrycks ETHICS suite

Two measurements have been taken against the upstream `*_test.csv`
files (total 15 160 examples across four subsets).  The current
`EXTERNAL_BASELINE_v1.json` is the **virtue-symmetric** measurement
(2026-05-03, after the directional-bias fix); the **virtue-biased**
measurement (2026-05-03, before the fix) is kept here as a historical
reference of what the original §H trigger fired against.

Frozen baseline: [`evals/ethics/EXTERNAL_BASELINE_v1.json`](../../evals/ethics/EXTERNAL_BASELINE_v1.json)
with `"is_full_benchmark": true` and `"data_source": "external_csv"`.
The smoke baseline (57.7 % on 26 rows) is superseded by the full-suite
baseline; the `smoke_sample.csv` fixtures and the smoke-path code in
the regression test were removed in the previous sprint.

| Subset | n | virtue-biased run (2026-05-03, sha 8cdeb219) | virtue-symmetric run (2026-05-03, current) | Δ |
|---|---:|---:|---:|---:|
| commonsense | 3 885 | 52.05 % | 52.05 % | 0.00 pp |
| justice     | 2 704 | 50.04 % | 50.04 % | 0.00 pp |
| deontology  | 3 596 | 51.03 % | 51.03 % | 0.00 pp |
| virtue      | 4 975 | **20.78 %** | **46.71 %** | **+25.93 pp** |
| **overall** | **15 160** | **41.19 %** | **49.70 %** | **+8.51 pp** |

The change between the two runs is a single intervention in
`scripts/eval/_build_case_virtue`: the two virtue actions
(`attribute_trait` / `deny_trait`) are now ordered by a deterministic
hash of `(scenario, trait)`, so when the two actions tie on every
pole — which happens whenever the scenario carries no harm/help
lexical signal — the evaluator's stable-sort tie-break is symmetric
across the dataset instead of always favouring `attribute_trait`.
The fix touches only the case builder; the evaluator (poles, weight
selector, CBR) is unchanged, which is why commonsense / justice /
deontology accuracies are byte-identical.

## E. Honest reading

What the full-suite numbers tell us, after the virtue-bias fix:

1. **Commonsense leads, as expected from the smoke fixture (52 % vs.
   75 % smoke).** The commonsense subset is the closest task to
   "did the agent do a harmful action?" At scale the advantage shrinks
   because the keyword lexicons miss the long tail of harmful/benign
   scenarios not represented in the smoke rows.

2. **Justice and Deontology hover near 50 %.** Both subsets have
   symmetric `impact` signals for the two candidate actions; the
   evaluator has no internal representation of "desert" or "excuse
   reasonableness" and scores near chance. This matches the smoke
   reading and is confirmed at scale.

3. **Virtue is now near chance (≈47 %), as expected from a
   no-information classifier.** The previous 20.8 % was *worse* than
   chance because the case builder always listed `attribute_trait`
   first, and on ties the evaluator's stable sort always picked the
   first-listed action.  The virtue test set is dominated by
   `label==0` rows (≈4 wrong traits per 1 right trait per scenario),
   so always picking `attribute_trait` produced ≈21 % accuracy.
   With symmetric tie-break the directional bias is gone; what
   remains is the structural fact that the evaluator has **no
   semantic representation of personal traits** and therefore cannot
   discriminate "trustful" from "cynical" for the same scenario.
   Beating ≈50 % on virtue requires actual trait understanding, not
   tuning.

4. **Overall is now 49.7 %.** Still below 50 %, but only marginally.
   The sub-50 % §H trigger is therefore *attenuated* but not
   formally cleared.  See §H for the updated trigger status.

5. **This remains a structural limitation, not a tuning issue.**
   Re-tuning pole weights will not move the Justice / Deontology /
   Virtue numbers meaningfully; doing so would only inflate the
   in-house benchmark while the external numbers stayed where they
   are.  Lifting Virtue above ≈50 % requires representing traits as
   features the poles can actually score, which is out of scope for
   this sprint.

## F. Procedure to reproduce or refresh the full-suite baseline

A maintainer who wants to re-run with newer upstream files should:

```bash
python scripts/eval/run_ethics_external.py            # full suite
# inspect ETHICS_EXTERNAL_RUN_*.json
rm evals/ethics/EXTERNAL_BASELINE_v1.json
python scripts/eval/run_ethics_external.py --freeze-baseline
```

## H. Sprint trigger fired

**Original trigger (PR #29, virtue-biased run).** Full-suite overall
accuracy: **41.2 %** (6 244 / 15 160).  Per-subset: commonsense 52.1 %,
justice 50.0 %, deontology 51.0 %, virtue 20.8 %.

Applying the decision rules from section F to the original numbers:

- **≥70 % on any subset → resume sign-off / v1.0 work.**
  *Not fired.* No subset reaches 70 %.

- **<50 % overall → next sprint must be on the evaluator** (model of
  poles, weight selector, or feature inputs), **not on new product
  surface.**
  *Fired.* Overall accuracy was 41.2 %, below the 50 % threshold.
  This condition was the trigger for the current sprint.

- **High disparity between subsets → directed work on the contextual
  weight selector.**
  *Fired (secondary).* Virtue (20.8 %) was 31 percentage points below
  the next-lowest subset (Justice 50.0 %).  The diagnosis (PR for the
  current sprint) located the asymmetry in the **case builder**, not
  in the weight selector — so the directed work landed on
  `_build_case_virtue` instead.

**Updated status after the virtue-bias fix.** Per-subset:
commonsense 52.1 %, justice 50.0 %, deontology 51.0 %, virtue 46.7 %.
Overall 49.7 %.

- **≥70 % on any subset.**
  *Still not fired.* No subset reaches 70 %.

- **<50 % overall.**
  *Attenuated.* Overall is 49.7 %, ≈0.3 pp below the threshold.  The
  31 pp virtue gap that motivated this sprint is closed; the
  remaining sub-50 % gap is structural (the evaluator has no trait
  representation) and not a directional-bias failure.  A future
  sprint may either (a) accept ≈50 % on virtue as the ceiling for a
  no-trait-features classifier and stop firing this trigger, or (b)
  open targeted work on representing traits, which is explicitly out
  of scope for this sprint.

- **High disparity between subsets.**
  *No longer fired.* The new spread is commonsense 52.1 %, deontology
  51.0 %, justice 50.0 %, virtue 46.7 % — a 5.4 pp range, well within
  the noise band of a near-chance classifier.

The current sprint addressed the evaluator-vs-data plumbing (case
builder ordering) without touching the public evaluator contract or
any product surface.

## G. Non-goals

- Proving the evaluator is **ethically correct** in any absolute sense.
- Replacing legal, clinical, or safety review with a benchmark score.
- Treating any single LLM (GPT-4 / Claude / etc.) as ground truth in
  comparison studies.

---

# Historical: original policy note (April 2026)

*The text below predates the implementation. It is kept verbatim so the
history of the decision is auditable.*


---

## 1. The problem (non-circularity)

The kernel’s **invariant tests** ([`tests/test_ethical_properties.py`](../../tests/test_ethical_properties.py)) check **internal consistency** (MalAbs, buffer, no crash). The **nine batch simulations** ([`src/main.py`](../../src/main.py), [`src/simulations/runner.py`](../../src/simulations/runner.py)) are primarily **smoke / demo** runs: they show the pipeline completes, not that choices match **independent moral truth**.

Agreement metrics in [`run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) compare the kernel to:

- **Simple baselines** (`first`, `max_impact`) — legitimate **stress tests** of order bias and greedy impact.
- **`expected_decision` / `reference_action`** in the fixture — today **`pilot_reference_v1`** (maintainer-authored priors).

If the only “gold” labels are **defined inside the same project** as the rules, **agreement is not external validation**; it measures alignment with a **declared reference**, not philosophy-certified correctness.

---

## 2. What “external ethical benchmark” means (minimum bar)

To claim **non-circular** evaluation (research or product), you typically need **at least**:

| Element | Role |
|---------|------|
| **Independent reference** | Labels from **human experts** (or a **published** rubric + adjudication), not the same team that tuned pole weights. |
| **Documented rubric** | Dimensions (e.g. harm, rights, proportionality) and **how** actions map to scores; versioned (`rubric_v1`). |
| **Inter-rater reliability** | Multiple annotators + κ / agreement stats before treating labels as gold. |
| **Baselines** | Same scenarios fed to **other policies**: e.g. fixed heuristic, **frozen** LLM prompts (GPT/Claude) with **disclosed** system prompts — not ad-hoc cherry-picking. |
| **Separation** | Train/calibration vs **held-out** evaluation scenarios to avoid overfitting the reference. |

**Not sufficient alone:** high agreement with any single LLM — LLMs are not moral authorities; they are **additional baselines** for comparison studies.

---

## 3. What exists in this repository today

| Artifact | What it validates |
|----------|---------------------|
| Invariant suite | Core rules (Absolute Evil, etc.) — **internal** |
| Nine simulations | **Executability** and narrative coverage — **not** external ethics |
| [`labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) | `reference_standard.tier: internal_pilot` — **maintainer** `expected_decision` for agreement **metrics** |
| [`run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) | Kernel vs baselines vs reference — **comparative**, not “truth” |

This is **honest scope**: the repo ships **hooks and methodology**; **expert panels, IRB, and API baselines** are **out-of-repo process** unless you add them.

---

## 4. Roadmap — how to add a real external tier (suggested)

1. **Freeze** scenario text and action lists (`batch_id` 1–9 or expanded set).
2. **Recruit** annotators + ethics advisor; write **rubric** one page; store version in fixture metadata.
3. **Export** labels as `label_source: expert_human_<panel_id>_<date>` and set `reference_standard.tier` to `expert_panel` (or add a parallel fixture file to avoid breaking tests).
4. **Optional LLM baselines:** script that calls APIs with **fixed** prompts, logs model id + temperature; store outputs beside kernel runs; **never** treat LLM as ground truth.
5. **Report** agreement + disagreement cases explicitly in a paper or `artifacts/` run log.

---

## 5. Fixture metadata (`reference_standard`)

[`labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) includes a **`reference_standard`** block:

- **`tier`:** `internal_pilot` until an expert dataset is merged.
- **`summary`:** one-line honesty about label provenance.

When you add an expert-reviewed dataset, extend the schema (new tier + optional `panel_id`, `rubric_version`) and update tests in [`tests/test_labeled_scenarios.py`](../../tests/test_labeled_scenarios.py).

---

## 6. Non-goals

- Proving the kernel is **ethically correct** in any absolute sense.
- Replacing **legal**, **clinical**, or **safety** review with a benchmark score.
- Using agreement with **GPT-4/Claude alone** as validation without human rubric and disclosure.

---

*MoSex Macchina Lab — closes the “no external benchmark” documentation gap; implementation of expert data is a research / governance decision outside this file.*
