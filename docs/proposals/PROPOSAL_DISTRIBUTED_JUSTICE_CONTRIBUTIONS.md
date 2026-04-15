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
| **DJ-BL-02** | **LAN reorder / duplicate (Phase 2)** — Idempotent merge of out-of-order or duplicated governance events. | **Done:** merge helper + WebSocket ``lan_governance_integrity_batch`` ([`chat_server.py`](../../src/chat_server.py); ``KERNEL_LAN_GOVERNANCE_MERGE_WS`` + ``KERNEL_DAO_INTEGRITY_AUDIT_WS``). DAO/judicial batch kinds still future work. |
| **DJ-BL-03** | **Operator runbook slice** — Short subsection in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md): “sync degraded, local-safe mode” (`KERNEL_TEMPORAL_*`, judicial JSON still present). | **Done** |
| **DJ-BL-04** | **Contract matrix** — Which `master-*` branches own which JSON keys (`judicial_escalation`, `mock_court`, `temporal_sync`). | **Done** — [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) |

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
