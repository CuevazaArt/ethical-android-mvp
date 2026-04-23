#!/usr/bin/env python3
"""
Operator smoke: concurrent cooperative LLM cancel (ADR 0002 burst path).

**EXPERIMENTAL / MOCK** — same invariants as :func:`src.modules.llm_cancel_burst.run_burst_cancel_smoke`;
this script adds argparse-time checks so bad ``NaN``/``Inf`` strings fail before any worker runs.
"""

from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.modules.llm_cancel_burst import (  # noqa: E402
    MAX_BURST_SMOKE_WORKERS,
    run_burst_cancel_smoke,
)


def _parse_smoke_workers(s: str) -> int:
    try:
        n = int(s, 10)
    except (TypeError, ValueError) as e:
        raise argparse.ArgumentTypeError(f"workers: invalid integer: {s!r}") from e
    if n < 1 or n > MAX_BURST_SMOKE_WORKERS:
        raise argparse.ArgumentTypeError(
            f"workers: must be in [1, {MAX_BURST_SMOKE_WORKERS}], got {n}"
        )
    return n


def _parse_positive_finite(label: str):
    def _inner(raw: str) -> float:
        try:
            v = float(raw)
        except (TypeError, ValueError) as e:
            raise argparse.ArgumentTypeError(f"{label}: not a number: {raw!r}") from e
        if not math.isfinite(v) or v <= 0.0:
            raise argparse.ArgumentTypeError(
                f"{label}: must be positive and finite, got {raw!r}"
            )
        return v

    return _inner


def _parse_nonneg_finite(label: str):
    def _inner(raw: str) -> float:
        try:
            v = float(raw)
        except (TypeError, ValueError) as e:
            raise argparse.ArgumentTypeError(f"{label}: not a number: {raw!r}") from e
        if not math.isfinite(v) or v < 0.0:
            raise argparse.ArgumentTypeError(
                f"{label}: must be finite and non-negative, got {raw!r}"
            )
        return v

    return _inner


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Burst LLM cancel smoke (MOCK backend; see llm_cancel_burst).",
    )
    ap.add_argument(
        "--workers",
        type=_parse_smoke_workers,
        default=32,
        metavar="N",
        help="Concurrent cancel simulations (1..MAX_BURST_SMOKE_WORKERS)",
    )
    ap.add_argument(
        "--delay",
        type=_parse_positive_finite("delay"),
        default=2.0,
        metavar="SEC",
        help="Mock completion duration (s), finite and > 0",
    )
    ap.add_argument(
        "--join-timeout",
        type=_parse_positive_finite("join-timeout"),
        default=5.0,
        metavar="SEC",
        help="Per-inner-thread join (s), finite and > 0",
    )
    ap.add_argument(
        "--cancel-after",
        type=_parse_nonneg_finite("cancel-after"),
        default=0.02,
        metavar="SEC",
        help="Delay before set cancel event (s), finite and >= 0",
    )
    args = ap.parse_args()
    try:
        run_burst_cancel_smoke(
            n_workers=args.workers,
            completion_delay_s=args.delay,
            join_timeout_s=args.join_timeout,
            cancel_after_s=args.cancel_after,
        )
    except (RuntimeError, ValueError, TypeError) as exc:
        print(exc, file=sys.stderr)
        return 1
    print(f"burst_cancel_smoke ok workers={args.workers}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
