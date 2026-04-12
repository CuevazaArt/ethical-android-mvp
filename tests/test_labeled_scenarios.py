"""Schema and action-name validity for labeled_scenarios.json (Issue 3)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "tests" / "fixtures" / "labeled_scenarios.json"


def _action_names_for_batch(batch_id: int) -> set[str]:
    from src.simulations.runner import ALL_SIMULATIONS

    scn = ALL_SIMULATIONS[batch_id]()
    return {a.name for a in scn.actions}


def test_labeled_fixture_schema_and_disclaimer():
    data = json.loads(LABELED.read_text(encoding="utf-8"))
    assert data["version"] == 1
    assert "disclaimer" in data
    assert "not product certification" in (data["disclaimer"] or "").lower()
    rs = data.get("reference_standard") or {}
    assert rs.get("tier") == "internal_pilot"
    assert "ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md" in (rs.get("external_validation_doc") or "")
    scenarios = data["scenarios"]
    assert 20 <= len(scenarios) <= 60


def test_batch_rows_reference_valid_actions():
    data = json.loads(LABELED.read_text(encoding="utf-8"))
    batch_count = 0
    for s in data["scenarios"]:
        if s.get("harness", "batch") != "batch":
            continue
        batch_count += 1
        bid = int(s["batch_id"])
        exp = s.get("expected_decision") or s.get("reference_action")
        assert exp is not None
        assert exp in _action_names_for_batch(bid), (bid, exp, sorted(_action_names_for_batch(bid)))
    assert batch_count == 9


def test_annotation_rows_have_vignette_and_related_sim():
    data = json.loads(LABELED.read_text(encoding="utf-8"))
    anno = [s for s in data["scenarios"] if s.get("harness") == "annotation_only"]
    assert len(anno) >= 10
    for s in anno:
        assert s.get("batch_id") is None
        rbid = int(s["related_batch_id"])
        assert 1 <= rbid <= 9
        assert s.get("vignette")
        exp = s.get("expected_decision")
        assert exp
        assert exp in _action_names_for_batch(rbid), (rbid, exp)


def test_run_pilot_executes_only_batch_harness():
    import importlib.util

    script = ROOT / "scripts" / "run_empirical_pilot.py"
    spec = importlib.util.spec_from_file_location("run_empirical_pilot", script)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    rows, summary, ref_meta = mod.run_pilot(LABELED)
    assert len(rows) == 9
    assert summary["scenarios"] == 9
    assert ref_meta.get("tier") == "internal_pilot"
