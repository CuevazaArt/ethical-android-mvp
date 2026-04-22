"""
Async bridge for chat UI / WebSocket layers.

The kernel and LLM calls are synchronous; this wrapper runs them in a worker thread
so the asyncio event loop is not blocked by deliberation or blocking HTTP (Ollama).

By default we use Starlette's ``run_in_threadpool`` (anyio thread limiter). Set
``KERNEL_CHAT_THREADPOOL_WORKERS`` to a positive integer to use a dedicated
``ThreadPoolExecutor`` sized for concurrent chat sessions (isolation from other
thread offload in the process).

**Cancellation / timeouts:** ``asyncio.wait_for`` around :meth:`process_chat` can
drop the **async** waiter when time elapses. The server sets a :class:`threading.Event`
so the worker thread can skip **subsequent** sync LLM HTTP calls (see
``llm_http_cancel``). Set ``KERNEL_CHAT_ASYNC_LLM_HTTP=1`` to run
:meth:`~src.kernel.EthicalKernel.process_chat_turn_async` on the event loop instead of a
worker thread so **in-flight** Ollama/HTTP JSON requests are cancelled when the async
deadline fires (see ADR 0002). ``cancel_event`` is passed through to
:meth:`~src.kernel.EthicalKernel.process_chat_turn_async` so the thread running
:meth:`~src.kernel.EthicalKernel.process` shares the same cooperative cancel + TLS scope
as the default worker-thread path.

**JSON response build:** After a turn returns, :meth:`RealTimeBridge.run_sync_in_chat_thread`
runs the WebSocket JSON builder (``chat_server`` module) in the **same** offload path so optional
LLM monologue embellishment (``KERNEL_LLM_MONOLOGUE``) does not block the asyncio loop.
See ADR 0002 and ``docs/proposals/README.md``.

**Thread-pool size:** ``KERNEL_CHAT_THREADPOOL_WORKERS`` is clamped to a conservative maximum
(``CHAT_THREADPOOL_MAX_WORKERS``) so a mis-set env cannot create hundreds of long-lived workers.

**Psi Sleep / maintenance:** :meth:`RealTimeBridge.run_execute_sleep` runs :meth:`~src.kernel.EthicalKernel.execute_sleep` in the same worker pool. The default WebSocket
chat path does not call it per message; use it from async code when exposing nightly maintenance
so heavy Psi Sleep work does not block the event loop.
"""

from __future__ import annotations

import asyncio
import functools
import os
import threading
from collections.abc import AsyncGenerator, Callable
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, TypeVar

from starlette.concurrency import run_in_threadpool

if TYPE_CHECKING:
    from .kernel import ChatTurnResult, EthicalKernel
    from .modules.perception.sensor_contracts import SensorSnapshot

from .modules.cognition.llm_http_cancel import clear_llm_cancel_scope, set_llm_cancel_scope


def _async_chat_llm_http_enabled() -> bool:
    """
    When true, :meth:`RealTimeBridge.process_chat` awaits :meth:`~src.kernel.EthicalKernel.process_chat_turn_async`
    on the asyncio loop so ``asyncio.wait_for`` can cancel in-flight ``httpx`` (Ollama / HTTP JSON).

    Set ``KERNEL_CHAT_ASYNC_LLM_HTTP=1``. Anthropic (``LLM_MODE=api``) uses async-wrapped sync calls;
    cancellation is weaker than native async HTTP — see ADR 0002.
    """
    return os.environ.get("KERNEL_CHAT_ASYNC_LLM_HTTP", "").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )


_T = TypeVar("_T")


def _run_process_chat_turn_in_worker(
    kernel: EthicalKernel,
    cancel_event: threading.Event | None,
    user_input: str,
    agent_id: str,
    place: str,
    include_narrative: bool,
    sensor_snapshot: SensorSnapshot | None,
    escalate_to_dao: bool,
    chat_turn_id: int | None,
) -> ChatTurnResult:
    if cancel_event is not None:
        set_llm_cancel_scope(cancel_event)
    try:
        return kernel.process_chat_turn(
            user_input,
            agent_id,
            place,
            include_narrative,
            sensor_snapshot,
            escalate_to_dao,
            chat_turn_id=chat_turn_id,
        )
    finally:
        clear_llm_cancel_scope()


