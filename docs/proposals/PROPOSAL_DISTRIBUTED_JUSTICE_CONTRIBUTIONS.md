# Distributed justice — contribution guide (V11 + staged execution)

**Status:** Active team reference (Cursor line and cross-team).  
**Language:** English (durable record per repository policy).  
**Purpose:** Align **contributions** (code, tests, docs, operator material) with **distributed justice** without over-claiming chain guarantees or bypassing L0 ethics.

---

## 1) What “distributed justice” means in this repo

| Layer | Role | Honesty limit |
|-------|------|----------------|
| **V11 judicial track** | Dossier, mock court, audit lines — [`PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) | Simulation and transparency; **not** a legal tribunal or on-chain policy core. |
| **MockDAO** | Quadratic vote simulation, audit ledger — [`MOCK_DAO_SIMULATION_LIMITS.md`](MOCK_DAO_SIMULATION_LIMITS.md), [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) | No real chain consensus; L0 / MalAbs unchanged. |
| **Staged execution** | Phased path to off-chain replay, LAN coordination, optional anchors — [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) | Each phase has acceptance criteria; do not ship “production blockchain justice” without those gates. |

**Non-negotiable:** [`CONTRIBUTING.md`](../../CONTRIBUTING.md) language policy, [`TRANSPARENCY_AND_LIMITS.md`](../TRANSPARENCY_AND_LIMITS.md) credibility posture, and **no** replacement of core ethical gates with DAO votes.

---

## 2) Where to contribute (code map)

| Topic | Primary modules | Tests (examples) |
|-------|-----------------|------------------|
| Judicial escalation & dossier | [`src/modules/judicial_escalation.py`](../../src/modules/judicial_escalation.py) | `tests/test_judicial_escalation.py` (if present), grep `judicial` under `tests/` |
| Mock DAO / court | [`src/modules/mock_dao.py`](../../src/modules/mock_dao.py) | `tests/test_mock_dao.py`, chat tests with `KERNEL_JUDICIAL_MOCK_COURT` |
| Hub / constitution / WS DAO actions | [`src/modules/moral_hub.py`](../../src/modules/moral_hub.py), [`src/chat_server.py`](../../src/chat_server.py) | `tests/test_chat_server.py` (DAO WS), constitution routes |
| Audit / transparency | [`src/modules/hub_audit.py`](../../src/modules/hub_audit.py) | Integrity / hub audit tests |
| Temporal sync + cross-node contracts | [`src/modules/temporal_planning.py`](../../src/modules/temporal_planning.py), [`src/chat_server.py`](../../src/chat_server.py) | `tests/test_temporal_planning.py`, `tests/test_chat_server_temporal_coerce.py` |
| Env & validation | [`src/validators/kernel_public_env.py`](../../src/validators/kernel_public_env.py) | `tests/test_env_policy.py` |

---

## 3) Contribution backlog (actionable)

**ID registry and states:** [`PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) (`DJ-BL-*`).

These items extend the **“Pending gaps”** list in [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) §*Pending gaps*:

