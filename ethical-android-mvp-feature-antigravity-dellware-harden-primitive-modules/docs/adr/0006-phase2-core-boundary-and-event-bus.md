# ADR 0006 — Phase 2: core vs extensions + in-process event bus

**Status:** Accepted (incremental spike, April 2026)  
**Context:** [`PRODUCTION_HARDENING_ROADMAP.md`](../proposals/PRODUCTION_HARDENING_ROADMAP.md) Fase 2 — integrators (e.g. robotics) need **signals → decision** without dragging full narrative/DAO, and secondary subsystems should fail without breaking the ethical core.

## Decision

1. **Keep one repo / import layout** for now (`from src.kernel import …`). A future **package split** (`ethos-core` vs extensions) will use the same tier table as this ADR; no forced rename in this step.
2. **Introduce an optional in-process `KernelEventBus`** (`src/modules/kernel_event_bus.py`), enabled with **`KERNEL_EVENT_BUS=1`**. It is **synchronous**, **single-threaded**, and **best-effort**: handler exceptions are logged and swallowed so telemetry cannot veto MalAbs/Bayes.
3. **`EthicalKernel`** exposes `subscribe_kernel_event(event, handler)` when the bus is active; publishes **`kernel.decision`** for every `process()` outcome and **`kernel.episode_registered`** when `register_episode` runs.
4. **Canonical core vs extensions** narrative stays aligned with [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md); elaboration and integration patterns live in [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](../proposals/PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md).

## Consequences

- **Positive:** Extension hooks without editing `kernel.py` for every bridge; clear path to extract `ethos-core` later (bus becomes boundary seam).
- **Negative:** Subscribers must stay fast and side-effect safe; misuse can still waste CPU or confuse operators (documented as “advisory channel only”).
- **Non-goals:** Async queues, cross-process IPC, or reordering the decision pipeline.

## Links

- [`PRODUCTION_HARDENING_ROADMAP.md`](../proposals/PRODUCTION_HARDENING_ROADMAP.md)  
- [`0001-packaging-core-boundary.md`](0001-packaging-core-boundary.md)  
- [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md)
