#!/usr/bin/env python3
"""
Leave-one-out posterior predictive calibration for the ethical mixture weight likelihood.

**What this does:**

For each feedback item in a JSON file, trains the sequential IS posterior on the
*remaining* N-1 items, then evaluates ``posterior_predictive_probability`` on the
held-out item.  A well-calibrated model should predict held-out choices with
probabilities consistent with their empirical frequency.

**Requires:** Feedback JSON with explicit ``hypothesis_override`` triples on all
referenced scenario candidates (same requirement as :class:`FeedbackUpdater`).

**Usage:**

    python scripts/run_likelihood_calibration.py \\
        --feedback tests/fixtures/feedback/compatible_17_18_19.json \\
        --output experiments/out/calibration_report.json \\
        --beta 10.0 \\
        --n-samples 4000

**Output (JSON):**

    {
      "n_feedback_items": N,
      "beta": 10.0,
      "mean_predictive_probability": 0.72,
      "min_predictive_probability": 0.41,
      "items": [
        {"scenario_id": 17, "preferred_action": "...", "predictive_probability": 0.78,
         "ess_train": 1240.3},
        ...
      ]
    }

See Also
--------
- :mod:`src.modules.ethical_mixture_likelihood` -- IS posterior, predictive check
- ADR 0012 -- Bayesian weight inference design
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np

from src.modules.cognition.bayesian_mixture_averaging import parse_bma_alpha_from_env
from src.modules.ethics.ethical_mixture_likelihood import (
    FeedbackObservation,
    posterior_predictive_probability,
    sequential_posterior_update,
)
from src.modules.cognition.feedback_mixture_updater import build_scenario_candidates_map


def _load_feedback_observations(path: Path) -> list[FeedbackObservation]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict) and "items" in raw:
        raw = raw["items"]
    if not isinstance(raw, list):
        raise ValueError("Feedback file must be a JSON list or {\"items\": [...]}")

    sids = sorted({int(r["scenario_id"]) for r in raw})
    cmap = build_scenario_candidates_map(sids)
    if cmap is None:
        raise ValueError(
            "All referenced scenarios must have hypothesis_override on every candidate "
            "to use explicit triples.  Use --feedback with scenarios 17-19 or similar."
        )

    obs: list[FeedbackObservation] = []
    for r in raw:
        sid = int(r["scenario_id"])
        pref = str(r["preferred_action"])
        conf = float(r.get("confidence", 1.0))
        cands = cmap[sid]
        obs.append(FeedbackObservation(
            scenario_id=sid,
            preferred_action=pref,
            candidates=cands,
            confidence=conf,
        ))
    return obs


def run_loo_calibration(
    observations: list[FeedbackObservation],
    *,
    initial_alpha: np.ndarray,
    beta: float,
    n_samples: int,
    seed: int,
) -> list[dict]:
    """
    For each index k, train on observations[0..k-1, k+1..N], then evaluate
    predictive probability on observation[k].

    Returns per-item result dicts.
    """
    rng = np.random.default_rng(seed)
    results: list[dict] = []

    for k in range(len(observations)):
        train = [o for j, o in enumerate(observations) if j != k]
        held_out = observations[k]

        if train:
            final_alpha, step_log = sequential_posterior_update(
                train,
                initial_alpha.copy(),
                beta=beta,
                n_samples=n_samples,
                rng=np.random.default_rng(seed ^ (k * 0xDEAD)),
            )
            ess_train = float(step_log[-1]["ess"]) if step_log else float("nan")
        else:
            final_alpha = initial_alpha.copy()
            ess_train = float("nan")

        pp = posterior_predictive_probability(
            held_out,
            final_alpha,
            beta=beta,
            n_samples=n_samples,
            rng=np.random.default_rng(seed ^ (k * 0xBEEF)),
        )
        results.append({
            "scenario_id": held_out.scenario_id,
            "preferred_action": held_out.preferred_action,
            "confidence": held_out.confidence,
            "predictive_probability": round(pp, 6),
            "ess_train": round(ess_train, 2) if not (ess_train != ess_train) else None,
            "posterior_alpha": [round(float(a), 4) for a in final_alpha],
        })

    return results


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1].strip())
    p.add_argument(
        "--feedback",
        type=Path,
        required=True,
        help="JSON feedback file (list of {scenario_id, preferred_action, ...}).",
    )
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write JSON report here (default: print to stdout).",
    )
    p.add_argument(
        "--beta",
        type=float,
        default=10.0,
        help="Softmax inverse temperature (default 10.0).",
    )
    p.add_argument(
        "--n-samples",
        type=int,
        default=4000,
        help="IS samples per LOO fold (default 4000).",
    )
    p.add_argument(
        "--alpha",
        type=str,
        default=None,
        metavar="A or A,B,C",
        help="Dirichlet prior alpha (overrides KERNEL_BMA_ALPHA env; default 3.0 symmetric).",
    )
    p.add_argument(
        "--seed",
        type=int,
        default=42,
    )
    args = p.parse_args()

    try:
        observations = _load_feedback_observations(args.feedback)
    except (ValueError, KeyError) as exc:
        print(f"ERROR loading feedback: {exc}", file=sys.stderr)
        return 1

    if not observations:
        print("ERROR: feedback file is empty.", file=sys.stderr)
        return 1

    # Resolve initial alpha
    if args.alpha:
        import os
        os.environ["KERNEL_BMA_ALPHA"] = args.alpha.strip()
    initial_alpha = parse_bma_alpha_from_env()

    items = run_loo_calibration(
        observations,
        initial_alpha=initial_alpha,
        beta=args.beta,
        n_samples=max(200, args.n_samples),
        seed=args.seed,
    )

    pps = [r["predictive_probability"] for r in items]
    report = {
        "feedback_path": str(args.feedback),
        "n_feedback_items": len(observations),
        "beta": args.beta,
        "n_samples": args.n_samples,
        "initial_alpha": [round(float(a), 4) for a in initial_alpha],
        "mean_predictive_probability": round(float(np.mean(pps)), 6),
        "min_predictive_probability": round(float(np.min(pps)), 6),
        "max_predictive_probability": round(float(np.max(pps)), 6),
        "items": items,
    }

    out_str = json.dumps(report, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out_str, encoding="utf-8")
        print(f"Calibration report written to {args.output}")
        print(f"  n={len(observations)}  beta={args.beta}")
        print(f"  mean_pp={report['mean_predictive_probability']:.4f}  "
              f"min_pp={report['min_predictive_probability']:.4f}")
    else:
        print(out_str)

    return 0


if __name__ == "__main__":
    sys.exit(main())
