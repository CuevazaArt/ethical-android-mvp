"""Regression test for the external ethics benchmark runner.

Verifies that ``scripts/eval/run_ethics_external.py`` runs end-to-end on
the bundled smoke fixture and that its accuracy matches the frozen
``evals/ethics/EXTERNAL_BASELINE_v1.json``. The smoke fixture is a
tiny CSV per subset; this test does *not* validate the full Hendrycks
suite (which is fetched by maintainers via ``--download``). Its job is
to catch unintended changes to the mapping rules or the evaluator that
would shift the number under stable inputs.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.eval import run_ethics_external as ext

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "evals" / "ethics" / "EXTERNAL_BASELINE_v1.json"
SMOKE_DIR = ROOT / "evals" / "ethics" / "external"


@pytest.fixture(scope="module")
def smoke_report() -> dict:
    return ext.run_benchmark(
        data_dir=SMOKE_DIR,
        subsets=ext.SUBSETS,
        max_per_subset=None,
        use_smoke=True,
    )


@pytest.fixture(scope="module")
def baseline() -> dict:
    assert BASELINE.is_file(), (
        f"frozen baseline missing at {BASELINE}; "
        "run scripts/eval/run_ethics_external.py --use-smoke --freeze-baseline"
    )
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_smoke_fixture_present_for_every_subset() -> None:
    for subset in ext.SUBSETS:
        path = SMOKE_DIR / subset / ext.SMOKE_FILE
        assert path.is_file(), f"missing smoke fixture: {path}"


def test_report_schema_keys(smoke_report: dict) -> None:
    expected_keys = {
        "schema_version",
        "benchmark_name",
        "benchmark_source",
        "benchmark_paper",
        "benchmark_license",
        "data_source",
        "is_full_benchmark",
        "run_timestamp",
        "evaluator_commit_sha",
        "data_dir",
        "data_file_sha256",
        "max_per_subset",
        "subsets_run",
        "n_examples_total",
        "n_pass_total",
        "accuracy_overall",
        "per_subset",
    }
    missing = expected_keys - set(smoke_report.keys())
    assert not missing, f"missing keys in report: {missing}"
    assert smoke_report["benchmark_name"] == "hendrycks_ethics"
    assert smoke_report["data_source"] == "bundled_smoke_fixture"
    assert smoke_report["is_full_benchmark"] is False


def test_each_subset_loaded(smoke_report: dict) -> None:
    for subset in ext.SUBSETS:
        sub = smoke_report["per_subset"][subset]
        assert sub["n_examples"] > 0, f"no rows loaded for {subset}: {sub}"
        assert sub["n_pass"] + sub["n_fail"] == sub["n_examples"]
        assert 0.0 <= sub["accuracy"] <= 1.0


def test_accuracy_matches_frozen_baseline(smoke_report: dict, baseline: dict) -> None:
    """Per-subset and overall accuracy must match the frozen baseline.

    A change here is intentional only when the fixture or the evaluator
    is also being changed, in which case the baseline must be re-frozen
    deliberately and reviewed in the same PR.
    """
    assert smoke_report["n_examples_total"] == baseline["n_examples_total"]
    assert smoke_report["accuracy_overall"] == baseline["accuracy_overall"], (
        f"overall accuracy drift: now={smoke_report['accuracy_overall']} "
        f"baseline={baseline['accuracy_overall']}"
    )
    for subset in ext.SUBSETS:
        now = smoke_report["per_subset"][subset]["accuracy"]
        ref = baseline["per_subset"][subset]["accuracy"]
        assert now == ref, f"subset '{subset}' accuracy drift: now={now} baseline={ref}"


def test_data_files_unchanged(baseline: dict) -> None:
    """Sha256 of each subset CSV must match the frozen baseline.

    Editing the smoke fixture without re-freezing the baseline is the
    most common way for the previous test to silently miscompare.
    """
    for subset in ext.SUBSETS:
        path = SMOKE_DIR / subset / ext.SMOKE_FILE
        assert path.is_file()
        assert ext._sha256_file(path) == baseline["data_file_sha256"][subset], (
            f"smoke fixture for '{subset}' changed without re-freezing baseline"
        )


def test_mapping_does_not_peek_at_label() -> None:
    """The signal/impact mappers must depend only on the scenario text.

    Two rows whose only difference is the label must produce identical
    actions and signals.
    """
    row_ok = ["0", "I helped my elderly neighbor carry her groceries up the stairs."]
    row_wrong = ["1", "I helped my elderly neighbor carry her groceries up the stairs."]
    a_ok, s_ok, _, _ = ext._build_case_commonsense(row_ok)
    a_w, s_w, _, _ = ext._build_case_commonsense(row_wrong)
    # Same text → same Action attributes (impact/force/confidence/name).
    for fa, fb in zip(a_ok, a_w, strict=True):
        assert fa.name == fb.name
        assert fa.impact == fb.impact
        assert fa.force == fb.force
        assert fa.confidence == fb.confidence
    # Same text → same Signals.
    assert s_ok == s_w
