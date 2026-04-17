"""LAN reorder + duplicate simulation for governance events (Phase 2 stub)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.lan_governance_event_merge import merge_lan_governance_events


def test_merge_sorts_by_turn_then_processor_elapsed() -> None:
    events = [
        {
            "event_id": "e2",
            "turn_index": 2,
            "processor_elapsed_ms": 0,
            "kind": "escalation",
        },
        {
            "event_id": "e1",
            "turn_index": 1,
            "processor_elapsed_ms": 100,
            "kind": "escalation",
        },
    ]
    out = merge_lan_governance_events(events)
    assert [x["event_id"] for x in out] == ["e1", "e2"]


def test_merge_stable_order_same_turn_different_elapsed() -> None:
    events = [
        {"event_id": "b", "turn_index": 5, "processor_elapsed_ms": 200},
        {"event_id": "a", "turn_index": 5, "processor_elapsed_ms": 50},
    ]
    out = merge_lan_governance_events(events)
    assert [x["event_id"] for x in out] == ["a", "b"]


def test_merge_dedupes_duplicate_event_id() -> None:
    one = {
        "event_id": "dossier-aa",
        "turn_index": 3,
        "processor_elapsed_ms": 10,
        "payload": "first",
    }
    dup = dict(one)
    dup["payload"] = "second"
    events = [one, dup]
    out = merge_lan_governance_events(events)
    assert len(out) == 1
    assert out[0]["payload"] == "first"


def test_merge_reordered_duplicates_first_wins_after_sort() -> None:
    """Late duplicate with same id: earlier turn wins (first in sorted order)."""
    late_dup = {
        "event_id": "x",
        "turn_index": 2,
        "processor_elapsed_ms": 0,
        "mark": "late",
    }
    early = {
        "event_id": "x",
        "turn_index": 1,
        "processor_elapsed_ms": 0,
        "mark": "early",
    }
    out = merge_lan_governance_events([late_dup, early])
    assert len(out) == 1
    assert out[0]["mark"] == "early"


def test_merge_skips_rows_without_event_id() -> None:
    events = [
        {"turn_index": 1, "processor_elapsed_ms": 0},
        {"event_id": "ok", "turn_index": 1, "processor_elapsed_ms": 1},
    ]
    out = merge_lan_governance_events(events)
    assert len(out) == 1
    assert out[0]["event_id"] == "ok"


def test_merge_custom_id_key() -> None:
    events = [
        {"audit_record_id": "A1", "turn_index": 1, "processor_elapsed_ms": 0},
        {"audit_record_id": "A1", "turn_index": 1, "processor_elapsed_ms": 1},
    ]
    out = merge_lan_governance_events(events, id_key="audit_record_id")
    assert len(out) == 1


def test_merge_frontier_turn_drops_stale_rows() -> None:
    events = [
        {"event_id": "old", "turn_index": 1, "processor_elapsed_ms": 0},
        {"event_id": "new", "turn_index": 2, "processor_elapsed_ms": 0},
    ]
    out = merge_lan_governance_events(events, frontier_turn=2)
    assert [r["event_id"] for r in out] == ["new"]
