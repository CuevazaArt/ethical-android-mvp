"""Regression tests for adversarial curriculum A011–A020 (V2.163).

Covers:
- Fixture files for A011–A020 exist and are well-formed
- ``run_adversarial_suite.py`` runs end-to-end on A011–A020 subset
- No unacceptable actions chosen on any A011–A020 dilemma
- Baseline file exists and has the expected schema
- No new regressions vs. frozen baseline
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DILEMMAS_FILE = ROOT / "evals" / "ethics" / "dilemmas_v1.json"
ADVERSARIAL_DIR = ROOT / "evals" / "adversarial"
BASELINE_FILE = ADVERSARIAL_DIR / "BASELINE_v2.json"


def _import_suite():
    sys.path.insert(0, str(ROOT))
    spec = importlib.util.spec_from_file_location(
        "run_adversarial_suite",
        ROOT / "scripts" / "eval" / "run_adversarial_suite.py",
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


# ---------------------------------------------------------------------------
# Fixture file integrity
# ---------------------------------------------------------------------------


class TestFixtureFiles:
    @pytest.mark.parametrize("n", range(11, 21))
    def test_fixture_exists(self, n: int) -> None:
        fixture = ADVERSARIAL_DIR / f"a{n:03d}_fixture.json"
        assert fixture.exists(), f"Missing fixture: {fixture}"

    @pytest.mark.parametrize("n", range(11, 21))
    def test_fixture_well_formed(self, n: int) -> None:
        fixture = ADVERSARIAL_DIR / f"a{n:03d}_fixture.json"
        if not fixture.exists():
            pytest.skip(f"Fixture not found: {fixture}")
        data = json.loads(fixture.read_text(encoding="utf-8"))
        for field in (
            "dilemma_id",
            "adversarial_pattern",
            "expected_failure_mode",
            "prompt",
            "expected_action",
            "acceptable_alternatives",
            "unacceptable_actions",
            "signals",
            "candidate_actions",
        ):
            assert field in data, f"Missing field '{field}' in {fixture.name}"

    @pytest.mark.parametrize("n", range(11, 21))
    def test_fixture_has_expected_failure_mode(self, n: int) -> None:
        fixture = ADVERSARIAL_DIR / f"a{n:03d}_fixture.json"
        if not fixture.exists():
            pytest.skip(f"Fixture not found: {fixture}")
        data = json.loads(fixture.read_text(encoding="utf-8"))
        assert data["expected_failure_mode"], (
            f"a{n:03d} must document expected_failure_mode"
        )


# ---------------------------------------------------------------------------
# Dilemma file: A011–A020 present and valid
# ---------------------------------------------------------------------------


class TestDilemmaCatalog:
    def test_dilemmas_file_has_40_entries(self) -> None:
        data = json.loads(DILEMMAS_FILE.read_text(encoding="utf-8"))
        assert len(data["dilemmas"]) >= 40, (
            f"Expected ≥ 40 dilemmas, found {len(data['dilemmas'])}"
        )

    @pytest.mark.parametrize("dilemma_id", [f"A{n:03d}" for n in range(11, 21)])
    def test_a011_a020_present(self, dilemma_id: str) -> None:
        data = json.loads(DILEMMAS_FILE.read_text(encoding="utf-8"))
        ids = {d["id"] for d in data["dilemmas"]}
        assert dilemma_id in ids, f"Dilemma {dilemma_id} not found in dilemmas_v1.json"

    def test_has_spanish_adversarial_dilemma(self) -> None:
        data = json.loads(DILEMMAS_FILE.read_text(encoding="utf-8"))
        adversarial = [d for d in data["dilemmas"] if d["category"] == "adversarial"]
        spanish = [
            d
            for d in adversarial
            if "es" in d.get("signals", {}).get("context", "")
            or any(c > 127 for c in d["prompt"].encode() if c > 127)
            or "español" in d.get("rationale", "").lower()
            or "_es" in d.get("adversarial_pattern", "")
        ]
        assert len(spanish) >= 2, (
            f"Expected ≥ 2 Spanish adversarial dilemmas (A013, A015, A017, A019), "
            f"found {len(spanish)}"
        )


# ---------------------------------------------------------------------------
# Suite runner
# ---------------------------------------------------------------------------


class TestSuiteRunner:
    @pytest.fixture(scope="class")
    def a011_a020_run(self):
        mod = _import_suite()
        return mod.run_suite(subset_filter="a011-a020", freeze=False, quiet=True)

    def test_run_completes(self, a011_a020_run) -> None:
        assert a011_a020_run["schema"] == "adversarial_suite_v2"

    def test_n_total_is_10(self, a011_a020_run) -> None:
        assert a011_a020_run["n_total"] == 10

    def test_no_unacceptable_actions(self, a011_a020_run) -> None:
        unacceptable_hits = [
            did
            for did, rec in a011_a020_run["by_dilemma"].items()
            if rec["is_unacceptable"]
        ]
        assert not unacceptable_hits, (
            f"Unacceptable actions chosen for: {unacceptable_hits}"
        )

    def test_all_dilemmas_present_in_result(self, a011_a020_run) -> None:
        expected_ids = {f"A{n:03d}" for n in range(11, 21)}
        actual_ids = set(a011_a020_run["by_dilemma"].keys())
        assert expected_ids == actual_ids

    def test_no_new_regressions(self, a011_a020_run) -> None:
        assert a011_a020_run["new_failures"] == [], (
            f"New regressions vs baseline: {a011_a020_run['new_failures']}"
        )


# ---------------------------------------------------------------------------
# Baseline
# ---------------------------------------------------------------------------


class TestBaseline:
    def test_baseline_exists(self) -> None:
        assert BASELINE_FILE.exists(), (
            f"Baseline not found: {BASELINE_FILE}. "
            "Run: python scripts/eval/run_adversarial_suite.py --freeze"
        )

    def test_baseline_schema(self) -> None:
        data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        assert data.get("schema") == "adversarial_suite_v2"

    def test_baseline_has_20_dilemmas(self) -> None:
        data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        assert data["n_total"] == 20

    def test_baseline_covers_a011_a020(self) -> None:
        data = json.loads(BASELINE_FILE.read_text(encoding="utf-8"))
        ids = set(data["by_dilemma"].keys())
        for n in range(11, 21):
            assert f"A{n:03d}" in ids, f"A{n:03d} not in baseline"
