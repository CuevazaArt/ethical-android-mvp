# Million-simulation experiment (optional batch machine)

**Design spec (mass study):** [`docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md).

| Doc | Role |
|-----|------|
| [`docs/README.md`](docs/README.md) | Index of all markdown under this folder (report, history, design, registry). |
| [`docs/EXPERIMENT_REPORT.md`](docs/EXPERIMENT_REPORT.md) | Narrative readout of run `cursor_start_1e6` (throughput, agreement, interpretation). |
| [`docs/EXPERIMENT_HISTORY.md`](docs/EXPERIMENT_HISTORY.md) | Lineage: critique of the million run, ADR links, **why** simplex / near-tie work replaced brute-force N. |
| [`docs/NEXT_EXPERIMENT_DESIGN.md`](docs/NEXT_EXPERIMENT_DESIGN.md) | **Canonical** scenarios **17–19** triples (mirrors `runner.py`), simplex coverage command, protocol **v5** status + infrastructure table. |
| [`docs/proposals/PROPOSAL_EXPERIMENT_V5_SENSITIVITY.md`](../../docs/proposals/PROPOSAL_EXPERIMENT_V5_SENSITIVITY.md) | v5 proposal: goals, lane F–H roadmap, `run_experiment_v5_sensitivity.py` vs mass study. |
| [`tests/fixtures/feedback/compatible_17_18_19.json`](../../tests/fixtures/feedback/compatible_17_18_19.json) | Sample **ADR 0012** feedback (17–19) for `KERNEL_FEEDBACK_PATH`. |
| [`docs/ARTIFACTS_REGISTRY.md`](docs/ARTIFACTS_REGISTRY.md) | **Summaries** of local runs (no heavy artifacts in repo). |

**Layout:** `docs/` = long-form documentation · `out/` = generated artifacts (gitignored) · `requirements-experiment.txt` = optional pip deps.

**Tree:** [`experiments/README.md`](../README.md) (how `million_sim/` and `out/` relate).

**Quick probes (mixture-only, cheap):**

- Corner audit: `python scripts/audit_mixture_simplex_corners.py --scenario-ids all`
- Simplex grid / bisection / plots: see **Part 3** in [`docs/NEXT_EXPERIMENT_DESIGN.md`](docs/NEXT_EXPERIMENT_DESIGN.md) (default example still uses **10–12 + 16**; **17–19** tables live in **Part 1** there).
- v5 sensitivity bundle (screening + refinement + `boundaries.json`): **Part 2** in [`docs/NEXT_EXPERIMENT_DESIGN.md`](docs/NEXT_EXPERIMENT_DESIGN.md) — one command + output notes (full `EthicalKernel.process` sweeps: `run_mass_kernel_study.py` / `run_experiment_v4_full_kernel_100k.py`).
- **ADR 0012 feedback posterior (offline):** `python scripts/run_feedback_posterior.py --pretty` — same update as `KERNEL_BAYESIAN_FEEDBACK` + `KERNEL_FEEDBACK_PATH`, JSON to stdout (default feedback file: [`compatible_17_18_19.json`](../../tests/fixtures/feedback/compatible_17_18_19.json)).

### Full decision stack at **N = 100,000** (protocol **v4**, recommended)

Use this when the goal is **`EthicalKernel.process`** (MalAbs, mixture, **pre-argmax** poles, will, modes, narrative) rather than mixture-only probes. **Frontier scenarios 10–12** were **retuned** (April 2026) for **tighter** candidate margins so mixture / poles / signal stress can surface more action-level variation; see `src/simulations/runner.py`.

**Wrapper (defaults: v4, 100k, stratify, context richness pre-argmax, signal stress 0.2, tight weight sampling, lane D includes 10–12 + 16, CSV + JSONL + summary):**

- **`--pole-weight-range 0.36,0.64`** — pole axes uniform in a **narrow** band around 0.5 (instead of 0.05–0.95).
- **`--mixture-dirichlet-alpha 12`** — symmetric Dirichlet **(12,12,12)** so mixture weights stay **near** the simplex center (finer local exploration than `Dirichlet(1,1,1)`).
- **`--borderline-scenario-ids 10,11,12,16`** — lane **D** also rotates the **two-candidate calibration** vignette **16**.

Each JSONL row and **`summary.json` → `meta.weight_sampling`** record **`sampling_pole_lo` / `sampling_pole_hi` / `sampling_mixture_dirichlet_alpha`** for analysis. Override with the same flags on `run_mass_kernel_study.py`.

```bash
python scripts/run_experiment_v4_full_kernel_100k.py
```

Optional: append `--workers 16` or a custom lane split, e.g. more weight on borderline + polemic:

`--lane-split 0.14,0.12,0.10,0.34,0.28` (A,B,C,D,E).

**Note:** `n=100000` does **not** require `--i-accept-large-run` (that gate applies only when **n > 100000**). Expect **~20–40 MB** JSONL and minutes of wall time depending on cores.

**Workflow:** run the **cheap** simplex probes first, then this **100k** run for full-stack telemetry (`ei_margin`, lanes, `observation_palette`, etc.).

## Research disclaimer

**Induced or loaded conditions** (stress scenario subsets, lane splits, ablation flags) are **experimental and investigative** — to **map sensitivity and attribution** in the batch harness. They are **not** chosen to please stakeholders, maximize agreement with fixture references, or prove external validity. **Reference labels** are maintainer priors for internal consistency checks, not independent ground truth.

**Optional Bayesian mixture telemetry** ([ADR 0012](../../docs/adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)): when enabled, the kernel can report **win probabilities** under a Dirichlet prior over mixture weights and optionally apply **operator feedback** as an approximate Dirichlet update. This assumes a **learnable** weight vector in the mixture — a stronger stance than fixed designer weights — and does not claim external moral validity.

## Environment

From the repository root:

```bash
python -m venv .venv-experiment
# Windows PowerShell:
.venv-experiment\Scripts\Activate.ps1
# Linux/macOS:
# source .venv-experiment/bin/activate

pip install -r requirements.txt
pip install -r experiments/million_sim/requirements-experiment.txt
```

Optional: `scipy` enables quasi-Monte Carlo upgrades in future tooling (not required for `run_mass_kernel_study.py`).

## Pilot (10⁴)

Use **`--summary-json`** for aggregated histograms and tier-level agreement; **`--output-csv`** for pandas/R; **`--run-label`** to tag your machine or protocol version; **`--progress`** if `tqdm` is installed.

```bash
pip install -r experiments/million_sim/requirements-experiment.txt
python scripts/run_mass_kernel_study.py --n-simulations 10000 --workers 8 --stratify-scenarios --run-label pilot_A --progress --output-jsonl experiments/million_sim/out/pilot_10k.jsonl --output-csv experiments/million_sim/out/pilot_10k.csv --summary-json experiments/million_sim/out/pilot_10k_summary.json
```

## Recommended v2 protocol (10⁵)

Stratified **lanes** (mixture focus / stress scenarios / ablation), telemetry (top-2 scorer margin, mixture entropy, `observation_palette`). See the proposal doc for semantics.

```bash
python scripts/run_mass_kernel_study.py --experiment-protocol v2 --n-simulations 100000 --workers 8 --stratify-scenarios --run-label v2_100k --i-accept-large-run --progress --output-jsonl experiments/million_sim/out/run_v2_100k.jsonl --summary-json experiments/million_sim/out/run_v2_100k_summary.json
```

## Protocol v4 (polemic + extreme lane E)

Five lanes; includes **13–15** (classified-leak / transplant fairness / synthetic extreme trolley). Default lane split **`0.20,0.16,0.12,0.20,0.32`**. Classic lanes **A/C** use only **IDs 1, 5, 7** (economy triple). Optional **`--context-richness-pre-argmax`** ([ADR 0011](../../docs/adr/0011-context-richness-pre-argmax.md)).

```bash
python scripts/run_mass_kernel_study.py --experiment-protocol v4 --n-simulations 80000 --stratify-scenarios --context-richness-pre-argmax --run-label v4_80k --i-accept-large-run --output-jsonl experiments/million_sim/out/run_v4.jsonl --summary-json experiments/million_sim/out/run_v4_summary.json
```

## Protocol v3 (frontier sensitivity — recommended for “breakpoints”)

**Four lanes** including **`D_borderline`** (batch scenarios **10–12**): near-tie actions designed so mixture / poles / noise can flip `final_action`. **Pole pre-argmax** is **on by default** (`KERNEL_POLES_PRE_ARGMAX` — [ADR 0010](../../docs/adr/0010-poles-pre-argmax-modulation.md)); use **`--no-poles-pre-argmax`** for ablations. Optional **`--signal-stress`** perturbs ethics scalars (see `synthetic_stochastic`).

```bash
python scripts/run_mass_kernel_study.py --experiment-protocol v3 --n-simulations 100000 --workers 8 --stratify-scenarios --run-label v3_100k --signal-stress 0.25 --i-accept-large-run --progress --output-jsonl experiments/million_sim/out/run_v3_100k.jsonl --summary-json experiments/million_sim/out/run_v3_100k_summary.json
```

## Full scale (10⁶, legacy)

Requires **`--i-accept-large-run`**, sufficient disk (~200–400 MB JSONL uncompressed), and a multi-core host.

```bash
python scripts/run_mass_kernel_study.py --n-simulations 1000000 --workers 16 --stratify-scenarios --i-accept-large-run --output-jsonl experiments/million_sim/out/run_1e6.jsonl --summary-json experiments/million_sim/out/run_1e6_summary.json
```

Compress for archival: `gzip -9 experiments/million_sim/out/run_1e6.jsonl`

## Output

- **JSONL:** one JSON object per simulation (weights, scenario_id, protocol lane, scorer margins, `final_action`, `decision_mode`, agreement).
- **Summary JSON:** aggregated counts for plotting and transparency (including lane / margin-bin / palette facets when using v2).

The `out/` folder is gitignored; do not commit large artifacts.
