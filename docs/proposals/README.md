# `docs/proposals/` — design, theory, and operations

**Reference** and **exploratory** material: versioned proposals, runtime contracts, theory ↔ code maps, operator guides, and design threads. This is **not** a substitute for the issue backlog or the root product README.

This directory is the **single** unified location for what used to live in `docs/discusion/`, `docs/experimental/`, and assorted top-level `docs/*.md` files. **ADRs** remain in [`docs/adr/`](../adr/README.md). Graphics and media: [`docs/multimedia/`](../multimedia/README.md).

---

## What’s new (April 2026)

High-level summary aligned with the code and docs; full chronology is in [`CHANGELOG.md`](../../CHANGELOG.md).

| Area | What changed |
|------|----------------|
| **Docs** | Single **`docs/proposals/`** tree; repo links point here. ADRs and templates were not moved. |
| **Uchi–Soto (roster)** | **Phase 3** in the kernel: `RelationalTier`, sensor-trust EMA, forget buffer, `linked_peer_ids`, wired into `process` / chat. See [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md). |
| **User model** | Enrichment phases A–C: cognitive pattern, risk band, judicial phase and checkpoint; snapshot persistence. See [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md). |
| **Time / Bayes** | Temporal horizon prior (Bayesian mixture, ADR 0005). See [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md). |
| **Perception** | Pydantic validation, coherence checks, local fallback. See [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md). |
| **MVP status** | Per-module maturity table and gaps. See [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md). |
| **Brand / media** | Canonical logo [`docs/multimedia/media/logo.png`](../multimedia/media/logo.png); index in [multimedia README](../multimedia/README.md). |

---

## Start here

| If you need… | Open |
|--------------|------|
| Theory ↔ implementation map and tests | [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) |
| Runtime contract (English) | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
| Snapshot and persistence | [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) |
| Runtime phases / migration | [RUNTIME_PHASES.md](RUNTIME_PHASES.md), [RUNTIME_FASES.md](RUNTIME_FASES.md) (Spanish) |
| Current kernel status | [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) |
| Operator quick reference | [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) |

---

## Versioned proposals (v6–v12 line and annexes)

| Document | Topic |
|----------|--------|
| [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md) | Self-reference / GWT / drives / narrative self (v6) — *Spanish* |
| [PROPUESTA_INTEGRACION_APORTES_V6.md](PROPUESTA_INTEGRACION_APORTES_V6.md) | Coherent phases, model inventory, exclusions — *Spanish* |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Five pillars, MVP status per pillar, open threads — *Spanish* |
| [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) | Light ToM, chronobiology, premise advisory, qualitative teleology — *Spanish* |
| [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) | Situated organism: sensor fusion, vitality, agency, hardware — *Spanish* |
| [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md) | v8 extension: vitality, sacrifice, dignified closure, narrative legacy — *Spanish* |
| [DEMO_SITUATED_V8.md](DEMO_SITUATED_V8.md) | Situated v8 demo |
| [PROPUESTA_ANGEL_DE_LA_GUARDIA.md](PROPUESTA_ANGEL_DE_LA_GUARDIA.md) | Guardian Angel mode (tone only; no second veto) — *Spanish* |
| [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | v9 pillars (epistemic, generative, swarm, metaplanning) — *Spanish* |
| [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md) | v10 operations: gray-zone diplomacy, skills, somatic markers — *Spanish* |
| [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) | V11 governance, DAO audit, roadmap — *English* in key phases |
| [PROPUESTA_VERIFICACION_REALIDAD_V11.md](PROPUESTA_VERIFICACION_REALIDAD_V11.md) | Reality verification (design) |
| [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](PROPUESTA_ESTADO_ETOSOCIAL_V12.md) | V12 registry, env vars, unified architecture pointer |
| [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) | Multi-agent roster, Uchi–Soto tiers, forget buffer, Phase 3 implemented |
| [PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md](PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md) | DAO alerts and transparency |
| [PROPUESTA_CONCIENCIA_NOMADA_HAL.md](PROPUESTA_CONCIENCIA_NOMADA_HAL.md) | Nomadic instantiation, HAL, existential serialization — *Spanish* |
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
| [TEMPORAL_PRIOR_HORIZONS.md](TEMPORAL_PRIOR_HORIZONS.md) | Temporal horizon prior (ADR 0005) |
| [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) | Input-trust threat model / advisory telemetry |

---

## Local infra, LLM, and nomad

| Document | Topic |
|----------|--------|
| [LOCAL_PC_AND_MOBILE_LAN.md](LOCAL_PC_AND_MOBILE_LAN.md) | Local PC and mobile LAN |
| [NOMAD_PC_SMARTPHONE_BRIDGE.md](NOMAD_PC_SMARTPHONE_BRIDGE.md) | Nomad PC–smartphone bridge |
| [LLM_STACK_OLLAMA_VS_HF.md](LLM_STACK_OLLAMA_VS_HF.md) | Ollama vs Hugging Face |

---

## Strategy, hardening, and traceability

| Document | Topic |
|----------|--------|
| [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) | Strategy and roadmap (Spanish) |
| [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md) | Production hardening roadmap |
| [PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md) | Phase 2 core/extensions seam + `KernelEventBus` (ADR 0006) |
| [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) | Critique, roadmap, and issues |
| [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) | Project status and per-module maturity |
| [TRACE_IMPLEMENTATION_RECENT.md](TRACE_IMPLEMENTATION_RECENT.md) | Recent implementation trace (Guardian, v9–v10) ↔ bibliography |
| [OPERATOR_QUICK_REF.md](OPERATOR_QUICK_REF.md) | Operator quick reference |

---

## Empirical pilots and P2P threats

| Document | Topic |
|----------|--------|
| [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md) | Empirical pilot methodology |
| [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md) | Empirical pilot protocol |
| [SWARM_P2P_THREAT_MODEL.md](SWARM_P2P_THREAT_MODEL.md) | Swarm P2P threat model |

---

## Consciousness, affect, and experimentation (not the live contract)

| Document | Topic |
|----------|--------|
| [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) | Experimental consciousness / affect archetypes |
| [PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md](PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md) | Draft paper (affect, phenomena, hypotheses) — *Spanish* |

---

## Elsewhere in the repository

- **Architecture decisions:** [`docs/adr/`](../adr/README.md)  
- **Versioned changes:** [`CHANGELOG.md`](../../CHANGELOG.md)  
- **Narrative history:** [`HISTORY.md`](../../HISTORY.md)  
- **Bibliography:** [`BIBLIOGRAPHY.md`](../../BIBLIOGRAPHY.md)  
- **Product and development:** [root README](../../README.md)
