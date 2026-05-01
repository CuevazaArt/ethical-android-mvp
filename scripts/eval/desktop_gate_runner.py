from __future__ import annotations

import argparse
import json
import statistics
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class GateResult:
    name: str
    passed: bool
    summary: str
    details: dict[str, Any]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def evaluate_stability_gate(ledger_path: Path, *, days: int = 14) -> GateResult:
    now = datetime.now(UTC)
    cutoff = now - timedelta(days=days)
    rows = _read_jsonl(ledger_path)
    in_window = []
    for row in rows:
        ts = datetime.fromisoformat(str(row["date"]).replace("Z", "+00:00"))
        if ts >= cutoff:
            in_window.append(row)
    unique_days = {row["date"][:10] for row in in_window}
    failed = [row for row in in_window if str(row.get("status", "")).lower() != "pass"]
    passed = len(unique_days) >= days and not failed
    summary = f"{len(unique_days)}/{days} day(s) covered, failures={len(failed)}"
    return GateResult(
        name="G1",
        passed=passed,
        summary=summary,
        details={
            "window_days": days,
            "covered_days": len(unique_days),
            "failed_entries": len(failed),
        },
    )


def evaluate_latency_gate(samples_path: Path, *, target_p95_ms: float = 2500.0) -> GateResult:
    rows = _read_jsonl(samples_path)
    totals = [float(row["total_ms"]) for row in rows]
    if not totals:
        return GateResult(
            name="G2",
            passed=False,
            summary="no samples",
            details={"target_p95_ms": target_p95_ms},
        )
    q = statistics.quantiles(totals, n=100, method="inclusive")
    p95 = float(q[94])
    passed = p95 < target_p95_ms
    return GateResult(
        name="G2",
        passed=passed,
        summary=f"p95={p95:.2f}ms target<{target_p95_ms:.2f}ms",
        details={
            "sample_count": len(totals),
            "p95_ms": p95,
            "target_p95_ms": target_p95_ms,
            "max_ms": max(totals),
        },
    )


def evaluate_demo_gate(checklist_path: Path, *, required_count: int = 10) -> GateResult:
    payload = _read_json(checklist_path)
    items: list[dict[str, Any]] = list(payload.get("items", []))
    passed_items = [item for item in items if bool(item.get("passed"))]
    passed = len(items) >= required_count and len(passed_items) == len(items)
    return GateResult(
        name="G4",
        passed=passed,
        summary=f"passed {len(passed_items)}/{len(items)} items (required>={required_count})",
        details={
            "required_count": required_count,
            "total_items": len(items),
            "passed_items": len(passed_items),
        },
    )


def _print_result(result: GateResult) -> None:
    blob = {
        "gate": result.name,
        "passed": result.passed,
        "summary": result.summary,
        "details": result.details,
    }
    print(json.dumps(blob, ensure_ascii=True, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="Desktop migration gate runner (51.x).")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_stability = sub.add_parser("stability", help="Evaluate G1 stability gate.")
    p_stability.add_argument("--ledger", required=True, type=Path)
    p_stability.add_argument("--days", type=int, default=14)

    p_latency = sub.add_parser("latency", help="Evaluate G2 latency gate.")
    p_latency.add_argument("--samples", required=True, type=Path)
    p_latency.add_argument("--target-p95-ms", type=float, default=2500.0)

    p_demo = sub.add_parser("demo", help="Evaluate G4 demo reliability gate.")
    p_demo.add_argument("--checklist", required=True, type=Path)
    p_demo.add_argument("--required-count", type=int, default=10)

    args = parser.parse_args()

    if args.cmd == "stability":
        result = evaluate_stability_gate(args.ledger, days=args.days)
    elif args.cmd == "latency":
        result = evaluate_latency_gate(args.samples, target_p95_ms=args.target_p95_ms)
    else:
        result = evaluate_demo_gate(args.checklist, required_count=args.required_count)

    _print_result(result)
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
