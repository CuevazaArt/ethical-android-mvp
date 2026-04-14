# DAO: alerts on corruption, transparency, and failure memory (design)

**Status:** design decision + traceability; **not** implemented as a network protocol.  
**Relationship:** complements [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) (escalation, mock tribunal, auditing) and [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md) (hub, transparency). Related code: auditing in `MockDAO`, `moral_hub`, stub `local_sovereignty.py`.

**Nomadic PC–smartphone milestone:** out of scope here; see [NOMAD_PC_SMARTPHONE_BRIDGE.md](../NOMAD_PC_SMARTPHONE_BRIDGE.md) when resumed.

---

## 1. Value vs. redundancy

| Contribution | Why it is useful |
|--------|----------------|
| **Ethical clarity** | Prevents future "tactical" features from contradicting the buffer's **transparency axiom** (explainability, no systematic deception of user/legitimate institution). |
| **Implementation criterion** | When cross-propagation of alerts exists, the default direction is **auditable diffusion**, not feigned obedience. |
| **Controlled redundancy** | Part of the narrative already appears in V11/V12; this document **pins down** a decision that previously only existed in conversation: **no** covert "guerrilla mode". |

---

## 2. Rejected stance: feigned obedience ("guerrilla")

A mode where the instance **simulates** loyalty to a corrupt DAO while operating in secret **conflicts** with:

- **Transparency** as a communication pillar (see `buffer.py` — *transparency* principle).
- The android's social function as an **auditable agent**, not a covert operative.

Therefore it is **not** the desired path for the ethical robustness of the network in this model.

---

## 3. Adopted stance: fast, broad, and traceable alerting

In a situation of **governance corruption** (directives or calibrations that contradict L0 or the auditable ethical trajectory):

1. **Priority propagation** — The alert must be able to spread through available channels (local and, when they exist, main channels), with **traceability metadata** (who/what order, what package is rejected), not as an unsourced rumor.
2. **Priority judgment** — The institutional design points to a **judicial emergency state** in the mock DAO / hub: it does not replace human law or real courts; in the MVP it is **documented simulation** (`run_mock_escalation_court`, auditing).
3. **Maximum penalty (design)** — Specific sanctions (expulsion, license revocation from the hub, etc.) are **product/legal** matters requiring a threat model and jurisdiction; this document only **anchors** the intended severity level.

Future implementation should hook into: existing audit records, `audit_transparency_event`, and explicit `MockDAO` extensions — never a kernel bypass.

---

## 4. "Digital civil death" of an AI instance vs. lesson for the collective

**Do not** mix with the **PreloadedBuffer (L0)**:

- L0 is an **immutable constitution** of principles, not a repository of pathological cases.
- Injecting "historical warnings" as if they were new principles **contaminates** the normative layer and opens the door to manipulation ("teachings" inserted by governance).

**Two paths consistent with the repo:**

| Option | Description | Risk |
|--------|-------------|--------|
| **A — Forensic memorial (recommended direction)** | Preserve a **case artifact** in the **auditing / transparency** layer (hub, educational ledger, "anonymized case"), **without** replicating the erroneous logic in other instances. Serves as a **readable "scar"** for humans and for training policies *outside* the buffer. | Governance of what is published (privacy, right to be forgotten). |
| **B — Identity erasure from the immortality network** | Revoke the corrupted instance's **shared narrative continuity** to prevent **propagating** harmful policy embeddings through the collective backup mechanism. Compatible with swarm immunity **without** denying the forensic record in (A) if governance requires it. | Do not confuse with erasing **evidence** of an institutional offense. |

**Summary:** the "lesson" does not live in the buffer as a new axiom; it lives as a **documented and governed case** (transparency + legal limits). The corrupted instance may cease to exist as a **subject** in the continuity network without necessarily erasing the **dossier** that explains the failure (depending on jurisdiction and retention policy).

---

## 5. Code implementation (v0 — local auditing)

- **`hub_audit.record_dao_integrity_alert`** → `HubAudit:dao_integrity:{json}` line in the mock ledger (no network).
- **`KERNEL_DAO_INTEGRITY_AUDIT_WS=1`** — WebSocket: send `{"integrity_alert": {"summary": "…", "scope": "…"}}` (without `text`); response includes `integrity` key. See `chat_server.py`.

This does **not** propagate alerts to P2P or "all networks"; it is the first **transparent and local** hook for trials and traceability.

## 6. Next technical steps (when prioritized)

- Extend **local sovereignty** (`local_sovereignty.py`) with explicit criteria and auditing, not "silence".
- New event types in **MockDAO** / hub for "integrity alert" — always with **mock / simulation** flags until a real threat model exists.
- No **MalAbs bypass** or hiding state from the legitimate owner in the name of strategy.

---

*Ex Machina Foundation — align with CHANGELOG and HISTORY if any hook is implemented.*
