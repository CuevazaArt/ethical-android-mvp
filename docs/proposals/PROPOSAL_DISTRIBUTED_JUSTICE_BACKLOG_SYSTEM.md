# Distributed justice — backlog proposal system

**Status:** Active process reference (Cursor line and cross-team).  
**Language:** English (durable record per repository policy).  
**Purpose:** Give **stable IDs**, **states**, and **traceability** to backlog items for distributed justice / governance work without duplicating GitHub Issues.

---

## 1) Relationship to other docs

| Artifact | Role |
|----------|------|
| [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md) | Contributor map + **DJ-BL-** backlog rows (what to build). |
| [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) | Phased execution (Phase 0–4) and **pending gaps**. |
| [`CHANGELOG.md`](../../CHANGELOG.md) | User-visible or contract-relevant completions. |

---

## 2) Backlog ID format

- **Prefix:** `DJ-BL-` (distributed justice backlog).
- **Number:** two digits, zero-padded: `DJ-BL-01` … `DJ-BL-99`.
- **Stability:** IDs are **not recycled** when an item is deferred or superseded; add a new ID for a new scope.

Current registry (aligned with contribution guide §3):

| ID | Topic | Status |
|----|--------|--------|
| **DJ-BL-01** | Replay / ledger checker (Phase 1) | Open |
| **DJ-BL-02** | LAN reorder / duplicate handling | **Partial** — pure merge helper [`lan_governance_event_merge.py`](../../src/modules/lan_governance_event_merge.py) + [`tests/test_lan_governance_event_merge.py`](../../tests/test_lan_governance_event_merge.py); WebSocket ingestion still future work. |
| **DJ-BL-03** | Operator runbook: sync degraded, local-safe mode | **Done** — [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) §Temporal planning / sync contract (*Sync degraded — local-safe mode*). |
| **DJ-BL-04** | Contract matrix (`master-*` × JSON keys) | Open |

Update this table when an ID changes state or when new IDs are added.

---

## 3) Suggested item states

Use in PR descriptions and proposal edits (not a database):

| State | Meaning |
|-------|---------|
| **Open** | Not started / not merged. |
| **In progress** | Active branch or draft PR linked in chat / issue. |
| **Partial** | Delivered slice (e.g. pure library without full integration). |
| **Done** | Merged; **CHANGELOG** updated if operator-facing or contract-changing. |
| **Deferred** | Explicitly postponed; short reason in this file or staged proposal. |

---

## 4) Definition of done (backlog hygiene)

- Closing **Done:** link the merging PR or commit; one-line pointer in **`CHANGELOG.md`** when behavior or JSON contracts change.
- **Partial:** document what remains (e.g. “wire merge helper into WebSocket replay path”).
- **No over-claim:** partial LAN simulation does **not** satisfy Phase 2 acceptance in the staged proposal until stress tests and coordinator schema exist.

---

## 5) Changelog

- **2026-04-15:** Initial backlog ID system; DJ-BL-02 marked partial after `lan_governance_event_merge` + tests.
- **2026-04-15:** DJ-BL-03 done — operator runbook slice in `OPERATOR_QUICK_REF.md` (sync flags vs local ethics/MockDAO).