| ID | Item | Notes |
|----|------|--------|
| **DJ-BL-01** | **Replay / ledger checker (Phase 1)** — Fingerprint of canonical audit-export JSON; CLI compare. | **Done** — [`mock_dao_audit_replay.py`](../../src/modules/mock_dao_audit_replay.py), [`scripts/eval/verify_mock_dao_audit_replay.py`](../../scripts/eval/verify_mock_dao_audit_replay.py). |
| **DJ-BL-02** | **LAN reorder / duplicate (Phase 2)** — Idempotent merge of out-of-order or duplicated governance events. | **Done:** merge helper + WebSocket LAN batches (integrity, DAO, judicial, mock court) + envelope/coordinator paths ([`chat_server.py`](../../src/chat_server.py); ``KERNEL_LAN_GOVERNANCE_MERGE_WS`` and per-feature gates). |
| **DJ-BL-03** | **Operator runbook slice** — Short subsection in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md): “sync degraded, local-safe mode” (`KERNEL_TEMPORAL_*`, judicial JSON still present). | **Done** |
| **DJ-BL-04** | **Contract matrix** — Which `master-*` branches own which JSON keys (`judicial_escalation`, `mock_court`, `temporal_sync`). | **Done** — [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) |
| **DJ-BL-05** | **LAN DAO batch** — deterministic apply of `dao_vote` / `dao_resolve` under reorder/duplicate delivery. | **Done** — ``lan_governance_dao_batch`` + stress convergence (`tests/test_chat_server.py`). |
| **DJ-BL-06** | **LAN judicial/mock-court batches** — deterministic dossier registration and simulated tribunal runs under reorder/duplicate delivery. | **Done** — ``lan_governance_judicial_batch`` + ``lan_governance_mock_court_batch`` + stress convergence (`tests/test_chat_server.py`). |
| **DJ-BL-07** | **Coordinator envelope schema** — versioned wrapper for LAN batches. | **Done** — ``lan_governance_envelope_v1`` routing contract (`src/modules/lan_governance_envelope.py`, `src/chat_server.py`). |
| **DJ-BL-08** | **Envelope ACK + replay fingerprint** — deterministic envelope hash and post-apply ledger fingerprint in WS response. | **Done** — ``lan_governance.envelope`` now includes `fingerprint`, `audit_ledger_fingerprint`, and merged/applied counters (`src/chat_server.py`, `tests/test_chat_server.py`). |
| **DJ-BL-09** | **Envelope idempotency + reject taxonomy** — stable ACK token and machine-parseable reject reasons for envelope failures. | **Done** — ``lan_governance.envelope`` now includes `idempotency_token`, `ack`, and `reject_reason` (`src/chat_server.py`, `src/modules/lan_governance_envelope.py`, `tests/test_chat_server.py`). |
| **DJ-BL-10** | **Envelope replay cache** — duplicate envelope detection per WebSocket session. | **Done** — duplicate `idempotency_token` returns `ack=already_seen` and skips batch reapply (`src/chat_server.py`, `tests/test_chat_server.py`). |
| **DJ-BL-11** | **Replay cache bounds + ACK telemetry** — TTL/LRU bounded cache and cache hit/miss counters in envelope responses. | **Done** — envelope ACK now includes `cache` stats and replay cache is bounded by `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS` / `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES` (`src/chat_server.py`, `tests/test_chat_server.py`). |
| **DJ-BL-12** | **Replay-cache Prometheus metrics** — process-level observability for envelope duplicate handling. | **Done** — `ethos_kernel_lan_envelope_replay_cache_events_total` when `KERNEL_METRICS=1` (`src/observability/metrics.py`, `src/chat_server.py`, `tests/test_observability_metrics.py`). |
| **DJ-BL-13** | **Multi-node coordinator envelope** — one WebSocket frame carries N peer envelopes; deterministic apply order. | **Done** — `lan_governance_coordinator` + `lan_governance_coordinator_v1` (`src/modules/lan_governance_coordinator.py`, `src/chat_server.py`, `tests/test_lan_governance_coordinator.py`, `tests/test_chat_server.py`). |
| **DJ-BL-14** | **LAN merge conflict taxonomy** — machine-parseable `event_conflicts` for multi-node merge (`same_turn`, `different_clock`, `stale_event`). | **Done** — `src/modules/lan_governance_conflict_taxonomy.py`, LAN batches in `src/chat_server.py`, `tests/test_lan_governance_conflict_taxonomy.py`, `tests/test_chat_server.py`; [`PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md). |
| **DJ-BL-15** | **Replay sidecar + cross-session hint** — fingerprint merge diagnostics JSON; optional `merge_context.cross_session_hint` (echo only, not quorum). | **Done** — `src/modules/lan_governance_replay_sidecar.py`, `src/modules/lan_governance_merge_context.py`, `scripts/eval/verify_lan_governance_replay_sidecar.py`, tests; [`PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md), [`PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md). |
| **DJ-BL-16** | **Frontier witnesses** — advisory aggregate of peer `observed_max_turn` claims in one batch (not quorum). | **Done** — `merge_context.frontier_witnesses` + `frontier_witness_resolution` echo; [`PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md). |
| **DJ-BL-17** | **Anchor compare CLI (Phase 3 stub)** — exit code compares audit ledger JSON to expected fingerprint hex. | **Done** — [`scripts/eval/compare_audit_ledger_anchor.py`](../../scripts/eval/compare_audit_ledger_anchor.py), tests. |

Contributors should pick **one** item per PR when possible; link **`CHANGELOG.md`** when operator-visible behavior or JSON contracts change.

---

## 4) Definition of done (distributed justice PRs)

- **Tests:** `pytest` for changed paths; full `pytest tests/` before merge if CI matches repo policy.
- **Docs:** Update this file’s backlog or the staged proposal when closing a gap; link **V11** if behavior is user-visible.
- **Claims:** No “validated on mainnet” or “binding arbitration” unless backed by evidence artifacts in-repo (see [`TRANSPARENCY_AND_LIMITS.md`](../TRANSPARENCY_AND_LIMITS.md)).

---

## 5) Related documents

- [`PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) — `DJ-BL-*` IDs and states  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) — governance JSON keys vs `master-*`  
- [`PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) — HTTP GET JSON routes  
- [`PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md)  
- [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md)  
- [`PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md`](PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md)  
- [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)

---

## 6) Changelog

- **2026-04-15:** Initial contribution guide and backlog alignment with staged execution pending gaps.
- **2026-04-15:** DJ-BL-* table; link to [`PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md); DJ-BL-02 partial (`lan_governance_event_merge`).
- **2026-04-15:** DJ-BL-03 done — `OPERATOR_QUICK_REF.md` sync degraded / local-safe mode paragraph.
- **2026-04-15:** DJ-BL-01 (audit fingerprint + `verify_mock_dao_audit_replay.py`); DJ-BL-04 (contract matrix + [`PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md)).
- **2026-04-15:** DJ-BL-02 done — `lan_governance_integrity_batch` WebSocket path.
- **2026-04-15:** DJ-BL-05/06 done — LAN DAO/judicial/mock-court batches + stress tests.
- **2026-04-15:** DJ-BL-07 done — `lan_governance_envelope_v1` schema + routing.
- **2026-04-15:** DJ-BL-08 done — envelope ACK/replay fingerprints for multi-node traceability.
- **2026-04-15:** DJ-BL-09 done — envelope ACK token + reject taxonomy.
- **2026-04-15:** DJ-BL-10 done — per-session replay cache (`ack=already_seen`).
- **2026-04-15:** DJ-BL-11 done — replay cache TTL/LRU bounds + cache telemetry in ACK.
- **2026-04-15:** DJ-BL-12 done — Prometheus metrics for envelope replay-cache events.
- **2026-04-15:** DJ-BL-13 done — multi-envelope coordinator WebSocket contract.
- **2026-04-15:** DJ-BL-14 done — LAN merge conflict taxonomy + optional merge frontier.
- **2026-04-16:** DJ-BL-15 done — replay sidecar + cross-session hint channel.
- **2026-04-16:** DJ-BL-16 done — frontier witness aggregation echo; DJ-BL-17 — `compare_audit_ledger_anchor.py`; DJ-BL-02 table text corrected.
