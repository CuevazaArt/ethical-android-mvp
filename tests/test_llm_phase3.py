"""Fase 3.1 / 3.3 / 3.4 — resolve_llm_mode, USE_LOCAL_LLM, optional monologue."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.llm_layer import LLMModule, resolve_llm_mode


def test_resolve_use_local_llm_selects_ollama(monkeypatch):
    monkeypatch.delenv("LLM_MODE", raising=False)
    monkeypatch.setenv("USE_LOCAL_LLM", "1")
    assert resolve_llm_mode("auto") == "ollama"


def test_resolve_explicit_local_unchanged(monkeypatch):
    monkeypatch.setenv("USE_LOCAL_LLM", "1")
    assert resolve_llm_mode("local") == "local"


def test_resolve_kernel_llm_auto_ollama(monkeypatch):
    monkeypatch.delenv("USE_LOCAL_LLM", raising=False)
    monkeypatch.delenv("KERNEL_LOCAL_LLM_FIRST", raising=False)
    monkeypatch.setenv("KERNEL_LLM_AUTO_OLLAMA", "1")
    assert resolve_llm_mode("auto") == "ollama"


def test_resolve_kernel_local_llm_first(monkeypatch):
    monkeypatch.delenv("USE_LOCAL_LLM", raising=False)
    monkeypatch.delenv("KERNEL_LLM_AUTO_OLLAMA", raising=False)
    monkeypatch.setenv("KERNEL_LOCAL_LLM_FIRST", "1")
    assert resolve_llm_mode("auto") == "ollama"


def test_optional_monologue_passthrough_when_disabled(monkeypatch):
    monkeypatch.delenv("KERNEL_LLM_MONOLOGUE", raising=False)
    llm = LLMModule(mode="local")
    assert llm.optional_monologue_embellishment("[MONO] x=1") == "[MONO] x=1"


def test_resolve_cloud_disabled_maps_auto_and_api(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_CLOUD_DISABLED", "1")
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    assert resolve_llm_mode("api") in ("ollama", "local")
    assert resolve_llm_mode("auto") in ("ollama", "local")


def test_llm_module_api_mode_skips_anthropic_when_cloud_disabled(monkeypatch):
    monkeypatch.setenv("KERNEL_LLM_CLOUD_DISABLED", "1")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "fake-key-for-test")
    llm = LLMModule(mode="api")
    assert llm.client is None
    assert llm.mode in ("ollama", "local")


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
