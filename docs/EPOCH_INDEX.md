# Project Epoch Index — Ethos / Mos Ex Machina

> Navigation hub for the full development history organized by era.
> For the current operating state, read [`CONTEXT.md`](../CONTEXT.md) first.
> For the detailed block-by-block log, see [`CHANGELOG.md`](../CHANGELOG.md).
> For the narrative arc, see [`HISTORY.md`](../HISTORY.md).

---

## Epoch overview

| # | Era | Period | Tag / Branch | Architecture |
|---|-----|--------|-------------|--------------|
| 0 | **Pre-Alpha — Conceptual** | Q1 2026 | *(design docs only)* | 7-layer paper architecture |
| 1 | **V1 Series** | March – April 2026 | `v15-archive-full-vision` | `src/modules/` — tri-lobe monolith |
| 2 | **V2 Series** | April 2026 – present | `main` (active) | `src/core/` — minimal clean kernel |

---

## Epoch 0 — Pre-Alpha / Conceptual (Q1 2026)

**Summary:** The project existed only as design documentation. No runnable code. Core ideas established: ethics-by-architecture, Bayesian decision-making, narrative identity, DAO governance, and a 7-layer cognitive stack.

### Key documents
| Document | Description |
|----------|-------------|
| [`HISTORY.md § Pre-alpha Spanish corpus`](../HISTORY.md) | Digest of the founding `androide_etico_alpha_v1.0_2026.md` Spanish corpus |
| [`HISTORY.md § Intellectual foundations`](../HISTORY.md) | 14-discipline academic bibliography map |
| [`BIBLIOGRAPHY.md` on `main-whit-landing`](https://github.com/CuevazaArt/ethical-android-mvp/blob/main-whit-landing/BIBLIOGRAPHY.md) | Full 104+ reference academic bibliography |

### Defining concepts established
- **Ethics-by-architecture:** values encoded in structure, not post-hoc filters.
- **Seven functional layers:** physical shielding → perception → world model → deliberative ethics → action selection → adaptive learning → DAO oracle.
- **Narrative identity:** the android knows itself through story, not static config.
- **Distributed governance:** no single actor owns the android's values.

---

## Epoch 1 — V1 Series (March – April 2026)

**Summary:** The full Python implementation, from first runnable kernel to a complex distributed tri-lobe architecture with multi-team swarm development. Ended with the full archive tag `v15-archive-full-vision`. **This epoch is frozen — do not modify.**

### Git reference
```
git checkout v15-archive-full-vision   # Read-only frozen archive
```

### Architecture: `src/modules/` (V1 path)
All modules lived under `src/modules/`. The kernel grew from a simple batch runner to a WebSocket server, then to a distributed nervous system with the `CorpusCallosum` event bus.

### Version timeline

| Version | Date | Milestone |
|---------|------|-----------|
| **v1.0** | March 2026 | Conceptual phase — 40+ design docs, 7-layer math formalization |
| **v2.0** | March 2026 | First runnable kernel — `absolute_evil.py`, `buffer.py`, `weighted_ethics_scorer.py`, 9 simulations |
| **v3.0** | March 2026 | Integrated kernel — Uchi-Soto, Locus, Psi Sleep, Mock DAO, Variability; 38 tests |
| **v4.0** | March 2026 | LLM layer — `llm_layer.py`; Ollama local or heuristic fallback |
| **v5.0** | March 2026 | Humanization — weakness pole, forgiveness, immortality, augenesis; 51 tests |
| **v6.0** | April 2026 | Runtime MVP — WebSocket chat (`chat_server.py`), snapshot persistence, checkpoints |
| **v7.0** | April 2026 | Relational advisory layer — `user_model.py`, theory-of-mind hints |
| **v8.0** | April 2026 | Situated organism — sensor contract, vitality, cross-modal trust |
| **v9.0** | April 2026 | Epistemic/generative extensions — `epistemic_dissonance.py`, `generative_candidates.py` |
| **v10.0** | April 2026 | Operational strategy hooks — gray-zone diplomacy, skill registry, somatic markers |
| **v11.0** | April 2026 | Distributed Justice Phase 1 — `judicial_escalation.py`, DAO audit dossier |
| **v12.0** | April 2026 | Moral Infrastructure Hub — `moral_hub.py`, DemocraticBuffer, EthosPayroll, snapshot v2/v3 |
| **v13.0** | April 2026 | Distributed Nervous System — monolith guillotine, 5 async lobes, `CorpusCallosum` event bus |
| **v13.1** | April 2026 | Nomadic Autonomy — `MotivationEngine`, proactive intents, voice synthesis, BGR→RGB fix |

### Key V1 archived docs
| Document | Path |
|----------|------|
| V1 CHANGELOG archive (Phases 1-7) | [`docs/archive_v1-7/CHANGELOG_ARCHIVE_PHASE1-7.md`](archive_v1-7/CHANGELOG_ARCHIVE_PHASE1-7.md) |
| V1 Operational plan | [`docs/archive_v1-7/ETHOS_2_PLAN_OPERATIVO.md`](archive_v1-7/ETHOS_2_PLAN_OPERATIVO.md) |
| V1 Architecture — Tri-Lobe Core | [`docs/architecture/TRI_LOBE_CORE.md`](architecture/TRI_LOBE_CORE.md) |
| V1 Architecture — Ethical Model Mechanics | [`docs/architecture/ETHICAL_MODEL_MECHANICS.md`](architecture/ETHICAL_MODEL_MECHANICS.md) |
| V1 Proposals (archived) | [`docs/proposals/archived/`](proposals/archived/) |
| V1 Archive proposals | [`docs/archive_v1-7/proposals/`](archive_v1-7/proposals/) |
| V1 ADR history | [`docs/adr/`](adr/) (ADRs 0001–0018) |
| V1 Swarm orchestration | [`docs/SWARM_AUDIT_ORDER.md`](SWARM_AUDIT_ORDER.md), [`docs/SWARM_MESH_CYCLE_01.md`](SWARM_MESH_CYCLE_01.md) |
| Executive summary (V1 vision) | [`docs/proposals/WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md`](proposals/WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md) |

### V1 multi-team swarm structure
V1 was developed by a parallel multi-agent swarm:
- **L0 (Juan):** Merge authority. Only person who can merge to `main`.
- **L1 (Antigravity):** Integration hub. `master-antigravity` branch.
- **L2 Teams:** Cursor, Claude, Copilot — independent feature branches.

This structure is documented in [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](collaboration/MULTI_OFFICE_GIT_WORKFLOW.md).

### V1 redirect trigger (why V2 was born)
By V13–V15, the codebase had accumulated significant complexity: a 3,200+ line `chat_server.py` monolith, distributed lobes over an event bus, dozens of auxiliary modules, and multi-team merge debt. V2 was born as a **clean architectural restart** to deliver a minimal, fast, auditable kernel without the accumulated scaffolding.

> **FROZEN.** The V1 archive is preserved at tag `v15-archive-full-vision`. Do not modify.

---

## Epoch 2 — V2 Series (April 2026 – present)

**Summary:** Complete re-architecture. All logic moved to `src/core/` — a lean, direct, highly-testable kernel. No event bus, no lobes, no distributed scaffolding. The `ChatEngine` in `src/core/chat.py` orchestrates the entire pipeline sequentially. Tests jumped from sporadic to 203 systematic tests. This is the **active epoch**.

### Architecture: `src/core/` (V2 path)
```
src/core/
  chat.py          ChatEngine — master pipeline orchestrator
  ethics.py        CBR ethics engine (36 precedents)
  safety.py        MalAbs absolute evil gate
  memory.py        Hybrid semantic + TF-IDF memory
  perception.py    Deterministic perception (<1ms, no LLM)
  identity.py      Narrative journal + archetype
  llm.py           LLM adapter (Ollama / heuristic fallback)
  precedents.py    CBR case library
  sleep.py         PsiSleepDaemon (REM consolidation)
  plugins.py       Extensible plugin system
  vault.py         Encrypted secret management
  roster.py        Known-person context
  user_model.py    Behavioral profile tracker
  tts.py / stt.py  Voice I/O
  vision.py        Vision triggers
  status.py        System health telemetry
```

### Block timeline

| Block | Name | Status |
|-------|------|--------|
| **V2.22** | Consolidated Core Minimal | ✅ Closed |
| **V2.25** | Fase 16 Complete — zero legacy imports | ✅ Closed |
| **V2.40** | Perception Classifier (no LLM, 0ms) | ✅ Closed |
| **V2.41** | Case-Based Ethics (CBR Precedents) | ✅ Closed |
| **V2.42** | Single-Call Pipeline (Hardening) | ✅ Closed |
| **V2.43** | Sentence Embeddings (Semantic Memory) | ✅ Closed |
| **V2.44** | Narrative Identity (LLM Journal) | ✅ Closed |
| **V2.45** | Nomad PWA Ethics HUD (Metadata stream) | ✅ Closed |
| **V2.46** | Precedents Expansion (36 rich cases) | ✅ Closed |
| **V2.47** | GPU Docker Orchestration (NVIDIA + Ollama) | ✅ Closed |
| **V2.48** | LLM Native Multi-turn & Crash Fixes | ✅ Closed |
| **V2.49** | Neural TTS (`edge-tts`) | ✅ Closed |
| **V2.50** | Sensory Expansion — Autonomous vision triggers | ✅ Closed |
| **V2.51** | Thalamic Gate — Wake word protection | ✅ Closed |
| **V2.52** | Limbic System — Emotional TTS and Visual Resonance | ✅ Closed |
| **V2.53** | Acoustic Echo Shield | ✅ Closed |
| **V2.54** | Cognitive Proprioception — STT semantic echo cancellation | ✅ Closed |
| **V2.55** | Temporal Multimodal Fusion | ✅ Closed |
| **V2.56** | Status Telemetry Hardening | ✅ Closed |
| **V2.57** | SensoryBuffer WebSocket Integration | ✅ Closed |
| **V2.58** | Speech-Triggered Immediate Fusion | ✅ Closed |
| **V2.59** | Sensory-Context Perception — Multimodal patterns | ✅ Closed |
| **V2.60** | Audio Feedback Suppression (field-tested) | ✅ Field-tested |
| **V2.61–V2.64** | Mente y Memoria — Narrative Archetype + UserModelTracker | ✅ Closed |
| **V2.65** | LLM Reasoning Suppression (`<think>` state machine) | ✅ Closed |
| **V2.66** | CBR Injection (Legal Doctrine) | ✅ Closed |
| **V2.70** | Secure Vault (Isolation Boundary) | ✅ `v2.70-secure-vault` |
| **V2.71** | Vault Authorization Pipeline | ✅ Closed |
| **V2.72** | External Plugins Architecture | ✅ Closed |
| **V2.73** | Web Search Plugin + Weather | ✅ Closed |
| **V2.74** | Plugin STM Continuity + Telemetry | ✅ Closed |
| **V2.75** | Narrative Roster & Memory Enrichment | ✅ Closed |
| **V2.76** | Psi-Sleep Cognitive Consolidation | ✅ Closed |
| **V2.77** | Native Android Scaffolding (PWA archived) | ✅ Closed |
| **V2.78** | Native Android Core Setup (Gradle/Compose) | ✅ Closed |
| **V2.79** | Parasite SDK & Mesh Discovery | 🔄 **Active** |

### Current state docs (V2)
| Document | Description |
|----------|-------------|
| [`CONTEXT.md`](../CONTEXT.md) | **START HERE** — current state, active blocks, key files |
| [`README.md`](../README.md) | Quick-start, features, architecture summary |
| [`CHANGELOG.md`](../CHANGELOG.md) | Full block-by-block history (V2 era at top) |
| [`LICENSING_STRATEGY.md`](../LICENSING_STRATEGY.md) | Dual-license model (Apache 2.0 + BSL 1.1) |
| [`docs/LICENSING_OVERVIEW.md`](LICENSING_OVERVIEW.md) | Wiki-friendly license map |
| [`docs/ROADMAP_PRACTICAL_PHASES.md`](ROADMAP_PRACTICAL_PHASES.md) | Engineering roadmap (Phases 0–3) |
| [`docs/TRANSPARENCY_AND_LIMITS.md`](TRANSPARENCY_AND_LIMITS.md) | Honest capability limits |
| [`docs/GOVERNANCE_DATA_POLICY.md`](GOVERNANCE_DATA_POLICY.md) | Data governance for operators |
| [`docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md`](AUDIT_TRAIL_AND_REPRODUCIBILITY.md) | Audit chain documentation |
| [`docs/ENV_VAR_CATALOG.md`](ENV_VAR_CATALOG.md) | All `KERNEL_*` env vars |
| [`docs/IDE_ANDROID_STUDIO_HANDOFF.md`](IDE_ANDROID_STUDIO_HANDOFF.md) | Android Studio setup (V2.77+) |
| [`docs/SWARM_FLASH_PROMPTS.md`](SWARM_FLASH_PROMPTS.md) | Current swarm prompt templates |
| [`docs/proposals/STRATEGY_AND_ROADMAP.md`](proposals/STRATEGY_AND_ROADMAP.md) | Product + operations roadmap |
| [`docs/proposals/OPERATOR_QUICK_REF.md`](proposals/OPERATOR_QUICK_REF.md) | Operator quick reference |
| [`docs/proposals/THEORY_AND_IMPLEMENTATION.md`](proposals/THEORY_AND_IMPLEMENTATION.md) | Theory ↔ code map |
| [`docs/proposals/SWARM_P2P_THREAT_MODEL.md`](proposals/SWARM_P2P_THREAT_MODEL.md) | P2P mesh threat model (V2.79) |

### V2 design principles (vs V1)
| Principle | V1 | V2 |
|-----------|----|----|
| Module location | `src/modules/` | `src/core/` |
| Orchestration | Event bus (`CorpusCallosum`) + async lobes | Direct sequential pipeline (`ChatEngine`) |
| Complexity | ~3,200 line `chat_server.py` monolith | ~350 line app factory |
| Test count | Sporadic (varied by team) | 203 systematic tests |
| LLM dependency for ethics | Partial (LLM in some perception paths) | Zero (perception is fully deterministic) |
| Android client | PWA (archived) | Native Kotlin / Jetpack Compose |

---

## Navigation quick-reference

| I want to… | Go to |
|------------|-------|
| Understand what the project does today | [`README.md`](../README.md) |
| See the current active blocks | [`CONTEXT.md`](../CONTEXT.md) |
| Read the full version history | [`HISTORY.md`](../HISTORY.md) |
| Find a specific code change | [`CHANGELOG.md`](../CHANGELOG.md) |
| Contribute code | [`CONTRIBUTING.md`](../CONTRIBUTING.md) |
| Understand the license | [`LICENSING_STRATEGY.md`](../LICENSING_STRATEGY.md) |
| Browse V1 archived docs | [`docs/archive_v1-7/`](archive_v1-7/) |
| Understand security posture | [`SECURITY.md`](../SECURITY.md) |
| See operator env vars | [`docs/ENV_VAR_CATALOG.md`](ENV_VAR_CATALOG.md) |
| Set up Android Studio (V2) | [`docs/IDE_ANDROID_STUDIO_HANDOFF.md`](IDE_ANDROID_STUDIO_HANDOFF.md) |
| Run the kernel locally | `python -m src.chat_server` → `http://localhost:8000` |
| Run the test suite | `pytest tests/core/ -q` |

---

*Ethos Kernel — Ex Machina Foundation — 2026*
