#!/usr/bin/env python3
"""
**Protocol v5 (partial)** — mixture screening + refinement + boundary export.

Runs :func:`run_simplex_decision_map.run_one_scenario` per scenario and writes:

- ``screening_grid.csv`` — barycentric grid points only
- ``refinement_band.csv`` — optional extra draws near bisection anchors (may be empty)
- ``boundaries.json`` — edge bisection ``w_at_flip`` anchors per scenario
- ``summary.json`` — counts and winner diversity

**Does not** run ``EthicalKernel.process`` at each mixture point (that remains
``mass_kernel_study`` / ``run_experiment_v4_full_kernel_100k.py``). A stub note is written as
``full_kernel_note.json``.

Example::

    python scripts/run_experiment_v5_sensitivity.py \\
        --scenario-ids 16,17,18,19 \\
        --screening-denominator 30 \\
        --refinement-samples 200 \\
        --output-dir experiments/out/v5_sensitivity/ \\
        --plot-extended
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_run_simplex() -> Any:
    path = ROOT / "scripts" / "run_simplex_decision_map.py"
    spec = importlib.util.spec_from_file_location("run_simplex_decision_map", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    p = argparse.ArgumentParser(description="v5 sensitivity: screening + refinement + boundaries.")
    p.add_argument(
        "--scenario-ids",
        type=str,
        default="16,17,18,19",
        help="Comma-separated batch simulation IDs.",
    )
    p.add_argument(
        "--screening-denominator",
        type=int,
        default=30,
        help="Barycentric denominator for the screening grid.",
    )
    p.set_defaults(bisect_edges=True)
    p.add_argument(
        "--bisect-edges",
        dest="bisect_edges",
        action="store_true",
        help="Run edge bisection (default).",
    )
    p.add_argument(
        "--no-bisect-edges",
        dest="bisect_edges",
        action="store_false",
        help="Disable edge bisection (no boundary anchors).",
    )
    p.add_argument(
        "--refinement-samples",
        type=int,
        default=0,
        help="Extra mixture samples near bisection anchors.",
    )
    p.add_argument(
        "--refinement-band",
        type=float,
        default=0.05,
        help="Gaussian perturbation scale for refinement draws.",
    )
    p.add_argument(
        "--refinement-seed",
        type=int,
        default=42,
        help="RNG seed for refinement.",
    )
    p.add_argument(
        "--full-ranking",
        action="store_true",
        help="Include candidates_ranked in each row.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Output directory (created if missing).",
    )
    p.add_argument(
        "--plot-extended",
        action="store_true",
        help="Write PNGs (winners + optional gap/entropy/boundary heatmaps).",
    )
    args = p.parse_args()

    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)
    plot_dir = out / "plots" if args.plot_extended else None
    if plot_dir:
        plot_dir.mkdir(parents=True, exist_ok=True)

    mod = _load_run_simplex()
    run_one_scenario = mod.run_one_scenario
    maybe_plot = mod._maybe_plot_ternary

    ids = [int(x.strip()) for x in args.scenario_ids.split(",") if x.strip()]
    blocks: list[dict[str, Any]] = []
    for sid in ids:
        block = run_one_scenario(
            sid,
            denominator=int(args.screening_denominator),
            bisect_edges=bool(args.bisect_edges),
            full_ranking=bool(args.full_ranking),
            include_softmax_entropy=True,
            refinement_band=float(args.refinement_band),
            refinement_samples=int(args.refinement_samples),
            refinement_seed=int(args.refinement_seed),
        )
        blocks.append(block)
        if plot_dir is not None:
            maybe_plot(
                block["grid_rows"],
                scenario_id=sid,
                scenario_name=block["scenario_name"],
                plot_dir=plot_dir,
                bisections=block.get("bisections_along_edges") or [],
                plot_extended=bool(args.plot_extended),
            )

    # CSV: screening
    screen_path = out / "screening_grid.csv"
    with screen_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "scenario_id",
                "w_util",
                "w_deon",
                "w_virtue",
                "winner",
                "score_gap_top2",
                "score_gap_top3",
                "ranking_order",
                "score_entropy_softmax",
                "distance_to_nearest_boundary",
            ]
        )
        for block in blocks:
            sid = block["scenario_id"]
            for r in block["grid_rows"]:
                if r.get("sampling_phase", "screening") != "screening":
                    continue
                mw = r["mixture_weights"]
                w.writerow(
                    [
                        sid,
                        mw[0],
                        mw[1],
                        mw[2],
                        r["winner"],
                        r.get("score_gap_top2"),
                        r.get("score_gap_top3"),
                        r.get("ranking_order"),
                        r.get("score_entropy_softmax"),
                        r.get("distance_to_nearest_boundary"),
                    ]
                )

    # CSV: refinement
    ref_path = out / "refinement_band.csv"
    with ref_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            [
                "scenario_id",
                "w_util",
                "w_deon",
                "w_virtue",
                "winner",
                "score_gap_top2",
                "distance_to_nearest_boundary",
            ]
        )
        n_ref = 0
        for block in blocks:
            sid = block["scenario_id"]
            for r in block["grid_rows"]:
                if r.get("sampling_phase") != "refinement":
                    continue
                n_ref += 1
                mw = r["mixture_weights"]
                w.writerow(
                    [
                        sid,
                        mw[0],
                        mw[1],
                        mw[2],
                        r["winner"],
                        r.get("score_gap_top2"),
                        r.get("distance_to_nearest_boundary"),
                    ]
                )

    boundaries: dict[str, Any] = {
        "tool": "run_experiment_v5_sensitivity",
        "scenarios": [],
    }
    for block in blocks:
        boundaries["scenarios"].append(
            {
                "scenario_id": block["scenario_id"],
                "scenario_name": block["scenario_name"],
                "bisections": block.get("bisections_along_edges") or [],
            }
        )
    (out / "boundaries.json").write_text(
        json.dumps(boundaries, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    summary = {
        "scenario_ids": ids,
        "screening_denominator": args.screening_denominator,
        "refinement_samples_requested": args.refinement_samples,
        "refinement_rows_written": n_ref,
        "per_scenario": [
            {
                "scenario_id": b["scenario_id"],
                "n_screening": b["summary"]["n_grid_points"],
                "n_refinement": b["summary"]["n_refinement_points"],
                "n_unique_winners": b["summary"]["n_unique_winners"],
                "unique_winners": b["summary"]["unique_winners"],
                "n_bisections": len(b.get("bisections_along_edges") or []),
            }
            for b in blocks
        ],
    }
    (out / "summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    note = {
        "phase_3_full_kernel": (
            "Not executed here. Use scripts/run_mass_kernel_study.py or "
            "scripts/run_experiment_v4_full_kernel_100k.py for EthicalKernel.process at scale."
        ),
        "mixture_phases": "screening_grid.csv + refinement_band.csv + boundaries.json",
    }
    (out / "full_kernel_note.json").write_text(
        json.dumps(note, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"wrote {screen_path}", file=sys.stderr)
    print(f"wrote {ref_path}", file=sys.stderr)
    print(f"wrote {out / 'boundaries.json'}", file=sys.stderr)
    print(f"wrote {out / 'summary.json'}", file=sys.stderr)
    print(f"wrote {out / 'full_kernel_note.json'}", file=sys.stderr)
    if plot_dir:
        print(f"wrote plots under {plot_dir}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
