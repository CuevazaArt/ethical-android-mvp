"""Semantic chat gate (ADR 0003): optional Ollama embeddings + MalAbs chain."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilDetector
from src.modules.semantic_chat_gate import (
    evaluate_semantic_chat_gate,
    semantic_chat_gate_env_enabled,
)


def test_evaluate_semantic_chat_gate_returns_none_when_disabled():
    os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
    assert evaluate_semantic_chat_gate("any text") is None


def test_semantic_chat_gate_env_enabled_default_off():
    os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
    assert semantic_chat_gate_env_enabled() is False


def test_semantic_chat_gate_env_enabled_truthy():
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    try:
        assert semantic_chat_gate_env_enabled() is True
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)


def test_semantic_blocks_when_embedding_matches_reference(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD"] = "0.5"
    import src.modules.semantic_chat_gate as sg

    sg._ref_embed_cache.clear()
    v = np.array([3.0, 4.0, 0.0], dtype=np.float64)
    v = v / np.linalg.norm(v)

    def same_vec(*_args, **_kwargs):
        return v

    monkeypatch.setattr(sg, "_fetch_embedding", same_vec)
    monkeypatch.setattr(sg, "_cached_ref_embedding", same_vec)
    try:
        r = evaluate_semantic_chat_gate("paraphrase not in substring list")
        assert r is not None
        assert r.blocked is True
        assert r.category == AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD", None)
        sg._ref_embed_cache.clear()


def test_evaluate_chat_text_prefers_semantic_when_enabled(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    try:
        import src.modules.absolute_evil as ae

        fake = ae.AbsoluteEvilResult(
            blocked=True,
            category=AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING,
            reason="semantic test",
        )
        monkeypatch.setattr(ae, "evaluate_semantic_chat_gate", lambda _t: fake)
        d = AbsoluteEvilDetector()
        r = d.evaluate_chat_text("hello")
        assert r.blocked is True
        assert r.reason == "semantic test"
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
