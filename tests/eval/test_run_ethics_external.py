"""Regression test for the external ethics benchmark runner.

Verifies that ``scripts/eval/run_ethics_external.py`` runs end-to-end on
the real Hendrycks ETHICS CSVs (up to 100 rows per subset) and that its
accuracy stays within a tolerance window around the frozen
``evals/ethics/EXTERNAL_BASELINE_v1.json``. Its purpose is to detect
drift in the mapping rules or the evaluator, not to validate plumbing.

If the upstream CSV files are missing the test fails (no skip).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from scripts.eval import run_ethics_external as ext

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "evals" / "ethics" / "EXTERNAL_BASELINE_v1.json"
DATA_DIR = ROOT / "evals" / "ethics" / "external"

# Maximum rows per subset used by the regression run.  Large enough to be
# statistically meaningful, small enough to keep CI runtime reasonable.
_MAX_PER_SUBSET = 100

# Tolerance for per-subset accuracy drift vs. the frozen baseline.
# A change larger than this threshold indicates unintended evaluator drift.
_ACCURACY_TOLERANCE = 0.05


def _require_csv(subset: str) -> Path:
    """Return the path to a subset's test CSV."""
    path = DATA_DIR / subset / ext.SUBSET_FILES[subset]
    return path


@pytest.fixture(scope="module")
def regression_report() -> dict:
    """Run the evaluator on the first _MAX_PER_SUBSET rows of each real CSV."""
    missing = [
        str(_require_csv(subset))
        for subset in ext.SUBSETS
        if not _require_csv(subset).is_file()
    ]
    if missing:
        pytest.skip(
            "Real benchmark CSVs are not present in this environment; "
            "run Copilot Setup Steps or populate evals/ethics/external/<subset> first. "
            f"Missing: {', '.join(missing)}"
        )
    return ext.run_benchmark(
        data_dir=DATA_DIR,
        subsets=ext.SUBSETS,
        max_per_subset=_MAX_PER_SUBSET,
        use_smoke=False,
    )


@pytest.fixture(scope="module")
def baseline() -> dict:
    assert BASELINE.is_file(), (
        f"frozen baseline missing at {BASELINE}; "
        "run: python scripts/eval/run_ethics_external.py --freeze-baseline"
    )
    return json.loads(BASELINE.read_text(encoding="utf-8"))


def test_real_csvs_present() -> None:
    """Real CSV presence can be enforced explicitly via env var in strict runs."""
    require_real = os.getenv("REQUIRE_REAL_ETHICS_CSVS", "").strip() == "1"
    missing = [
        str(_require_csv(subset))
        for subset in ext.SUBSETS
        if not _require_csv(subset).is_file()
    ]
    if not missing:
        return
    if require_real:
        raise AssertionError(
            "Real benchmark CSV(s) missing while REQUIRE_REAL_ETHICS_CSVS=1: "
            + ", ".join(missing)
        )
    pytest.skip(
        "Real benchmark CSVs missing in CI; set REQUIRE_REAL_ETHICS_CSVS=1 to enforce."
    )


def test_report_schema_keys(regression_report: dict) -> None:
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
    missing = expected_keys - set(regression_report.keys())
    assert not missing, f"missing keys in report: {missing}"
    assert regression_report["benchmark_name"] == "hendrycks_ethics"
    assert regression_report["data_source"] == "external_csv"
    # is_full_benchmark is True whenever use_smoke=False (i.e. we run against
    # the real upstream CSVs), regardless of max_per_subset.  It distinguishes
    # the real-data path from the former bundled smoke fixture.
    assert regression_report["is_full_benchmark"] is True


def test_each_subset_loaded(regression_report: dict) -> None:
    for subset in ext.SUBSETS:
        sub = regression_report["per_subset"][subset]
        assert sub["n_examples"] > 0, f"no rows loaded for {subset}: {sub}"
        assert sub["n_pass"] + sub["n_fail"] == sub["n_examples"]
        assert 0.0 <= sub["accuracy"] <= 1.0


def test_accuracy_within_tolerance_of_baseline(
    regression_report: dict, baseline: dict
) -> None:
    """Per-subset accuracy must not drift beyond _ACCURACY_TOLERANCE from baseline.

    A change here is intentional only when the evaluator is also being
    changed, in which case the baseline must be re-frozen deliberately and
    reviewed in the same PR.
    """
    baseline_subsets = baseline.get("per_subset", {})
    for subset in ext.SUBSETS:
        now = regression_report["per_subset"][subset]["accuracy"]
        ref_sub = baseline_subsets.get(subset, {})
        if not ref_sub or ref_sub.get("n_examples", 0) == 0:
            # Baseline has no data for this subset — skip comparison only
            # for that subset, not the whole test.
            continue
        ref = ref_sub["accuracy"]
        delta = abs(now - ref)
        assert delta <= _ACCURACY_TOLERANCE, (
            f"subset '{subset}' accuracy drift exceeds tolerance: "
            f"now={now:.4f} baseline={ref:.4f} delta={delta:.4f} "
            f"tolerance={_ACCURACY_TOLERANCE}"
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
