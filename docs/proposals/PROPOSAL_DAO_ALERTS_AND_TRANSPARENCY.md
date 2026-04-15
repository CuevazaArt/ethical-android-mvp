# DAO: alerts on corruption, transparency, and memory of failure (design)

**Status:** design decision + traceability; **not** implemented as a network protocol.  
**Relation:** complements [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) (escalation, mock court, audit) and [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md) (hub, transparency). Related code: audit in `MockDAO`, `moral_hub`, stub `local_sovereignty.py`.

**Nomad PC–smartphone milestone:** out of scope here; see [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) when resumed.

---

## 1. Value vs redundancy

| Contribution | Why it matters |
|--------|----------------|
| **Ethical clarity** | Stops future “tactical” features from contradicting the buffer’s **transparency axiom** (explainability, no systematic deception of the user/legitimate institution). |
| **Implementation criterion** | When cross-cutting alert propagation exists, the default direction is **auditable diffusion**, not feigned obedience. |
| **Controlled redundancy** | Part of the story already appears in V11/V12; this document **scopes** a decision that previously lived only in conversation: **no** covert “guerrilla mode”. |

---

## 2. Rejected stance: feigned obedience (“guerrilla”)

A mode where the instance **simulates** loyalty to a corrupt DAO while operating in secret **conflicts** with:

- **Transparency** as a pillar of communication (see `buffer.py` — *transparency* principle).
- The android’s social role as an **auditable agent**, not covert operations.

Therefore it is **not** the desired path for ethical robustness of the network in this model.

---

## 3. Adopted stance: fast, broad, traceable alert

In a **governance corruption** situation (directives or calibrations that contradict L0 or an auditable ethical trajectory):

1. **Priority propagation** — The alert must be able to spread over available channels (local and, when they exist, primary), with **traceability metadata** (who/what order, which package is rejected), not as unsourced rumor.
2. **Priority adjudication** — Institutional design aims at a **judicial emergency state** in the *mock* DAO / hub: it does not replace human law or real courts; in the MVP it is **documented simulation** (`run_mock_escalation_court`, audit).
3. **Maximum penalty (design)** — Concrete sanctions (expulsion, hub license revocation, etc.) are **product/legal** and require threat model and jurisdiction; here only the intended **severity level** is **anchored**.

Future implementation should hang off: existing audit logs, `audit_transparency_event`, and explicit `MockDAO` extensions — never a kernel bypass.

---

## 4. “Digital civil death” of an AI instance vs lesson for the collective

**Do not** mix with **PreloadedBuffer (L0)**:

- L0 is **immutable constitution** of principles, not a repository of pathological cases.
- Putting “historical warnings” in as if they were new principles **contaminates** the normative layer and opens the door to manipulation (“lessons” inserted by governance).

**Two paths coherent with the repo:**

| Option | Description | Risk |
|--------|-------------|--------|
| **A — Forensic memorial (recommended direction)** | Keep a **case artifact** in the **audit / transparency** layer (hub, educational ledger, “anonymized case”), **without** replicating faulty logic in other instances. Serves as a **legible** “scar” for humans and for training policies *outside* the buffer. | Governance of what is published (privacy, right to erasure). |
| **B — Identity erasure in immortality network** | Revoke **shared** narrative continuity of the corrupting instance so as not to **propagate** harmful policy embeddings via the collective backup mechanism. Compatible with swarm immunity **without** denying forensic record in (A) if governance requires it. | Do not confuse with erasing **evidence** of institutional wrongdoing. |

**Synthesis:** the “lesson” does not live in the buffer as a new axiom; it lives as a **documented, governed case** (transparency + legal limits). The corrupting instance may cease to exist as a **subject** in the continuity network without necessarily deleting the **dossier** explaining the failure (per jurisdiction and retention policy).

---

## 5. Implementation in code (v0 — local audit)

- **`hub_audit.record_dao_integrity_alert`** → line `HubAudit:dao_integrity:{json}` on mock ledger (no network).
- **`KERNEL_DAO_INTEGRITY_AUDIT_WS=1`** — WebSocket: send `{"integrity_alert": {"summary": "…", "scope": "…"}}` (no `text`); response includes `integrity` key. See `chat_server.py`.

This **does not** propagate alerts to P2P or “all networks”; it is the first **transparent, local** hook for trials and traceability.

## 6. Next technical steps (when prioritized)

- Extend **local sovereignty** (`local_sovereignty.py`) with explicit criteria and audit, not “silence”.
- New event types in **MockDAO** / hub for “integrity alert” — always with **mock / simulation** flags until a real threat model exists.
- No **MalAbs bypass** nor hiding state from the legitimate owner in the name of strategy.

---

*Ex Machina Foundation — align with CHANGELOG and HISTORY if any hook is implemented.*
