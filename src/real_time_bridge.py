"""
Async bridge for chat UI / WebSocket layers.

The kernel and LLM calls are synchronous; this wrapper runs them in a worker thread
so the asyncio event loop is not blocked by deliberation or blocking HTTP (Ollama).

By default we use Starlette's ``run_in_threadpool`` (anyio thread limiter). Set
``KERNEL_CHAT_THREADPOOL_WORKERS`` to a positive integer to use a dedicated
``ThreadPoolExecutor`` sized for concurrent chat sessions (isolation from other
thread offload in the process).

**Cancellation / timeouts:** ``asyncio.wait_for`` around :meth:`process_chat` can
drop the **async** waiter when time elapses, but the synchronous work in the thread
(including ``httpx`` to Ollama) may continue until its own timeout. True cooperative
cancellation needs an async HTTP client (future work; see ADR 0002).
"""

from __future__ import annotations

import asyncio
import functools
import os
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING

from starlette.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from .kernel import ChatTurnResult, EthicalKernel
    from .modules.sensor_contracts import SensorSnapshot

_executor: ThreadPoolExecutor | None = None


def _dedicated_pool_workers() -> int:
    raw = os.environ.get("KERNEL_CHAT_THREADPOOL_WORKERS", "").strip()
    if not raw:
        return 0
    try:
        n = int(raw)
    except ValueError:
        return 0
    return max(0, n)


def _get_dedicated_executor() -> ThreadPoolExecutor | None:
    global _executor
    n = _dedicated_pool_workers()
    if n <= 0:
        return None
    if _executor is None:
        _executor = ThreadPoolExecutor(max_workers=n, thread_name_prefix="ethos_chat")
    return _executor


def shutdown_chat_threadpool(*, wait: bool = True) -> None:
    """Release dedicated chat workers (call from ASGI lifespan shutdown)."""
    global _executor
    if _executor is not None:
        _executor.shutdown(wait=wait, cancel_futures=False)
        _executor = None


def reset_chat_threadpool_for_tests() -> None:
    """Test helper: clear executor so a new ``max_workers`` applies."""
    shutdown_chat_threadpool(wait=False)


class RealTimeBridge:
    """Runs ``process_chat_turn`` in a worker thread (non-blocking event loop)."""

    def __init__(self, kernel: EthicalKernel):
        self.kernel = kernel

    async def process_chat(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
    ) -> ChatTurnResult:
        bound = functools.partial(
            self.kernel.process_chat_turn,
            user_input,
            agent_id,
            place,
            include_narrative,
            sensor_snapshot,
            escalate_to_dao,
        )
        ex = _get_dedicated_executor()
        if ex is None:
            return await run_in_threadpool(
                self.kernel.process_chat_turn,
                user_input,
                agent_id,
                place,
                include_narrative,
                sensor_snapshot,
                escalate_to_dao,
            )
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(ex, bound)
