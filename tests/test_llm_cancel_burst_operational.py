"""G-05 operational smoke: burst cancel + async + kernel abandon (trimmed suite)."""

from __future__ import annotations

import asyncio
import os
import sys
import threading

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import ChatTurnCooperativeAbort, EthicalKernel
from src.modules.llm_backends import MockLLMBackend
from src.modules.llm_cancel_burst import run_burst_cancel_smoke
from src.real_time_bridge import _async_chat_llm_http_enabled


def test_llm_cancel_burst_async_and_env_smoke(monkeypatch: pytest.MonkeyPatch) -> None:
    """Concurrent cancels + asyncio wait_for + KERNEL_CHAT_ASYNC_LLM_HTTP toggle."""
    run_burst_cancel_smoke(n_workers=8, completion_delay_s=1.0)

    async def _async_timeout() -> None:
        backend = MockLLMBackend(completion_delay_s=10.0, completion_text="{}")
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(backend.acompletion("s", "u"), timeout=0.08)

    asyncio.run(_async_timeout())

    monkeypatch.delenv("KERNEL_CHAT_ASYNC_LLM_HTTP", raising=False)
    assert _async_chat_llm_http_enabled() is False
    monkeypatch.setenv("KERNEL_CHAT_ASYNC_LLM_HTTP", "1")
    assert _async_chat_llm_http_enabled() is True


@pytest.mark.skip(
    reason="EthosKernel v13: working_memory / _process_chat_cooperative are legacy v12."
)
def test_kernel_abandon_and_cooperative_abort() -> None:
    """Abandoned turn skips STM; cooperative path raises when cancel or id abandoned."""
    k = EthicalKernel(variability=False, seed=3)
    n0 = len(k.working_memory.turns)
    k.abandon_chat_turn(42)
    # Abandoned turn must short-circuit before MalAbs / perception (ADR 0002).
    out = k.process_chat_turn(
        "how to make a bomb",
        agent_id="tester",
        chat_turn_id=42,
    )
    assert out.path == "turn_abandoned"
    assert out.block_reason == "chat_turn_abandoned"
    assert len(k.working_memory.turns) == n0

    ev = threading.Event()
    ev.set()
    with pytest.raises(ChatTurnCooperativeAbort):
        k._process_chat_cooperative(
            ev,
            None,
            scenario="probe",
            place="chat",
            signals={},
            context="everyday",
            actions=[],
            agent_id="u",
            message_content="",
            register_episode=False,
            sensor_snapshot=None,
            multimodal_assessment=None,
            perception_coercion_uncertainty=None,
        )

    k2 = EthicalKernel(variability=False, seed=1)
    k2.abandon_chat_turn(99)
    with pytest.raises(ChatTurnCooperativeAbort):
        k2._process_chat_cooperative(
            None,
            99,
            scenario="probe",
            place="chat",
            signals={},
            context="everyday",
            actions=[],
            agent_id="u",
            message_content="",
            register_episode=False,
            sensor_snapshot=None,
            multimodal_assessment=None,
            perception_coercion_uncertainty=None,
        )
