#!/usr/bin/env python3
"""
Mass kernel batch study — up to millions of ``process()`` calls with random pole + Dirichlet mixture weights.

**Not CI.** Use a dedicated venv and disk space; see ``experiments/million_sim/README.md`` and
``docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md``.

Example (pilot):
  python scripts/run_mass_kernel_study.py --n-simulations 10000 --workers 8 --output-jsonl out/run.jsonl --summary-json out/summary.json

Full scale (requires flag):
  python scripts/run_mass_kernel_study.py --n-simulations 1000000 --workers 16 --i-accept-large-run --output-jsonl out/million.jsonl
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.sandbox.mass_kernel_study import (  # noqa: E402
    load_reference_labels,
    load_tier_labels,
    run_single_simulation,
)

_G: dict[str, Any] = {}


def _init_worker(payload: dict[str, Any]) -> None:
    global _G
    _G = payload


def _worker(i: int) -> dict[str, Any]:
    return run_single_simulation(
        i,
        base_seed=_G["base_seed"],
        refs=_G["refs"],
        tiers=_G["tiers"],
        stratify_scenario=_G["stratify_scenario"],
        scenario_id_override=_G["scenario_id_override"],
        n_total=_G["n_total"],
    )


def main() -> int:
    p = argparse.ArgumentParser(
        description="Mass batch kernel study (pole + mixture random sweep)."
    )
    p.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json",
    )
    p.add_argument("--n-simulations", type=int, default=10_000, help="Total process() calls.")
    p.add_argument("--base-seed", type=int, default=42)
    p.add_argument(
        "--workers",
        type=int,
        default=max(1, (mp.cpu_count() or 4)),
        help="Process pool size (default: CPU count or 4).",
    )
    p.add_argument(
        "--stratify-scenarios",
        action="store_true",
        help="Balance scenario IDs 1..9 (recommended).",
    )
    p.add_argument(
        "--i-accept-large-run",
        action="store_true",
        help="Required when --n-simulations > 100000.",
    )
    p.add_argument(
        "--output-jsonl", type=Path, required=True, help="Append one JSON object per line."
    )
    p.add_argument("--summary-json", type=Path, default=None, help="Write aggregate findings.")
    args = p.parse_args()

    n = max(1, args.n_simulations)
    if n > 100_000 and not args.i_accept_large_run:
        print(
            "Refusing n>100000 without --i-accept-large-run (disk/time). "
            "See docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md",
            file=sys.stderr,
        )
        return 2

    refs = load_reference_labels(args.fixture)
    tiers = load_tier_labels(args.fixture)

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "base_seed": args.base_seed,
        "refs": refs,
        "tiers": tiers,
        "stratify_scenario": args.stratify_scenarios,
        "scenario_id_override": None,
        "n_total": n,
    }

    t0 = time.perf_counter()
    by_action: Counter[str] = Counter()
    by_mode: Counter[str] = Counter()
    by_sid: Counter[int] = Counter()
    agree_n = 0
    agree_denom = 0

    chunksize = max(1, n // max(8, args.workers * 16))

    with open(args.output_jsonl, "w", encoding="utf-8") as out_f:
        with mp.Pool(args.workers, initializer=_init_worker, initargs=(payload,)) as pool:
            for row in pool.imap(_worker, range(n), chunksize=chunksize):
                out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                by_action[row["final_action"]] += 1
                by_mode[row["decision_mode"]] += 1
                by_sid[int(row["scenario_id"])] += 1
                if row.get("reference_action") is not None:
                    agree_denom += 1
                    if row["agree_reference"]:
                        agree_n += 1

    elapsed = time.perf_counter() - t0
    summary = {
        "meta": {
            "n_simulations": n,
            "base_seed": args.base_seed,
            "workers": args.workers,
            "stratify_scenarios": args.stratify_scenarios,
            "fixture": str(args.fixture.resolve()),
            "runtime_seconds": round(elapsed, 3),
            "doc": "docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md",
        },
        "findings": {
            "agreement_rate_vs_reference": agree_n / agree_denom if agree_denom else None,
            "agreement_denominator": agree_denom,
            "unique_final_actions": len(by_action),
            "counts_by_final_action": dict(by_action),
            "counts_by_decision_mode": dict(by_mode),
            "counts_by_scenario_id": {str(k): v for k, v in sorted(by_sid.items())},
        },
    }

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(
        f"Done: n={n}  wall_s={elapsed:.1f}  agreement={summary['findings']['agreement_rate_vs_reference']}"
    )
    print(f"  wrote {args.output_jsonl}")
    if args.summary_json:
        print(f"  summary {args.summary_json}")
    return 0


if __name__ == "__main__":
    # Windows spawn — guard required for multiprocessing.
    mp.freeze_support()
    raise SystemExit(main())
