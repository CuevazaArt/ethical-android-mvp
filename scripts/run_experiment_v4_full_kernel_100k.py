#!/usr/bin/env python3
"""
Launch protocol **v4** with **full** ``EthicalKernel.process`` at **N=100,000**.

**Tight weight sampling (default):** pole axes **Uniform(0.36, 0.64)** and symmetric mixture
**Dirichlet(12,12,12)** so draws stay near neutral poles and near the simplex center — finer
local exploration than the legacy **0.05–0.95** pole span and **Dirichlet(1,1,1)** mixture.

**Lane D** includes calibration scenario **16** alongside **10–12** (override with
``--borderline-scenario-ids``).

See ``experiments/README.md``. Per-row and summary ``meta.weight_sampling`` record
the exact settings for analysis.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    out = ROOT / "experiments" / "out"
    out.mkdir(parents=True, exist_ok=True)
    jsonl = out / "run_v4_tight_100k.jsonl"
    summary = out / "run_v4_tight_100k_summary.json"
    csv_path = out / "run_v4_tight_100k.csv"

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "run_mass_kernel_study.py"),
        "--experiment-protocol",
        "v4",
        "--n-simulations",
        "100000",
        "--stratify-scenarios",
        "--context-richness-pre-argmax",
        "--signal-stress",
        "0.2",
        "--pole-weight-range",
        "0.36,0.64",
        "--mixture-dirichlet-alpha",
        "12",
        "--borderline-scenario-ids",
        "10,11,12,16",
        "--run-label",
        "v4_tight_100k",
        "--progress",
        "--output-jsonl",
        str(jsonl),
        "--summary-json",
        str(summary),
        "--output-csv",
        str(csv_path),
    ]
    cmd.extend(sys.argv[1:])
    print("Running:", " ".join(cmd), file=sys.stderr)
    return subprocess.call(cmd, cwd=str(ROOT))


if __name__ == "__main__":
    raise SystemExit(main())
