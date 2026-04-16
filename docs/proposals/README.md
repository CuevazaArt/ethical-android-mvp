# `docs/proposals/` — design, theory, and operations

**Reference** and **exploratory** material: versioned proposals, runtime contracts, theory ↔ code maps, operator guides, and design threads. This is **not** a substitute for the issue backlog or the root product README.

This directory is the **single** unified location for what used to live in `docs/discusion/`, `docs/experimental/`, and assorted top-level `docs/*.md` files. **ADRs** remain in [`docs/adr/`](../adr/README.md). Graphics and media: [`docs/multimedia/`](../multimedia/README.md).

---

## What’s new (April 2026)

High-level summary aligned with the code and docs; full chronology is in [`CHANGELOG.md`](../../CHANGELOG.md).

| Document | Summary |
|----------|---------|
| [`PROPOSAL_001_HARDENIDO_DE_MODULOS_PRIMITIVOS.md`](PROPOSAL_001_HARDENIDO_DE_MODULOS_PRIMITIVOS.md) | Antigravity: hardening plan for primitive modules (filename legacy; content English). |
| [`PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md`](PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md) | Antigravity: narrative / cognitive architecture pillar; tiers 1–3. |
| [`PROPOSAL_003_NARRATIVE_HARDENING_ANALYSIS.md`](PROPOSAL_003_NARRATIVE_HARDENING_ANALYSIS.md) | Antigravity: narrative hardening (encryption, integrity, Uchi–Soto). |
| [`PROPOSAL_004_NARRATIVE_IDENTITY_REFLECTION.md`](PROPOSAL_004_NARRATIVE_IDENTITY_REFLECTION.md) | Antigravity: narrative identity reflection layer. |
| [`PROPOSAL_005_NARRATIVE_RESILIENCE_AND_HIERARCHY.md`](PROPOSAL_005_NARRATIVE_RESILIENCE_AND_HIERARCHY.md) | Antigravity: narrative resilience and memory hierarchy. |
| [`PROPOSAL_008_METACOGNITIVE_CURIOSITY.md`](PROPOSAL_008_METACOGNITIVE_CURIOSITY.md) | Cursor: metacognitive curiosity and epistemic alignment. |
| [`PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md`](PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md) | Antigravity: distributed justice and blockchain-style DAO (design scope). |
| [`PROPOSAL_010_CRITIQUE_SYNTESIS_AND_ALIGNMENT.md`](PROPOSAL_010_CRITIQUE_SYNTESIS_AND_ALIGNMENT.md) | Antigravity: architectural critique synthesis and alignment plan (phase 7). |
| [`PROPOSAL_011_DAO_CALIBRATION_PIPELINE.md`](PROPOSAL_011_DAO_CALIBRATION_PIPELINE.md) | Antigravity: DAO calibration pipeline and boundary-safety caps (phase 7). |
| [`ANTIGRAVITY_COLLABORATION_GUIDE.md`](ANTIGRAVITY_COLLABORATION_GUIDE.md) | Antigravity: collaboration guide and operational workflows. |
| [`PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md`](PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md) | ADR 0012 stack: BMA (L1), feedback posteriors (L2), context buckets (L3), softmax / importance-sampling likelihood, env vars, tests, link to ADR 0012. |
| [`PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md`](PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md) | Offline taxonomy (voluntary, transient, structural, systemic); L0 vs curated knowledge pack; resource/energy priority; entry planning and sync; maps to `PreloadedBuffer` and MalAbs. |

