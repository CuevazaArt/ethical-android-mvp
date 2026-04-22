"""Async LLM HTTP path: ``asyncio.wait_for`` can cancel in-flight ``httpx`` (see ADR 0002)."""

from __future__ import annotations

import asyncio

import pytest

from src.modules.cognition.llm_backends import MockLLMBackend


def test_mock_acompletion_cancelled_by_wait_for() -> None:
    async def run() -> None:
        backend = MockLLMBackend(completion_delay_s=30.0, completion_text="{}")
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(backend.acompletion("s", "u"), timeout=0.08)

    asyncio.run(run())


def test_bridge_async_llm_env_toggle(monkeypatch: pytest.MonkeyPatch) -> None:
    from src.real_time_bridge import _async_chat_llm_http_enabled

    monkeypatch.delenv("KERNEL_CHAT_ASYNC_LLM_HTTP", raising=False)
    assert _async_chat_llm_http_enabled() is False
    monkeypatch.setenv("KERNEL_CHAT_ASYNC_LLM_HTTP", "1")
    assert _async_chat_llm_http_enabled() is True
