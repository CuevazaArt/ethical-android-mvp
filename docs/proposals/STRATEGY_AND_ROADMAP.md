# Strategy, roadmap, and risks — Ethos Kernel

**Synthesis** document (April 2026): conclusions from project review, realistic expectations, **roadmap readjustment**, and the **main gap** that drives the next work.

**Relationship to other docs:** the normative core and advisory layers remain described in [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) and [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). Proposal files under `docs/proposals/` are design; **this file is product / operations governance**.

**Quick index (2026 coherence):** [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) · [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) · [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) · [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) · [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) · [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md) · [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) · [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) · [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) · [adr/README.md](adr/README.md).

---

## 1. Where we are (verifiable facts)

- The repository is an **MVP runtime** on an ethical kernel (v5) with **fixed simulations**, **WebSocket chat**, versioned persistence, **governance mocks** (DAO, simulated court), constitutional hub, **HAL / nomadic identity**, `HubAudit`-style auditing, and **optional** JSON checkpoint encryption.
- The **test suite** covers core invariants and server smoke/integration tests; CI installs `requirements.txt` and runs `pytest` on Python 3.11 and 3.12.
- **Documentation** (CHANGELOG, HISTORY, proposals) is extensive; the risk is not missing text but **operational coherence** across `KERNEL_*` combinations.

---

## 2. Recorded conclusions (constructive critique)

### 2.1 Strengths

- **Ethical invariants** with dedicated tests; runtime wraps the core with flags rather than replacing it.
- **Versioned persistence** and migration from older snapshots support demo and dev continuity.
- **Explicit mocks** (DAO, court, vault) avoid confusing demo with real distributed infrastructure.
- **Traces and auditing** (`HubAudit`, DAO lines) help narrative and debugging; they are not by themselves legal or cryptographic evidence.

### 2.2 Expectations vs. what the code can promise

| Area | Common expectation | MVP reality |
|------|-------------------|-------------|
| Governance | “Real democracy” | **Off-chain** pipeline in-process + snapshot state; no network, strong identity, or distributed threat model. |
| Security / privacy | “Protected data” | Fernet on **JSON on disk**; SQLite rows remain plain JSON; threat model must be documented per layer. |
| Nomadic consciousness | “Hardware continuity” | HAL abstraction + narrative + auditing; physical integrity remains **declarative / stub** without integration. |
| Product coherence | “One product” | Many dimensions (ethics, relational, sensors, judicial, hub, nomad); coherence depends on **contracts** and supported **profiles**. |

### 2.3 Active risks

1. **Operational complexity:** environment-variable combinatorics; without named profiles, maintenance and support get expensive.
2. **Two worlds:** formal ethical pipeline vs. advisory layers; layers must stay documented as **non-veto** unless the contract says otherwise.
3. **Documentation vs. velocity:** more proposals do not replace a **status index** (what is “demo-stable” vs. experimental).

---

## 3. Readjusted roadmap (priorities)

The previous roadmap still prioritized features (metaplan, generative LLM, swarm). **Adjusted** as follows:

| Priority | Focus | Goal |
|----------|--------|------|
| **P0** | **Runtime profiles** + CI smoke tests | Reduce accidental surface: demos and CI know **supported env sets** (`src/runtime_profiles.py`). |
| **P1** | Goal / marker persistence (when due) | Longitudinal continuity aligned with snapshot and round-trip tests. |
| **P2** | Generative / local LLM / metaplanning | Only with acceptance criteria and clear MalAbs tests. |
| **P3** | Swarm / P2P | Outside the core until an explicit threat model exists. |

**Next task executed as the P0 gap closure:** definition of `RUNTIME_PROFILES` and `tests/test_runtime_profiles.py` (included in `pytest tests/` for CI).

### 3.1 Recommended delivery order (robustness → epistemology → demo)

1. **Robustness:** profiles in `src/runtime_profiles.py` (`apply_runtime_profile` in tests); CI runs `tests/test_runtime_profiles.py` with the rest of `tests/`; strengthen MalAbs / perception in `tests/test_input_trust.py` with [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md).
2. **Epistemology:** operational lighthouse KB and limits in [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md); tests in `tests/test_reality_verification.py` / `tests/test_lighthouse_kb_schema.py`.
3. **Demo / situated:** **closed** with nominal profile **`situated_v8_lan_demo`** + guide [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md) (v8 + LAN without raw hardware); frame [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md), network steps [`LOCAL_PC_AND_MOBILE_LAN.md`](LOCAL_PC_AND_MOBILE_LAN.md).

---

## 4. Nominal profiles (operators and CI)

Names and variables live in code: **`src/runtime_profiles.py`**. Summary:

| Profile | Role |
|---------|------|
| `baseline` | No extra flags; regression baseline. |
| `judicial_demo` | Judicial escalation + mock court + judicial JSON. |
| `hub_dao_demo` | Public constitution HTTP + DAO actions over WebSocket. |
| `nomad_demo` | HAL simulation + nomadic migration audit. |
| `reality_lighthouse_demo` | JSON lighthouse (`KERNEL_LIGHTHOUSE_KB_PATH`) + `reality_verification` in WebSocket; run from repo root. |
| `lan_mobile_thin_client` | `CHAT_HOST=0.0.0.0` for mobile client on same WiFi ([LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)). |
| `operational_trust` | “Stoic” WebSocket UX: no homeostasis / monologue / experience_digest — core policy unchanged ([POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md), Issue 5). |
| `lan_operational` | `lan_mobile_thin_client` + `operational_trust`: WiFi LAN with minimal narrative JSON ([KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md), Issue 7). |
| `moral_hub_extended` | Extended V12 hub: public constitution + DAO vote + `deontic_gate` + transparency audit (Issue 7). |
| `situated_v8_lan_demo` | Situated v8: LAN + `KERNEL_SENSOR_*` (fixture + preset) + vitality / multimodal in JSON — [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md). |

**Flag policy (Issue 7):** `KERNEL_*` families, **not recommended** combinations, and deprecation posture — **[KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md)**.

**Experimental:** any other `KERNEL_*` combination is **not guaranteed** until a profile or dedicated test is added.

**Epistemic pillar (V11+):** see [PROPOSAL_REALITY_VERIFICATION_V11.md](PROPOSAL_REALITY_VERIFICATION_V11.md) — local lighthouse vs. rival premises (implemented); distillation and DAO veto (pending).

**Nomad PC–smartphone bridge:** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — hardware classes, compatibility layers to build, smartphone as first step toward coordinated sensory perception; field network under operator direction.

---

## 5. Public backlog (technical critique → issues)

After **two** independent external reviews (April 2026), the project publishes an **honest scope statement** and **seven consolidated items** (redundant themes merged: e.g. text lists + **GIGO perception** risk → one P0 **input trust** epic). Includes: documented core + pip packaging *spike*, HCI/weakness in critical domains, honest **L0 immutable vs. community drafts** policy. Content ready to paste as *GitHub Issues*:

- **[CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md)**

The public [Roadmap](https://mosexmacchinalab.com/roadmap) summarizes the same track for partners and visitors.

---

## 6. Cross-references

- [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) — per-module maturity snapshot and known gaps (April 2026).
- [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) — recent technical traceability; the “Next development session” section points here for the route.
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — persistence and Fernet.
- [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) — hub map.
- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) — `KERNEL_*` variable policy (Issue 7).
- [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) — **non-binding** roadmap toward deployment hardening (phases 1–3); **review synthesis** (strengths, critiques, conclusions); doc round closed — follow-up in issues/ADRs.

---

*Ex Machina Foundation — living document; align roadmap changes with CHANGELOG and HISTORY.*
