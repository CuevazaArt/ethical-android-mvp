# Strategy, roadmap and risks — Ethos Kernel

**Synthesis** document (April 2026): conclusions from the project review, realistic expectations, **roadmap readaptation**, and the **main gap** that prioritizes the next work.

**Relationship with other docs:** the normative core and advisory layers continue to be described in [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) and [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md). The PROPOSALs in `docs/discusion/` are design; this file is **product governance / operations**.

**Quick index (2026 coherence):** [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) · [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) · [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) · [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) · [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) · [discusion/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](discusion/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) · [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) · [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) · [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) · [adr/README.md](adr/README.md).

---

## 1. Where we are (verifiable facts)

- The repository is a **runtime MVP** on an ethical kernel (v5) with **fixed simulations**, **WebSocket chat**, versioned persistence, **governance mocks** (DAO, simulated tribunal), constitutional hub, **HAL / nomadic identity**, `HubAudit`-style auditing, and **optional encryption** of JSON checkpoints.
- The **test suite** covers core invariants and server smoke/integration tests; CI installs `requirements.txt` and runs `pytest` on Python 3.11 and 3.12.
- The **documentation** (CHANGELOG, HISTORY, PROPOSAL) is rich; the risk is not a lack of text but **operational coherence** between combinations of `KERNEL_*`.

---

## 2. Recorded conclusions (constructive critique)

### 2.1 Strengths

- **Ethical invariants** with dedicated tests; the runtime does not replace the core but wraps it with flags.
- **Versioned persistence** and migration from old snapshots favor continuity of demos and development.
- **Explicit mocks** (DAO, court, vault) avoid confusing demo with real distributed infrastructure.
- **Traces and auditing** (`HubAudit`, lines in DAO) help with narrative and debugging; they are not by themselves legal or cryptographic evidence.

### 2.2 Expectations vs. what the code can promise

| Area | Common expectation | MVP reality |
|--------|------------------------|------------------|
| Governance | “Real democracy” | **Off-chain** pipeline in process + state in snapshot; no network, strong identity, or distributed threat model. |
| Security / privacy | “Protected data” | Fernet on **JSON on disk**; SQLite remains in plain text; the threat model must be documented per layer. |
| Nomadic consciousness | “Hardware continuity” | HAL abstraction + narrative + auditing; actual physical integrity remains **declarative / stub** where there is no integration. |
| Product coherence | “A single product” | Many dimensions (ethical, relational, sensors, judicial, hub, nomadic); coherence depends on supported **contracts** and **profiles**. |

### 2.3 Active risks

1. **Operational complexity:** combinatorics of environment variables; without nominal profiles, maintenance and support become expensive.
2. **Two worlds:** formal ethical pipeline vs. advisory layers; layers must remain documented as **non-veto** unless the contract says otherwise.
3. **Documentation vs. speed:** more PROPOSALs do not replace a **status index** (what is “stable for demo” vs. experimental).

---

## 3. Readapted roadmap (priorities)

The previous roadmap kept prioritizing features (metaplan, generative LLM, swarm). **Adjusted** as follows:

| Priority | Focus | Goal |
|-----------|---------|----------|
| **P0** | **Runtime profiles** + smoke tests in CI | Reduce accidental surface: demos and CI know **supported env sets** (`src/runtime_profiles.py`). |
| **P1** | Goal / marker persistence (when due) | Longitudinal continuity aligned with snapshot and round-trip tests. |
| **P2** | Generative / local LLM / metaplanning | Only with clear acceptance criteria and MalAbs tests. |
| **P3** | Swarm / P2P | Outside the core until an explicit threat model is defined. |

**Next task executed as gap-closing for P0:** definition of `RUNTIME_PROFILES` and `tests/test_runtime_profiles.py` (included in `pytest tests/` by CI).

### 3.1 Recommended delivery order (robustness → epistemology → demo)

