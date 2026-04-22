"""
Concurrent cooperative LLM cancel smoke (ADR 0002 burst-cancel operational path).

Used by ``scripts/eval/run_burst_cancel_smoke.py`` and a minimal pytest. Each worker
simulates a chat thread: bind cancel scope, start a long mock completion, signal
cancel shortly after — all workers share one :class:`MockLLMBackend` (thread-safe
delay loop + thread-local cancel scope).
"""
# Status: SCAFFOLD


from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from src.modules.cognition.llm_backends import MockLLMBackend
from src.modules.cognition.llm_http_cancel import (
    LLMHttpCancelledError,
    clear_llm_cancel_scope,
    set_llm_cancel_scope,
)


def run_burst_cancel_smoke(
    *,
    n_workers: int = 16,
    completion_delay_s: float = 2.0,
    join_timeout_s: float = 5.0,
    cancel_after_s: float = 0.02,
) -> None:
    """
    Run ``n_workers`` concurrent mock completions; each should end with
    :class:`LLMHttpCancelledError`. Raises ``RuntimeError`` on hang or wrong exception.
    """
    if n_workers < 1:
        raise ValueError("n_workers must be >= 1")
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
