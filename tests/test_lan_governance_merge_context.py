"""Tests for LAN merge_context parsing and cross-session hint (Phase 2)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.lan_governance_merge_context import (
    LAN_GOVERNANCE_CROSS_SESSION_HINT_SCHEMA_V1,
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
    assert p.warnings == ()
