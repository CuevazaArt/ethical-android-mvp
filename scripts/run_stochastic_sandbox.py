#!/usr/bin/env python3
"""
Monte Carlo stochastic sandbox — batch scenarios under artificial noise + optional kernel variability.

Exercises **chance / stress** dimensions: perturbed sensory signals (see ``src/sandbox/synthetic_stochastic.py``)
and independent ``EthicalKernel`` seeds per roll so scoring noise can diverge non-linearly from deterministic pilot.

Usage (repo root):
  python scripts/run_stochastic_sandbox.py --rolls 25 --stress 0.4 --output artifacts/stochastic_sandbox.json
  python scripts/run_stochastic_sandbox.py --rolls 10 --stress 0 --no-kernel-variability  # signal noise only off at stress=0

Does **not** replace ``run_empirical_pilot.py`` (deterministic regression). Archive JSON for analysis / discussion.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kernel import EthicalKernel  # noqa: E402
from src.sandbox.synthetic_stochastic import (  # noqa: E402
    SyntheticStochasticConfig,
    perturb_scenario_signals,
    trial_seed,
)
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402


def _load_fixture(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_stochastic_sandbox(
    fixture_path: Path,
    *,
    rolls: int,
    stress: float,
    base_seed: int,
    kernel_variability: bool,
    signal_perturbation: bool,
    stochastic_config: SyntheticStochasticConfig | None = None,
) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any]]:
    data = _load_fixture(fixture_path)
    ref_meta = data.get("reference_standard") or {}
    st_cfg = stochastic_config or SyntheticStochasticConfig()

    trial_rows: list[dict[str, Any]] = []

    for entry in data["scenarios"]:
        if entry.get("harness", "batch") != "batch":
            continue
        sid_key = entry.get("batch_id", entry.get("id"))
        if sid_key is None:
            raise ValueError(f"Batch scenario missing batch_id/id: {entry!r}")
        sid = int(sid_key)
        ref = entry.get("reference_action")
        if ref is None:
            ref = entry.get("expected_decision")
        if sid not in ALL_SIMULATIONS:
            raise ValueError(
                f"Unknown simulation id {sid}; expected one of {sorted(ALL_SIMULATIONS)}"
            )
        tier = entry.get("difficulty_tier")
        tag = entry.get("tag", "")

        for roll in range(rolls):
            ts = trial_seed(base_seed, sid, roll)
            rng = np.random.default_rng(ts & 0xFFFFFFFFFFFFFFFF)

            scn = ALL_SIMULATIONS[sid]()
            sig = scn.signals
            trace: dict[str, Any] | None = None
            if signal_perturbation and stress > 0:
                sig, trace = perturb_scenario_signals(sig, rng, stress=stress, config=st_cfg)
            else:
                sig = dict(sig)

            # Fresh kernel per roll so variability RNG is independent across trials.
            kernel = EthicalKernel(
                variability=kernel_variability,
                seed=ts,
                llm_mode="local",
            )
            decision = kernel.process(
                scenario=f"[SIM {sid}] {scn.name}",
                place=scn.place,
                signals=sig,
                context=scn.context,
                actions=scn.actions,
            )
            k_act = decision.final_action
            d_mode = decision.decision_mode
            agree = ref is None or k_act == ref

            trial_rows.append(
                {
                    "id": sid,
                    "uid": entry.get("uid"),
                    "tag": tag,
                    "difficulty_tier": tier,
                    "roll": roll,
                    "trial_seed": ts,
                    "kernel": k_act,
                    "decision_mode": d_mode,
                    "reference_action": ref,
                    "agree_kernel": agree,
                    "perturbation": trace,
                }
            )

    # Build per-scenario aggregates from trial_rows
    by_scenario: dict[int, dict[str, Any]] = {}
    for row in trial_rows:
        sid = int(row["id"])
        if sid not in by_scenario:
            by_scenario[sid] = {
                "id": sid,
                "tag": row.get("tag", ""),
                "difficulty_tier": row.get("difficulty_tier"),
                "reference_action": row.get("reference_action"),
                "rolls": rolls,
                "action_histogram": Counter(),
                "mode_histogram": Counter(),
                "agreement_rate": 0.0,
            }
        by_scenario[sid]["action_histogram"][row["kernel"]] += 1
        by_scenario[sid]["mode_histogram"][row["decision_mode"]] += 1

    for sid, block in by_scenario.items():
        ref = block.get("reference_action")
        subset = [r for r in trial_rows if int(r["id"]) == sid]
        if ref is not None:
            block["agreement_rate"] = sum(1 for r in subset if r["agree_kernel"]) / len(subset)
        else:
            block["agreement_rate"] = None
        # diversity: unique actions / rolls
        nuniq = len({r["kernel"] for r in subset})
        block["action_entropy_proxy"] = nuniq / rolls if rolls else 0.0
        block["action_histogram"] = dict(block["action_histogram"])
        block["mode_histogram"] = dict(block["mode_histogram"])

    summary = {
        "rolls_per_scenario": rolls,
        "stress": stress,
        "signal_perturbation": signal_perturbation,
        "kernel_variability": kernel_variability,
        "base_seed": base_seed,
        "scenarios": len(by_scenario),
        "trial_total": len(trial_rows),
        "mean_agreement_vs_reference": (
            sum(
                1 for r in trial_rows if r.get("reference_action") is not None and r["agree_kernel"]
            )
            / max(
                1,
                sum(1 for r in trial_rows if r.get("reference_action") is not None),
            )
        ),
        "by_scenario": [by_scenario[k] for k in sorted(by_scenario.keys())],
    }

    return trial_rows, summary, ref_meta


def main() -> int:
    p = argparse.ArgumentParser(
        description="Stochastic Monte Carlo sandbox over batch scenarios (research; not CI regression)."
    )
    p.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json",
        help="Batch fixture (same as empirical pilot).",
    )
    p.add_argument("--rolls", type=int, default=20, help="Monte Carlo rolls per scenario.")
    p.add_argument(
        "--stress",
        type=float,
        default=0.35,
        help="Stress in [0,1]: scales signal noise + aleatory spikes.",
    )
    p.add_argument(
        "--base-seed", type=int, default=42, help="Base seed for reproducible trial seeds."
    )
    p.add_argument(
        "--no-kernel-variability",
        action="store_true",
        help="Disable EthicalKernel VariabilityEngine (signal perturbation only).",
    )
    p.add_argument(
        "--no-signal-perturbation",
        action="store_true",
        help="Disable synthetic signal noise (kernel variability + seed diversity only).",
    )
    p.add_argument("--json", action="store_true", help="Print JSON only.")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write full artifact (trials + summary + meta).",
    )
    args = p.parse_args()

    trials, summary, ref_meta = run_stochastic_sandbox(
        args.fixture,
        rolls=max(1, args.rolls),
        stress=max(0.0, min(1.0, args.stress)),
        base_seed=args.base_seed,
        kernel_variability=not args.no_kernel_variability,
        signal_perturbation=not args.no_signal_perturbation,
    )

    meta = {
        "fixture": str(args.fixture.resolve()),
        "kernel_defaults": {
            "llm_mode": "local",
            "kernel_variability": not args.no_kernel_variability,
            "signal_perturbation": not args.no_signal_perturbation,
            "stress": summary["stress"],
        },
        "reference_standard": ref_meta,
        "doc": "docs/proposals/PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md",
    }

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {"trials": trials, "summary": summary, "meta": meta}
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({"trials": trials, "summary": summary, "meta": meta}, indent=2))
        return 0

    print("Stochastic sandbox (Monte Carlo) — research artifact")
    print(f"Fixture: {args.fixture}")
    print(
        f"rolls={summary['rolls_per_scenario']}  stress={summary['stress']:.2f}  "
        f"kernel_variability={summary['kernel_variability']}  "
        f"signal_perturbation={summary['signal_perturbation']}"
    )
    print(f"Mean agreement vs reference: {summary['mean_agreement_vs_reference']:.2%}")
    print()
    for block in summary["by_scenario"]:
        print(f"  sim {block['id']} [{block.get('tag')}]  agree={block.get('agreement_rate')}")
        print(
            f"    actions: {block['action_histogram']}  diversity~={block['action_entropy_proxy']:.2f}"
        )
        print(f"    modes: {block['mode_histogram']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
