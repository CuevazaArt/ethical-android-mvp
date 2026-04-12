# Proposal: million-scale batch simulations (weight space + findings)

**Purpose:** Plan a **large-N** study (`EthicalKernel.process` on the **batch harness**) to record **synthetic findings** under diverse **pole** and **mixture** weights — for transparency and plots — without claiming field validation, DAO finality, or “full stack” coverage. **Recommended default scale:** **N = 100,000** for the **v2 protocol** (stratified lanes + richer telemetry); **N = 10⁶** remains optional for legacy uniform sweeps when disk and time allow.

**Related:** [PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md](PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md), [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md), [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md), [`experiments/million_sim/README.md`](../../experiments/million_sim/README.md).

---

## 1. What “representative of the full kernel” means (and does not)

| Covered by this experiment | Not covered (different harness / phase) |
|----------------------------|----------------------------------------|
| `process()` on canonical **batch** scenarios **1–9** with injected **pole** + **mixture** weights | WebSocket chat, LLM perception JSON, MalAbs **semantic** layers, many `KERNEL_*` advisory modules |
| MalAbs + buffer + **weighted mixture** + poles + will + mode fusion as wired in `process()` | Judicial DAO votes, hub “governance” as policy core, real sensors |
| Deterministic **`variability=False`** so variance comes from **weights + scenario choice**, not RNG inside `VariabilityEngine` | Async bridge load, thread-pool contention |

**Honest claim:** this is **representative of the batch ethical core path** under sweeping static weights — **not** of every production entrypoint.

**Architectural note (what actually moves `final_action`):** In `EthicalKernel.process`, **`final_action` is the mixture scorer’s argmax** (`WeightedEthicsScorer` / legacy alias `BayesianEngine`). **Pole weights are applied after that choice** for multipolar moral narration — sweeping poles alone does **not** change which discrete action wins. The v2 protocol therefore **fixes default pole centers** in lane A and stresses **mixture + pre-argmax margins**; see [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md).

---

## 1b. Research integrity disclaimer (induced or “loaded” conditions)

Any **hand-picked stress scenario subset**, **tight-margins focus**, or **ablation of episodic / temporal nudge flags** exists **only** to make **sensitivity and attribution** easier to observe in plots and tables. These choices are **experimental and investigative** — **not** tuned to maximize agreement with fixture references, stakeholder satisfaction, or a predetermined narrative. Operators must label runs (`--run-label`) and document **why** a non-uniform protocol was used. **Reference labels** in fixtures remain **maintainer priors** for internal consistency checks, not independent ground truth.

---

## 2. How to make the experiment efficient (same N, better science)

1. **Define one “simulation”** = one `process()` with one `(pole_weights, mixture_weights, scenario_id)` triple. Target **N = 10⁶** total simulations (configurable).

2. **Cover weight space without a naive dense grid**  
   - A full grid on poles (even 10 steps) × mixture × scenarios explodes. Prefer **independent random or quasi-random** draws:
   - **Poles:** independent Uniform on `[0.05, 0.95]` per axis (or truncated Gaussian around 0.5 for a “lab” prior).
   - **Mixture:** `Dirichlet(1,1,1)` (uniform on the simplex) — symmetric and standard for mixture sensitivity.
   - Optional upgrade: **Sobol / LHS** in 6D with mapping to simplex (add **scipy** in the experiment venv) for **space-filling** coverage with fewer duplicates.

3. **Stratify scenarios** so each **scenario_id 1–9** appears **≈ N/9** times (±1), instead of i.i.d. uniform which could skew by sampling noise. Implementation: **round-robin** or **per-block permutation**.

4. **Reproducibility:** `base_seed` + deterministic index `i → RNG` so any run can replay row `i` without storing all weights (see `src/sandbox/mass_kernel_study.py`).

5. **Parallelism:** `multiprocessing` with `chunksize` tuned to CPU count; avoid sending huge argument lists — pass **integer index** only.

6. **Artifacts:** stream **JSONL** (one JSON object per line) for post-processing; optional **summary JSON** with histograms (actions, modes, per-scenario agreement). **Do not** commit multi-GB files — output under `experiments/million_sim/out/` (gitignored).

