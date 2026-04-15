"""
Deterministic merge for governance-style events (Phase 2 LAN simulation stub).

When multiple nodes or retries deliver the **same** logical event out of order or twice,
operators need a **replayable** ordering and **idempotent** deduplication before any future
coordinator persists state. This module is pure logic — it does **not** perform I/O or
override MalAbs / L0. See ``docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md``.

**Evidence posture:** ordering keys are ``turn_index`` and ``processor_elapsed_ms`` (aligned
with ``temporal_sync_v1``). Events without ``id_key`` are **skipped** (caller must tag events).
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any


def _as_int(value: object, default: int = 0) -> int:
    if value is None:
        return default
    if isinstance(value, bool):
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if math.isfinite(value) else default
    if isinstance(value, str):
        try:
            s = value.strip()
            return int(s, 10) if s else default
        except ValueError:
            return default
    return default


def merge_lan_governance_events(
    events: list[Mapping[str, Any]],
    *,
    id_key: str = "event_id",
) -> list[dict[str, Any]]:
    """
    Sort by ``(turn_index, processor_elapsed_ms, id)``, then dedupe by ``id_key`` (first wins).

    Skips rows where ``id_key`` is missing or empty after strip — callers must assign stable ids
    for cross-node correlation (e.g. dossier / audit reference).
    """
    if not events:
        return []

    keyed: list[tuple[tuple[int, int, str], dict[str, Any]]] = []
    for raw in events:
        row = dict(raw)
        eid = str(row.get(id_key, "") or "").strip()
        if not eid:
            continue
        tid = _as_int(row.get("turn_index"), 0)
        pe = _as_int(row.get("processor_elapsed_ms"), 0)
        keyed.append(((tid, pe, eid), row))

    keyed.sort(key=lambda item: item[0])

    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for _sort_key, row in keyed:
        eid = str(row.get(id_key, "") or "").strip()
        if eid in seen:
            continue
        seen.add(eid)
        out.append(row)
    return out
