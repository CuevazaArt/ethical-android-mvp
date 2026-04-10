"""JSON file persistence adapter."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .kernel_io import apply_snapshot
from .schema import SCHEMA_VERSION, KernelSnapshotV1


def snapshot_from_dict(raw: dict) -> KernelSnapshotV1:
    ver = raw.get("schema_version", 0)
    merged = dict(raw)
    if ver == 1:
        merged["schema_version"] = SCHEMA_VERSION
        merged.setdefault("constitution_l1_drafts", [])
        merged.setdefault("constitution_l2_drafts", [])
    elif ver == 2:
        merged["schema_version"] = SCHEMA_VERSION
        merged.setdefault("constitution_l1_drafts", [])
        merged.setdefault("constitution_l2_drafts", [])
    elif ver == SCHEMA_VERSION:
        merged.setdefault("constitution_l1_drafts", [])
        merged.setdefault("constitution_l2_drafts", [])
    else:
        raise ValueError(
            f"Unsupported schema_version {ver!r}; expected 1, 2, or {SCHEMA_VERSION}"
        )
    merged.setdefault("dao_proposals", [])
    merged.setdefault("dao_participants", [])
    merged.setdefault("dao_proposal_counter", 0)
    if "experience_digest" not in merged:
        merged["experience_digest"] = ""
    return KernelSnapshotV1(**merged)


class JsonFilePersistence:
    """
    Save/load :class:`KernelSnapshotV1` as UTF-8 JSON.

    Intended for local single-user checkpoints. At-rest encryption is not implemented
    here; see docs/RUNTIME_PERSISTENT.md for the planned cryptography layer.
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def save(self, snapshot: KernelSnapshotV1) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(asdict(snapshot), f, indent=2, ensure_ascii=False)

    def load(self) -> Optional[KernelSnapshotV1]:
        if not self.path.is_file():
            return None
        with open(self.path, encoding="utf-8") as f:
            raw = json.load(f)
        return snapshot_from_dict(raw)

    def load_into_kernel(self, kernel) -> bool:
        """
        Load snapshot from disk and apply to ``kernel``. Returns False if no file.
        """
        snap = self.load()
        if snap is None:
            return False
        apply_snapshot(kernel, snap)
        return True
