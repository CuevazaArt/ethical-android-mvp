# PROPOSAL — LAN governance replay sidecar (Phase 2 evidence)

**Status:** Implemented (operator artifact).  
**Language:** English (repository policy).  
**Code:** [`src/modules/lan_governance_replay_sidecar.py`](../../src/modules/lan_governance_replay_sidecar.py) · CLI [`scripts/eval/verify_lan_governance_replay_sidecar.py`](../../scripts/eval/verify_lan_governance_replay_sidecar.py).

## Evidence posture

A **replay sidecar** is a JSON object derived from a saved **`lan_governance`** WebSocket fragment. It keeps merge diagnostics (`event_conflicts`, `merge_context_echo`, `merge_context_warnings`) and optionally the **`audit_ledger_fingerprint`** from the same turn so operators can:

1. Fingerprint merge/reconciliation evidence alongside the audit ledger (DJ-BL-01).
2. Compare two sidecars for equality (bit-exact canonical JSON hash).

This does **not** replace cross-session quorum or chain anchoring; it is a **local** reproducibility aid.

## Schema (`lan_governance_replay_sidecar_v1`)

- **`schema`:** `lan_governance_replay_sidecar_v1`
- **`audit_ledger_fingerprint`:** optional hex string (same algorithm as `fingerprint_audit_ledger`)
- **`batches`:** optional object with keys among `integrity_batch`, `dao_batch`, `judicial_batch`, `mock_court_batch`; each value may include `event_conflicts`, `merge_context_echo`, `merge_context_warnings` when non-empty in the source response
- **`coordinator`:** optional object with `aggregated_event_conflicts` and/or `aggregated_frontier_witness_resolutions` when present

Empty sections are omitted. Use `build_replay_sidecar_v1(lan_governance=..., audit_ledger_fingerprint=optional)` to construct from public JSON.

## CLI

```text
python scripts/eval/verify_lan_governance_replay_sidecar.py sidecar.json
python scripts/eval/verify_lan_governance_replay_sidecar.py a.json --compare b.json
python scripts/eval/verify_lan_governance_replay_sidecar.py sidecar.json --audit-ledger audit_export.json
```

## Related

- [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md)  
- [`PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md)  
- [`scripts/eval/verify_mock_dao_audit_replay.py`](../../scripts/eval/verify_mock_dao_audit_replay.py)

## Changelog

- **2026-04-16:** Initial implementation (DJ-BL-15).
