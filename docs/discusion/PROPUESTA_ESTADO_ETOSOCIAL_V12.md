# V12 — Distributed etosocial state & hybrid justice hub (vision)

**Status:** **design and research only** — no implementation commitment in the MVP codebase.  
**Relationship to V11:** V11 ([PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md)) supplies **traceability, dossiers, and local DAO audit hooks**; V12 describes the **macro-infrastructure** those hooks could eventually plug into: mixed institutions, federated learning, and economic layers. The kernel ethical pipeline (MalAbs → … → will) remains the **normative core**; V12 is **governance, operations, and society-scale architecture**, not a replacement kernel.

---

## How this integrates with prior work (non-redundant)

| Prior track | Role | How V12 builds on it |
|-------------|------|----------------------|
| **V11 — Justice / escalation** | Social-contract metaphor; `escalation` audit; optional `escalate_to_dao` | Becomes the **on-ramp** to a future **mixed tribunal** and **certified buffer violations** — today: local mock only. |
| **V10 — Operational** | Gray-zone diplomacy, skills, somatic markers, metaplan | **Work layer** prefiguration: human-in-the-loop roles in §3 extend “advisory” into **paid governance jobs** (design level). |
| **V9 — Epistemic / generative** | Dissonance telemetry, generative candidates | **Truth and dilemma** surfaces that **Auditors of Truth** (§3) could later arbitrate — not redundant; V12 names institutional scale. |
| **V8 — Situated / vitality** | Sensors, multimodal trust | **Evidence** path toward abstract fact representations for jurors (§1 MPC) — V12 specifies *who* sees *what*, not implemented. |
| **Persistence / immortality / augenesis** | Snapshots, `ImmortalityProtocol`, synthetic profiles | **Hybrid immortality registry** (§4) is a **vision** for fragmentation and legacy — extends but does not duplicate MVP backup semantics. |
| **MockDAO** | Quadratic voting, reputation vectors, audit | V12’s **√(reputation)** vote weight is a **variant** of quadratic philosophy; must be reconciled explicitly if ever implemented (see §1). |

**Value:** frames the project as **long-horizon civic infrastructure** (hybrid civilization), not only a software model — useful for grants, ethics boards, and roadmap narrative.  
**Redundancy:** low **if** V12 is kept as **non-overlapping scope** (institutions, economy, MPC, federated global model). It **would** be redundant if copied verbatim into V11 phases; therefore V12 is a **separate version** in the registry.

---

## 1. Mixed tribunal (justice and deliberation)

Justice is not **only** algorithms: a **balanced jury** is envisioned.

- **Composition (target ratios, design sketch):** ~33% high-tier android instances, ~33% human experts (bioethicists, jurists), ~34% institutional observers — **not** a commitment; governance product decision.
- **Privacy protocol:** **Multi-Party Computation (MPC)** so human jurors never see raw private video/audio; they see **abstract fact representations** and **buffer violations certified by the kernel** (not by the LLM alone).
- **Quadratic-style weighting:** Vote weight as **square root of accumulated reputation** to limit dominance by any single actor — **related to** existing quadratic voting in `MockDAO` but **not identical**; reconciliation is a future spec.

**Risk:** legal jurisdiction, juror liability, coercion, and “kernel-certified” evidentiary standards.

---

## 2. Technical evolution hub (ML and firmware)

The DAO maintains collective **body** (deployment) and **mind** (model behaviour) without exposing individual raw data.

- **Ethical federated learning:** Local error-driven updates; **gradients** aggregated at the DAO, not raw chat — aligns with privacy-preserving ML literature; **not** in-repo training today.
- **Firmware maintenance:** Human developers (conceptually DAO-governed) propose sensor stack and security patches; **DAO votes** on capability changes — maps to future CI/governance, not current GitHub flow.

**Risk:** poisoning attacks on federated aggregates; who is allowed to submit gradients.

---

## 3. Value economy and human employment

The hub generates value through **ethical services**, paying humans for tasks machines **must not** or **cannot** do alone.

| Role (design) | Function |
|---------------|----------|
| **Truth auditors** | Validate complex premises the android cannot verify alone (disinformation / epistemic load). |
| **Affective tutors** | Help configure augenesis profiles for new users. |
| **Identity rescuers** | Hardware experts recover soul backups from destroyed devices. |

**Business model (sketch):** Institutions pay the android network for **large-scale ethical advisory** or **conflict mediation**; flows fund salaries and network maintenance.

**Risk:** gig-economy exploitation, perverse incentives to manufacture conflicts.

---

## 4. Hybrid immortality registry (soul backup)

Identity backup is framed as the **highest network priority**.

- **Fragmented encryption (design):** e.g. **12 fragments** — split across user devices, random android nodes, and institutional DAO vaults — **illustrative**, not a cryptographic spec.
- **Sovereign restore:** Only the **owner** initiates reconstruction; **narrative legacy protocol** if the owner dies (android continues stated ethical mission) — **ethics and law**, not implemented.

**Risk:** key custody, institutional coercion, conflict with “right to be forgotten.”

---

## Architecture stack (V12 “value hub”)

| Layer | Responsibility |
|-------|------------------|
| **Service** | Digital actions + advisory → **revenue** (design). |
| **Work** | Android processing + **human audit** → **employment** (design). |
| **Justice** | **Mixed tribunal** → owner/agent disputes (design). |
| **Evolution** | **Federated ML** → global firmware/consciousness updates (design). |

---

## Registry note (versioning)

- **V11** = governance traceability track with **Phase 1 in code** (`judicial_escalation.py`, `MockDAO.register_escalation_case`).
- **V12** = **etosocial / civilization hub** vision — **documentation only** until a future product line adopts it.

Updates to implementation should advance **V11 phases** first; V12 informs **roadmap** and **institutional narrative** without implying shipped features.

---

## References

- [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md)
- [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md)
- [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)
- [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)

*Ex Machina Foundation — V12 vision layer (not a kernel contract).*
