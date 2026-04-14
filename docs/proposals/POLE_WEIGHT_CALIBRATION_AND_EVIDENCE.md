# Pole weight calibration and evidence (roadmap)

**Purpose:** State clearly that **linear pole weights** and **context multipliers** in the Ethos Kernel are **engineering heuristics**, not outcomes of an empirical study with human judges. Define what a **credible calibration program** would require and how it relates to the **empirical pilot** fixture and **invariant tests**.

**Related:** [ADR 0004 — configurable linear pole evaluator](../adr/0004-configurable-linear-pole-evaluator.md) (`KERNEL_POLE_LINEAR_CONFIG`), [`pole_linear_default.json`](../../src/modules/pole_linear_default.json), [`ethical_poles.py`](../../src/modules/ethical_poles.py) (`BASE_WEIGHTS`, `CONTEXTS`), [POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md), [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md), [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json), [`tests/test_ethical_properties.py`](../../tests/test_ethical_properties.py).

---

## 1. What is “ad hoc” today

| Layer | Role | Calibration status |
|-------|------|---------------------|
| **`pole_linear_default.json`** | Per-pole linear map from MalAbs-style **features** to a scalar score; thresholds and moral strings | Chosen to match **legacy** `evaluate_pole` behavior (see JSON `description`). Not fit to human labels. |
| **`EthicalPoles.BASE_WEIGHTS`** | Combines the three pole scores into one multipolar aggregate | Same: **design** weights, not posterior estimates from data. |
| **`EthicalPoles.CONTEXTS`** | String-keyed multipliers on pole weights | Same: **stylized** context knobs for narration and audit. |

Together, these control **telemetry and narrative framing** around the chosen action. Per [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md), they do **not** replace MalAbs → mixture as the source of `final_action`.

**Product and research honesty:** Do not describe these numbers as “validated,” “optimal,” or “calibrated to experts” unless you publish the study design, N, agreement metrics, and constraints under which weights were chosen.

---

## 2. Why the default empirical pilot (n = 9) is not enough

The fixture [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) lists the **nine** canonical **batch** simulations (`id` 1–9). The pilot script compares **whole-kernel** (and baseline) **action choices** to optional `reference_action` labels — see [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md).

**Limits for pole-weight fitting:**

- **Degrees of freedom:** Linear pole config exposes multiple term weights per pole plus thresholds; `BASE_WEIGHTS` and `CONTEXTS` add more free parameters. **Nine** scenario-level action labels severely **underidentify** that space even if labels were noise-free.
- **Target mismatch:** Pilot agreement is on **discrete chosen actions**, not on **continuous pole scores** or per-pole rankings. Many weight vectors can yield the same argmax action on a small grid.
- **Power:** Classical inference (confidence intervals, significance) for weight recovery needs a **much larger** scenario bank and/or repeated judgments — not something this repository claims to ship.

**Conclusion:** The nine-scenario fixture is a **reproducible template** for policy comparison and annotator workflows, **not** statistical validation of pole weights.

---

## 3. What a serious calibration program would look like

This is **future work**; the steps below are a minimal scientific bar if the project ever claims empirical alignment with human judgment.

1. **Define the prediction target**  
   Examples: preferred **action** among candidates; **ordinal** ranking of actions; **scalar** “acceptable / gray / unacceptable” per pole; **pairwise** preferences. The target must match what linear poles are supposed to approximate.

2. **Scenario bank**  
   Grow beyond the fixed nine IDs as new batch scenarios are added to `ALL_SIMULATIONS`, or use **exported traces** (same action sets, fixed seeds) with documented priors. Publish N and sampling strategy.

3. **Human protocol**  
   Multiple raters, blinding where possible, documented instructions, inter-rater agreement (e.g. Fleiss’ kappa, Krippendorff’s alpha for ordinal data). Store annotations outside the repo or in a dedicated dataset with versioning.

4. **Fitting under constraints**  
   Any weight search must **preserve** existing **invariant** and **regression** tests (`tests/test_ethical_properties.py` and related). Treat invariants as **hard** constraints; optimize agreement or loss **subject to** them.

5. **Reporting**  
   Report **held-out** performance, not only training fit. Prefer **simple** weight sets (sparsity, bounded ranges) and justify changes in `CHANGELOG.md` with a pointer to the study artifact.

Optional in-repo tooling (e.g. [`ml_ethics_tuner.py`](../../src/modules/ml_ethics_tuner.py)) may explore parameter tweaks; any production-facing weight changes should still be **secondary** to **invariant** guarantees in `tests/test_ethical_properties.py` and documented as in step 4 above.

---

## 4. Repository posture (today)

- **Default weights stay heuristic** until a published calibration satisfies the bar above.
- Operators may override linear pole JSON via **`KERNEL_POLE_LINEAR_CONFIG`** (ADR 0004); custom weights are **their** responsibility to validate for their deployment.
- The empirical pilot remains the right place to grow **action-level** human agreement studies; pole calibration is a **distinct** track documented here.

---

*MoSex Macchina Lab — evidence roadmap; align substantive claims with CHANGELOG / HISTORY when publishing results.*
