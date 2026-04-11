"""JSON file persistence adapter."""

from __future__ import annotations

import json
import os
from dataclasses import asdict
from pathlib import Path
from typing import Optional

from .kernel_io import apply_snapshot
from .schema import SCHEMA_VERSION, KernelSnapshotV1


def fernet_key_from_env() -> Optional[bytes]:
    """
    URL-safe base-64 key from ``KERNEL_CHECKPOINT_FERNET_KEY`` (same format as
    ``cryptography.fernet.Fernet.generate_key().decode()``). If unset, checkpoints are plain UTF-8 JSON.
    """
    raw = os.environ.get("KERNEL_CHECKPOINT_FERNET_KEY", "").strip()
    if not raw:
        return None
    return raw.encode("ascii")


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
    merged.setdefault("metaplan_goals", [])
    merged.setdefault("somatic_marker_weights", {})
    merged.setdefault("skill_learning_tickets", [])
    merged.setdefault("user_model_frustration_streak", 0)
    merged.setdefault("user_model_premise_concern_streak", 0)
    merged.setdefault("user_model_last_circle", "neutral_soto")
    merged.setdefault("user_model_turns_observed", 0)
    merged.setdefault("subjective_turn_index", 0)
    merged.setdefault("subjective_stimulus_ema", 0.55)
    return KernelSnapshotV1(**merged)


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
        self.path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(asdict(snapshot), indent=2, ensure_ascii=False)
        key = fernet_key_from_env()
        if key:
            from cryptography.fernet import Fernet

            self.path.write_bytes(Fernet(key).encrypt(text.encode("utf-8")))
        else:
            with open(self.path, "w", encoding="utf-8") as f:
                f.write(text)

    def load(self) -> Optional[KernelSnapshotV1]:
        if not self.path.is_file():
            return None
        blob = self.path.read_bytes()
        key = fernet_key_from_env()
        if key:
            from cryptography.fernet import Fernet

            try:
                text = Fernet(key).decrypt(blob).decode("utf-8")
            except Exception:
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
