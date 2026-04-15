"""Contract tests for lan_governance_envelope_v1."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.lan_governance_envelope import (
    LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
    normalize_lan_governance_envelope,
)


def test_envelope_normalize_ok():
    raw = {
        "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
        "node_id": "node-1",
        "sent_unix_ms": 1710000000000,
        "kind": "integrity_batch",
        "batch": {"events": [{"event_id": "e1"}]},
    }
    norm, err = normalize_lan_governance_envelope(raw)
    assert err is None
    assert norm is not None
    assert norm["schema"] == LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1
    assert norm["kind"] == "integrity_batch"


def test_envelope_invalid_schema():
    norm, err = normalize_lan_governance_envelope(
        {
            "schema": "bad",
            "node_id": "n",
            "sent_unix_ms": 1,
            "kind": "dao_batch",
            "batch": {"events": []},
        }
    )
    assert norm is None
    assert err is not None
    assert err.get("error") == "unsupported_schema"


def test_envelope_invalid_kind():
    norm, err = normalize_lan_governance_envelope(
        {
            "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
            "node_id": "n",
            "sent_unix_ms": 1,
            "kind": "unknown",
            "batch": {"events": []},
        }
    )
    assert norm is None
    assert err is not None
    assert err.get("error") == "unsupported_kind"
