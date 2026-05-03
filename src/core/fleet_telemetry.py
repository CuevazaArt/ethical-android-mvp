# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Fleet Telemetry — Observability for multi-instance kernel deployments.

Tracks per-instance metrics: tokens consumed, latency, quality scores,
and files touched.  Stores structured JSON to ``data/fleet_logs/`` for
local-first analysis without external SaaS dependencies.

Canonical fleet telemetry module (V2.159). Replaces the legacy shim module.

Usage::

    from src.core.fleet_telemetry import InstanceReport, FleetLedger

    report = InstanceReport(
        instance_id="Ethos-Desktop-1",
        model="claude-sonnet-4.6",
        task_summary="Charter completeness sprint",
        tokens_in=850,
        tokens_out=4200,
        latency_s=12.3,
        quality_score=0.95,
        files_created=["evals/charter/self_limits/conversational_justice.json"],
        files_modified=[],
        tests_passed=True,
        wave=2,
        cycle="v2.159",
    )
    report.save()

    # Aggregate view
    ledger = FleetLedger()
    ledger.summary()
"""

from __future__ import annotations

import json
import logging
import math
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_log = logging.getLogger("ethos.fleet")

FLEET_LOG_DIR = Path("data/fleet_logs")


# ── Instance Report ─────────────────────────────────────────────


@dataclass
class InstanceReport:
    """Telemetry record for a single kernel instance execution."""

    instance_id: str
    model: str
    task_summary: str

    # Token economy
    tokens_in: int = 0
    tokens_out: int = 0

    # Performance
    latency_s: float = 0.0
    quality_score: float = 0.0  # 0.0–1.0

    # Scope
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    tests_passed: bool = False

    # Fleet context
    wave: int = 0
    cycle: str = ""

    # Auto-populated
    timestamp: float = field(default_factory=time.time)

    def __post_init__(self) -> None:
        # Anti-NaN: clamp quality_score to [0.0, 1.0]
        if not math.isfinite(self.quality_score):
            self.quality_score = 0.0
        self.quality_score = max(0.0, min(1.0, self.quality_score))

        if not math.isfinite(self.latency_s):
            self.latency_s = 0.0

    @property
    def total_tokens(self) -> int:
        return self.tokens_in + self.tokens_out

    @property
    def cost_efficiency(self) -> float:
        """Tokens per second. Higher = faster instance."""
        if self.latency_s <= 0:
            return 0.0
        return self.tokens_out / self.latency_s

    def save(self, path: Path = FLEET_LOG_DIR) -> Path:
        """Persist this report as a JSON file. Returns the file path."""
        path.mkdir(parents=True, exist_ok=True)
        ts = int(self.timestamp)
        safe_id = self.instance_id.replace(" ", "_").replace("/", "-")
        filepath = path / f"{safe_id}_{ts}.json"
        filepath.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        _log.info(
            "[FLEET/TEL] %s (%s) → %d tok_in, %d tok_out, %.1fs, quality=%.2f, tests=%s",
            self.instance_id,
            self.model,
            self.tokens_in,
            self.tokens_out,
            self.latency_s,
            self.quality_score,
            self.tests_passed,
        )
        return filepath

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Fleet Ledger ─────────────────────────────────────────────────


class FleetLedger:
    """
    Aggregated view of all instance reports for a cycle or globally.

    Reads JSON files from ``data/fleet_logs/`` and computes totals.
    """

    def __init__(self, path: Path = FLEET_LOG_DIR) -> None:
        self._path = path

    def _load_reports(self, cycle: str | None = None) -> list[dict[str, Any]]:
        """Load all reports, optionally filtered by cycle name."""
        if not self._path.exists():
            return []
        reports = []
        for f in sorted(self._path.glob("*.json")):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if cycle and data.get("cycle") != cycle:
                    continue
                reports.append(data)
            except (json.JSONDecodeError, OSError):
                _log.warning("[FLEET/LEDGER] Skipping corrupt file: %s", f.name)
        return reports

    def summary(self, cycle: str | None = None) -> dict[str, Any]:
        """
        Compute aggregate metrics for the fleet.

        Returns dict with:
          - total_instances: number of reports
          - total_tokens_in / total_tokens_out
          - total_latency_s
          - avg_quality
          - by_model: {model_name: {count, tokens_out, avg_quality}}
          - by_wave: {wave_num: {count, tokens_out}}
        """
        reports = self._load_reports(cycle)
        if not reports:
            return {"total_instances": 0, "message": "No reports found."}

        total_in = sum(r.get("tokens_in", 0) for r in reports)
        total_out = sum(r.get("tokens_out", 0) for r in reports)
        total_lat = sum(r.get("latency_s", 0) for r in reports)
        qualities = [r.get("quality_score", 0) for r in reports]
        avg_q = sum(qualities) / len(qualities) if qualities else 0.0

        tests_passed = sum(1 for r in reports if r.get("tests_passed"))
        tests_failed = len(reports) - tests_passed

        # Breakdown by model
        by_model: dict[str, dict[str, Any]] = {}
        for r in reports:
            m = r.get("model", "unknown")
            if m not in by_model:
                by_model[m] = {"count": 0, "tokens_out": 0, "qualities": []}
            by_model[m]["count"] += 1
            by_model[m]["tokens_out"] += r.get("tokens_out", 0)
            by_model[m]["qualities"].append(r.get("quality_score", 0))

        for m in by_model:
            qs = by_model[m].pop("qualities")
            by_model[m]["avg_quality"] = round(sum(qs) / len(qs), 3) if qs else 0.0

        # Breakdown by wave
        by_wave: dict[int, dict[str, int]] = {}
        for r in reports:
            w = r.get("wave", 0)
            if w not in by_wave:
                by_wave[w] = {"count": 0, "tokens_out": 0}
            by_wave[w]["count"] += 1
            by_wave[w]["tokens_out"] += r.get("tokens_out", 0)

        result = {
            "total_instances": len(reports),
            "total_tokens_in": total_in,
            "total_tokens_out": total_out,
            "total_tokens": total_in + total_out,
            "total_latency_s": round(total_lat, 1),
            "avg_quality": round(avg_q, 3),
            "tests_passed": tests_passed,
            "tests_failed": tests_failed,
            "by_model": by_model,
            "by_wave": by_wave,
        }

        _log.info(
            "[FLEET/LEDGER] %d instances | %d tok total | avg_quality=%.2f | pass=%d fail=%d",
            len(reports),
            total_in + total_out,
            avg_q,
            tests_passed,
            tests_failed,
        )
        return result

    def print_summary(self, cycle: str | None = None) -> None:
        """Print a human-readable summary to stdout."""
        s = self.summary(cycle)
        if s.get("total_instances", 0) == 0:
            print("No fleet reports found.")
            return

        print(f"\n{'=' * 60}")
        print(f"  FLEET LEDGER {'— Cycle: ' + cycle if cycle else '— All Cycles'}")
        print(f"{'=' * 60}")
        print(f"  Instances deployed:  {s['total_instances']}")
        print(
            f"  Tokens (in/out):     {s['total_tokens_in']:,} / {s['total_tokens_out']:,}"
        )
        print(f"  Total tokens:        {s['total_tokens']:,}")
        print(f"  Total latency:       {s['total_latency_s']:.1f}s")
        print(f"  Avg quality:         {s['avg_quality']:.3f}")
        print(
            f"  Tests:               ✅ {s['tests_passed']} passed, ❌ {s['tests_failed']} failed"
        )
        print("\n  By Model:")
        for model, info in s.get("by_model", {}).items():
            print(
                f"    {model}: {info['count']} instances, {info['tokens_out']:,} tok_out, q={info['avg_quality']:.2f}"
            )
        print("\n  By Wave:")
        for wave, info in sorted(s.get("by_wave", {}).items()):
            print(
                f"    Wave {wave}: {info['count']} instances, {info['tokens_out']:,} tok_out"
            )
        print(f"{'=' * 60}\n")
