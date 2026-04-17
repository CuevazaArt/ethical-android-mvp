# ADR 0002 — Async orchestration for chat / kernel

**Status:** Accepted — **partial** (April 2026)  
**Context:** The kernel and ``LLMModule`` remain **synchronous** by design (testability, clear stack traces). The WebSocket server is **async** (FastAPI/Starlette). Reviews flagged **event-loop blocking**, **concurrency between sessions**, and **timeouts / cancellation** for LLM I/O.

## Decision (current)

1. **Non-blocking event loop (implemented):** ``RealTimeBridge`` runs ``EthicalKernel.process_chat_turn`` in a **worker thread** — default via Starlette ``run_in_threadpool``, or a **dedicated** ``ThreadPoolExecutor`` when ``KERNEL_CHAT_THREADPOOL_WORKERS`` > 0. One slow Ollama call does **not** block the asyncio loop from accepting other connections; throughput is limited by thread pool size and host resources, not by a single blocking call on the loop.

2. **Async turn deadline (implemented):** Optional ``KERNEL_CHAT_TURN_TIMEOUT`` wraps ``await bridge.process_chat`` in ``asyncio.wait_for``. On expiry the server sends WebSocket JSON with ``error=chat_turn_timeout`` and sets a **cooperative cancel** ``threading.Event`` so sync LLM backends skip **further** HTTP calls in that worker thread (``src/modules/llm_http_cancel.py``); the **current** sync ``httpx`` request, if any, still runs until its read timeout unless **opt-in async LLM** is enabled (see item 5). The handler also calls :meth:`src.kernel.EthicalKernel.abandon_chat_turn` with the per-connection monotonic ``chat_turn_id`` so late completions skip STM / ``wm.add_turn`` and related effects (path ``turn_abandoned``; see item 9).

3. **Executor lifecycle:** On ASGI lifespan shutdown, ``shutdown_chat_threadpool()`` waits on the dedicated executor (if any).

4. **Future (not required for this ADR):** Queue-based workers for background jobs; structured concurrency per session; optional split of a sync kernel package boundary. The chat path can already use async HTTP (item 5).

5. **Async LLM HTTP on chat (opt-in — April 2026):** When ``KERNEL_CHAT_ASYNC_LLM_HTTP=1``, :meth:`src.real_time_bridge.RealTimeBridge.process_chat` awaits :meth:`src.kernel.EthicalKernel.process_chat_turn_async` on the **asyncio** loop. Perception / communicate / narrate use ``httpx.AsyncClient`` (Ollama, HTTP JSON) so ``asyncio.wait_for`` can **cancel in-flight** HTTP. The same **cancel** ``threading.Event`` is passed into ``process_chat_turn_async`` and bound in the thread that runs :meth:`~src.kernel.EthicalKernel.process` via :meth:`~src.kernel.EthicalKernel._process_chat_cooperative` (thread-local ``llm_http_cancel`` scope + cooperative abort checks). The ethical core still runs in ``asyncio.to_thread`` (not OS-preempted); it **can** exit early when the deadline or abandon is observed (see item 9). ``LLM_MODE=api`` (Anthropic): :meth:`src.modules.llm_backends.AnthropicLLMBackend.acompletion` uses the SDK’s ``AsyncAnthropic`` Messages API when available (otherwise falls back to sync completion in a worker). Default **off** to preserve the worker-thread chat model and avoid surprising semantics.

6. **WebSocket JSON offload (April 2026):** After each turn, optional LLM monologue embellishment (``KERNEL_LLM_MONOLOGUE``) and JSON assembly run in :meth:`src.real_time_bridge.RealTimeBridge.run_sync_in_chat_thread` when ``KERNEL_CHAT_JSON_OFFLOAD`` is on (default), using the same executor policy as :meth:`~src.real_time_bridge.RealTimeBridge.process_chat`.

7. **Advisory telemetry offload:** :func:`src.runtime.telemetry.advisory_loop` evaluates drive intents via ``run_in_threadpool`` so the periodic advisory path does not block the event loop.

