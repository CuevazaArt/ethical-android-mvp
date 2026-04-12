# Million-simulation experiment (optional batch machine)

This directory holds **operator instructions** for large-N runs described in
[`docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md).

**Narrative report** (origin, method, expected vs observed, conclusions — run `cursor_start_1e6`): [`EXPERIMENT_REPORT.md`](EXPERIMENT_REPORT.md).

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

## Full scale (10⁶)

Requires **`--i-accept-large-run`**, sufficient disk (~200–400 MB JSONL uncompressed), and a multi-core host.

```bash
python scripts/run_mass_kernel_study.py --n-simulations 1000000 --workers 16 --stratify-scenarios --i-accept-large-run --output-jsonl experiments/million_sim/out/run_1e6.jsonl --summary-json experiments/million_sim/out/run_1e6_summary.json
```

Compress for archival: `gzip -9 experiments/million_sim/out/run_1e6.jsonl`

## Output

- **JSONL:** one JSON object per simulation (weights, scenario_id, `final_action`, `decision_mode`, agreement).
- **Summary JSON:** aggregated counts for plotting and transparency.

The `out/` folder is gitignored; do not commit large artifacts.
