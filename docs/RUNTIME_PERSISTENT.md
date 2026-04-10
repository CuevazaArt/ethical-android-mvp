# Persistent runtime (initial design)

This document does **not** mandate immediate implementation; it sets criteria for when the kernel stops being ephemeral demos only and moves to **long-lived processes** with recoverable state.

## Goal

A **persistent runtime** keeps narrative identity, episodic memory, and audited governance across restarts **without** changing the kernel’s ethical contract (MalAbs → Bayes → poles → will; v6+ layers are read-only for tone/UX).

## State worth externalizing

| Area | In memory today | Risk if it lives only in-process |
|------|-----------------|-----------------------------------|
| Episodes | `NarrativeMemory` | Total loss on restart |
| Identity | `NarrativeIdentityTracker` | Same |
| Forgiveness / load | `AlgorithmicForgiveness`, `WeaknessPole` | Unsaved drift |
| Chat STM | `WorkingMemory` | Short by design; may stay session-only |
| Immortality | `ImmortalityProtocol` | Snapshots are conceptually “backup”; real storage still needed |
| Variability | `VariabilityEngine` (seed) | Reproducibility across environments |

## Reproducible baseline

- **`AugenesisEngine`** stays **optional** and outside the default `process` / `execute_sleep` loop (see [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)). Synthetic-profile experiments must not mix with the validation baseline without explicit opt-in.
- A persistent runtime should **version the snapshot schema** (episodes + identity + metadata) and ship incremental migration tests.

## Current implementation (Phase 2 — MVP)

- **`src/persistence/`** — `KernelSnapshotV1` + `extract_snapshot` / `apply_snapshot` (mutable kernel state without changing ethical algorithms).
- **`JsonFilePersistence`** — save/load UTF-8 JSON at a configurable path (`save` / `load` / `load_into_kernel`).
- **`SqlitePersistence`** (`sqlite_store.py`) — same DTO as one JSON row in SQLite (useful if queries or metadata are added later).
- **`checkpoint.py`** — WebSocket integration: load on session open, save on close, autosave every N episodes (`KERNEL_CHECKPOINT_*` env vars).

## Encryption at rest (future; not in current MVP)

JSON and SQLite checkpoints in the repo are **unencrypted**: fine for local dev and tests. For **deployments** where snapshots may hold personal data or sensitive audit trails, **at-rest encryption** will be required (e.g. a layer on the file or blob before SQLite write). In Python this often uses the **`cryptography`** library (Fernet, AES-GCM, or another scheme matched to the threat model); **key material must never** be committed to the repo.

**Status:** no `cryptography` dependency or crypto code in the MVP yet; when added, prefer encrypted ↔ kernel roundtrip tests and key-rotation notes. Until then, treat checkpoint files as **limited confidentiality**.

## Recommended boundaries (hexagonal, incremental)

1. **Persistence port** — the v1 DTO is a full snapshot; future adapters (SQLite today; **encryption as a future wrapper**) can map to the same schema or `schema_version++`.
2. **LLM port** — already implicit in `LLMModule`; a second provider forces clear boundaries.
3. **Service process** — `chat_server` as the WebSocket front; optional workers for scheduled `execute_sleep` without blocking chat.

## Operations and deployment

- Health checks (`/health` on `chat_server`) and per-instance connection limits.
- One kernel per WebSocket connection suits isolation; multi-tenant runtimes would need strong state separation and quotas.

## Phased plan (detail)

Staged delivery: **runtime first**, then **persistence/DB**, then **local LLM (Ollama)** — with explicit ethical limits each phase. See [RUNTIME_PHASES.md](RUNTIME_PHASES.md).

**Runtime contract (Phase 1):** [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

## Suggested next steps

1. Define a **minimal snapshot DTO** (JSON or msgpack serializable) aligned with what `ImmortalityProtocol` / episodes already expose.
2. Add a **filesystem** adapter behind the port without changing `EthicalKernel.process`.
3. Idempotence tests: restore → same ethical behavior on fixed scenarios (same variability seed).

When this is reflected in code, update [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) and the README with the default adapter path.
