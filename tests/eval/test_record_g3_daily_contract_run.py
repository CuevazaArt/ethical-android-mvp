from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from scripts.eval.record_g3_daily_contract_run import run_g3_daily_contract


def _append_jsonl(path: Path, row: dict[str, object]) -> None:
    line = json.dumps(row, ensure_ascii=True) + "\n"
    if path.exists():
        path.write_text(path.read_text(encoding="utf-8") + line, encoding="utf-8")
    else:
        path.write_text(line, encoding="utf-8")


def test_run_g3_skips_when_day_already_recorded(tmp_path: Path) -> None:
    history = tmp_path / "G3_CONTRACT_NO_DRIFT_HISTORY.jsonl"
    utc_now = datetime(2026, 5, 2, 15, 30, 0, tzinfo=UTC)
    _append_jsonl(
        history,
        {
            "month": "2026-05",
            "executed_at": "2026-05-02T08:00:00Z",
            "exit_code": 0,
            "command": ["pytest"],
        },
    )

    calls: list[str] = []

    def fake_runner(_path: Path, *, pytest_cmd: list[str]) -> int:
        calls.append("run")
        return 0

    code, blob = run_g3_daily_contract(
        history=history,
        required_days=28,
        utc_now=utc_now,
        run_guardrail=fake_runner,
    )

    assert code == 0
    assert blob["action"] == "skipped_duplicate_day"
    assert blob["recorded_today"] is True
    assert calls == []


def test_run_g3_appends_when_day_missing(tmp_path: Path) -> None:
    history = tmp_path / "G3_CONTRACT_NO_DRIFT_HISTORY.jsonl"
    utc_now = datetime(2026, 5, 2, 15, 30, 0, tzinfo=UTC)

    def fake_runner(path: Path, *, pytest_cmd: list[str]) -> int:
        _append_jsonl(
            path,
            {
                "month": "2026-05",
                "executed_at": "2026-05-02T15:30:00Z",
                "exit_code": 0,
                "command": pytest_cmd,
            },
        )
        return 0

    code, blob = run_g3_daily_contract(
        history=history,
        required_days=28,
        utc_now=utc_now,
        run_guardrail=fake_runner,
    )

    assert code == 0
    assert blob["action"] == "appended_today_run"
    assert blob["recorded_today"] is True
    text = history.read_text(encoding="utf-8").strip().splitlines()
    assert len(text) == 1
