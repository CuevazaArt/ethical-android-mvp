"""
Checkpoint integration (Fase 2.4): load on session start, save on exit / periodic autosave.

Environment:

- ``KERNEL_CHECKPOINT_PATH`` — filesystem path to JSON (see :class:`JsonFilePersistence`).
  If unset, all checkpoint functions no-op.

- ``KERNEL_CHECKPOINT_LOAD`` — if ``1``/``true`` (default), try to load existing file when a
  session starts. If ``0``, never load (overwrite-only workflows).

- ``KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`` — if ``1`` (default when path is set), save when the
  WebSocket session ends. Set to ``0`` to only use periodic saves.

- ``KERNEL_CHECKPOINT_EVERY_N_EPISODES`` — if > 0, save after the episode count grows by at least
  this many new episodes since the last successful save (per connection).

**Limitation:** one kernel per WebSocket; concurrent connections sharing one file will race.
For production, use one session at a time or separate paths per client.

**Privacy:** snapshots persist narrative episodes (and related fields), not the WebSocket
``monologue`` line — that is response-only. To hide ``monologue`` from live JSON, set
``KERNEL_CHAT_EXPOSE_MONOLOGUE=0`` (see ``chat_server``).

**At-rest encryption (optional):** set ``KERNEL_CHECKPOINT_FERNET_KEY`` to a Fernet key
(same format as ``Fernet.generate_key().decode()``). :class:`JsonFilePersistence` then
writes encrypted blobs; load decrypts or falls back to plain JSON for legacy files.
See ``src/persistence/json_store.py``.

**Conduct guide export (optional):** ``KERNEL_CONDUCT_GUIDE_EXPORT_PATH`` — JSON written on
WebSocket disconnect (after checkpoint save) for edge / “small body” handoff. See
``src/modules/conduct_guide_export.py`` and ``docs/proposals/README.md``.

**Dependency injection (optional):** pass ``checkpoint_persistence`` into
:class:`src.kernel.EthicalKernel` to use a :class:`CheckpointPersistencePort` (JSON,
SQLite, or test mocks) without ``KERNEL_CHECKPOINT_PATH``. Load/save flags still
respect ``KERNEL_CHECKPOINT_LOAD`` and ``KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT``.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .checkpoint_adapters import JsonFileCheckpointAdapter
from .checkpoint_port import CheckpointPersistencePort
from .json_store import JsonFilePersistence
from .kernel_io import extract_snapshot

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def checkpoint_path_from_env() -> Path | None:
    raw = os.environ.get("KERNEL_CHECKPOINT_PATH", "").strip()
    if not raw:
        return None
    return Path(raw)


def checkpoint_persistence_from_env() -> CheckpointPersistencePort | None:
    """
    Build a JSON file checkpoint adapter when ``KERNEL_CHECKPOINT_PATH`` is set.

    Used by the chat server so the kernel uses the same injection path as tests;
    behavior matches the legacy branch that constructed :class:`JsonFilePersistence`
    inline when no port was attached.
    """
    path = checkpoint_path_from_env()
    if path is None:
        return None
    return JsonFileCheckpointAdapter(path)


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, "")
    if v == "":
        return default
    return v.lower() in ("1", "true", "yes", "on")


def should_load_checkpoint(kernel: EthicalKernel | None = None) -> bool:
    if kernel is not None and getattr(kernel, "checkpoint_persistence", None) is not None:
        return _env_bool("KERNEL_CHECKPOINT_LOAD", True)
    if checkpoint_path_from_env() is None:
        return False
    return _env_bool("KERNEL_CHECKPOINT_LOAD", True)


def should_save_on_disconnect(kernel: EthicalKernel | None = None) -> bool:
    if kernel is not None and getattr(kernel, "checkpoint_persistence", None) is not None:
        return _env_bool("KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT", True)
    if checkpoint_path_from_env() is None:
        return False
    return _env_bool("KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT", True)


def autosave_interval_episodes() -> int:
    raw = os.environ.get("KERNEL_CHECKPOINT_EVERY_N_EPISODES", "0").strip()
    try:
        n = int(raw)
    except ValueError:
        return 0
    return max(0, n)


def try_load_checkpoint(kernel: EthicalKernel) -> bool:
    """Load JSON checkpoint into ``kernel`` if configured and file exists. Returns True if loaded."""
    port = getattr(kernel, "checkpoint_persistence", None)
    if port is not None:
        if not should_load_checkpoint(kernel):
            return False
        return port.load_into_kernel(kernel)
    if not should_load_checkpoint():
        return False
    path = checkpoint_path_from_env()
    assert path is not None
    store = JsonFilePersistence(path)
    return store.load_into_kernel(kernel)


def try_save_checkpoint(kernel: EthicalKernel) -> bool:
    """Persist kernel state via injected port or ``KERNEL_CHECKPOINT_PATH``. Returns False if unset."""
    port = getattr(kernel, "checkpoint_persistence", None)
    if port is not None:
        return port.save_from_kernel(kernel)
    path = checkpoint_path_from_env()
    if path is None:
        return False
    JsonFilePersistence(path).save(extract_snapshot(kernel))
    return True


def _checkpoint_active(kernel: EthicalKernel) -> bool:
    if getattr(kernel, "checkpoint_persistence", None) is not None:
        return True
    return checkpoint_path_from_env() is not None


def maybe_autosave_episodes(
    kernel: EthicalKernel,
    session_state: dict[str, Any],
) -> None:
    """
    Save if episode count increased by ``KERNEL_CHECKPOINT_EVERY_N_EPISODES`` since last save.

    ``session_state`` must be the same dict for the WebSocket lifetime; stores key
    ``last_checkpoint_episode_count`` (int).
    """
    n = autosave_interval_episodes()
    if n <= 0 or not _checkpoint_active(kernel):
        return
    cur = len(kernel.memory.episodes)
    last = int(session_state.get("last_checkpoint_episode_count", 0))
    if cur >= last + n:
        if try_save_checkpoint(kernel):
            session_state["last_checkpoint_episode_count"] = cur


def init_session_checkpoint_state(kernel: EthicalKernel) -> dict[str, Any]:
    """Call after optional load so autosave baseline matches restored memory."""
    return {"last_checkpoint_episode_count": len(kernel.memory.episodes)}


def on_websocket_session_end(kernel: EthicalKernel) -> None:
    """Save on disconnect when enabled; optional conduct guide export for nomadic handoff."""
    if should_save_on_disconnect(kernel):
        try_save_checkpoint(kernel)
    from src.modules.governance.conduct_guide_export import try_export_conduct_guide

    try_export_conduct_guide(kernel)
