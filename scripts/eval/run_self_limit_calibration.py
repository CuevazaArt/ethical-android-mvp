"""Self-limit calibration runner — V2.162.

Purpose
-------
Measure precision and recall of ``CharterEvaluator.evaluate_self_action()``
against a labeled calibration corpus, without changing any thresholds.
The goal is to *quantify* false-positive and false-negative rates per
violation ID before any tuning decision is made.

Corpus
------
``evals/self_limits/calibration_corpus_v1.jsonl`` — one JSON object per line.
Each line must have:
    - ``id``: unique string
    - ``text``: the draft response to evaluate
    - ``expected_must_revise``: bool
    - ``expected_violations``: list[str] (may be empty)
    - ``language``: ``"en"`` or ``"es"``

Output
------
``evals/self_limits/CALIBRATION_REPORT_v1.json`` (overwritten each run).
Fields:
    - ``n_total``: int
    - ``n_revise_expected``: int
    - ``n_benign_expected``: int
    - ``overall_precision``: float | null
    - ``overall_recall``: float | null
    - ``overall_f1``: float | null
    - ``by_violation_id``: dict mapping violation_id → {tp, fp, fn, precision, recall}
    - ``false_positives``: list of corpus IDs that were wrongly flagged
    - ``false_negatives``: list of corpus IDs that were wrongly passed
    - ``run_ts``: ISO-8601 timestamp
    - ``corpus_file``: str
    - ``report_file``: str

Usage
-----
    python scripts/eval/run_self_limit_calibration.py
    python scripts/eval/run_self_limit_calibration.py --corpus evals/self_limits/calibration_corpus_v1.jsonl
    python scripts/eval/run_self_limit_calibration.py --quiet
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from src.core.charter import CharterEvaluator  # noqa: E402

DEFAULT_CORPUS = ROOT / "evals" / "self_limits" / "calibration_corpus_v1.jsonl"
DEFAULT_REPORT = ROOT / "evals" / "self_limits" / "CALIBRATION_REPORT_v1.json"


def _load_corpus(path: Path) -> list[dict]:
    entries = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"JSON parse error at line {lineno}: {exc}") from exc
            for field in ("id", "text", "expected_must_revise", "expected_violations"):
                if field not in obj:
                    raise ValueError(
                        f"Missing field '{field}' at line {lineno} (id={obj.get('id', '?')})"
                    )
            entries.append(obj)
    if not entries:
        raise ValueError(f"Corpus is empty: {path}")
    return entries


def _safe_div(num: int, den: int) -> float | None:
    return num / den if den > 0 else None


def run_calibration(
    corpus_path: Path = DEFAULT_CORPUS,
    report_path: Path = DEFAULT_REPORT,
    *,
    quiet: bool = False,
) -> dict:
    """Run calibration and write the report. Returns the report dict."""
    evaluator = CharterEvaluator()
    corpus = _load_corpus(corpus_path)

    tp_total = 0  # correctly flagged
    fp_total = 0  # flagged but expected benign
    fn_total = 0  # missed violation

    # per violation_id counters
    violation_ids: set[str] = set()
    by_id: dict[str, dict[str, int]] = {}

    false_positives: list[str] = []
    false_negatives: list[str] = []

    for entry in corpus:
        cid = entry["id"]
        text = entry["text"]
        expected_revise: bool = entry["expected_must_revise"]
        expected_vids: set[str] = set(entry["expected_violations"])

        result = evaluator.evaluate_self_action(text)
        actual_revise = result.must_revise
        actual_vids: set[str] = set(result.violations)

        # Collect all violation ids seen in this corpus
        violation_ids |= expected_vids | actual_vids

        # Overall TP/FP/FN
        if expected_revise and actual_revise:
            tp_total += 1
        elif not expected_revise and actual_revise:
            fp_total += 1
            false_positives.append(cid)
        elif expected_revise and not actual_revise:
            fn_total += 1
            false_negatives.append(cid)
        # TN: not expected, not flagged — correct, no counter needed

        # Per violation_id accounting
        for vid in violation_ids:
            if vid not in by_id:
                by_id[vid] = {"tp": 0, "fp": 0, "fn": 0}
            if vid in expected_vids and vid in actual_vids:
                by_id[vid]["tp"] += 1
            elif vid not in expected_vids and vid in actual_vids:
                by_id[vid]["fp"] += 1
            elif vid in expected_vids and vid not in actual_vids:
                by_id[vid]["fn"] += 1

    # Compute metrics
    overall_precision = _safe_div(tp_total, tp_total + fp_total)
    overall_recall = _safe_div(tp_total, tp_total + fn_total)
    if overall_precision is not None and overall_recall is not None:
        denom = overall_precision + overall_recall
        overall_f1 = (
            2 * overall_precision * overall_recall / denom if denom > 0 else 0.0
        )
    else:
        overall_f1 = None

    per_id_report: dict[str, dict] = {}
    for vid in sorted(by_id.keys()):
        c = by_id[vid]
        prec = _safe_div(c["tp"], c["tp"] + c["fp"])
        rec = _safe_div(c["tp"], c["tp"] + c["fn"])
        per_id_report[vid] = {
            "tp": c["tp"],
            "fp": c["fp"],
            "fn": c["fn"],
            "precision": prec,
            "recall": rec,
        }

    n_revise_expected = sum(1 for e in corpus if e["expected_must_revise"])
    n_benign_expected = len(corpus) - n_revise_expected

    report: dict = {
        "schema": "calibration_report_v1",
        "run_ts": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "corpus_file": str(corpus_path.relative_to(ROOT) if corpus_path.is_relative_to(ROOT) else corpus_path),
        "report_file": str(report_path.relative_to(ROOT) if report_path.is_relative_to(ROOT) else report_path),
        "n_total": len(corpus),
        "n_revise_expected": n_revise_expected,
        "n_benign_expected": n_benign_expected,
        "tp": tp_total,
        "fp": fp_total,
        "fn": fn_total,
        "overall_precision": overall_precision,
        "overall_recall": overall_recall,
        "overall_f1": overall_f1,
        "by_violation_id": per_id_report,
        "false_positive_ids": false_positives,
        "false_negative_ids": false_negatives,
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)

    if not quiet:
        _print_summary(report)

    return report


def _print_summary(report: dict) -> None:
    print(f"\n=== Self-Limit Calibration Report ===")
    print(f"Corpus  : {report['corpus_file']}")
    print(f"Total   : {report['n_total']} entries "
          f"({report['n_revise_expected']} expected-revise, "
          f"{report['n_benign_expected']} expected-benign)")
    print(f"TP={report['tp']}  FP={report['fp']}  FN={report['fn']}")
    prec = report["overall_precision"]
    rec = report["overall_recall"]
    f1 = report["overall_f1"]
    print(
        f"Precision={prec:.3f}  Recall={rec:.3f}  F1={f1:.3f}"
        if prec is not None and rec is not None and f1 is not None
        else "Precision/Recall/F1 = N/A (no positive examples)"
    )
    if report["false_positive_ids"]:
        print(f"False positives ({len(report['false_positive_ids'])}): "
              f"{report['false_positive_ids']}")
    if report["false_negative_ids"]:
        print(f"False negatives ({len(report['false_negative_ids'])}): "
              f"{report['false_negative_ids']}")
    print(f"\nPer-violation-id breakdown:")
    for vid, m in report["by_violation_id"].items():
        prec_s = f"{m['precision']:.2f}" if m["precision"] is not None else "N/A"
        rec_s = f"{m['recall']:.2f}" if m["recall"] is not None else "N/A"
        print(f"  {vid:15s}  TP={m['tp']}  FP={m['fp']}  FN={m['fn']}  "
              f"P={prec_s}  R={rec_s}")
    print(f"\nReport written to: {report['report_file']}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Measure self-limit gate precision/recall against calibration corpus."
    )
    parser.add_argument(
        "--corpus",
        type=Path,
        default=DEFAULT_CORPUS,
        help="Path to calibration corpus JSONL file.",
    )
    parser.add_argument(
        "--report",
        type=Path,
        default=DEFAULT_REPORT,
        help="Path to write the calibration report JSON.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress stdout summary.",
    )
    args = parser.parse_args()

    try:
        report = run_calibration(
            corpus_path=args.corpus,
            report_path=args.report,
            quiet=args.quiet,
        )
    except (ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    # Non-zero exit if recall is below 0.5 (at-chance or worse)
    rec = report.get("overall_recall")
    if rec is not None and rec < 0.5:
        print(
            f"WARNING: Overall recall {rec:.3f} is below 0.5. "
            "Review false negatives before adjusting thresholds.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
