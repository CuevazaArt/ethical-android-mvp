# ADR 0007 — Kernel snapshot schema migration policy

**Status:** Accepted (April 2026)  
**Context:** `KernelSnapshotV1` is serialized to JSON (checkpoints, `JsonFilePersistence`, SQLite adapter). Loads must remain compatible across releases. Implementation lives in [`src/persistence/migrations.py`](../../src/persistence/migrations.py) and [`src/persistence/schema.py`](../../src/persistence/schema.py).

## Decision

When bumping **`SCHEMA_VERSION`** (in `schema.py`) or adding **required** persisted fields that older files cannot omit:

1. **Extend the dataclass** [`KernelSnapshotV1`](../../src/persistence/schema.py) with defaults where backward compatibility allows; otherwise document a breaking bump and increment `SCHEMA_VERSION`.
2. **Add an explicit migration step** in [`migrations.py`](../../src/persistence/migrations.py): either a new `migrate_vN_to_vN+1` or an extension to `apply_schema3_defaults` / the `migrate_raw_to_current` loop, so every supported on-disk version maps to the current schema without silent data loss.
3. **Add a minimal golden fixture** under [`tests/fixtures/snapshots/`](../../tests/fixtures/snapshots/) for the lowest version affected (or the new version), containing only fields needed to exercise the migration path.
4. **Add or extend regression tests** in [`tests/test_persistence_migration.py`](../../tests/test_persistence_migration.py) (and existing persistence tests as needed) so CI fails if migration logic drifts from `extract_snapshot` / `apply_snapshot` expectations.
5. **Keep `snapshot_from_dict`** as a thin wrapper: [`migrate_raw_to_current`](../../src/persistence/migrations.py) then `KernelSnapshotV1(**merged)` — do not duplicate migration rules in `json_store.py` beyond that call.
6. **Validate after construct:** [`validate_snapshot_for_apply`](../../src/persistence/snapshot_validate.py) runs JSON Schema ([`kernel_snapshot_v3.schema.json`](../../src/persistence/schemas/kernel_snapshot_v3.schema.json)) on the explicit serde dict from [`kernel_snapshot_to_json_dict`](../../src/persistence/snapshot_serde.py) before `apply_snapshot` mutates the kernel, and after `snapshot_from_dict` builds the DTO.
7. **Atomic disk writes:** [`JsonFilePersistence.save`](../../src/persistence/json_store.py) writes via a temp file + `os.replace` under an advisory file lock ([`file_lock.py`](../../src/persistence/file_lock.py)). [`SqlitePersistence.save`](../../src/persistence/sqlite_store.py) uses `BEGIN IMMEDIATE` for a reserved DB lock during the upsert.
8. **Explicit field serde:** Prefer [`snapshot_serde.py`](../../src/persistence/snapshot_serde.py) helpers over root `dataclasses.asdict` on `KernelSnapshotV1` so persisted fields stay deliberate; advisory-only blobs are described in the JSON Schema `description` fields.

## Consequences

- **Positive:** Clear checklist for contributors; golden files catch missing `setdefault` / wrong keys when restoring old checkpoints.
- **Negative:** Each schema bump requires coordinated edits (schema + migrations + tests + fixture); avoids ad hoc `asdict`-only changes without a migration story.

## Links

- [`src/persistence/kernel_io.py`](../../src/persistence/kernel_io.py) — `extract_snapshot` / `apply_snapshot`  
- [`src/persistence/json_store.py`](../../src/persistence/json_store.py) — `snapshot_from_dict`  
- [`RUNTIME_PERSISTENT.md`](../proposals/RUNTIME_PERSISTENT.md) — persistence design notes
