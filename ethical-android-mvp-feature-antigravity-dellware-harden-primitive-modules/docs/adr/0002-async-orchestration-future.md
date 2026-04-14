# ADR 0002 — Async orchestration for chat / kernel

**Status:** Accepted — **partial** (April 2026)  
**Context:** The kernel and ``LLMModule`` remain **synchronous** by design (testability, clear stack traces). The WebSocket server is **async** (FastAPI/Starlette). Reviews flagged **event-loop blocking**, **concurrency between sessions**, and **timeouts / cancellation** for LLM I/O.

## Decision (current)

1. **Non-blocking event loop (implemented):** ``RealTimeBridge`` runs ``EthicalKernel.process_chat_turn`` in a **worker thread** — default via Starlette ``run_in_threadpool``, or a **dedicated** ``ThreadPoolExecutor`` when ``KERNEL_CHAT_THREADPOOL_WORKERS`` > 0. One slow Ollama call does **not** block the asyncio loop from accepting other connections; throughput is limited by thread pool size and host resources, not by a single blocking call on the loop.

2. **Async turn deadline (implemented):** Optional ``KERNEL_CHAT_TURN_TIMEOUT`` wraps ``await bridge.process_chat`` in ``asyncio.wait_for``. On expiry the server sends WebSocket JSON with ``error=chat_turn_timeout``. The **worker thread** may continue until the synchronous ``httpx`` client returns (bounded by ``OLLAMA_TIMEOUT`` for Ollama). This is **not** full cancellation of an in-flight HTTP request.

3. **Executor lifecycle:** On ASGI lifespan shutdown, ``shutdown_chat_threadpool()`` waits on the dedicated executor (if any).

4. **Future (not required for this ADR):** Replace sync ``httpx.Client`` with **async** ``httpx.AsyncClient`` for true request cancellation; queue-based workers for background jobs; structured concurrency per session. Kernel API remains sync unless a future ADR splits a package boundary.

5. **WebSocket JSON offload (April 2026):** After each turn, optional LLM monologue embellishment (``KERNEL_LLM_MONOLOGUE``) and JSON assembly run in :meth:`src.real_time_bridge.RealTimeBridge.run_sync_in_chat_thread` when ``KERNEL_CHAT_JSON_OFFLOAD`` is on (default), using the same executor policy as :meth:`~src.real_time_bridge.RealTimeBridge.process_chat`.

6. **Advisory telemetry offload:** :func:`src.runtime.telemetry.advisory_loop` evaluates drive intents via ``run_in_threadpool`` so the periodic advisory path does not block the event loop.

7. **Psi Sleep / ``execute_sleep`` (April 2026):** :meth:`src.real_time_bridge.RealTimeBridge.run_execute_sleep` runs :meth:`src.kernel.EthicalKernel.execute_sleep` in the **same** executor policy as chat turns. The default ``/ws/chat`` loop does **not** invoke Psi Sleep on each message; any future HTTP/WebSocket surface that triggers nightly maintenance must use this async wrapper (or ``run_sync_in_chat_thread``) rather than calling the kernel synchronously on the event loop. WebSocket **session end** (checkpoint save + conduct guide export) runs via ``run_sync_in_chat_thread`` so disconnect does not block other connections’ I/O.

## Consequences

- **Positive:** Multiple WebSocket sessions remain **responsive** at the transport layer; operators can cap **perceived** turn latency and size a **known** thread pool.
- **Negative:** Under heavy load, **thread** exhaustion still queues work; ``KERNEL_CHAT_TURN_TIMEOUT`` does not kill Ollama server-side; document honestly in operator docs.

## Links

- [`src/real_time_bridge.py`](../../src/real_time_bridge.py)  
- [`src/chat_settings.py`](../../src/chat_settings.py) — ``KERNEL_CHAT_TURN_TIMEOUT``, ``KERNEL_CHAT_THREADPOOL_WORKERS``, ``KERNEL_CHAT_JSON_OFFLOAD``  
- [`PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md`](../proposals/PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md)  
- [`RUNTIME_CONTRACT.md`](../proposals/RUNTIME_CONTRACT.md)  
- [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md)  
- [ADR 0001 — packaging boundary](0001-packaging-core-boundary.md)
