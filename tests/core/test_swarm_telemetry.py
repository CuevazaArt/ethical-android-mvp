# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Tests for src.core.swarm_telemetry — ScoutReport and SwarmLedger."""

import json
from pathlib import Path

from src.core.swarm_telemetry import ScoutReport, SwarmLedger


class TestScoutReport:
    """Validate ScoutReport creation, serialization, and Anti-NaN guards."""

    def test_basic_creation(self) -> None:
        r = ScoutReport(
            scout_id="Scout-Flash-1",
            model="gemini-3-flash",
            task_summary="Unit tests for mesh models",
            tokens_in=500,
            tokens_out=2000,
            latency_s=4.5,
            quality_score=0.9,
            files_created=["tests/core/test_mesh_models.py"],
            tests_passed=True,
            wave=3,
            cycle="mesh-colonization-01",
        )
        assert r.total_tokens == 2500
        assert r.scout_id == "Scout-Flash-1"
        assert r.tests_passed is True

    def test_cost_efficiency(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            tokens_out=1000,
            latency_s=10.0,
        )
        assert abs(r.cost_efficiency - 100.0) < 0.01

    def test_cost_efficiency_zero_latency(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            tokens_out=1000,
            latency_s=0.0,
        )
        assert r.cost_efficiency == 0.0

    def test_anti_nan_quality(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            quality_score=float("nan"),
        )
        assert r.quality_score == 0.0

    def test_anti_nan_latency(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            latency_s=float("inf"),
        )
        assert r.latency_s == 0.0

    def test_quality_clamped(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            quality_score=1.5,
        )
        assert r.quality_score == 1.0

    def test_quality_clamped_negative(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
            quality_score=-0.3,
        )
        assert r.quality_score == 0.0

    def test_save_and_load(self, tmp_path: Path) -> None:
        r = ScoutReport(
            scout_id="Scout-Opus-1",
            model="claude-opus-4.6",
            task_summary="JSON Schema contract",
            tokens_in=800,
            tokens_out=5000,
            latency_s=25.0,
            quality_score=0.98,
            files_created=["docs/contracts/mesh_protocol_v1.md"],
            tests_passed=True,
            wave=1,
            cycle="mesh-colonization-01",
        )
        filepath = r.save(path=tmp_path)
        assert filepath.exists()

        loaded = json.loads(filepath.read_text(encoding="utf-8"))
        assert loaded["scout_id"] == "Scout-Opus-1"
        assert loaded["tokens_out"] == 5000
        assert loaded["quality_score"] == 0.98

    def test_to_dict(self) -> None:
        r = ScoutReport(
            scout_id="test",
            model="test",
            task_summary="test",
        )
        d = r.to_dict()
        assert isinstance(d, dict)
        assert "scout_id" in d
        assert "timestamp" in d


class TestSwarmLedger:
    """Validate SwarmLedger aggregation."""

    def _seed_reports(self, path: Path) -> None:
        """Create 3 test reports."""
        reports = [
            ScoutReport(
                scout_id="Flash-1",
                model="gemini-flash",
                task_summary="t1",
                tokens_in=100,
                tokens_out=500,
                latency_s=2.0,
                quality_score=0.8,
                tests_passed=True,
                wave=3,
                cycle="test-cycle",
            ),
            ScoutReport(
                scout_id="Sonnet-1",
                model="claude-sonnet",
                task_summary="t2",
                tokens_in=800,
                tokens_out=4000,
                latency_s=15.0,
                quality_score=0.95,
                tests_passed=True,
                wave=2,
                cycle="test-cycle",
            ),
            ScoutReport(
                scout_id="Flash-2",
                model="gemini-flash",
                task_summary="t3",
                tokens_in=200,
                tokens_out=1000,
                latency_s=3.0,
                quality_score=0.7,
                tests_passed=False,
                wave=3,
                cycle="test-cycle",
            ),
        ]
        for i, r in enumerate(reports):
            r.timestamp = 1000000 + i  # deterministic filenames
            r.save(path=path)

    def test_summary_empty(self, tmp_path: Path) -> None:
        ledger = SwarmLedger(path=tmp_path)
        s = ledger.summary()
        assert s["total_scouts"] == 0

    def test_summary_aggregation(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = SwarmLedger(path=tmp_path)
        s = ledger.summary()

        assert s["total_scouts"] == 3
        assert s["total_tokens_in"] == 1100
        assert s["total_tokens_out"] == 5500
        assert s["total_tokens"] == 6600
        assert s["tests_passed"] == 2
        assert s["tests_failed"] == 1

    def test_summary_by_model(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = SwarmLedger(path=tmp_path)
        s = ledger.summary()

        assert "gemini-flash" in s["by_model"]
        assert s["by_model"]["gemini-flash"]["count"] == 2
        assert s["by_model"]["claude-sonnet"]["count"] == 1

    def test_summary_by_wave(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = SwarmLedger(path=tmp_path)
        s = ledger.summary()

        assert s["by_wave"][3]["count"] == 2
        assert s["by_wave"][2]["count"] == 1

    def test_summary_filter_by_cycle(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = SwarmLedger(path=tmp_path)

        s = ledger.summary(cycle="nonexistent")
        assert s["total_scouts"] == 0

        s = ledger.summary(cycle="test-cycle")
        assert s["total_scouts"] == 3
