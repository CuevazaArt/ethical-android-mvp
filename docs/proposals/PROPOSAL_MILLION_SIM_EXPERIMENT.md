# Proposal: million-scale batch simulations (weight space + findings)

**Purpose:** Plan a **large-N** study (target **≥ 1,000,000** `EthicalKernel.process` calls on the **batch harness**) to record **synthetic findings** under diverse **pole** and **mixture** weights — for transparency and plots — without claiming field validation, DAO finality, or “full stack” coverage.

**Related:** [PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md](PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md), [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md), [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md), [`experiments/million_sim/README.md`](../../experiments/million_sim/README.md).

---

## 1. What “representative of the full kernel” means (and does not)

| Covered by this experiment | Not covered (different harness / phase) |
|----------------------------|----------------------------------------|
| `process()` on canonical **batch** scenarios **1–9** with injected **pole** + **mixture** weights | WebSocket chat, LLM perception JSON, MalAbs **semantic** layers, many `KERNEL_*` advisory modules |
| MalAbs + buffer + **weighted mixture** + poles + will + mode fusion as wired in `process()` | Judicial DAO votes, hub “governance” as policy core, real sensors |
| Deterministic **`variability=False`** so variance comes from **weights + scenario choice**, not RNG inside `VariabilityEngine` | Async bridge load, thread-pool contention |

**Honest claim:** this is **representative of the batch ethical core path** under sweeping static weights — **not** of every production entrypoint.

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
   - **Medium:** N = 10⁵ — check distributions stabilize.  
   - **Full:** N = 10⁶ — overnight / cluster.

---

## 3. Findings (“hallazgos”) schema

**Row schema version** `RECORD_SCHEMA_VERSION` in [`src/sandbox/mass_kernel_study.py`](../../src/sandbox/mass_kernel_study.py) — bump when columns change.

Minimum fields per line (JSONL), as written by `run_mass_kernel_study.py`:

- `schema_version`, optional `run_label` (from `--run-label`)
- `i`, `kernel_seed` (= `base_seed + i` for the `EthicalKernel` instance), `scenario_id`, `difficulty_tier` (from fixture)
- `pole_*`, `mixture_*`, `final_action`, `decision_mode`, `reference_action`, `agree_reference`

Optional **`--output-csv`**: same columns for **pandas / R / Excel** quick plots.

**Summary JSON** (`--summary-json`) additionally includes:

- **Reproducibility:** `started_at_utc`, `finished_at_utc`, `platform`, `python`, `git_commit_short`, `argv`, `sims_per_second`
- **Stratification:** `counts_by_difficulty_tier`, `agreement_by_difficulty_tier` (rates use rows **with** reference only)
- **Plotting aids:** `histograms` — 10-bin counts (edges `0.0..1.0`) for each pole scalar and each mixture component (heatmaps / marginal densities)
- `counts_by_final_action`, `counts_by_decision_mode`, `counts_by_scenario_id`, `agreement_rate_vs_reference`, `unique_final_actions`

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

## 6. Implementation in this repo

- **Library:** [`src/sandbox/mass_kernel_study.py`](../../src/sandbox/mass_kernel_study.py) — `run_single_simulation`, `load_reference_labels`, `stratified_scenario_ids`.
- **CLI:** [`scripts/run_mass_kernel_study.py`](../../scripts/run_mass_kernel_study.py) — `--n-simulations`, `--workers`, `--stratify-scenarios`, `--run-label`, `--output-jsonl`, `--output-csv`, `--summary-json`, `--progress`, safety `--i-accept-large-run`.
- **Environment:** [`experiments/million_sim/README.md`](../../experiments/million_sim/README.md) + optional [`requirements-experiment.txt`](../../experiments/million_sim/requirements-experiment.txt).

---

*MoSex Macchina Lab — design-first million-scale study; execution is operator responsibility.*
