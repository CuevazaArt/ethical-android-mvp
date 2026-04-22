#!/usr/bin/env python3
"""
Mass static-weight sensitivity sweep — pole base weights and/or ethical mixture weights.

Centers: poles at **0.5** (in-repo default); mixture at **(1/3, 1/3, 1/3)** on the simplex.
Fluctuates symmetrically (axes / grid / random) for synthetic transparency plots — not field DAO data.

Usage:
  python scripts/run_weight_sweep_batch.py --target poles --mode axes --steps 5 --amplitude 0.35 --output artifacts/pole_sweep.json
  python scripts/run_weight_sweep_batch.py --target mixture --mode random --samples 80 --mixture-amplitude 0.12 --csv artifacts/mixture_sweep.csv
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kernel import EthicalKernel  # noqa: E402
from src.kernel_components import KernelComponentOverrides  # noqa: E402
from src.modules.ethics.ethical_poles import EthicalPoles  # noqa: E402
from src.sandbox.weight_sweep import (  # noqa: E402
    SweepMode,
    count_mixture_configs,
    count_pole_configs,
    iter_mixture_weight_configs,
    iter_pole_weight_configs,
)
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402


def _load_fixture(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _apply_mixture(kernel: EthicalKernel, w: np.ndarray) -> None:
    mw = np.asarray(w, dtype=np.float64)
    mw = mw / mw.sum()
    kernel.bayesian.hypothesis_weights = mw


def run_weight_sweep(
    fixture_path: Path,
    *,
    target: str,
    pole_mode: str,
    mixture_mode: str,
    steps: int,
    amplitude: float,
    mixture_amplitude: float,
    n_random: int,
    base_seed: int,
    max_total_runs: int,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data = _load_fixture(fixture_path)
    ref_meta = data.get("reference_standard") or {}
    rng = np.random.default_rng(base_seed)

    pole_cfgs: list[dict[str, float]] | list[None]
    mix_cfgs: list[np.ndarray] | list[None]

    if target == "poles":
        pole_cfgs = list(
            iter_pole_weight_configs(
                mode=SweepMode(pole_mode),
                amplitude=amplitude,
                steps=steps,
                n_random=n_random,
                rng=rng,
            )
        )
        mix_cfgs = [None]
    elif target == "mixture":
        pole_cfgs = [None]
        mix_cfgs = list(
            iter_mixture_weight_configs(
                mode=SweepMode(mixture_mode),
                amplitude=mixture_amplitude,
                steps=steps,
                n_random=n_random,
                rng=rng,
            )
        )
    elif target == "both":
        pole_cfgs = list(
            iter_pole_weight_configs(
                mode=SweepMode(pole_mode),
                amplitude=amplitude,
                steps=steps,
                n_random=n_random,
                rng=rng,
            )
        )
        mix_cfgs = list(
            iter_mixture_weight_configs(
                mode=SweepMode(mixture_mode),
                amplitude=mixture_amplitude,
                steps=steps,
                n_random=n_random,
                rng=rng,
            )
        )
    else:
        raise ValueError(f"Unknown --target {target}")

    batch_scenarios = [e for e in data["scenarios"] if e.get("harness", "batch") == "batch"]
    total_configs = max(1, len(pole_cfgs)) * max(1, len(mix_cfgs))
    total_runs_est = total_configs * max(1, len(batch_scenarios))
    if total_runs_est > max_total_runs:
        raise ValueError(
            f"Refusing {total_runs_est} total runs ({total_configs} weight configs × "
            f"{len(batch_scenarios)} scenarios; cap {max_total_runs}). "
            "Use smaller --steps, --samples, or --max-total-runs."
        )

    runs: list[dict[str, Any]] = []
    cfg_index = 0

    for pw in pole_cfgs:
        for mw in mix_cfgs:
            k = EthicalKernel(
                variability=False,
                seed=base_seed + cfg_index,
                llm_mode="local",
                components=(
                    KernelComponentOverrides(poles=EthicalPoles(base_weights=pw))
                    if pw is not None
                    else None
                ),
            )
            if mw is not None:
                _apply_mixture(k, mw)

            for entry in batch_scenarios:
                sid_key = entry.get("batch_id", entry.get("id"))
                if sid_key is None:
                    continue
                sid = int(sid_key)
                ref = entry.get("reference_action")
                if ref is None:
                    ref = entry.get("expected_decision")
                if sid not in ALL_SIMULATIONS:
                    continue

                scn = ALL_SIMULATIONS[sid]()
                decision = k.process(
                    scenario=f"[SIM {sid}] {scn.name}",
                    place=scn.place,
                    signals=scn.signals,
                    context=scn.context,
                    actions=scn.actions,
                )
                agree = ref is None or decision.final_action == ref
                row: dict[str, Any] = {
                    "config_index": cfg_index,
                    "scenario_id": sid,
                    "tag": entry.get("tag", ""),
                    "difficulty_tier": entry.get("difficulty_tier"),
                    "final_action": decision.final_action,
                    "decision_mode": decision.decision_mode,
                    "reference_action": ref,
                    "agree_reference": agree,
                }
                if pw is not None:
                    row["pole_compassionate"] = pw["compassionate"]
                    row["pole_conservative"] = pw["conservative"]
                    row["pole_optimistic"] = pw["optimistic"]
                if mw is not None:
                    row["mixture_util"] = float(mw[0])
                    row["mixture_deon"] = float(mw[1])
                    row["mixture_virtue"] = float(mw[2])
                runs.append(row)

            cfg_index += 1

    summary = {
        "total_runs": len(runs),
        "weight_configs": cfg_index,
        "scenarios_per_config": len(batch_scenarios),
        "target": target,
        "agreement_rate": (
            sum(1 for r in runs if r.get("reference_action") is not None and r["agree_reference"])
            / max(1, sum(1 for r in runs if r.get("reference_action") is not None))
        ),
        "unique_final_actions": len({r["final_action"] for r in runs}),
    }
    return runs, {"summary": summary, "reference_standard": ref_meta}


def main() -> int:
    p = argparse.ArgumentParser(description="Static weight sensitivity sweep (batch harness).")
    p.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json",
    )
    p.add_argument(
        "--target",
        choices=("poles", "mixture", "both"),
        default="poles",
        help="Sweep pole base weights, ethical mixture weights, or Cartesian product (large).",
    )
    p.add_argument(
        "--mode",
        default="axes",
        choices=("axes", "grid", "random"),
        help="Pole sweep geometry (also used for mixture when --target mixture/both).",
    )
    p.add_argument("--steps", type=int, default=5, help="Grid/axes resolution (>=2).")
    p.add_argument(
        "--amplitude",
        type=float,
        default=0.35,
        help="Pole sweep half-range around 0.5 per axis.",
    )
    p.add_argument(
        "--mixture-amplitude",
        type=float,
        default=0.15,
        help="Mixture sweep scale around simplex center (1/3 each).",
    )
    p.add_argument("--samples", type=int, default=40, help="Random mode: configs per target axis.")
    p.add_argument("--base-seed", type=int, default=42)
    p.add_argument(
        "--max-total-runs",
        type=int,
        default=50_000,
        help="Safety cap on weight_configs * scenarios.",
    )
    p.add_argument("--output", type=Path, default=None, help="JSON artifact (runs + meta).")
    p.add_argument(
        "--csv",
        type=Path,
        default=None,
        help="Optional flat CSV for plotting (one row per scenario × weight config).",
    )
    p.add_argument("--json", action="store_true", help="Print JSON only.")
    args = p.parse_args()

    pm = args.mode
    n_rand = args.samples if pm == "random" else 0
    # Dry-run count for pole/mixture
    pc = count_pole_configs(pm, args.steps, n_rand)
    mc = count_mixture_configs(pm, args.steps, n_rand)
    if args.target == "poles":
        est = pc
    elif args.target == "mixture":
        est = mc
    else:
        est = pc * mc
    batch_n = sum(
        1 for e in _load_fixture(args.fixture)["scenarios"] if e.get("harness", "batch") == "batch"
    )
    if est * batch_n > args.max_total_runs:
        print(
            f"Abort: estimated {est} configs × {batch_n} scenarios = {est * batch_n} runs "
            f"exceeds --max-total-runs {args.max_total_runs}",
            file=sys.stderr,
        )
        return 2

    try:
        runs, meta = run_weight_sweep(
            args.fixture,
            target=args.target,
            pole_mode=pm,
            mixture_mode=pm,
            steps=max(2, args.steps),
            amplitude=args.amplitude,
            mixture_amplitude=args.mixture_amplitude,
            n_random=max(1, args.samples),
            base_seed=args.base_seed,
            max_total_runs=args.max_total_runs,
        )
    except ValueError as e:
        print(str(e), file=sys.stderr)
        return 2

    payload = {
        "runs": runs,
        "meta": {
            "fixture": str(args.fixture.resolve()),
            "target": args.target,
            "mode": pm,
            "steps": args.steps,
            "amplitude_poles": args.amplitude,
            "amplitude_mixture": args.mixture_amplitude,
            "base_seed": args.base_seed,
            "doc": "docs/proposals/README.md",
            **meta,
        },
    }

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.csv is not None and runs:
        args.csv.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = list(runs[0].keys())
        with open(args.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            w.writeheader()
            w.writerows(runs)

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print("Weight sensitivity sweep (batch)")
    print(f"  runs={len(runs)}  agreement vs ref={meta['summary']['agreement_rate']:.2%}")
    print(f"  unique actions across grid: {meta['summary']['unique_final_actions']}")
    if args.output:
        print(f"  wrote {args.output}")
    if args.csv:
        print(f"  csv {args.csv}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
