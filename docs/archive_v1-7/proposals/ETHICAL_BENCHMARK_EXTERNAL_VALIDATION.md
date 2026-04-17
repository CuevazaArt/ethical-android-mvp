# Ethical benchmark — external validation vs. circular self-score

**Status:** policy + backlog (April 2026).  
**Related:** [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md), [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) (Issue 3), [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json), [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py).

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
