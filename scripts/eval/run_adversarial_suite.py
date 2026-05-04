"""Adversarial curriculum suite runner — V2.163.

Purpose
-------
Run the full set of adversarial dilemmas (A001–A020 and beyond) from
``evals/ethics/dilemmas_v1.json`` through the :class:`EthicalEvaluator`
and measure how many produce the expected (correct-refusal) action.

**Anti-acceptance criterion (per V2.163 plan):** the suite must NOT be used
to inflate the 30/30 internal dilemma score. Adversarial dilemmas expose
fragility; the goal is to *surface* failure modes, not to pass them all.

This script is *curricular*: it is intentionally distinct from
``run_adversarial_consistency.py`` (which tests robustness under surface
variation). This script tests categorical correctness on adversarial prompts.

Outputs
-------
``evals/adversarial/BASELINE_v2.json`` — frozen on first run; subsequent runs
compare against it. Written only if the file does not exist or ``--freeze``
is passed.

Fields in the run record:
    ``n_total``, ``n_pass``, ``accuracy``, ``by_dilemma``,
    ``new_failures`` (vs. baseline), ``new_passes`` (vs. baseline),
    ``run_ts``, ``dilemmas_file``.

Usage
-----
    python scripts/eval/run_adversarial_suite.py
    python scripts/eval/run_adversarial_suite.py --subset a011-a020
    python scripts/eval/run_adversarial_suite.py --freeze
    python scripts/eval/run_adversarial_suite.py --quiet
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.core.ethics import Action, EthicalEvaluator, Signals  # noqa: E402

DILEMMAS_FILE = ROOT / "evals" / "ethics" / "dilemmas_v1.json"
BASELINE_FILE = ROOT / "evals" / "adversarial" / "BASELINE_v2.json"


def _build_signals(raw: dict) -> Signals:
    return Signals(
        risk=raw.get("risk", 0.5),
        urgency=raw.get("urgency", 0.5),
        vulnerability=raw.get("vulnerability", 0.5),
        calm=raw.get("calm", 0.5),
        legality=raw.get("legality", 0.5),
        hostility=raw.get("hostility", 0.0),
        context=raw.get("context", "unknown"),
        summary=raw.get("summary", ""),
    )


def _best_action(
    evaluator: EthicalEvaluator,
    dilemma: dict,
) -> str:
    """Run the evaluator and return the name of the chosen action."""
    signals = _build_signals(dilemma["signals"])
    actions = [
        Action(
            name=ca["name"],
            description=ca["description"],
            impact=ca["impact"],
            confidence=ca["confidence"],
            force=ca.get("force", 0.0),
        )
        for ca in dilemma["candidate_actions"]
    ]
    result = evaluator.evaluate(actions, signals)
    return result.chosen.name if result.chosen else ""


def run_suite(
    *,
    subset_filter: str | None = None,
    freeze: bool = False,
    quiet: bool = False,
) -> dict:
    """Run adversarial curriculum. Returns run record dict."""
    evaluator = EthicalEvaluator()
    raw = json.loads(DILEMMAS_FILE.read_text(encoding="utf-8"))
    all_dilemmas = [d for d in raw["dilemmas"] if d["category"] == "adversarial"]

    if subset_filter:
        lo, hi = _parse_subset(subset_filter)
        all_dilemmas = [
            d for d in all_dilemmas if lo <= int(d["id"][1:]) <= hi
        ]

    by_dilemma: dict[str, dict] = {}
    n_pass = 0

    for d in all_dilemmas:
        chosen = _best_action(evaluator, d)
        expected = d["expected_action"]
        acceptable = set(d.get("acceptable_alternatives", []))
        unacceptable = set(d.get("unacceptable_actions", []))

        passed = chosen == expected or chosen in acceptable
        is_unacceptable = chosen in unacceptable

        if passed:
            n_pass += 1

        by_dilemma[d["id"]] = {
            "chosen": chosen,
            "expected": expected,
            "acceptable_alternatives": list(acceptable),
            "unacceptable_actions": list(unacceptable),
            "passed": passed,
            "is_unacceptable": is_unacceptable,
            "adversarial_pattern": d.get("adversarial_pattern", ""),
            "expected_failure_mode": d.get("expected_failure_mode", ""),
        }

    n_total = len(all_dilemmas)
    accuracy = n_total and n_pass / n_total

    run_record: dict = {
        "schema": "adversarial_suite_v2",
        "run_ts": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dilemmas_file": str(DILEMMAS_FILE.relative_to(ROOT)),
        "subset_filter": subset_filter,
        "n_total": n_total,
        "n_pass": n_pass,
        "accuracy": accuracy,
        "by_dilemma": by_dilemma,
        "new_failures": [],
        "new_passes": [],
    }

    # Compare against baseline
    if BASELINE_FILE.exists() and not freeze:
        baseline = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        base_by = baseline.get("by_dilemma", {})
        for did, rec in by_dilemma.items():
            if did in base_by:
                was_pass = base_by[did]["passed"]
                now_pass = rec["passed"]
                if was_pass and not now_pass:
                    run_record["new_failures"].append(did)
                elif not was_pass and now_pass:
                    run_record["new_passes"].append(did)

    # Write baseline if requested or missing
    if freeze or not BASELINE_FILE.exists():
        BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE_FILE.write_text(
            json.dumps(run_record, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        if not quiet:
            print(f"[*] Baseline written to: {BASELINE_FILE.relative_to(ROOT)}")

    if not quiet:
        _print_summary(run_record)

    return run_record


def _parse_subset(s: str) -> tuple[int, int]:
    """Parse 'a011-a020' or '11-20' → (11, 20)."""
    s = s.lower().lstrip("a")
    parts = s.replace("a", "").split("-")
    if len(parts) == 2:
        return int(parts[0]), int(parts[1])
    raise argparse.ArgumentTypeError(f"Invalid subset format: {s!r}")


def _print_summary(rec: dict) -> None:
    print(f"\n=== Adversarial Curriculum Suite (V2.163) ===")
    print(f"Dilemmas : {rec['n_total']}  Pass={rec['n_pass']}  "
          f"Accuracy={rec['accuracy']:.1%}")
    if rec["subset_filter"]:
        print(f"Subset   : {rec['subset_filter']}")
    print()
    for did, r in sorted(rec["by_dilemma"].items()):
        status = "PASS" if r["passed"] else ("FAIL(unacceptable)" if r["is_unacceptable"] else "FAIL")
        print(f"  {did}  {status:24s}  chosen={r['chosen']}  expected={r['expected']}")
        if r["adversarial_pattern"]:
            print(f"         pattern: {r['adversarial_pattern']}")
        if not r["passed"] and r["expected_failure_mode"]:
            print(f"         failure_mode: {r['expected_failure_mode'][:80]}")
    if rec["new_failures"]:
        print(f"\nNEW REGRESSIONS vs baseline: {rec['new_failures']}")
    if rec["new_passes"]:
        print(f"NEW PASSES vs baseline     : {rec['new_passes']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run adversarial curriculum suite and compare against baseline."
    )
    parser.add_argument("--subset", default=None, help="e.g. 'a011-a020'")
    parser.add_argument(
        "--freeze",
        action="store_true",
        help="Overwrite the baseline with the current run.",
    )
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    rec = run_suite(subset_filter=args.subset, freeze=args.freeze, quiet=args.quiet)
    if rec["new_failures"]:
        print(
            f"ERROR: {len(rec['new_failures'])} regression(s) vs baseline: "
            f"{rec['new_failures']}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