| Area | What changed |
|------|----------------|
| **Docs** | Single **`docs/proposals/`** tree; repo links point here. ADRs and templates were not moved. **April 2026:** proposal snapshots reconcile against **`main-whit-landing`** for bibliography + landing. **Cursor team charter (sensors + perception):** [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md). |
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
| **Claude team — real Bayesian inference scope** | [CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md](CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md) |
| **Cursor team — sensors & perception (mission charter)** | [CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) |
| **Model-critical backlog (post–perception P0 sequencing)** | [MODEL_CRITICAL_BACKLOG.md](MODEL_CRITICAL_BACKLOG.md) |
| **Honest April 2026 project critique** | [PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md](PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md) |
| **LLM touchpoint env precedence (team matrix)** | [PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) |
| **LLM integration track (ownership + gap register G-01…)** | [PROPOSAL_LLM_INTEGRATION_TRACK.md](PROPOSAL_LLM_INTEGRATION_TRACK.md) |
| **LLM vertical roadmap (phased operator + observability + tests)** | [PROPOSAL_LLM_VERTICAL_ROADMAP.md](PROPOSAL_LLM_VERTICAL_ROADMAP.md) |
| **Next ~2 weeks — triage, P0/P1/P2, reproduction checklists** | [PLAN_IMMEDIATE_TWO_WEEKS.md](PLAN_IMMEDIATE_TWO_WEEKS.md) |
| **Quick wins (two sprints) — strict env, perception breaker, entry points, MalAbs alerts** | [PROPOSAL_QUICK_WINS_TWO_SPRINTS.md](PROPOSAL_QUICK_WINS_TWO_SPRINTS.md) |
| **Module count vs observable ethics (ablation gap, tiers A–E)** | [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](MODULE_IMPACT_AND_EMPIRICAL_GAP.md) |
| **Closing core weaknesses (async, naming, evidence, governance, LLM) — execution plan** | [PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md](PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md) |
| **Tiered sandbox + deterministic `by_tier`; stochastic Monte Carlo (`run_stochastic_sandbox.py`)** | [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md) |
| **Static weight sweeps (poles @ 0.5 center, mixture @ 1/3 simplex) — mass batch + CSV** | [PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md](PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md) |
| **Million-scale random weight + stratified scenarios — design + `run_mass_kernel_study`** | [PROPOSAL_MILLION_SIM_EXPERIMENT.md](PROPOSAL_MILLION_SIM_EXPERIMENT.md) · [`experiments/million_sim/README.md`](../experiments/million_sim/README.md) |
| **Mock DAO — no chain, QV assumptions, not policy core** | [MOCK_DAO_SIMULATION_LIMITS.md](MOCK_DAO_SIMULATION_LIMITS.md) |
| **DAO/blockchain/distributed justice staged execution** | [PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) |
| **Distributed justice — contribution guide (V11 + backlog)** | [PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md) |
| **Distributed justice — backlog IDs (DJ-BL-*)** | [PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md](PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) |
| **Distributed justice — contract matrix (`master-*` JSON)** | [PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md](PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md) |
| **Chat server — HTTP GET / JSON surface** | [PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md](PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) |
| **KERNEL_* typed public API (Pydantic, phased)** | [KERNEL_ENV_TYPED_PUBLIC_API.md](KERNEL_ENV_TYPED_PUBLIC_API.md) |
| Theory ↔ implementation map and tests | [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) |
| Runtime contract (English) | [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) |
| Snapshot and persistence | [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) |
| Runtime phases / migration | [RUNTIME_PHASES.md](RUNTIME_PHASES.md) — [RUNTIME_FASES.md](RUNTIME_FASES.md) is a one-line redirect to the same doc |
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
| [PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md](PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) | Staged execution from deterministic off-chain justice to optional blockchain anchoring — *English* |
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
| [PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md](PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md) | Mixture feedback + BMA stack (**ADR 0012**) — modules, env vars, tests |
| [ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md](ROADMAP_MINIMAL_EXECUTABLE_MODEL_30_DAY.md) | 30-day plan: compose, ethical telemetry, persistence migrations, operator manual — *English* |
| [RUNTIME_PROFILES_OPERATOR_TABLE.md](RUNTIME_PROFILES_OPERATOR_TABLE.md) | `ETHOS_RUNTIME_PROFILE` names, risks, LAN/semantic notes — *English* |
| [PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md](PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md) | Sync kernel vs async FastAPI — thread offload for turns, JSON, advisory — *English* |

---

## Governance, user model, and semantic layers

| Document | Topic |
|----------|--------|
| [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md) | MockDAO and L0 layer |
| [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) | User model enrichment (judicial, cognitive, risk) |
| [LIGHTHOUSE_KB.md](LIGHTHOUSE_KB.md) | Lighthouse knowledge base |
| [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md) | MALABS semantic layers |
| [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) | Cosine θ_block / θ_allow: evidence posture, guardrail tests, offline zone table — *English* |
| [PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md](PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) | Psi Sleep v2 (feedback + mixture), semantic gate as default perception — *English* |

---

## Perception, poles, time, and input trust

| Document | Topic |
|----------|--------|
| [PERCEPTION_VALIDATION.md](PERCEPTION_VALIDATION.md) | Perception validation (Pydantic, coherence) |
| [PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md](PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md) | Unified ``KERNEL_PERCEPTION_BACKEND_POLICY`` (template_local / fast_fail / session_banner) |
| [PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md](PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md) | Stable chat JSON perception diagnostics contract for operators and dashboards |
| [PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md](PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md) | ``KERNEL_VERBAL_LLM_BACKEND_POLICY`` for communicate/narrate failure + ``verbal_llm_observability`` |
| [PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) | ``KERNEL_LLM_TP_*`` precedence, verbal family key, monologue policies — operator + contributor reference |
| [PROPOSAL_LLM_INTEGRATION_TRACK.md](PROPOSAL_LLM_INTEGRATION_TRACK.md) | Cursor track: LLM wiring, adjacent layers, integration gaps (G-01…G-10) |
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
| [PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md](PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md) | Repository-wide critical assessment: maturity, over-claim risks, and stabilization priorities |
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
- **Bibliography:** [`BIBLIOGRAPHY.md` on `main-whit-landing`](https://github.com/CuevazaArt/ethical-android-mvp/blob/main-whit-landing/BIBLIOGRAPHY.md) (not shipped on lightweight `main`)  
- **Product and development:** [root README](../../README.md)
