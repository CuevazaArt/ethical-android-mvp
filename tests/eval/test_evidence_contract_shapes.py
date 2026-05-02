from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_evidence_json(name: str) -> dict[str, object]:
    path = _REPO_ROOT / "docs" / "collaboration" / "evidence" / name
    raw = path.read_text(encoding="utf-8")
    payload = json.loads(raw)
    assert isinstance(payload, dict)
    return payload


def test_g2_transition_readiness_contract_shape() -> None:
    p = _load_evidence_json("G2_TRANSITION_READINESS.json")
    assert isinstance(p.get("generated_at"), str)
    assert isinstance(p.get("status"), str)
    assert isinstance(p.get("provisional_valid"), bool)
    assert isinstance(p.get("hardware_ready"), bool)
    assert isinstance(p.get("live_sample_count"), int)
    assert isinstance(p.get("target_live_sample_count"), int)
    assert isinstance(p.get("checklist"), list)
    assert isinstance(p.get("notes"), list)
    for item in p["checklist"]:
        assert isinstance(item, str)
    for item in p["notes"]:
        assert isinstance(item, str)


def test_g3_cadence_plan_contract_shape() -> None:
    p = _load_evidence_json("G3_CADENCE_PLAN.json")
    assert p.get("gate") == "G3"
    assert isinstance(p.get("month"), str)
    assert isinstance(p.get("required_days"), int)
    assert isinstance(p.get("covered_days"), int)
    assert isinstance(p.get("missing_days"), list)
    assert isinstance(p.get("overdue_missing_days"), list)
    assert isinstance(p.get("next_run_due_at"), str)
    for day in p["missing_days"]:
        assert isinstance(day, str)
    for day in p["overdue_missing_days"]:
        assert isinstance(day, str)
