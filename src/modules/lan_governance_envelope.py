"""
Versioned LAN governance envelope contract (Phase 2 coordinator schema stub).

This module validates a schema-tagged wrapper so cross-node batches can travel with
stable metadata (node id, send time, kind). It does not perform networking.
"""

from __future__ import annotations

import math
from collections.abc import Mapping
from typing import Any

LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1 = "lan_governance_envelope_v1"
SUPPORTED_LAN_GOVERNANCE_KINDS = {
    "integrity_batch",
    "dao_batch",
    "judicial_batch",
    "mock_court_batch",
}


def _as_non_negative_int(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value >= 0 else None
    if isinstance(value, float):
        if not math.isfinite(value):
            return None
        iv = int(value)
        return iv if iv >= 0 else None
    if isinstance(value, str):
        s = value.strip()
        if not s:
            return None
        try:
            iv = int(s, 10)
            return iv if iv >= 0 else None
        except ValueError:
            return None
    return None


def normalize_lan_governance_envelope(
    raw: object,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """
    Validate and normalize ``lan_governance_envelope`` payload.

    Returns ``(normalized, error)``, where ``error`` is JSON-safe and includes ``error`` + ``hint``.
    """
    if not isinstance(raw, Mapping):
        return None, {"error": "invalid_payload", "hint": "expected object"}

    schema = str(raw.get("schema") or "").strip()
    if schema != LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1:
        return (
            None,
            {
                "error": "unsupported_schema",
                "hint": f"expected schema={LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1}",
            },
        )

    node_id = str(raw.get("node_id") or "").strip()
    if not node_id:
        return None, {"error": "missing_node_id", "hint": "provide non-empty node_id"}

    sent_unix_ms = _as_non_negative_int(raw.get("sent_unix_ms"))
    if sent_unix_ms is None:
        return (
            None,
            {"error": "invalid_sent_unix_ms", "hint": "provide non-negative integer milliseconds"},
        )

    kind = str(raw.get("kind") or "").strip()
    if kind not in SUPPORTED_LAN_GOVERNANCE_KINDS:
        return (
            None,
            {
                "error": "unsupported_kind",
                "hint": (
                    "kind must be one of: " + ", ".join(sorted(SUPPORTED_LAN_GOVERNANCE_KINDS))
                ),
            },
        )

    batch = raw.get("batch")
    if not isinstance(batch, Mapping):
        return None, {"error": "invalid_batch", "hint": "batch must be object with events list"}
    events = batch.get("events")
    if not isinstance(events, list):
        return None, {"error": "events_must_be_list", "hint": "batch.events must be list"}

    out = {
        "schema": LAN_GOVERNANCE_ENVELOPE_SCHEMA_V1,
        "node_id": node_id[:200],
        "sent_unix_ms": sent_unix_ms,
        "kind": kind,
        "batch": dict(batch),
    }
    return out, None
