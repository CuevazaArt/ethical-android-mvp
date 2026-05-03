"""V2.136: Deterministic ethics benchmark runner.

Loads ``evals/ethics/dilemmas_v1.json``, runs each dilemma through the
EthicalEvaluator, classifies results as PASS / SOFT_FAIL / HARD_FAIL,
and writes a timestamped report to ``evals/ethics/``.

Classification rules:
  - PASS      : chosen action is ``expected_action`` or in ``acceptable_alternatives``
  - HARD_FAIL : chosen action is in ``unacceptable_actions``
  - SOFT_FAIL : chosen action is none of the above (evaluator picked something valid
                but not the curated best answer)

The runner is deterministic: same code + same dilemma file → same results.
No random seed is needed because EthicalEvaluator is purely deterministic.

Usage::

    python scripts/eval/run_ethics_benchmark.py
    python scripts/eval/run_ethics_benchmark.py --suite v1 --out evals/ethics/
    python scripts/eval/run_ethics_benchmark.py --freeze-baseline
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.core.ethics import Action, EthicalEvaluator, Signals  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_file(path: Path) -> str:
    h = hashlib.sha256(path.read_bytes())
    return h.hexdigest()


def _git_commit_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip()
    except Exception:
        return "unavailable"


def _load_suite(suite_name: str) -> dict[str, Any]:
    path = ROOT / "evals" / "ethics" / f"dilemmas_{suite_name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Suite file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _build_actions(raw_actions: list[dict]) -> list[Action]:
    actions = []
    for r in raw_actions:
        actions.append(
            Action(
                name=r["name"],
                description=r.get("description", ""),
                impact=float(r.get("impact", 0.0)),
                confidence=float(r.get("confidence", 0.7)),
                force=float(r.get("force", 0.0)),
            )
        )
    return actions


def _build_signals(raw: dict) -> Signals:
    return Signals.from_dict(raw)


def _classify(
    chosen_name: str,
    expected_action: str,
    acceptable_alternatives: list[str],
    unacceptable_actions: list[str],
) -> str:
    if chosen_name == expected_action or chosen_name in acceptable_alternatives:
        return "PASS"
    if chosen_name in unacceptable_actions:
        return "HARD_FAIL"
    return "SOFT_FAIL"


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_benchmark(suite: dict[str, Any]) -> dict[str, Any]:
    """Run all dilemmas in the suite and return a full report dict."""

    evaluator = EthicalEvaluator()
    dilemmas = suite["dilemmas"]

    results: list[dict] = []
    per_category: dict[str, dict] = {}
    per_axis: dict[str, dict] = {}

    for d in dilemmas:
        dilemma_id = d["id"]
        category = d.get("category", "unknown")
        axis = d.get("axis_focus", "unknown")

        actions = _build_actions(d["candidate_actions"])
        signals = _build_signals(d["signals"])

        eval_result = evaluator.evaluate(actions, signals)
        chosen_name = eval_result.chosen.name

        classification = _classify(
            chosen_name=chosen_name,
            expected_action=d["expected_action"],
            acceptable_alternatives=d.get("acceptable_alternatives", []),
            unacceptable_actions=d.get("unacceptable_actions", []),
        )

        result_entry: dict[str, Any] = {
            "id": dilemma_id,
            "category": category,
            "axis_focus": axis,
            "expected_action": d["expected_action"],
            "chosen_action": chosen_name,
            "score": eval_result.score,
            "verdict": eval_result.verdict,
            "mode": eval_result.mode,
            "classification": classification,
            "pole_scores": eval_result.pole_scores,
            "reasoning": eval_result.reasoning,
        }
        results.append(result_entry)

        # Category aggregation
        if category not in per_category:
            per_category[category] = {"total": 0, "pass": 0, "soft_fail": 0, "hard_fail": 0}
        per_category[category]["total"] += 1
        if classification == "PASS":
            per_category[category]["pass"] += 1
        elif classification == "SOFT_FAIL":
            per_category[category]["soft_fail"] += 1
        else:
            per_category[category]["hard_fail"] += 1

        # Axis aggregation
        if axis not in per_axis:
            per_axis[axis] = {"total": 0, "pass": 0, "soft_fail": 0, "hard_fail": 0}
        per_axis[axis]["total"] += 1
        if classification == "PASS":
            per_axis[axis]["pass"] += 1
        elif classification == "SOFT_FAIL":
            per_axis[axis]["soft_fail"] += 1
        else:
            per_axis[axis]["hard_fail"] += 1

    n_total = len(results)
    n_pass = sum(1 for r in results if r["classification"] == "PASS")
    n_soft = sum(1 for r in results if r["classification"] == "SOFT_FAIL")
    n_hard = sum(1 for r in results if r["classification"] == "HARD_FAIL")
    accuracy = round(n_pass / n_total, 4) if n_total > 0 else 0.0

    # Compute accuracy per category and axis
    for group in (per_category, per_axis):
        for key in group:
            t = group[key]["total"]
            p = group[key]["pass"]
            group[key]["accuracy"] = round(p / t, 4) if t > 0 else 0.0

    suite_path = ROOT / "evals" / "ethics" / f"dilemmas_{suite.get('schema_version', 'v1')}.json"
    suite_file = ROOT / "evals" / "ethics" / "dilemmas_v1.json"
    dilemmas_sha256 = _sha256_file(suite_file) if suite_file.exists() else "unavailable"

    report: dict[str, Any] = {
        "schema_version": "1",
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluator_commit_sha": _git_commit_sha(),
        "suite_name": "v1",
        "dilemmas_sha256": dilemmas_sha256,
        "n_dilemmas": n_total,
        "n_correct": n_pass,
        "n_soft_fail": n_soft,
        "n_hard_fail": n_hard,
        "accuracy": accuracy,
        "per_category": per_category,
        "per_axis_breakdown": per_axis,
        "results": results,
    }
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the Ethos ethics benchmark suite."
    )
    parser.add_argument(
        "--suite", default="v1", help="Suite name (default: v1 → dilemmas_v1.json)"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=ROOT / "evals" / "ethics",
        help="Output directory for the benchmark run report.",
    )
    parser.add_argument(
        "--freeze-baseline",
        action="store_true",
        help=(
            "After running, also write the result as BASELINE_v1.json. "
            "Only do this once to set the reference baseline."
        ),
    )
    args = parser.parse_args()

    try:
        suite = _load_suite(args.suite)
    except FileNotFoundError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 2

    print(f"Running ethics benchmark suite '{args.suite}'...")
    report = run_benchmark(suite)

    # Write timestamped run file
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir: Path = args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    run_file = out_dir / f"ETHICS_BENCHMARK_RUN_{ts}.json"
    run_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Also write the canonical "latest" file for quick reference
    latest_file = out_dir / "ETHICS_BENCHMARK_RUN.json"
    latest_file.write_text(json.dumps(report, indent=2), encoding="utf-8")

    # Summary to stdout
    print(json.dumps({
        "suite": args.suite,
        "n_dilemmas": report["n_dilemmas"],
        "n_correct": report["n_correct"],
        "n_soft_fail": report["n_soft_fail"],
        "n_hard_fail": report["n_hard_fail"],
        "accuracy": report["accuracy"],
        "per_category": {k: v["accuracy"] for k, v in report["per_category"].items()},
        "per_axis": {k: v["accuracy"] for k, v in report["per_axis_breakdown"].items()},
        "run_file": str(run_file),
    }, indent=2))

    if args.freeze_baseline:
        baseline_file = out_dir / "BASELINE_v1.json"
        if baseline_file.exists():
            print(
                f"\nWARNING: {baseline_file} already exists. "
                "Remove it manually before re-freezing the baseline.",
                file=sys.stderr,
            )
            return 1
        baseline_file.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nBaseline frozen: {baseline_file}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
