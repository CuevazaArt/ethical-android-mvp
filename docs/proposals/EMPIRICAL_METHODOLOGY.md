# Empirical methodology — internal agreement, not moral certification (Issue 3)

**Purpose:** Explain how to **interpret** human-labeled scenarios, baseline comparisons, and agreement metrics for the Ethos Kernel **without** claiming product certification, legal safety, or objective moral truth.

**Related:** [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) (Issue 3), [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md) (batch pilot mechanics), [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json), [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json), [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py), invariant suite [`tests/test_ethical_properties.py`](../../tests/test_ethical_properties.py), [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md).

---

## 1. What automated tests already prove

| Layer | What it shows | What it does **not** show |
|--------|----------------|---------------------------|
| **`tests/test_ethical_properties.py`** and related | **Internal consistency** of the wired pipeline (MalAbs → buffer → Bayes → …) under declared invariants | Alignment with any external “correct” ethics |
| **Empirical pilot (`run_empirical_pilot.py`)** | **Agreement rates** between kernel choices, simple baselines, and **optional** human priors on a **fixed** action set | That those priors are universally valid or legally sufficient |

**Disclaimer (required in publications and operator-facing claims):** results from this repository’s empirical fixtures are **not** product certification, regulatory approval, or evidence that the kernel is “moral” in the real world.

---

## 2. Dataset: `labeled_scenarios.json`

The fixture [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) has two harness types:

| `harness` | Meaning |
|-----------|---------|
| **`batch`** | Executable with the canonical batch runner (`ALL_SIMULATIONS` in [`src/simulations/runner.py`](../../src/simulations/runner.py)). Each row has `batch_id` **1–9** and an `expected_decision` (action **name** from that scenario’s candidate list). |
| **`annotation_only`** | **Not** executed by the batch runner. Short **vignettes** for **inter-rater** design, training materials, or future catalog expansion. `related_batch_id` ties them thematically to a batch sim; `expected_decision` is still an action name from **that** sim’s candidate list so labels stay comparable in principle. |

Fields such as `label_source` document provenance (e.g. pilot reference vs synthetic illustration). **Synthetic** rows may include **contested** priors on purpose to measure disagreement and protocol stability.

---

## 3. Metrics (kernel vs baseline vs label)

From [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py), on **`harness: batch`** rows only:

- **Agreement (kernel vs label):** fraction of rows where `final_action` equals `expected_decision` / `reference_action`.
- **Baselines:** **first** (list-order) and **max_impact** (greedy on stated `estimated_impact`) on the **same** candidate lists — stress tests for order bias and impact priors, not “ground truth.”
- **Kernel vs baselines:** fraction of scenarios where the kernel matches each baseline (descriptive divergence, not a moral score).

Low agreement with a human panel is **data**, not automatic failure: it may reflect value disagreement, thin scenario specs, or intentional contested labels.

---

## 4. How to run

```bash
# Default nine-scenario pilot fixture
python scripts/run_empirical_pilot.py --json

# Full labeled dataset (executes the nine batch rows; skips annotation_only)
python scripts/run_empirical_pilot.py --fixture tests/fixtures/labeled_scenarios.json --json
```

Agreement summary uses only rows with a reference label present (same as the original pilot).

---

## 5. Comparison against other ethical systems

This repo does **not** ship a benchmark harness for third-party ethics engines. A **methodologically sound** comparison would:

1. **Shared scenario interface:** same structured `CandidateAction` lists and signals (or a documented export from `ALL_SIMULATIONS`).
2. **Same baselines** (first, max_impact) for every policy under test.
3. **Frozen seeds** and declared `KERNEL_*` / profile for reproducibility.
4. **Separate** human study for labels (IRB, consent, demographics) if you generalize beyond illustrative priors.

Treat competitor systems as **policies on the same MDP-shaped toy scenarios**, not as oracles.

---

## 6. Power, labels, and pole weights

Nine batch scenarios **underidentify** rich policy and pole parameters. The expanded file adds **annotation_only** vignettes for **study design**, not automatic statistical power. See [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md) and [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md).

---

*MoSex Macchina Lab — Issue 3 methodology; align substantive claims with CHANGELOG / HISTORY.*
