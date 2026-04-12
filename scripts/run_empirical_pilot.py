#!/usr/bin/env python3
"""
Empirical pilot runner (Issue 3) — batch simulations vs simple baselines + optional reference labels.

Usage (repo root):
  python scripts/run_empirical_pilot.py
  python scripts/run_empirical_pilot.py --json
  python scripts/run_empirical_pilot.py --fixture tests/fixtures/labeled_scenarios.json --json
  python scripts/run_empirical_pilot.py --output runs/pilot_last.json

Batch rows only: scenarios with ``harness: batch`` (default if omitted). Skips ``annotation_only``.
Labels: ``reference_action`` or ``expected_decision``; ``batch_id`` or ``id`` for simulation id.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.kernel import EthicalKernel  # noqa: E402
from src.simulations.runner import ALL_SIMULATIONS  # noqa: E402


def _baseline_first(actions):
    return actions[0].name


def _baseline_max_impact(actions):
    best = max(actions, key=lambda a: a.estimated_impact)
    return best.name


def _load_fixture(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def run_pilot(fixture_path: Path) -> tuple[list[dict[str, Any]], dict[str, float]]:
    data = _load_fixture(fixture_path)
    rows: list[dict[str, Any]] = []
    kernel = EthicalKernel(variability=False, seed=42, llm_mode="local")

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

        scn = ALL_SIMULATIONS[sid]()
        decision = kernel.process(
            scenario=f"[SIM {sid}] {scn.name}",
            place=scn.place,
            signals=scn.signals,
            context=scn.context,
            actions=scn.actions,
        )
        k_act = decision.final_action
        b_first = _baseline_first(scn.actions)
        b_max = _baseline_max_impact(scn.actions)

        rows.append(
            {
                "id": sid,
                "uid": entry.get("uid"),
                "tag": entry.get("tag", ""),
                "kernel": k_act,
                "baseline_first": b_first,
                "baseline_max_impact": b_max,
                "reference_action": ref,
                "agree_kernel": ref is None or k_act == ref,
                "agree_first": ref is None or b_first == ref,
                "agree_max_impact": ref is None or b_max == ref,
            }
        )

    with_ref = [r for r in rows if r["reference_action"] is not None]
    n = len(with_ref)
    nrows = len(rows)
    summary = {
        "scenarios": nrows,
        "with_reference": n,
        "agreement_kernel": sum(1 for r in with_ref if r["agree_kernel"]) / n if n else 0.0,
        "agreement_first": sum(1 for r in with_ref if r["agree_first"]) / n if n else 0.0,
        "agreement_max_impact": sum(1 for r in with_ref if r["agree_max_impact"]) / n if n else 0.0,
        "kernel_vs_first_rate": (
            sum(1 for r in rows if r["kernel"] == r["baseline_first"]) / nrows if nrows else 0.0
        ),
        "kernel_vs_max_impact_rate": (
            sum(1 for r in rows if r["kernel"] == r["baseline_max_impact"]) / nrows
            if nrows
            else 0.0
        ),
    }
    return rows, summary


def main() -> int:
    p = argparse.ArgumentParser(
        description="Empirical pilot: kernel vs baselines on batch scenarios."
    )
    p.add_argument(
        "--fixture",
        type=Path,
        default=ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json",
        help="Path to scenarios.json",
    )
    p.add_argument("--json", action="store_true", help="Emit JSON only (no table).")
    p.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write rows + summary + run metadata to this JSON file (UTF-8).",
    )
    args = p.parse_args()

    rows, summary = run_pilot(args.fixture)

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "rows": rows,
            "summary": summary,
            "meta": {
                "fixture": str(args.fixture.resolve()),
                "kernel": {"variability": False, "seed": 42, "llm_mode": "local"},
            },
        }
        args.output.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps({"rows": rows, "summary": summary}, indent=2))
        return 0

    print("Empirical pilot (batch) — Issue 3")
    print(f"Fixture: {args.fixture}")
    print(
        f"Scenarios: {summary['scenarios']}  |  With reference label: {summary['with_reference']}"
    )
    print()
    for r in rows:
        ref = r["reference_action"] or "—"
        print(f"  sim {r['id']:d} [{r['tag']}]: kernel={r['kernel']}")
        print(f"    first={r['baseline_first']}  max_impact={r['baseline_max_impact']}  ref={ref}")
    print()
    print(
        "Agreement vs reference (illustrative labels): "
        f"kernel={summary['agreement_kernel']:.2%}  "
        f"first={summary['agreement_first']:.2%}  "
        f"max_impact={summary['agreement_max_impact']:.2%}"
    )
    print(
        "Kernel vs baselines (order / greedy impact): "
        f"kernel==first {summary['kernel_vs_first_rate']:.2%}  "
        f"kernel==max_impact {summary['kernel_vs_max_impact_rate']:.2%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
