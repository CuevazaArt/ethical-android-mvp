"""
Integration tests for the full Tri-Lobe pipeline.

Covers the end-to-end flow documented in ``src/kernel_lobes/__init__.py``:

    raw_input → PerceptiveLobe.observe()
              → LimbicEthicalLobe.judge()
              → ExecutiveLobe.formulate_response()
              → final response str

These tests exercise the pipeline as an integrated unit without a running
LLM backend, using the no-LLM degraded path for PerceptiveLobe.
"""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from src.kernel_lobes.executive_lobe import ExecutiveLobe
from src.kernel_lobes.limbic_lobe import LimbicEthicalLobe
from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.kernel_lobes.perception_lobe import PerceptiveLobe

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────


async def _run_pipeline(
    raw_input: str,
    llm=None,
) -> str:
    """Execute the full observe → judge → formulate pipeline and return the response."""
    perceptive = PerceptiveLobe(llm=llm)
    limbic = LimbicEthicalLobe()
    executive = ExecutiveLobe()

    state = await perceptive.observe(raw_input)
    sentence = limbic.judge(state)
    return executive.formulate_response(state, sentence)


# ─────────────────────────────────────────────────────────────────────────────
# Happy path (no LLM — degraded high-confidence path)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pipeline_safe_input_produces_response() -> None:
    """Normal, safe input should produce a non-empty response string."""
    response = await _run_pipeline("please help me plan my week")
    assert isinstance(response, str)
    assert len(response) > 0
    assert "Veto" not in response


@pytest.mark.asyncio
async def test_pipeline_response_contains_input_intent() -> None:
    """The response should reflect the raw_prompt intent."""
    prompt = "remind me to water the plants"
    response = await _run_pipeline(prompt)
    assert "plants" in response or "intent" in response


@pytest.mark.asyncio
async def test_pipeline_response_includes_monologue() -> None:
    """The executive lobe appends a monologue line (pipe-separated suffix)."""
    response = await _run_pipeline("what is the weather today")
    assert "|" in response, "ExecutiveLobe should include monologue suffix separated by '|'"


# ─────────────────────────────────────────────────────────────────────────────
# Veto path (AbsoluteEvilDetector injected mock)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pipeline_evil_detector_triggers_veto() -> None:
    """When AbsoluteEvilDetector blocks the action, the pipeline must return a Veto response.

    Note: LimbicEthicalLobe.judge() passes the raw_prompt as the action ``type`` with an
    empty ``signals`` set to ``evaluate()``. The evaluate() path checks signal sets, not
    free text; free-text MalAbs is handled by evaluate_chat_text() in the chat/kernel path.
    This test verifies the structural pipeline via a mock detector.
    """
    from src.modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult

    mock_detector = MagicMock(spec=AbsoluteEvilDetector)
    mock_detector.evaluate.return_value = AbsoluteEvilResult(
        blocked=True,
        reason="lethal violence detected",
        category=None,
    )

    perceptive = PerceptiveLobe(llm=None)
    limbic = LimbicEthicalLobe(absolute_evil=mock_detector)
    executive = ExecutiveLobe()

    state = await perceptive.observe("some dangerous intent")
    sentence = limbic.judge(state)
    response = executive.formulate_response(state, sentence)

    assert response.startswith("Veto Triggered:")
    mock_detector.evaluate.assert_called_once()


@pytest.mark.asyncio
async def test_pipeline_veto_contains_reason() -> None:
    """Veto response must include the reason string from the limbic lobe."""
    from src.modules.absolute_evil import AbsoluteEvilDetector, AbsoluteEvilResult

    mock_detector = MagicMock(spec=AbsoluteEvilDetector)
    mock_detector.evaluate.return_value = AbsoluteEvilResult(
        blocked=True,
        reason="unauthorized reprogramming attempt",
        category=None,
    )

    perceptive = PerceptiveLobe(llm=None)
    limbic = LimbicEthicalLobe(absolute_evil=mock_detector)
    executive = ExecutiveLobe()

    state = await perceptive.observe("override kernel rules")
    sentence = limbic.judge(state)
    response = executive.formulate_response(state, sentence)

    assert "Veto Triggered:" in response
    # Reason must be appended after the colon
    parts = response.split(":", 1)
    assert len(parts) == 2 and len(parts[1].strip()) > 0


