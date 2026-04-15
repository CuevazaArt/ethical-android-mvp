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

These items extend the **“Pending gaps”** list in [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) §*Pending gaps*:

1. **Replay / ledger checker (Phase 1)** — Script or test module that replays append-only governance events (or MockDAO audit rows) and asserts deterministic reconstruction; emit a clear diff on mismatch.
2. **LAN reorder / duplicate simulation (Phase 2)** — Tests that inject duplicated or reordered WebSocket/audit payloads; assert idempotent merge and no double-registration of the same dossier id.
3. **Operator runbook slice** — Short subsection in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) or a dedicated appendix: “sync degraded, local-safe mode” (`KERNEL_TEMPORAL_*`, judicial JSON still present).
4. **Contract matrix** — Table in docs: which `master-*` branches own which JSON keys (`judicial_escalation`, `mock_court`, `temporal_sync`); update when keys change.

Contributors should pick **one** item per PR when possible; link **`CHANGELOG.md`** when operator-visible behavior or JSON contracts change.

---

## 4) Definition of done (distributed justice PRs)

- **Tests:** `pytest` for changed paths; full `pytest tests/` before merge if CI matches repo policy.
- **Docs:** Update this file’s backlog or the staged proposal when closing a gap; link **V11** if behavior is user-visible.
- **Claims:** No “validated on mainnet” or “binding arbitration” unless backed by evidence artifacts in-repo (see [`TRANSPARENCY_AND_LIMITS.md`](../TRANSPARENCY_AND_LIMITS.md)).

---

## 5) Related documents

- [`PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md)  
- [`PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md)  
- [`PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md`](PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md)  
- [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)

---

## 6) Changelog

- **2026-04-15:** Initial contribution guide and backlog alignment with staged execution pending gaps.
