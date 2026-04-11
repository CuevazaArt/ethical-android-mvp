# ADR 0002 — Async orchestration for chat / kernel (future)

**Status:** Proposed (stub, April 2026)  
**Context:** The WebSocket stack and `EthicalKernel` today are largely **synchronous** on the request path; reviews have flagged **latency**, **backpressure**, and **cancellation** as eventual concerns if the surface area grows (LLM, multimodal, persistence).

## Decision (placeholder)

**No change in the MVP:** keep the current synchronous decision path unless profiling shows a concrete bottleneck.

**Future options to evaluate** (not mutually exclusive):

1. **Structured concurrency** around I/O-bound steps (LLM, disk checkpoint) with explicit timeouts.
2. **Queue + worker** for non-user-facing work (telemetry digest, optional audits).
3. **Kernel API boundary** unchanged: async wrappers must preserve **ordering per session** and **failure semantics** documented in [`RUNTIME_CONTRACT.md`](../RUNTIME_CONTRACT.md).

## Consequences

- **Positive:** Room to scale chat throughput without blocking the event loop — *if* measured need arises.
- **Negative:** Higher operational complexity; every async hop needs tests for races and partial failure.

## Links

- [`RUNTIME_CONTRACT.md`](../RUNTIME_CONTRACT.md)  
- [`CORE_DECISION_CHAIN.md`](../CORE_DECISION_CHAIN.md)  
- [ADR 0001 — packaging boundary](0001-packaging-core-boundary.md)
