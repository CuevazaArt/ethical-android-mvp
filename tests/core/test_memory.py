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
