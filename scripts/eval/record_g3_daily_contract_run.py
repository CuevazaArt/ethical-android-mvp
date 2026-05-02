from __future__ import annotations

import argparse
import importlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Protocol


class _GuardrailRunner(Protocol):
    def __call__(self, history_path: Path, *, pytest_cmd: list[str]) -> int: ...


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _has_entry_for_day(rows: list[dict[str, Any]], *, month: str, day_key: str) -> bool:
    for row in rows:
        if str(row.get("month", "")) != month:
            continue
        if str(row.get("executed_at", ""))[:10] == day_key:
            return True
    return False


def _load_freeze_lane_module() -> Any:
    """Load freeze_lane_monthly_report after repo root is on sys.path."""
    root = Path(__file__).resolve().parents[2]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    return importlib.import_module("scripts.eval.freeze_lane_monthly_report")


def run_g3_daily_contract(
    *,
    history: Path,
    required_days: int,
    utc_now: datetime,
    run_guardrail: _GuardrailRunner | None = None,
) -> tuple[int, dict[str, Any]]:
    """Ensure one G3 guardrail run exists for the UTC calendar day of `utc_now`.

    Returns (exit_code, result_blob). When the day already has a row, pytest is not run.
    """
    mod = _load_freeze_lane_module()
    _read_jsonl = mod._read_jsonl
    evaluate_monthly_status = mod.evaluate_monthly_status
    run_guardrail_pytest = mod.run_guardrail_pytest

    month = _month_key(utc_now)
    day_key = utc_now.date().isoformat()
    rows = _read_jsonl(history)

    if _has_entry_for_day(rows, month=month, day_key=day_key):
        snapshot = evaluate_monthly_status(history, month=month, required_days=required_days)
        blob = {
            "gate": "G3",
            "schema_version": "1",
            "recorded_today": True,
            "action": "skipped_duplicate_day",
            "month": snapshot.month,
            "status": snapshot.status,
            "covered_days": snapshot.covered_days,
            "required_days": snapshot.required_days,
        }
        return 0, blob

    cmd = [sys.executable, "-m", "pytest", "tests/test_freeze_lane_guardrails.py", "-q"]
    runner = run_guardrail or run_guardrail_pytest
    exit_code = runner(history, pytest_cmd=cmd)
    snapshot = evaluate_monthly_status(history, month=month, required_days=required_days)
    blob = {
        "gate": "G3",
        "schema_version": "1",
        "recorded_today": exit_code == 0,
        "action": "appended_today_run",
        "month": snapshot.month,
        "status": snapshot.status,
        "covered_days": snapshot.covered_days,
        "required_days": snapshot.required_days,
    }
    return exit_code, blob


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Ensure G3 has one contract no-drift run recorded for the current UTC day.",
    )
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("docs/collaboration/evidence/G3_CONTRACT_NO_DRIFT_HISTORY.jsonl"),
    )
    parser.add_argument(
        "--required-days",
        type=int,
        default=28,
    )
    args = parser.parse_args()

    exit_code, blob = run_g3_daily_contract(
        history=args.history,
        required_days=args.required_days,
        utc_now=datetime.now(UTC),
    )
    print(json.dumps(blob, ensure_ascii=True, indent=2))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
