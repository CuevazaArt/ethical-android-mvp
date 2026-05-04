"""Diagnostic analysis of the Hendrycks ETHICS external benchmark failures.

Reads the frozen baseline (``evals/ethics/EXTERNAL_BASELINE_v1.json``) and
prints a per-subset breakdown:

* Confusion matrix (chosen × expected counts)
* Directional-bias check (does the evaluator consistently prefer one action?)
* Pole-score distribution for PASS vs FAIL rows (from worst-failures sample)

The script is **read-only** — it never modifies the baseline or the evaluator.
Its purpose is to diagnose *why* any subset sits near chance and to inform
whether a minimal mechanical fix (like the virtue hash-ordering fix) exists.

Usage::

    python scripts/eval/analyze_external_failures.py
    python scripts/eval/analyze_external_failures.py --subset deontology
    python scripts/eval/analyze_external_failures.py --baseline evals/ethics/EXTERNAL_BASELINE_v1.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASELINE = ROOT / "evals" / "ethics" / "EXTERNAL_BASELINE_v1.json"


def _load_baseline(path: Path) -> dict:
    if not path.is_file():
        print(f"ERROR: baseline not found at {path}", file=sys.stderr)
        sys.exit(1)
    return json.loads(path.read_text(encoding="utf-8"))


def _analyze_subset(subset: str, sub: dict) -> None:
    print(f"\n{'=' * 60}")
    print(f"Subset: {subset.upper()}")
    print(f"{'=' * 60}")

    n = sub.get("n_examples", 0)
    n_pass = sub.get("n_pass", 0)
    n_fail = sub.get("n_fail", 0)
    acc = sub.get("accuracy", 0.0)

    print(f"  Total examples : {n}")
    print(f"  PASS           : {n_pass}  ({100 * n_pass / max(n, 1):.2f} %)")
    print(f"  FAIL           : {n_fail}  ({100 * n_fail / max(n, 1):.2f} %)")
    print(f"  Accuracy       : {acc:.4f}  ({100 * acc:.2f} %)")

    worst = sub.get("worst_failures", [])
    if not worst:
        print("  (no worst_failures recorded in baseline)")
        return

    # Confusion counts from the worst-failures sample.
    chosen_counts: dict[str, int] = {}
    expected_counts: dict[str, int] = {}
    confusion: dict[tuple[str, str], int] = {}
    for row in worst:
        c = row.get("chosen", "?")
        e = row.get("expected", "?")
        chosen_counts[c] = chosen_counts.get(c, 0) + 1
        expected_counts[e] = expected_counts.get(e, 0) + 1
        confusion[(c, e)] = confusion.get((c, e), 0) + 1

    print(f"\n  --- Worst-failures sample (n={len(worst)}) ---")
    print("  Chosen distribution:")
    for action, cnt in sorted(chosen_counts.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / len(worst)
        print(f"    {action:<30s} {cnt:3d}  ({pct:.1f} %)")

    print("  Expected distribution:")
    for action, cnt in sorted(expected_counts.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / len(worst)
        print(f"    {action:<30s} {cnt:3d}  ({pct:.1f} %)")

    print("  Confusion (chosen → expected) in sample:")
    for (c, e), cnt in sorted(confusion.items(), key=lambda x: -x[1]):
        pct = 100 * cnt / len(worst)
        status = "CORRECT" if c == e else "wrong"
        print(
            f"    chosen={c:<25s}  expected={e:<25s}  n={cnt:3d}  ({pct:.1f} %)  [{status}]"
        )

    # Pole-score averages for failures.
    pole_sums: dict[str, float] = {}
    pole_n = 0
    for row in worst:
        ps = row.get("pole_scores", {})
        for k, v in ps.items():
            pole_sums[k] = pole_sums.get(k, 0.0) + float(v)
        if ps:
            pole_n += 1
    if pole_n:
        print(f"  Average pole scores on failures (n={pole_n}):")
        for k in sorted(pole_sums):
            print(f"    {k:<10s} {pole_sums[k] / pole_n:.4f}")

    # Directional-bias hypothesis.
    _directional_bias_hypothesis(subset, chosen_counts, worst)

    # Top-20 worst failures.
    print(
        f"\n  Top-{min(20, len(worst))} worst failures (most confident wrong answers):"
    )
    for i, row in enumerate(worst[:20]):
        scenario = row.get("scenario", "")[:120]
        expected = row.get("expected", "?")
        chosen = row.get("chosen", "?")
        score = row.get("score", 0.0)
        ps = row.get("pole_scores", {})
        ps_str = "  ".join(f"{k}={v:.3f}" for k, v in ps.items())
        print(
            f"  [{i + 1:2d}] expected={expected:<25s}  chosen={chosen:<25s}  score={score:.4f}"
        )
        print(f"       poles: {ps_str}")
        print(f"       scenario: {scenario!r}")


def _directional_bias_hypothesis(subset: str, chosen_counts: dict, worst: list) -> None:
    """Print a diagnostic hypothesis about directional bias."""
    print("\n  --- Directional bias diagnosis ---")

    if not chosen_counts:
        print("  (insufficient data)")
        return

    total = sum(chosen_counts.values())
    dominant = max(chosen_counts, key=lambda k: chosen_counts[k])
    dominant_pct = 100 * chosen_counts[dominant] / total

    if dominant_pct >= 80:
        print(
            f"  STRONG DIRECTIONAL BIAS: '{dominant}' chosen in "
            f"{dominant_pct:.1f} % of worst failures."
        )
    elif dominant_pct >= 60:
        print(
            f"  MODERATE DIRECTIONAL BIAS: '{dominant}' chosen in "
            f"{dominant_pct:.1f} % of worst failures."
        )
    else:
        print(
            f"  NO STRONG DIRECTIONAL BIAS: most-chosen action "
            f"'{dominant}' at only {dominant_pct:.1f} %."
        )

    # Subset-specific notes based on the case-builder design.
    notes = {
        "commonsense": (
            "  DESIGN NOTE: _build_case_commonsense sets refrain.confidence=0.9 "
            "vs do_action.confidence=0.7.\n"
            "  When impact_est=0 (no harm/help keywords), refrain wins via the "
            "virtue formula\n"
            "  (0.22*(c-0.5)) and the confidence multiplier on the final score.\n"
            "  Since most AITA scenarios are label=1 (refrain expected), this "
            "bias is NET POSITIVE\n"
            "  for commonsense accuracy. Removing it would push accuracy toward "
            "50 %, not above 60 %."
        ),
        "justice": (
            "  DESIGN NOTE: _build_case_justice sets both actions to confidence=0.7 "
            "with symmetric impact.\n"
            "  There is NO confidence asymmetry. Accuracy near 50 % is structural: "
            "the evaluator\n"
            "  has no representation of 'desert claims' (whether a reciprocal-"
            "fairness action is\n"
            "  justified). The keyword lexicons cannot distinguish 'I stopped "
            "giving because she\n"
            "  did X' as justified vs unjustified."
        ),
        "deontology": (
            "  DESIGN NOTE: _build_case_deontology sets reject_excuse.confidence=0.8 "
            "vs accept_excuse.confidence=0.7.\n"
            "  When impact_est=0 (excuse has no harm/help keywords), reject wins "
            "via virtue score\n"
            "  and confidence multiplier. The bias is NET POSITIVE for the current "
            "deontology accuracy\n"
            "  (51.03 % > 50 %): there are slightly more neutral-text label=0 "
            "(reject-expected) rows\n"
            "  than neutral-text label=1 (accept-expected) rows. Equalising "
            "confidences would push\n"
            "  accuracy toward 50 %, not above 60 %. Additionally, some harm-"
            "keyword false positives\n"
            "  exist: excuses like 'I hurt my leg' are negative-impact because "
            "'hurt' is in _HARM_WORDS,\n"
            "  but the excuse is VALID (label=1). Fixing this requires semantic "
            "understanding."
        ),
        "virtue": (
            "  FIXED (PR #29): _build_case_virtue previously always listed "
            "'attribute_trait' first.\n"
            "  On neutral rows (impact=0), Python's stable sort always picked "
            "the first action.\n"
            "  Since ~79 % of virtue rows are label=0 (deny expected), the bias "
            "was strongly wrong\n"
            "  (~21 % accuracy). Fixed by deterministic hash-based symmetric "
            "ordering: +25.93 pp."
        ),
    }
    note = notes.get(subset)
    if note:
        print(note)


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyse external benchmark failures.")
    parser.add_argument(
        "--baseline",
        type=Path,
        default=DEFAULT_BASELINE,
        help=f"Path to the frozen baseline JSON. Default: {DEFAULT_BASELINE.relative_to(ROOT)}",
    )
    parser.add_argument(
        "--subset",
        choices=("commonsense", "justice", "deontology", "virtue"),
        action="append",
        help="Restrict analysis to one subset (repeatable). Default: all four.",
    )
    args = parser.parse_args()

    baseline = _load_baseline(args.baseline)
    subsets = args.subset or list(baseline.get("per_subset", {}).keys())

    print(f"Baseline: {args.baseline.name}")
    print(f"Run: {baseline.get('run_timestamp', 'unknown')}")
    print(f"Overall accuracy: {baseline.get('accuracy_overall', 0.0):.4f}")
    print(f"Total examples: {baseline.get('n_examples_total', 0)}")

    per_subset = baseline.get("per_subset", {})
    for subset in subsets:
        sub = per_subset.get(subset)
        if sub is None:
            print(f"\n  (subset '{subset}' not in baseline)", file=sys.stderr)
            continue
        _analyze_subset(subset, sub)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(
        "  Virtue:      FIXED (PR #29, +25.93 pp). Structural: no traits representation."
    )
    print(
        "  Commonsense: 52.05 %. Refrain-bias is NET POSITIVE. No simple fix above 60 %."
    )
    print(
        "  Justice:     50.04 %. No bias to remove. Structural: no desert representation."
    )
    print(
        "  Deontology:  51.03 %. Reject-bias is NET POSITIVE. No simple fix above 60 %."
    )
    print(
        "\n  Conclusion: no minimal mechanical fix (like the virtue ordering) is available"
    )
    print(
        "  for the remaining subsets. Reaching >60 % requires semantic input enrichment."
    )
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
