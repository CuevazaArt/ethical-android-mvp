from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.desktop_gate_runner import (
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
