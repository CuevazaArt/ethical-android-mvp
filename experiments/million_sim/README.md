# Million-simulation experiment (optional batch machine)

This directory holds **operator instructions** for large-N runs described in
[`docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../../docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md).

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

```bash
python scripts/run_mass_kernel_study.py --n-simulations 10000 --workers 8 --stratify-scenarios --output-jsonl experiments/million_sim/out/pilot_10k.jsonl --summary-json experiments/million_sim/out/pilot_10k_summary.json
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