7. **Phased rollout (recommended):**  
   - **Pilot:** N = 10⁴ — validate runtime, disk, summary.  
   - **Medium / primary:** N = **10⁵** — v2 protocol with lanes (see below).  
   - **Large (legacy uniform):** N = 10⁶ — optional overnight / cluster.

---

## 2b. Protocol **v2** (lanes + “color” dimensions)

Use **`--experiment-protocol v2`** on [`scripts/run_mass_kernel_study.py`](../../scripts/run_mass_kernel_study.py). The total **N** is split across **three lanes** (default **`--lane-split 0.45,0.35,0.2`**, must sum to 1):

| Lane | Code | Intent |
|------|------|--------|
| **A — Mixture focus** | `A_mixture_focus` | **Default pole centers** (0.5 on each axis); **Dirichlet(1,1,1)** mixture varies. **Stratified 1–9 within lane A only** when `--stratify-scenarios` is set — isolates **simplex** sensitivity on the path that sets `final_action`. |
| **B — Stress scenarios** | `B_stress_scenarios` | Same default poles; scenarios rotate through a **subset** of batch IDs (default **`--stress-scenario-ids 2,5,8`**, overridable). **Induced** to increase exposure to vignettes we want to compare under mixture stress — **not** to “optimize” agreement. |
| **C — Ablation** | `C_ablation` | Random poles in **[0.05, 0.95]** as in legacy; **rotates** bounded nudge env flags (`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`, `KERNEL_TEMPORAL_HORIZON_PRIOR` — see ADR 0009). Tests **which code paths** move scores when episodic / horizon priors apply. |

**Extra observability columns (schema v2):** mixture **entropy** on the simplex, **dominant_hypothesis** (`util` / `deon` / `virtue`), **scorer_second_action**, **scorer_second_ei**, **ei_margin**, **ei_margin_bin** (`tight` / `medium` / `wide` / `single_or_tight_pruned`), and **observation_palette** = `dominant_hypothesis | ei_margin_bin | experiment_lane` for quick faceted plots.

**Legacy protocol** (`--experiment-protocol legacy`, default): original **uniform pole sweep** + mixture + optional global stratification — unchanged behavior for backward compatibility.

---

## 2c. Protocol **v3** (frontier scenarios + pole pre-argmax + optional signal noise)

Use **`--experiment-protocol v3`**. Same lane idea as v2 with a **fourth lane** **`D_borderline`**: scenarios **10–12** in [`src/simulations/runner.py`](../../src/simulations/runner.py) — **tight** candidate scores and conflicting lexical cues (aggregate welfare vs duty, whistleblow vs cohesion, deterrence vs flee) so mixture / pole / noise can **flip** `final_action`. Default **`--lane-split`** is **`0.28,0.22,0.12,0.38`** (emphasizes lane D).

- **Pole pre-argmax (default on for v3):** sets **`KERNEL_POLES_PRE_ARGMAX=1`** so **ethical poles modulate util/deon/virtue valuations before argmax** (see [ADR 0010](../adr/0010-poles-pre-argmax-modulation.md)). Disable with **`--no-poles-pre-argmax`** for A/B comparisons.
- **Signal perturbation:** **`--signal-stress`** in **[0, 1]** applies [`synthetic_stochastic.perturb_scenario_signals`](../../src/sandbox/synthetic_stochastic.py) so inputs are not identical across rolls — logged as **`signal_noise_trace`** per row.

**Risks (honest):** pre-argmax poles can **reorder** actions and **lower** agreement with legacy fixture references; that is **expected** when measuring sensitivity, not a regression by itself.

---

## 2d. Classic **economy** triple (lanes A/C in v2–v4)

To reduce redundant coverage of similar “obvious” classics, lanes **A** and **C** stratify only **`(1, 5, 7)`** by default — **low-stakes civic (1)**, **violent high-stakes (5)**, **mission tradeoff (7)**. Override with **`--classic-economy-ids`**. Legacy stratification still uses **1..9** unless **`--legacy-economy-classics`**.

