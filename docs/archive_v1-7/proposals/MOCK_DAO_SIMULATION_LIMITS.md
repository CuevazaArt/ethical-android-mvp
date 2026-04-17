# Mock DAO — simulation limits and non-goals

**Audience:** reviewers who compare `src/modules/mock_dao.py` to production governance or blockchain products.

This document **does not** add on-chain security; it **stops overclaiming** in docs and product narrative.

---

## 1. What the critique gets right

| Claim | Status in this repo |
|-------|---------------------|
| No real smart contracts shipped | **True.** There is no audited Solidity runtime wired to the kernel. A **non-functional** stub lives under [`contracts/stubs/`](../../contracts/stubs/) for repo layout only — see [`contracts/README.md`](../../contracts/README.md). |
| Simulated governance never stress-tested by strategic actors | **True.** Tests cover **deterministic** flows and demos, not game-theoretic attacks or economic incentives. |
| Quadratic voting assumes cooperative participants | **True.** Cost is `n²` tokens from a **fixed in-memory** participant table; there is **no** Sybil resistance, identity oracle, or collusion model. |
| “Most important and emptiest” if DAO were central | **Partially mis-framed:** the **ethical action pipeline** (MalAbs → mixture scorer → poles / will → `final_action`) does **not** read `MockDAO` votes to choose actions. DAO + hub are **parallel** narrative/governance UX — important for **story and traceability**, not for the **scalar policy core** (see [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md), [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md)). |

---

## 2. Relationship to the ethical kernel

- **L0** (`PreloadedBuffer`) and **MalAbs** are **not** overridden by DAO outcomes in the current architecture.
- **`MockDAO`** registers audits, proposals, and demo votes **in-process**; WebSocket / moral hub surfaces may **display** governance state — that is **not** on-chain consensus or legal authority.

If product messaging implies “the DAO decides ethics,” that is **incorrect** for this codebase unless explicitly redesigned with ADRs and tests.

---

## 3. Quadratic voting — documented assumptions

The implementation:

- Debits `n_votes ** 2` from `Participant.available_tokens`.
- Weights votes by a **static** reputation scalar derived from three floats.
- Resolves by comparing aggregated for/against weights.

**Not modeled:** identity binding, delegation bribery, mempool ordering, MEV, privacy, coercion, or cross-device replay. Treat as **UX math for demos**, not a cryptoeconomic proof.

---

## 4. What would be required for “real” chain governance (out of scope here)

Minimum bar (non-exhaustive): specification of powers (what on-chain votes may change), identity/Sybil policy, contract audit, key management, upgradeability, and **explicit** mapping from chain state to kernel config — **not** a drop-in replacement of `MockDAO` without a separate project.

---

## 5. References

- [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md)  
- [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md)  
- [`SECURITY.md`](../SECURITY.md)  
- [`src/modules/mock_dao.py`](../../src/modules/mock_dao.py)

---

*MoSex Macchina Lab — honest scope for Issue 6 and external reviews.*