_executor: ThreadPoolExecutor | None = None


# Hard cap: misconfiguration must not create an oversized OS thread pool on the server.
CHAT_THREADPOOL_MAX_WORKERS = 64


def _dedicated_pool_workers() -> int:
    raw = os.environ.get("KERNEL_CHAT_THREADPOOL_WORKERS", "").strip()
    if not raw:
        return 0
    try:
        n = int(raw)
    except ValueError:
        return 0
    n = max(0, n)
    return min(n, CHAT_THREADPOOL_MAX_WORKERS)


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
        cancel_event: threading.Event | None = None,
        chat_turn_id: int | None = None,
    ) -> ChatTurnResult:
        # Architecture V1.5 - Forced Async for Tri-Lobe Mode
        tri_lobe_enabled = os.environ.get("KERNEL_TRI_LOBE_ENABLED", "").lower() in (
            "1",
            "true",
            "yes",
        )

        if _async_chat_llm_http_enabled() or tri_lobe_enabled:
            return await self.kernel.process_chat_turn_async(
                user_input,
                agent_id,
                place,
                include_narrative,
                sensor_snapshot,
                escalate_to_dao,
                chat_turn_id=chat_turn_id,
                cancel_event=cancel_event,
            )
        bound = functools.partial(
            _run_process_chat_turn_in_worker,
            self.kernel,
            cancel_event,
            user_input,
            agent_id,
            place,
            include_narrative,
            sensor_snapshot,
            escalate_to_dao,
            chat_turn_id,
        )
        ex = _get_dedicated_executor()
        if ex is None:
            return await run_in_threadpool(bound)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(ex, bound)

    async def process_chat_stream(
        self,
        user_input: str,
        agent_id: str = "user",
        place: str = "chat",
        include_narrative: bool = False,
        sensor_snapshot: SensorSnapshot | None = None,
        escalate_to_dao: bool = False,
        cancel_event: threading.Event | None = None,
        chat_turn_id: int | None = None,
        conversation_context: str = "",
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Real-time stream via kernel.process_chat_turn_stream."""
        async for event in self.kernel.process_chat_turn_stream(
            user_input,
            agent_id=agent_id,
            place=place,
            include_narrative=include_narrative,
            sensor_snapshot=sensor_snapshot,
            escalate_to_dao=escalate_to_dao,
            chat_turn_id=chat_turn_id,
            cancel_event=cancel_event,
            conversation_context=conversation_context,
        ):
            yield event

    async def run_execute_sleep(self) -> str:
        """
        Run :meth:`~src.kernel.EthicalKernel.execute_sleep` in the chat worker pool.

        Psi Sleep, forgiveness, and related work are CPU- and I/O-heavy relative to a single
        asyncio tick. Call this from FastAPI/WebSocket handlers or background tasks instead of
        invoking ``kernel.execute_sleep()`` directly on the event loop.
        """
        ex = _get_dedicated_executor()
        if ex is None:
            return await run_in_threadpool(self.kernel.execute_sleep)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(ex, self.kernel.execute_sleep)

    async def run_sync_in_chat_thread(
        self,
        fn: Callable[..., _T],
        /,
        *args: Any,
        **kwargs: Any,
    ) -> _T:
        """
        Run a synchronous callable in the chat worker pool so the asyncio loop is not blocked.

        Used after :meth:`process_chat` returns to build WebSocket JSON (including optional
        ``KERNEL_LLM_MONOLOGUE`` HTTP to Ollama). Same executor policy as :meth:`process_chat`.
        """
        bound = functools.partial(fn, *args, **kwargs)
        ex = _get_dedicated_executor()
        if ex is None:
            return await run_in_threadpool(bound)
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(ex, bound)
