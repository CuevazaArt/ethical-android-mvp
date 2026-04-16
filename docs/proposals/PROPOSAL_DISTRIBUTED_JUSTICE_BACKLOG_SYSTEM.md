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
| **DJ-BL-01** | Replay / ledger checker (Phase 1) | **Done** — [`mock_dao_audit_replay.py`](../../src/modules/mock_dao_audit_replay.py), [`verify_mock_dao_audit_replay.py`](../../scripts/eval/verify_mock_dao_audit_replay.py), [`tests/test_mock_dao_audit_replay.py`](../../tests/test_mock_dao_audit_replay.py). Fingerprint equality only; full state replay of proposals not in scope. |
| **DJ-BL-02** | LAN reorder / duplicate handling | **Done** — merge helper + tests; WebSocket ``lan_governance_integrity_batch`` when ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` and ``KERNEL_DAO_INTEGRITY_AUDIT_WS=1`` ([`chat_server.py`](../../src/chat_server.py)). Extending the same pattern to ``dao_vote`` / judicial batches is **not** in this ID. |
| **DJ-BL-03** | Operator runbook: sync degraded, local-safe mode | **Done** — [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) §Temporal planning / sync contract (*Sync degraded — local-safe mode*). |
| **DJ-BL-04** | Contract matrix (`master-*` × JSON keys) | **Done** — [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) |
| **DJ-BL-05** | LAN DAO batch (`dao_vote`/`dao_resolve`) | **Done** — WebSocket ``lan_governance_dao_batch`` + stress convergence in [`tests/test_chat_server.py`](../../tests/test_chat_server.py). |
| **DJ-BL-06** | LAN judicial + mock-court batches | **Done** — WebSocket ``lan_governance_judicial_batch`` and ``lan_governance_mock_court_batch`` + stress convergence tests in [`tests/test_chat_server.py`](../../tests/test_chat_server.py). |
| **DJ-BL-07** | LAN coordinator envelope schema | **Done** — ``lan_governance_envelope_v1`` contract + routing in [`src/modules/lan_governance_envelope.py`](../../src/modules/lan_governance_envelope.py) and [`src/chat_server.py`](../../src/chat_server.py). |
| **DJ-BL-08** | LAN envelope ACK + replay fingerprint | **Done** — ``lan_governance.envelope`` now returns deterministic ``fingerprint`` plus ``audit_ledger_fingerprint`` and applied counters for replay traceability in [`src/chat_server.py`](../../src/chat_server.py). |
| **DJ-BL-09** | Envelope idempotency token + reject taxonomy | **Done** — ACK now includes ``idempotency_token`` and stable reject taxonomy (`reject_reason`, `ack`) for schema/routing failures in [`src/chat_server.py`](../../src/chat_server.py) and [`src/modules/lan_governance_envelope.py`](../../src/modules/lan_governance_envelope.py). |
| **DJ-BL-10** | Envelope replay cache (`already_seen`) | **Done** — per-session replay cache drops duplicated envelopes by ``idempotency_token`` and returns ``ack=already_seen`` without reapplying events in [`src/chat_server.py`](../../src/chat_server.py). |
| **DJ-BL-11** | Envelope replay cache bounds + telemetry | **Done** — replay cache now enforces TTL/LRU bounds and returns cache stats (`hit`, totals, size) in envelope ACKs in [`src/chat_server.py`](../../src/chat_server.py). |
| **DJ-BL-12** | Envelope replay-cache Prometheus metrics | **Done** — `ethos_kernel_lan_envelope_replay_cache_events_total` when `KERNEL_METRICS=1` in [`src/observability/metrics.py`](../../src/observability/metrics.py), emitted from envelope handling in [`src/chat_server.py`](../../src/chat_server.py). |

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
- **2026-04-15:** DJ-BL-01 done (audit fingerprint + script); DJ-BL-04 done (contract matrix + HTTP API surface doc).
- **2026-04-15:** DJ-BL-02 done — WebSocket ``lan_governance_integrity_batch`` + env gate ``KERNEL_LAN_GOVERNANCE_MERGE_WS``.
- **2026-04-15:** DJ-BL-05/06 done — LAN DAO/judicial/mock-court batches + stress tests.
- **2026-04-15:** DJ-BL-07 done — LAN envelope schema ``lan_governance_envelope_v1``.
- **2026-04-15:** DJ-BL-08 done — envelope ACK includes deterministic fingerprint + replay hash.
- **2026-04-15:** DJ-BL-09 done — envelope ACK adds idempotency token + reject reason taxonomy.
- **2026-04-15:** DJ-BL-10 done — envelope replay cache returns `already_seen` on duplicates.
- **2026-04-15:** DJ-BL-11 done — replay cache TTL/LRU bounds + ACK cache telemetry.
- **2026-04-15:** DJ-BL-12 done — Prometheus counters for envelope replay-cache events.
