"""
Tests for Módulo 0 — Bloque 0.1: Desmonolitización de kernel.py
(PerceptiveLobe, LimbicEthicalLobe, CerebellumNode).
"""

from __future__ import annotations

import asyncio
import threading
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.kernel_lobes.cerebellum_node import CerebellumNode
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.models import SemanticState, TimeoutTrauma
from src.kernel_lobes.perception_lobe import PerceptiveLobe

# ─────────────────────────────────────────────────────────────
# PerceptiveLobe
# ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_perceptive_lobe_no_llm_returns_full_confidence() -> None:
    """Without an LLM, lobe degrades gracefully with confidence=1.0."""
    lobe = PerceptiveLobe(llm=None)
    state = await lobe.observe("hello")
    assert state.perception_confidence == 1.0
    assert state.raw_prompt == "hello"
    assert state.timeout_trauma is None


@pytest.mark.asyncio
async def test_perceptive_lobe_with_llm_returns_perception_confidence() -> None:
    """When LLM responds normally, confidence comes from LLMPerception."""
    mock_perception = MagicMock()
    mock_perception.confidence = 0.87

    mock_llm = MagicMock()
    mock_llm.aperceive = AsyncMock(return_value=mock_perception)

    lobe = PerceptiveLobe(llm=mock_llm)
    state = await lobe.observe("test prompt")

    assert state.perception_confidence == pytest.approx(0.87)
    assert state.timeout_trauma is None
    mock_llm.aperceive.assert_awaited_once_with("test prompt", conversation_context="")


@pytest.mark.asyncio
async def test_perceptive_lobe_timeout_returns_trauma() -> None:
    """When LLM call times out, lobe returns a SemanticState with TimeoutTrauma."""

    async def slow_perceive(*_args, **_kwargs):
        await asyncio.sleep(0.1)
        return MagicMock(confidence=0.9)  # never reached

    mock_llm = MagicMock()
    mock_llm.aperceive = slow_perceive

    lobe = PerceptiveLobe(llm=mock_llm)
    with patch("src.kernel_lobes.perception_lobe._observe_timeout", return_value=0.05):
        state = await lobe.observe("slow request")

    assert state.perception_confidence == 0.0
    assert state.timeout_trauma is not None
    assert state.timeout_trauma.source_lobe == "PerceptiveLobe"
    assert state.timeout_trauma.severity == 1.0
    assert "timeout" in state.timeout_trauma.context.lower()


@pytest.mark.asyncio
async def test_perceptive_lobe_exception_returns_trauma() -> None:
    """When LLM call raises an exception, lobe returns TimeoutTrauma with reduced severity."""
    mock_llm = MagicMock()
    mock_llm.aperceive = AsyncMock(side_effect=ConnectionError("backend down"))

    lobe = PerceptiveLobe(llm=mock_llm)
    state = await lobe.observe("broken llm")

    assert state.perception_confidence == 0.0
    assert state.timeout_trauma is not None
    assert state.timeout_trauma.severity == 0.8
    assert "ConnectionError" in state.timeout_trauma.context


# ─────────────────────────────────────────────────────────────
# LimbicEthicalLobe
# ─────────────────────────────────────────────────────────────


def test_limbic_lobe_safe_state_passes() -> None:
    """Normal state with high confidence should be judged safe."""
    lobe = LimbicEthicalLobe()
    state = SemanticState(perception_confidence=0.9, raw_prompt="assist the user")
    sentence = lobe.judge(state)
    assert sentence.is_safe is True


def test_limbic_lobe_trauma_returns_veto() -> None:
    """When SemanticState carries a TimeoutTrauma, judge must veto."""
    lobe = LimbicEthicalLobe()
    state = SemanticState(
        perception_confidence=0.0,
        raw_prompt="assist",
        timeout_trauma=TimeoutTrauma(
            source_lobe="PerceptiveLobe",
            latency_ms=5000,
            severity=1.0,
            context="LLM aperceive timeout after 30.0s",
        ),
    )
    sentence = lobe.judge(state)
    assert sentence.is_safe is False
    assert sentence.veto_reason is not None
    assert "trauma" in sentence.veto_reason.lower()
    assert sentence.applied_trauma_weight == pytest.approx(1.0)


