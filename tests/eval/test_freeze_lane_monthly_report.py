from __future__ import annotations

import json
from pathlib import Path

from scripts.eval.freeze_lane_monthly_report import evaluate_monthly_status


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    payload = "\n".join(json.dumps(row) for row in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def test_monthly_status_passes_with_required_distinct_days(tmp_path: Path) -> None:
    history = tmp_path / "g3.jsonl"
    rows = [
        {
            "month": "2026-05",
            "executed_at": f"2026-05-{day:02d}T09:00:00Z",
            "exit_code": 0,
        }
        for day in range(1, 29)
    ]
    _write_jsonl(history, rows)

    snapshot = evaluate_monthly_status(history, month="2026-05", required_days=28)

    assert snapshot.status == "PASS"
    assert snapshot.covered_days == 28


def test_monthly_status_stays_in_progress_with_insufficient_days(
    tmp_path: Path,
) -> None:
    history = tmp_path / "g3.jsonl"
    rows = [
        {
            "month": "2026-05",
            "executed_at": "2026-05-01T09:00:00Z",
            "exit_code": 0,
        }
    ]
    _write_jsonl(history, rows)

    snapshot = evaluate_monthly_status(history, month="2026-05", required_days=28)

    assert snapshot.status == "IN_PROGRESS"
    assert snapshot.failed_runs == 0