8. **Psi Sleep / ``execute_sleep`` (April 2026):** :meth:`src.real_time_bridge.RealTimeBridge.run_execute_sleep` runs :meth:`src.kernel.EthicalKernel.execute_sleep` in the **same** executor policy as chat turns. The default ``/ws/chat`` loop does **not** invoke Psi Sleep on each message; any future HTTP/WebSocket surface that triggers nightly maintenance must use this async wrapper (or ``run_sync_in_chat_thread``) rather than calling the kernel synchronously on the event loop. WebSocket **session end** (checkpoint save + conduct guide export) runs via ``run_sync_in_chat_thread`` so disconnect does not block other connections’ I/O.

9. **Cooperative exit from ``process`` (April 2026):** When ``process`` is invoked from ``_process_chat_cooperative`` (async LLM chat path), thread-local state records the cancel event and ``chat_turn_id``. :meth:`~src.kernel.EthicalKernel.process` consults them at **several** points (before buffer activation, before Bayesian evaluation, after optional BMA, before reflection, before narrative episode registration, etc.) and raises ``ChatTurnCooperativeAbort`` so the async caller returns ``turn_abandoned`` without further STM effects. **Limits:** a single very long native call (e.g. one huge scoring step with no yield) is still not interruptible; tuning ``KERNEL_CHAT_TURN_TIMEOUT`` / ``OLLAMA_TIMEOUT`` remains important.

## Consequences

- **Positive:** Multiple WebSocket sessions remain **responsive** at the transport layer; operators can cap **perceived** turn latency and size a **known** thread pool.
- **Negative:** Under heavy load, **thread** exhaustion still queues work; ``KERNEL_CHAT_TURN_TIMEOUT`` does not kill Ollama server-side; document honestly in operator docs.

## Cooperative HTTP cancellation (April 2026)

**A — Sync worker (default):** On ``KERNEL_CHAT_TURN_TIMEOUT``, the WebSocket handler sets a per-turn ``threading.Event`` that sync LLM backends consult before each blocking completion (``src/modules/llm_http_cancel.py``). An in-flight sync ``httpx`` POST is not cancelled mid-flight.

**B — Async LLM (``KERNEL_CHAT_ASYNC_LLM_HTTP=1``):** ``process_chat_turn_async`` runs LLM HTTP as awaitable ``httpx.AsyncClient`` calls; ``asyncio.wait_for`` cancels in-flight Ollama/HTTP JSON requests. The **same** event is passed through so the **thread** running ``process`` sees ``set_llm_cancel_scope`` and cooperative abort. MalAbs / non-LLM work before the first await remains synchronous on the loop for that segment (typically short).

**Metrics:** When ``KERNEL_METRICS=1``, ``ethos_kernel_llm_cancel_scope_signals_total`` increments alongside ``ethos_kernel_chat_turn_async_timeouts_total`` on the async-timeout path. Late abandoned effects (skipped STM updates) increment ``ethos_kernel_chat_turn_abandoned_effects_skipped_total``.

**Still future work:** Burst-cancel stress tests; finer-grained preemption inside the Bayesian engine if profiling shows hotspots.

**Operator alignment:** Tune ``OLLAMA_TIMEOUT`` relative to ``KERNEL_CHAT_TURN_TIMEOUT`` when using the default sync worker path; see [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §1 and G-05 in [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](../proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md).

## Links

- [`src/real_time_bridge.py`](../../src/real_time_bridge.py)  
- [`src/chat_settings.py`](../../src/chat_settings.py) — ``KERNEL_CHAT_TURN_TIMEOUT``, ``KERNEL_CHAT_THREADPOOL_WORKERS``, ``KERNEL_CHAT_JSON_OFFLOAD``, ``KERNEL_CHAT_ASYNC_LLM_HTTP``  
- [`PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md`](../proposals/PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md)  
- [`RUNTIME_CONTRACT.md`](../proposals/RUNTIME_CONTRACT.md)  
- [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md)  
- [ADR 0001 — packaging boundary](0001-packaging-core-boundary.md)
