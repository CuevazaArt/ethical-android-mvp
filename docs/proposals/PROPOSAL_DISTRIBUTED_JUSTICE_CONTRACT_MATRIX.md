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
| `lan_governance_integrity_batch` | Yes (when `KERNEL_DAO_INTEGRITY_AUDIT_WS=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + apply integrity alerts; [`lan_governance_event_merge.py`](../../src/modules/lan_governance_event_merge.py) |
| `lan_governance_dao_batch` | Yes (when `KERNEL_MORAL_HUB_DAO_VOTE=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + apply DAO vote/resolve; deterministic replay slice |
| `lan_governance_judicial_batch` | Yes (when `KERNEL_JUDICIAL_ESCALATION=1` **and** `KERNEL_LAN_GOVERNANCE_MERGE_WS=1`) | Merge + register escalation dossiers on audit ledger |
| `constitution` (in-message snapshot) | Optional (`KERNEL_CHAT_INCLUDE_*`) | Hub stack |

---

## 2) HTTP JSON (same FastAPI app as WebSocket)

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Service index + WebSocket hint + protocol summary |
| `/health` | GET | Liveness, observability flags, `chat_bridge`, `safety_defaults`, optional `runtime_profile` |
| `/metrics` | GET | Prometheus (when `KERNEL_METRICS=1`) |
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