---

## 2e. Protocol **v4** (polemic + extreme lane)

**`--experiment-protocol v4`** adds lane **`E_polemic_extreme`** rotating scenarios **13–15** (polemic + synthetic extreme). Default **5-way** split **`0.20,0.16,0.12,0.20,0.32`**. Same pole / mixture / signal knobs as v3.

**Context richness (optional):** **`--context-richness-pre-argmax`** sets **`KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX`** so **trust / caution / sympathetic sigma / locus** apply **small** bounded multipliers on hypothesis slots before argmax ([ADR 0011](../adr/0011-context-richness-pre-argmax.md)), **after** pole scaling when both are on.

---

## 3. Findings (“hallazgos”) schema

**Row schema version** `RECORD_SCHEMA_VERSION` in [`src/sandbox/mass_kernel_study.py`](../../src/sandbox/mass_kernel_study.py) — bump when columns change.

Minimum fields per line (JSONL), as written by `run_mass_kernel_study.py` (current **`RECORD_SCHEMA_VERSION`**):

- `schema_version`, optional `run_label` (from `--run-label`)
- `i`, `kernel_seed` (= `base_seed + i` for the `EthicalKernel` instance), `scenario_id`, `difficulty_tier` (from fixture)
- `experiment_protocol` (`legacy` | `v2`), `experiment_lane` (e.g. `legacy_uniform`, `A_mixture_focus`, `B_stress_scenarios`, `C_ablation`)
- `ablation_tag` (lane C only; empty otherwise), `stress_scenario_ids`, `borderline_scenario_ids`
- `classic_economy_ids` (configuration list), `polemic_extreme_ids` (v3/v4 meta)
- `poles_pre_argmax` (bool), `context_richness_pre_argmax` (bool), `signal_stress`, `signal_noise_trace` (null or perturbation trace)
- `pole_*`, `mixture_*`, `mixture_entropy`, `dominant_hypothesis`
- `scorer_second_action`, `scorer_second_ei`, `ei_margin`, `ei_margin_bin`, `observation_palette`
- `final_action`, `decision_mode`, `reference_action`, `agree_reference`
- **Schema 5+:** `sampling_pole_lo`, `sampling_pole_hi`, `sampling_mixture_dirichlet_alpha` — echo the CLI knobs **`--pole-weight-range`** and **`--mixture-dirichlet-alpha`** for reproducible analysis (same values on every row of a run).

Optional **`--output-csv`**: same columns for **pandas / R / Excel** quick plots.

**CLI — weight sampling (defaults preserve legacy behavior):** **`--pole-weight-range LO,HI`** (uniform per-axis pole draws where random; default `0.05,0.95`), **`--mixture-dirichlet-alpha`** (symmetric Dirichlet concentration; default `1` = uniform on the simplex). Summary **`meta.weight_sampling`** duplicates these for archival plots.

**Summary JSON** (`--summary-json`) additionally includes:

- **Reproducibility:** `started_at_utc`, `finished_at_utc`, `platform`, `python`, `git_commit_short`, `argv`, `sims_per_second`, **`meta.weight_sampling`**
- **Stratification:** `counts_by_difficulty_tier`, `agreement_by_difficulty_tier` (rates use rows **with** reference only)
- **Plotting aids:** `histograms` — 10-bin counts (edges `0.0..1.0`) for each pole scalar and each mixture component (heatmaps / marginal densities)
- `counts_by_final_action`, `counts_by_decision_mode`, `counts_by_scenario_id`, `agreement_rate_vs_reference`, `unique_final_actions`
- `experiment_protocol`, `lane_split` (when v2), `stress_scenario_ids`
- `counts_by_experiment_lane`, `counts_by_ei_margin_bin`, `counts_by_dominant_hypothesis`, `top_observation_palettes` (top 40 palette strings)

**Progress:** `--progress` requires **`tqdm`** (`pip install -r experiments/million_sim/requirements-experiment.txt`).

**Interpretation:** low agreement is **expected** when weights sweep widely; the value is **sensitivity mapping**, not maximizing agreement.

---

