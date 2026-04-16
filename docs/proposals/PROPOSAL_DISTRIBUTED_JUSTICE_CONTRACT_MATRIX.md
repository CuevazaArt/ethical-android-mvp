# Distributed justice — JSON contract matrix (`master-*` integration)

**Status:** Living document (Cursor line; update on contract changes).  
**Language:** English (durable record per repository policy).  
**Purpose:** **DJ-BL-04** — surface-area map for WebSocket / HTTP JSON contracts relevant to governance and distributed justice, so cross-team merges can check **what this branch implements** without implying other teams’ branch contents.

**Honesty:** Rows for other integration lines are **unknown unless verified** in those repos at merge time. This table describes **contract keys shipped in `master-Cursor`** (this repository).

---

## 1) WebSocket chat (`GET` upgrade to `/ws/chat`)

| Payload area (response keys) | In `master-Cursor` | Notes |
|------------------------------|--------------------|--------|
| `judicial_escalation` | Yes (when `KERNEL_CHAT_INCLUDE_JUDICIAL=1` and path produces view) | V11 — [`PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) |
| `mock_court` | Yes (when `KERNEL_JUDICIAL_MOCK_COURT=1` and court runs) | Simulated tribunal disclaimer in JSON |
| `temporal_context` / `temporal_sync` | Yes (per turn when temporal planning builds context) | `sync_schema` = `temporal_sync_v1` unless announced otherwise |
| `verbal_llm_observability` | Yes (when generative verbal degrades) | LLM matrix |
| `dao` (list / vote / resolve / submit_draft) | Yes (when `KERNEL_MORAL_HUB_DAO_VOTE=1`) | Meta: [`GET /dao/governance`](../../src/chat_server.py) |
| `lan_governance_integrity_batch` | Yes (when `KERNEL_DAO_INTEGRITY_AUDIT_WS=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + apply integrity alerts; optional `merge_context.frontier_turn`; optional `event_conflicts` (`same_turn` / `different_clock` / `stale_event`) — [`lan_governance_conflict_taxonomy.py`](../../src/modules/lan_governance_conflict_taxonomy.py) |
| `lan_governance_dao_batch` | Yes (when `KERNEL_MORAL_HUB_DAO_VOTE=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + apply DAO vote/resolve; same merge diagnostics as integrity batch |
| `lan_governance_judicial_batch` | Yes (when `KERNEL_JUDICIAL_ESCALATION=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + register escalation dossiers on audit ledger; same merge diagnostics |
| `lan_governance_mock_court_batch` | Yes (when `KERNEL_JUDICIAL_ESCALATION=1`, `KERNEL_JUDICIAL_MOCK_COURT=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + run mock court on dossiers; same merge diagnostics |
| `lan_governance_envelope` | Yes (schema `lan_governance_envelope_v1`) | Versioned coordinator envelope; routes `kind` → batch handler |
| `lan_governance_coordinator` | Yes (schema `lan_governance_coordinator_v1`, when `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Hub message: multiple inner envelopes; fingerprint sort + dedupe; applies each in order; optional `aggregated_event_conflicts` when inner batches emit merge conflicts |
| `constitution` (in-message snapshot) | Optional (`KERNEL_CHAT_INCLUDE_*`) | Hub stack |

---

## 2) HTTP JSON (same FastAPI app as WebSocket)

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Service index + WebSocket hint + protocol summary |
| `/health` | GET | Liveness, observability flags, `chat_bridge`, `safety_defaults`, optional `runtime_profile` |
| `/metrics` | GET | Prometheus (when `KERNEL_METRICS=1`; includes `ethos_kernel_lan_envelope_replay_cache_events_total` for envelope replay-cache hits/misses/evictions) |
| `/constitution` | GET | L0 principles (when `KERNEL_MORAL_HUB_PUBLIC=1`) |
| `/dao/governance` | GET | DAO WebSocket protocol meta (V12.3) |
| `/nomad/migration` | GET | Nomad HAL simulation meta |

Full listing: [`PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md).

---

## 3) Other `master-*` lines

| Line | Contract ownership |
|------|----------------------|
| `master-claude` | Merge-time verification; do not assume parity without integration PR. |
| `master-antigravity` | Merge-time verification; do not assume parity without integration PR. |

Update this section when a cross-team integration gate run documents verified parity for specific keys.

---

## 4) Related

- [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) (DJ-BL-04 **Done** for matrix v1)

---

## 5) Changelog

- **2026-04-15:** Initial matrix + pointer to HTTP API surface doc.
- **2026-04-15:** WebSocket ``lan_governance_integrity_batch`` row (DJ-BL-02).
- **2026-04-15:** LAN batch rows — `merge_context.frontier_turn` + `event_conflicts` taxonomy (DJ-BL-14); see [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md).
- **2026-04-15:** Coordinator row — optional `aggregated_event_conflicts` when inner batches report merge conflicts.
