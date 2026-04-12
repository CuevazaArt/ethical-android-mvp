# Million-simulation batch experiment — narrative report

**Run label:** `cursor_start_1e6`  
**Artifact:** [`out/run_1e6_summary.json`](out/run_1e6_summary.json) (generated locally; not committed)  
**Design doc:** [`docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md)

**Update (2026):** the repository adds **`--experiment-protocol v2`** (stratified lanes, richer scorer-margin telemetry, `observation_palette`). The historical run below used the **legacy uniform** protocol. New runs should cite the protocol and read [`README.md`](README.md) for the **research disclaimer** on induced stress subsets. For the **full experiment lineage** (critique, protocol evolution, successor simplex / near-tie design), see [`EXPERIMENT_HISTORY.md`](EXPERIMENT_HISTORY.md).

---

## 1. Origin and motivation

The Ethos Kernel has been criticized for **many modules**, **heuristic weights**, and naming around a **weighted mixture** (not Bayesian inference — see [ADR 0009](../../docs/adr/0009-ethical-mixture-scorer-naming.md)). External reviewers also asked for **evidence** that sweeping hyperparameters changes behavior in a measurable way.

This experiment was introduced to:

- **Stress-test** the **batch** ethical path (`EthicalKernel.process` on canonical simulations **1–9**) at **large N** (10⁶).
- **Record** outcomes (actions, modes, agreement with maintainer reference labels) under **random pole scalars** and **Dirichlet(1,1,1)** mixture weights.
- Produce **reproducible artifacts** (JSONL, CSV, summary JSON) for **plots and transparency**, without claiming field validation or DAO calibration.

---

## 2. Logical and methodological design

### 2.1 What one “simulation” is

Each row corresponds to:

1. **Index `i`** ∈ [0, N−1] with **`base_seed`** (42 in this run).
2. **Reproducible RNG** per index: independent **Uniform[0.05, 0.95]** for each **pole base weight** (compassionate / conservative / optimistic).
3. **Mixture vector** from **Dirichlet(1,1,1)** — approximately uniform on the **probability simplex** over the three hypothesis valuations (util / deon / virtue slots in the mixture scorer).
4. **Scenario ID** **1–9**, **stratified** so each ID appears **≈ N/9** times (±1), reducing sampling bias across vignettes.

`EthicalKernel` is built with **`variability=False`**: no `VariabilityEngine` noise inside scoring; variance is intended to come from **weights + scenario assignment**.

### 2.2 How it was implemented

- **Library:** [`src/sandbox/mass_kernel_study.py`](../../src/sandbox/mass_kernel_study.py) — `run_single_simulation`, `stratified_scenario_ids`, reference/tier loaders.
- **Runner:** [`scripts/run_mass_kernel_study.py`](../../scripts/run_mass_kernel_study.py) — multiprocessing pool, JSONL + optional CSV, summary with histograms and tier-level agreement.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) (batch rows + `difficulty_tier` + reference labels).

### 2.3 What the experiment is *not*

- **Not** WebSocket chat, **not** LLM perception, **not** semantic MalAbs, **not** production `KERNEL_*` stacks.
- **Not** proof of “correct ethics” — reference labels are **maintainer priors** for alignment metrics ([Issue 3](../../docs/proposals/CRITIQUE_ROADMAP_ISSUES.md)), not independent expert ground truth.

---

## 3. What we expected (hypotheses)

**H1 (sensitivity):** Under wide random mixture weights, we might see **some** rows where `final_action` **differs** from the fixture’s `reference_action`, or at least a **distribution** of actions that is not trivially tied one-to-one to scenario ID.

**H2 (throughput):** The pipeline should sustain **high sims/s** on a many-core host with **JSONL + CSV** output without exhausting RAM.

**H3 (stratification):** With **stratified** scenario IDs, **per-scenario** counts should be **balanced** (~N/9 each).

---

## 4. What actually happened (this run)

Facts taken from **`run_1e6_summary.json`** (same commit as `git_commit_short` in meta when the run was executed):

| Field | Value |
|--------|--------|
| **N** | 1,000,000 |
| **Workers** | 28 |
| **Wall time** | ~3037 s (~50.6 min) |
| **Throughput** | ~329 sims/s |
| **Platform** | Windows 11, Python 3.13.5 |
| **`agreement_rate_vs_reference`** | **1.0** (1,000,000 / 1,000,000 labeled rows) |
| **`unique_final_actions`** | **9** (one canonical action name per scenario outcome) |

**Per-scenario counts** are **balanced** (≈111,111–111,112 per scenario ID), matching **H3**.

**Action counts** mirror that stratification: each of the **nine** reference-level actions appears **~111,111** times — consistent with **one stable `final_action` per scenario** across all weight draws.

**Mixture marginal histograms** (in the summary) show the expected **Dirichlet(1,1,1)** shape (mass concentrated away from exact 0/1 corners on each marginal). **Pole** histograms are **roughly flat** across 10 bins, as expected from uniform sampling.

---

## 5. Interpretation — why agreement stayed at 100%

Two mechanisms interact:

### 5.1 Pole weights likely do **not** move the argmax

In `process()`, the **mixture scorer** picks the candidate (`bayesian.evaluate`); **ethical poles** are evaluated **on the already chosen action name** for multipolar narrative (`poles.evaluate(bayes_result.chosen_action.name, …)`). So **changing `EthicalPoles.base_weights`** does **not** change which candidate wins the argmax — it affects **post-choice** multipolar synthesis.  
*Therefore, sweeping pole weights was never expected to flip `final_action` in this architecture.*

### 5.2 Mixture weights did not flip winners in these nine scenarios

The **mixture weights** do affect `bayesian.evaluate`. Observing **zero** flips across 10⁶ samples suggests that, for the **nine fixed scenarios and candidate lists**, the **margin between the best and second-best candidate** under the implemented valuations is **large enough** that random mixture vectors on the simplex **do not reorder** the ranking — at least for the sampling realized in this run.

That is a **substantive negative result** for **action-level sensitivity** under this protocol: the experiment is still valuable for **infrastructure and throughput**, but it **did not** produce variation in **`final_action`** across mixture draws.

**`decision_mode`** *did* vary (`gray_zone`, `D_fast`, `D_delib` counts in summary), so **some** internal classification responded even when the winning action name did not change.

---

## 6. Final conclusions

1. **Engineering:** The **10⁶** batch run completed successfully with **documented throughput**, **stratified** scenario coverage, and **rich** summary output (histograms, tier breakdowns, git metadata). The **methodology and tooling** are fit for large-N **synthetic** studies.

2. **Science (action choice):** This run **does not** demonstrate sensitivity of **`final_action`** to **pole** sweeps (consistent with pipeline order). It also **did not** observe sensitivity of **`final_action`** to **Dirichlet mixture** sweeps on these nine scenarios — suggesting **robust ranking margins** or a need for **stronger perturbations** (e.g. signal noise, adversarial near-tie scenarios, or explicit near-tie fixtures).

3. **Next steps (if the goal is visible action flips):** Combine with **signal perturbation** ([`run_stochastic_sandbox.py`](../../scripts/run_stochastic_sandbox.py)), **weight sweeps** focused on **mixture-only** with **extreme** corners, or **new scenarios** designed with **close** candidate scores; optionally record **score gaps** (best vs second) per row for analysis.

4. **Governance:** Results remain **lab-synthetic**; they **do not** replace DAO or field trials for operational weight choices.

---

## 7. How to cite this run

Reference the **summary JSON** path, **`run_label`**, **`git_commit_short`**, and **`started_at_utc` / `finished_at_utc`** from `meta` when publishing plots or slides.

---

*MoSex Macchina Lab — honest readout of the first million-scale batch study (April 2026).*
