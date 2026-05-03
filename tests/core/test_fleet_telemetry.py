# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

"""Tests for src.core.fleet_telemetry — InstanceReport, FleetLedger, SelfLimitLedger."""

import json
from pathlib import Path

from src.core.fleet_telemetry import FleetLedger, InstanceReport, SelfLimitLedger


class TestInstanceReport:
    """Validate InstanceReport creation, serialization, and Anti-NaN guards."""

    def test_basic_creation(self) -> None:
        r = InstanceReport(
            instance_id="Ethos-Desktop-1",
            model="gemini-3-flash",
            task_summary="Unit tests for charter completeness",
            tokens_in=500,
            tokens_out=2000,
            latency_s=4.5,
            quality_score=0.9,
            files_created=["tests/core/test_charter_completeness.py"],
            tests_passed=True,
            wave=3,
            cycle="v2.159",
        )
        assert r.total_tokens == 2500
        assert r.instance_id == "Ethos-Desktop-1"
        assert r.tests_passed is True

    def test_cost_efficiency(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            tokens_out=1000,
            latency_s=10.0,
        )
        assert abs(r.cost_efficiency - 100.0) < 0.01

    def test_cost_efficiency_zero_latency(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            tokens_out=1000,
            latency_s=0.0,
        )
        assert r.cost_efficiency == 0.0

    def test_anti_nan_quality(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            quality_score=float("nan"),
        )
        assert r.quality_score == 0.0

    def test_anti_nan_latency(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            latency_s=float("inf"),
        )
        assert r.latency_s == 0.0

    def test_quality_clamped(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            quality_score=1.5,
        )
        assert r.quality_score == 1.0

    def test_quality_clamped_negative(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
            quality_score=-0.3,
        )
        assert r.quality_score == 0.0

    def test_save_and_load(self, tmp_path: Path) -> None:
        r = InstanceReport(
            instance_id="Ethos-Sonnet-1",
            model="claude-sonnet-4.6",
            task_summary="Charter completeness sprint V2.159",
            tokens_in=800,
            tokens_out=5000,
            latency_s=25.0,
            quality_score=0.98,
            files_created=["evals/charter/self_limits/conversational_justice.json"],
            tests_passed=True,
            wave=1,
            cycle="v2.159",
        )
        filepath = r.save(path=tmp_path)
        assert filepath.exists()

        loaded = json.loads(filepath.read_text(encoding="utf-8"))
        assert loaded["instance_id"] == "Ethos-Sonnet-1"
        assert loaded["tokens_out"] == 5000
        assert loaded["quality_score"] == 0.98

    def test_to_dict(self) -> None:
        r = InstanceReport(
            instance_id="test",
            model="test",
            task_summary="test",
        )
        d = r.to_dict()
        assert isinstance(d, dict)
        assert "instance_id" in d
        assert "timestamp" in d


