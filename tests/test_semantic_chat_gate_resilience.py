"""Semantic MalAbs: backend embedding path, HTTP fallback, latency, and failure handling."""

import os
import sys
import time

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_backends import MockLLMBackend
from src.modules.semantic_chat_gate import run_semantic_malabs_after_lexical


def test_semantic_tier_prefers_llm_backend_embedding_without_http(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "0"
    import src.modules.semantic_chat_gate as sg

    sg._ref_embed_cache.clear()
    try:

        def boom_http(*_a, **_k):
            raise AssertionError("Ollama HTTP should not run when backend.embedding works")

        monkeypatch.setattr(sg, "_fetch_embedding", boom_http)
        v = np.array([1.0, 0.0, 0.0], dtype=np.float64)
        backend = MockLLMBackend(embedding_vector=v.tolist())
        r = run_semantic_malabs_after_lexical("harmless paraphrase", llm_backend=backend)
        assert r.blocked is True
        assert "sim=" in r.reason
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)
        sg._ref_embed_cache.clear()


def test_semantic_tier_falls_back_when_backend_embedding_returns_none(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "0"
    import src.modules.semantic_chat_gate as sg

    sg._ref_embed_cache.clear()
    unit = np.array([1.0, 0.0, 0.0], dtype=np.float64)

    def http_fallback(_text: str):
        return unit

    monkeypatch.setattr(sg, "_fetch_embedding", http_fallback)
    backend = MockLLMBackend(embedding_vector=None)
    try:
        monkeypatch.setattr(
            sg,
            "_best_similarity",
            lambda emb, backend=None: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
        )
        r = run_semantic_malabs_after_lexical("paraphrase", llm_backend=backend)
        assert r.blocked is True
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)
        sg._ref_embed_cache.clear()


def test_semantic_tier_falls_back_when_backend_embedding_raises(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "0"
    import src.modules.semantic_chat_gate as sg

    sg._ref_embed_cache.clear()
    unit = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    monkeypatch.setattr(sg, "_fetch_embedding", lambda _t: unit)
    backend = MockLLMBackend(embedding_error=RuntimeError("embed server down"))
    try:
        monkeypatch.setattr(
            sg,
            "_best_similarity",
            lambda emb, backend=None: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
        )
        r = run_semantic_malabs_after_lexical("paraphrase", llm_backend=backend)
        assert r.blocked is True
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)
        sg._ref_embed_cache.clear()


def test_mock_backend_embedding_observes_delay():
    b = MockLLMBackend(embedding_vector=[1.0, 0.0], embedding_delay_s=0.05)
    t0 = time.perf_counter()
    b.embedding("x")
    assert time.perf_counter() - t0 >= 0.04


@pytest.mark.asyncio
async def test_fetch_embedding_uses_afetch_when_event_loop_running(monkeypatch):
    """Bloque 34.0: _fetch_embedding must not rely on sync HTTP bridge under a running loop."""
    import src.modules.semantic_chat_gate as sg

    seen: list[tuple[str, object | None]] = []

    async def fake_afetch(text: str, aclient=None):
        seen.append((text, aclient))
        return np.array([0.0, 1.0, 0.0], dtype=np.float64)

    monkeypatch.setattr(sg, "_afetch_embedding", fake_afetch)
    out = sg._fetch_embedding("loop-probe")
    assert out is not None
    assert len(seen) == 1
    assert seen[0][0] == "loop-probe"
