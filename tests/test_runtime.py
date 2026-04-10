"""Runtime entrypoint, bind config, and read-only advisory telemetry."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from src.chat_server import get_uvicorn_bind, run_chat_server
from src.kernel import EthicalKernel
from src.modules.drive_arbiter import DriveIntent
from src.runtime.telemetry import (
    advisory_interval_seconds_from_env,
    advisory_loop,
    advisory_snapshot,
)


def test_get_uvicorn_bind_defaults(monkeypatch):
    monkeypatch.delenv("CHAT_HOST", raising=False)
    monkeypatch.delenv("CHAT_PORT", raising=False)
    assert get_uvicorn_bind() == ("127.0.0.1", 8765)


def test_get_uvicorn_bind_from_env(monkeypatch):
    monkeypatch.setenv("CHAT_HOST", "0.0.0.0")
    monkeypatch.setenv("CHAT_PORT", "9999")
    assert get_uvicorn_bind() == ("0.0.0.0", 9999)


def test_run_chat_server_is_same_callable_as_documented():
    assert callable(run_chat_server)


def test_runtime_package_reexports_bind(monkeypatch):
    monkeypatch.delenv("CHAT_HOST", raising=False)
    monkeypatch.delenv("CHAT_PORT", raising=False)
    from src.runtime import get_uvicorn_bind as g2

    assert g2() == get_uvicorn_bind()


def test_advisory_snapshot_returns_list_of_drive_intent():
    k = EthicalKernel(variability=False)
    out = advisory_snapshot(k)
    assert isinstance(out, list)
    assert all(isinstance(x, DriveIntent) for x in out)


def test_advisory_loop_stops_quickly():
    k = EthicalKernel(variability=False)
    stop = asyncio.Event()

    async def _run():
        await asyncio.sleep(0.02)
        stop.set()

    async def _main():
        t = asyncio.create_task(_run())
        await advisory_loop(k, interval_s=60.0, stop=stop)
        await t

    asyncio.run(_main())


def test_advisory_interval_from_env_default(monkeypatch):
    monkeypatch.delenv("KERNEL_ADVISORY_INTERVAL_S", raising=False)
    assert advisory_interval_seconds_from_env() == 0.0


def test_advisory_interval_from_env_positive(monkeypatch):
    monkeypatch.setenv("KERNEL_ADVISORY_INTERVAL_S", "30")
    assert advisory_interval_seconds_from_env() == 30.0


def test_advisory_interval_from_env_invalid_is_zero(monkeypatch):
    monkeypatch.setenv("KERNEL_ADVISORY_INTERVAL_S", "not-a-float")
    assert advisory_interval_seconds_from_env() == 0.0


def test_advisory_loop_interval_must_be_positive():
    k = EthicalKernel(variability=False)
    stop = asyncio.Event()

    async def _bad():
        await advisory_loop(k, interval_s=0.0, stop=stop)

    with pytest.raises(ValueError, match="interval_s"):
        asyncio.run(_bad())
