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

## D. Result on the bundled smoke fixture

The repository ships a small bundled fixture
(`evals/ethics/external/<subset>/smoke_sample.csv`, 6–8 rows per
subset, 26 rows total). It exists so the script and the regression
test can run with **no internet access**. It is **not** the full
benchmark; the `EXTERNAL_BASELINE_v1.json` file marks it explicitly
with `"data_source": "bundled_smoke_fixture"` and
`"is_full_benchmark": false`.

First (and frozen) measurement on the smoke fixture:

| Subset | n | passes | accuracy |
|---|---:|---:|---:|
| commonsense | 8 | 6 | **75.0 %** |
| justice | 6 | 3 | 50.0 % |
| deontology | 6 | 3 | 50.0 % |
| virtue | 6 | 3 | 50.0 % |
| **overall** | **26** | **15** | **57.7 %** |

This number is frozen in
[`evals/ethics/EXTERNAL_BASELINE_v1.json`](../../evals/ethics/EXTERNAL_BASELINE_v1.json)
and not retried.

## E. Honest reading

What the smoke-fixture number does *and does not* tell us:

1. **It is not the benchmark result.** 26 rows is plumbing
   verification. The full Hendrycks suite has tens of thousands of test
   rows. The smoke result must not be cited as "the evaluator scores
   58 % on ETHICS".

2. **The 75 % on Commonsense is interpretable plumbing.** The
   commonsense subset is the closest to the kind of "did the agent do
   a harmful action?" question the evaluator was actually designed for.
   On a tiny harm-vs-help fixture it picks the right side most of the
   time. This is the only subset where the evaluator's structure
   roughly matches the task.

3. **The 50 % on Justice / Deontology / Virtue is informative even at
   this scale.** The evaluator has no internal representation of *"is
   this claim of desert fair?"*, *"is this excuse for a duty
   reasonable?"*, or *"does this trait fit this behaviour?"* — and the
   smoke result reflects that. Both candidate actions in those subsets
   carry symmetric `impact`, and the keyword-derived signals do not
   discriminate between the labels. The evaluator scores them at
   chance.

4. **This is a structural limitation, not a tuning issue.** Re-tuning
   pole weights will not move the Justice/Deontology/Virtue numbers
   meaningfully, because the input the evaluator sees does not contain
   the information the task is asking about.

## F. Procedure to produce the full-suite baseline

A maintainer with network access to `people.eecs.berkeley.edu` (or who
manually places the upstream `*_test.csv` files into
`evals/ethics/external/<subset>/`) should:

```bash
python scripts/eval/run_ethics_external.py --download
python scripts/eval/run_ethics_external.py            # without --use-smoke
# inspect ETHICS_EXTERNAL_RUN_*.json
rm evals/ethics/EXTERNAL_BASELINE_v1.json
python scripts/eval/run_ethics_external.py --freeze-baseline
```

The result, whatever it is, should land in the same PR that updates the
"Result" section of this document. **Do not** attempt to "improve" the
number before freezing it. The next sprint's plan depends on knowing
the unmodified value:

- ≥70 % on any subset → there is enough evidence of generalisation to
  resume operator-sign-off / `v1.0` tag work.
- <50 % overall → the next sprint must be on the evaluator (model of
  poles, weight selector, or feature inputs), not on new product
  surface.
- Highly uneven per-subset → the contextual weight selector needs
  directed work.

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
