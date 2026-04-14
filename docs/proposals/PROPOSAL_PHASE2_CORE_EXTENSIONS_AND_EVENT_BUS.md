# PROPOSAL — Phase 2 core/extensions seam and kernel event bus

**Status:** proposal (implements incremental spike; package split deferred)  
**ADR:** [`docs/adr/0006-phase2-core-boundary-and-event-bus.md`](../adr/0006-phase2-core-boundary-and-event-bus.md)  
**Roadmap:** [`PRODUCTION_HARDENING_ROADMAP.md`](PRODUCTION_HARDENING_ROADMAP.md) Fase 2

## Goal

Support integrations that consume **structured decision outcomes** (and optional episode IDs) **without** forking `EthicalKernel.process`, while keeping MalAbs → Bayes → poles → will **strictly synchronous** and deterministic for tests.

## Core vs extensions (product tiers)

Aligned with [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md):

| Tier | Role | Event usage |
|------|------|----------------|
| **Core policy** | MalAbs, buffer, Bayes, poles, will, uchi/sympathetic/locus as wired | Emits **`kernel.decision`** — payload is JSON-serializable summary only. |
| **Narrative & audit** | Memory, weakness, forgiveness, DAO mock | **`kernel.episode_registered`** after `NarrativeMemory.register`; extensions may also subscribe to **`kernel.decision`** for audit sinks. |
| **Advisory / UX** | PAD, reflection, salience, LLM tone | Should **not** require the bus; remain read-only on `final_action`. |
| **Runtime** | FastAPI, checkpoints, LAN | May **subscribe** to forward events to external systems; must not block the kernel on network I/O without a future async ADR. |

## Event catalog (v1)

| Event | When | Payload (stable keys) |
|-------|------|------------------------|
| `kernel.decision` | Every return from `EthicalKernel.process` | `scenario`, `place`, `final_action`, `decision_mode`, `blocked`, `block_reason`, `verdict`, `score`, `context` |
| `kernel.episode_registered` | After `memory.register` when `register_episode=True` | `episode_id`, `final_action`, `context`, `decision_mode`, `verdict`, `score` |

Unknown keys may be added in minor versions; subscribers should ignore extras.

## Environment

| Variable | Default | Meaning |
|----------|---------|---------|
| `KERNEL_EVENT_BUS` | off | When truthy, `EthicalKernel` constructs `KernelEventBus` and publishes. |

## Failure model

Subscriber exceptions are **logged** and **suppressed** so a broken logger never blocks ethics code paths.

## Future work

- Optional **`ethos-core`** package: same events, slimmer `install_requires`, re-exports from `src` or renamed package.
- Optional **async** fan-out (ADR 0002 family) behind explicit env — not implied by this bus.

## Tests

See `tests/test_kernel_event_bus.py` and runtime profile **`phase2_event_bus_lab`** in `src/runtime_profiles.py`.
