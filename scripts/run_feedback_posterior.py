#!/usr/bin/env python3
"""
Apply ADR 0012 operator feedback JSON and print posterior Dirichlet α (JSON).

Uses :func:`src.modules.feedback_mixture_posterior.load_and_apply_feedback` with the
same ``KERNEL_*`` env vars as :class:`src.kernel.EthicalKernel`.

If ``--feedback`` is omitted and ``KERNEL_FEEDBACK_PATH`` is unset, defaults to the
versioned compatible sample for scenarios 17–19:

``tests/fixtures/feedback/compatible_17_18_19.json``

Example::

    python scripts/run_feedback_posterior.py
    python scripts/run_feedback_posterior.py --feedback path/to/feedback.json -o out/posterior.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

DEFAULT_FIXTURE = ROOT / "tests" / "fixtures" / "feedback" / "compatible_17_18_19.json"


def _json_safe(obj: Any) -> Any:
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, (np.floating, np.integer)):
        return float(obj) if isinstance(obj, np.floating) else int(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def main() -> int:
    p = argparse.ArgumentParser(description="ADR 0012: apply feedback JSON → posterior α.")
    p.add_argument(
        "--feedback",
        type=Path,
        default=None,
        help=f"Feedback JSON (default: {DEFAULT_FIXTURE.name} or KERNEL_FEEDBACK_PATH).",
    )
    p.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write JSON to this path (default: stdout).",
    )
    p.add_argument(
        "--pretty",
        action="store_true",
        help="Indent JSON for readability.",
    )
    args = p.parse_args()

    fb_path = args.feedback
    if fb_path is None:
        env = os.environ.get("KERNEL_FEEDBACK_PATH", "").strip()
        fb_path = Path(env) if env else DEFAULT_FIXTURE
    fb_path = fb_path.resolve()
    if not fb_path.is_file():
        print(f"error: feedback file not found: {fb_path}", file=sys.stderr)
        return 2

    from src.modules.cognition.feedback_mixture_posterior import load_and_apply_feedback

    seed = int(os.environ.get("KERNEL_FEEDBACK_SEED", "42"))
    rng = np.random.default_rng(seed)
    alpha, consistency, meta = load_and_apply_feedback(fb_path, rng=rng)
    mean = alpha / np.sum(alpha)

    out: dict[str, Any] = {
        "feedback_path": str(fb_path),
        "posterior_alpha": [float(x) for x in alpha],
        "posterior_mean_weights": [float(x) for x in mean],
        "feedback_consistency": consistency,
        "meta": _json_safe(meta),
    }

    indent = 2 if args.pretty else None
    text = json.dumps(out, indent=indent) + "\n"
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
