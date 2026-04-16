# PROPOSAL — LAN governance cross-session hint (Phase 2, non-consensus)

**Status:** Implemented (shape validation + echo).  
**Language:** English (repository policy).  
**Code:** [`src/modules/lan_governance_merge_context.py`](../../src/modules/lan_governance_merge_context.py) · wired in [`src/chat_server.py`](../../src/chat_server.py) LAN batch handlers.

## Evidence posture

`merge_context.cross_session_hint` lets a **hub or operator** attach opaque metadata about multi-session coordination **without** the kernel treating it as authoritative consensus.

The runtime:

- **Validates** schema and string/list bounds.
- **Echoes** the normalized object under `merge_context_echo.cross_session_hint` in batch responses.
- **Does not** use `claimed_frontier_turn` or `participant_sessions` to alter merge order, votes, or ledger writes.
- On validation failure, emits `merge_context_warnings` (e.g. `cross_session_hint_rejected:unsupported_schema`) and continues the batch.

## Schema (`lan_governance_cross_session_hint_v1`)

| Field | Required | Notes |
|-------|----------|--------|
| `schema` | Yes | Must be `lan_governance_cross_session_hint_v1` |
| `claimant_session_id` | Yes | Non-empty string, max 200 chars |
| `quorum_ref` | No | Opaque string for hub logging, max 200 chars |
| `claimed_frontier_turn` | No | Non-negative int; **advisory only**; not applied unless also set as `merge_context.frontier_turn` |
| `participant_sessions` | No | List of non-empty strings (max 32 entries, 200 chars each); **not** verified as live sessions |

## Quorum / Phase 3

True **cross-session quorum** (replicated frontier, membership proofs, split-brain policy) is **out of scope** for this hint. Future work must add explicit contracts and tests; this field is a **carrying channel** for operator-visible claims only.

## Related

- [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md)  
- [`PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md)  
- [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md)

## Changelog

- **2026-04-16:** Initial schema + echo + warnings (DJ-BL-15 / cross-session slice).
