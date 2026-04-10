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
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from .json_store import JsonFilePersistence
from .kernel_io import extract_snapshot

if TYPE_CHECKING:
    from src.kernel import EthicalKernel


def checkpoint_path_from_env() -> Optional[Path]:
    raw = os.environ.get("KERNEL_CHECKPOINT_PATH", "").strip()
    if not raw:
        return None
    return Path(raw)


def _env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, "")
    if v == "":
        return default
    return v.lower() in ("1", "true", "yes", "on")


def should_load_checkpoint() -> bool:
    if checkpoint_path_from_env() is None:
        return False
    return _env_bool("KERNEL_CHECKPOINT_LOAD", True)


def should_save_on_disconnect() -> bool:
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


def try_load_checkpoint(kernel: "EthicalKernel") -> bool:
    """Load JSON checkpoint into ``kernel`` if configured and file exists. Returns True if loaded."""
    if not should_load_checkpoint():
        return False
    path = checkpoint_path_from_env()
    assert path is not None
    store = JsonFilePersistence(path)
    return store.load_into_kernel(kernel)


def try_save_checkpoint(kernel: "EthicalKernel") -> bool:
    """Persist current kernel state to ``KERNEL_CHECKPOINT_PATH``. Returns False if path unset."""
    path = checkpoint_path_from_env()
    if path is None:
        return False
    JsonFilePersistence(path).save(extract_snapshot(kernel))
    return True


def maybe_autosave_episodes(
    kernel: "EthicalKernel",
    session_state: Dict[str, Any],
) -> None:
    """
    Save if episode count increased by ``KERNEL_CHECKPOINT_EVERY_N_EPISODES`` since last save.

    ``session_state`` must be the same dict for the WebSocket lifetime; stores key
    ``last_checkpoint_episode_count`` (int).
    """
    n = autosave_interval_episodes()
    if n <= 0 or checkpoint_path_from_env() is None:
        return
    cur = len(kernel.memory.episodes)
    last = int(session_state.get("last_checkpoint_episode_count", 0))
    if cur >= last + n:
        if try_save_checkpoint(kernel):
            session_state["last_checkpoint_episode_count"] = cur


def init_session_checkpoint_state(kernel: "EthicalKernel") -> Dict[str, Any]:
    """Call after optional load so autosave baseline matches restored memory."""
    return {"last_checkpoint_episode_count": len(kernel.memory.episodes)}


def on_websocket_session_end(kernel: "EthicalKernel") -> None:
    """Save on disconnect when enabled."""
    if should_save_on_disconnect():
        try_save_checkpoint(kernel)
