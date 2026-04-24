"""
MockDAO audit ledger fingerprinting (DJ-BL-01 — Phase 1 replay evidence).

Append-only ``MockDAO.records`` can be exported to a canonical JSON form and hashed so two
snapshots can be compared for **bit-exact** ledger equality (order-sensitive).

This does **not** prove blockchain integrity; it supports operator diagnostics and staged
execution Phase 1 acceptance. See ``docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md``.
"""
# Status: SCAFFOLD

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any

from src.modules.governance.mock_dao import AuditRecord


def audit_record_to_public_dict(rec: AuditRecord) -> dict[str, Any]:
    """Stable dict for serialization (all fields that define ledger row identity)."""
    return {
        "id": rec.id,
        "type": rec.type,
        "content": rec.content,
        "timestamp": rec.timestamp,
        "episode_id": rec.episode_id,
    }


def audit_rows_from_mappings(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Normalize imported JSON rows to the same key set (missing keys → None)."""
    keys = ("id", "type", "content", "timestamp", "episode_id")
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append({k: r.get(k) for k in keys})
    return out


def fingerprint_audit_ledger(
    records: Sequence[AuditRecord] | Sequence[Mapping[str, Any]],
) -> str:
    """
    SHA-256 of canonical JSON array (sorted keys per object, UTF-8, order preserved).

    Two ledgers match iff fingerprints match (same sequence and field values).
    """
    rows: list[dict[str, Any]] = []
    for r in records:
        if isinstance(r, AuditRecord):
            rows.append(audit_record_to_public_dict(r))
        else:
            rows.append(audit_rows_from_mappings([r])[0])
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
