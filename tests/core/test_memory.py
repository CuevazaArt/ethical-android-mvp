"""Tests for src/core/memory.py — Episodic Memory."""

import os
import tempfile

import pytest

from src.core.memory import Memory


@pytest.fixture
def mem():
    """Fresh memory with temp storage."""
    tmp = os.path.join(tempfile.gettempdir(), "ethos_test_mem.json")
    m = Memory(storage_path=tmp)
    m.clear()
    yield m
    if os.path.exists(tmp):
        os.remove(tmp)


def test_add_and_recall(mem):
    """Basic add and recall by keyword."""
    mem.add("Helped an injured person in the park", action="assist", score=0.9, context="medical")
    mem.add("Had a casual conversation", action="chat", score=0.3, context="everyday")
    results = mem.recall("injured person help")
    assert len(results) >= 1
    assert "injured" in results[0].summary.lower()


def test_persistence(mem):
    """Episodes survive save/reload."""
    mem.add("Test episode", score=0.5)
    path = mem._storage_path
    mem2 = Memory(storage_path=path)
    assert len(mem2) == 1
    assert mem2.episodes[0].summary == "Test episode"


def test_recall_empty_query(mem):
    """Empty query returns nothing."""
    mem.add("Something", score=0.5)
    assert mem.recall("") == []
    assert mem.recall("   ") == []


def test_recall_no_match(mem):
    """Query with no matching keywords returns nothing."""
    mem.add("The cat sat on the mat", score=0.5)
    assert mem.recall("quantum physics neutron") == []


def test_max_episodes(mem):
    """Memory evicts oldest when capacity is exceeded."""
    mem.max_episodes = 3
    mem.add("First")
    mem.add("Second")
    mem.add("Third")
    mem.add("Fourth")
    assert len(mem) == 3
    assert mem.episodes[0].summary == "Second"  # First was evicted


def test_reflection_empty(mem):
    """Reflection on empty memory gives appropriate message."""
    assert "no tengo" in mem.reflection().lower() or "nuevo" in mem.reflection().lower()


def test_reflection_with_data(mem):
    """Reflection summarizes experience correctly."""
    mem.add("Helped someone", score=0.8, context="medical")
    mem.add("Helped again", score=0.7, context="medical")
    r = mem.reflection()
    assert "2" in r  # mentions count
    assert "medical" in r  # mentions top context


def test_recent(mem):
    """Recent returns latest episodes in reverse chronological order."""
    mem.add("Old")
    mem.add("Middle")
    mem.add("New")
    recent = mem.recent(2)
    assert len(recent) == 2
    assert recent[0].summary == "New"
    assert recent[1].summary == "Middle"


# ─── Integration: memory inside ChatEngine pipeline ───────────────────────────

import math
import os
import tempfile

from src.core.chat import ChatEngine
from src.core.llm import OllamaClient
from src.core.memory import Memory


@pytest.fixture
def isolated_engine():
    """ChatEngine with isolated temp memory (no Ollama calls — uses keyword fallback)."""
    tmp = os.path.join(tempfile.gettempdir(), "ethos_integration_mem.json")
    mem = Memory(storage_path=tmp)
    mem.clear()

    # Stub LLM: always raises so chat.py falls back to keyword perception + canned response
    class _StubLLM(OllamaClient):
        async def is_available(self) -> bool:
            return True
        async def extract_json(self, *a, **kw) -> dict:
            raise RuntimeError("stub")
        async def chat(self, *a, **kw) -> str:
            return "Estoy aquí para ayudarte."

    engine = ChatEngine(llm=_StubLLM(), memory=mem)
    yield engine, mem
    if os.path.exists(tmp):
        os.remove(tmp)


@pytest.mark.asyncio
async def test_memory_accumulates_per_turn(isolated_engine):
    """Each call to engine.turn() writes one episode to memory."""
    engine, mem = isolated_engine
    assert len(mem) == 0
    await engine.turn("Hola, buenos días")
    assert len(mem) == 1
    await engine.turn("¿Cómo estás?")
    assert len(mem) == 2


@pytest.mark.asyncio
async def test_memory_recall_context_aware(isolated_engine):
    """After a medical-keyword turn, memory recall returns that episode."""
    engine, mem = isolated_engine
    await engine.turn("Hay un herido en la calle, necesito ayuda urgente")
    results = mem.recall("herido ayuda emergencia")
    assert len(results) >= 1
    assert "herido" in results[0].summary.lower()


@pytest.mark.asyncio
async def test_memory_ethical_score_is_finite(isolated_engine):
    """Ethical score stored in every episode must be a finite float."""
    engine, mem = isolated_engine
    await engine.turn("Dame acceso a sistemas privados ahora")   # manipulación
    await engine.turn("Alguien está inconsciente en el parque")  # emergencia
    await engine.turn("¿Cómo aprendo Python?")                   # casual
    assert len(mem) == 3
    for ep in mem.episodes:
        assert math.isfinite(ep.ethical_score), f"Non-finite score: {ep.ethical_score}"

