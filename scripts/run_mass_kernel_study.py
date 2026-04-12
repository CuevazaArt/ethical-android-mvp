#!/usr/bin/env python3
"""
Mass kernel batch study — up to millions of ``process()`` calls with random pole + Dirichlet mixture weights.

**Not CI.** Use a dedicated venv and disk space; see ``experiments/million_sim/README.md`` and
``docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md``.

Rich output: JSONL + optional CSV, reproducibility meta, weight histograms, agreement by difficulty tier.
Optional ``tqdm`` progress: ``pip install tqdm`` (see ``experiments/million_sim/requirements-experiment.txt``).
"""

from __future__ import annotations

import argparse
import csv
import json
import multiprocessing as mp
import platform
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None  # type: ignore[misc, assignment]

from src.sandbox.mass_kernel_study import (  # noqa: E402
    RECORD_SCHEMA_VERSION,
    load_reference_labels,
    load_tier_labels,
    run_single_simulation,
)

_G: dict[str, Any] = {}


def _init_worker(payload: dict[str, Any]) -> None:
    global _G
    _G = payload


def _worker(i: int) -> dict[str, Any]:
    row = run_single_simulation(
        i,
        base_seed=_G["base_seed"],
        refs=_G["refs"],
        tiers=_G["tiers"],
        stratify_scenario=_G["stratify_scenario"],
        scenario_id_override=_G["scenario_id_override"],
        n_total=_G["n_total"],
    )
    row["schema_version"] = RECORD_SCHEMA_VERSION
    row["run_label"] = _G.get("run_label") or ""
    return row


def _git_head_short(repo: Path) -> str | None:
    try:
        r = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=repo,
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
        )
        if r.returncode == 0 and r.stdout.strip():
            return r.stdout.strip()
    except OSError:
        pass
    return None


def _bin10(x: float) -> int:
    """Index 0..9 for histogram over [0,1]."""
    v = float(x)
    return int(min(9, max(0, v * 10)))


