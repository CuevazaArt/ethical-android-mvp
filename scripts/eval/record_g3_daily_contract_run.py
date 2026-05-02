from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.eval.freeze_lane_monthly_report import (  # noqa: E402
    _read_jsonl,
    evaluate_monthly_status,
    run_guardrail_pytest,
)


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def _has_entry_for_day(rows: list[dict[str, Any]], *, month: str, day_key: str) -> bool:
    for row in rows:
        if str(row.get("month", "")) != month:
            continue
        if str(row.get("executed_at", ""))[:10] == day_key:
            return True
    return False


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

    now = datetime.now(UTC)
    month = _month_key(now)
    day_key = now.date().isoformat()
    rows = _read_jsonl(args.history)

    if _has_entry_for_day(rows, month=month, day_key=day_key):
        snapshot = evaluate_monthly_status(args.history, month=month, required_days=args.required_days)
        print(
            json.dumps(
                {
                    "gate": "G3",
                    "recorded_today": True,
                    "action": "skipped_duplicate_day",
                    "month": snapshot.month,
                    "status": snapshot.status,
                    "covered_days": snapshot.covered_days,
                    "required_days": snapshot.required_days,
                },
                ensure_ascii=True,
                indent=2,
            )
        )
        return 0

    cmd = [sys.executable, "-m", "pytest", "tests/test_freeze_lane_guardrails.py", "-q"]
    exit_code = run_guardrail_pytest(args.history, pytest_cmd=cmd)
    snapshot = evaluate_monthly_status(args.history, month=month, required_days=args.required_days)
    print(
        json.dumps(
            {
                "gate": "G3",
                "recorded_today": exit_code == 0,
                "action": "appended_today_run",
                "month": snapshot.month,
                "status": snapshot.status,
                "covered_days": snapshot.covered_days,
                "required_days": snapshot.required_days,
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