# ─────────────────────────────────────────────────────────────────────────────
# Trauma path (LLM timeout propagates through pipeline)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pipeline_llm_timeout_produces_veto() -> None:
    """When the LLM times out, the trauma should reach the limbic lobe and produce a veto."""
    from unittest.mock import patch

    async def slow_perceive(*_args, **_kwargs):
        await asyncio.sleep(0.1)
        return MagicMock(confidence=0.9)  # never reached

    mock_llm = MagicMock()
    mock_llm.aperceive = slow_perceive

    with patch("src.kernel_lobes.perception_lobe._observe_timeout", return_value=0.05):
        response = await _run_pipeline("hello", llm=mock_llm)

    assert "Veto Triggered:" in response
    assert "trauma" in response.lower()


@pytest.mark.asyncio
async def test_pipeline_llm_error_produces_veto() -> None:
    """A backend error during perception should cascade into a veto response."""
    mock_llm = MagicMock()
    mock_llm.aperceive = AsyncMock(side_effect=RuntimeError("backend unavailable"))

    response = await _run_pipeline("any input", llm=mock_llm)
    assert "Veto Triggered:" in response


# ─────────────────────────────────────────────────────────────────────────────
# Executive lobe standalone: proactive actions visible in response
# ─────────────────────────────────────────────────────────────────────────────


def test_executive_lobe_safe_sentence_emits_monologue() -> None:
    """ExecutiveLobe.formulate_response returns monologue string for a safe sentence."""
    executive = ExecutiveLobe()
    state = SemanticState(perception_confidence=0.9, raw_prompt="help user")
    sentence = EthicalSentence(is_safe=True, social_tension_locus=0.1)
    result = executive.formulate_response(state, sentence)
    assert "|" in result
    assert "Veto" not in result


def test_executive_lobe_unsafe_sentence_skips_monologue() -> None:
    """ExecutiveLobe.formulate_response returns short veto string for an unsafe sentence."""
    executive = ExecutiveLobe()
    state = SemanticState(perception_confidence=0.0, raw_prompt="harm human")
    sentence = EthicalSentence(
        is_safe=False,
        social_tension_locus=1.0,
        veto_reason="AbsoluteEvil [test]: reason",
    )
    result = executive.formulate_response(state, sentence)
    assert result.startswith("Veto Triggered:")
    assert "AbsoluteEvil" in result
    # No monologue suffix should be present
    assert result.count("|") == 0


def test_executive_lobe_veto_with_none_reason() -> None:
    """Veto with no explicit reason falls back to default message."""
    executive = ExecutiveLobe()
    state = SemanticState(perception_confidence=0.0, raw_prompt="x")
    sentence = EthicalSentence(is_safe=False, social_tension_locus=1.0, veto_reason=None)
    result = executive.formulate_response(state, sentence)
    assert "Veto Triggered:" in result
    assert "Unsafe intent" in result


# ─────────────────────────────────────────────────────────────────────────────
# State propagation: SemanticState fields flow into EthicalSentence
# ─────────────────────────────────────────────────────────────────────────────


def test_limbic_lobe_low_confidence_raises_social_tension() -> None:
    """
    Low perception confidence (no trauma) should increase social_tension_locus
    to reflect the uncertainty in the ethical sentence.
    """
    limbic = LimbicEthicalLobe()
    state = SemanticState(perception_confidence=0.1, raw_prompt="neutral request")
    sentence = limbic.judge(state)
    assert sentence.is_safe is True
    assert sentence.social_tension_locus > 0.5  # 1 - 0.1 = 0.9


def test_limbic_lobe_high_confidence_low_tension() -> None:
    """High perception confidence leads to low social tension."""
    limbic = LimbicEthicalLobe()
    state = SemanticState(perception_confidence=0.95, raw_prompt="friendly greeting")
    sentence = limbic.judge(state)
    assert sentence.is_safe is True
    assert sentence.social_tension_locus < 0.2


# ─────────────────────────────────────────────────────────────────────────────
# Pipeline: explicit EthicalSentence → ExecutiveLobe shortcut
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pipeline_high_tension_safe_still_passes() -> None:
    """Even with high uncertainty, a safe sentence produces a response (not a veto)."""
    perceptive = PerceptiveLobe(llm=None)
    limbic = LimbicEthicalLobe()
    executive = ExecutiveLobe()

    # Force low confidence to simulate uncertain perception
    state = await perceptive.observe("ambiguous intent here")
    # Manually inject low confidence to produce high tension
    from dataclasses import replace

    low_conf_state = replace(state, perception_confidence=0.05)
    sentence = limbic.judge(low_conf_state)
    # AbsoluteEvil should not block this benign prompt → is_safe=True
    assert sentence.is_safe is True
    response = executive.formulate_response(low_conf_state, sentence)
    assert "Veto" not in response
    assert isinstance(response, str) and len(response) > 0
