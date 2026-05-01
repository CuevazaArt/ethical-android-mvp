from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ALLOWED_STATUS = {"pass", "fail", "critical"}


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


def _normalize_day_key(timestamp: str) -> str:
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"invalid ISO timestamp: {timestamp}") from exc
    return dt.date().isoformat()


def append_stability_entry(
    ledger_path: Path,
    *,
    timestamp: str,
    status: str,
    cycle: str,
    note: str,
    replace_existing_day: bool = False,
) -> dict[str, Any]:
    status_lc = status.lower()
    if status_lc not in ALLOWED_STATUS:
        raise ValueError(f"invalid status '{status}'; expected one of {sorted(ALLOWED_STATUS)}")

    day_key = _normalize_day_key(timestamp)
    rows = _read_jsonl(ledger_path)
    existing = [row for row in rows if str(row.get("date", ""))[:10] == day_key]
    if existing and not replace_existing_day:
        raise ValueError(f"entry for day {day_key} already exists")

    fresh_rows = [row for row in rows if str(row.get("date", ""))[:10] != day_key]
    record = {
        "date": timestamp,
        "status": status_lc,
        "cycle": cycle,
        "note": note,
    }
    fresh_rows.append(record)
    fresh_rows.sort(key=lambda row: str(row["date"]))

    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(row, ensure_ascii=True) for row in fresh_rows) + "\n"
    ledger_path.write_text(payload, encoding="utf-8")
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description="Append one daily entry to desktop stability ledger.")
    parser.add_argument(
        "--ledger",
        type=Path,
        default=Path("docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl"),
    )
    parser.add_argument(
        "--date",
        default=datetime.now(UTC).replace(hour=9, minute=0, second=0, microsecond=0).isoformat().replace("+00:00", "Z"),
        help="ISO datetime in UTC (e.g. 2026-05-01T09:00:00Z).",
    )
    parser.add_argument("--status", default="pass", choices=sorted(ALLOWED_STATUS))
    parser.add_argument("--cycle", default="desktop-smoke")
    parser.add_argument(
        "--note",
        default="No critical crash; ping/status/voice fallback healthy.",
    )
    parser.add_argument(
        "--replace-existing-day",
        action="store_true",
        help="Replace existing record for the same UTC date.",
    )
    args = parser.parse_args()

    record = append_stability_entry(
        args.ledger,
        timestamp=args.date,
        status=args.status,
        cycle=args.cycle,
        note=args.note,
        replace_existing_day=args.replace_existing_day,
    )
    print(json.dumps(record, ensure_ascii=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
