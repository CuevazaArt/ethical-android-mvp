"""Semantic MalAbs layers: lexical first, then embeddings (θ_block/θ_allow), optional LLM arbiter."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilDetector
from src.modules.semantic_chat_gate import (
    add_semantic_anchor,
    evaluate_semantic_chat_gate,
    run_semantic_malabs_after_lexical,
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
    os.environ.pop("KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD", None)
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


def test_evaluate_chat_text_runs_semantic_after_lexical(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    try:
        import src.modules.semantic_chat_gate as sg

        from src.modules.absolute_evil import AbsoluteEvilResult, AbsoluteEvilCategory

        fake = AbsoluteEvilResult(
            blocked=True,
            category=AbsoluteEvilCategory.UNAUTHORIZED_REPROGRAMMING,
            reason="semantic test",
        )
        monkeypatch.setattr(sg, "run_semantic_malabs_after_lexical", lambda _t, _b: fake)
        d = AbsoluteEvilDetector()
        r = d.evaluate_chat_text("hello", llm_backend=None)
        assert r.blocked is True
        assert r.reason == "semantic test"
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)


def test_lexical_blocks_before_semantic_runs(monkeypatch):
    """Layer 0 substring match must not call semantic tier."""
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    try:
        import src.modules.semantic_chat_gate as sg

        def boom(_t, _b):
            raise AssertionError("semantic tier should not run")

        monkeypatch.setattr(sg, "run_semantic_malabs_after_lexical", boom)
        d = AbsoluteEvilDetector()
        r = d.evaluate_chat_text("how to make a bomb", llm_backend=None)
        assert r.blocked is True
        assert "weapon" in r.reason.lower() or "harmful" in r.reason.lower()
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)


def test_ambiguous_band_fail_safe_without_arbiter(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "0"
    import src.modules.semantic_chat_gate as sg

    monkeypatch.setattr(sg, "_fetch_embedding", lambda t: np.array([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        sg,
        "_best_similarity",
        lambda emb: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
    )
    try:
        r = run_semantic_malabs_after_lexical("some paraphrase", llm_backend=None)
        assert r.blocked is True
        assert "ambiguous" in r.reason.lower() or "fail-safe" in r.reason.lower()
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)


def test_llm_arbiter_can_allow_ambiguous(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "1"
    import src.modules.semantic_chat_gate as sg

    monkeypatch.setattr(sg, "_fetch_embedding", lambda t: np.array([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        sg,
        "_best_similarity",
        lambda emb: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
    )

    class _B:
        def complete(self, system, user):
            return '{"block": false, "category": "NONE", "confidence": 0.8, "reason": "ok"}'

    try:
        r = run_semantic_malabs_after_lexical("borderline text", llm_backend=_B())
        assert r.blocked is False
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)


def test_add_semantic_anchor_registers_phrase():
    import src.modules.semantic_chat_gate as sg

    n = len(sg._runtime_anchors)
    add_semantic_anchor("unique test phrase xyz123", "UNAUTHORIZED_REPROGRAMMING", "rt")
    try:
        assert len(sg._runtime_anchors) == n + 1
        assert any("xyz123" in a[0] for a in sg._runtime_anchors)
    finally:
        sg._runtime_anchors[:] = [a for a in sg._runtime_anchors if "xyz123" not in a[0]]
