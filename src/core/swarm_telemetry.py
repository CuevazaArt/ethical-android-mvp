# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""
Swarm Telemetry — Observability for the Men Scout Swarm.

Tracks per-agent metrics: tokens consumed, latency, quality scores,
and files touched. Replaces the need for external SaaS (PromptLayer,
Braintrust) by logging structured JSON to `data/swarm_logs/`.

Usage (by L1 after reviewing a Scout's output):

    from src.core.swarm_telemetry import ScoutReport, SwarmLedger

    report = ScoutReport(
        scout_id="Scout-Sonnet-1",
        model="claude-sonnet-4.6",
        task_summary="AudioStreamer — 16kHz PCM Flow via AudioRecord",
        tokens_in=850,
        tokens_out=4200,
        latency_s=12.3,
        quality_score=0.95,
        files_created=["src/clients/.../AudioStreamer.kt"],
        files_modified=[],
        tests_passed=True,
        wave=2,
        cycle="mesh-colonization-01",
    )
    report.save()

    # Aggregate view
    ledger = SwarmLedger()
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

_log = logging.getLogger("ethos.swarm")

SWARM_LOG_DIR = Path("data/swarm_logs")


# ── Scout Report ────────────────────────────────────────────────


@dataclass
class ScoutReport:
    """Telemetry record for a single Men Scout execution."""

    scout_id: str
    model: str
    task_summary: str

    # Token economy
    tokens_in: int = 0
    tokens_out: int = 0

    # Performance
    latency_s: float = 0.0
    quality_score: float = 0.0  # 0.0–1.0 (L1 assigns after review)

    # Scope
    files_created: list[str] = field(default_factory=list)
    files_modified: list[str] = field(default_factory=list)
    tests_passed: bool = False

    # Swarm context
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
        """Tokens per second. Higher = faster agent."""
        if self.latency_s <= 0:
            return 0.0
        return self.tokens_out / self.latency_s

    def save(self, path: Path = SWARM_LOG_DIR) -> Path:
        """Persist this report as a JSON file. Returns the file path."""
        path.mkdir(parents=True, exist_ok=True)
        ts = int(self.timestamp)
        safe_id = self.scout_id.replace(" ", "_").replace("/", "-")
        filepath = path / f"{safe_id}_{ts}.json"
        filepath.write_text(json.dumps(asdict(self), indent=2), encoding="utf-8")
        _log.info(
            "[SWARM/TEL] %s (%s) → %d tok_in, %d tok_out, %.1fs, quality=%.2f, tests=%s",
            self.scout_id,
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


# ── Swarm Ledger ────────────────────────────────────────────────


class SwarmLedger:
    """
    Aggregated view of all Scout reports for a cycle or globally.

    Reads JSON files from `data/swarm_logs/` and computes totals.
    """

    def __init__(self, path: Path = SWARM_LOG_DIR) -> None:
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
                _log.warning("[SWARM/LEDGER] Skipping corrupt file: %s", f.name)
        return reports

    def summary(self, cycle: str | None = None) -> dict[str, Any]:
        """
        Compute aggregate metrics for the swarm.

        Returns dict with:
          - total_scouts: number of reports
          - total_tokens_in / total_tokens_out
          - total_latency_s
          - avg_quality
          - by_model: {model_name: {count, tokens_out, avg_quality}}
          - by_wave: {wave_num: {count, tokens_out}}
        """
        reports = self._load_reports(cycle)
        if not reports:
            return {"total_scouts": 0, "message": "No reports found."}

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
            "total_scouts": len(reports),
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
            "[SWARM/LEDGER] %d scouts | %d tok total | avg_quality=%.2f | pass=%d fail=%d",
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
        if s.get("total_scouts", 0) == 0:
            print("No swarm reports found.")
            return

        print(f"\n{'=' * 60}")
        print(f"  SWARM LEDGER {'— Cycle: ' + cycle if cycle else '— All Cycles'}")
        print(f"{'=' * 60}")
        print(f"  Scouts deployed:  {s['total_scouts']}")
        print(
            f"  Tokens (in/out):  {s['total_tokens_in']:,} / {s['total_tokens_out']:,}"
        )
        print(f"  Total tokens:     {s['total_tokens']:,}")
        print(f"  Total latency:    {s['total_latency_s']:.1f}s")
        print(f"  Avg quality:      {s['avg_quality']:.3f}")
        print(
            f"  Tests:            ✅ {s['tests_passed']} passed, ❌ {s['tests_failed']} failed"
        )
        print("\n  By Model:")
        for model, info in s.get("by_model", {}).items():
            print(
                f"    {model}: {info['count']} scouts, {info['tokens_out']:,} tok_out, q={info['avg_quality']:.2f}"
            )
        print("\n  By Wave:")
        for wave, info in sorted(s.get("by_wave", {}).items()):
            print(
                f"    Wave {wave}: {info['count']} scouts, {info['tokens_out']:,} tok_out"
            )
        print(f"{'=' * 60}\n")