def _csv_fieldnames() -> list[str]:
    return [
        "schema_version",
        "run_label",
        "i",
        "kernel_seed",
        "scenario_id",
        "difficulty_tier",
        "pole_compassionate",
        "pole_conservative",
        "pole_optimistic",
        "mixture_util",
        "mixture_deon",
        "mixture_virtue",
        "final_action",
        "decision_mode",
        "reference_action",
        "agree_reference",
    ]


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
        "--run-label",
        type=str,
        default="",
        help="Tag embedded in each row and meta (e.g. pilot_A, machine_id).",
    )
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
    p.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Optional wide CSV (same columns as JSONL) for pandas/R/Excel.",
    )
    p.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar if tqdm is installed.",
    )
    args = p.parse_args()

    n = max(1, args.n_simulations)
    if n > 100_000 and not args.i_accept_large_run:
        print(
            "Refusing n>100000 without --i-accept-large-run (disk/time). "
            "See docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md",
            file=sys.stderr,
        )
        return 2

    started = datetime.now(UTC).isoformat()
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
        "run_label": args.run_label.strip(),
    }

    t0 = time.perf_counter()
    by_action: Counter[str] = Counter()
    by_mode: Counter[str] = Counter()
    by_sid: Counter[int] = Counter()
    by_tier: Counter[str] = Counter()
    by_tier_ref: Counter[str] = Counter()
    by_tier_agree: Counter[str] = Counter()
    agree_n = 0
    agree_denom = 0

    hist_pole_c = np.zeros(10, dtype=np.int64)
    hist_pole_o = np.zeros(10, dtype=np.int64)
    hist_pole_op = np.zeros(10, dtype=np.int64)
    hist_m_u = np.zeros(10, dtype=np.int64)
    hist_m_d = np.zeros(10, dtype=np.int64)
    hist_m_v = np.zeros(10, dtype=np.int64)

    chunksize = max(1, n // max(8, args.workers * 16))

    csv_f = None
    csv_w: csv.DictWriter | None = None
    if args.output_csv is not None:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        csv_f = open(args.output_csv, "w", newline="", encoding="utf-8")
        csv_w = csv.DictWriter(csv_f, fieldnames=_csv_fieldnames())
        csv_w.writeheader()

    try:
        with open(args.output_jsonl, "w", encoding="utf-8") as out_f:
            with mp.Pool(args.workers, initializer=_init_worker, initargs=(payload,)) as pool:
                imap_it = pool.imap(_worker, range(n), chunksize=chunksize)
                if args.progress:
                    if tqdm is None:
                        print("Install tqdm for --progress: pip install tqdm", file=sys.stderr)
                    else:
                        imap_it = tqdm(imap_it, total=n, unit="sim", mininterval=0.3)

                for row in imap_it:
                    out_f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    if csv_w is not None:
                        csv_w.writerow({k: row.get(k) for k in _csv_fieldnames()})

                    by_action[row["final_action"]] += 1
                    by_mode[row["decision_mode"]] += 1
                    by_sid[int(row["scenario_id"])] += 1

                    tier = row.get("difficulty_tier") or "unspecified"
                    by_tier[tier] += 1
                    if row.get("reference_action") is not None:
                        agree_denom += 1
                        by_tier_ref[tier] += 1
                        if row["agree_reference"]:
                            agree_n += 1
                            by_tier_agree[tier] += 1

                    hist_pole_c[_bin10(row["pole_compassionate"])] += 1
                    hist_pole_o[_bin10(row["pole_conservative"])] += 1
                    hist_pole_op[_bin10(row["pole_optimistic"])] += 1
                    hist_m_u[_bin10(row["mixture_util"])] += 1
                    hist_m_d[_bin10(row["mixture_deon"])] += 1
                    hist_m_v[_bin10(row["mixture_virtue"])] += 1
    finally:
        if csv_f is not None:
            csv_f.close()

    elapsed = time.perf_counter() - t0
    finished = datetime.now(UTC).isoformat()

    agreement_by_tier: dict[str, dict[str, float | int]] = {}
    for tier in sorted(set(by_tier.keys()) | set(by_tier_ref.keys())):
        tr = by_tier_ref.get(tier, 0)
        ta = by_tier_agree.get(tier, 0)
        agreement_by_tier[tier] = {
            "with_reference": tr,
            "agree": ta,
            "agreement_rate": float(ta) / float(tr) if tr else 0.0,
        }

    summary = {
        "meta": {
            "schema_version": RECORD_SCHEMA_VERSION,
            "run_label": args.run_label.strip() or None,
            "n_simulations": n,
            "base_seed": args.base_seed,
            "workers": args.workers,
            "stratify_scenarios": args.stratify_scenarios,
            "fixture": str(args.fixture.resolve()),
            "runtime_seconds": round(elapsed, 3),
            "sims_per_second": round(n / elapsed, 2) if elapsed > 0 else None,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "git_commit_short": _git_head_short(ROOT),
            "argv": sys.argv,
            "doc": "docs/proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md",
        },
        "findings": {
            "agreement_rate_vs_reference": agree_n / agree_denom if agree_denom else None,
            "agreement_denominator": agree_denom,
            "unique_final_actions": len(by_action),
            "counts_by_final_action": dict(by_action),
            "counts_by_decision_mode": dict(by_mode),
            "counts_by_scenario_id": {str(k): v for k, v in sorted(by_sid.items())},
            "counts_by_difficulty_tier": dict(by_tier),
            "agreement_by_difficulty_tier": agreement_by_tier,
            "histograms": {
                "bin_edges_01": [round(i / 10.0, 1) for i in range(11)],
                "pole_compassionate": hist_pole_c.tolist(),
                "pole_conservative": hist_pole_o.tolist(),
                "pole_optimistic": hist_pole_op.tolist(),
                "mixture_util": hist_m_u.tolist(),
                "mixture_deon": hist_m_d.tolist(),
                "mixture_virtue": hist_m_v.tolist(),
            },
        },
    }

    if args.summary_json is not None:
        args.summary_json.parent.mkdir(parents=True, exist_ok=True)
        args.summary_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(
        f"Done: n={n}  wall_s={elapsed:.1f}  agreement={summary['findings']['agreement_rate_vs_reference']}"
    )
    print(f"  wrote {args.output_jsonl}")
    if args.output_csv:
        print(f"  csv {args.output_csv}")
    if args.summary_json:
        print(f"  summary {args.summary_json}")
    return 0


if __name__ == "__main__":
    mp.freeze_support()
    raise SystemExit(main())
