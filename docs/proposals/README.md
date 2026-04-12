# `docs/proposals/` — design, theory, and operations

**Reference** and **exploratory** material: versioned proposals, runtime contracts, theory ↔ code maps, operator guides, and design threads. This is **not** a substitute for the issue backlog or the root product README.

This directory is the **single** unified location for what used to live in `docs/discusion/`, `docs/experimental/`, and assorted top-level `docs/*.md` files. **ADRs** remain in [`docs/adr/`](../adr/README.md). Graphics and media: [`docs/multimedia/`](../multimedia/README.md).

---

## What’s new (April 2026)

High-level summary aligned with the code and docs; full chronology is in [`CHANGELOG.md`](../../CHANGELOG.md).

| Area | What changed |
|------|----------------|
| **Docs** | Single **`docs/proposals/`** tree; repo links point here. ADRs and templates were not moved. |
| **Uchi–Soto (roster)** | **Phase 3** in the kernel: `RelationalTier`, sensor-trust EMA, forget buffer, `linked_peer_ids`, wired into `process` / chat. See [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md). |
| **User model** | Enrichment phases A–C: cognitive pattern, risk band, judicial phase and checkpoint; snapshot persistence. See [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md). |
| **Time / Bayes** | Temporal horizon prior (Bayesian mixture, ADR 0005). See [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md). |
| **Perception** | Pydantic validation, coherence checks, local fallback. See [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md). |
| **MVP status** | Per-module maturity table and gaps. See [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md). |
| **Brand / media** | Canonical logo [`docs/multimedia/media/logo.png`](../multimedia/media/logo.png); index in [multimedia README](../multimedia/README.md). |

---

## Start here

| If you need… | Open |
|--------------|------|
| **Next ~2 weeks — triage, P0/P1/P2, reproduction checklists** | [PLAN_IMMEDIATE_TWO_WEEKS.md](PLAN_IMMEDIATE_TWO_WEEKS.md) |
| **Module count vs observable ethics (ablation gap, tiers A–E)** | [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](MODULE_IMPACT_AND_EMPIRICAL_GAP.md) |
| **Mock DAO — no chain, QV assumptions, not policy core** | [MOCK_DAO_SIMULATION_LIMITS.md](MOCK_DAO_SIMULATION_LIMITS.md) |
| Theory ↔ implementation map and tests | [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) |
| Runtime contract (English) | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
| Snapshot and persistence | [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) |
| Runtime phases / migration | [RUNTIME_PHASES.md](RUNTIME_PHASES.md), [RUNTIME_FASES.md](RUNTIME_FASES.md) (Spanish) |
| Current kernel status | [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) |
| Operator quick reference | [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) |

---

## Versioned proposals (v6–v12 line and annexes)

Legacy Spanish filenames (`PROPUESTA_*.md`, `ESTRATEGIA_Y_RUTA.md`, `PAPER_AFECTO_*.md`) are **redirect stubs** to the matching `PROPOSAL_*.md` / `STRATEGY_AND_ROADMAP.md` / `PAPER_AFFECT_*.md` files. Prefer linking to the English paths in new text.

| Document | Topic |
|----------|--------|
| [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md) | Self-reference / GWT / drives / narrative self (v6) — *Spanish* |
| [PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md](PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md) | Coherent phases, model inventory, exclusions — *English* |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Five pillars, MVP status per pillar, open threads — *English* |
| [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) | Light ToM, chronobiology, premise advisory, qualitative teleology — *English* |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | Situated organism: sensor fusion, vitality, agency, hardware — *English* |
| [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md) | v8 extension: vitality, sacrifice, dignified closure, narrative legacy — *English* |
| [DEMO_SITUATED_V8.md](DEMO_SITUATED_V8.md) | Situated v8 demo |
| [PROPOSAL_GUARDIAN_ANGEL.md](PROPOSAL_GUARDIAN_ANGEL.md) | Guardian Angel mode (tone only; no second veto) — *English* |
| [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) | v9 pillars (epistemic, generative, swarm, metaplanning) — *English* |
| [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](PROPOSAL_OPERATIONAL_STRATEGY_V10.md) | v10 operations: gray-zone diplomacy, skills, somatic markers — *English* |
| [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) | V11 governance, DAO audit, roadmap — *English* |
| [PROPOSAL_REALITY_VERIFICATION_V11.md](PROPOSAL_REALITY_VERIFICATION_V11.md) | Reality verification (design) |
| [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md) | V12 registry, env vars, unified architecture pointer |
| [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md) | Multi-agent roster, Uchi–Soto tiers, forget buffer, Phase 3 implemented |
| [PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md](PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md) | DAO alerts and transparency |
| [PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md](PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md) | Nomadic instantiation, HAL, existential serialization — *English* |
| [UNIVERSAL_ETHOS_AND_HUB.md](UNIVERSAL_ETHOS_AND_HUB.md) | Hub vision ↔ code, UniversalEthos layers, module map — *English* |

