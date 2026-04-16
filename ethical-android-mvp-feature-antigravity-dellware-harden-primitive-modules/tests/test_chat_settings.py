"""Chat server Pydantic settings (env parsing)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.chat_settings import ChatServerSettings


def test_kernel_chat_turn_timeout_unset(monkeypatch):
    monkeypatch.delenv("KERNEL_CHAT_TURN_TIMEOUT", raising=False)
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_turn_timeout_seconds is None


def test_kernel_chat_turn_timeout_positive(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "180.5")
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_turn_timeout_seconds == 180.5


def test_kernel_chat_turn_timeout_zero_means_unlimited(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_TURN_TIMEOUT", "0")
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_turn_timeout_seconds is None


def test_kernel_chat_threadpool_workers_default_zero(monkeypatch):
    monkeypatch.delenv("KERNEL_CHAT_THREADPOOL_WORKERS", raising=False)
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_threadpool_workers == 0


def test_kernel_chat_threadpool_workers_positive(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_THREADPOOL_WORKERS", "12")
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_threadpool_workers == 12


def test_model_dump_public_includes_async_bridge_keys():
    s = ChatServerSettings(
        chat_host="127.0.0.1",
        chat_port=8765,
        kernel_api_docs=False,
        kernel_variability=True,
        llm_mode=None,
        kernel_chat_include_malabs_trace=True,
        kernel_chat_turn_timeout_seconds=60.0,
        kernel_chat_threadpool_workers=8,
        kernel_chat_json_offload=True,
    )
    d = s.model_dump_public()
    assert d["kernel_chat_turn_timeout_seconds"] == 60.0
    assert d["kernel_chat_threadpool_workers"] == 8
    assert d["kernel_chat_json_offload"] is True


def test_kernel_chat_json_offload_default_on(monkeypatch):
    monkeypatch.delenv("KERNEL_CHAT_JSON_OFFLOAD", raising=False)
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_json_offload is True


def test_kernel_chat_json_offload_can_disable(monkeypatch):
    monkeypatch.setenv("KERNEL_CHAT_JSON_OFFLOAD", "0")
    s = ChatServerSettings.from_env()
    assert s.kernel_chat_json_offload is False
