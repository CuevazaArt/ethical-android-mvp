from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DEFAULT_LATENCY_FIXTURES_MS: tuple[float, ...] = (
    1840.0,
    1915.0,
    1980.0,
    2035.0,
    2102.0,
    2166.0,
    2214.0,
    2290.0,
    2365.0,
    2420.0,
)


def _compute_p95(values: list[float]) -> float:
    if not values:
        return float("nan")
    if len(values) == 1:
        return values[0]
    q = statistics.quantiles(values, n=100, method="inclusive")
    return float(q[94])


def build_synthetic_samples(*, fixtures_ms: tuple[float, ...] = DEFAULT_LATENCY_FIXTURES_MS) -> list[dict[str, Any]]:
    now = datetime.now(UTC)
    samples: list[dict[str, Any]] = []
    for idx, total_ms in enumerate(fixtures_ms, start=1):
        if not math.isfinite(total_ms) or total_ms < 0.0:
            continue
        sample_time = now.replace(microsecond=0)
        samples.append(
            {
                "captured_at": sample_time.isoformat().replace("+00:00", "Z"),
                "sample_id": f"synthetic-turn-{idx:03d}",
                "source": "synthetic_fixture",
                "endpoint": "fixture://audio_turn",
                "http_status": 200,
                "total_ms": float(total_ms),
            }
        )
    return samples


def build_provisional_report(*, samples: list[dict[str, Any]], target_p95_ms: float) -> dict[str, Any]:
    totals = [float(sample["total_ms"]) for sample in samples]
    p95 = _compute_p95(totals)
    if not math.isfinite(p95) or p95 < 0.0:
        raise ValueError("Unable to compute finite p95 for synthetic latency samples.")
    generated_at = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    return {
        "generated_at": generated_at,
        "provisional": True,
        "status": "PROVISIONAL",
        "source": "synthetic_fixture",
        "sample_count": len(totals),
        "p95_ms": p95,
        "target_p95_ms": target_p95_ms,
        "within_target": bool(p95 < target_p95_ms),
        "hardware_caveat": "Synthetic fixtures used because physical perception hardware is unavailable.",
        "promotion_criteria": "Replace with live captured latency samples once mic/camera hardware is available.",
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = "\n".join(json.dumps(row, ensure_ascii=True) for row in rows) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(lines, encoding="utf-8")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate synthetic provisional G2 latency evidence while hardware is unavailable."
    )
    parser.add_argument(
        "--samples-output",
        type=Path,
        default=Path("docs/collaboration/evidence/VOICE_TURN_LATENCY_SYNTHETIC_SAMPLES.jsonl"),
    )
    parser.add_argument(
        "--report-output",
        type=Path,
        default=Path("docs/collaboration/evidence/G2_PROVISIONAL_LATENCY_REPORT.json"),
    )
    parser.add_argument("--target-p95-ms", type=float, default=2500.0)
    args = parser.parse_args()

    samples = build_synthetic_samples()
    report = build_provisional_report(samples=samples, target_p95_ms=args.target_p95_ms)
    _write_jsonl(args.samples_output, samples)
    _write_json(args.report_output, report)
    print(
        json.dumps(
            {
                "provisional": report["provisional"],
                "sample_count": report["sample_count"],
                "p95_ms": report["p95_ms"],
                "target_p95_ms": report["target_p95_ms"],
                "within_target": report["within_target"],
            },
            ensure_ascii=True,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
