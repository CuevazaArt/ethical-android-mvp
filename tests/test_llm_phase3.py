"""Fase 3.1 / 3.3 / 3.4 — resolve_llm_mode, USE_LOCAL_LLM, optional monologue."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.cognition.llm_layer import LLMModule, resolve_llm_mode


def test_resolve_use_local_llm_selects_ollama(monkeypatch):
    monkeypatch.delenv("LLM_MODE", raising=False)
    monkeypatch.setenv("USE_LOCAL_LLM", "1")
    assert resolve_llm_mode("auto") == "ollama"


def test_resolve_explicit_local_unchanged(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "1")
    assert resolve_llm_mode("local") == "local"


def test_optional_monologue_passthrough_when_disabled(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_MONOLOGUE", raising=False)
    llm = LLMModule(mode="local")
    assert llm.optional_monologue_embellishment("[MONO] x=1") == "[MONO] x=1"


def test_optional_monologue_mock_backend(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_MONOLOGUE", "1")
    llm = LLMModule(mode="ollama")

    class FakeB:
        def complete(self, system: str, user: str) -> str:
            return "soft light on the console"

    llm._text_backend = FakeB()
    out = llm.optional_monologue_embellishment("[MONO] action=test")
    assert "soft light" in out
    assert out.startswith("[MONO] action=test")
