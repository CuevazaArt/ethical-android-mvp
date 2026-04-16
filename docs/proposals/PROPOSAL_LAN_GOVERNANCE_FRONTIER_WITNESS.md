# PROPOSAL — LAN governance frontier witnesses (advisory aggregate)

**Status:** Implemented (deterministic aggregation + echo).  
**Language:** English (repository policy).  
**Code:** [`src/modules/lan_governance_merge_context.py`](../../src/modules/lan_governance_merge_context.py) · LAN batch handlers in [`src/chat_server.py`](../../src/chat_server.py).

## Evidence posture

`merge_context.frontier_witnesses` carries **peer-claimed** `observed_max_turn` values keyed by `claimant_session_id`. The kernel:

- Validates each entry (`lan_governance_frontier_witness_v1`).
- Keeps at most **16** inputs per batch (extras truncated with `merge_context_warnings`).
- **Dedupes** by `claimant_session_id`, keeping the **maximum** `observed_max_turn`.
- Emits sorted witnesses (by `claimant_session_id`) under `merge_context_echo.frontier_witness_resolution` with:
  - `advisory_max_observed_turn` — max over surviving claims
  - `evidence_posture` — **`advisory_aggregate_not_quorum`**

This is **not** a quorum proof, BFT vote, or replicated consensus. It does **not** change merge behavior unless the operator also sets `merge_context.frontier_turn` (local stale detection). Hubs may use the advisory field for logging, dashboards, or **manual** policy only.

## Schema (`lan_governance_frontier_witness_v1`)

| Field | Required | Notes |
|-------|----------|--------|
| `schema` | Yes | `lan_governance_frontier_witness_v1` |
| `claimant_session_id` | Yes | Non-empty string, max 200 chars |
| `observed_max_turn` | No | Non-negative int (default coerced to 0) |

## Related

- [`PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md)  
- [`PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md)  
- [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) (Phase 3 anchor utility: `scripts/eval/compare_audit_ledger_anchor.py`)

## Changelog

- **2026-04-16:** Initial implementation (DJ-BL-16).
