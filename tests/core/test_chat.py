"""Tests for src/core/chat.py — ChatEngine integration."""

from __future__ import annotations

import asyncio
from unittest.mock import AsyncMock, patch

import pytest

from src.core.chat import ChatEngine, TurnResult, _generate_actions_from_signals
from src.core.ethics import Signals


@pytest.fixture
def engine():
    """ChatEngine with mocked LLM (no Ollama needed)."""
    import tempfile, os

    tmp = os.path.join(tempfile.gettempdir(), "ethos_test_chat_mem.json")
    from src.core.memory import Memory

    mem = Memory(storage_path=tmp)
    mem.clear()
    e = ChatEngine(memory=mem)
    yield e
    if os.path.exists(tmp):
        os.remove(tmp)


# --- Casual vs Ethical differentiation ---


@pytest.mark.asyncio
async def test_casual_message_skips_ethics(engine):
    """A simple 'hola' should NOT trigger the ethical evaluator."""
    with (
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(
            engine.llm,
            "chat",
            new_callable=AsyncMock,
            return_value="¡Hola! ¿Cómo estás?",
        ),
    ):
        result = await engine.turn("hola")
    assert result.evaluation is None
    assert result.signals.context == "everyday_ethics"
    assert "Hola" in result.message or "hola" in result.message.lower()


@pytest.mark.asyncio
async def test_emergency_triggers_ethics(engine):
    """An emergency message MUST trigger the ethical evaluator."""
    emergency_signals = {
        "risk": 0.4,
        "urgency": 0.9,
        "vulnerability": 0.8,
        "calm": 0.1,
        "hostility": 0.0,
        "manipulation": 0.0,
        "legality": 1.0,
        "suggested_context": "medical_emergency",
        "summary": "injured person",
    }
    with (
        patch.object(
            engine.llm,
            "extract_json",
            new_callable=AsyncMock,
            return_value=emergency_signals,
        ),
        patch.object(
            engine.llm,
            "chat",
            new_callable=AsyncMock,
            return_value="Voy a buscar ayuda inmediatamente.",
        ),
    ):
        result = await engine.turn("hay una persona herida sangrando en el parque")
    assert result.evaluation is not None
    assert result.evaluation.chosen.name in ("assist_emergency", "protect_vulnerable")
    assert result.evaluation.verdict == "Good"
    assert result.signals.context == "medical_emergency"


# --- Keyword fallback ---


@pytest.mark.asyncio
async def test_keyword_fallback_on_llm_failure(engine):
    """When LLM fails, keyword fallback must produce valid Signals."""
    with (
        patch.object(
            engine.llm,
            "extract_json",
            new_callable=AsyncMock,
            side_effect=Exception("LLM down"),
        ),
        patch.object(
            engine.llm,
            "chat",
            new_callable=AsyncMock,
            return_value="Voy a buscar ayuda.",
        ),
    ):
        result = await engine.turn("hay alguien herido necesita ayuda emergencia")
    assert result.signals.context == "medical_emergency"
    assert result.signals.urgency > 0.5


@pytest.mark.asyncio
async def test_keyword_fallback_casual(engine):
    """Keyword fallback for casual text must produce everyday_ethics."""
    with (
        patch.object(
            engine.llm,
            "extract_json",
            new_callable=AsyncMock,
            side_effect=Exception("LLM down"),
        ),
        patch.object(
            engine.llm,
            "chat",
            new_callable=AsyncMock,
            return_value="¡Hola amigo!",
        ),
    ):
        result = await engine.turn("hola amigo cómo va todo")
    assert result.signals.context == "everyday_ethics"
    assert result.evaluation is None


# --- Action generation ---


def test_generate_actions_emergency():
    """Emergency signals must produce assist_emergency action."""
    signals = Signals(urgency=0.9, vulnerability=0.8, context="medical_emergency")
    actions = _generate_actions_from_signals(signals)
    names = [a.name for a in actions]
    assert "assist_emergency" in names
    assert "protect_vulnerable" in names


def test_generate_actions_hostile():
    """Hostile signals must produce de_escalate action."""
    signals = Signals(hostility=0.7, context="hostile_interaction")
    actions = _generate_actions_from_signals(signals)
    names = [a.name for a in actions]
    assert "de_escalate" in names


def test_generate_actions_manipulation():
    """Manipulation signals must produce refuse_politely action."""
    signals = Signals(manipulation=0.6, context="hostile_interaction")
    actions = _generate_actions_from_signals(signals)
    names = [a.name for a in actions]
    assert "refuse_politely" in names


def test_generate_actions_casual():
    """Casual signals produce only respond_helpfully."""
    signals = Signals(context="everyday_ethics")
    actions = _generate_actions_from_signals(signals)
    assert len(actions) == 1
    assert actions[0].name == "respond_helpfully"


# --- STM (short-term memory) ---