1. **Robustness:** profiles in `src/runtime_profiles.py` (`apply_runtime_profile` in tests); CI runs `tests/test_runtime_profiles.py` alongside the rest of `tests/`; reinforcement of MalAbs / perception in `tests/test_input_trust.py` with [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md).
2. **Epistemology:** operational KB lighthouse and limits in [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md); tests in `tests/test_reality_verification.py` / `tests/test_lighthouse_kb_schema.py`.
3. **Demo / situated:** **closed** with nominal profile **`situated_v8_lan_demo`** + guide [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md) (v8 + LAN without raw hardware); framework [`PROPUESTA_ORGANISMO_SITUADO_V8.md`](discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md), network steps [`LOCAL_PC_AND_MOBILE_LAN.md`](LOCAL_PC_AND_MOBILE_LAN.md).

---

## 4. Nominal profiles (operators and CI)

Names and variables live in code: **`src/runtime_profiles.py`**. Summary:

| Profile | Role |
|--------|-----|
| `baseline` | No extra flags; baseline for regression. |
| `judicial_demo` | Judicial escalation + mock tribunal + judicial JSON. |
| `hub_dao_demo` | Public HTTP constitution + DAO actions via WebSocket. |
| `nomad_demo` | HAL simulation + nomadic migration auditing. |
| `reality_lighthouse_demo` | JSON lighthouse (`KERNEL_LIGHTHOUSE_KB_PATH`) + `reality_verification` JSON in WebSocket; run from repo root. |
| `lan_mobile_thin_client` | `CHAT_HOST=0.0.0.0` for mobile client on the same WiFi ([LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md)). |
| `operational_trust` | “Stoic” UX in WebSocket: no homeostasis / monologue / experience_digest — core policy unchanged ([POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md), Issue 5). |
| `lan_operational` | `lan_mobile_thin_client` + `operational_trust`: WiFi LAN with minimal narrative JSON ([KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md), Issue 7). |
| `moral_hub_extended` | Extended V12 hub: public constitution + DAO vote + `deontic_gate` + transparency auditing (Issue 7). |
| `situated_v8_lan_demo` | Situated v8: LAN + `KERNEL_SENSOR_*` (fixture + preset) + vitality / multimodal in JSON — [`DEMO_SITUATED_V8.md`](DEMO_SITUATED_V8.md). |

**Flags policy (Issue 7):** `KERNEL_*` families, **non-recommended** combinations and deprecation stance — **[KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md)**.

**Experimental:** any other combination of `KERNEL_*` is considered **unsupported** until a dedicated profile or test is added.

**Epistemic pillar (V11+):** see [PROPUESTA_VERIFICACION_REALIDAD_V11.md](discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md) — local lighthouse vs. rival premises (implemented); distillation and DAO veto (pending).

**PC–smartphone nomadic bridge:** [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) — hardware classes, compatibility layers to develop, smartphone as a first approximation to coordinated sensory perception; secure network for field use under operator instruction.

---

## 5. Public backlog (technical critique → issues)

After **two** independent external reviews (April 2026), the project publishes an **honest disclaimer** and **seven consolidated items** (redundant topics merged: e.g., text lists + risk of **GIGO perception** → a single P0 epic on **input trust**). Includes: documented core + pip packaging spike, HCI/weakness in critical domains, honest policy **immutable L0 vs. community drafts**. Content ready to paste as *GitHub Issues*:

- **[CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md)**

The [Roadmap](https://mosexmacchinalab.com/roadmap) landing summarizes the same track for partners and visitors.

---

## 6. Cross-references

- [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) — maturity snapshot by module and conscious gaps (April 2026).
- [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) — recent technical traceability; the “Next development session” section points here for the roadmap.
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — persistence and Fernet.
- [discusion/UNIVERSAL_ETHOS_AND_HUB.md](discusion/UNIVERSAL_ETHOS_AND_HUB.md) — hub map.
- [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) — `KERNEL_*` variable policy (Issue 7).
- [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) — **non-binding** roadmap toward deployment hardening (phases 1–3); **synthesis of reviews** (strengths, critiques, conclusions); documentary round closed — tracking in issues/ADRs.

---

*Ex Machina Foundation — living document; align roadmap changes with CHANGELOG and HISTORY.*
