"""JSON file persistence adapter."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

from .atomic_io import atomic_write_bytes
from .file_lock import advisory_file_lock
from .kernel_io import apply_snapshot
from .migrations import migrate_raw_to_current
from .schema import KernelSnapshotV1
from .snapshot_serde import kernel_snapshot_to_json_dict
from .snapshot_validate import validate_snapshot_for_apply

_log = logging.getLogger(__name__)


def fernet_key_from_env() -> bytes | None:
    """
    URL-safe base-64 key from ``KERNEL_CHECKPOINT_FERNET_KEY`` (same format as
    ``cryptography.fernet.Fernet.generate_key().decode()``). If unset, checkpoints are plain UTF-8 JSON.
    """
    raw = os.environ.get("KERNEL_CHECKPOINT_FERNET_KEY", "").strip()
    if not raw:
        return None
    return raw.encode("ascii")


def snapshot_from_dict(raw: dict) -> KernelSnapshotV1:
    merged = migrate_raw_to_current(raw)
    snap = KernelSnapshotV1(**merged)
    validate_snapshot_for_apply(snap)
    return snap


class JsonFilePersistence:
    """
    Save/load :class:`KernelSnapshotV1` as UTF-8 JSON, or **Fernet-encrypted** bytes when
    ``KERNEL_CHECKPOINT_FERNET_KEY`` is set (at-rest confidentiality for local files).

    Load tries decrypt first when a key is present; if that fails, falls back to plain JSON
    (migration from unencrypted checkpoints).
    """

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def save(self, snapshot: KernelSnapshotV1) -> None:
        validate_snapshot_for_apply(snapshot)
        lock = self.path.with_suffix(self.path.suffix + ".lock")
        text = json.dumps(
            kernel_snapshot_to_json_dict(snapshot),
            indent=2,
            ensure_ascii=False,
        )
        payload = text.encode("utf-8")
        key = fernet_key_from_env()
        if key:
            payload = Fernet(key).encrypt(payload)
        with advisory_file_lock(lock):
            atomic_write_bytes(self.path, payload)

    def load(self) -> KernelSnapshotV1 | None:
        if not self.path.is_file():
            return None
        blob = self.path.read_bytes()
        key = fernet_key_from_env()
        if key:
            try:
                text = Fernet(key).decrypt(blob).decode("utf-8")
            except (InvalidToken, UnicodeDecodeError, ValueError) as exc:
                # Wrong key, legacy plain JSON, or non-UTF8 decrypt output — last resort: UTF-8 file body.
                _log.info(
                    "Checkpoint %s: Fernet path unusable; loading as plain UTF-8 JSON (legacy/migration or key mismatch): %s",
                    self.path,
                    exc,
                )
                text = blob.decode("utf-8")
        else:
            text = blob.decode("utf-8")
        raw = json.loads(text)
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
