"""Tests for LAN merge_context parsing and cross-session hint (Phase 2)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.lan_governance_merge_context import (
    LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1,
    LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
    normalize_cross_session_hint,
    parse_lan_merge_context,
)


def test_normalize_cross_session_hint_minimal() -> None:
    h, err = normalize_cross_session_hint(
        {"schema": LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1, "claimant_session_id": "sess-a"}
    )
    assert err is None
    assert h is not None
    assert h["claimant_session_id"] == "sess-a"


def test_normalize_cross_session_hint_with_participants() -> None:
    h, err = normalize_cross_session_hint(
        {
            "schema": LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1,
            "claimant_session_id": "hub",
            "quorum_ref": "run-1",
            "claimed_frontier_turn": 3,
            "participant_sessions": ["a", "b"],
        }
    )
    assert err is None
    assert h is not None
    assert h["quorum_ref"] == "run-1"
    assert h["claimed_frontier_turn"] == 3
    assert h["participant_sessions"] == ["a", "b"]


def test_parse_merge_context_rejects_bad_hint_with_warning() -> None:
    p = parse_lan_merge_context(
        {
            "merge_context": {
                "frontier_turn": 2,
                "cross_session_hint": {"schema": "wrong", "claimant_session_id": "x"},
            }
        }
    )
    assert p.frontier_turn == 2
    assert p.cross_session_hint is None
    assert any("cross_session_hint_rejected" in w for w in p.warnings)


def test_parse_merge_context_valid_hint() -> None:
    p = parse_lan_merge_context(
        {
            "merge_context": {
                "cross_session_hint": {
                    "schema": LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1,
                    "claimant_session_id": "peer-1",
                },
            }
        }
    )
    assert p.cross_session_hint is not None
    assert p.frontier_witnesses == ()
    assert p.warnings == ()


def test_frontier_witnesses_dedupe_by_claimant_max_turn() -> None:
    p = parse_lan_merge_context(
        {
            "merge_context": {
                "frontier_witnesses": [
                    {
                        "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
                        "claimant_session_id": "b",
                        "observed_max_turn": 3,
                    },
                    {
                        "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
                        "claimant_session_id": "b",
                        "observed_max_turn": 7,
                    },
                    {
                        "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
                        "claimant_session_id": "a",
                        "observed_max_turn": 5,
                    },
                ],
            }
        }
    )
    assert len(p.frontier_witnesses) == 2
    assert p.frontier_witnesses[0]["claimant_session_id"] == "a"
    assert p.frontier_witnesses[0]["observed_max_turn"] == 5
    assert p.frontier_witnesses[1]["claimant_session_id"] == "b"
    assert p.frontier_witnesses[1]["observed_max_turn"] == 7
    assert p.witness_advisory_max_turn == 7


def test_frontier_witnesses_invalid_entry_warns() -> None:
    p = parse_lan_merge_context(
        {
            "merge_context": {
                "frontier_witnesses": [
                    {"schema": "bad", "claimant_session_id": "x", "observed_max_turn": 1},
                    {
                        "schema": LAN_GOVERNANCE_FRONTIER_WITNESS_SCHEMA_V1,
                        "claimant_session_id": "ok",
                        "observed_max_turn": 2,
                    },
                ],
            }
        }
    )
    assert len(p.frontier_witnesses) == 1
    assert p.frontier_witnesses[0]["claimant_session_id"] == "ok"
    assert any("frontier_witness_rejected" in w for w in p.warnings)
