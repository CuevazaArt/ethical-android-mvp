"""Unit tests for LAN governance merge conflict taxonomy (Phase 2)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.lan_governance_conflict_taxonomy import (
    CONFLICT_DIFFERENT_CLOCK,
    CONFLICT_SAME_TURN,
    CONFLICT_STALE_EVENT,
    event_content_fingerprint,
    merge_lan_governance_events_detailed,
)


def test_detailed_benign_duplicate_no_conflict() -> None:
    one = {
        "event_id": "a",
        "turn_index": 1,
        "processor_elapsed_ms": 0,
        "payload": "x",
    }
    dup = dict(one)
    dup["processor_elapsed_ms"] = 50
    r = merge_lan_governance_events_detailed([one, dup])
    assert len(r["merged"]) == 1
    assert r["conflicts"] == []


def test_same_turn_divergent_payload() -> None:
    r = merge_lan_governance_events_detailed(
        [
            {
                "event_id": "x",
                "turn_index": 2,
                "processor_elapsed_ms": 0,
                "v": 1,
            },
            {
                "event_id": "x",
                "turn_index": 2,
                "processor_elapsed_ms": 10,
                "v": 2,
            },
        ]
    )
    assert len(r["merged"]) == 1
    assert r["merged"][0]["v"] == 1
    assert len(r["conflicts"]) == 1
    assert r["conflicts"][0]["kind"] == CONFLICT_SAME_TURN


def test_different_turn_divergent_payload_is_different_clock() -> None:
    r = merge_lan_governance_events_detailed(
        [
            {
                "event_id": "x",
                "turn_index": 2,
                "processor_elapsed_ms": 0,
                "v": 1,
            },
            {
                "event_id": "x",
                "turn_index": 3,
                "processor_elapsed_ms": 0,
                "v": 2,
            },
        ]
    )
    assert len(r["merged"]) == 1
    assert r["merged"][0]["turn_index"] == 2
    assert r["conflicts"][0]["kind"] == CONFLICT_DIFFERENT_CLOCK


def test_different_turn_identical_payload_is_stale_event() -> None:
    row = {
        "event_id": "x",
        "turn_index": 1,
        "processor_elapsed_ms": 0,
        "v": 1,
    }
    late = dict(row)
    late["turn_index"] = 2
    r = merge_lan_governance_events_detailed([late, row])
    assert len(r["merged"]) == 1
    assert r["merged"][0]["turn_index"] == 1
    assert r["conflicts"][0]["kind"] == CONFLICT_STALE_EVENT
    assert r["conflicts"][0]["reason"] == "duplicate_id_later_turn_identical_payload"


def test_frontier_turn_stale() -> None:
    r = merge_lan_governance_events_detailed(
        [
            {
                "event_id": "a",
                "turn_index": 1,
                "processor_elapsed_ms": 0,
            },
        ],
        frontier_turn=2,
    )
    assert r["merged"] == []
    assert r["conflicts"][0]["kind"] == CONFLICT_STALE_EVENT
    assert r["conflicts"][0]["reason"] == "below_frontier_turn"


def test_content_fingerprint_ignores_ordering_fields() -> None:
    a = {"event_id": "z", "turn_index": 1, "processor_elapsed_ms": 9, "k": 1}
    b = {"event_id": "z", "turn_index": 99, "processor_elapsed_ms": 0, "k": 1}
    assert event_content_fingerprint(a, "event_id") == event_content_fingerprint(b, "event_id")
