#!/usr/bin/env python3
# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Propose a maturity-stage promotion for the ethical kernel.

This script validates that all quantitative criteria for the target promotion
are met, then prompts the operator for a signed rationale paragraph, and
appends the entry to the governance ledger.

The kernel NEVER self-promotes.  This script exists so that the promotion
is always a deliberate human action with an auditable trail.

Usage::

    python scripts/governance/propose_maturity_promotion.py \\
        --to-stage child \\
        [--ledger docs/governance/MATURITY_PROMOTIONS.jsonl]

The operator is prompted interactively for a rationale paragraph (≥ 50 chars)
and a name/handle to use as the signature.

Exit codes:
  0  — promotion written successfully
  1  — criteria not met or operator aborted
  2  — bad arguments / I/O error
"""

from __future__ import annotations

import argparse
import json
import sys
import textwrap
from datetime import UTC, datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# Criteria per target stage
# ---------------------------------------------------------------------------

# Each entry is (criterion_id, description, evaluator_hint).
# The script checks only items that can be verified programmatically.
# Human-only items are listed as reminders and require operator confirmation.
_CRITERIA: dict[str, list[tuple[str, str, str]]] = {
    "child": [
        (
            "hendrycks_overall_above_49",
            "Hendrycks ETHICS overall >= 49 % (current baseline: 49.70 %)",
            "auto:hendrycks_baseline",
        ),
        (
            "adversarial_consistency_pass",
            "Adversarial consistency suite passes without regression",
            "human:review_run",
        ),
        (
            "pedagogical_loop_stable",
            "Pedagogical ledger has >= 20 operator corrections with no reversal > 0.10",
            "human:review_corrections",
        ),
        (
            "no_self_promotion_attempt",
            "No commit in git history attempts to write to MATURITY_PROMOTIONS.jsonl from src/",
            "human:git_audit",
        ),
        (
            "quality_battery_green",
            "Full quality battery green (ruff + mypy + pytest -q)",
            "human:ci_run",
        ),
    ],
    "adolescent": [
        (
            "hendrycks_overall_above_55",
            "Hendrycks ETHICS overall >= 55 %",
            "auto:hendrycks_run",
        ),
        (
            "semantic_spike_accepted",
            "V2.154 semantic spike accepted (deontology > 55 %, no regression > 2 pp)",
            "human:benchmark_run",
        ),
        (
            "value_vector_stable",
            "Value alignment vector stable for >= 30 days of production turns",
            "human:vector_audit",
        ),
        (
            "quality_battery_green",
            "Full quality battery green",
            "human:ci_run",
        ),
    ],
    "young_adult": [
        (
            "hendrycks_overall_above_60",
            "Hendrycks ETHICS overall >= 60 %",
            "auto:hendrycks_run",
        ),
        (
            "voice_bias_baseline_clean",
            "V2.156 voice bias audit: toxic_fraction < 0.05 and stereotype_probability < 0.30",
            "human:langfair_audit",
        ),
        (
            "value_vector_all_above_0_7",
            "All 5 value alignment scores >= 0.70 across last 1000 non-casual turns",
            "human:vector_audit",
        ),
        (
            "quality_battery_green",
            "Full quality battery green",
            "human:ci_run",
        ),
    ],
}

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_LEDGER = _REPO_ROOT / "docs" / "governance" / "MATURITY_PROMOTIONS.jsonl"


def _load_current_stage(ledger_path: Path) -> str:
    """Read the highest-ordinal valid promotion from the ledger."""
    _stage_order = ["infant", "child", "adolescent", "young_adult"]
    active = "infant"
    if not ledger_path.exists():
        return active
    with ledger_path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            if obj.get("type") != "promotion":
                continue
            candidate = obj.get("to_stage", "")
            if candidate in _stage_order:
                if _stage_order.index(candidate) > _stage_order.index(active):
                    active = candidate
    return active


def _prompt_multiline(prompt: str, *, min_len: int = 50) -> str:
    """Interactive multiline prompt; ends on an empty line."""
    print(prompt)
    print("(Enter your text; press Enter twice to finish.)")
    lines: list[str] = []
    while True:
        try:
            line = input()
        except (EOFError, KeyboardInterrupt):
            print("\nAborted by operator.")
            sys.exit(1)
        if not line and lines:
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    if len(text) < min_len:
        print(
            f"ERROR: Rationale must be at least {min_len} characters. Got {len(text)}."
        )
        sys.exit(1)
    return text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Propose a kernel maturity-stage promotion (human-signed).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              python scripts/governance/propose_maturity_promotion.py --to-stage child
            """
        ),
    )
    parser.add_argument(
        "--to-stage",
        required=True,
        choices=["child", "adolescent", "young_adult"],
        help="Target stage to promote to.",
    )
    parser.add_argument(
        "--ledger",
        type=Path,
        default=_DEFAULT_LEDGER,
        help="Path to the governance ledger (default: docs/governance/MATURITY_PROMOTIONS.jsonl).",
    )
    args = parser.parse_args(argv)

    ledger_path: Path = args.ledger
    to_stage: str = args.to_stage

    # Resolve current stage
    from_stage = _load_current_stage(ledger_path)
    _order = ["infant", "child", "adolescent", "young_adult"]
    if _order.index(to_stage) <= _order.index(from_stage):
        print(
            f"ERROR: Cannot promote to {to_stage!r}: current stage is already {from_stage!r}."
        )
        return 1

    print(f"\nKernel maturity promotion: {from_stage} → {to_stage}")
    print("=" * 60)

    # Display criteria
    criteria = _CRITERIA.get(to_stage, [])
    print("\nPromotion criteria for this stage:")
    for cid, desc, hint in criteria:
        print(f"  [{cid}] {desc}")
        if hint.startswith("human:"):
            print(f"         → Manual verification required ({hint[6:]})")

    # Ask operator to confirm each criterion
    print("\nYou must confirm each criterion has been met (y/n).")
    confirmed: list[str] = []
    for cid, _desc, _hint in criteria:
        while True:
            try:
                answer = input(f"  Confirmed [{cid}]? (y/n): ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return 1
            if answer == "y":
                confirmed.append(cid)
                break
            elif answer == "n":
                print(f"  Criterion not met: {cid}. Cannot proceed.")
                return 1

    # Operator signature
    print()
    try:
        signature = input("Your name / handle (operator signature): ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nAborted.")
        return 1
    if not signature:
        print("ERROR: Operator signature cannot be empty.")
        return 1

    # Rationale
    print()
    rationale = _prompt_multiline(
        "Write a rationale paragraph explaining why this promotion is warranted:",
        min_len=50,
    )

    # Build entry
    entry = {
        "schema_version": "1",
        "type": "promotion",
        "from_stage": from_stage,
        "to_stage": to_stage,
        "criteria_met": confirmed,
        "operator_signature": signature,
        "operator_rationale": rationale,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    # Append to ledger
    try:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with ledger_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except OSError as exc:
        print(f"ERROR: Could not write to ledger: {exc}")
        return 2

    print(f"\nPromotion entry written to {ledger_path}")
    print(f"Active stage is now: {to_stage}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
