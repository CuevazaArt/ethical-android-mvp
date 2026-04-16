# PROPOSAL — LAN governance merge conflict taxonomy (Phase 2)

**Status:** Implemented slice (per-session merge diagnostics).  
**Language:** English (repository policy).  
**Code:** [`src/modules/lan_governance_conflict_taxonomy.py`](../../src/modules/lan_governance_conflict_taxonomy.py), [`src/modules/lan_governance_event_merge.py`](../../src/modules/lan_governance_event_merge.py), LAN batch handlers in [`src/chat_server.py`](../../src/chat_server.py).

## Evidence posture

This taxonomy classifies **drops** during deterministic merge of batch `events` **inside one WebSocket session**. It does **not** prove cross-node quorum, global clock agreement, or chain-finality. Operators supply an optional **`merge_context.frontier_turn`** so late rows can be flagged as stale relative to a **local** progress hint (not a replicated consensus value).

## Conflict kinds (stable JSON strings)

| `kind` | Meaning | Detection (deterministic) |
|--------|---------|---------------------------|
| `same_turn` | Concurrent edits for the same `event_id` in the same `turn_index` | Duplicate id + same `turn_index` + different **content fingerprint** (ordering fields excluded). First row in `(turn_index, processor_elapsed_ms, event_id)` sort wins. |
| `different_clock` | Same `event_id` observed under different `turn_index` with **different** content | Duplicate id + different `turn_index` + different content fingerprints. Earlier `turn_index` wins. |
| `stale_event` | Below operator frontier **or** late replay of an identical payload under a later `turn_index` | `turn_index < merge_context.frontier_turn`, **or** duplicate id + different `turn_index` + **identical** content fingerprint (first turn wins). |

Benign duplicates (same id, same turn, same content, different `processor_elapsed_ms`) produce **no** conflict entry.

## Response surface

LAN batch sections (`integrity_batch`, `dao_batch`, `judicial_batch`, `mock_court_batch`) may include **`event_conflicts`**: a JSON array of objects with at least `kind`, `event_id`, and `reason`, plus numeric hints (`turn_index`, `processor_elapsed_ms`, `content_fingerprint`, etc.) as documented in the module.

The key is omitted when the array would be empty.

**Hub coordinator:** `lan_governance.coordinator` may include **`aggregated_event_conflicts`**: the same conflict objects as above, each augmented with `source_batch` (which LAN section produced it), `envelope_fingerprint`, and `envelope_idempotency_token` so operators can map conflicts back to a specific inner envelope in `items`.

## Related

- [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) — Phase 2 deliverable list.  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) — WebSocket contract map.

## Changelog

- **2026-04-15:** Initial proposal + implementation (DJ-BL-14).
- **2026-04-15:** Coordinator responses add optional `aggregated_event_conflicts`; operator quick ref documents `merge_context` and hub aggregation.
