#!/usr/bin/env python3
"""
Benchmark kernel chat-style turns for timing regression / A-B comparisons.

Example::

    python scripts/eval/benchmark_turns.py --turns 50
    python scripts/eval/benchmark_turns.py --turns 20 --seed 42 --label baseline
"""

from __future__ import annotations

import argparse
import os
import statistics
import sys
import time
from pathlib import Path

# Repo root on sys.path
_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--turns", type=int, default=30)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--label", type=str, default="run")
    args = ap.parse_args()

    os.environ.setdefault("KERNEL_SEMANTIC_CHAT_GATE", "0")

    from src.kernel import EthicalKernel

    k = EthicalKernel(variability=False)
    times: list[float] = []
    base = f"bench turn {{i}} seed={args.seed}"
    for i in range(args.turns):
        t0 = time.perf_counter()
        k.process_chat_turn(base.format(i=i), agent_id="bench", place="eval")
        times.append(time.perf_counter() - t0)

    print(
        json_line(
            {
                "label": args.label,
                "turns": args.turns,
                "mean_ms": round(statistics.mean(times) * 1000, 3),
                "stdev_ms": round(statistics.stdev(times) * 1000, 3) if len(times) > 1 else 0.0,
                "p95_ms": round(_pctl(times, 0.95) * 1000, 3),
            }
        )
    )


def json_line(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False)


def _pctl(xs: list[float], p: float) -> float:
    ys = sorted(xs)
    if not ys:
        return 0.0
    k = min(len(ys) - 1, max(0, int(round(p * (len(ys) - 1)))))
    return ys[k]


if __name__ == "__main__":
    main()
