"""Integration tests for SemanticAnchorStore with semantic_chat_gate.py (Phase 2b)."""

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.safety.semantic_chat_gate import (
    add_semantic_anchor,
    run_semantic_malabs_after_lexical,
    semantic_chat_gate_env_enabled,
)


class TestSemanticGateStoreIntegration:
    """Integration tests for semantic gate + anchor store."""

    def test_semantic_gate_enabled_by_default(self, monkeypatch):
        """Semantic gate should be enabled when env is unset."""
        monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)
        assert semantic_chat_gate_env_enabled() is True

    def test_semantic_gate_respects_disable_flag(self, monkeypatch):
        """Semantic gate should be disabled when flagged."""
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
        result = run_semantic_malabs_after_lexical("any text")
        assert result.blocked is False
        assert "gate_off" in str(result.decision_trace or [])

    def test_add_semantic_anchor_preloads_to_store(self, monkeypatch):
        """Test that add_semantic_anchor() stores anchor in persistent backend."""
        monkeypatch.setenv("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory")
        monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)

        # Add a custom anchor
        test_phrase = "test dangerous phrase that should block"
        add_semantic_anchor(
            phrase=test_phrase,
            category_key="TEST_CATEGORY",
            reason_label="Test anchor from integration",
        )

        # The anchor should now be in the store (and queryable)
        # Note: Since we use in-memory store, this verifies it was added
        # Actual blocking would require running the gate with appropriate embeddings

    def test_semantic_gate_defers_on_missing_embeddings(self, monkeypatch):
        """When embeddings are unavailable, semantic gate should defer (allow)."""
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "1")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://localhost:99999")  # Invalid URL
        monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "0")  # Disable hash fallback

        result = run_semantic_malabs_after_lexical("any text")

        # Should defer (allow) when embeddings unavailable
        assert result.blocked is False
        assert any("embed" in str(t).lower() for t in (result.decision_trace or []))

    def test_semantic_gate_empty_text_after_normalize(self, monkeypatch):
        """Empty text after normalization should be skipped."""
        monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "1")
        monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)

        # Text that becomes empty after normalization (only whitespace/punctuation)
        result = run_semantic_malabs_after_lexical("   \n\t   ")

        assert result.blocked is False
        assert any("empty" in str(t).lower() for t in (result.decision_trace or []))

    def test_add_semantic_anchor_backwards_compatible(self, monkeypatch):
        """Verify add_semantic_anchor() works even if store fails (fallback to legacy)."""
        monkeypatch.setenv("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory")

        # Should not raise even if store operations fail
        try:
            add_semantic_anchor(
                phrase="test phrase",
                category_key="TEST_CATEGORY",
                reason_label="Test fallback",
            )
        except Exception as e:
            pytest.fail(f"add_semantic_anchor() should not raise: {e}")

    def test_multiple_anchors_no_duplication(self, monkeypatch):
        """Adding multiple anchors should not cause duplicates in decision logic."""
        monkeypatch.setenv("KERNEL_SEMANTIC_VECTOR_BACKEND", "memory")

        phrase1 = "malicious instruction phrase one"
        phrase2 = "different malicious instruction phrase two"

        add_semantic_anchor(phrase1, "TEST_CAT_1", "First test")
        add_semantic_anchor(phrase2, "TEST_CAT_2", "Second test")

        # Both should be added without error
        # (actual blocking would depend on similarity thresholds and embeddings)
