"""Atomic file replace (write temp then os.replace) for checkpoint durability."""

from __future__ import annotations

import os
from pathlib import Path

__all__ = ["atomic_write_bytes"]


def _try_unlink_tmp(p: Path) -> None:
    """Best-effort remove of a temp segment file; ignore races (e.g. Windows)."""
    try:
        p.unlink(missing_ok=True)
    except OSError:
        pass


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """
    Write ``data`` to ``path`` atomically (same filesystem).

    Uses a sibling ``*.tmp.<pid>`` file then :func:`os.replace` so readers never see a half-written checkpoint.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp.{os.getpid()}")
    try:
        tmp.write_bytes(data)
        os.replace(tmp, path)
    except (OSError, TypeError):
        # Best-effort remove partial temp; re-raise so callers see the real I/O or type error.
        _try_unlink_tmp(tmp)
        raise