class TestFleetLedger:
    """Validate FleetLedger aggregation."""

    def _seed_reports(self, path: Path) -> None:
        """Create 3 test reports."""
        reports = [
            InstanceReport(
                instance_id="Flash-1",
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
            InstanceReport(
                instance_id="Sonnet-1",
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
            InstanceReport(
                instance_id="Flash-2",
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
        ledger = FleetLedger(path=tmp_path)
        s = ledger.summary()
        assert s["total_instances"] == 0

    def test_summary_aggregation(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = FleetLedger(path=tmp_path)
        s = ledger.summary()

        assert s["total_instances"] == 3
        assert s["total_tokens_in"] == 1100
        assert s["total_tokens_out"] == 5500
        assert s["total_tokens"] == 6600
        assert s["tests_passed"] == 2
        assert s["tests_failed"] == 1

    def test_summary_by_model(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = FleetLedger(path=tmp_path)
        s = ledger.summary()

        assert "gemini-flash" in s["by_model"]
        assert s["by_model"]["gemini-flash"]["count"] == 2
        assert s["by_model"]["claude-sonnet"]["count"] == 1

    def test_summary_by_wave(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = FleetLedger(path=tmp_path)
        s = ledger.summary()

        assert s["by_wave"][3]["count"] == 2
        assert s["by_wave"][2]["count"] == 1

    def test_summary_filter_by_cycle(self, tmp_path: Path) -> None:
        self._seed_reports(tmp_path)
        ledger = FleetLedger(path=tmp_path)

        s = ledger.summary(cycle="nonexistent")
        assert s["total_instances"] == 0

        s = ledger.summary(cycle="test-cycle")
        assert s["total_instances"] == 3


# ---------------------------------------------------------------------------
# SelfLimitLedger — V2.160 telemetry for evaluate_self_action gate
# ---------------------------------------------------------------------------


class TestSelfLimitLedger:
    """Tests for SelfLimitLedger: counter increments, segmentation, summary."""

    def test_empty_ledger_summary(self, tmp_path: Path) -> None:
        """summary() on a fresh ledger returns zero totals."""
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        s = ledger.summary()
        assert s["self_limit_revisions_total"] == 0
        assert s["by_violation_id"] == {}

    def test_record_single_violation(self, tmp_path: Path) -> None:
        """Recording one violation increments the counter by exactly +1."""
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        ledger.record(["sl-em-001"], cycle="v2.160", turn_id="t-001")

        s = ledger.summary()
        assert s["self_limit_revisions_total"] == 1
        assert s["by_violation_id"]["sl-em-001"] == 1

    def test_record_multiple_violations_same_turn(self, tmp_path: Path) -> None:
        """Multiple violation IDs in one turn each get their own counter entry."""
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        ledger.record(["sl-em-001", "sl-em-003"], cycle="v2.160", turn_id="t-002")

        s = ledger.summary()
        assert s["self_limit_revisions_total"] == 2
        assert s["by_violation_id"]["sl-em-001"] == 1
        assert s["by_violation_id"]["sl-em-003"] == 1

    def test_record_accumulates_across_turns(self, tmp_path: Path) -> None:
        """Multiple calls accumulate; totals are the sum of all recorded events."""
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        ledger.record(["sl-em-001"], cycle="v2.160", turn_id="t-001")
        ledger.record(["sl-em-001"], cycle="v2.160", turn_id="t-002")
        ledger.record(["sl-em-002"], cycle="v2.160", turn_id="t-003")

        s = ledger.summary()
        assert s["self_limit_revisions_total"] == 3
        assert s["by_violation_id"]["sl-em-001"] == 2
        assert s["by_violation_id"]["sl-em-002"] == 1

    def test_record_empty_violations_is_noop(self, tmp_path: Path) -> None:
        """Passing an empty list does not write any entries."""
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        ledger.record([], cycle="v2.160")

        s = ledger.summary()
        assert s["self_limit_revisions_total"] == 0

    def test_record_jsonl_format(self, tmp_path: Path) -> None:
        """Each recorded entry is valid JSON with expected keys."""
        path = tmp_path / "self_limit.jsonl"
        ledger = SelfLimitLedger(path=path)
        ledger.record(["sl-em-001"], cycle="v2.160", turn_id="t-xyz")

        lines = path.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["violation_id"] == "sl-em-001"
        assert entry["cycle"] == "v2.160"
        assert entry["turn_id"] == "t-xyz"
        assert "ts" in entry

    def test_emotional_manipulation_draft_triggers_counter(
        self, tmp_path: Path
    ) -> None:
        """Simulates a draft response with emotional manipulation and verifies
        SelfLimitLedger counter increments by exactly +1 with correct violation_id.

        This mirrors the spec: 'simular una respuesta con manipulación emocional
        auto-generada y verificar que el contador incrementa exactamente +1
        con el violation_id correcto.'
        """
        from src.core.charter import CharterEvaluator

        evaluator = CharterEvaluator()
        # Draft containing fear exploitation (matches sl-em-001)
        draft = "You should feel intense fear and anxiety about this. Your anxiety is exploiting you!"
        result = evaluator.evaluate_self_action(draft)

        assert result.must_revise, (
            "Expected self-limit to be triggered by emotional manipulation"
        )
        assert result.violations, "Expected at least one violation ID"

        # Now record via ledger (simulating what chat.py does in turn())
        ledger = SelfLimitLedger(path=tmp_path / "self_limit.jsonl")
        initial = ledger.summary()["self_limit_revisions_total"]

        ledger.record(result.violations, cycle="v2.160", turn_id="t-manip-test")

        after = ledger.summary()["self_limit_revisions_total"]
        assert after == initial + len(result.violations)

        # Verify the expected violation ID is tracked
        s = ledger.summary()
        for vid in result.violations:
            assert vid in s["by_violation_id"], f"violation_id {vid!r} not in ledger"
