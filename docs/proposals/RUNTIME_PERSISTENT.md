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
| v7 user model / subjective clock | `UserModelTracker`, `SubjectiveClock` | Included in **`KernelSnapshotV1`** (checkpoint) for continuity across reconnects; STM still not persisted |
| V11 escalation session | `EscalationSessionTracker` | **`escalation_session_strikes` / `escalation_session_idle_turns`** in snapshot (advisory strikes continuity) |
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

## Encryption at rest (optional — Fernet)

Set **`KERNEL_CHECKPOINT_FERNET_KEY`** to the string form of a Fernet key (`Fernet.generate_key().decode()`). **`JsonFilePersistence`** then encrypts the JSON snapshot at write time and decrypts on read. If decryption fails (e.g. legacy plain JSON), load falls back to UTF-8 JSON for migration.

**SQLite** rows are still plain JSON strings unless a separate wrapper is added.

**Key material must never** be committed to the repo. The `cryptography` package is a direct dependency for this path; CI runs encrypted roundtrip tests.

## Recommended boundaries (hexagonal, incremental)

1. **Persistence port** — the snapshot DTO (`KernelSnapshotV1`, **schema_version** 3: L1/L2 constitution drafts + MockDAO proposals/participants) is a full checkpoint; older JSON (**schema_version** 1 or 2) migrates with empty new fields. JSON files may use **optional Fernet** encryption via env; SQLite adapter unchanged.
2. **LLM port** — already implicit in `LLMModule`; a second provider forces clear boundaries.
3. **Service process** — `chat_server` as the WebSocket front; optional workers for scheduled `execute_sleep` without blocking chat.

## Operations and deployment

- Health checks (`/health` on `chat_server`) and per-instance connection limits.
- One kernel per WebSocket connection suits isolation; multi-tenant runtimes would need strong state separation and quotas.

## Phased plan (detail)

Staged delivery: **runtime first**, then **persistence/DB**, then **local LLM (Ollama)** — with explicit ethical limits each phase. See [RUNTIME_PHASES.md](RUNTIME_PHASES.md).

**Runtime contract (Phase 1):** [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

When this is reflected in code, update [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) and the README with the default adapter path.
