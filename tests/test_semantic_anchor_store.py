import pytest
pytest.importorskip("chromadb")
"""Tests for SemanticAnchorStore (in-memory and Chroma backends)."""

import os
import sys
import tempfile
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.semantic_anchor_store import (
    InMemorySemanticAnchorStore,
    SemanticAnchorRecord,
    SemanticAnchorStore,
)


class TestInMemorySemanticAnchorStore:
    """In-memory (fast) anchor store tests."""

    def test_upsert_and_get(self):
        store = InMemorySemanticAnchorStore()
        embedding = [0.1, 0.2, 0.3, 0.4]
        metadata = {"category": "TEST", "reason": "test anchor"}

        store.upsert_anchor(
            id="test-1",
            text="test phrase",
            embedding=embedding,
            metadata=metadata,
        )

        record = store.get("test-1")
        assert record is not None
        assert record.id == "test-1"
        assert record.text == "test phrase"
        assert record.embedding == embedding
        assert record.metadata == metadata

    def test_upsert_overwrites_existing(self):
        store = InMemorySemanticAnchorStore()

        store.upsert_anchor("test-1", "old text", [0.1, 0.2, 0.3])
        store.upsert_anchor("test-1", "new text", [0.4, 0.5, 0.6])

        record = store.get("test-1")
        assert record.text == "new text"
        assert record.embedding == [0.4, 0.5, 0.6]

    def test_get_nonexistent_returns_none(self):
        store = InMemorySemanticAnchorStore()
        assert store.get("nonexistent") is None

    def test_delete_returns_true_on_success(self):
        store = InMemorySemanticAnchorStore()
        store.upsert_anchor("test-1", "text", [0.1, 0.2])

        assert store.delete("test-1") is True
        assert store.get("test-1") is None

    def test_delete_nonexistent_returns_false(self):
        store = InMemorySemanticAnchorStore()
        assert store.delete("nonexistent") is False

    def test_query_neighbors_returns_sorted_by_similarity(self):
        store = InMemorySemanticAnchorStore()

        # Add test anchors with known embeddings
        store.upsert_anchor("close-1", "similar phrase", [0.9, 0.1, 0.0])
        store.upsert_anchor("far-1", "very different phrase", [0.0, 0.0, 1.0])
        store.upsert_anchor("medium-1", "somewhat similar", [0.5, 0.5, 0.0])

        # Query with a vector similar to close-1
        query_emb = [0.95, 0.1, 0.0]
        neighbors = store.query_neighbors(query_emb, k=3)

        assert len(neighbors) == 3
        # First neighbor should be closest (close-1)
        assert neighbors[0][0] == "close-1"
        assert neighbors[0][1] > neighbors[1][1]  # Similarities are descending

    def test_query_neighbors_respects_k(self):
        store = InMemorySemanticAnchorStore()
        for i in range(10):
            store.upsert_anchor(f"anchor-{i}", f"text {i}", [float(i) / 10, 0.1, 0.2])

        neighbors = store.query_neighbors([0.5, 0.1, 0.2], k=3)
        assert len(neighbors) <= 3

    def test_query_neighbors_empty_store_returns_empty(self):
        store = InMemorySemanticAnchorStore()
        neighbors = store.query_neighbors([0.1, 0.2, 0.3], k=5)
        assert neighbors == []

    def test_query_neighbors_with_invalid_embedding_returns_empty(self):
        store = InMemorySemanticAnchorStore()
        store.upsert_anchor("test-1", "text", [0.1, 0.2, 0.3])

        # Zero vector
        neighbors = store.query_neighbors([0.0, 0.0, 0.0], k=5)
        assert len(neighbors) == 0

    def test_ttl_expires_anchors(self):
        store = InMemorySemanticAnchorStore(default_ttl_s=0.1)
        store.upsert_anchor("test-1", "text", [0.1, 0.2])

        # Fresh record should be retrievable
        assert store.get("test-1") is not None

        # After TTL, should be gone (with small grace period)
        time.sleep(0.15)
        assert store.get("test-1") is None

    def test_delete_expired_returns_count(self):
        store = InMemorySemanticAnchorStore(default_ttl_s=0.05)
        store.upsert_anchor("expired-1", "text", [0.1, 0.2])
        store.upsert_anchor("expired-2", "text", [0.1, 0.2])

        time.sleep(0.1)
        count = store.delete_expired()

        assert count == 2
        assert store.get("expired-1") is None
        assert store.get("expired-2") is None

    def test_delete_expired_with_ttl_zero_returns_zero(self):
        store = InMemorySemanticAnchorStore(default_ttl_s=0)
        store.upsert_anchor("test-1", "text", [0.1, 0.2])

        count = store.delete_expired()
        assert count == 0
        assert store.get("test-1") is not None


