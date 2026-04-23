"""Embedding HTTP policy: circuit breaker, stats, hash fallback."""

import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules import semantic_embedding_client as sec
from src.modules.llm_http_cancel import (
    LLMHttpCancelledError,
    clear_llm_cancel_scope,
    set_llm_cancel_scope,
)


def test_hash_scoped_embedding_is_unit_norm():
    a = sec.hash_scoped_unit_embedding("hello", dim=64)
    b = sec.hash_scoped_unit_embedding("hello", dim=64)
    c = sec.hash_scoped_unit_embedding("other", dim=64)
    assert a is not None and b is not None and c is not None
    import numpy as np

    assert abs(float(np.linalg.norm(a)) - 1.0) < 1e-6
    assert np.allclose(a, b)
    assert not np.allclose(a, c)


def test_circuit_opens_after_failures(monkeypatch):
    sec.reset_embedding_transport_stats_for_tests()
    os.environ["KERNEL_SEMANTIC_EMBED_CIRCUIT_FAILURES"] = "2"
    os.environ["KERNEL_SEMANTIC_EMBED_CIRCUIT_COOLDOWN_S"] = "30"
    os.environ["KERNEL_SEMANTIC_EMBED_RETRIES"] = "0"
    try:

        def boom(*a, **k):
            raise OSError("down")

        monkeypatch.setattr(sec, "_post_once", boom)
        v = sec.http_fetch_ollama_embedding_with_policy("http://x", "m", "t")
        assert v is None
        v2 = sec.http_fetch_ollama_embedding_with_policy("http://x", "m", "t")
        assert v2 is None
        st = sec.get_embedding_transport_stats()
        assert st["consecutive_failures"] >= 2
        assert st["circuit_open_until_monotonic"] > 0
    finally:
        os.environ.pop("KERNEL_SEMANTIC_EMBED_CIRCUIT_FAILURES", None)
        os.environ.pop("KERNEL_SEMANTIC_EMBED_CIRCUIT_COOLDOWN_S", None)
        os.environ.pop("KERNEL_SEMANTIC_EMBED_RETRIES", None)
        sec.reset_embedding_transport_stats_for_tests()


def test_http_embedding_raises_cooperative_cancel_when_scope_set() -> None:
    pytest.importorskip("httpx")
    sec.reset_embedding_transport_stats_for_tests()
    os.environ["KERNEL_SEMANTIC_EMBED_RETRIES"] = "0"
    try:
        ev = threading.Event()
        ev.set()
        set_llm_cancel_scope(ev)
        try:
            with pytest.raises(LLMHttpCancelledError):
                sec.http_fetch_ollama_embedding_with_policy("http://unused", "m", "p")
        finally:
            clear_llm_cancel_scope()
    finally:
        os.environ.pop("KERNEL_SEMANTIC_EMBED_RETRIES", None)
        sec.reset_embedding_transport_stats_for_tests()


async def test_async_http_embedding_raises_cooperative_cancel_when_scope_set() -> None:
    pytest.importorskip("httpx")
    sec.reset_embedding_transport_stats_for_tests()
    os.environ["KERNEL_SEMANTIC_EMBED_RETRIES"] = "0"
    try:
        ev = threading.Event()
        ev.set()
        set_llm_cancel_scope(ev)
        try:
            with pytest.raises(LLMHttpCancelledError):
                await sec.ahttp_fetch_ollama_embedding_with_policy("http://unused", "m", "p")
        finally:
            clear_llm_cancel_scope()
    finally:
        os.environ.pop("KERNEL_SEMANTIC_EMBED_RETRIES", None)
        sec.reset_embedding_transport_stats_for_tests()
