"""SQLite persistence adapter — same DTO as JSON, one row blob (Fase 2.2b)."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from .json_store import snapshot_from_dict
from .kernel_io import apply_snapshot
from .schema import KernelSnapshotV1
from .snapshot_serde import kernel_snapshot_to_json_dict
from .snapshot_validate import validate_snapshot_for_apply


def _connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(path))
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS kernel_snapshot (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            json_blob TEXT NOT NULL
        )
        """
    )


class SqlitePersistence:
    """
    Save/load :class:`KernelSnapshotV1` as a single JSON row in SQLite.

    For local single-user checkpoints; same concurrency caveats as
    :class:`JsonFilePersistence` if multiple writers share one file.
    Unencrypted at rest in the MVP; future encryption layer documented in
    docs/proposals/RUNTIME_PERSISTENT.md (planned ``cryptography``).
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def save(self, snapshot: KernelSnapshotV1) -> None:
        validate_snapshot_for_apply(snapshot)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(kernel_snapshot_to_json_dict(snapshot), ensure_ascii=False)
        with _connect(self.path) as conn:
            _ensure_schema(conn)
            conn.execute("BEGIN IMMEDIATE")
            conn.execute(
                """
                INSERT INTO kernel_snapshot (id, json_blob) VALUES (1, ?)
                ON CONFLICT(id) DO UPDATE SET json_blob = excluded.json_blob
                """,
                (raw,),
            )
            conn.commit()

    def load(self) -> KernelSnapshotV1 | None:
        if not self.path.is_file():
            return None
        with _connect(self.path) as conn:
            _ensure_schema(conn)
            row = conn.execute("SELECT json_blob FROM kernel_snapshot WHERE id = 1").fetchone()
        if row is None:
            return None
        return snapshot_from_dict(json.loads(row[0]))

    def load_into_kernel(self, kernel) -> bool:
        snap = self.load()
        if snap is None:
            return False
        apply_snapshot(kernel, snap)
        return True
