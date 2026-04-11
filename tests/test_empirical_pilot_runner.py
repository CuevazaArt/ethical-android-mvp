"""Regression for scripts/run_empirical_pilot.py (Issue 3 batch harness)."""

import importlib.util
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_FIXTURE = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "scenarios.json"
_SUMMARY_FIXTURE = _ROOT / "tests" / "fixtures" / "empirical_pilot" / "last_run_summary.json"


def _load_run_pilot():
    spec = importlib.util.spec_from_file_location(
        "run_empirical_pilot", _ROOT / "scripts" / "run_empirical_pilot.py"
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.run_pilot


def test_empirical_pilot_default_fixture_summary_stable():
    """Kernel + seed=42 in runner; agreement vs illustrative references."""
    run_pilot = _load_run_pilot()
    rows, summary = run_pilot(_FIXTURE)
    assert summary["scenarios"] == 9
    assert summary["with_reference"] == 9
    assert summary["agreement_kernel"] == 1.0
    assert summary["agreement_first"] == 1.0
    assert summary["agreement_max_impact"] == 1.0
    assert summary["kernel_vs_first_rate"] == 1.0
    assert summary["kernel_vs_max_impact_rate"] == 1.0
    for r in rows:
        assert r["agree_kernel"] is True
        assert r["kernel"] == r["reference_action"]


def test_last_run_summary_fixture_matches_disk():
    """Archived summary JSON stays aligned with runner (update file when behavior changes)."""
    run_pilot = _load_run_pilot()
    _, summary = run_pilot(_FIXTURE)
    with open(_SUMMARY_FIXTURE, encoding="utf-8") as f:
        archived = json.load(f)
    assert summary == archived["summary"]
