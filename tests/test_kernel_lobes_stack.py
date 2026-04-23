"""Tri-lobe stack: limbic trauma weights, orchestrator integration, sensor adapter seam."""

from __future__ import annotations

import asyncio
import math

import pytest
from src.kernel import CorpusCallosumOrchestrator, _format_proactive_candidate_line
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState, TimeoutTrauma
from src.kernel_lobes.sensor_adapter import FixedSensorAdapter, StubSensorAdapter
from src.modules.sensor_contracts import SensorSnapshot
from src.modules.weighted_ethics_scorer import CandidateAction


def test_format_proactive_candidate_line_clamps_nonfinite_impact_conf() -> None:
    poisoned = CandidateAction(
        name="n",
        description="d",
        estimated_impact=float("nan"),
        confidence=float("inf"),
    )
    out = _format_proactive_candidate_line(poisoned)
    assert "impact=0.000" in out
    assert "conf=0.500" in out


def test_corpus_callosum_proactive_idle_uses_finite_operator_line() -> None:
    orch = CorpusCallosumOrchestrator()

    def _one_action() -> list[CandidateAction]:
        return [
            CandidateAction(
                name="proactive_check",
                description="integrity",
                estimated_impact=0.1,
                confidence=0.9,
            )
        ]

    orch.motivation_engine.get_proactive_actions = _one_action  # type: ignore[method-assign]
    try:
        line = asyncio.run(orch._async_proactive_pulse(None))  # noqa: SLF001
        assert line.startswith("ProactivePulse:")
        assert "proactive_check" in line
        assert "impact=0.100" in line
        assert "conf=0.900" in line
    finally:
        orch.shutdown()


def test_limbic_execute_stage_ignores_nonfinite_swarm_nudge() -> None:
    class _SwarmInf:
        @staticmethod
        def get_swarm_trust_nudge() -> float:
            return float("inf")

    signals = {"trust": 0.5, "risk": 0.0, "hostility": 0.0, "calm": 0.5}
    limbic = LimbicEthicalLobe(swarm=_SwarmInf())
    limbic.execute_stage("agent-1", signals, "hi", 0)
    assert math.isfinite(signals["trust"])
    assert signals["trust"] == 0.5


def test_limbic_judge_raises_tension_on_timeout_trauma() -> None:
    limbic = LimbicEthicalLobe()
    base = SemanticState(perception_confidence=1.0, raw_prompt="ok")
    calm = limbic.judge(base)
    assert calm.social_tension_locus == 0.0
    assert calm.applied_trauma_weight == 0.0

    stressed = SemanticState(
        perception_confidence=0.35,
        raw_prompt="x",
        timeout_trauma=TimeoutTrauma(
            source_lobe="perceptive", latency_ms=50, severity=0.8, context="probe failed"
        ),
    )
    out = limbic.judge(stressed)
    assert isinstance(out, EthicalSentence)
    assert out.is_safe is True
    assert out.social_tension_locus > 0.4
    assert out.applied_trauma_weight > 0.0


def test_corpus_callosum_probe_failure_surfaces_tension_in_response(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", "http://127.0.0.1:1/")
    orch = CorpusCallosumOrchestrator()
    try:
        out = asyncio.run(orch.async_process("ping", None))
        assert "tension=" in out
    finally:
        orch.shutdown()


def test_corpus_callosum_no_probe_plain_response(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("KERNEL_PERCEPTIVE_LOBE_PROBE_URL", raising=False)
    orch = CorpusCallosumOrchestrator()
    try:
        out = asyncio.run(orch.async_process("ping", None))
        assert "Response generated" in out
        assert "tension=" not in out
    finally:
        orch.shutdown()


def test_stub_sensor_adapter_empty_snapshot() -> None:
    stub = StubSensorAdapter()
    snap = stub.read_snapshot()
    assert isinstance(snap, SensorSnapshot)
    assert snap.is_empty()


def test_fixed_sensor_adapter_replays_snapshot() -> None:
    inner = SensorSnapshot(battery_level=0.42, place_trust=0.9)
    fixed = FixedSensorAdapter(inner)
    assert fixed.read_snapshot() is inner
