"""Contract tests for lan_governance_coordinator_v1."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.lan_governance_coordinator import (
    LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
    fingerprint_lan_governance_coordinator,
    normalize_lan_governance_coordinator,
)
from src.modules.governance.lan_governance_envelope import LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1


def _env(kind: str, node: str, ms: int, event_id: str, summary: str) -> dict:
    return {
        "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
        "node_id": node,
        "sent_unix_ms": ms,
        "kind": kind,
        "batch": {
            "events": [
                {
                    "event_id": event_id,
                    "turn_index": 1,
                    "processor_elapsed_ms": 1,
                    "summary": summary,
                }
            ]
        },
    }


def test_coordinator_normalize_ok_and_dedupes_identical_envelopes():
    dup = _env("integrity_batch", "node-a", 1, "e1", "same")
    raw = {
        "schema": LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
        "coordinator_id": "hub",
        "coordination_run_id": "run-1",
        "items": [dup, dict(dup)],
    }
    norm, err = normalize_lan_governance_coordinator(raw)
    assert err is None
    assert norm is not None
    assert norm["input_count"] == 2
    assert norm["deduped_count"] == 1
    assert len(norm["items"]) == 1


def test_coordinator_rejects_on_item_validation():
    raw = {
        "schema": LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
        "coordinator_id": "hub",
        "coordination_run_id": "run-2",
        "items": [
            _env("integrity_batch", "node-a", 1, "e1", "ok"),
            {
                "schema": "bad",
                "node_id": "x",
                "sent_unix_ms": 1,
                "kind": "integrity_batch",
                "batch": {"events": []},
            },
        ],
    }
    norm, err = normalize_lan_governance_coordinator(raw)
    assert norm is None
    assert err is not None
    assert err.get("error") == "item_validation_failed"


def test_coordinator_fingerprint_stable():
    a = _env("integrity_batch", "node-a", 10, "e1", "x")
    b = _env("integrity_batch", "node-b", 20, "e2", "y")
    raw1 = {
        "schema": LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
        "coordinator_id": "hub",
        "coordination_run_id": "run-3",
        "items": [a, b],
    }
    raw2 = {
        "schema": LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
        "coordinator_id": "hub",
        "coordination_run_id": "run-3",
        "items": [b, a],
    }
    n1, e1 = normalize_lan_governance_coordinator(raw1)
    n2, e2 = normalize_lan_governance_coordinator(raw2)
    assert e1 is None and e2 is None
    assert n1 is not None and n2 is not None
    assert fingerprint_lan_governance_coordinator(n1) == fingerprint_lan_governance_coordinator(n2)
