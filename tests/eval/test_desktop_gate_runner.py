from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.desktop_gate_runner import (
    build_gate_snapshot,
    evaluate_demo_gate,
    evaluate_latency_gate,
    evaluate_stability_gate,
)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(row) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def test_stability_gate_passes_with_14_days(tmp_path: Path) -> None:
    rows = [
        {
            "date": f"2026-04-{day:02d}T09:00:00Z",
            "status": "pass",
            "cycle": "desktop-smoke",
        }
        for day in range(17, 31)
    ]
    ledger = tmp_path / "ledger.jsonl"
    _write_jsonl(ledger, rows)

    result = evaluate_stability_gate(ledger, days=14)

    assert result.passed is True
    assert result.details["covered_days"] == 14


def test_latency_gate_fails_when_p95_exceeds_target(tmp_path: Path) -> None:
    samples = tmp_path / "latency.jsonl"
    _write_jsonl(
        samples,
        [
            {"total_ms": 2000.0},
            {"total_ms": 2100.0},
            {"total_ms": 2200.0},
            {"total_ms": 3100.0},
        ],
    )

    result = evaluate_latency_gate(samples, target_p95_ms=2500.0)

    assert result.passed is False
    assert result.details["p95_ms"] > 2500.0


def test_demo_gate_requires_all_items_to_pass(tmp_path: Path) -> None:
    checklist = tmp_path / "checklist.json"
    checklist.write_text(
        json.dumps(
            {
                "items": [
                    {"id": "a", "passed": True},
                    {"id": "b", "passed": False},
                ]
            }
        ),
        encoding="utf-8",
    )

    result = evaluate_demo_gate(checklist, required_count=2)

    assert result.passed is False
    assert result.details["passed_items"] == 1


def test_snapshot_includes_gate_details_shape(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    _write_jsonl(
        evidence / "DESKTOP_STABILITY_LEDGER.jsonl",
        [
            {
                "date": f"2026-04-{day:02d}T09:00:00Z",
                "status": "pass",
                "cycle": "desktop-smoke",
            }
            for day in range(17, 31)
        ],
    )
    _write_jsonl(
        evidence / "VOICE_TURN_LATENCY_SAMPLES.jsonl",
        [{"captured_at": "2026-04-30T10:00:00Z", "total_ms": 1234.0}],
    )
    _write_jsonl(
        evidence / "G3_CONTRACT_NO_DRIFT_HISTORY.jsonl",
        [{"month": "2099-01", "executed_at": "2099-01-01T09:00:00Z", "exit_code": 0}],
    )
    (evidence / "DEMO_RELIABILITY_CHECKLIST.json").write_text(
        json.dumps(
            {
                "run_id": "demo-reliability-20990101T090000Z",
                "items": [{"id": str(i), "passed": True} for i in range(10)],
            }
        ),
        encoding="utf-8",
    )

    snapshot = build_gate_snapshot(evidence_dir=evidence)

    assert "generated_at" in snapshot
    assert "gates" in snapshot
    for gate in ("G1", "G2", "G3", "G4", "G5"):
        assert gate in snapshot["gates"]
        detail = snapshot["gates"][gate]
        assert detail["status"] in {"pass", "in_progress", "fail"}
        assert isinstance(detail["source"], str)
        assert "summary" in detail
        assert isinstance(detail["stale"], bool)


def test_snapshot_marks_stale_when_updated_at_missing(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    _write_jsonl(
        evidence / "DESKTOP_STABILITY_LEDGER.jsonl",
        [{"date": "bad-date", "status": "pass", "cycle": "desktop-smoke"}],
    )
    _write_jsonl(evidence / "VOICE_TURN_LATENCY_SAMPLES.jsonl", [])
    _write_jsonl(evidence / "G3_CONTRACT_NO_DRIFT_HISTORY.jsonl", [])
    (evidence / "DEMO_RELIABILITY_CHECKLIST.json").write_text(
        json.dumps({"items": []}),
        encoding="utf-8",
    )

    snapshot = build_gate_snapshot(evidence_dir=evidence)

    assert snapshot["gates"]["G1"]["stale"] is True


def test_snapshot_marks_g2_as_in_progress_with_provisional_report(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    evidence.mkdir(parents=True, exist_ok=True)
    _write_jsonl(
        evidence / "DESKTOP_STABILITY_LEDGER.jsonl",
        [{"date": "2099-01-01T09:00:00Z", "status": "pass", "cycle": "desktop-smoke"}],
    )
    _write_jsonl(
        evidence / "VOICE_TURN_LATENCY_SAMPLES.jsonl",
        [{"captured_at": "2099-01-01T10:00:00Z", "total_ms": 999.0}],
    )
    (evidence / "G2_PROVISIONAL_LATENCY_REPORT.json").write_text(
        json.dumps(
            {
                "generated_at": "2099-01-01T11:00:00Z",
                "provisional": True,
                "source": "synthetic_fixture",
                "sample_count": 10,
                "p95_ms": 2200.0,
                "target_p95_ms": 2500.0,
            }
        ),
        encoding="utf-8",
    )
    _write_jsonl(evidence / "G3_CONTRACT_NO_DRIFT_HISTORY.jsonl", [])
    (evidence / "DEMO_RELIABILITY_CHECKLIST.json").write_text(
        json.dumps({"items": []}),
        encoding="utf-8",
    )

    snapshot = build_gate_snapshot(evidence_dir=evidence)

    g2 = snapshot["gates"]["G2"]
    assert g2["status"] == "in_progress"
    assert "PROVISIONAL" in g2["summary"]
