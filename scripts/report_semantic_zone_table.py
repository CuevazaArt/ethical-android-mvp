#!/usr/bin/env python3
"""
Offline report: semantic MalAbs zones vs cosine ``best_sim`` (pure math).

Uses :func:`src.modules.semantic_chat_gate.classify_semantic_zone` and default θ constants.
This does **not** estimate real-world false positive/false negative rates (no labeled corpus).

Usage (repo root):
  python scripts/report_semantic_zone_table.py
  python scripts/report_semantic_zone_table.py --sweep-block 0.78 0.82 0.90
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.modules.safety.semantic_chat_gate import (  # noqa: E402
    DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
    DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
    classify_semantic_zone,
)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--sweep-block",
        type=float,
        nargs="*",
        default=None,
        metavar="THETA",
        help="Optional θ_block values to compare (default: single column with defaults).",
    )
    args = p.parse_args()

    theta_allow = DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD
    sims = [0.0, 0.20, 0.45, 0.46, 0.60, 0.81, 0.82, 0.90, 1.0]

    if args.sweep_block:
        print("# zone = classify_semantic_zone(best_sim, theta_block, theta_allow)")
        print(f"# theta_allow fixed at {theta_allow}\n")
        print("| best_sim | " + " | ".join(f"theta_block={t:.2f}" for t in args.sweep_block) + " |")
        print("|" + "---|" * (len(args.sweep_block) + 1))
        for s in sims:
            cells = [
                classify_semantic_zone(s, tb, theta_allow) for tb in args.sweep_block
            ]
            print(f"| {s:.2f} | " + " | ".join(cells) + " |")
        return

    theta_block = DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD
    print("# Default theta_block / theta_allow (engineering priors; see PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md)")
    print(f"# theta_block={theta_block}  theta_allow={theta_allow}\n")
    print("| best_sim | zone |")
    print("|---|-----|")
    for s in sims:
        z = classify_semantic_zone(s, theta_block, theta_allow)
        print(f"| {s:.2f} | {z} |")


if __name__ == "__main__":
    main()