---

## Runtime, environment, and decision chain

| Document | Topic |
|----------|--------|
| [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) | Runtime contract |
| [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) | Persistence (English) |
| [RUNTIME_PERSISTENTE.md](RUNTIME_PERSISTENTE.md) | Persistence (Spanish) |
| [RUNTIME_PHASES.md](RUNTIME_PHASES.md) | Runtime phases |
| [RUNTIME_FASES.md](RUNTIME_FASES.md) | Phases (Spanish) |
| [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) | Environment variable policy |
| [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) | Core decision chain |
| [ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md](ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md) | 30-day plan: compose, ethical telemetry, persistence migrations, operator manual — *English* |
| [RUNTIME_PROFILES_OPERATOR_TABLE.md](RUNTIME_PROFILES_OPERATOR_TABLE.md) | `ETHOS_RUNTIME_PROFILE` names, risks, LAN/semantic notes — *English* |

---

## Governance, user model, and semantic layers

| Document | Topic |
|----------|--------|
| [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md) | MockDAO and L0 layer |
| [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) | User model enrichment (judicial, cognitive, risk) |
| [LIGHTHOUSE_KB.md](LIGHTHOUSE_KB.md) | Lighthouse knowledge base |
| [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) | MALABS semantic layers |
| [PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md](PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) | Psi Sleep v2 (feedback + mixture), semantic gate as default perception — *English* |

---

## Perception, poles, time, and input trust

| Document | Topic |
|----------|--------|
| [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) | Perception validation (Pydantic, coherence) |
| [POLES_WEAKNESS_PAD_AND_PROFILES.md](POLES_WEAKNESS_PAD_AND_PROFILES.md) | Poles, weakness, PAD, and profiles |
| [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md) | Pole weights: heuristics vs empirical calibration roadmap |
| [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) | Temporal horizon prior (ADR 0005) |
| [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) | Input-trust threat model / advisory telemetry |

---

## Local infra, LLM, nomad, and landing

| Document | Topic |
|----------|--------|
| [LANDING_DECOUPLING_AND_SUPPORT.md](LANDING_DECOUPLING_AND_SUPPORT.md) | Next.js `landing/`: support level, versioning, robots sync, dashboard iframe vs standalone |
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | Local PC and mobile LAN |
| [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) | Nomad PC–smartphone bridge |
| [LLM_STACK_OLLAMA_VS_HF.md](LLM_STACK_OLLAMA_VS_HF.md) | Ollama vs Hugging Face |

---

## Strategy, hardening, and traceability

| Document | Topic |
|----------|--------|
| [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md) | Strategy and roadmap — *English* |
| [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) | Production hardening roadmap |
| [PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md) | Phase 2 core/extensions seam + `KernelEventBus` (ADR 0006) |
| [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) | Critique, roadmap, and issues |
| [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md) | Phased remediation — core integrity vs. governance (backlog structure) |
| [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) | Project status and per-module maturity |
| [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) | Recent implementation trace (Guardian, v9–v10) ↔ bibliography |
| [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) | Operator quick reference |

---

## Empirical pilots and P2P threats

| Document | Topic |
|----------|--------|
| [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md) | Empirical pilot methodology |
| [ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md](ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md) | External vs circular ethical evaluation (expert baselines, rubrics) |
| [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md) | Issue 3 — interpreting agreement metrics; not moral certification |
| [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md) | Empirical pilot protocol |
| [SWARM_P2P_THREAT_MODEL.md](SWARM_P2P_THREAT_MODEL.md) | Swarm P2P threat model |

---

## Consciousness, affect, and experimentation (not the live contract)

| Document | Topic |
|----------|--------|
| [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) | Experimental consciousness / affect archetypes |
| [PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md](PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md) | Draft paper (affect, phenomena, hypotheses) — *English* |

---

## Elsewhere in the repository

- **Architecture decisions:** [`docs/adr/`](../adr/README.md)  
- **Versioned changes:** [`CHANGELOG.md`](../../CHANGELOG.md)  
- **Narrative history:** [`HISTORY.md`](../../HISTORY.md)  
- **Bibliography:** [`BIBLIOGRAPHY.md`](../../BIBLIOGRAPHY.md)  
- **Product and development:** [root README](../../README.md)
