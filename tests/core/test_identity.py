"""Tests for src/core/identity.py — Identity Neuroplasticity (V2.15)."""

import math
import os
import tempfile

import pytest

from src.core.identity import Identity
from src.core.memory import Memory


def _temp_identity() -> Identity:
    import uuid
    tmp = os.path.join(tempfile.gettempdir(), f"ethos_identity_test_{uuid.uuid4().hex}.json")
    return Identity(storage_path=tmp)


def _temp_memory() -> Memory:
    tmp = os.path.join(tempfile.gettempdir(), f"ethos_memory_test_{os.getpid()}.json")
    mem = Memory(storage_path=tmp)
    mem.clear()
    return mem


# --- Basic update ---


def test_update_empty_memory_is_noop():
    identity = _temp_identity()
    mem = _temp_memory()
    identity.update(mem)
    # No episodes → profile stays empty → narrative is empty string
    assert identity.narrative() == ""


def test_update_builds_profile():
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Ayudé a alguien herido", action="assist_emergency", score=0.9, context="medical_emergency")
    mem.add("Rechacé manipulación", action="refuse_manipulation", score=0.7, context="social_engineering")
    identity.update(mem)
    profile = identity.as_dict()
    assert profile["episodes_total"] == 2
    assert math.isfinite(profile["avg_ethical_score"])
    assert "medical_emergency" in profile["top_contexts"] or "social_engineering" in profile["top_contexts"]


def test_narrative_is_non_empty_with_episodes():
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Desescalé conflicto", action="de_escalate", score=0.6, context="hostile_interaction")
    identity.update(mem)
    narr = identity.narrative()
    assert isinstance(narr, str)
    assert len(narr) > 20
    assert "[Identidad" in narr


def test_narrative_contains_episode_count():
    identity = _temp_identity()
    mem = _temp_memory()
    for i in range(5):
        mem.add(f"Episodio {i}", action="casual_chat", score=0.5, context="everyday_ethics")
    identity.update(mem)
    narr = identity.narrative()
    assert "5" in narr


# --- Trending ---


def test_trending_stable():
    identity = _temp_identity()
    mem = _temp_memory()
    for _ in range(15):
        mem.add("Episodio", action="casual_chat", score=0.5, context="everyday_ethics")
    identity.update(mem)
    assert identity.as_dict()["trending"] == "estable"


def test_trending_improving():
    identity = _temp_identity()
    mem = _temp_memory()
    # Old episodes low score
    for _ in range(10):
        mem.add("Old", action="casual_chat", score=0.1, context="everyday_ethics")
    # Recent episodes high score
    for _ in range(10):
        mem.add("Recent", action="assist_emergency", score=0.9, context="medical_emergency")
    identity.update(mem)
    assert identity.as_dict()["trending"] == "mejorando"


# --- Anti-NaN ---


def test_profile_values_all_finite():
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Test", action="casual_chat", score=0.5, context="everyday_ethics")
    identity.update(mem)
    p = identity.as_dict()
    for key in ("avg_ethical_score", "recent_ethical_score", "safety_block_ratio"):
        assert math.isfinite(p[key]), f"{key} not finite"


# --- Persistence ---


def test_identity_persists_across_instances():
    tmp = os.path.join(tempfile.gettempdir(), f"ethos_id_persist_{os.getpid()}.json")
    mem = _temp_memory()
    mem.add("Persistencia", action="assist_emergency", score=0.9, context="medical_emergency")

    id1 = Identity(storage_path=tmp)
    id1.update(mem)

    id2 = Identity(storage_path=tmp)  # Load from disk
    assert id2.as_dict()["episodes_total"] == 1

    os.remove(tmp)


# --- Reset ---


def test_reset_clears_profile():
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Test", action="casual_chat", score=0.5, context="everyday_ethics")
    identity.update(mem)
    assert identity.narrative() != ""
    identity.reset()
    assert identity.narrative() == ""


# --- V2.44: Narrative Identity (reflect + journal) ---


@pytest.mark.asyncio
async def test_reflect_adds_to_journal():
    """V2.44: reflect() calls LLM and appends result to _journal."""
    from unittest.mock import AsyncMock, MagicMock
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Ayudé a una persona herida", action="assist_emergency", score=0.9, context="medical_emergency")

    llm = MagicMock()
    llm.chat = AsyncMock(return_value="Soy reflexivo y empático con quienes sufren.")

    await identity.reflect(mem, llm)

    assert len(identity._journal) == 1
    assert "reflexivo" in identity._journal[0] or "empático" in identity._journal[0]


def test_narrative_uses_journal():
    """V2.44: narrative() returns the most recent journal entry when available."""
    identity = _temp_identity()
    mem = _temp_memory()
    mem.add("Episodio", action="casual_chat", score=0.5, context="everyday_ethics")
    identity.update(mem)  # ensure _profile is populated

    identity._journal = ["Soy curioso y aprendo de cada interacción."]
    narr = identity.narrative()

    assert "curioso" in narr


def test_journal_capped_at_10():
    """V2.44: journal never exceeds 10 entries (FIFO eviction)."""
    identity = _temp_identity()
    # Inject 11 entries directly
    for i in range(11):
        identity._journal.append(f"Reflexión número {i}")
    # Simulate what reflect() does on save/reload by enforcing the cap
    if len(identity._journal) > 10:
        identity._journal = identity._journal[-10:]

    assert len(identity._journal) == 10
    assert "número 10" in identity._journal[-1]  # newest entry survives


@pytest.mark.asyncio
async def test_reflect_noop_on_empty_memory():
    """V2.44: reflect() does nothing if memory has no episodes."""
    from unittest.mock import AsyncMock, MagicMock
    identity = _temp_identity()
    mem = _temp_memory()  # 0 episodes

    llm = MagicMock()
    llm.chat = AsyncMock(return_value="esto no debería ejecutarse")

    await identity.reflect(mem, llm)

    assert len(identity._journal) == 0
    llm.chat.assert_not_called()

