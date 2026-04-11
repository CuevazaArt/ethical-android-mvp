# UniversalEthos + Hub — canonical architecture (vision ↔ code)

**Purpose:** Single source of truth for the *DemocraticBuffer / multicultural overlays*, *services hub*, *audit protocol*, *evolution loops*, and the *V11–V12 module map*. Detailed phase specs remain in versioned proposals ([V11](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md), [V12](PROPOSAL_ETOSOCIAL_STATE_V12.md)); this document **unifies** narrative and **maps** to `src/` without duplicating their env tables.

**Kernel contract:** MalAbs → `PreloadedBuffer` (L0) remains the **normative core**. Hub layers add governance, audit, and operations **without** bypassing safety.

**Governance honesty (Issue 6):** mock DAO vs immutable L0, exit checklist, public landing alignment — [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md).

---

## 1. DemocraticBuffer & UniversalEthos (cultural overlays)

| Layer | Role | Code today |
|-------|------|------------|
| **L0 — Kernel core** | Human-rights class absolutes + MalAbs; immutable vs simple majorities | `PreloadedBuffer` in `buffer.py`, `AbsoluteEvilDetector` |
| **L1 / L2 — Cultural overlays** | Regional coexistence norms and owner preferences (vision: community votes) | **Drafts** on `EthicalKernel` (`constitution_l1_drafts` / `constitution_l2_drafts`), snapshot **schema v2+**, DAO proposals via **V12.3** |
| **Non-contradiction (deontic gate)** | Block “cultural forks” that contradict L0 | **`deontic_gate.py`** — heuristic check + explicit **repeal of named `PreloadedBuffer` principles** (`repeal no_harm`, …) when `KERNEL_DEONTIC_GATE`; not full deontic logic |

**Flow:** `add_constitution_draft` → optional deontic check → `submit_constitution_draft_for_vote` → `MockDAO` quadratic vote → `resolve` → **`apply_proposal_resolution_to_constitution_drafts`** updates draft `status` (`approved` / `rejected`). L0 is **never** written by vote.

---

## 2. Services hub & employment (economic motor)

| Concept | Vision | Code / stub |
|---------|--------|-------------|
| **Distributed justice** | External ethical arbitration | **V11** `judicial_escalation` + mock tribunal (`MockDAO`) |
| **Expert-in-the-loop (gray zone)** | Philosophers + devs propose **Bayesian weight** adjustments after ambiguous inference | **`ml_ethics_tuner.py`** — audit line when turn is gray zone (`KERNEL_ML_ETHICS_TUNER_LOG`); no weight mutation in MVP |
| **Reparation fund** | DAO treasury pays third parties after validated votes | **`reparation_vault.py`** — mock **intent** → DAO audit (`KERNEL_REPARATION_VAULT_MOCK`); after **V11 mock tribunal**, `maybe_register_reparation_after_mock_court` (in `kernel.process_chat_turn`) |
| **Soul / firmware care** | Backup + updates | Persistence + **NomadIdentity** (`nomad_identity.py`) + `ImmortalityProtocol` |

---

## 3. Experimental audit protocol (observation levels)

| Level | Focus | Existing instrumentation |
|-------|--------|---------------------------|
| **1 — Social / environment** | What the model “sees” in Uchi‑Soto / perception | `KERNEL_TRANSPARENCY_AUDIT`, WebSocket `perception`, `sensor` fusion (v8) |
| **2 — Vitality / safety** | Battery, multimodal trust, critical thresholds | `KERNEL_CHAT_INCLUDE_VITALITY`, `multimodal_trust`, vitality module |
| **3 — Operability** | Digital actions, permissions | DAO audit, `decision` in WebSocket JSON, generative `proposal_id` (v9.2) |

**Monologue ↔ sensor:** Not a single UI product; building blocks are `monologue`, `sensor`, `perception` in the same JSON payload. **Future:** explicit trace IDs (design).

---

## 4. Evolutionary loops (living firmware)

| Step | Vision | Code today |
|------|--------|------------|
| Incident / gray-zone registration | Archive in DAO | `MLEthicsTuner` audit line; narrative episodes; escalation audit (V11) |
| Deliberation | Monthly votes on firmware | **Mock** DAO proposals + resolve (V12.3); no calendar |
| Nomadic deploy | P2P updates to all instances | **Not implemented**; persistence + export/import checkpoints |

---

## 5. Module map (V11 hub naming ↔ repository)

| Name | Intended role | Implementation |
|------|-----------------|----------------|
| **DemocraticBuffer** | L0 immutable + L1/L2 governance path | `buffer.py` + `moral_hub.py` + `MockDAO` + persistence |
| **MLEthicsTuner** | Expert loop for gray-zone weight tuning | `ml_ethics_tuner.py` (audit only in MVP) |
| **ReparationVault** | Indemnification fund | `reparation_vault.py` (mock audit) |
| **NomadIdentity** | Hardware jump + continuity of self | `nomad_identity.py` (facade) + `ImmortalityProtocol` + checkpoint; HAL: [PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMADIC_CONSCIOUSNESS_HAL.md), `hardware_abstraction.py`, `existential_serialization.py` |

---

## References

- [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md) — V12.1–V12.4 registry and env vars  
- [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) — justice track  
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — snapshot schema  
- [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) — traceability  

*Ex Machina Foundation — unified hub vision; kernel ethics contract unchanged.*
