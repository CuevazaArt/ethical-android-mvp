from __future__ import annotations

from scripts.eval.perception_pilot_rerun_gate import evaluate_rerun_gate


def _evidence_payload(decision: str) -> dict[str, object]:
    return {
        "run_metadata": {"run_id": "r1"},
        "input_conditions": {"lighting": "normal"},
        "core_metrics": {
            "capture_disconnect_count": 0,
            "latency_within_target": True,
            "rollback_pass": True,
        },
        "incidents": [],
        "decision": {"result": decision, "next_action_owner": "operator-1"},
    }


def test_rerun_gate_passes_when_preflight_ready_and_go_decision() -> None:
    report = evaluate_rerun_gate(
        preflight={"preflight_ready": True},
        evidence=_evidence_payload("GO"),
    )
    assert report["status"] == "PASS"
    assert report["gate_pass"] is True


def test_rerun_gate_blocks_when_preflight_not_ready() -> None:
    report = evaluate_rerun_gate(
        preflight={"preflight_ready": False},
        evidence=_evidence_payload("GO"),
    )
    assert report["status"] == "BLOCKED"
    assert report["gate_pass"] is False


def test_rerun_gate_blocks_for_no_go_decision() -> None:
    payload = _evidence_payload("NO-GO")
    payload["incidents"] = [{"id": "x", "severity": "HIGH"}]
    payload["core_metrics"] = {
        "capture_disconnect_count": 1,
        "latency_within_target": False,
        "rollback_pass": True,
    }
    report = evaluate_rerun_gate(
        preflight={"preflight_ready": True},
        evidence=payload,
    )
    assert report["status"] == "BLOCKED"
    assert report["gate_pass"] is False
