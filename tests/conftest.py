"""
Pytest defaults: isolate tests from production MalAbs defaults.

Production defaults (unset env): semantic MalAbs + hash embedding fallback are **on** — see
``semantic_chat_gate.semantic_chat_gate_env_enabled`` and ``semantic_embedding_client``.

Tests default to lexical-only MalAbs unless they enable semantic explicitly, so the suite stays
fast and deterministic without Ollama.

**KERNEL_* drift:** this isolation is intentional; CI defaults are not identical to an unset
production shell — see ``docs/proposals/KERNEL_ENV_TYPED_PUBLIC_API.md`` (Issue 7).
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _malabs_test_env_isolation(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_SEMANTIC_CHAT_GATE", "0")
    monkeypatch.setenv("KERNEL_SEMANTIC_EMBED_HASH_FALLBACK", "0")
