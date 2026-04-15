# Sync kernel inside an async ASGI server — bridge contract

**Status:** implemented (April 2026) — complements [ADR 0002](../adr/0002-async-orchestration-future.md).

## Problem

`EthicalKernel` and `LLMModule` are **synchronous** (deliberate: testability, stack traces). The chat surface is **FastAPI / Starlette** (async). If synchronous CPU work or blocking HTTP runs **on the asyncio event loop**, every WebSocket session shares that loop: one slow path degrades **all** connections.

Heavy **Psi Sleep** (`EthicalKernel.execute_sleep`) is **not** part of the per-chat hot path; it is intended for batch / CLI / explicit maintenance. **Do not** schedule `execute_sleep` on the ASGI event loop without offloading (see [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) — background tasks).

## Mitigations in code

| Stage | Mechanism |
|-------|-----------|
| **Chat turn** | `RealTimeBridge.process_chat` runs `process_chat_turn` in a worker thread (`run_in_threadpool` or dedicated `ThreadPoolExecutor` when `KERNEL_CHAT_THREADPOOL_WORKERS` > 0). |
| **WebSocket JSON** | `RealTimeBridge.run_sync_in_chat_thread` runs `_chat_turn_to_jsonable` in the same offload path when `KERNEL_CHAT_JSON_OFFLOAD` is on (default). This covers optional `KERNEL_LLM_MONOLOGUE` (sync HTTP to Ollama) after the turn completes. |
| **Advisory telemetry** | `advisory_loop` uses `run_in_threadpool(advisory_snapshot, kernel)` so periodic `DriveArbiter.evaluate` does not block the loop. |
| **Turn deadline** | Optional `KERNEL_CHAT_TURN_TIMEOUT` — async wait only; does not cancel in-flight sync HTTP (see ADR 0002). |

## Operator knobs

- `KERNEL_CHAT_THREADPOOL_WORKERS` — size dedicated pool for chat offload; `0` uses Starlette default pool.
- `KERNEL_CHAT_JSON_OFFLOAD` — default **on**; set to `0` only to debug (JSON built on the event loop).
- `KERNEL_ADVISORY_INTERVAL_S` — advisory loop interval; work is thread-offloaded but still consumes CPU somewhere.

## Residual limits

- Thread pool **saturation** still queues work; tune workers and host capacity.
- `execute_sleep` remains **out of band** for the chat server unless a future design adds a **separate worker process** or explicit thread offload for maintenance jobs.
- True HTTP cancellation requires async clients (ADR 0002 future).

## Links

- [`src/real_time_bridge.py`](../../src/real_time_bridge.py)  
- [`src/chat_server.py`](../../src/chat_server.py)  
- [`src/runtime/telemetry.py`](../../src/runtime/telemetry.py)  
- [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §1
