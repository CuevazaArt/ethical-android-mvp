"""
Deterministic merge for governance-style events (Phase 2 LAN simulation stub).

When multiple nodes or retries deliver the **same** logical event out of order or twice,
operators need a **replayable** ordering and **idempotent** deduplication before any future
coordinator persists state. This module is pure logic — it does **not** perform I/O or
override MalAbs / L0. See ``docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md``.

**Evidence posture:** ordering keys are ``turn_index`` and ``processor_elapsed_ms`` (aligned
with ``temporal_sync_v1``). Events without ``id_key`` are **skipped** (caller must tag events).
"""
# Status: SCAFFOLD


from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from src.modules.governance.lan_governance_conflict_taxonomy import (
    CONFLICT_DIFFERENT_CLOCK,
    CONFLICT_SAME_TURN,
    CONFLICT_STALE_EVENT,
    merge_lan_governance_events_detailed,
)

__all__ = (
    "CONFLICT_DIFFERENT_CLOCK",
    "CONFLICT_SAME_TURN",
    "CONFLICT_STALE_EVENT",
    "merge_lan_governance_events",
    "merge_lan_governance_events_detailed",
)


def merge_lan_governance_events(
    events: Sequence[Mapping[str, Any]],
    *,
    id_key: str = "event_id",
    frontier_turn: int | None = None,
) -> list[dict[str, Any]]:
    """
    Sort by ``(turn_index, processor_elapsed_ms, id)``, then dedupe by ``id_key`` (first wins).

    Skips rows where ``id_key`` is missing or empty after strip — callers must assign stable ids
    for cross-node correlation (e.g. dossier / audit reference).

    When ``frontier_turn`` is set, rows with ``turn_index < frontier_turn`` are dropped as
    ``stale_event`` (see ``merge_lan_governance_events_detailed``).
    """
    return merge_lan_governance_events_detailed(events, id_key=id_key, frontier_turn=frontier_turn)[
        "merged"
    ]
