"""Bloque 20.2 — local Ollama chat defaults and verbal prompt brevity."""

from __future__ import annotations

import pytest

from src.modules.llm_layer import PROMPT_COMMUNICATION_LOCAL_FLUENCY_APPEND


def test_local_fluency_prompt_exists() -> None:
    assert "LOCAL LLM FLUENCY" in PROMPT_COMMUNICATION_LOCAL_FLUENCY_APPEND
    assert "inner_voice" in PROMPT_COMMUNICATION_LOCAL_FLUENCY_APPEND


def test_kernel_settings_rejects_non_finite_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "nan")
    monkeypatch.delenv("USE_LOCAL_LLM", raising=False)
    monkeypatch.delenv("LLM_MODE", raising=False)
    monkeypatch.delenv("KERNEL_NOMAD_MODE", raising=False)
    from src.settings.kernel_settings import KernelSettings

    st = KernelSettings.from_env()
    assert st.kernel_chat_turn_timeout_seconds is None
