"""
Concurrent cooperative LLM cancel smoke (ADR 0002 burst-cancel operational path).

Used by ``scripts/eval/run_burst_cancel_smoke.py`` and a minimal pytest. Each worker
simulates a chat thread: bind cancel scope, start a long mock completion, signal
cancel shortly after — all workers share one :class:`MockLLMBackend` (thread-safe
delay loop + thread-local cancel scope).
"""

from __future__ import annotations

import math
import numbers
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .llm_backends import MockLLMBackend
from .llm_http_cancel import (
    LLMHttpCancelledError,
    clear_llm_cancel_scope,
    set_llm_cancel_scope,
)

# Smoke only (not load testing): cap worker count to keep thread pools and CI predictable.
_MAX_BURST_SMOKE_WORKERS = 4096
# Public alias for operator CLIs (``scripts/eval/run_burst_cancel_smoke.py``).
MAX_BURST_SMOKE_WORKERS = _MAX_BURST_SMOKE_WORKERS


def _validate_run_burst_params(
    *,
    n_workers: int,
    completion_delay_s: float,
    join_timeout_s: float,
    cancel_after_s: float,
) -> None:
    """Reject non-ints, NaN/Inf, and wrong signs before any ``time.sleep`` in workers."""
    if type(n_workers) is not int or n_workers < 1 or n_workers > _MAX_BURST_SMOKE_WORKERS:
        raise ValueError(
            f"n_workers must be int in [1, {_MAX_BURST_SMOKE_WORKERS}], got {n_workers!r}"
        )
    for name, raw in (
        ("completion_delay_s", completion_delay_s),
        ("join_timeout_s", join_timeout_s),
        ("cancel_after_s", cancel_after_s),
    ):
        if not isinstance(raw, numbers.Real) or isinstance(raw, bool):
            raise TypeError(
                f"{name} must be a real number (int/float/np scalar; not bool), got {type(raw).__name__}"
            )
    for name, raw in (
        ("completion_delay_s", completion_delay_s),
        ("join_timeout_s", join_timeout_s),
    ):
        v = float(raw)
        if not math.isfinite(v) or v <= 0.0:
            raise ValueError(f"{name} must be positive and finite, got {raw!r}")
    c = float(cancel_after_s)
    if not math.isfinite(c) or c < 0.0:
        raise ValueError(f"cancel_after_s must be finite and non-negative, got {cancel_after_s!r}")


def run_burst_cancel_smoke(
    *,
    n_workers: int = 16,
    completion_delay_s: float = 2.0,
    join_timeout_s: float = 5.0,
    cancel_after_s: float = 0.02,
) -> None:
    """
    Run ``n_workers`` concurrent **MOCK** completions; each should end with
    :class:`LLMHttpCancelledError`. Raises ``RuntimeError`` on hang or wrong exception.

    All delays are validated (finite, correct sign) before any worker runs; bool is not a
    valid ``n_workers`` (avoids ``True`` counting as ``1``).
    """
    _validate_run_burst_params(
        n_workers=n_workers,
        completion_delay_s=completion_delay_s,
        join_timeout_s=join_timeout_s,
        cancel_after_s=cancel_after_s,
    )
    backend = MockLLMBackend(completion_delay_s=completion_delay_s, completion_text="{}")
    failures: list[str] = []
    lock = threading.Lock()

    def worker(_: int) -> None:
        ev = threading.Event()
        err: list[BaseException] = []

        def run_completion() -> None:
            set_llm_cancel_scope(ev)
            try:
                backend.completion("s", "u")
            except BaseException as exc:
                err.append(exc)
            finally:
                clear_llm_cancel_scope()

        t = threading.Thread(target=run_completion, daemon=True)
        t.start()
        time.sleep(cancel_after_s)
        ev.set()
        t.join(timeout=join_timeout_s)
        if t.is_alive():
            with lock:
                failures.append("hang")
            return
        if len(err) != 1 or not isinstance(err[0], LLMHttpCancelledError):
            with lock:
                failures.append(f"expected LLMHttpCancelledError, got {err!r}")

    max_workers = min(64, max(4, n_workers))
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = [pool.submit(worker, i) for i in range(n_workers)]
        for fut in as_completed(futures):
            fut.result()

    if failures:
        sample = failures[:12]
        raise RuntimeError(f"burst_cancel_smoke: {len(failures)} failures (sample): {sample}")
