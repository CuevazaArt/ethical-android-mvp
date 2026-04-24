"""
LAN governance event conflict taxonomy (Phase 2, per-session merge).

Classifies **drops** during deterministic merge of governance-style events when duplicate
``event_id`` values appear with inconsistent temporal or payload cues. This is **pure**
logic for operator diagnostics — it does **not** implement cross-session quorum, global
clocks, or chain consensus.

Conflict kinds (stable string values for JSON):

- ``same_turn`` — same ``event_id`` and ``turn_index`` but **different** payload fingerprint
  (concurrent edits in one turn). First row in sort order wins.
- ``different_clock`` — same ``event_id`` observed under **different** ``turn_index`` with
  **different** payload fingerprints (ordering / skew across nodes). Earlier ``turn_index``
  wins.
- ``stale_event`` — row is below an operator-supplied ``frontier_turn``, or same ``event_id``
  reappears in a **later** ``turn_index`` with an **identical** payload fingerprint (late replay).

See ``docs/proposals/PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md``.
"""
# Status: SCAFFOLD

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping, Sequence
from typing import Any

CONFLICT_SAME_TURN = "same_turn"
CONFLICT_DIFFERENT_CLOCK = "different_clock"
CONFLICT_STALE_EVENT = "stale_event"


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


def event_content_fingerprint(row: Mapping[str, Any], id_key: str) -> str:
    """
    Stable digest of row content excluding ordering fields and the correlation id column.

    Uses the same JSON canonicalization style as other LAN fingerprints.
    """
    skip = {id_key, "turn_index", "processor_elapsed_ms"}
    payload = {k: row[k] for k in sorted(row.keys(), key=lambda x: str(x)) if k not in skip}
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def merge_lan_governance_events_detailed(
    events: Sequence[Mapping[str, Any]],
    *,
    id_key: str = "event_id",
    frontier_turn: int | None = None,
) -> dict[str, Any]:
    """
    Sort by ``(turn_index, processor_elapsed_ms, event_id)``, dedupe, and report conflicts.

    Skips rows with missing/empty ``id_key`` (same as ``merge_lan_governance_events``).
    """
    if not events:
        return {
            "merged": [],
            "conflicts": [],
            "conflict_counts": {
                CONFLICT_SAME_TURN: 0,
                CONFLICT_DIFFERENT_CLOCK: 0,
                CONFLICT_STALE_EVENT: 0,
            },
        }

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

    merged: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    counts = {CONFLICT_SAME_TURN: 0, CONFLICT_DIFFERENT_CLOCK: 0, CONFLICT_STALE_EVENT: 0}
    accepted: dict[str, tuple[int, int, str]] = {}

    for _sk, row in keyed:
        eid = str(row.get(id_key, "") or "").strip()
        tid = _as_int(row.get("turn_index"), 0)
        pe = _as_int(row.get("processor_elapsed_ms"), 0)
        cfp = event_content_fingerprint(row, id_key)

        if frontier_turn is not None and tid < frontier_turn:
            conflicts.append(
                {
                    "kind": CONFLICT_STALE_EVENT,
                    "event_id": eid,
                    "reason": "below_frontier_turn",
                    "dropped_turn_index": tid,
                    "dropped_processor_elapsed_ms": pe,
                    "frontier_turn": frontier_turn,
                    "content_fingerprint": cfp,
                }
            )
            counts[CONFLICT_STALE_EVENT] += 1
            continue

        if eid not in accepted:
            merged.append(row)
            accepted[eid] = (tid, pe, cfp)
            continue

        kept_turn, kept_pe, kept_fp = accepted[eid]
        if tid == kept_turn and cfp == kept_fp:
            continue

        if tid == kept_turn and cfp != kept_fp:
            conflicts.append(
                {
                    "kind": CONFLICT_SAME_TURN,
                    "event_id": eid,
                    "reason": "duplicate_id_same_turn_divergent_payload",
                    "kept_turn_index": kept_turn,
                    "kept_processor_elapsed_ms": kept_pe,
                    "dropped_turn_index": tid,
                    "dropped_processor_elapsed_ms": pe,
                    "kept_content_fingerprint": kept_fp,
                    "dropped_content_fingerprint": cfp,
                }
            )
            counts[CONFLICT_SAME_TURN] += 1
            continue

        if cfp == kept_fp:
            conflicts.append(
                {
                    "kind": CONFLICT_STALE_EVENT,
                    "event_id": eid,
                    "reason": "duplicate_id_later_turn_identical_payload",
                    "kept_turn_index": kept_turn,
                    "kept_processor_elapsed_ms": kept_pe,
                    "dropped_turn_index": tid,
                    "dropped_processor_elapsed_ms": pe,
                    "content_fingerprint": cfp,
                }
            )
            counts[CONFLICT_STALE_EVENT] += 1
            continue

        conflicts.append(
            {
                "kind": CONFLICT_DIFFERENT_CLOCK,
                "event_id": eid,
                "reason": "duplicate_id_different_turn_divergent_payload",
                "kept_turn_index": kept_turn,
                "kept_processor_elapsed_ms": kept_pe,
                "dropped_turn_index": tid,
                "dropped_processor_elapsed_ms": pe,
                "kept_content_fingerprint": kept_fp,
                "dropped_content_fingerprint": cfp,
            }
        )
        counts[CONFLICT_DIFFERENT_CLOCK] += 1

    return {"merged": merged, "conflicts": conflicts, "conflict_counts": counts}
