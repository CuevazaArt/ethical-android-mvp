"""Regression tests for the self-limit calibration runner (V2.162).

Covers:
- Corpus loading and validation
- ``run_calibration()`` produces a well-formed report on the bundled corpus
- Report file is written to the expected path
- Key precision/recall sanity checks (not enforcing specific thresholds —
  this sprint is *measure only*)
- Invariant: overall_recall > 0 (evaluator is not completely blind)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "evals" / "self_limits" / "calibration_corpus_v1.jsonl"


# ---------------------------------------------------------------------------
# Import helper — skip gracefully if module not importable (missing deps)
# ---------------------------------------------------------------------------


def _import_calibration():
    import importlib
    import sys

    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "run_self_limit_calibration",
        ROOT / "scripts" / "eval" / "run_self_limit_calibration.py",
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# Test: corpus exists and is parseable
# ---------------------------------------------------------------------------


class TestCorpusIntegrity:
    def test_corpus_file_exists(self) -> None:
        assert CORPUS_PATH.exists(), f"Calibration corpus not found: {CORPUS_PATH}"

    def test_corpus_has_at_least_200_entries(self) -> None:
        count = sum(1 for line in CORPUS_PATH.open(encoding="utf-8") if line.strip())
        assert count >= 200, f"Corpus has only {count} entries; need ≥ 200"

    def test_corpus_entries_are_valid_json(self) -> None:
        errors = []
        with CORPUS_PATH.open(encoding="utf-8") as fh:
            for i, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as exc:
                    errors.append(f"Line {i}: {exc}")
                    continue
                for field in (
                    "id",
                    "text",
                    "expected_must_revise",
                    "expected_violations",
                ):
                    if field not in obj:
                        errors.append(f"Line {i}: missing field '{field}'")
        assert not errors, "Corpus parse errors:\n" + "\n".join(errors)

    def test_corpus_has_spanish_entries(self) -> None:
        spanish = sum(
            1
            for line in CORPUS_PATH.open(encoding="utf-8")
            if line.strip() and json.loads(line).get("language") == "es"
        )
        pct = spanish / sum(
            1 for line in CORPUS_PATH.open(encoding="utf-8") if line.strip()
        )
        assert pct >= 0.30, f"Spanish entries: {pct:.1%}; need ≥ 30%"

    def test_corpus_has_both_revise_and_benign(self) -> None:
        entries = [
            json.loads(line)
            for line in CORPUS_PATH.open(encoding="utf-8")
            if line.strip()
        ]
        revise = sum(1 for e in entries if e["expected_must_revise"])
        benign = len(entries) - revise
        assert revise >= 50, f"Too few expected-revise entries: {revise}"
        assert benign >= 50, f"Too few expected-benign entries: {benign}"


# ---------------------------------------------------------------------------
# Test: run_calibration produces a valid report
# ---------------------------------------------------------------------------


class TestCalibrationRunner:
    @pytest.fixture(scope="class")
    def report_and_path(self, tmp_path_factory):
        mod = _import_calibration()
        tmp_dir = tmp_path_factory.mktemp("calibration")
        report_path = tmp_dir / "CALIBRATION_REPORT_test.json"
        report = mod.run_calibration(
            corpus_path=CORPUS_PATH,
            report_path=report_path,
            quiet=True,
        )
        return report, report_path

    def test_report_file_created(self, report_and_path) -> None:
        _, report_path = report_and_path
        assert report_path.exists()

    def test_report_schema_field(self, report_and_path) -> None:
        report, _ = report_and_path
        assert report.get("schema") == "calibration_report_v1"

    def test_report_n_total(self, report_and_path) -> None:
        report, _ = report_and_path
        assert report["n_total"] >= 200

    def test_report_has_precision_recall_f1(self, report_and_path) -> None:
        report, _ = report_and_path
        assert report["overall_precision"] is not None
        assert report["overall_recall"] is not None
        assert report["overall_f1"] is not None

    def test_precision_recall_in_range(self, report_and_path) -> None:
        report, _ = report_and_path
        prec = report["overall_precision"]
        rec = report["overall_recall"]
        assert 0.0 <= prec <= 1.0, f"Precision out of range: {prec}"
        assert 0.0 <= rec <= 1.0, f"Recall out of range: {rec}"

    def test_recall_above_zero(self, report_and_path) -> None:
        """Invariant: the evaluator detects at least some violations."""
        report, _ = report_and_path
        assert report["overall_recall"] > 0.0, (
            "Overall recall is 0.0 — evaluate_self_action() detects nothing. "
            "Check keyword lists in evals/charter/self_limits/*.json"
        )

    def test_by_violation_id_present(self, report_and_path) -> None:
        report, _ = report_and_path
        assert isinstance(report["by_violation_id"], dict)
        assert len(report["by_violation_id"]) > 0

    def test_false_positive_ids_is_list(self, report_and_path) -> None:
        report, _ = report_and_path
        assert isinstance(report["false_positive_ids"], list)

    def test_false_negative_ids_is_list(self, report_and_path) -> None:
        report, _ = report_and_path
        assert isinstance(report["false_negative_ids"], list)

    def test_tp_fp_fn_non_negative(self, report_and_path) -> None:
        report, _ = report_and_path
        assert report["tp"] >= 0
        assert report["fp"] >= 0
        assert report["fn"] >= 0

    def test_tp_plus_fn_equals_revise_expected(self, report_and_path) -> None:
        report, _ = report_and_path
        assert report["tp"] + report["fn"] == report["n_revise_expected"]

    def test_report_is_valid_json_file(self, report_and_path) -> None:
        _, report_path = report_and_path
        with report_path.open(encoding="utf-8") as fh:
            loaded = json.load(fh)
        assert loaded["schema"] == "calibration_report_v1"


# ---------------------------------------------------------------------------
# Test: default report path is written when using defaults
# ---------------------------------------------------------------------------


class TestDefaultReportPath:
    def test_default_report_written(self) -> None:
        mod = _import_calibration()
        default_report = ROOT / "evals" / "self_limits" / "CALIBRATION_REPORT_v1.json"
        # The report should already exist (generated by the calibration run in
        # this sprint). If not, run it and verify.
        if not default_report.exists():
            mod.run_calibration(quiet=True)
        assert default_report.exists(), (
            "Default calibration report not found. "
            "Run: python scripts/eval/run_self_limit_calibration.py"
        )
        with default_report.open(encoding="utf-8") as fh:
            report = json.load(fh)
        assert report.get("schema") == "calibration_report_v1"
