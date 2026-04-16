"""
Cooperative LLM HTTP cancellation for sync backends (chat worker thread).

When ``KERNEL_CHAT_TURN_TIMEOUT`` fires, asyncio drops the waiter but the worker
thread may still run. The WebSocket handler sets a shared :class:`threading.Event`
so sync LLM backends can **abort before** the next blocking ``httpx`` call (and
between chunked waits in tests). The same event is passed when
``KERNEL_CHAT_ASYNC_LLM_HTTP`` runs ``process_chat_turn_async`` so the thread
that executes :meth:`EthicalKernel.process` uses :func:`set_llm_cancel_scope`
(see ``_process_chat_cooperative`` in ``kernel.py``). An in-flight **sync**
``httpx`` request is still bounded by its read timeout; use async LLM HTTP for
cancellable in-flight requests (ADR 0002).
"""

from __future__ import annotations

import threading

_tls = threading.local()


class LLMHttpCancelledError(Exception):
    """Raised when the chat async deadline has signalled cancellation for this worker thread."""


def set_llm_cancel_scope(cancel_event: threading.Event | None) -> None:
    """Bind ``cancel_event`` for the current thread (call from the chat worker entrypoint)."""
    _tls.cancel_event = cancel_event


def clear_llm_cancel_scope() -> None:
    """Clear cancel scope for the current thread."""
    if hasattr(_tls, "cancel_event"):
        del _tls.cancel_event


def llm_cancel_event_for_thread() -> threading.Event | None:
    """Return the bound event for the current thread, if any."""
    return getattr(_tls, "cancel_event", None)


def check_llm_cancel_requested() -> bool:
    """True when a cancel event is bound and set."""
    ev = getattr(_tls, "cancel_event", None)
    return ev is not None and ev.is_set()


def raise_if_llm_cancel_requested() -> None:
    """Raise :class:`LLMHttpCancelledError` if cancellation was requested for this thread."""
    if check_llm_cancel_requested():
        raise LLMHttpCancelledError("llm http cancelled (async chat deadline)")
