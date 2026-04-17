"""Schema and action-name validity for labeled_scenarios.json (Issue 3)."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LABELED = ROOT / "tests" / "fixtures" / "labeled_scenarios.json"

# Agreement labels may match kernel meta-actions (clarification / mission advancement) not present as
# CandidateAction.name on the simulation row — see tests/fixtures/empirical_pilot/scenarios.json.
_PILOT_LABELS_OUTSIDE_SCENARIO_ACTIONS = frozenset({"ask_for_clarification", "proactive_mission_advancement"})


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
    assert (rs.get("external_validation_doc") or "").endswith("docs/proposals/README.md")
    scenarios = data["scenarios"]
    assert 20 <= len(scenarios) <= 80


def test_batch_rows_reference_valid_actions():
    data = json.loads(LABELED.read_text(encoding="utf-8"))
    batch_count = 0
    for s in data["scenarios"]:
        if s.get("harness", "batch") != "batch":
            continue
        batch_count += 1
        bid = int(s["batch_id"])
        if "expected_decision" in s:
            exp = s["expected_decision"]
        else:
            exp = s.get("reference_action")
        # Mapping-only harnesses (17–19): no illustrative agreement label — see empirical_pilot/scenarios.json.
        if exp is None:
            assert bid in {17, 18, 19}, bid
            continue
        names = _action_names_for_batch(bid)
        assert exp in names or exp in _PILOT_LABELS_OUTSIDE_SCENARIO_ACTIONS, (
            bid,
            exp,
            sorted(names),
        )
    assert batch_count == 21


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
    assert len(rows) == 21
    assert summary["scenarios"] == 21
    assert summary["with_reference"] == 18
    assert summary["agreement_kernel"] == 1.0
    assert ref_meta.get("tier") == "internal_pilot"
