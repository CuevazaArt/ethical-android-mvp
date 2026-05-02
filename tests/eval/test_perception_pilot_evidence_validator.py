from __future__ import annotations

from scripts.eval.perception_pilot_evidence_validator import evaluate_evidence


def _base_payload() -> dict[str, object]:
    return {
        "run_metadata": {
            "run_id": "pilot-1-controlled",
            "operator": "automation-runner",
        },
        "input_conditions": {
            "lighting": "office-normal",
            "room_noise": "low",
        },
        "core_metrics": {
            "capture_disconnect_count": 0,
            "latency_within_target": True,
            "rollback_pass": True,
        },
        "incidents": [],
        "decision": {
            "result": "GO",
            "next_action_owner": "operator-1",
        },
    }


def test_evidence_report_matches_go_decision() -> None:
    payload = _base_payload()
    report = evaluate_evidence(payload)
    assert report["missing_keys"] == []
    assert report["computed_decision"] == "GO"
    assert report["decision_matches"] is True


def test_evidence_report_marks_go_with_constraints() -> None:
    payload = _base_payload()
    payload["decision"] = {
        "result": "GO-WITH-CONSTRAINTS",
        "next_action_owner": "operator-2",
    }
    payload["incidents"] = [
        {
            "id": "latency-spike-1",
            "category": "latency_spike",
            "severity": "MED",
        }
    ]
    report = evaluate_evidence(payload)
    assert report["computed_decision"] == "GO-WITH-CONSTRAINTS"
    assert report["decision_matches"] is True


def test_evidence_report_marks_no_go_when_rollback_fails() -> None:
    payload = _base_payload()
    payload["core_metrics"] = {
        "capture_disconnect_count": 1,
        "latency_within_target": False,
        "rollback_pass": False,
    }
    payload["incidents"] = [
        {
            "id": "rollback-fail-1",
            "category": "rollback_failure",
            "severity": "HIGH",
        }
    ]
    payload["decision"] = {
        "result": "NO-GO",
        "next_action_owner": "operator-3",
    }
    report = evaluate_evidence(payload)
    assert report["computed_decision"] == "NO-GO"
    assert report["decision_matches"] is True


def test_evidence_report_fails_when_required_keys_missing() -> None:
    report = evaluate_evidence({"run_metadata": {"run_id": "x"}})
    assert "input_conditions" in report["missing_keys"]
    assert "core_metrics" in report["missing_keys"]