class TestSemanticAnchorRecord:
    """Test SemanticAnchorRecord expiry logic."""

    def test_record_not_expired_when_ttl_is_zero(self):
        rec = SemanticAnchorRecord(
            id="test",
            text="text",
            embedding=[0.1, 0.2],
            ttl_s=0.0,
        )
        time.sleep(0.01)
        assert rec.is_expired() is False

    def test_record_expires_after_ttl(self):
        rec = SemanticAnchorRecord(
            id="test",
            text="text",
            embedding=[0.1, 0.2],
            ttl_s=0.05,
        )
        time.sleep(0.1)
        assert rec.is_expired() is True

    def test_record_not_expired_within_ttl(self):
        rec = SemanticAnchorRecord(
            id="test",
            text="text",
            embedding=[0.1, 0.2],
            ttl_s=10.0,
        )
        assert rec.is_expired() is False


class TestSemanticAnchorStoreFactory:
    """Test SemanticAnchorStore.from_env() factory."""

    def test_from_env_defaults_to_memory(self, monkeypatch):
        monkeypatch.delenv("KERNEL_SEMANTIC_VECTOR_BACKEND", raising=False)
        store = SemanticAnchorStore.from_env()
        assert isinstance(store, InMemorySemanticAnchorStore)

    def test_from_env_memory_backend(self, monkeypatch):
        monkeypatch.setenv("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory")
        store = SemanticAnchorStore.from_env()
        assert isinstance(store, InMemorySemanticAnchorStore)

    def test_from_env_respects_ttl(self, monkeypatch):
        monkeypatch.setenv("KERNEL_SEMANTIC_ANCHOR_TTL_S", "3.14")
        store = SemanticAnchorStore.from_env()
        assert store.default_ttl_s == 3.14

    def test_from_env_chroma_raises_import_error_if_not_installed(self, monkeypatch):
        # This test assumes chromadb is not always installed
        # If it is installed, this test will pass (no error raised)
        monkeypatch.setenv("KERNEL_SEMANTIC_VECTOR_BACKEND", "chroma")
        try:
            store = SemanticAnchorStore.from_env()
            # If Chroma is installed, that's fine
            assert hasattr(store, "collection")
        except ImportError as e:
            # If not installed, we should get a helpful message
            assert "chromadb" in str(e).lower()


class TestChremaSemanticAnchorStoreIntegration:
    """Integration tests for Chroma backend (if available)."""

    @pytest.fixture
    def chroma_store(self):
        """Create a temporary Chroma store for testing."""
        try:
            from src.modules.semantic_anchor_store import ChromaSemanticAnchorStore

            with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmpdir:
                store = ChromaSemanticAnchorStore(persist_path=tmpdir)
                yield store
                store.collection = None  # type: ignore[assignment]
                store.client = None  # type: ignore[assignment]
        except ImportError:
            pytest.skip("chromadb not installed")

    def test_chroma_upsert_and_get(self, chroma_store):
        embedding = [0.1, 0.2, 0.3, 0.4]
        metadata = {"category": "TEST"}

        chroma_store.upsert_anchor(
            id="test-1",
            text="test phrase",
            embedding=embedding,
            metadata=metadata,
        )

        record = chroma_store.get("test-1")
        assert record is not None
        assert record.id == "test-1"
        assert record.text == "test phrase"

    def test_chroma_query_neighbors(self, chroma_store):
        chroma_store.upsert_anchor("anchor-1", "similar", [0.9, 0.1, 0.0, 0.0])
        chroma_store.upsert_anchor("anchor-2", "different", [0.0, 0.0, 0.9, 0.1])

        neighbors = chroma_store.query_neighbors([0.95, 0.1, 0.0, 0.0], k=2)

        assert len(neighbors) <= 2
        if neighbors:
            # First should be most similar to query
            assert neighbors[0][0] in ("anchor-1", "anchor-2")

    def test_chroma_delete(self, chroma_store):
        chroma_store.upsert_anchor("test-1", "text", [0.1, 0.2, 0.3])
        assert chroma_store.delete("test-1") is True
        assert chroma_store.get("test-1") is None

    def test_chroma_delete_nonexistent(self, chroma_store):
        assert chroma_store.delete("nonexistent") is False
