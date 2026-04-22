"""
Replay sidecar for LAN governance merge diagnostics (DJ-BL-15 — Phase 2 evidence).

Build a small JSON document from a public ``lan_governance`` fragment (e.g. saved WebSocket
payload) so operators can fingerprint **audit ledger + merge conflicts + merge context echo**
in one artifact. This does **not** prove cross-session quorum; it pairs with
``fingerprint_audit_ledger`` for local replay checks.

See ``docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`` (DJ-BL-15).
"""
# Status: SCAFFOLD


from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from typing import Any

LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1 = "lan_governance_replay_sidecar_v1"

_BATCH_KEYS = (
    "integrity_batch",
    "dao_batch",
    "judicial_batch",
    "mock_court_batch",
)


def _batch_slice(block: Mapping[str, Any]) -> dict[str, Any] | None:
    """Keep only replay-relevant keys from one batch section."""
    out: dict[str, Any] = {}
    ec = block.get("event_conflicts")
    if isinstance(ec, list) and ec:
        out["event_conflicts"] = list(ec)
    me = block.get("merge_context_echo")
    if isinstance(me, dict) and me:
        out["merge_context_echo"] = dict(me)
    mw = block.get("merge_context_warnings")
    if isinstance(mw, list) and mw:
        out["merge_context_warnings"] = list(mw)
    return out if out else None


def build_replay_sidecar_v1(
    *,
    lan_governance: Mapping[str, Any],
    audit_ledger_fingerprint: str | None = None,
) -> dict[str, Any]:
    """
    Build ``lan_governance_replay_sidecar_v1`` from a public ``lan_governance`` object.

    Omits empty sections. ``audit_ledger_fingerprint`` may be ``None`` if unknown.
    """
    batches: dict[str, Any] = {}
    for key in _BATCH_KEYS:
        block = lan_governance.get(key)
        if not isinstance(block, dict):
            continue
        sl = _batch_slice(block)
        if sl is not None:
            batches[key] = sl

    coord = lan_governance.get("coordinator")
    coord_out: dict[str, Any] | None = None
    if isinstance(coord, dict):
        coord_out = {}
        agg = coord.get("aggregated_event_conflicts")
        if isinstance(agg, list) and agg:
            coord_out["aggregated_event_conflicts"] = list(agg)
        aw = coord.get("aggregated_frontier_witness_resolutions")
        if isinstance(aw, list) and aw:
            coord_out["aggregated_frontier_witness_resolutions"] = list(aw)
        if not coord_out:
            coord_out = None

    body: dict[str, Any] = {
        "schema": LAN_GOVERNANCE_REPLAY_SIDECAR_SCHEMA_V1,
    }
    if audit_ledger_fingerprint:
        body["audit_ledger_fingerprint"] = str(audit_ledger_fingerprint)
    if batches:
        body["batches"] = batches
    if coord_out is not None:
        body["coordinator"] = coord_out

    return body


def fingerprint_replay_sidecar(sidecar: Mapping[str, Any]) -> str:
    """Deterministic SHA-256 over canonical JSON (sorted keys recursively via json.dumps)."""
    payload = json.dumps(dict(sidecar), sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def fingerprint_event_conflicts_only(conflicts: list[Mapping[str, Any]]) -> str:
    """Hash only the ``event_conflicts`` array (order-preserving, canonical JSON per row)."""
    rows = [dict(x) for x in conflicts]
    payload = json.dumps(rows, sort_keys=True, ensure_ascii=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()
