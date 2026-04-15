#!/usr/bin/env python3
"""
**Simplex decision map** for the weighted mixture scorer (Phase 2–3 successor experiment).

Evaluates a **barycentric grid** on the util/deon/virtue simplex (cheap vs million Monte Carlo),
records **winner**, **top-2 gap**, **ranking hash**, **softmax entropy**, and optionally:

- **Bisection** along grid edges where adjacent mixture points disagree on the winner.
- **Ternary plots** (PNG) if ``matplotlib`` is installed: winner scatter; with ``--plot-extended`` also **gap** and **entropy** heatmaps and **boundary** overlay (bisection anchors).
- Per screening/refinement row: optional **distance_to_nearest_boundary** (2D ternary distance to nearest edge-bisection point).

Does **not** run ``EthicalKernel.process``. See ``experiments/README.md``.

Example::

    python scripts/run_simplex_decision_map.py --denominator 40 --scenario-ids 16 \\
        --output-json experiments/out/simplex_map.json --bisect-edges --plot-dir experiments/out/plots
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.modules.weighted_ethics_scorer import WeightedEthicsScorer  # noqa: E402
from src.sandbox.simplex_mixture_probe import (  # noqa: E402
    adjacent_barycentric_pairs,
    bisect_flip_along_segment,
    iter_barycentric_grid,
    mixture_ranking,
)
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402


def _sample_simplex_near(
    w: np.ndarray, band: float, rng: np.random.Generator
) -> np.ndarray:
    """Perturb a mixture point and renormalize to the 2-simplex."""
    noise = rng.normal(0.0, float(band), size=3)
    w2 = np.clip(np.asarray(w, dtype=np.float64) + noise, 1e-12, None)
    s = float(np.sum(w2))
    return w2 / s


def _row_from_mixture_result(
    r: dict[str, Any],
    *,
    sampling_phase: str,
    full_ranking: bool,
    include_softmax_entropy: bool,
) -> dict[str, Any]:
    row: dict[str, Any] = {
        "mixture_weights": r["mixture_weights"],
        "winner": r["winner"],
        "score_gap_top2": r["score_gap_top2"],
        "score_gap_top3": r.get("score_gap_top3"),
        "score_gap_12": r["score_gap_top2"],
        "score_gap_13": r.get("score_gap_top3"),
        "ranking_order": r.get("ranking_order"),
        "ranking_hash": r["ranking_hash"],
        "sampling_phase": sampling_phase,
    }
    if full_ranking and r.get("ranking"):
        row["candidates_ranked"] = [
            {"action": x["action"], "score": x["expected_impact"], "rank": x["rank"]}
            for x in r["ranking"]
        ]
    if include_softmax_entropy:
        row["score_entropy_softmax"] = r["score_entropy_softmax"]
    return row


def _barycentric_to_xy(w: np.ndarray) -> tuple[float, float]:
    """Equilateral-triangle embedding of the 2-simplex (vertices util, deon, virtue)."""
    w = np.asarray(w, dtype=np.float64)
    x = float(w[1] + 0.5 * w[2])
    y = float((np.sqrt(3) / 2.0) * w[2])
    return x, y


def _triangle_axes(ax: Any) -> None:  # matplotlib Axes
    ax.plot([0, 1, 0.5, 0], [0, 0, np.sqrt(3) / 2, 0], "k-", linewidth=0.8)
    ax.set_aspect("equal")
    ax.axis("off")


def _flip_points_xy(bisections: list[dict[str, Any]]) -> list[tuple[float, float]]:
    out: list[tuple[float, float]] = []
    for b in bisections:
        wf = b.get("w_at_flip")
        if not wf:
            continue
        out.append(_barycentric_to_xy(np.array(wf, dtype=np.float64)))
    return out


def _attach_distance_to_nearest_boundary(
    rows: list[dict[str, Any]],
    *,
    bisections: list[dict[str, Any]],
) -> None:
    """Euclidean distance in ternary (x,y) space to nearest edge-bisection flip point."""
    flip_xy = _flip_points_xy(bisections)
    for r in rows:
        w = np.array(r["mixture_weights"], dtype=np.float64)
        x, y = _barycentric_to_xy(w)
        if not flip_xy:
            r["distance_to_nearest_boundary"] = None
        else:
            d = min(float(np.hypot(x - fx, y - fy)) for fx, fy in flip_xy)
            r["distance_to_nearest_boundary"] = round(d, 6)


def _maybe_plot_ternary(
    rows: list[dict[str, Any]],
    *,
    scenario_id: int,
    scenario_name: str,
    plot_dir: Path,
    bisections: list[dict[str, Any]] | None = None,
    plot_extended: bool = False,
) -> None:
    try:
        import matplotlib.pyplot as plt
        from matplotlib.lines import Line2D
    except ImportError:
        print(
            "matplotlib not installed; skip ternary plot. "
            "Install with: pip install matplotlib",
            file=sys.stderr,
        )
        return

    plot_dir.mkdir(parents=True, exist_ok=True)
    plot_rows = [r for r in rows if r.get("sampling_phase", "screening") == "screening"]
    bisections = bisections or []
    title_base = (
        f"Scenario {scenario_id}: {scenario_name[:60]}…"
        if len(scenario_name) > 60
        else f"Scenario {scenario_id}: {scenario_name}"
    )

    winners = [r["winner"] for r in plot_rows if r.get("winner")]
    uniq = sorted(set(winners))
    cmap = plt.get_cmap("tab10")
    color_of = {w: cmap(i % 10) for i, w in enumerate(uniq)}

    xs, ys, cs = [], [], []
    for r in plot_rows:
        w = np.array(r["mixture_weights"], dtype=np.float64)
        x, y = _barycentric_to_xy(w)
        xs.append(x)
        ys.append(y)
        cs.append(color_of.get(r["winner"], (0.5, 0.5, 0.5, 1.0)))

    fig, ax = plt.subplots(figsize=(6, 5.5))
    ax.scatter(xs, ys, c=cs, s=12, marker="o", edgecolors="k", linewidths=0.2)
    _triangle_axes(ax)
    ax.set_title(title_base)
    for i, w in enumerate(uniq):
        ax.scatter([], [], c=[cmap(i % 10)], label=w, s=30)
    ax.legend(loc="upper right", fontsize=8)
    out = plot_dir / f"simplex_map_{scenario_id}.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {out}", file=sys.stderr)

    if not plot_extended:
        return

    # Heatmap: top-2 score gap (hot = tight race)
    gaps = [
        float(r["score_gap_top2"])
        for r in plot_rows
        if r.get("score_gap_top2") is not None
    ]
    gmax = max(gaps) if gaps else 1.0
    gmin = min(gaps) if gaps else 0.0
    fig2, ax2 = plt.subplots(figsize=(6, 5.5))
    gx, gy, gz = [], [], []
    for r in plot_rows:
        if r.get("score_gap_top2") is None:
            continue
        w = np.array(r["mixture_weights"], dtype=np.float64)
        x, y = _barycentric_to_xy(w)
        gx.append(x)
        gy.append(y)
        gz.append(float(r["score_gap_top2"]))
    if gz:
        sc = ax2.scatter(
            gx,
            gy,
            c=gz,
            s=22,
            cmap="inferno",
            vmin=gmin,
            vmax=gmax,
            edgecolors="k",
            linewidths=0.15,
        )
        plt.colorbar(sc, ax=ax2, fraction=0.046, pad=0.04, label="score_gap top-1 vs top-2")
    _triangle_axes(ax2)
    ax2.set_title(f"{title_base} — score gap (tight=hot)")
    out2 = plot_dir / f"simplex_map_{scenario_id}_gap12.png"
    fig2.savefig(out2, dpi=150, bbox_inches="tight")
    plt.close(fig2)
    print(f"wrote {out2}", file=sys.stderr)

    # Heatmap: softmax entropy over candidate scores
    ex, ey, ez = [], [], []
    for r in plot_rows:
        if r.get("score_entropy_softmax") is None:
            continue
        w = np.array(r["mixture_weights"], dtype=np.float64)
        x, y = _barycentric_to_xy(w)
        ex.append(x)
        ey.append(y)
        ez.append(float(r["score_entropy_softmax"]))
    if ez:
        fig3, ax3 = plt.subplots(figsize=(6, 5.5))
        emin, emax = float(np.min(ez)), float(np.max(ez))
        sc3 = ax3.scatter(
            ex,
            ey,
            c=ez,
            s=22,
            cmap="viridis",
            vmin=emin,
            vmax=emax,
            edgecolors="k",
            linewidths=0.15,
        )
        plt.colorbar(sc3, ax=ax3, fraction=0.046, pad=0.04, label="softmax entropy")
        _triangle_axes(ax3)
        ax3.set_title(f"{title_base} — softmax entropy")
        out3 = plot_dir / f"simplex_map_{scenario_id}_entropy.png"
        fig3.savefig(out3, dpi=150, bbox_inches="tight")
        plt.close(fig3)
        print(f"wrote {out3}", file=sys.stderr)

    # Winners + bisection flip points (approximate boundary anchors)
    fig4, ax4 = plt.subplots(figsize=(6, 5.5))
    ax4.scatter(xs, ys, c=cs, s=10, marker="o", edgecolors="k", linewidths=0.2)
    fxy = _flip_points_xy(bisections)
    if fxy:
        fx, fy = zip(*fxy)
        ax4.scatter(
            fx,
            fy,
            s=55,
            facecolors="none",
            edgecolors="k",
            linewidths=1.2,
            label="edge bisection",
        )
    _triangle_axes(ax4)
    ax4.set_title(f"{title_base} — winners + boundary anchors")
    leg_handles = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            label=w,
            markerfacecolor=cmap(i % 10),
            markersize=8,
            linestyle="None",
        )
        for i, w in enumerate(uniq)
    ]
    if fxy:
        leg_handles.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="none",
                markersize=9,
                markeredgecolor="k",
                markeredgewidth=1.2,
                linestyle="None",
                label="edge bisection",
            )
        )
    ax4.legend(handles=leg_handles, loc="upper right", fontsize=7)
    out4 = plot_dir / f"simplex_map_{scenario_id}_boundaries.png"
    fig4.savefig(out4, dpi=150, bbox_inches="tight")
    plt.close(fig4)
    print(f"wrote {out4}", file=sys.stderr)


def run_one_scenario(
    scenario_id: int,
    *,
    denominator: int,
    bisect_edges: bool,
    full_ranking: bool = False,
    include_softmax_entropy: bool = True,
    refinement_band: float = 0.0,
    refinement_samples: int = 0,
    refinement_seed: int = 42,
) -> dict[str, Any]:
    if scenario_id not in ALL_SIMULATIONS:
        raise ValueError(f"Unknown scenario_id {scenario_id}")
    scn = ALL_SIMULATIONS[scenario_id]()
    text = f"[SIM {scenario_id}] {scn.name}"
    actions = list(scn.actions)
    grid = iter_barycentric_grid(denominator)

    scorer = WeightedEthicsScorer()
    rows: list[dict[str, Any]] = []
    winners_at: dict[tuple[float, float, float], str | None] = {}
    for w in grid:
        r = mixture_ranking(
            scorer,
            mixture=w,
            scenario=text,
            context=scn.context,
            signals=scn.signals,
            actions=actions,
        )
        key = tuple(round(float(x), 6) for x in w)
        winners_at[key] = r["winner"]
        rows.append(
            _row_from_mixture_result(
                r,
                sampling_phase="screening",
                full_ranking=full_ranking,
                include_softmax_entropy=include_softmax_entropy,
            )
        )

    n_screen = len(rows)

    bisections: list[dict[str, Any]] = []
    if bisect_edges:
        for wa, wb in adjacent_barycentric_pairs(denominator):
            key_a = tuple(round(float(x), 6) for x in wa)
            key_b = tuple(round(float(x), 6) for x in wb)
            win_a = winners_at.get(key_a)
            win_b = winners_at.get(key_b)
            if win_a and win_b and win_a != win_b:
                bf = bisect_flip_along_segment(
                    wa,
                    wb,
                    scenario=text,
                    context=scn.context,
                    signals=scn.signals,
                    actions=actions,
                )
                if bf:
                    bisections.append(
                        {
                            "edge": [
                                [round(float(x), 6) for x in wa],
                                [round(float(x), 6) for x in wb],
                            ],
                            **bf,
                        }
                    )

    if refinement_samples > 0:
        band = float(refinement_band) if refinement_band > 0 else 0.08
        rng = np.random.default_rng(int(refinement_seed))
        anchors: list[np.ndarray] = []
        for b in bisections:
            anchors.append(np.array(b["w_at_flip"], dtype=np.float64))
        if not anchors:
            tight = sorted(
                rows[:n_screen],
                key=lambda x: float(x["score_gap_top2"])
                if x.get("score_gap_top2") is not None
                else 999.0,
            )[: min(40, n_screen)]
            for tr in tight:
                anchors.append(np.array(tr["mixture_weights"], dtype=np.float64))
        if not anchors:
            anchors = [np.ones(3, dtype=np.float64) / 3.0]
        for i in range(int(refinement_samples)):
            a = anchors[i % len(anchors)]
            w = _sample_simplex_near(a, band, rng)
            r = mixture_ranking(
                scorer,
                mixture=w,
                scenario=text,
                context=scn.context,
                signals=scn.signals,
                actions=actions,
            )
            rows.append(
                _row_from_mixture_result(
                    r,
                    sampling_phase="refinement",
                    full_ranking=full_ranking,
                    include_softmax_entropy=include_softmax_entropy,
                )
            )

    _attach_distance_to_nearest_boundary(rows, bisections=bisections)

    winners = [r["winner"] for r in rows if r["winner"]]
    wc = Counter(winners)
    summary = {
        "n_grid_points": n_screen,
        "n_refinement_points": len(rows) - n_screen,
        "n_total_evaluations": len(rows),
        "unique_winners": sorted(wc.keys()),
        "counts_by_winner": dict(wc),
        "n_unique_winners": len(wc),
    }

    gaps = [r["score_gap_top2"] for r in rows if r["score_gap_top2"] is not None]
    gap_stats = {}
    if gaps:
        arr = np.array(gaps, dtype=np.float64)
        gap_stats = {
            "min": float(np.min(arr)),
            "max": float(np.max(arr)),
            "mean": float(np.mean(arr)),
            "p10": float(np.percentile(arr, 10)),
            "p50": float(np.percentile(arr, 50)),
            "p90": float(np.percentile(arr, 90)),
        }

    return {
        "scenario_id": scenario_id,
        "scenario_name": scn.name,
        "denominator": denominator,
        "grid_rows": rows,
        "summary": summary,
        "score_gap_stats": gap_stats,
        "bisections_along_edges": bisections,
    }


def main() -> int:
    p = argparse.ArgumentParser(
        description="Mixture simplex grid + optional edge bisection (WeightedEthicsScorer only)."
    )
    p.add_argument(
        "--scenario-ids",
        type=str,
        default="10,11,12,16",
        help="Comma-separated batch IDs (default: frontier + calibration 16).",
    )
    p.add_argument(
        "--denominator",
        type=int,
        default=40,
        help="Barycentric denominator D (grid size ~ (D+2)(D+1)/2). Default 40 → 861 points.",
    )
    p.add_argument(
        "--bisect-edges",
        action="store_true",
        help="Run bisection on grid edges where adjacent points disagree on winner.",
    )
    p.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help="Write full JSON report.",
    )
    p.add_argument(
        "--output-csv",
        type=Path,
        default=None,
        help="Append flattened grid rows for all scenarios (CSV).",
    )
    p.add_argument(
        "--plot-dir",
        type=Path,
        default=None,
        help="If set, write ternary PNGs per scenario (needs matplotlib).",
    )
    p.add_argument(
        "--plot-extended",
        action="store_true",
        help="With --plot-dir: also write gap12 heatmap, entropy heatmap, and boundary-overlay PNGs.",
    )
    p.add_argument(
        "--full-ranking",
        action="store_true",
        help="Include per-candidate scores and ranks (candidates_ranked) in each row.",
    )
    p.add_argument(
        "--no-softmax-entropy",
        action="store_true",
        help="Omit score_entropy_softmax in each row (smaller JSON).",
    )
    p.add_argument(
        "--refinement-band",
        type=float,
        default=0.05,
        help="Gaussian perturbation scale (in mixture space) around flip anchors for refinement samples.",
    )
    p.add_argument(
        "--refinement-samples",
        type=int,
        default=0,
        help="Extra mixture draws near bisection anchors (or tightest grid points if no bisections).",
    )
    p.add_argument(
        "--refinement-seed",
        type=int,
        default=42,
        help="RNG seed for refinement sampling.",
    )
    args = p.parse_args()

    if args.denominator < 3:
        print("denominator must be >= 3", file=sys.stderr)
        return 2

    ids = [int(x.strip()) for x in args.scenario_ids.split(",") if x.strip()]
    report: dict[str, Any] = {
        "tool": "run_simplex_decision_map",
        "doc": "experiments/README.md",
        "denominator": args.denominator,
        "scenarios": [],
    }

    for sid in ids:
        block = run_one_scenario(
            sid,
            denominator=args.denominator,
            bisect_edges=args.bisect_edges,
            full_ranking=args.full_ranking,
            include_softmax_entropy=not args.no_softmax_entropy,
            refinement_band=args.refinement_band,
            refinement_samples=args.refinement_samples,
            refinement_seed=args.refinement_seed,
        )
        report["scenarios"].append(block)
        if args.plot_dir:
            _maybe_plot_ternary(
                block["grid_rows"],
                scenario_id=sid,
                scenario_name=block["scenario_name"],
                plot_dir=args.plot_dir,
                bisections=block.get("bisections_along_edges") or [],
                plot_extended=args.plot_extended,
            )

    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"wrote {args.output_json}", file=sys.stderr)

    if args.output_csv:
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        with args.output_csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(
                [
                    "scenario_id",
                    "sampling_phase",
                    "w_util",
                    "w_deon",
                    "w_virtue",
                    "winner",
                    "score_gap_top2",
                    "score_gap_top3",
                    "ranking_order",
                    "ranking_hash",
                    "score_entropy_softmax",
                    "distance_to_nearest_boundary",
                ]
            )
            for block in report["scenarios"]:
                sid = block["scenario_id"]
                for r in block["grid_rows"]:
                    mw = r["mixture_weights"]
                    w.writerow(
                        [
                            sid,
                            r.get("sampling_phase", "screening"),
                            mw[0],
                            mw[1],
                            mw[2],
                            r["winner"],
                            r["score_gap_top2"],
                            r.get("score_gap_top3"),
                            r.get("ranking_order"),
                            r["ranking_hash"],
                            r.get("score_entropy_softmax"),
                            r.get("distance_to_nearest_boundary"),
                        ]
                    )
        print(f"wrote {args.output_csv}", file=sys.stderr)

    if not args.output_json and not args.output_csv:
        print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