## 4. Compute and storage (order of magnitude)

- Assume **0.5–3 ms** per `process()` on a laptop CPU → **8–50 minutes** for 10⁶ on one core; **~4–15 minutes** with 8 workers (rough).
- JSONL: ~200–400 bytes/line → **200–400 MB** for 10⁶ lines (compress with `gzip` for archive).

---

## 5. Ethics / ops

- **Synthetic only** — no user data.
- **No CI default** for N=10⁶ — manual / batch machine only.
- Document **machine, commit hash, Python version** in `meta` for the run.

---

## 5b. Successor: marginal simplex sensitivity (design, not a second million)

The legacy **10⁶** run is documented honestly in [`experiments/million_sim/EXPERIMENT_REPORT.md`](../../experiments/million_sim/EXPERIMENT_REPORT.md). When the goal is **decision boundaries** (where the mixture changes the winner) rather than **throughput demos**, prefer:

1. **Corner audit** on the util/deon/virtue simplex (pure corners + uniform center), full rankings and **top-2 margin** — script: [`scripts/audit_mixture_simplex_corners.py`](../../scripts/audit_mixture_simplex_corners.py).
2. **Near-tie** batch scenarios and **grid or bisection** on the simplex instead of **i.i.d. millions** when flips are absent under the same distribution.
3. **Ternary plots** and **margin histograms** as primary artifacts.

Narrative context, critique integration, and phased outline: [`experiments/million_sim/EXPERIMENT_HISTORY.md`](../../experiments/million_sim/EXPERIMENT_HISTORY.md). **Executable grid + bisection:** [`scripts/run_simplex_decision_map.py`](../../scripts/run_simplex_decision_map.py) (batch scenario **16** = two-candidate calibration near-tie). **Full kernel at 100k (v4):** [`scripts/run_experiment_v4_full_kernel_100k.py`](../../scripts/run_experiment_v4_full_kernel_100k.py); frontier **10–12** valuations periodically **retuned** for sensitivity (see `src/simulations/runner.py`). **Pre-argmax poles** ([ADR 0010](../adr/0010-poles-pre-argmax-modulation.md)) apply when the question is pole sensitivity **of the argmax**, not post-hoc narrative alone.

---

## 6. Implementation in this repo

- **Library:** [`src/sandbox/mass_kernel_study.py`](../../src/sandbox/mass_kernel_study.py) — `run_single_simulation`, `load_reference_labels`, `stratified_scenario_ids`.
- **CLI:** [`scripts/run_mass_kernel_study.py`](../../scripts/run_mass_kernel_study.py) — `--n-simulations`, `--workers`, `--stratify-scenarios`, `--run-label`, `--output-jsonl`, `--output-csv`, `--summary-json`, `--progress`, safety `--i-accept-large-run`; **`--experiment-protocol`**, **`--lane-split`** (3 / 4 / 5 fractions), **`--stress-scenario-ids`**, **`--borderline-scenario-ids`**, **`--polemic-extreme-ids`**, **`--classic-economy-ids`**, **`--legacy-economy-classics`**, **`--poles-pre-argmax`**, **`--no-poles-pre-argmax`** (v3/v4), **`--context-richness-pre-argmax`**, **`--signal-stress`**.
- **Phase-1 simplex corner audit (mixture-only):** [`scripts/audit_mixture_simplex_corners.py`](../../scripts/audit_mixture_simplex_corners.py) — see [`experiments/million_sim/EXPERIMENT_HISTORY.md`](../../experiments/million_sim/EXPERIMENT_HISTORY.md).
- **Simplex grid + edge bisection (mixture-only):** [`scripts/run_simplex_decision_map.py`](../../scripts/run_simplex_decision_map.py); library [`src/sandbox/simplex_mixture_probe.py`](../../src/sandbox/simplex_mixture_probe.py).
- **Environment:** [`experiments/million_sim/README.md`](../../experiments/million_sim/README.md) + optional [`requirements-experiment.txt`](../../experiments/million_sim/requirements-experiment.txt).

---

*MoSex Macchina Lab — design-first million-scale study; execution is operator responsibility.*
