#!/usr/bin/env python3
"""
Mass kernel batch study — up to millions of ``process()`` calls with random pole + Dirichlet mixture weights.

**Not CI.** Use a dedicated venv and disk space; see ``experiments/README.md`` and
``docs/proposals/README.md``.

Rich output: JSONL + optional CSV, reproducibility meta, weight histograms, agreement by difficulty tier.
Optional ``tqdm`` progress: ``pip install tqdm`` (see ``experiments/requirements-experiment.txt``).
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
    DEFAULT_BORDERLINE_SCENARIO_IDS,
    DEFAULT_CLASSIC_ECONOMY_IDS,
    DEFAULT_POLEMIC_EXTREME_IDS,
    DEFAULT_STRESS_SCENARIO_IDS,
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
        experiment_protocol=_G["experiment_protocol"],
        lane_split=_G["lane_split"],
        stress_scenario_ids=_G["stress_scenario_ids"],
        borderline_scenario_ids=_G["borderline_scenario_ids"],
        polemic_extreme_ids=_G["polemic_extreme_ids"],
        classic_economy_ids=_G["classic_economy_ids"],
        classic_stratify_economy=_G["classic_stratify_economy"],
        poles_pre_argmax=_G["poles_pre_argmax"],
        context_richness_pre_argmax=_G["context_richness_pre_argmax"],
        signal_stress=_G["signal_stress"],
        pole_weight_low=_G["pole_weight_low"],
        pole_weight_high=_G["pole_weight_high"],
        mixture_dirichlet_alpha=_G["mixture_dirichlet_alpha"],
        bma_enabled=_G["bma_enabled"],
        bma_dirichlet_alpha=_G["bma_dirichlet_alpha"],
        bma_n_samples=_G["bma_n_samples"],
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


def _parse_lane_split_flex(s: str) -> tuple[float, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) not in (3, 4, 5):
        raise argparse.ArgumentTypeError(
            "lane-split must be 3 (v2), 4 (v3), or 5 (v4) comma-separated floats summing to 1"
        )
    vals = tuple(float(x) for x in parts)
    if abs(sum(vals) - 1.0) > 1e-4:
        raise argparse.ArgumentTypeError("lane-split values must sum to 1.0")
    return vals


def _parse_stress_ids(s: str) -> tuple[int, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return DEFAULT_STRESS_SCENARIO_IDS
    return tuple(int(x) for x in parts)


def _parse_borderline_ids(s: str) -> tuple[int, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return DEFAULT_BORDERLINE_SCENARIO_IDS
    return tuple(int(x) for x in parts)


def _parse_polemic_extreme_ids(s: str) -> tuple[int, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return DEFAULT_POLEMIC_EXTREME_IDS
    return tuple(int(x) for x in parts)


def _parse_classic_economy_ids(s: str) -> tuple[int, ...]:
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if not parts:
        return DEFAULT_CLASSIC_ECONOMY_IDS
    return tuple(int(x) for x in parts)


def _parse_pole_weight_range(s: str) -> tuple[float, float]:
    """``lo,hi`` inclusive range for Uniform pole draws (lanes C/D/E and legacy)."""
    parts = [p.strip() for p in s.split(",") if p.strip()]
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("pole-weight-range must be two comma-separated floats")
    lo, hi = float(parts[0]), float(parts[1])
    if not (0.0 <= lo < hi <= 1.0):
        raise argparse.ArgumentTypeError("pole-weight-range needs 0 <= lo < hi <= 1")
    return lo, hi


def _csv_fieldnames() -> list[str]:
    return [
        "schema_version",
        "run_label",
        "i",
        "kernel_seed",
        "scenario_id",
        "difficulty_tier",
        "experiment_protocol",
        "experiment_lane",
        "ablation_tag",
        "stress_scenario_ids",
        "borderline_scenario_ids",
        "polemic_extreme_ids",
        "classic_economy_ids",
        "poles_pre_argmax",
        "context_richness_pre_argmax",
        "signal_stress",
        "signal_noise_trace",
        "sampling_pole_lo",
        "sampling_pole_hi",
        "sampling_mixture_dirichlet_alpha",
        "pole_compassionate",
        "pole_conservative",
        "pole_optimistic",
        "mixture_util",
        "mixture_deon",
        "mixture_virtue",
        "mixture_entropy",
        "dominant_hypothesis",
        "scorer_second_action",
        "scorer_second_ei",
        "ei_margin",
        "ei_margin_bin",
        "observation_palette",
        "final_action",
        "decision_mode",
        "reference_action",
        "agree_reference",
        # ADR 0012 Phase D — BMA win probabilities
        "bma_enabled",
        "bma_win_prob_winner",
        "bma_win_prob_max",
        "bma_winner_prob_at_final_action",
    ]


def main() -> int:
    p = argparse.ArgumentParser(
        description="Mass batch kernel study (pole + mixture sweep; legacy / v2 / v3 / v4 lanes)."
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
        help="Balance scenario IDs per lane (recommended).",
    )
    p.add_argument(
        "--experiment-protocol",
        choices=("legacy", "v2", "v3", "v4"),
        default="legacy",
        help="legacy | v2 | v3 (4 lanes) | v4 (5 lanes + polemic/extreme 13–15). See PROPOSAL doc.",
    )
    p.add_argument(
        "--lane-split",
        type=str,
        default="",
        help="Comma floats: 3 (v2), 4 (v3), or 5 (v4); must sum to 1. Defaults by protocol.",
    )
    p.add_argument(
        "--stress-scenario-ids",
        type=_parse_stress_ids,
        default=",".join(str(x) for x in DEFAULT_STRESS_SCENARIO_IDS),
        help="Lane B: comma-separated batch scenario IDs.",
    )
    p.add_argument(
        "--borderline-scenario-ids",
        type=_parse_borderline_ids,
        default=",".join(str(x) for x in DEFAULT_BORDERLINE_SCENARIO_IDS),
        help="Lane D (v3/v4): frontier scenario IDs (default 10–12).",
    )
    p.add_argument(
        "--polemic-extreme-ids",
        type=_parse_polemic_extreme_ids,
        default=",".join(str(x) for x in DEFAULT_POLEMIC_EXTREME_IDS),
        help="Lane E (v4): polemic + extreme IDs (default 13–15).",
    )
    p.add_argument(
        "--classic-economy-ids",
        type=_parse_classic_economy_ids,
        default=",".join(str(x) for x in DEFAULT_CLASSIC_ECONOMY_IDS),
        help="Classic triple for lanes A/C (default 1,5,7) to save runs vs full 1–9.",
    )
    p.add_argument(
        "--legacy-economy-classics",
        action="store_true",
        help="Legacy + stratify: rotate only --classic-economy-ids instead of 1–9.",
    )
    p.add_argument(
        "--poles-pre-argmax",
        action="store_true",
        help="Set KERNEL_POLES_PRE_ARGMAX (poles modulate valuations before argmax). For v3 this is the default unless --no-poles-pre-argmax.",
    )
    p.add_argument(
        "--no-poles-pre-argmax",
        action="store_true",
        help="v3/v4: turn off pole pre-argmax (default-on for v3/v4).",
    )
    p.add_argument(
        "--context-richness-pre-argmax",
        action="store_true",
        help="Set KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX (social/sympathetic/locus texture before argmax).",
    )
    p.add_argument(
        "--signal-stress",
        type=float,
        default=0.0,
        help="Synthetic signal perturbation stress in [0,1] (see synthetic_stochastic).",
    )
    p.add_argument(
        "--pole-weight-range",
        type=_parse_pole_weight_range,
        default=(0.05, 0.95),
        metavar="LO,HI",
        help="Uniform range for each ethical pole axis (legacy + lanes C/D/E). Default 0.05,0.95.",
    )
    p.add_argument(
        "--mixture-dirichlet-alpha",
        type=float,
        default=1.0,
        help="Symmetric Dirichlet concentration for mixture weights; 1=historical uniform on simplex, "
        "larger values concentrate near (1/3,1/3,1/3).",
    )
    # ADR 0012 Phase D — BMA win-probability recording
    p.add_argument(
        "--bma-enabled",
        action="store_true",
        help="Record BMA win probabilities per row (ADR 0012 Level 1). Adds bma_win_prob_* fields.",
    )
    p.add_argument(
        "--bma-alpha",
        type=float,
        default=3.0,
        metavar="ALPHA",
        help="Symmetric Dirichlet alpha for BMA prior (default 3.0; symmetric → center of simplex).",
    )
    p.add_argument(
        "--bma-samples",
        type=int,
        default=5000,
        metavar="N",
        help="Monte Carlo draws for BMA win probabilities per simulation (default 5000).",
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
            "See docs/proposals/README.md",
            file=sys.stderr,
        )
        return 2

    proto = args.experiment_protocol
    if args.lane_split.strip():
        lane_split = _parse_lane_split_flex(args.lane_split.strip())
    elif proto == "v4":
        lane_split = (0.20, 0.16, 0.12, 0.20, 0.32)
    elif proto == "v3":
        lane_split = (0.28, 0.22, 0.12, 0.38)
    else:
        lane_split = (0.45, 0.35, 0.2)

    if proto == "v2" and len(lane_split) != 3:
        print("v2 requires --lane-split with exactly 3 fractions.", file=sys.stderr)
        return 2
    if proto == "v3" and len(lane_split) != 4:
        print("v3 requires --lane-split with exactly 4 fractions (or omit for default).", file=sys.stderr)
        return 2
    if proto == "v4" and len(lane_split) != 5:
        print("v4 requires --lane-split with exactly 5 fractions (or omit for default).", file=sys.stderr)
        return 2

    if proto in ("v3", "v4"):
        poles_pre_argmax = not bool(args.no_poles_pre_argmax)
    else:
        poles_pre_argmax = bool(args.poles_pre_argmax)

    signal_stress = float(np.clip(args.signal_stress, 0.0, 1.0))
    pole_lo, pole_hi = args.pole_weight_range
    mix_alpha = float(args.mixture_dirichlet_alpha)

    started = datetime.now(UTC).isoformat()
    refs = load_reference_labels(args.fixture)
    tiers = load_tier_labels(args.fixture)

    stress_ids: tuple[int, ...] = args.stress_scenario_ids
    borderline_ids: tuple[int, ...] = args.borderline_scenario_ids
    polemic_ids: tuple[int, ...] = args.polemic_extreme_ids
    classic_economy: tuple[int, ...] = args.classic_economy_ids
    context_richness = bool(args.context_richness_pre_argmax)

    args.output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "base_seed": args.base_seed,
        "refs": refs,
        "tiers": tiers,
        "stratify_scenario": args.stratify_scenarios,
        "scenario_id_override": None,
        "n_total": n,
        "run_label": args.run_label.strip(),
        "experiment_protocol": proto,
        "lane_split": lane_split,
        "stress_scenario_ids": stress_ids,
        "borderline_scenario_ids": borderline_ids,
        "polemic_extreme_ids": polemic_ids,
        "classic_economy_ids": classic_economy,
        "classic_stratify_economy": bool(args.legacy_economy_classics),
        "poles_pre_argmax": poles_pre_argmax,
        "context_richness_pre_argmax": context_richness,
        "signal_stress": signal_stress,
        "pole_weight_low": pole_lo,
        "pole_weight_high": pole_hi,
        "mixture_dirichlet_alpha": mix_alpha,
        "bma_enabled": bool(args.bma_enabled),
        "bma_dirichlet_alpha": float(args.bma_alpha),
        "bma_n_samples": max(100, int(args.bma_samples)),
    }

    t0 = time.perf_counter()
    by_action: Counter[str] = Counter()
    by_mode: Counter[str] = Counter()
    by_sid: Counter[int] = Counter()
    by_tier: Counter[str] = Counter()
    by_tier_ref: Counter[str] = Counter()
    by_tier_agree: Counter[str] = Counter()
    by_lane: Counter[str] = Counter()
    by_palette: Counter[str] = Counter()
    by_margin_bin: Counter[str] = Counter()
    by_dom: Counter[str] = Counter()
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
                        row_csv = {k: row.get(k) for k in _csv_fieldnames()}
                        for list_key in (
                            "stress_scenario_ids",
                            "borderline_scenario_ids",
                            "polemic_extreme_ids",
                            "classic_economy_ids",
                        ):
                            if isinstance(row_csv.get(list_key), list):
                                row_csv[list_key] = json.dumps(row_csv[list_key], ensure_ascii=False)
                        if row_csv.get("signal_noise_trace") is not None:
                            row_csv["signal_noise_trace"] = json.dumps(
                                row_csv["signal_noise_trace"], ensure_ascii=False
                            )
                        csv_w.writerow(row_csv)

                    by_action[row["final_action"]] += 1
                    by_mode[row["decision_mode"]] += 1
                    by_sid[int(row["scenario_id"])] += 1
                    by_lane[str(row.get("experiment_lane", ""))] += 1
                    by_palette[str(row.get("observation_palette", ""))] += 1
                    by_margin_bin[str(row.get("ei_margin_bin", ""))] += 1
                    by_dom[str(row.get("dominant_hypothesis", ""))] += 1

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
            "experiment_protocol": proto,
            "lane_split": list(lane_split) if proto in ("v2", "v3", "v4") else None,
            "stress_scenario_ids": list(stress_ids),
            "borderline_scenario_ids": list(borderline_ids),
            "polemic_extreme_ids": list(polemic_ids),
            "classic_economy_ids": list(classic_economy),
            "legacy_economy_classics": bool(args.legacy_economy_classics),
            "poles_pre_argmax": poles_pre_argmax,
            "context_richness_pre_argmax": context_richness,
            "signal_stress": signal_stress,
            "weight_sampling": {
                "pole_weight_low": pole_lo,
                "pole_weight_high": pole_hi,
                "mixture_dirichlet_alpha": mix_alpha,
                "note": "Poles Uniform(lo,hi) per axis where random; mixture symmetric Dirichlet(α,α,α).",
            },
            "fixture": str(args.fixture.resolve()),
            "runtime_seconds": round(elapsed, 3),
            "sims_per_second": round(n / elapsed, 2) if elapsed > 0 else None,
            "started_at_utc": started,
            "finished_at_utc": finished,
            "platform": platform.platform(),
            "python": sys.version.split()[0],
            "git_commit_short": _git_head_short(ROOT),
            "argv": sys.argv,
            "doc": "docs/proposals/README.md",
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
            "counts_by_experiment_lane": dict(by_lane),
            "counts_by_ei_margin_bin": dict(by_margin_bin),
            "counts_by_dominant_hypothesis": dict(by_dom),
            "top_observation_palettes": dict(by_palette.most_common(40)),
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
