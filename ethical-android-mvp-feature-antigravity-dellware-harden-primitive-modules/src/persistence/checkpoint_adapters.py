"""Concrete :class:`CheckpointPersistencePort` implementations for JSON and SQLite stores."""

from __future__ import annotations

from pathlib import Path

from .json_store import JsonFilePersistence
from .kernel_io import extract_snapshot
from .sqlite_store import SqlitePersistence


class JsonFileCheckpointAdapter:
    """File-backed checkpoint using :class:`JsonFilePersistence` (Fernet optional via env)."""

    def __init__(self, path: Path | str) -> None:
        self._store = JsonFilePersistence(path)

    def load_into_kernel(self, kernel) -> bool:
        return self._store.load_into_kernel(kernel)

    def save_from_kernel(self, kernel) -> bool:
        self._store.save(extract_snapshot(kernel))
        return True


class SqliteCheckpointAdapter:
    """SQLite-backed checkpoint using :class:`SqlitePersistence`."""

    def __init__(self, path: Path | str) -> None:
        self._store = SqlitePersistence(path)

    def load_into_kernel(self, kernel) -> bool:
        return self._store.load_into_kernel(kernel)

    def save_from_kernel(self, kernel) -> bool:
        self._store.save(extract_snapshot(kernel))
        return True
