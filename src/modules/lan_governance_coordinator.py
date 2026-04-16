"""
Multi-node LAN governance coordinator contract (Phase 2 stub).

Aggregates multiple ``lan_governance_envelope_v1`` payloads under one versioned message so a
hub node can forward batches from several peers in a single WebSocket frame. Ordering is
deterministic (fingerprint sort) with duplicate fingerprint removal. This module does not
perform networking or cross-session consensus.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

from .lan_governance_envelope import (
    fingerprint_lan_governance_envelope,
    normalize_lan_governance_envelope,
)

LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1 = "lan_governance_coordinator_v1"
DEFAULT_COORDINATOR_MAX_ITEMS = 32


def fingerprint_lan_governance_coordinator(normalized: Mapping[str, Any]) -> str:
    """Deterministic hash of coordinator metadata plus ordered envelope fingerprints."""
    items = normalized.get("items")
    fps: list[str] = []
    if isinstance(items, list):
        for it in items:
            if isinstance(it, Mapping):
                fps.append(fingerprint_lan_governance_envelope(it))
    fps.sort()
    payload = {
        "schema": normalized.get("schema"),
        "coordinator_id": normalized.get("coordinator_id"),
        "coordination_run_id": normalized.get("coordination_run_id"),
        "envelope_fingerprints": fps,
    }
    body = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def normalize_lan_governance_coordinator(
    raw: object,
    *,
    max_items: int = DEFAULT_COORDINATOR_MAX_ITEMS,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """
    Validate ``lan_governance_coordinator`` payload.

    Returns ``(normalized, error)``; every item must be a valid ``lan_governance_envelope_v1``.
    """
    if not isinstance(raw, Mapping):
        return None, {"error": "invalid_payload", "hint": "expected object"}

    schema = str(raw.get("schema") or "").strip()
    if schema != LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1:
        return (
            None,
            {
                "error": "unsupported_schema",
                "hint": f"expected schema={LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1}",
            },
        )

    coordinator_id = str(raw.get("coordinator_id") or "").strip()
    if not coordinator_id:
        return None, {"error": "missing_coordinator_id", "hint": "provide non-empty coordinator_id"}

    coordination_run_id = str(raw.get("coordination_run_id") or "").strip()
    if not coordination_run_id:
        return (
            None,
            {
                "error": "missing_coordination_run_id",
                "hint": "provide non-empty coordination_run_id",
            },
        )

    items_in = raw.get("items")
    if not isinstance(items_in, list):
        return None, {"error": "invalid_items", "hint": "items must be a list"}
    if not items_in:
        return None, {"error": "items_empty", "hint": "provide at least one envelope"}
    if len(items_in) > max_items:
        return (
            None,
            {
                "error": "items_too_many",
                "hint": f"max {max_items} envelopes per coordinator message",
            },
        )

    normalized_items: list[dict[str, Any]] = []
    item_errors: list[dict[str, Any]] = []
    for idx, item in enumerate(items_in):
        norm, err = normalize_lan_governance_envelope(item)
        if err is not None:
            item_errors.append({"index": idx, **err})
            continue
        if norm is None:
            item_errors.append(
                {
                    "index": idx,
                    "error": "invalid_item",
                    "hint": "envelope normalize returned no payload",
                }
            )
            continue
        normalized_items.append(norm)

    if item_errors:
        return None, {
            "error": "item_validation_failed",
            "hint": "one or more items failed lan_governance_envelope_v1 validation",
            "item_errors": item_errors,
        }

    # Deterministic order + dedupe by envelope fingerprint (same logical batch from multiple nodes).
    keyed = [(fingerprint_lan_governance_envelope(env), env) for env in normalized_items]
    keyed.sort(key=lambda t: t[0])
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for fp, env in keyed:
        if fp in seen:
            continue
        seen.add(fp)
        deduped.append(env)

    input_count = len(normalized_items)
    deduped_count = input_count - len(deduped)

    out: dict[str, Any] = {
        "schema": LAN_GOVERNANCE_COORDINATOR_SCHEMA_V1,
        "coordinator_id": coordinator_id[:200],
        "coordination_run_id": coordination_run_id[:200],
        "items": deduped,
        "input_count": input_count,
        "deduped_count": deduped_count,
    }
    return out, None
