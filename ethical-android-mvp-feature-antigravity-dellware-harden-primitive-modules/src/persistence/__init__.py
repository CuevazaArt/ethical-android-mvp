"""
Persistence layer — optional snapshot of kernel state (Phase 2).

Does not change ethical policy; only serializes/restores state for long-lived runtimes.
"""

from .checkpoint import (
    checkpoint_persistence_from_env,
    init_session_checkpoint_state,
    maybe_autosave_episodes,
    on_websocket_session_end,
    try_load_checkpoint,
    try_save_checkpoint,
)
from .checkpoint_adapters import JsonFileCheckpointAdapter, SqliteCheckpointAdapter
from .checkpoint_port import CheckpointPersistencePort
from .json_store import JsonFilePersistence, fernet_key_from_env, snapshot_from_dict
from .kernel_io import apply_snapshot, extract_snapshot
from .migrations import (
    apply_schema3_defaults,
    migrate_raw_to_current,
    migrate_v1_to_v2,
    migrate_v2_to_v3,
)
from .schema import SCHEMA_VERSION, KernelSnapshotV1
from .snapshot_serde import kernel_snapshot_to_json_dict
from .snapshot_validate import validate_migrated_snapshot_dict, validate_snapshot_for_apply
from .sqlite_store import SqlitePersistence

__all__ = [
    "CheckpointPersistencePort",
    "JsonFileCheckpointAdapter",
    "SqliteCheckpointAdapter",
    "SCHEMA_VERSION",
    "KernelSnapshotV1",
    "extract_snapshot",
    "apply_snapshot",
    "JsonFilePersistence",
    "fernet_key_from_env",
    "SqlitePersistence",
    "snapshot_from_dict",
    "migrate_raw_to_current",
    "migrate_v1_to_v2",
    "migrate_v2_to_v3",
    "apply_schema3_defaults",
    "checkpoint_persistence_from_env",
    "try_load_checkpoint",
    "try_save_checkpoint",
    "init_session_checkpoint_state",
    "maybe_autosave_episodes",
    "on_websocket_session_end",
    "kernel_snapshot_to_json_dict",
    "validate_snapshot_for_apply",
    "validate_migrated_snapshot_dict",
]
