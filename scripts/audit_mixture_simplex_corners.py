#!/usr/bin/env python3
"""
Phase-1 **simplex corner audit** for the weighted mixture scorer (no EthicalKernel, no MalAbs).

For each batch scenario, sets ``hypothesis_weights`` to the three **pure** corners of the
util/deon/virtue simplex plus the **uniform** center, and records the **full ranking** of
viable actions by expected impact (same path as ``WeightedEthicsScorer.evaluate``).

**Use:** answer “does the winner change under extreme mixture axes?” before spending budget on
large-N Monte Carlo. See ``experiments/README.md``.

**Not** a substitute for ``EthicalKernel.process`` (no Absolute Evil, will, poles-as-narrative, etc.).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.modules.weighted_ethics_scorer import WeightedEthicsScorer  # noqa: E402
from src.sandbox.simplex_mixture_probe import mixture_ranking  # noqa: E402
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402

_CORNERS: dict[str, np.ndarray] = {
    "util_corner": np.array([1.0, 0.0, 0.0], dtype=np.float64),
    "deon_corner": np.array([0.0, 1.0, 0.0], dtype=np.float64),
    "virtue_corner": np.array([0.0, 0.0, 1.0], dtype=np.float64),
    "uniform_center": np.array([1.0, 1.0, 1.0], dtype=np.float64) / 3.0,
}


def audit_scenario(scenario_id: int) -> dict[str, Any]:
    if scenario_id not in ALL_SIMULATIONS:
        raise ValueError(f"Unknown scenario_id {scenario_id}")
    scn = ALL_SIMULATIONS[scenario_id]()
    text = f"[SIM {scenario_id}] {scn.name}"
    per_corner: dict[str, Any] = {}
    winners: list[str] = []
    scorer = WeightedEthicsScorer()
    for label, vec in _CORNERS.items():
        r = mixture_ranking(
            scorer,
            mixture=vec,
            scenario=text,
            context=scn.context,
            signals=scn.signals,
            actions=list(scn.actions),
        )
        per_corner[label] = {
            "mixture_weights": r["mixture_weights"],
            "pruned": r["pruned"],
            "ranking": r["ranking"],
            "winner": r["winner"],
            "score_gap_top2": r["score_gap_top2"],
        }
        w = per_corner[label].get("winner")
        if w is not None:
            winners.append(w)
    unique_winners = sorted(set(winners))
    return {
        "scenario_id": scenario_id,
        "scenario_name": scn.name,
        "corners": per_corner,
        "winner_varies_across_corners": len(unique_winners) > 1,
        "unique_winners_at_corners": unique_winners,
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Mixture simplex corner audit (batch scenarios).")
    p.add_argument(
        "--scenario-ids",
        type=str,
        default="all",
        help='Comma-separated batch IDs or "all" (default: all registered simulations).',
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON (default: stdout).",
    )
    args = p.parse_args()

    if args.scenario_ids.strip().lower() == "all":
        ids = sorted(ALL_SIMULATIONS.keys())
    else:
        ids = [int(x.strip()) for x in args.scenario_ids.split(",") if x.strip()]

    report = {
        "tool": "audit_mixture_simplex_corners",
        "doc": "experiments/README.md",
        "scenarios": [audit_scenario(sid) for sid in ids],
    }
    n = len(report["scenarios"])
    report["summary"] = {
        "n_scenarios": n,
        "n_with_varying_winner_at_corners": sum(
            1 for s in report["scenarios"] if s["winner_varies_across_corners"]
        ),
    }
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
