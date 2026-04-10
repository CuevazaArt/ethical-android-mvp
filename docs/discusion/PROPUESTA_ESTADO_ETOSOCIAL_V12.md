# V12 — Moral Infrastructure Hub & distributed etosocial state

**Status:** **vision + Phase 1 code hooks** in `src/modules/moral_hub.py` (constitution export, transparency audit, mock proposals, EthosPayroll audit lines).  
**Relationship to V11:** V11 implements **justice traceability and mock tribunal**; V12 frames the **civilization-scale hub** (constitution, economy, R&D ethics) that those features plug into. The kernel pipeline (MalAbs → … → will) remains the **normative core**; hub layers are **governance and operations**, not a replacement kernel.

---

## Hub positioning: “living constitution”

The project is not only a software model but an **infrastructure for hybrid moral civilization**: humans, institutions, and services maintain a **Living Constitution** — the android’s “instinct” becomes a **democratic expression of universal values** only in the **full product vision**; in the MVP, **L0** remains **immutable in code** (`buffer.py`), with **read-only export** and **mock** DAO proposals for demos.

---

## Pillar 1 — Community constitution (DemocraticBuffer)

The buffer stops being **only** a static file in the **vision**: it becomes a **dynamic social contract** where validated institutions and humans propose **ethical articles**, and the community votes (quadratic voting) on what enters the immutable layers.

| Layer | Content (vision) | Vote threshold (design) | MVP codebase |
|-------|------------------|-------------------------|--------------|
| **L0 — Hard core** | Human rights + MalAbs-class absolutes | ~90% consensus (design) | **Implemented** as `PreloadedBuffer` in `buffer.py`; **not** community-editable yet |
| **L1 — Coexistence** | Culture / hardware norms | ~66% (design) | **Placeholder** empty list in `constitution_snapshot()` |
| **L2 — Owner directives** | Private preferences, may not violate L0/L1 | Owner + bounds (design) | **Placeholder** |

**Phase 1 code:** `constitution_snapshot()` exports L0 **read-only**; `propose_community_article_mock()` → `MockDAO.create_proposal` when `KERNEL_DEMOCRATIC_BUFFER_MOCK=1` (does **not** mutate `PreloadedBuffer`).

---

## Pillar 2 — Services hub (value + employment)

| Service | Role (vision) | MVP |
|---------|---------------|-----|
| **Distributed justice** | External parties contract DAO for ethical arbitration; human + android analysts | V11 mock court + escalation audit |
| **Soul / firmware care** | Subscription for backup + updates | Persistence + immortality modules (existing) |
| **ML ethics tuning** | Sell certified ethical inference models; human “value trainers” | Not implemented; federated learning remains design |

---

## Pillar 3 — Mixed remuneration (EthosPayroll)

**Vision:** Fiat/crypto from services and licenses; **reputation tokens** for DAO weight and priority access.  
**Phase 1 code:** `ethos_payroll_record_mock()` appends **audit** lines when `KERNEL_ETHOS_PAYROLL_MOCK=1` (narrative only; no payments).

---

## Pillar 4 — R&D transparency vs. privacy veil

| Stage | Policy (vision) | Phase 1 code |
|-------|-----------------|--------------|
| **Sandbox observation** | Core team holds an **auditor transparency** role: thought flows visible for debugging **only under policy** | `KERNEL_TRANSPARENCY_AUDIT=1` → `audit_transparency_event()` on each WebSocket open (and extensible to other events) |
| **Auditability** | Each access generates a **DAO audit record** (mock) | `register_audit` via `moral_hub` |
| **Future veil** | Human direct observation replaced by **statistical summaries** from trusted androids | Not implemented |

---

## Logistics architecture (inputs → hub)

```
(Input) Institutions + humans → propose buffer / ML changes (vision)
        ↓
Deliberation DAO → votes on weights & firmware (vision; mock DAO today)
        ↓
Hub execution → androids deliver services; humans audit truth/ethics (vision)
        ↓
Value flow → maintenance, salaries, network expansion (vision; EthosPayroll mock audit only)
```

---

## Phased implementation (registry)

| Phase | Deliverable | Risk | Code status |
|-------|-------------|------|-------------|
| **V12.1** | Read-only L0 JSON (`GET /constitution`); `KERNEL_MORAL_HUB_PUBLIC` | Low | **Done** |
| **V12.1** | Transparency audit hook on WebSocket; `KERNEL_TRANSPARENCY_AUDIT` | Low | **Done** |
| **V12.1** | Mock DemocraticBuffer proposals; `KERNEL_DEMOCRATIC_BUFFER_MOCK` | Low | **Done** |
| **V12.1** | EthosPayroll mock audit lines; `KERNEL_ETHOS_PAYROLL_MOCK` | Low | **Done** |
| **V12.2** | Persist L1/L2 drafts in snapshot schema (optional) | Medium | Planned |
| **V12.3** | Real vote pipeline on proposals (off-chain → testnet) | High | Research |
| **V12.4** | MPC jury, federated learning, payroll tokens | Very high | Research (see sections 1–4 legacy below) |

---

## How this integrates with prior work (non-redundant)

| Prior track | Role | How V12 builds on it |
|-------------|------|----------------------|
| **V11 — Justice** | Escalation, mock tribunal | On-ramp to certified buffer violations and **paid** arbitration (vision). |
| **V10 — Operational** | Gray-zone, skills | **Work layer** toward paid governance roles. |
| **MockDAO** | Quadratic voting, audit | DemocraticBuffer proposals and **EthosPayroll** mock lines use the same ledger. |
| **PreloadedBuffer** | Immutable L0 | **Source of truth** for `constitution_snapshot` until governance ships. |

---

## Legacy sections — mixed tribunal, FL, economy, immortality (design)

### Mixed tribunal (justice and deliberation)

- Composition sketch: ~33% android / ~33% human experts / ~34% institutions — product decision.
- **MPC** for juror privacy — research.
- **√(reputation)** vote weight — related to quadratic voting in `MockDAO`; reconcile in a future spec.

### Technical evolution hub (ML and firmware)

- Ethical federated learning; DAO-voted firmware — not in-repo training.

### Value economy and human employment

- Truth auditors, affective tutors, identity rescuers — design; institutions pay for advisory at scale.

### Hybrid immortality registry

- Fragmented backup, sovereign restore, narrative legacy — design; see persistence docs.

### Architecture stack (value hub)

| Layer | Responsibility |
|-------|----------------|
| **Service** | Digital actions + advisory → revenue (design). |
| **Work** | Android + human audit → employment (design). |
| **Justice** | Mixed tribunal → disputes (design). |
| **Evolution** | Federated ML → global updates (design). |

---

## Environment variables (Phase 1)

| Variable | Default | Effect |
|----------|---------|--------|
| `KERNEL_MORAL_HUB_PUBLIC` | off | Enables `GET /constitution` |
| `KERNEL_TRANSPARENCY_AUDIT` | off | Logs `TransparencyAudit` on WebSocket open |
| `KERNEL_DEMOCRATIC_BUFFER_MOCK` | off | `propose_community_article_mock` creates DAO proposals |
| `KERNEL_ETHOS_PAYROLL_MOCK` | off | One-line EthosPayroll audit on WebSocket connect |

---

## Registry note (versioning)

- **V11** = justice/escalation track (implemented phases 1–3).
- **V12** = moral infrastructure hub: **vision** + **V12.1** code hooks above; no change to MalAbs or buffer semantics.

---

## References

- [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md)
- [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md)
- [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)
- [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)

*Ex Machina Foundation — V12 hub layer; kernel contract unchanged.*
