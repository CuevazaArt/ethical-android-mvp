from __future__ import annotations

import asyncio
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from src.modules.perception.nomad_chat_adapter import NomadChatConsumer


class _FakeBridgeQueueHolder:
    def __init__(self) -> None:
        self.chat_text_queue: asyncio.Queue[str] = asyncio.Queue()
        self.charm_feedback_queue: asyncio.Queue[dict] = asyncio.Queue()
        self.dashboard_events: list[dict] = []

    def broadcast_to_dashboards(self, payload: dict) -> None:
        self.dashboard_events.append(payload)


@pytest.mark.asyncio
async def test_nomad_chat_consumer_success_path() -> None:
    nb = _FakeBridgeQueueHolder()
    await nb.chat_text_queue.put("hello from vessel")

    consumer = NomadChatConsumer(kernel=object())

    async def _fake_process_chat(*args, **kwargs):
        return SimpleNamespace(response=SimpleNamespace(message="ok", inner_voice="inner ok"))

    consumer.bridge = SimpleNamespace(process_chat=_fake_process_chat)

    with patch("src.modules.nomad_chat_adapter.get_nomad_bridge", return_value=nb):
        task = asyncio.create_task(consumer._consume_loop())
        for _ in range(30):
            await asyncio.sleep(0)
            if not nb.charm_feedback_queue.empty():
                break
        task.cancel()
        await task

    msg = nb.charm_feedback_queue.get_nowait()
    assert msg["type"] == "kernel_voice"
    assert msg["text"] == "ok"
    assert nb.dashboard_events


@pytest.mark.asyncio
async def test_nomad_chat_consumer_timeout_path() -> None:
    nb = _FakeBridgeQueueHolder()
    await nb.chat_text_queue.put("slow turn")

    consumer = NomadChatConsumer(kernel=object())

    async def _slow_process_chat(*args, **kwargs):
        await asyncio.sleep(0.2)
        return SimpleNamespace(response=SimpleNamespace(message="late", inner_voice=None))

    consumer.bridge = SimpleNamespace(process_chat=_slow_process_chat)

    with patch.dict("os.environ", {"KERNEL_NOMAD_CHAT_TIMEOUT": "0.01"}):
        with patch("src.modules.nomad_chat_adapter.get_nomad_bridge", return_value=nb):
            task = asyncio.create_task(consumer._consume_loop())
            for _ in range(40):
                await asyncio.sleep(0.01)
                if not nb.charm_feedback_queue.empty():
                    break
            task.cancel()
            await task

    msg = nb.charm_feedback_queue.get_nowait()
    assert msg["role"] == "error"
    assert "Timeout" in msg["text"]


@pytest.mark.asyncio
async def test_nomad_chat_consumer_ignores_empty_text() -> None:
    nb = _FakeBridgeQueueHolder()
    await nb.chat_text_queue.put("   ")

    consumer = NomadChatConsumer(kernel=object())

    async def _fake_process_chat(*args, **kwargs):
        return SimpleNamespace(
            response=SimpleNamespace(message="should_not_happen", inner_voice=None)
        )

    consumer.bridge = SimpleNamespace(process_chat=_fake_process_chat)

    with patch("src.modules.nomad_chat_adapter.get_nomad_bridge", return_value=nb):
        task = asyncio.create_task(consumer._consume_loop())
        for _ in range(20):
            await asyncio.sleep(0)
        task.cancel()
        await task

    assert nb.charm_feedback_queue.empty()