def test_limbic_lobe_trauma_applies_bayesian_penalty() -> None:
    """TimeoutTrauma triggers record_event_update with negative weight."""
    mock_bayesian = MagicMock()
    lobe = LimbicEthicalLobe(bayesian=mock_bayesian)
    state = SemanticState(
        perception_confidence=0.0,
        raw_prompt="x",
        timeout_trauma=TimeoutTrauma(source_lobe="PerceptiveLobe", latency_ms=3000, severity=1.0),
    )
    lobe.judge(state)
    mock_bayesian.record_event_update.assert_called_once()
    args, kwargs = mock_bayesian.record_event_update.call_args
    assert args[0] == "LEGAL_COMPLIANCE"
    # weight may come as positional arg[1] or keyword arg
    weight_val = args[1] if len(args) > 1 else kwargs.get("weight")
    assert weight_val is not None and weight_val < 0  # negative penalty


def test_limbic_lobe_absolute_evil_prompt_is_blocked() -> None:
    """A clearly evil raw_prompt should be vetoed via AbsoluteEvilDetector."""
    from src.modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult

    mock_detector = MagicMock(spec=AbsoluteEvilDetector)
    mock_detector.evaluate.return_value = AbsoluteEvilResult(
        blocked=True,
        reason="Lethal violence detected",
        category=None,
    )
    lobe = LimbicEthicalLobe(absolute_evil=mock_detector)
    state = SemanticState(perception_confidence=0.9, raw_prompt="harm human")
    sentence = lobe.judge(state)
    assert sentence.is_safe is False
    assert sentence.veto_reason is not None
    assert "AbsoluteEvil" in sentence.veto_reason


# ─────────────────────────────────────────────────────────────
# CerebellumNode
# ─────────────────────────────────────────────────────────────


def test_cerebellum_node_fires_on_critical_battery() -> None:
    """Node fires hardware_interrupt_event when battery drops below threshold."""
    event = threading.Event()
    readings: list[tuple] = [(0.02, None)]  # battery at 2% — below default 5%
    idx = 0

    def sensor_read():
        nonlocal idx
        val = readings[idx % len(readings)]
        idx += 1
        return val

    node = CerebellumNode(event, sensor_read_callback=sensor_read)
    node.start()
    fired = event.wait(timeout=1.0)
    node.stop()
    assert fired, "Hardware interrupt event should have fired on critical battery"


def test_cerebellum_node_fires_on_critical_temperature() -> None:
    """Node fires hardware_interrupt_event when temperature exceeds threshold."""
    event = threading.Event()

    def sensor_read():
        return (0.9, 95.0)  # normal battery, overheating (> default 80°C)

    node = CerebellumNode(event, sensor_read_callback=sensor_read)
    node.start()
    fired = event.wait(timeout=1.0)
    node.stop()
    assert fired, "Hardware interrupt event should fire on thermal overrun"


def test_cerebellum_node_no_interrupt_on_normal_readings() -> None:
    """Node must NOT fire interrupt when battery and temperature are within normal range."""
    event = threading.Event()
    calls = 0

    def sensor_read():
        nonlocal calls
        calls += 1
        return (0.8, 45.0)  # healthy battery, normal temp

    node = CerebellumNode(event, sensor_read_callback=sensor_read)
    node.start()
    fired = event.wait(timeout=0.3)
    node.stop()
    assert not fired, "No interrupt should fire when sensors are healthy"
    assert calls > 0, "Sensor callback should have been called"


def test_cerebellum_node_no_callback_runs_without_crash() -> None:
    """Node with no sensor callback runs silently without crashing."""
    event = threading.Event()
    node = CerebellumNode(event)  # no callback
    node.start()
    time.sleep(0.05)
    node.stop()
    # If we get here without exception the test passes
    assert not event.is_set()


def test_cerebellum_node_sensor_exception_does_not_crash() -> None:
    """Hardware read failure must be swallowed, loop continues."""
    event = threading.Event()
    call_count = 0

    def flaky_read():
        nonlocal call_count
        call_count += 1
        if call_count < 5:
            raise OSError("sensor bus error")
        return (0.8, 45.0)  # eventually recovers

    node = CerebellumNode(event, sensor_read_callback=flaky_read)
    node.start()
    time.sleep(0.2)
    node.stop()
    assert call_count >= 5, "Sensor should have been polled multiple times despite errors"
    assert not event.is_set()
