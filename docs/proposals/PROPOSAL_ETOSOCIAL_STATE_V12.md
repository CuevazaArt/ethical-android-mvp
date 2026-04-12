# V12 — Moral Infrastructure Hub & distributed etosocial state

**Status:** **vision + Phase 1–3 code hooks** in `src/modules/moral_hub.py`, `mock_dao.py`, persistence, and hub stubs (`deontic_gate`, `ml_ethics_tuner`, `reparation_vault`, `nomad_identity`). **Canonical narrative + module map:** [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) (DemocraticBuffer / overlays, services hub, audit levels, evolution loops, V11 naming table).

**Relationship to V11:** V11 implements **justice traceability and mock tribunal**; V12 frames the **civilization-scale hub** (constitution, economy, R&D ethics) that those features plug into. The kernel pipeline (MalAbs → … → will) remains the **normative core**; hub layers are **governance and operations**, not a replacement kernel.

**Living constitution (summary):** In the MVP, **L0** stays **immutable in code** (`buffer.py`); L1/L2 are **drafts + DAO votes** (checkpointed), with optional **deontic gate** on drafts (`KERNEL_DEONTIC_GATE`). Full pillar detail is in **UNIVERSAL_ETHOS_AND_HUB.md** — this file keeps the **V12 release registry** and **environment variables**.

---

## Phased implementation (registry)

| Phase | Deliverable | Risk | Code status |
|-------|-------------|------|-------------|
| **V12.1** | Read-only L0 JSON (`GET /constitution`); `KERNEL_MORAL_HUB_PUBLIC` | Low | **Done** |
| **V12.1** | Transparency audit hook on WebSocket; `KERNEL_TRANSPARENCY_AUDIT` | Low | **Done** |
| **V12.1** | Mock DemocraticBuffer proposals; `KERNEL_DEMOCRATIC_BUFFER_MOCK` | Low | **Done** |
| **V12.1** | EthosPayroll mock audit lines; `KERNEL_ETHOS_PAYROLL_MOCK` | Low | **Done** |
| **V12.2** | Persist L1/L2 drafts in snapshot schema | Medium | **Done** (`constitution_*_drafts`; snapshot schema v2+; optional WS/env) |
| **V12.3** | Vote pipeline on MockDAO proposals (off-chain; checkpointed) | Medium | **Done** (`KERNEL_MORAL_HUB_DAO_VOTE`, schema v3, `submit_constitution_draft_for_vote`, draft status sync on resolve) |
| **V12.3+** | UniversalEthos stubs (deontic, expert loop, reparation, nomad bridge) | Low | **Done** (see UNIVERSAL_ETHOS_AND_HUB.md) |
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

## Environment variables (Phases 2–3)

| Variable | Default | Effect |
|----------|---------|--------|
| `KERNEL_MORAL_HUB_DRAFT_WS` | off | WebSocket `constitution_draft` appends L1/L2 drafts |
| `KERNEL_CHAT_INCLUDE_CONSTITUTION` | off | WebSocket responses include full `constitution` JSON |
| `KERNEL_MORAL_HUB_DAO_VOTE` | off | WebSocket `dao_list`, `dao_submit_draft`, `dao_vote`, `dao_resolve`; see `GET /dao/governance` |
| `KERNEL_DEONTIC_GATE` | off | Reject L1/L2 drafts that fail L0 heuristic check (`deontic_gate.py`) |
| `KERNEL_ML_ETHICS_TUNER_LOG` | off | DAO audit line on gray-zone turns (`ml_ethics_tuner.py`) |
| `KERNEL_REPARATION_VAULT_MOCK` | off | Mock reparation **intent** lines on DAO audit |
| `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY` | off | WebSocket `nomad_identity` summary (`nomad_identity.py`) |

---

## Registry note (versioning)

- **V11** = justice/escalation track (implemented phases 1–3).
- **V12** = moral infrastructure hub: **vision** + **V12.1–V12.3** + **UniversalEthos stubs**; no change to MalAbs or L0 buffer semantics.

---

## References

- [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) — **unified** hub architecture (vision ↔ code)
- [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md)
- [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](PROPOSAL_OPERATIONAL_STRATEGY_V10.md)
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md)
- [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)

*Ex Machina Foundation — V12 hub layer; kernel contract unchanged.*
