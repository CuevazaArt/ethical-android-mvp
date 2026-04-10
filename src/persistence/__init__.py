"""
Persistence layer — optional snapshot of kernel state (Phase 2).

Does not change ethical policy; only serializes/restores state for long-lived runtimes.
"""

from .checkpoint import (
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
    try_save_checkpoint,
)
from .json_store import JsonFilePersistence, snapshot_from_dict
from .kernel_io import apply_snapshot, extract_snapshot
from .schema import SCHEMA_VERSION, KernelSnapshotV1

__all__ = [
    "SCHEMA_VERSION",
    "KernelSnapshotV1",
    "extract_snapshot",
    "apply_snapshot",
    "JsonFilePersistence",
    "snapshot_from_dict",
    "try_load_checkpoint",
    "try_save_checkpoint",
    "init_session_checkpoint_state",
    "maybe_autosave_episodes",
    "on_websocket_session_end",
]
