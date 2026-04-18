"""RealTimeBridge thread offload (ADR 0002)."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.kernel import EthicalKernel
from src import real_time_bridge as rtb
from src.real_time_bridge import RealTimeBridge, reset_chat_threadpool_for_tests


def test_run_sync_in_chat_thread_runs_function_off_loop():
    async def _run() -> None:
        k = EthicalKernel(variability=False)
        bridge = RealTimeBridge(k)

        def add(a: int, b: int) -> int:
            return a + b

        assert await bridge.run_sync_in_chat_thread(add, 2, 3) == 5

    asyncio.run(_run())


def test_dedicated_threadpool_env_is_capped(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "500")
    reset_chat_threadpool_for_tests()
    try:
        assert rtb._dedicated_pool_workers() == rtb.CHAT_THREADPOOL_MAX_WORKERS
    finally:
        reset_chat_threadpool_for_tests()
        monkeypatch.delenv("KERNEL_CHAT_THREADPOOL_WORKERS", raising=False)


def test_run_sync_in_chat_thread_uses_dedicated_executor_when_configured(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "2")
    reset_chat_threadpool_for_tests()
    try:

        async def _run() -> None:
            k = EthicalKernel(variability=False)
            bridge = RealTimeBridge(k)
            out: list[int] = []

            def touch() -> None:
                out.append(1)

            await bridge.run_sync_in_chat_thread(touch)
            assert out == [1]

        asyncio.run(_run())
    finally:
        reset_chat_threadpool_for_tests()


def test_run_execute_sleep_returns_string():
    async def _run() -> None:
        k = EthicalKernel(variability=False)
        bridge = RealTimeBridge(k)
        out = await bridge.run_execute_sleep()
        assert isinstance(out, str)

    asyncio.run(_run())