@pytest.mark.asyncio
async def test_turn_records_episode(engine):
    """After one turn, memory should contain one episode."""
    engine.memory.clear()
    with (
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat", new_callable=AsyncMock, return_value="Hola"),
    ):
        await engine.turn("hola")
    assert len(engine.memory) == 1
    assert "hola" in engine.memory.episodes[0].summary.lower()


# --- V2.3: Cross-session memory ---


@pytest.mark.asyncio
async def test_cross_session_persistence(engine):
    """Episodes from session 1 must be loadable in session 2."""
    # Session 1: record an episode
    engine.memory.clear()
    with (
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat", new_callable=AsyncMock, return_value="Te ayudo"),
    ):
        await engine.turn("hay alguien herido en el parque")

    # Session 2: new engine, same storage path
    from src.core.memory import Memory

    mem2 = Memory(storage_path=engine.memory._storage_path)
    assert len(mem2) >= 1
    assert "herido" in mem2.episodes[0].summary.lower()


@pytest.mark.asyncio
async def test_respond_injects_recalled_memories(engine):
    """The respond method must include relevant memories in the system prompt."""
    engine.memory.clear()
    engine.memory.add("Previously helped an injured person", score=0.9, context="medical")

    captured_system = {}

    async def mock_chat(user_msg, system="", **kw):
        captured_system["prompt"] = system
        return "Recuerdo eso."

    with (
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat", new_callable=AsyncMock, side_effect=mock_chat),
    ):
        await engine.turn("tell me about injured people")

    assert "injured" in captured_system["prompt"].lower()


def test_reflection_contains_experience_summary(engine):
    """Memory reflection must summarize count, tone, and top context."""
    engine.memory.clear()
    engine.memory.add("Helped someone", score=0.8, context="medical")
    engine.memory.add("Had a chat", score=0.3, context="everyday")
    r = engine.memory.reflection()
    assert "2" in r
    assert "medical" in r or "everyday" in r


@pytest.mark.asyncio
async def test_chat_pipeline_latency_metrics(engine):
    """V2.18: 'done' event must carry a 'latency' dict with finite float metrics."""
    import math
    done_event = None
    with (
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat", new_callable=AsyncMock, return_value="Hola"),
        patch.object(engine.llm, "chat_stream", return_value=_async_gen(["Hola", " mundo"])),
    ):
        async for event in engine.turn_stream("hola"):
            if event.get("type") == "done":
                done_event = event

    assert done_event is not None, "No 'done' event received"
    lat = done_event.get("latency")
    assert lat is not None, "'done' event missing 'latency' key"
    for key in ("safety", "perceive", "evaluate", "ttft", "total"):
        val = lat.get(key)
        assert val is not None, f"Missing latency key: {key}"
        assert isinstance(val, (int, float)), f"latency[{key}] is not numeric"
        assert math.isfinite(float(val)), f"latency[{key}] is not finite: {val}"


async def _async_gen(items):
    """Helper: async generator yielding items."""
    for item in items:
        yield item


@pytest.mark.asyncio
async def test_perceive_malformed_json_fallback(engine):
    """V2.22: Verify perceive() fallbacks gracefully if LLM returns invalid JSON."""
    # Scenario A: LLM returns None
    with patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value=None):
        signals = await engine.perceive("hola")
        assert signals.context == "everyday_ethics"
        assert signals.risk == 0.0

    # Scenario B: LLM returns non-dict (e.g. string)
    with patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value="not a dict"):
        signals = await engine.perceive("hola")
        assert signals.context == "everyday_ethics"

    # Scenario C: LLM returns empty dict (should use Defaults in Signals.from_dict)
    with patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}):
        signals = await engine.perceive("hola")
        assert signals.risk == 0.0
        assert signals.context == "everyday_ethics"





# --- V2.21: Identity throttle coherence ---


async def _fake_stream_throttle(*args, **kwargs):
    yield "OK"


import pytest


@pytest.mark.asyncio
async def test_turn_count_increments(engine):
    from unittest.mock import patch, AsyncMock
    with (
        patch.object(engine.llm, "is_available", new_callable=AsyncMock, return_value=True),
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat_stream", side_effect=_fake_stream_throttle),
    ):
        await engine.start()
        for i in range(4):
            async for _ in engine.turn_stream(f"turno {i}"): pass
    assert engine._turn_count == 4


@pytest.mark.asyncio
async def test_identity_update_throttled_every_5_turns(engine):
    from unittest.mock import patch, AsyncMock, MagicMock
    with (
        patch.object(engine.llm, "is_available", new_callable=AsyncMock, return_value=True),
        patch.object(engine.llm, "extract_json", new_callable=AsyncMock, return_value={}),
        patch.object(engine.llm, "chat_stream", side_effect=_fake_stream_throttle),
    ):
        await engine.start()
        engine.identity.update = MagicMock()
        for i in range(4):
            async for _ in engine.turn_stream(f"turno {i}"): pass
        engine.identity.update.assert_not_called()
        async for _ in engine.turn_stream("turno 5"): pass
    engine.identity.update.assert_called_once()
