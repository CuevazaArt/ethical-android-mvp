"""Cooperative LLM cancel scope (thread-local event) used by chat timeout + sync backends."""

from __future__ import annotations

import threading
import time

import pytest

from src.modules.llm_backends import MockLLMBackend
from src.modules.llm_http_cancel import (
    LLMHttpCancelledError,
    check_llm_cancel_requested,
    clear_llm_cancel_scope,
    raise_if_llm_cancel_requested,
    set_llm_cancel_scope,
)


def test_raise_if_llm_cancel_when_event_set() -> None:
    ev = threading.Event()
    ev.set()
    set_llm_cancel_scope(ev)
    try:
        with pytest.raises(LLMHttpCancelledError):
            raise_if_llm_cancel_requested()
    finally:
        clear_llm_cancel_scope()


def test_check_false_without_scope_or_unset_event() -> None:
    clear_llm_cancel_scope()
    assert not check_llm_cancel_requested()
    ev = threading.Event()
    set_llm_cancel_scope(ev)
    try:
        assert not check_llm_cancel_requested()
    finally:
        clear_llm_cancel_scope()


def test_mock_completion_aborts_long_delay_when_cancel_signaled() -> None:
    backend = MockLLMBackend(completion_delay_s=30.0, completion_text='{"x":1}')
    ev = threading.Event()
    err: list[BaseException] = []

    def run() -> None:
        set_llm_cancel_scope(ev)
        try:
            backend.completion("sys", "user")
        except BaseException as exc:
            err.append(exc)
        finally:
            clear_llm_cancel_scope()

    t = threading.Thread(target=run, daemon=True)
    t.start()
    time.sleep(0.05)
    ev.set()
    t.join(timeout=2.0)
    assert not t.is_alive(), "worker should finish quickly after cancel"
    assert len(err) == 1
    assert isinstance(err[0], LLMHttpCancelledError)
