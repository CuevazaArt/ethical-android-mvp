# Governance: MockDAO exit criteria + L0 constitution (Issue 6)

**Purpose:** Align **public narrative** with **runtime facts**: the MVP’s DAO is a **mock**; **L0** (`PreloadedBuffer`) is **immutable in code**; community-facing votes and drafts **do not** silently rewrite MalAbs or the buffer at runtime.

**Aligns with:** [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md), [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md), [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

**Public landing (partners):** [BlockChainDAO / governance story](https://mosexmacchinalab.com/blockchain-dao) — same honesty: mock code path today, research toward real distributed governance.

---

## 1. What `MockDAO` is today

| Claim to avoid | Reality in repo |
|----------------|-----------------|
| “On-chain consensus” / “distributed vote” | **`MockDAO`** (`src/modules/mock_dao.py`) — **in-process**, in-memory governance **simulation**; audit lines for demos and tests. |
| “Tamper-proof ethics” | No blockchain anchor; persistence of snapshots **does not** make votes **sociologically** or **legally** binding. |

**Narrative risk:** audit strings and WebSocket JSON can **look** like authority. Operators should treat them as **traceability**, not **consensus**.

---

## 2. L0 — explicit non-negotiable constitution (in-process)

**`PreloadedBuffer`** (`src/modules/buffer.py`) encodes **foundational principles** loaded at construction. They are **not** mutable by `MockDAO` votes, manufacturer hooks, or LLM output in the current architecture.

This is a deliberate **“constitution in the repo”** stance:

- **Pro:** Auditable, testable, reproducible ethics core for research and demos.
- **Tension:** Community **governance rhetoric** must not imply that **token holders** or **majorities** can override L0 **without a new software release** and explicit policy.

**Honest framing:** L0 is **dictatorship of the maintainer-defined core** until a future governance model is **specified, implemented, and reviewed** — not hidden behind DAO UX.

---

## 3. Where community drafts and votes attach (L1 / L2)

As documented in **UniversalEthos + Hub**:

- **L1 / L2** appear as **draft overlays** and **proposal resolution** on the kernel snapshot — **not** a write to `PreloadedBuffer`’s immutable principle set at runtime.
- **`deontic_gate`** (when enabled) blocks contradictions with L0; **repeal** mechanics are **explicit** and **named**, not silent erosion.

Votes **change draft status** and **documented** constitution views — they **do not** replace `AbsoluteEvilDetector` rules or MalAbs optimization paths without a **separate** code change.

---

## 4. Checklist — moving beyond mock (research / product)

Before claiming **real** distributed governance, expect **all** of the following to be addressed (non-exhaustive):

| Area | Questions |
|------|-----------|
| **Identity** | Who is a voter? Sybil resistance? Legal personhood vs device ID? |
| **Serialization / evidence** | What is signed, anchored, or reproducible off-box? |
| **Legal** | Jurisdiction, liability, fiduciary duty, export controls — **outside** this repo. |
| **Operations** | Key custody, upgrade path, rollback, incident response. |
| **Ethics** | Whether **any** vote may **ever** amend L0 — if yes, that is a **new constitution**, not a config flag. |

**Design surface (public):** [mosexmacchinalab.com/blockchain-dao](https://mosexmacchinalab.com/blockchain-dao) — roadmap language should stay consistent with this checklist.

---

## 5. References

- `src/modules/mock_dao.py` — implementation  
- `src/modules/buffer.py` — L0 principles  
- `src/modules/moral_hub.py`, `src/modules/deontic_gate.py` — drafts / gate  
- [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) — unified map  

---

*MoSex Macchina Lab — critique roadmap Issue 6.*
