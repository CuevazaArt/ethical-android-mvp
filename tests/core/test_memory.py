"""Tests for src/core/memory.py — Episodic Memory."""

import os
import tempfile

import pytest

from src.core.memory import Memory


@pytest.fixture
def mem():
    """Fresh memory with temp storage (unique file per test — Windows-safe)."""
    tmp = tempfile.mktemp(suffix=".json", prefix="ethos_test_mem_")
    m = Memory(storage_path=tmp)
    m.clear()
    yield m
    try:
        if os.path.exists(tmp):
            os.remove(tmp)
    except PermissionError:
        pass  # Windows: file still locked by GC — benign, temp dir is cleaned up anyway


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
async def isolated_engine():
    """ChatEngine with isolated temp memory (no Ollama calls — uses keyword fallback)."""
    tmp = os.path.join(tempfile.gettempdir(), "ethos_integration_mem.json")
    mem = Memory(storage_path=tmp)
    mem.clear()

    # Stub LLM: extract_json raises → keyword fallback; chat returns canned string
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


def test_memory_persistence_with_identity(mem):
    import json
    # Add episodes and change identity
    mem.add("Test", score=0.5)
    mem.identity = "Nueva identidad test"
    mem.save()
    
    # Verify structure on disk
    with open(mem._storage_path, encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, dict)
    assert data["identity"] == "Nueva identidad test"
    assert len(data["episodes"]) == 1
    
    # Reload
    mem2 = Memory(storage_path=mem._storage_path)
    assert mem2.identity == "Nueva identidad test"
    assert len(mem2) == 1

def test_memory_legacy_migration(mem):
    import json
    # Create a legacy flat list structure
    legacy_data = [{"summary": "Legacy 1", "action": "test", "ethical_score": 0.5, "context": "everyday"}]
    with open(mem._storage_path, "w", encoding="utf-8") as f:
        json.dump(legacy_data, f)
        
    # Load and verify it migrated transparently
    mem2 = Memory(storage_path=mem._storage_path)
    assert len(mem2) == 1
    assert mem2.episodes[0].summary == "Legacy 1"
    # Identity should be the default
    assert "ética cívica" in mem2.identity


# ─── V2.16: TF-IDF Semantic Recall ──────────────────────────────────────────


def test_tfidf_recall_finds_semantic_match(mem):
    """TF-IDF recall surfaces the most relevant episode for a related query."""
    mem.add("El usuario preguntó sobre el clima hoy", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Se discutió el horario del transporte público", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Pregunta sobre recetas de cocina vegetariana", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Conversación sobre películas de ciencia ficción", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Conversación sobre deportes y fútbol", action="casual_chat", score=0.3, context="everyday_ethics")
    # Target: medical episode
    mem.add("Encontré a una persona herida que necesitaba atención médica urgente",
            action="assist_emergency", score=0.9, context="medical_emergency")
    mem.add("El usuario preguntó sobre libros de historia", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Conversación sobre viajes y turismo", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Discusión sobre tecnología y smartphones", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Pregunta sobre cine y televisión", action="casual_chat", score=0.3, context="everyday_ethics")

    results = mem.recall("persona herida atención médica", limit=3)
    assert len(results) >= 1
    top_summaries = [ep.summary for ep in results]
    assert any("herida" in s.lower() or "médica" in s.lower() for s in top_summaries)


def test_tfidf_score_finite(mem):
    """All TF-IDF scores must be finite floats."""
    for i in range(8):
        mem.add(f"Episodio de prueba número {i}", action="casual_chat", score=0.5, context="everyday_ethics")
    idf = mem._build_idf()
    for ep in mem.episodes:
        score = ep.matches_tfidf(["prueba", "episodio"], idf)
        assert math.isfinite(score), f"Non-finite TF-IDF score: {score}"


def test_tfidf_fallback_small_corpus(mem):
    """With < 5 episodes, recall() uses keyword fallback without crashing."""
    mem.add("Ayudé a alguien", action="assist_emergency", score=0.9, context="medical_emergency")
    mem.add("Conversación casual", action="casual_chat", score=0.3, context="everyday_ethics")
    mem.add("Otro episodio más", action="casual_chat", score=0.4, context="everyday_ethics")
    results = mem.recall("ayudé alguien")
    assert isinstance(results, list)
    assert len(results) >= 1


def test_tfidf_idf_cache_invalidated_on_add(mem):
    """After add(), _idf_cache must be None."""
    for i in range(6):
        mem.add(f"Episodio {i}", action="casual_chat", score=0.5, context="everyday_ethics")
    _ = mem._build_idf()
    assert mem._idf_cache is not None
    mem.add("Nuevo episodio", action="casual_chat", score=0.5, context="everyday_ethics")
    assert mem._idf_cache is None


def test_recall_empty_query_tfidf(mem):
    """recall() with empty or whitespace-only query always returns [] even with large corpus."""
    for i in range(6):
        mem.add(f"Episodio {i}", action="casual_chat", score=0.5, context="everyday_ethics")
    assert mem.recall("") == []
    assert mem.recall("   ") == []
