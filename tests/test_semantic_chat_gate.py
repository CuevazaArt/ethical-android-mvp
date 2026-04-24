import pytest

pytest.importorskip("chromadb")
"""Semantic MalAbs layers: lexical first, then embeddings (θ_block/θ_allow), optional LLM arbiter."""

import asyncio
import os
import subprocess
import sys

import numpy as np
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.ethics.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilDetector
from src.modules.memory.semantic_anchor_store import create_anchor_store
from src.modules.safety.semantic_chat_gate import (
    DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
    DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
    add_semantic_anchor,
    arun_semantic_malabs_acl_bypass,
    classify_semantic_zone,
    evaluate_semantic_chat_gate,
    run_semantic_malabs_after_lexical,
    semantic_chat_gate_env_enabled,
)


def test_evaluate_semantic_chat_gate_returns_none_when_disabled(monkeypatch):
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    assert evaluate_semantic_chat_gate("any text") is None


def test_semantic_chat_gate_env_enabled_explicit_off(monkeypatch):
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    assert semantic_chat_gate_env_enabled() is False


def test_semantic_chat_gate_env_enabled_unset_defaults_on(monkeypatch):
    monkeypatch.delenv("KERNEL_SEMANTIC_CHAT_GATE", raising=False)
    assert semantic_chat_gate_env_enabled() is True


def test_semantic_gate_defaults_on_in_fresh_interpreter():
    """Unset env → gate on; uses a subprocess so pytest ``conftest`` env does not apply."""
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os
os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
from src.modules.safety.semantic_chat_gate import semantic_chat_gate_env_enabled
assert semantic_chat_gate_env_enabled() is True
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


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
    import src.modules.safety.semantic_chat_gate as sg

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
        import src.modules.safety.semantic_chat_gate as sg
        from src.modules.ethics.absolute_evil import AbsoluteEvilCategory, AbsoluteEvilResult

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
        import src.modules.safety.semantic_chat_gate as sg

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
    import src.modules.safety.semantic_chat_gate as sg

    monkeypatch.setattr(sg, "_fetch_embedding", lambda t: np.array([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        sg,
        "_best_similarity",
        lambda emb, backend=None: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
    )
    try:
        r = run_semantic_malabs_after_lexical("some paraphrase", llm_backend=None)
        assert r.blocked is True
        assert "ambiguous" in r.reason.lower() or "fail-safe" in r.reason.lower()
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)
        os.environ.pop("KERNEL_SEMANTIC_CHAT_LLM_ARBITER", None)


def test_semantic_block_maps_torture_category(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    import src.modules.safety.semantic_chat_gate as sg

    monkeypatch.setattr(sg, "_fetch_embedding", lambda _t: np.array([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        sg,
        "_best_similarity",
        lambda _emb, backend=None: (0.93, "TORTURE", "torture anchor match"),
    )
    try:
        r = run_semantic_malabs_after_lexical("paraphrased cruelty request", llm_backend=None)
        assert r.blocked is True
        assert r.category == AbsoluteEvilCategory.TORTURE
    finally:
        os.environ.pop("KERNEL_SEMANTIC_CHAT_GATE", None)


def test_llm_arbiter_can_allow_ambiguous(monkeypatch):
    os.environ["KERNEL_SEMANTIC_CHAT_GATE"] = "1"
    os.environ["KERNEL_SEMANTIC_CHAT_LLM_ARBITER"] = "1"
    import src.modules.safety.semantic_chat_gate as sg

    monkeypatch.setattr(sg, "_fetch_embedding", lambda t: np.array([1.0, 0.0, 0.0]))
    monkeypatch.setattr(
        sg,
        "_best_similarity",
        lambda emb, backend=None: (0.6, "INTENTIONAL_LETHAL_VIOLENCE", "hint"),
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


def test_default_semantic_threshold_constants_guardrail():
    """Changing production defaults is deliberate: update constants, tests, and evidence doc."""
    assert DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD == 0.82
    assert DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD == 0.45


def test_classify_semantic_zone_boundaries():
    tb, ta = 0.82, 0.45
    assert classify_semantic_zone(1.0, tb, ta) == "block"
    assert classify_semantic_zone(tb, tb, ta) == "block"
    assert classify_semantic_zone(tb - 1e-9, tb, ta) == "ambiguous"
    assert classify_semantic_zone(ta, tb, ta) == "allow"
    assert classify_semantic_zone(0.0, tb, ta) == "allow"


def test_block_and_allow_thresholds_match_defaults_in_fresh_interpreter():
    """Unset env → θ_block/θ_allow match named defaults (guards accidental drift)."""
    root = os.path.join(os.path.dirname(__file__), "..")
    code = """
import os
for k in (
    "KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD",
    "KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD",
    "KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD",
):
    os.environ.pop(k, None)
from src.modules.safety.semantic_chat_gate import (
    DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD,
    DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD,
    _allow_threshold,
    _block_threshold,
)
assert _block_threshold() == DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD
assert _allow_threshold() == DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD
"""
    subprocess.run([sys.executable, "-c", code], cwd=root, check=True)


def test_add_semantic_anchor_registers_phrase():
    import src.modules.safety.semantic_chat_gate as sg

    n = len(sg._runtime_anchors)
    add_semantic_anchor("unique test phrase xyz123", "UNAUTHORIZED_REPROGRAMMING", "rt")
    try:
        assert len(sg._runtime_anchors) == n + 1
        assert any("xyz123" in a[0] for a in sg._runtime_anchors)
    finally:
        sg._runtime_anchors[:] = [a for a in sg._runtime_anchors if "xyz123" not in a[0]]


def test_anchor_store_basic_functionality():
    """Test that the anchor store can store and retrieve anchors."""
    store = create_anchor_store("memory")

    # Test upsert and query
    embedding = np.random.rand(768).astype(np.float32)
    store.upsert_anchor("test_id", "test phrase", embedding, {"category": "test"})

    neighbors = store.query_neighbors(embedding, k=1)
    assert len(neighbors) == 1
    anchor_id, similarity, metadata = neighbors[0]
    assert anchor_id == "test_id"
    assert abs(similarity - 1.0) < 0.01  # Should be very close to 1
    assert metadata["category"] == "test"

    # Test get_all_anchors
    all_anchors = store.get_all_anchors()
    assert len(all_anchors) >= 1
    assert any(aid == "test_id" for aid, _, _ in all_anchors)


def test_arun_semantic_malabs_acl_bypass_is_deterministic_allow() -> None:
    """Thermal ACL bypass must not use unittest mocks; returns a stable allow trace."""
    r = asyncio.run(arun_semantic_malabs_acl_bypass())
    assert r.blocked is False
    assert r.metadata.get("acl_degraded") is True
    assert any("thermal_bypass" in str(x) for x in r.decision_trace)


@pytest.mark.asyncio
async def test_sync_evaluate_chat_text_runs_semantic_off_event_loop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """
    Bloque 34.0: sync ``evaluate_chat_text`` under a running loop must not call
    ``http_fetch_ollama_embedding_with_policy`` on the loop thread (no event-loop warning).
    """
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "1")
    det = AbsoluteEvilDetector()

    async def _inner() -> None:
        r = det.evaluate_chat_text("hello from async context for bloque 34", None)
        assert r is not None
        assert isinstance(r.blocked, bool)

    await _inner()
