"""
Shared hash utilities for secure boot scripts.
Consolidates compute_file_hash() that was duplicated across 5+ scripts (refactoring artifact).
"""
from __future__ import annotations

import hashlib
from pathlib import Path


def compute_file_hash(path: str | Path, algorithm: str = "sha256") -> str:
    """Return hex digest of a file using the specified algorithm."""
    h = hashlib.new(algorithm)
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Cannot hash missing file: {path}")
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()
