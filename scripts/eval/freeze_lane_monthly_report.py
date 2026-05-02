from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class MonthlySnapshot:
    month: str
    status: str
    total_runs: int
    failed_runs: int
    covered_days: int
    required_days: int


@dataclass(frozen=True)
class CadencePlan:
    month: str
    required_days: int
    covered_days: int
    missing_days: list[str]
    overdue_missing_days: list[str]
    next_run_due_at: str


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def _append_jsonl(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(row, ensure_ascii=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"{payload}\n")


def _month_key(dt: datetime) -> str:
    return dt.strftime("%Y-%m")


def evaluate_monthly_status(
    history_path: Path,
    *,
    month: str | None = None,
    required_days: int = 28,
) -> MonthlySnapshot:
    target_month = month or _month_key(datetime.now(UTC))
    rows = [row for row in _read_jsonl(history_path) if str(row.get("month")) == target_month]
    failed = [row for row in rows if int(row.get("exit_code", 1)) != 0]
    covered_days = {str(row.get("executed_at", ""))[:10] for row in rows}
    covered_days.discard("")
    if failed:
        status = "FAIL"
    elif len(covered_days) >= required_days:
        status = "PASS"
    else:
        status = "IN_PROGRESS"
    return MonthlySnapshot(
        month=target_month,
        status=status,
        total_runs=len(rows),
        failed_runs=len(failed),
        covered_days=len(covered_days),
        required_days=required_days,
    )


def build_cadence_plan(
    history_path: Path,
    *,
    month: str | None = None,
    required_days: int = 28,
    now: datetime | None = None,
) -> CadencePlan:
    clock = now or datetime.now(UTC)
    target_month = month or _month_key(clock)
    rows = [row for row in _read_jsonl(history_path) if str(row.get("month")) == target_month]
    covered = {
        str(row.get("executed_at", ""))[:10]
        for row in rows
        if str(row.get("executed_at", "")).strip()
    }
    target_days = [f"{target_month}-{day:02d}" for day in range(1, required_days + 1)]
    missing_days = [day for day in target_days if day not in covered]
    today_key = clock.date().isoformat()
    overdue_missing_days = [day for day in missing_days if day <= today_key]
    if today_key in covered:
        next_due_day = (clock + timedelta(days=1)).date()
    else:
        next_due_day = clock.date()
    next_run_due_at = datetime(
        next_due_day.year,
        next_due_day.month,
        next_due_day.day,
        9,
        0,
        tzinfo=UTC,
    ).isoformat().replace("+00:00", "Z")
    return CadencePlan(
        month=target_month,
        required_days=required_days,
        covered_days=len(set(target_days).intersection(covered)),
        missing_days=missing_days,
        overdue_missing_days=overdue_missing_days,
        next_run_due_at=next_run_due_at,
    )


def run_guardrail_pytest(history_path: Path, *, pytest_cmd: list[str]) -> int:
    completed = subprocess.run(pytest_cmd, check=False)
    now = datetime.now(UTC)
    row = {
        "month": _month_key(now),
        "executed_at": now.isoformat().replace("+00:00", "Z"),
        "command": pytest_cmd,
        "exit_code": completed.returncode,
    }
    _append_jsonl(history_path, row)
    return completed.returncode


def _print_snapshot(snapshot: MonthlySnapshot) -> None:
    blob = {
        "gate": "G3",
        "month": snapshot.month,
        "status": snapshot.status,
        "summary": (
            f"{snapshot.status}: runs={snapshot.total_runs}, failed={snapshot.failed_runs}, "
            f"covered_days={snapshot.covered_days}/{snapshot.required_days}"
        ),
        "details": {
            "total_runs": snapshot.total_runs,
            "failed_runs": snapshot.failed_runs,
            "covered_days": snapshot.covered_days,
            "required_days": snapshot.required_days,
        },
    }
    print(json.dumps(blob, ensure_ascii=True, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Freeze-lane monthly contract no-drift report.")
    parser.add_argument(
        "--history",
        type=Path,
        default=Path("docs/collaboration/evidence/G3_CONTRACT_NO_DRIFT_HISTORY.jsonl"),
        help="JSONL run history file for G3 checks.",
    )
    parser.add_argument(
        "--required-days",
        type=int,
        default=28,
        help="Minimum distinct run-days required to declare month PASS.",
    )
    parser.add_argument(
        "--month",
        type=str,
        default=None,
        help="Month key (YYYY-MM). Defaults to current UTC month.",
    )
    parser.add_argument(
        "--record-run",
        action="store_true",
        help="Execute guardrail pytest and append history before summary.",
    )
    parser.add_argument(
        "--allow-in-progress",
        action="store_true",
        help="Return exit code 0 when status is IN_PROGRESS.",
    )
    parser.add_argument(
        "--cadence-output",
        type=Path,
        default=None,
        help="Optional path to write deterministic cadence plan JSON.",
    )
    args = parser.parse_args()

    if args.record_run:
        cmd = [sys.executable, "-m", "pytest", "tests/test_freeze_lane_guardrails.py", "-q"]
        exit_code = run_guardrail_pytest(args.history, pytest_cmd=cmd)
        if exit_code != 0:
            snapshot = evaluate_monthly_status(
                args.history,
                month=args.month,
                required_days=args.required_days,
            )
            _print_snapshot(snapshot)
            return exit_code

    snapshot = evaluate_monthly_status(
        args.history,
        month=args.month,
        required_days=args.required_days,
    )
    if args.cadence_output is not None:
        cadence = build_cadence_plan(
            args.history,
            month=snapshot.month,
            required_days=args.required_days,
        )
        payload = {
            "gate": "G3",
            "month": cadence.month,
            "required_days": cadence.required_days,
            "covered_days": cadence.covered_days,
            "missing_days": cadence.missing_days,
            "overdue_missing_days": cadence.overdue_missing_days,
            "next_run_due_at": cadence.next_run_due_at,
        }
        args.cadence_output.parent.mkdir(parents=True, exist_ok=True)
        args.cadence_output.write_text(
            json.dumps(payload, ensure_ascii=True, indent=2) + "\n",
            encoding="utf-8",
        )
    _print_snapshot(snapshot)
    if snapshot.status == "PASS":
        return 0
    if snapshot.status == "IN_PROGRESS" and args.allow_in_progress:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
