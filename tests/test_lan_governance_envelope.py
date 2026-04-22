"""Contract tests for lan_governance_envelope_v1."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.modules.governance.lan_governance_envelope import (
    LAN_GOVERNANCE_ENVELOPE_IDEMPOTENCY_PREFIX,
    LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
    fingerprint_lan_governance_envelope,
    idempotency_token_for_envelope,
    normalize_lan_governance_envelope,
    reject_reason_for_envelope_error,
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


def test_envelope_fingerprint_is_deterministic():
    raw = {
        "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
        "node_id": "node-1",
        "sent_unix_ms": 1710000000000,
        "kind": "dao_batch",
        "batch": {"events": [{"event_id": "e1", "op": "dao_vote"}]},
    }
    norm, err = normalize_lan_governance_envelope(raw)
    assert err is None
    assert norm is not None
    fp1 = fingerprint_lan_governance_envelope(norm)
    fp2 = fingerprint_lan_governance_envelope(norm)
    assert fp1 == fp2
    assert len(fp1) == 64


def test_envelope_idempotency_token_is_deterministic():
    raw = {
        "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
        "node_id": "node-2",
        "sent_unix_ms": 1710000000001,
        "kind": "judicial_batch",
        "batch": {"events": [{"event_id": "e2", "op": "judicial_register_dossier"}]},
    }
    norm, err = normalize_lan_governance_envelope(raw)
    assert err is None
    assert norm is not None
    t1 = idempotency_token_for_envelope(norm)
    t2 = idempotency_token_for_envelope(norm)
    assert t1 == t2
    assert t1.startswith(f"{LAN_GOVERNANCE_ENVELOPE_IDEMPOTENCY_PREFIX}:")


def test_envelope_reject_reason_taxonomy_mapping():
    assert reject_reason_for_envelope_error("unsupported_schema") == "unsupported_contract"
    assert reject_reason_for_envelope_error("invalid_payload") == "schema_validation_failed"
    assert reject_reason_for_envelope_error("unknown_code") == "invalid_envelope"
