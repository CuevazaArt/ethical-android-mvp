#!/usr/bin/env python3
"""Operator smoke: concurrent cooperative LLM cancel (ADR 0002 burst path)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.modules.llm_cancel_burst import run_burst_cancel_smoke  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser(description="Burst LLM cancel smoke (mock backend)")
    ap.add_argument("--workers", type=int, default=32, help="Concurrent cancel simulations")
    ap.add_argument("--delay", type=float, default=2.0, help="Mock completion duration (s)")
    ap.add_argument("--join-timeout", type=float, default=5.0, help="Per-inner-thread join (s)")
    args = ap.parse_args()
    try:
        run_burst_cancel_smoke(
            n_workers=args.workers,
            completion_delay_s=args.delay,
            join_timeout_s=args.join_timeout,
        )
    except (RuntimeError, ValueError, TypeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"burst_cancel_smoke ok workers={args.workers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
