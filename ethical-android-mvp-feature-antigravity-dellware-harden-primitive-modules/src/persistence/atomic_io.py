"""Atomic file replace (write temp then os.replace) for checkpoint durability."""

from __future__ import annotations

import os
from pathlib import Path


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
    except Exception:
        try:
            tmp.unlink(missing_ok=True)
        except OSError:
            pass
        raise
