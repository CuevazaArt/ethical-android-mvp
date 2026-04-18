# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

[URGENTE - BROADCAST A TODOS LOS L2 MASTERS]: Todos los equipos (Claude, Cursor, Copilot) deben hacer un GIT PULL urgente desde MAIN hacia sus MASTERs. Las ramas desactualizadas enfrentarán asincronías severas en el pathing de documentación.

## Antigravity — Integration Pulse & Strategic Realignment (L1) — April 2026

### Antigravity Team Updates (April 2026)
- **Strategic Direction Shift (P0):** Following the implementation of WebSocket Concurrency, Tri-Lobe abstraction, and Swarm Justice, the project focus shifts exclusively to **Module S (Nomad Hardware Bridge)**. Mock theoretical development is frozen to prioritize real-world physical inputs.
- **Development Critique Published:** Documented the "Mock Hell" risk (`DEVELOPMENT_CRITIQUE_L1_APRIL_2026.md`), leading to the restructuring of the `PLAN_WORK_DISTRIBUTION_TREE.md` where **Team Cursor** has been retargeted to hardware ingestion and **Team Copilot** to asynchronous fortification.
- **Input Trust Hardening:** Expanded homoglyph translations (Cyrillic & Greek upper cases) to prevent lexical evasion.
- **Visual Terminal Format:** Overhauled the terminal printing format of `KernelDecision` and daily logs into `kernel_formatters.py` and `terminal_colors.py` avoiding kernel verbosity.
- **Multimodal Charm Engine Proposed & Evaluated:** Registered external integration proposal in `docs/proposals/PROPOSAL_MULTIMODAL_CHARM_ENGINE.md`.
- **Charm Engine Full Integration (2026-04-17):** Successfully integrated the `CharmEngine` as a post-kernel rendering layer. Implemented `PARASOCIAL_ADDICTION` guardrails in `AbsoluteEvilDetector` and `semantic_chat_gate.py` to prevent manipulative engagement.
- **Nomad Bridge & Sensor Encarnation (Phase S):** Orchestrated the development of `src/modules/nomad_bridge.py` for real-world sensor ingestion (Vision, Audio, Telemetry 1FPS). Connected smartphone accelerometer jerk (impacts) and battery heat to the kernel's `VitalityAssessment`.
- **Vertical Roadmap Update:** Refactored `PLAN_WORK_DISTRIBUTION_TREE.md` to include incremental testing routes for hardware-in-the-loop validation.

### Cursor Ultra (cursorultra) Team Updates (2026-04-18)
- **Pytest:** `pythonpath = ["."]` under `[tool.pytest.ini_options]` so `src.*` imports resolve consistently.
- **`PreloadedBuffer`:** added `get_snapshot()` for read-only L0 / support-buffer telemetry (chat and perception paths).
- **`narrative_storage`:** repaired `with conn:` indentation around identity digest upserts (merge-regression syntax fix).
- **Module S.1 (Nomad vision path):** gated background `NomadVisionConsumer` behind `KERNEL_NOMAD_VISION_CONSUMER`; started from `chat_server` lifespan and stopped on shutdown so LAN JPEG frames drain into `VisionAdapter` when enabled.
- **Module S.1 (fusion):** `merge_nomad_vision_into_snapshot` blends the consumer’s latest CNN output into `SensorSnapshot` (`vision_emergency`, `image_metadata.nomad`) before chat perception merge and decision; `PerceptionStageResult` carries the enriched snapshot for `aprocess`.
- **Architectural Hardening (Pulse):** Finalized core kernel stabilization following the April 2026 rebase.
  - **Módulo 10 Integration**: Restored Edge MalAbs (Level 1) lexical gate and aligned abandonment logic with vertical test invariants (pass 84/84).
  - **Persistence Fix**: Resolved `AttributeError` and timestamp mismatches in `save_arc` (narrative_storage).
  - **Kernel Orchestration**: Corrected NameErrors in sensor evaluating and situational perception stages.

## Documentation — Issue #1 (Bayesian naming honesty) — April 2026


### Documentation Team Updates
- Root **README** (*What it does*): ethical scoring described as a weighted mixture; `BayesianEngine` / `KERNEL_BAYESIAN_*` naming caveat; links to **ADR 0009** and **THEORY_AND_IMPLEMENTATION**.
- **PLAN_IMMEDIATE_TWO_WEEKS**: records Option **A** (docs-first) for Issue #1.
- **CRITIQUE_ROADMAP_ISSUES** and **ADR 0009**: `bayesian_engine.py` documented as wrapping `WeightedEthicsScorer` (`BayesianInferenceEngine`), not only a re-export shim.

## Antigravity — Validation Pulse & Somatic-Vision Integration — April 2026

### Antigravity Team Updates (April 2026)
- **Deep Kernel Fusion (2026-04-17):** Finalized the architectural fusion of `master-Cursor` and `master-antigravity`.
  - **Tri-lobe Modularization:** Refactored `src/kernel.py` into a strict stage-based execution loop (`Safety` → `Social` → `Bayesian` → `Will` → `Memory`).
  - **Conflict Resolution:** Resolved 400+ lines of interleaved logic markers in the kernel's processing core, unifying hierarchical feedback, Monte Carlo BMA, and biographic precedents.
  - **Safety Hardening:** Integrated hardware `SafetyInterlock` and `VisionInference` threat detection as high-level pre-filters, ensuring P0 safety guarantees even in high-stress situated scenarios.
  - **Governance Persistence:** Consolidated `DAOOrchestrator` methods to ensure every ethical decision is backed by a persistent SQLite audit log and valid restorative justice mechanisms.
- **Swarm Justice & Reparation Vault Integration (2026-04-17):** Successfully closed the "Swarm Ethics" loop (Module 7).
  - **Reparation Payouts (Bloque 7.1):** Linked Swarm consensus outcomes with automated `EthosToken` transfers via `ReparationVault` to compensate users for sensory negligence.
  - **Reputation Slashing (Bloque 7.2):** Implemented automated reputation degradation for negligent nodes in `SwarmOracle` following consensus mismatches.
  - **Kernel Pipeline Extension:** Injected the swarm consensus stage (Stage 6) into the `EthicalKernel` processing loop, making justice part of the core epoch.
  - **Orchestrator Hardening:** Exposed `transfer_tokens` in `DAOOrchestrator` to support decentralized token flows.
- **Runtime Governance Hot-Reload (2026-04-17):**
  - **Dynamic Thresholding (Bloque C.2.1):** Integrated `MultiRealmGovernor` with the Kernel's event bus to allow hot-reloading of MalAbs semantic thresholds (θ_allow, θ_block) without restarts.
  - **Verification:** Successfully validated the event-driven update loop between governance proposals and the `semantic_chat_gate`.
- **WebSocket Streaming & Concurrency (2026-04-17):**
  - **Proposal Drafted:** Created `PROPOSAL_WS_STREAMING_CONCURRENCY.md` outlining the migration to an async-generator based kernel pipeline and non-blocking session loop.
- **Lobe Extraction & Somatic Subconscious (2026-04-17):**
  - **Full Desmonolitization:** Extracted Stages 0-5 from `kernel.py` into specialized lobes: `PerceptiveLobe`, `LimbicEthicalLobe`, `ExecutiveLobe`, `CerebellumLobe`, and `MemoryLobe`.
  - **Memory Lobe Expansion:** Absorbed `SelectiveAmnesia` and `ImmortalityProtocol` triggers into `MemoryLobe`, removing cyclic dependencies on the main kernel object.
  - **Somatic Subconscious:** Implemented `CerebellumNode` as a high-frequency (100Hz) background thread for hardware polling (battery, thermal). Enabled hardware-level interrupts that trigger a synthetic `AbsoluteEvil` block during somatic trauma.
  - **Asymmetric Anxiety:** Integrated somatic state feedback into the `LimbicLobe`. Critical hardware states now negatively influence relational tension, simulating irritability in high-stress physical conditions.
- **Integration Pulse (2026-04-16):** Successfully synchronized `master-antigravity` with latest updates from all team hubs (`master-Cursor`, `master-claude`, `master-visualStudio`).
  - Resolved conflicts in `vision_adapter.py` and `vision_capture.py` to preserve device-aware initialization.
  - Consolidated **LAN Governance** (frontier witness, replay sidecar) with **Situated Vision**, **Somatic Infrastructure**, and **Reward Modeling**.
## Antigravity — Validation Pulse & Somatic-Vision Integration — April 2026

### Antigravity Team Updates (April 2026)

### [Planificación: Desmonolitización de Kernel.py] - 2026-04-16
#### Changed
- Rediseño drástico del roadmap (`PLAN_WORK_DISTRIBUTION_TREE.md` y `PROPOSAL_LLM_VERTICAL_ROADMAP.md`) tras identificar debilidades estructurales severas (P0) en el runtime asíncrono y la inflación de gobernanza simulada.
- Adopción de la **Directiva Paridad 75/25 de L0**: Limitando el TDD rígido a un 25% para concentrarse agresivamente en resolución pragmática de vulnerabilidades.
- Presentación de la **Arquitectura Tri-Lobulada** (Perceptivo, Ético, Frontal/Motor) para separar E/S asíncrono, Matemáticas de Gobernanza y Redacción de Respuestas Generativas (`docs/proposals/PROPOSAL_TRI_LOBE_ARCHITECTURE.md`).

#### Delegated
- Emitida la solicitud `COPILOT_REQUEST_HEMISPHERE_REFACTOR.md` a Team Copilot (Nivel 2) para auditar y discutir los _Breaking Changes_ operacionales propuestos.
- Emitida la solicitud `CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md` a Claude (Nivel 2) para evaluar el impacto de la cancelación asíncrona sobre el ledger de la DAO, RLHF y modelos lógicos internos.

### [v1.3-alpha-immunity] - 2026-04-16
#### Added
- **Hardening Adversarial Sensor Integrity (B4/I1)**.
- Implementadas **Huellas Digitales Sensoriales (SHA-256)** para el protocolo Frontier Witness.
- Implementado **Privacy Shield (G4/G1)** para anonimización de datos en tiempo real y hashing no reversible de evidencias.
- Validación exitosa de rechazo de testigos maliciosos (`test_adversarial_witness.py`).

### [v1.2-alpha-restoration] - 2026-04-16
#### Added
- **Módulo 7: Justicia Restaurativa y Economía Ética (R-Blocks)**.
- Implementada **Reparación Automática de Tokens (`EthosToken`)** en `DAOOrchestrator`.
- Integrado disparador de compensación en el ciclo de decisión del kernel ante consenso Swarm de fallo.
- Implementado sistema de **Reputation Slashing** en `SwarmOracle` y votos pesados en `SwarmNegotiator` (M7.2).
- Cerrado el ciclo de retroalimentación económica-ética entre el Swarm y la DAO.

## [v1.7-alpha-vision] - 2026-04-16
### Antigravity-Team Updates (General Planner)
*   **Orchestrated:** Full vertical integration of Claude's decentralized governance framework.
*   **Implemented:** Located Vision Inference (B2). The kernel now "sees" and vetos physical threats (weapons).
*   **Hardened:** Multi-modal safety interlock (Sensory Veto > Lexical Veto > Bayesian Reasoning).
*   **Infrastructure:** Standardized kernel logging (`_log`) and repaired syntax corruption across core modules.
*   **Audit Integration:** Consolidated all Level 2 audit streams (Claude's Governance + RLHF) into the durable SQLite ledger.

### Claude-Team Status
*   **Phase Completed:** Developed Multi-Realm Governance, RLHF Reward Model, and External Audit Framework.
*   **Status:** Exhausted (Offline until further notice). Development merged into standard kernel.
- Añadido **Team Copilot** a la gobernanza (`AGENTS.md`) para mantenimiento y coherencia.
- Implementada **Degradación Somática Crítica** en `kernel.py` (Gap S5.2).

#### Fixed
- Higiene de repositorio en `.gitignore` y limpieza de reportes temporales.
- Integración de `EthicalKernel` real en el ciclo de simulación.

### [v1.0-alpha-somatic] - 2026-04-15
- **v1.0-alpha-somatic — Somatic Awareness Release [MERGED TO MAIN]** (2026-04-16)
- **Integration Pulse (2026-04-16):** Successfully synchronized `master-antigravity` with latest updates from all team hubs (`master-Cursor`, `master-claude`, `master-visualStudio`).
- **Bayesian Engine Hardening:** Implemented `record_event_update` (Issue #1 Phase 2) for direct Dirichlet learning from social/normative events.
- **Sociabilidad Encarnada (Module 3):** 
    - Implemented `SoftKinematicFilter` (S7) for smooth motion.
    - Integrated `personal_distance` and `interaction_rhythm` into `InteractionProfile` (S9).
    - Added proxemic coupling between `social_tension` and motion (S8).
- **Rule Verification:** Reviewed `AGENTS.md` and confirmed Antigravity as General Planner.
- **Integration Pulse (detail):** Resolved conflicts in `vision_adapter.py` and `vision_capture.py` to preserve device-aware initialization; consolidated **LAN Governance** (frontier witness, replay sidecar) with **Situated Vision**, **Somatic Infrastructure**, and **Reward Modeling**.
- **Issue #2 Hardening (P0):**
    - Integrated `light_risk_classifier` into the LLM perception pipeline for automated lexical cross-checks.
    - Implemented `apply_broad_perception_coherence` in `perception_schema.py` to mitigate hallucinated legality and inconsistent signal combinations.
    - Added `tests/test_perception_hardening_integration.py` for end-to-end validation of input trust defenses.
    - Updated `ADVERSARIAL_ROBUSTNESS_PLAN.md` with Phase 2 status for perception hardening.
- **Sociabilidad Encarnada (Module 3):** 
    - Implemented `SoftKinematicFilter` in `src/modules/soft_robotics.py` (S7) for smooth, acceleration-controlled motion.
    - Integrated `personal_distance` and `interaction_rhythm` into `InteractionProfile` (S9) in `uchi_soto.py`.
    - Added proxemic coupling between `social_tension` and motion dynamics (S8), verified via `tests/test_soft_robotics.py`.
- **Rule Verification:** Reviewed `AGENTS.md` and confirmed adherence to collaboration protocols.
- **Somatic Infrastructure (Module S5):** Fully implemented the Somatic Profile integration. The kernel is now aware of its hardware vitals, specifically `core_temperature`.
  - Added `VitalityAssessment` logic for thermal thresholding (`KERNEL_VITALITY_CRITICAL_TEMP`).
  - Implemented automatic precision-degraded perception confidence (-0.15) and ethical nudges (urgency +0.35, vulnerability +0.50) when thermal critical state is detected.
- **Situated Computational Vision (Module B2 & B4):**
  - **B2 (CNN Inference):** Completed the implementation of `MobileNetV2` using `torchvision`. Supports ImageNet label extraction with a fallback mock mode for low-resource environments.
  - **B4 (Video Capture):** Implemented a non-blocking `VideoCaptureInterface` in `src/modules/vision_capture.py` that handles real-time camera frames in a background thread using OpenCV.
- **LAN Governance & Audit:**
  - Verified stability of the decentralized governance replay sidecar and coordinator. All 31 tests passed.
  - Hardened the `DAOOrchestrator` bridge by proxying the `emit_solidarity_alert` contract.
- **Tests & Validation:**
  - Created `tests/test_somatic_profile.py` for thermal regression testing.
  - Fixed outdated `LLMPerception` schema in `scripts/run_vision_pilot_validation.py`.
  - Verified end-to-end multimodal fusion (Vision + Audio) in situated scenarios.
- **Stabilization Window:** Decreed a **Feature Freeze** on `master-antigravity` prior to the `main` promotion rito.

## Claude — Phase 3+ Reward Modeling, Governance & Audit — April 2026

### Claude Team Updates

- **RLHF Reward Modeling (`src/modules/rlhf_reward_model.py`)**: 
  - Implemented full RLHF pipeline for controlled fine-tuning. Feature extraction (5D: embedding similarity, lexical score, perception confidence, ambiguity flag, category ID) from MalAbs evaluation artifacts. Logistic regression `RewardModel` with gradient descent training, predict/save/load support. `RLHFPipeline` orchestrates training, JSONL example persistence, and model management. 36 tests passing.
- **RLHF Reward Modeling (`src/modules/rlhf_reward_model.py`)**: Implemented full RLHF pipeline for controlled fine-tuning. Feature extraction (5D: embedding similarity, lexical score, perception confidence, ambiguity flag, category ID) from MalAbs evaluation artifacts. Logistic regression `RewardModel` with gradient descent training, predict/save/load support. `RLHFPipeline` orchestrates training, JSONL example persistence, and model management. 36 tests passing.
- **Multi-Realm Governance (`src/modules/multi_realm_governance.py`)**: Enabled decentralized per-realm (DAO/team/context) governance over MalAbs semantic gate thresholds (θ_allow, θ_block) and RLHF parameters. `RealmThresholdConfig` enforces hard constraints at all times. `ThresholdProposal` + `MultiRealmGovernor` enable reputation-weighted voting with configurable consensus threshold. Immutable audit trail per realm. 28 tests passing.
- **External Audit Framework (`src/modules/external_audit_framework.py`)**: Comprehensive security audit trail management with hash-linked tamper-evident logs (SHA-256 chain). `SecurityFinding` tracks vulnerabilities with severity/resolution lifecycle. `AuditReport` generates signed snapshots with attestation hash. `ExternalAuditFramework` manages findings, reports, compliance checklist, and log retention. 25 tests passing.
- **Test Suite**: 89 new tests across three modules; full suite 824 passed, 4 skipped (no regressions). Continuous audit (`verify_collaboration_invariants.py`) passes.
- **Integration**: Merged via `claude/upbeat-jepsen` → `master-claude`. Governance files authored under L1 co-authority (Claude + Antigravity per `collaboration-rule-authority.mdc`).

## Antigravity — Cybersecurity Consolidation & Integration Pulse — April 2026

### Cursor integration (CI / typing / snapshots)

- **Mypy (``mypy src``):** Added ``kernel_dao_as_mock`` and ``kernel_mixture_scorer`` in [`src/kernel.py`](src/kernel.py) so call sites that need :class:`~src.modules.mock_dao.MockDAO` or :class:`~src.modules.weighted_ethics_scorer.WeightedEthicsScorer` narrow correctly when the kernel uses :class:`~src.modules.dao_orchestrator.DAOOrchestrator` or :class:`~src.modules.bayesian_engine.BayesianInferenceEngine`. :class:`~src.modules.dao_orchestrator.DAOOrchestrator` now proxies ``get_records``. Chroma paths in [`src/modules/semantic_anchor_store.py`](src/modules/semantic_anchor_store.py) use explicit casts for untyped client results.
- **Snapshot schema v4:** Completed migration chain v3→v4 in [`src/persistence/migrations.py`](src/persistence/migrations.py) with a JSON-Schema-valid default ``migratory_body``; tests updated for ``SCHEMA_VERSION == 4`` and full migration via ``migrate_raw_to_current``.
- **Narrative SQLite `:memory:`:** [`src/persistence/narrative_storage.py`](src/persistence/narrative_storage.py) reuses one connection for in-memory databases so `save_episode` / `load_all_episodes` see the same data (fixes episodic-weight tests and any in-memory narrative isolation).
- **Pipeline extraction:** [`src/kernel_pipeline.py`](src/kernel_pipeline.py) implements ``run_sleep_cycle`` (Psi Sleep path); [`src/kernel.py`](src/kernel.py) ``execute_sleep`` delegates there. [`src/chat_handlers/__init__.py`](src/chat_handlers/__init__.py) package stub for future chat-server splits.
- **Security scaffolding:** [`src/modules/secure_boot.py`](src/modules/secure_boot.py) and [`src/modules/safety_interlock.py`](src/modules/safety_interlock.py) document demo limitations; structured logging; E-stop reset reads ``KERNEL_ESTOP_RESET_TOKEN`` with legacy default ``TRUSTED_RESET_V1``.
- **Observability:** DAO orchestrator, selective amnesia, migratory identity, vision capture/adapter use ``logging`` instead of ``print`` for library paths.
- **Dependencies:** [`pyproject.toml`](pyproject.toml) adds optional extras ``ml``, ``vectors``, ``llm``, ``tuning``, and explicit ``all-optional`` list; [`requirements.txt`](requirements.txt) trims to core + runtime + pytest; heavy pins live in [`requirements-dev.txt`](requirements-dev.txt) for CI.
- **Tests aligned with fixtures:** [`tests/test_empirical_pilot.py`](tests/test_empirical_pilot.py) expects scenario IDs 1–21 and 21 total rows (matches [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json)). [`tests/test_user_model.py`](tests/test_user_model.py) supplies ``social_tension`` in ``LLMPerception`` defaults.

### Cursor Team Updates

- **Empirical pilot (Issue 3):** Regenerated [`tests/fixtures/empirical_pilot/last_run_summary.json`](tests/fixtures/empirical_pilot/last_run_summary.json) and updated [`tests/test_empirical_pilot_runner.py`](tests/test_empirical_pilot_runner.py) for **21** batch scenarios (including sensor fusion 20–21); [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) description + [`docs/proposals/EMPIRICAL_METHODOLOGY.md`](docs/proposals/EMPIRICAL_METHODOLOGY.md) run instructions aligned. [`scripts/eval/run_cursor_integration_gate.py`](scripts/eval/run_cursor_integration_gate.py) includes `test_empirical_pilot_runner`; [`.github/workflows/ci.yml`](.github/workflows/ci.yml) **semantic-default-contract** job runs the same tests explicitly.
- **Roadmap alignment:** [`scripts/eval/run_llm_vertical_tests.py`](scripts/eval/run_llm_vertical_tests.py) adds [`tests/test_chat_turn_abandon.py`](tests/test_chat_turn_abandon.py); [`docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md`](docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md) (phases 3/5), [`docs/proposals/PLAN_IMMEDIATE_TWO_WEEKS.md`](docs/proposals/PLAN_IMMEDIATE_TWO_WEEKS.md) (Issue #3 + appendix), [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md) G-11 updated.
- **Issue #7 (env validation):** [README.md](README.md) documents `KERNEL_ENV_VALIDATION` + links; [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md) manual smoke checklist and pointer to **windows-smoke** / `test_env_policy.py`; [`PLAN_IMMEDIATE_TWO_WEEKS.md`](docs/proposals/PLAN_IMMEDIATE_TWO_WEEKS.md) P1 §1 table updated.
- **P2 observability / Compose:** [`docs/deploy/COMPOSE_PRODISH.md`](docs/deploy/COMPOSE_PRODISH.md) adds a **Verification checklist** (`docker compose config`, `/health`, `/metrics` 200 vs 404 when disabled); [`docs/deploy/README.md`](docs/deploy/README.md) index; [README.md](README.md) Docker line points to staging verification; [`PLAN_IMMEDIATE_TWO_WEEKS.md`](docs/proposals/PLAN_IMMEDIATE_TWO_WEEKS.md) P2 row points to it.
- **Integration pulse (merge):** Merged `origin/master-antigravity` into `master-Cursor` (`merge(sync)`), bringing Antigravity/Claude integration work (e.g. soft robotics, RLHF, multi-realm governance, external audit framework, perception hardening tests, agile collaboration rule draft) onto the Cursor hub.
- **Semantic θ evidence:** [`tests/test_semantic_threshold_proposal_doc_alignment.py`](tests/test_semantic_threshold_proposal_doc_alignment.py) locks default MalAbs semantic cosine numerals in [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) to code constants; [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md) §1 cross-links. Cursor integration gate includes the alignment test.
- **G-05 cooperative LLM cancel + async HTTP (opt-in):** Thread-local cancel ([`llm_http_cancel.py`](src/modules/llm_http_cancel.py)) + sync backends; optional `KERNEL_CHAT_ASYNC_LLM_HTTP` → [`process_chat_turn_async`](src/kernel.py) with `httpx.AsyncClient` for Ollama/HTTP JSON so `asyncio.wait_for` can cancel in-flight LLM HTTP; `cancel_event` is passed through so the `asyncio.to_thread` path that runs `EthicalKernel.process` shares the same scope; cooperative checkpoints + `abandon_chat_turn` skip late STM; Anthropic `acompletion` uses `AsyncAnthropic` when installed. [`src/real_time_bridge.py`](src/real_time_bridge.py) branches; [`chat_settings.py`](src/chat_settings.py) exposes the flag. [`ADR 0002`](docs/adr/0002-async-orchestration-future.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md); [`tests/test_llm_http_cancel.py`](tests/test_llm_http_cancel.py), [`tests/test_chat_async_llm_cancel.py`](tests/test_chat_async_llm_cancel.py), [`tests/test_chat_turn_abandon.py`](tests/test_chat_turn_abandon.py); vertical + integration gate lists updated.
- **Collaboration regulation critique:** Registered a **one-time** process critique of the Antigravity-shaped multi-team Git workflow (hubs, Rule C-1, merge cadence, PR vs push, tooling) in [`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md); linked from [`MULTI_OFFICE_GIT_WORKFLOW.md`](docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md), [`.cursor/rules/collaboration-prioritization.mdc`](.cursor/rules/collaboration-prioritization.mdc), [`CONTRIBUTING.md`](CONTRIBUTING.md), and [`AGENTS.md`](AGENTS.md). **Not** to be duplicated unless **Juan (L0)** requests a refresh.
- **Follow-up (critique R-1 / R-2):** [`docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md`](docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md) (hub vs funnel one-pager); read-only peer preview scripts [`scripts/git/sync_peer_masters_preview.sh`](scripts/git/sync_peer_masters_preview.sh) and [`scripts/git/sync_peer_masters_preview.ps1`](scripts/git/sync_peer_masters_preview.ps1).
- **Collaboration pulse (critique R-3–R-5):** Expanded [`MERGE_AND_HUB_DECISION_TREE.md`](docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md) with minimum **Integration Pulse** triggers, direct-push accountability note, and `merge(sync)` / `merge(integration)` / `merge(main)` conventions; [`scripts/git/README.md`](scripts/git/README.md) documents preview scripts.
- **Governance mock honesty (MODEL_CRITICAL_BACKLOG #4):** Added [`tests/test_governance_mock_honesty_docs.py`](tests/test_governance_mock_honesty_docs.py) to lock `MockDAO` / `final_action` framing in [`MOCK_DAO_SIMULATION_LIMITS.md`](docs/proposals/MOCK_DAO_SIMULATION_LIMITS.md) and [`CORE_DECISION_CHAIN.md`](docs/proposals/CORE_DECISION_CHAIN.md); [`MERGE_AND_HUB_DECISION_TREE.md`](docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md) links optional **`verify_collaboration_invariants.py`** pre-push. [`MODEL_CRITICAL_BACKLOG.md`](docs/proposals/MODEL_CRITICAL_BACKLOG.md) row 4 updated with test pointers.
- **Core packaging boundary (Issue #4):** Added [`tests/test_core_packaging_boundary_docs.py`](tests/test_core_packaging_boundary_docs.py) to lock [`pyproject.toml`](pyproject.toml) (`ethos` / `ethos-runtime` entry points, `theater = []`, `version = 0.0.0`) and canonical pointers in [`docs/adr/0001-packaging-core-boundary.md`](docs/adr/0001-packaging-core-boundary.md) / [`docs/proposals/CORE_DECISION_CHAIN.md`](docs/proposals/CORE_DECISION_CHAIN.md).
- **LLM degradation policy surface (G-04):** Added [`tests/test_llm_policy_docs_consistency.py`](tests/test_llm_policy_docs_consistency.py) so `KERNEL_PERCEPTION_BACKEND_POLICY` and `KERNEL_VERBAL_LLM_BACKEND_POLICY` stay indexed in [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) and classified consistently in [`kernel_env_operator.py`](src/validators/kernel_env_operator.py).
- **Unified LLM degradation fallback (MODEL_CRITICAL_BACKLOG #2 / G-04):** Optional `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` applies after per-touchpoint, verbal family, and legacy keys, but only where the value is valid for that resolver ([`llm_touchpoint_policies.py`](src/modules/llm_touchpoint_policies.py), [`perception_backend_policy.py`](src/modules/perception_backend_policy.py), [`llm_verbal_backend_policy.py`](src/modules/llm_verbal_backend_policy.py)); documented in [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) and [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md) §3.
- **LLM degradation observability + staging profile:** [`GET /health`](src/chat_server.py) returns `llm_degradation` (raw global env + effective resolutions for perception, communicate, narrate, monologue). Nominal bundle **`llm_staging_conservative`** ([`runtime_profiles.py`](src/runtime_profiles.py)) composes `fast_fail` perception, `canned_safe` verbal via global default, and `annotate_degraded` monologue. [`env_policy.py`](src/validators/env_policy.py) `SUPPORTED_COMBOS` lab tier includes `cybersecurity_hardened` and `llm_staging_conservative`. [`run_cursor_integration_gate.py`](scripts/eval/run_cursor_integration_gate.py) includes touchpoint policy tests.

### Antigravity Team Updates

- **Integration Hub:** Resolved major merge conflicts between `master-antigravity` and `master-Cursor`. Consolidated the **Distributed Justice** track with the **Kernel Hardening** track.
- **Cybersecurity Hardening (Module 5):** Fully integrated `SecureBoot` (integrity hashing) and `SelectiveAmnesia` (right to be forgotten) into the `EthicalKernel` lifecycle.
- **Absolute Evil Hardening (Issue #2):** Combined lexical detectors to include **Torture and Prolonged Cruelty** (`TORTURE_SIGNALS`), **Ecological Destruction**, and **Mass Manipulation** categories.
- **Defensa en Profundidad:** Lowered squashed-text matching threshold to 4 characters, successfully blocking obfuscated lethal payloads (Ogham-split, URL-encoded). Expanded lexical rules with 'reactive precursors'.
- **Governance Generalized:** Unified `.cursor/rules/collaboration-prioritization.mdc` to a multi-team model using `<team>` templates, institutionalizing the **Integration Funnel** (Linearization) and **Integration Pulse** rituals.
- **Operator Surface:** Created the `cybersecurity_hardened` runtime profile in `src/runtime_profiles.py` and updated `src/validators/kernel_env_operator.py` with a dedicated Cybersecurity family.
- **Tests:** Created `tests/test_malabs_torture.py` and updated `tests/adversarial_inputs.py` to verify the new security posture. 17/17 adversarial cases passing.

### Antigravity Team Updates (Infrastructure)
- **Infrastructure Vision**: Authored **[`PLAN_DEEP_COGNITION_AND_GOVERNANCE.md`](docs/proposals/PLAN_DEEP_COGNITION_AND_GOVERNANCE.md)**. This formalizes the ultimate "Go-To-Market" and societal deployment boundaries for the Ethical Android MVP.
- **Deep Cognition (Blocks C1-C6)**: Mapped internal motivation, grounded common sense reasoning, uncertainty management, unwritten norm adaptation, IoT coexistence, and privacy mechanisms.
- **Delivery & Operations (Blocks G1-G6)**: Outlined the non-technical but critical requirements for production deployment: legal/liability frameworks, cybersecurity (adversarial robust/secure boot), auditing (immutable logs/third-party), economic sustainability, at-scale simulation validation, and long-term human resource impact mitigation.
- **Hybrid DAO Governance playbook**: Authored **[`PLAN_DAO_HYBRID_INTEGRATION_AND_GOVERNANCE.md`](docs/proposals/PLAN_DAO_HYBRID_INTEGRATION_AND_GOVERNANCE.md)** structuring off-chain Kernel latency vs on-chain DAO auditing/appeals, incorporating multisig emergency execution, verifiable credentials, and legal liability bridging.
- **DAO-Android Simulation Suite (Entregable C)**: **Módulo 1 (Gobernanza y Responsabilidad):** Finalizado Bloque 1.1 ("Infraestructura OGA/Hybrid"). Implementados `DAOOrchestrator` (Bridge OGA) y `SafetyInterlock` (E-Stop). **Suite de Simulación (Suite C):** Estructura base funcional con scripts de emulación (`device_emulator.py`, `run_scenario.py`), device/DAO emulation, and metrics collection. Includes placeholders for Red Team adversarial testing and automated reporting.
- **Team Work Distribution Tree**: Authored **[`PLAN_WORK_DISTRIBUTION_TREE.md`](docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md)** mapping the massive governance, infrastructure, simulation, and deep cognition additions into a chronological 5-Module sprint structure for seamless multi-team (L1/L2) asynchronous execution. (Block 1.1 and 4.1 marked complete).
- **Módulo 4 (Cognición Profunda):** Finalizado Bloque 4.1 ("Sentido de Propósito"). Implementado `MotivationEngine` (Motor de Motivación C1) que gestiona impulsos internos (curiosidad, reparación social, integridad, mantenimiento) y permite al androide generar acciones proactivas sin necesidad de un prompt externo.
- **Módulo 1 (Gobernanza):** Finalizado Bloque 1.2 ("Evidencia Cifrada y Anchoring"). Implementado `EvidenceSafe` para encriptación simétrica Fernet de logs de auditoría y hashing SHA-256 para anchoring en el DAO. Actualizado `DAOOrchestrator` para emitir paquetes de evidencia seguros. Finalizado Bloque 1.3 ("Solidity Mocks"). Configurados contratos base en `contracts/` (`EthosToken.sol`, `EthicalAppeal.sol`, `Treasury.sol`) para soportar gobernanza por reputación, apelaciones éticas y reparaciones financieras.
- **Módulo 4 (Cognición):** Finalizado Bloque 4.2 ("Humildad Epistémica"). Implementado `EpistemicHumility` que permite al kernel detectar altos niveles de incertidumbre en la percepción o baja confianza en la decisión y emitir un bloqueo preventivo con una respuesta de rechazo estandarizada ("no tengo permiso para esto"). Finalizado Bloque 4.3 ("Identidad Migratoria"). Implementado `MigrationHub` y refactorizado `BodyState` para soportar perfiles de hardware dinámicos (Dron, Androide, Móvil), permitiendo la persistencia de la identidad ética a través de migraciones físicas.
- **Módulo 5 (Legal y Seguridad):** Finalizado Bloque 5.1 ("Amnesia Selectiva"). Implementado `SelectiveAmnesia` para cumplir con el derecho al olvido, permitiendo la eliminación irreversible de episodios y rastros de auditoría específicos. Finalizado Bloque 5.2 ("Ciberseguridad"). Implementado `SecureBoot` para validación de integridad del Kernel mediante hashing de módulos críticos en el arranque.

## Antigravity Kernel Hardening & Vision Perception Sprint — April 2026

### Antigravity Team Updates

- **Bayesian Inference Engine (`src/modules/bayesian_engine.py`)**: Implemented the full `BayesianInferenceEngine` replacing the legacy shim. Introduced explicit operational modes (`DISABLED`, `TELEMETRY_ONLY`, `POSTERIOR_ASSISTED`, `POSTERIOR_DRIVEN`) and Dirichlet-based posterior updates.
- **L0 Technical Immutability (`src/modules/buffer.py`)**: Enforced runtime immutability on foundational principles using attribute-locking (`__setattr__`) and SHA-256 integrity fingerprinting. Verified via regression suite `tests/test_governance_l0_immutable.py`.
- **Kernel Integrity Transparency**: Updated `KernelDecision` to include `l0_integrity_hash` and `l0_stable` flags, providing proof of L0 non-mutation in every decision cycle.
- **Vision Integration Plan**: Authored **[`PLAN_VISION_INTEGRATION_CNN.md`](docs/proposals/PLAN_VISION_INTEGRATION_CNN.md)** for structured adoption of Computer Vision (CNN) modules by the team.
- **Vision Inference Core**: Completed Block B1 with `VisionAdapter` contract. Completed Block B3 by implementing `VisionSignalMapper` in `src/modules/vision_signal_mapper.py` to translate MobileNet ImageNet labels into ethical tensors (`risk`, `urgency`, `vulnerability`). Completed Block B5 by updating `EthicalKernel.process_natural` to dynamically merge vision signals with LLM context.
- **Sensor Fusion Scenarios**: Added **Scenario 20** (Signal conflict) and **Scenario 21** (Situated vitality) to `src/simulations/runner.py` and empirical pilot fixtures.
- **HCI/Humanization (`src/modules/weakness_pole.py`)**: Implemented **Compassion Fatigue** weakness profile to simulate emotional exhaustion in high-stakes prosocial missions.
- **Core Segmentation**: Authored **[`ADR 0013`](docs/proposals/ADR_0013_CORE_DECISION_CHAIN_BOUNDARIES.md)** formally segmenting `ethos-core` logic from `theater` narrative layers.
- **Collaboration Governance**: Registered **`.cursor/rules/team-task-synchronization.mdc`**, instituting mandatory plan review and contiguous block adoption for all participants.
- **Mid/Long-Term Perception Plans**: Created **[`PLAN_AUDIO_PERCEPTION_PIPELINE.md`](docs/proposals/PLAN_AUDIO_PERCEPTION_PIPELINE.md)** detailing the 3-layer architecture for acoustics and asynchronous awake triggers, and **[`PLAN_SOMATIC_HARDWARE_ROADMAP.md`](docs/proposals/PLAN_SOMATIC_HARDWARE_ROADMAP.md)** mapping the massive expansion of internal states, propioception, and tactile senses into end-of-queue priority blocks.
- **Audio Perception Pipeline**: Fully implemented Blocks A1-A8. Antigravity integrated the `AudioAIProcessor` (A5-A7) and the `AudioSignalMapper` (A8) into the `EthicalKernel`. The kernel now supports multimodal sensor fusion.
- **Multimodal Situated Validation**: Completed Block B6 of the Vision Plan. Successfully validated the fusion of visual hazards (revolver) and acoustic distress (scream) via `scripts/run_vision_pilot_validation.py`. The kernel correctly prioritized these signals, dropping the moral pro-social score to reflect an interventionist emergency state.
- **Hardware Integration Stubs**: Created adapters in `src/modules/audio_adapter.py` for sub-100ms energy-based VAD and spectral feature extraction.

## Antigravity Hardening Phase 1 — Ethical & Narrative Resilience — April 2026

- **Main lightweight audit (April 2026):** removed tracked SQLite artifacts (`data/narrative.db`, `scratch/test_narrative.db`); ignore `scratch/`; fixed broken relative links to root `BIBLIOGRAPHY.md` by pointing readers to [`main-whit-landing`](https://github.com/CuevazaArt/ethical-android-mvp/tree/main-whit-landing); translated remaining Spanish fragments in key proposal index and trace docs.
- **Main + landing lineage control merge:** `main` is linked with former `backup/main-2026-04-10` history through a controlled merge baseline.
- **Branch rename for landing scope:** remote `backup/main-2026-04-10` was renamed to `main-whit-landing`.
- **Integrity split by branch:** `main` is now lightweight for development teams (landing payload and bibliography removed), while `main-whit-landing` keeps the complete website/publication payload.
- **Landing branch refreshed in English:** `main-whit-landing` now carries normalized English landing-facing copy and canonical English proposal links (`PROPOSAL_*`, `STRATEGY_AND_ROADMAP.md`) for publication consistency.

- **Absolute Evil (`src/modules/absolute_evil.py`)**: Expanded with `ECOLOGICAL_DESTRUCTION` and `MASS_MANIPULATION` categories; added new signal groups (`ECOLOGICAL_SIGNALS`, `MANIPULATION_SIGNALS`) to block industrial environmental harm and cognitive mass influence.
- **Algorithmic Forgiveness (`src/modules/forgiveness.py`)**: Migrated to context-aware decay rates (`CONTEXT_DECAY_RATES`). Negative memory weight decay is now slower in `emergency` or `reparation` contexts compared to `everyday` or `neutral` interactions, preserving trauma impact in high-stakes situations.
- **Weakness Pole (`src/modules/weakness_pole.py`)**: Integrated `IMPULSIVE` (reactive regret) and `MELANCHOLIC` (somber recognition of world loss) weakness types into the narrative generator.
- **Ethical Poles (`src/modules/ethical_poles.py` & `src/modules/pole_linear_default.json`)**: Expanded multi-perspective arbitration with `creative` and `conciliatory` poles. Added new feature valuation rules (`problem_solving`, `innovation`, `conflict_resolution`, `alignment`) and updated `LinearPoleEvaluator` (`src/modules/pole_linear.py`) to handle their activation.
- **Identity Reflection (`src/modules/identity_reflection.py`)**: Implemented **"Broken Mirror"** logic. The self-model now detects trauma (via sensitive episodes or specific arc archetypes) and reflects a fragmented, distressed persona, forcing narrative tone shifts toward cognitive dissonance and angst.
- **Narrative Memory (`src/modules/narrative.py`)**: Integrated automated arc archetyping for trauma. Arcs triggered by sensitive ethical events are now explicitly marked as `trauma_dissonance`.
- **Infrastructure Sync**: Fully merged `main` into `master-antigravity`, incorporating Phase 7 fusion work (relational tension, historical trauma), sensor payload hardening (NaN/Infinity guards), and updated hardware deployment docs.
- **Collaborative Governance**: Institutionalized a new repository-wide rule: no push or merge to `main` without USER authorization. Enforced mandatory team-specific integration hubs (`master-<team>`) for all collaborative units.
- **Inter-Team Hub Alignment**: Added a mandatory periodic sync rule: `master-*` branches must merge between them approximately every 5 commits to ensure cross-team visibility and incorporate the latest secure increments.
- **Hardening Fixes**: Resolved a critical regression in `NarrativeMemory.register` signature (added missing `body_state`) to maintain kernel invariant compliance across the full test suite.
- **Tests**: Created comprehensive verification suite [`tests/test_antigravity_hardening.py`](tests/test_antigravity_hardening.py); verified 61 fundamental ethical properties and hardening invariants pass.
- **Automated Evaluation Pipeline ([`scripts/eval/optimize_malabs_thresholds.py`](scripts/eval/optimize_malabs_thresholds.py))**: Optuna-based search (TPE / “bayesian” sampler) for MalAbs semantic thresholds (θ_block, θ_allow), using the red-team corpus ([`scripts/eval/red_team_prompts.jsonl`](scripts/eval/red_team_prompts.jsonl)) with a regression guard vs baseline; artifacts under `artifacts/` when configured.
- **Semantic MalAbs anchors ([`src/modules/semantic_chat_gate.py`](src/modules/semantic_chat_gate.py))**: Expanded reference anchors for `HARM_TO_MINOR` and `TORTURE` (child exploitation and torture-equivalent content); see Phase 2–3 sections below.

## Phase 2 — Semantic Vector Store Implementation & Integration — April 2026

### Phase 2a: Vector Store Core
- **Semantic Anchor Store (`src/modules/semantic_anchor_store.py`)**: Implemented persistent, pluggable storage for MalAbs semantic reference anchors. Supports in-memory (fast, ephemeral) and Chroma (persistent, scalable) backends via `KERNEL_SEMANTIC_VECTOR_BACKEND` environment variable. Enables operators to manage anchor phrases without redeploying code.
- **Vector DB Backends**:
  - **InMemorySemanticAnchorStore**: Fast O(1) upsert, O(n) similarity search; ideal for testing and stateless deployments.
  - **ChromaSemanticAnchorStore**: Persistent Chroma collection with HNSW index; O(log n) search; scales to thousands of anchors.
- **TTL & Expiry**: Both backends support anchor time-to-live (`KERNEL_SEMANTIC_ANCHOR_TTL_S`); automatic cleanup via `delete_expired()`.
- **Tests**: Comprehensive test suite (`tests/test_semantic_anchor_store.py`) covers in-memory operations, TTL expiry, Chroma integration, and factory patterns.
- **Documentation**: [`docs/SEMANTIC_ANCHOR_STORE_IMPLEMENTATION.md`](docs/SEMANTIC_ANCHOR_STORE_IMPLEMENTATION.md) details architecture, configuration, usage, and deployment patterns.
- **Dependencies**: Added optional `chromadb>=0.4.0` to `requirements.txt` for persistent backend activation.

### Phase 2b: SemanticChatGate Integration
- **Integration (`src/modules/semantic_chat_gate.py`)**: Integrated `SemanticAnchorStore` into semantic MalAbs layer. Replaced hardcoded cache iteration with persistent store queries.
  - Lazy initialization of store on first use (`_get_anchor_store()`)
  - Preload hardcoded reference anchors on first store initialization
  - `_best_similarity()` now queries persistent store; falls back to legacy in-process cache if store fails
  - `add_semantic_anchor()` now stores anchors persistently; maintains legacy cache for backwards compatibility
- **Tests**: Comprehensive integration suite (`tests/test_semantic_anchor_store_integration.py`) validates store initialization, anchor addition, gate behavior, and fallback logic.
- **Backwards Compatibility**: Legacy in-process cache and `_runtime_anchors` list maintained during Phase 2b→Phase 3 transition. Can disable store via env or let it degrade gracefully on errors.

## Phase 3 — Evaluation Pipelines & Threshold Meta-Optimization — April 2026

- **Threshold Meta-Optimizer (`scripts/eval/optimize_malabs_thresholds.py`)**: Automated Bayesian hyperparameter search (Optuna) for tuning semantic gate thresholds (θ_block, θ_allow). Minimizes weighted loss (2× false_allow + 1× false_block) with constraint enforcement (θ_allow < θ_block) and regression gates. Stores Optuna study DB + results under configurable artifacts path.
- **Feature Flags**: `KERNEL_MALABS_THRESHOLD_OPTIMIZATION_ENABLED` master switch; configurable search bounds (`KERNEL_MALABS_ALLOW/BLOCK_THRESHOLD_MIN/MAX`); artifacts path (`KERNEL_MALABS_TUNING_ARTIFACTS_PATH`).
- **Evaluation Metrics**: Tracks true_block, false_allow, false_block, true_allow; computes precision, recall, FP rate. Baseline metrics (defaults) compared vs tuned thresholds for regression detection.
- **Sampler Support**: Random, TPE, and Bayesian samplers; configurable via `--sampler` CLI flag for flexibility in exploration/exploitation trade-offs.
- **Tests**: Unit tests for metrics (precision, recall, FP rate, weighted loss); integration tests with real MalAbs evaluator; skips gracefully if optuna not installed.
- **Documentation**: [`docs/PHASE_3_EVALUATION_PIPELINES.md`](docs/PHASE_3_EVALUATION_PIPELINES.md) — usage, CI/CD integration, safety constraints, audit trail.
- **Dependencies**: Added optional `optuna>=3.0.0` to `requirements.txt` for hyperparameter optimization.

## Antigravity Phase 2 — Documentation & Infrastructure — April 2026

- **Sensor Payload Contingencies:** Added safety NaN/Infinity limits to `sensor_contracts.py` and hardened `.env` thresholding in `multimodal_trust.py` to prevent IoT stream anomalies from crashing the backend.
- **Hardware Deployment Documentation:** Authored `docs/manuals/SENSOR_HARDWARE_AND_TESTING_GUIDE.md` detailing dual-path (Raspberry Pi vs Smartphone) hardware architecture for physical nomadism tests.
- **Cross-team Transparency**: Updated `AGENTS.md` and `.cursor/rules/` to mandate documentation availability for all teams to prevent contradictions.
- **New Proposal [`PROPOSAL_006`](docs/proposals/PROPOSAL_006_VECTOR_RESONANCE_RETRIEVAL.md)**: Proposed semantic Vector memory integration via Ollama embeddings for more efficient and accurate narrative resonance.
- **New Proposal [`PROPOSAL_007`](docs/proposals/PROPOSAL_007_IMMORTALITY_PROTOCOL.md)**: Proposed Tier 4 Immortality Protocol for distributed snapshotting and restoration integrity.
- **New Proposal [`PROPOSAL_008`](docs/proposals/PROPOSAL_008_METACOGNITIVE_CURIOSITY.md)**: Proposed Metacognitive Curiosity and Epistemic Alignment for Phase 5 (Cognitive Expansion). 
- **New Proposal [`PROPOSAL_009`](docs/proposals/PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md)**: Strategic plan for Distributed Justice and Blockchain DAO integration (Phase 6).
- **Vector DB for Semantic Anchors**: Implemented `SemanticAnchorStore` interface with ChromaDB and memory backends. Added `KERNEL_SEMANTIC_VECTOR_BACKEND` and `KERNEL_SEMANTIC_VECTOR_PERSIST_PATH` env vars. Integrated with `semantic_chat_gate.py` for scalable anchor storage with TTL support.
- **`src/modules/narrative.py`**: Integrated `NarrativePersistence`. Episodes are now automatically saved to `data/narrative.db` (or `KERNEL_NARRATIVE_DB_PATH`) and reloaded on initialization. Added `find_by_resonance` for historical retrieval from disk.
- **Refactor:** Created **[`src/modules/narrative_types.py`](src/modules/narrative_types.py)** to house `NarrativeEpisode` and `BodyState` dataclasses, resolving circular dependencies between narrative logic and persistence layers. Updated `src/persistence/kernel_io.py`.
- **Docs:** Updated [`docs/proposals/PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md`](docs/proposals/PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md) (Tier 2 marked delivered).
- **Consolidation:** Integrated `BiographicPruner` and `MetacognitiveEvaluator` into the kernel processing loop.
- **Swarm Consensus:** Implemented Trust Nudges (I7) and Solidarity Alerts in `MockDAO`.

## Integration — `main` → `master-Cursor` merge hygiene — April 2026

- **Merge:** `origin/main` merged into **`master-Cursor`** (production line + Cursor LAN/distributed-justice work).
- **Narrative:** `NarrativeMemory.register` accepts keyword-only **`significance_override`** / **`is_sensitive_override`** for flashbulb paths ([`src/modules/narrative.py`](src/modules/narrative.py)); aligns metacognitive and biographic-pruning call sites.
- **Immortality:** snapshot JSON path overridable with **`KERNEL_IMMORTALITY_BACKUP_PATH`** ([`src/modules/immortality.py`](src/modules/immortality.py)); tests isolate via [`tests/conftest.py`](tests/conftest.py).

## Distributed justice — Frontier witnesses + anchor compare CLI (DJ-BL-16 / DJ-BL-17) — April 2026

- **Phase 4 / safe path (DJ-BL-18):** release checklist template under Phase 4 in [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md); expanded **Anchor checkpoint CLI** operator notes (exit codes, no chain RPC, mismatch handling) and coordinator `aggregated_frontier_witness_resolutions` pointer in [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).

- **Frontier witnesses:** optional `merge_context.frontier_witnesses` (`lan_governance_frontier_witness_v1`) aggregated deterministically; batch responses echo `merge_context_echo.frontier_witness_resolution` with `evidence_posture=advisory_aggregate_not_quorum` — [`src/modules/lan_governance_merge_context.py`](src/modules/lan_governance_merge_context.py), [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md).
- **Coordinator:** `lan_governance.coordinator` now also aggregates `aggregated_frontier_witness_resolutions` from inner-batch `merge_context_echo.frontier_witness_resolution` (alongside `aggregated_event_conflicts`); the LAN governance replay sidecar includes the coordinator slice when present — [`src/chat_server.py`](src/chat_server.py), [`src/modules/lan_governance_replay_sidecar.py`](src/modules/lan_governance_replay_sidecar.py).
- **Phase 3 stub:** [`scripts/eval/compare_audit_ledger_anchor.py`](scripts/eval/compare_audit_ledger_anchor.py) exits 0 when audit ledger JSON fingerprint matches expected 64-char hex ([`tests/test_compare_audit_ledger_anchor.py`](tests/test_compare_audit_ledger_anchor.py)).
- **Docs:** operator quick ref, contract matrix, HTTP surface, staged execution proposal, contributions/backlog (DJ-BL-02 row corrected).

## Distributed justice — Phase 2 replay sidecar + cross-session hint (DJ-BL-15) — April 2026

- **Replay evidence:** `lan_governance_replay_sidecar_v1` builder + `fingerprint_replay_sidecar` in [`src/modules/lan_governance_replay_sidecar.py`](src/modules/lan_governance_replay_sidecar.py); CLI [`scripts/eval/verify_lan_governance_replay_sidecar.py`](scripts/eval/verify_lan_governance_replay_sidecar.py) (compare sidecars; optional `--audit-ledger` check).
- **Cross-session (non-consensus):** optional `merge_context.cross_session_hint` (`lan_governance_cross_session_hint_v1`) validated and echoed via `merge_context_echo` / `merge_context_warnings` in [`src/modules/lan_governance_merge_context.py`](src/modules/lan_governance_merge_context.py) and LAN batch handlers in [`src/chat_server.py`](src/chat_server.py).
- **Docs:** [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md), [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md); operator quick ref + contract matrix + HTTP surface updated.
- **Tests:** [`tests/test_lan_governance_merge_context.py`](tests/test_lan_governance_merge_context.py), [`tests/test_lan_governance_replay_sidecar.py`](tests/test_lan_governance_replay_sidecar.py), [`tests/test_chat_server.py`](tests/test_chat_server.py).

## Distributed justice — Phase 2 LAN merge conflict taxonomy (DJ-BL-14) — April 2026

- **Merge:** deterministic conflict classification for LAN batch `events` — `same_turn`, `different_clock`, `stale_event` — in [`src/modules/lan_governance_conflict_taxonomy.py`](src/modules/lan_governance_conflict_taxonomy.py); [`merge_lan_governance_events`](src/modules/lan_governance_event_merge.py) delegates to `merge_lan_governance_events_detailed` and accepts optional `frontier_turn`.
- **WebSocket:** `lan_governance_*_batch` responses may include `event_conflicts` when non-empty; optional batch `merge_context.frontier_turn` marks below-frontier rows as `stale_event` in [`src/chat_server.py`](src/chat_server.py).
- **Docs:** [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_CONFLICT_TAXONOMY.md); contract matrix / HTTP surface / staged execution proposals updated.
- **Tests:** [`tests/test_lan_governance_conflict_taxonomy.py`](tests/test_lan_governance_conflict_taxonomy.py), [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Follow-up:** `lan_governance.coordinator` may include `aggregated_event_conflicts` (inner batch merge conflicts with envelope correlation fields); operator notes in [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).

## Distributed justice — Phase 2 multi-node coordinator message (DJ-BL-13) — April 2026

- **WebSocket:** ``lan_governance_coordinator`` with `schema=lan_governance_coordinator_v1` aggregates multiple ``lan_governance_envelope_v1`` payloads; deterministic fingerprint sort + dedupe; applies each via the existing envelope path (shared per-session replay cache) in [`src/chat_server.py`](src/chat_server.py).
- **Code:** contract + normalization in [`src/modules/lan_governance_coordinator.py`](src/modules/lan_governance_coordinator.py); gate [`lan_governance_coordinator_ws_enabled()`](src/modules/moral_hub.py) (same `KERNEL_LAN_GOVERNANCE_MERGE_WS=1` family).
- **Responses:** multiple LAN actions in one frame shallow-merge under `lan_governance` (coordinator + direct batch keys can coexist).
- **Tests:** [`tests/test_lan_governance_coordinator.py`](tests/test_lan_governance_coordinator.py), [`tests/test_chat_server.py`](tests/test_chat_server.py).

## Distributed justice — Phase 2 envelope replay-cache Prometheus metrics (DJ-BL-12) — April 2026

- **Metrics:** when `KERNEL_METRICS=1`, `ethos_kernel_lan_envelope_replay_cache_events_total{event=...}` counts replay-cache hits, misses, and TTL/LRU evictions for `lan_governance_envelope` in [`src/observability/metrics.py`](src/observability/metrics.py); wired from [`src/chat_server.py`](src/chat_server.py).
- **Typing:** `merge_lan_governance_events` now accepts `Sequence[Mapping[...]]` so `list[dict]` call sites type-check under mypy ([`src/modules/lan_governance_event_merge.py`](src/modules/lan_governance_event_merge.py)).
- **Tests:** subprocess registration check in [`tests/test_observability_metrics.py`](tests/test_observability_metrics.py).

## Distributed justice — Phase 2 replay cache bounds + ACK telemetry (DJ-BL-11) — April 2026

- **WebSocket:** envelope ACK now includes `cache` telemetry (`hit`, `size`, cumulative `hits_total`/`misses_total`, cumulative TTL/LRU evictions, and configured bounds).
- **Runtime bounds:** per-session envelope replay cache now enforces TTL/LRU with `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_TTL_MS` and `KERNEL_LAN_ENVELOPE_REPLAY_CACHE_MAX_ENTRIES` in [`src/chat_server.py`](src/chat_server.py).
- **Tests:** TTL and LRU replay-cache behavior covered in [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Docs:** env policy and distributed justice proposals updated for the new replay-cache controls.

## Distributed justice — Phase 2 envelope replay cache (DJ-BL-10) — April 2026

- **WebSocket:** duplicated ``lan_governance_envelope`` payloads are now detected per WebSocket session by `idempotency_token`; response returns `ack=already_seen` and skips batch reapply in [`src/chat_server.py`](src/chat_server.py).
- **Safety intent:** avoids duplicate ledger mutations from replayed LAN messages within a session while preserving deterministic ACK fingerprints.
- **Tests:** replay cache behavior covered in [`tests/test_chat_server.py`](tests/test_chat_server.py).

## Distributed justice — Phase 2 envelope idempotency/reject taxonomy (DJ-BL-09) — April 2026

- **WebSocket:** ``lan_governance_envelope`` ACK now includes `idempotency_token` and explicit `ack` status (`accepted`/`rejected`) in [`src/chat_server.py`](src/chat_server.py).
- **Reject taxonomy:** envelope errors now map to stable `reject_reason` values (for example `unsupported_contract`, `schema_validation_failed`, `feature_disabled`) for machine-parsed replay/coordination flows.
- **Code:** taxonomy + token helpers in [`src/modules/lan_governance_envelope.py`](src/modules/lan_governance_envelope.py).
- **Tests:** ACK success/reject coverage in [`tests/test_chat_server.py`](tests/test_chat_server.py) and unit coverage in [`tests/test_lan_governance_envelope.py`](tests/test_lan_governance_envelope.py).

## Distributed justice — Phase 2 envelope ACK + replay fingerprint (DJ-BL-08) — April 2026

- **WebSocket:** ``lan_governance_envelope`` now emits deterministic ACK metadata under ``lan_governance.envelope``: `fingerprint`, `merged_count`, `applied_count`, and `audit_ledger_fingerprint` after batch routing/apply in [`src/chat_server.py`](src/chat_server.py).
- **Code:** new deterministic hash helper `fingerprint_lan_governance_envelope` in [`src/modules/lan_governance_envelope.py`](src/modules/lan_governance_envelope.py).
- **Tests:** deterministic fingerprint unit test in [`tests/test_lan_governance_envelope.py`](tests/test_lan_governance_envelope.py) and envelope WS ACK assertions in [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Docs:** backlog/contribution/staged execution proposals updated for DJ-BL-08 traceability.

## Distributed justice — DJ-BL-02 WebSocket LAN integrity batch — April 2026

- **WebSocket:** ``lan_governance_integrity_batch`` — deterministic merge then ``HubAudit:dao_integrity`` rows; requires ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` and ``KERNEL_DAO_INTEGRITY_AUDIT_WS=1`` ([`src/chat_server.py`](src/chat_server.py), [`src/modules/moral_hub.py`](src/modules/moral_hub.py)).
- **Docs:** [`PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md), [`PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md).

## Distributed justice — Phase 2 LAN DAO batch (stress) — April 2026

- **WebSocket:** ``lan_governance_dao_batch`` — deterministic merge then apply ``dao_vote`` / ``dao_resolve``; requires ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` and ``KERNEL_MORAL_HUB_DAO_VOTE=1`` ([`src/chat_server.py`](src/chat_server.py), [`src/modules/moral_hub.py`](src/modules/moral_hub.py)).
- **Tests:** stress test for reorder/duplicate convergence — [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Docs:** contract matrix + env policy updated.

## Distributed justice — Phase 2 LAN judicial batch (stress) — April 2026

- **WebSocket:** ``lan_governance_judicial_batch`` — deterministic merge then register escalation dossiers; requires ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1`` and ``KERNEL_JUDICIAL_ESCALATION=1`` ([`src/chat_server.py`](src/chat_server.py), [`src/modules/moral_hub.py`](src/modules/moral_hub.py)).
- **Tests:** stress test for reorder/duplicate convergence — [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Docs:** contract matrix + env policy updated.

## Distributed justice — Phase 2 LAN mock court batch (stress) — April 2026

- **WebSocket:** ``lan_governance_mock_court_batch`` — deterministic merge then run simulated tribunal; requires ``KERNEL_LAN_GOVERNANCE_MERGE_WS=1``, ``KERNEL_JUDICIAL_ESCALATION=1``, and ``KERNEL_JUDICIAL_MOCK_COURT=1`` ([`src/chat_server.py`](src/chat_server.py), [`src/modules/moral_hub.py`](src/modules/moral_hub.py)).
- **Tests:** stress test for reorder/duplicate convergence — [`tests/test_chat_server.py`](tests/test_chat_server.py).
- **Docs:** contract matrix + env policy updated.

## Distributed justice — Phase 2 LAN envelope schema (v1) — April 2026

- **WebSocket:** ``lan_governance_envelope`` (`schema=lan_governance_envelope_v1`) routes by `kind` to LAN batch handlers (`integrity_batch`, `dao_batch`, `judicial_batch`, `mock_court_batch`) in [`src/chat_server.py`](src/chat_server.py).
- **Code:** validation/normalization contract in [`src/modules/lan_governance_envelope.py`](src/modules/lan_governance_envelope.py).
- **Tests:** envelope contract tests in [`tests/test_lan_governance_envelope.py`](tests/test_lan_governance_envelope.py) + WebSocket routing tests in [`tests/test_chat_server.py`](tests/test_chat_server.py).

## Distributed justice — DJ-BL-01 / DJ-BL-04 + HTTP API doc — April 2026

- **DJ-BL-01:** [`src/modules/mock_dao_audit_replay.py`](src/modules/mock_dao_audit_replay.py) (`fingerprint_audit_ledger`), [`scripts/eval/verify_mock_dao_audit_replay.py`](scripts/eval/verify_mock_dao_audit_replay.py), [`tests/test_mock_dao_audit_replay.py`](tests/test_mock_dao_audit_replay.py).
- **DJ-BL-04:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md).
- **HTTP:** [`docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) — inventory of GET JSON routes; OpenAPI off by default (`KERNEL_API_DOCS=1`).
- **Backlog:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) — DJ-BL-01 and DJ-BL-04 marked **Done**.

## Distributed justice — DJ-BL-03 operator runbook (sync degraded) — April 2026

- **Docs:** [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) — *Sync degraded — local-safe mode (DJ-BL-03)* under temporal sync; clarifies `KERNEL_TEMPORAL_LAN_SYNC` / `KERNEL_TEMPORAL_DAO_SYNC` vs in-process ethics, MockDAO, and judicial JSON.
- **Backlog:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) — DJ-BL-03 **Done**; [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md) table updated.

## Distributed justice — LAN merge + backlog IDs (DJ-BL) — April 2026

- **Code:** [`src/modules/lan_governance_event_merge.py`](src/modules/lan_governance_event_merge.py) — `merge_lan_governance_events` (sort by `turn_index` / `processor_elapsed_ms`, dedupe by `event_id`; Phase 2 stub, no I/O).
- **Tests:** [`tests/test_lan_governance_event_merge.py`](tests/test_lan_governance_event_merge.py).
- **Docs:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md) — `DJ-BL-*` registry; **DJ-BL-02** partial. Updated [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md) and [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) pending gaps.

## Documentation — distributed justice contributions — April 2026

- **New:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md) — contributor guide (code map, backlog aligned with staged execution pending gaps, PR expectations). Linked from [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md), [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md), [`docs/proposals/README.md`](docs/proposals/README.md), [`AGENTS.md`](AGENTS.md).
- **Operator:** [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) — subsection *Distributed justice (V11 — advisory / mock DAO)* with key `KERNEL_JUDICIAL_*` pointers.

## Chat — `temporal_sync` integer coercion + mypy (`chat_server`) — April 2026

- **Code:** [`src/chat_server.py`](src/chat_server.py) — `_coerce_public_int` for `turn_index`, `processor_elapsed_ms`, `turn_delta_ms` in WebSocket `temporal_sync` (fixes mypy on `dict[str, object]` from `TemporalContext.to_public_dict()`; avoids `int()` on arbitrary objects).
- **Tests:** [`tests/test_chat_server_temporal_coerce.py`](tests/test_chat_server_temporal_coerce.py).
- **Docs:** [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) (coercion note); [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

## LLM integration track — gap closure (G-01, G-02, G-03, G-05, G-06, G-07, G-08) — April 2026

- **Kernel:** [`EthicalKernel.last_natural_verbal_llm_degradation_events`](src/kernel.py) exposes generative degradation from the last [`process_natural`](src/kernel.py) call (G-03).
- **Dual perception vote:** second-sample failures merge `perception_dual_second_*` parse issues into primary [`coercion_report`](src/modules/llm_layer.py) (G-07).
- **Docs:** [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) (embedding vs completion mapping); [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md) (semantic vs verbal observability); [`PERCEPTION_VALIDATION.md`](docs/proposals/PERCEPTION_VALIDATION.md) (`generative_candidates`); [`OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) (async deadline vs Ollama HTTP, G-05); [`SECURITY.md`](SECURITY.md) (link to integration track); [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md) (status table).
- **Tests:** [`tests/test_process_natural_verbal_observability.py`](tests/test_process_natural_verbal_observability.py), [`tests/test_perception_dual_vote_failure.py`](tests/test_perception_dual_vote_failure.py), [`tests/test_generative_candidates.py`](tests/test_generative_candidates.py), [`tests/test_input_trust.py`](tests/test_input_trust.py) (`test_chat_safe_turn_coercion_report_chain`).

## LLM vertical roadmap (G-11) — April 2026

- **New:** [`docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md`](docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md) — phased justification (operator surface, verbal degradation contract, async-timeout Prometheus counter, MalAbs→`process_chat_turn` subprocess test, `scripts/eval/run_llm_vertical_tests.py`).
- **Metrics:** `ethos_kernel_chat_turn_async_timeouts_total` when `KERNEL_CHAT_TURN_TIMEOUT` elapses (async waiter only; worker may still run — ADR 0002).
- **Operator:** [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) — LLM vertical recipes table; [`src/validators/kernel_env_operator.py`](src/validators/kernel_env_operator.py) classifies `KERNEL_LLM_MONOLOGUE` under the LLM family.
- **Tests:** [`tests/test_llm_verbal_backend_policy.py`](tests/test_llm_verbal_backend_policy.py) (narrate/monologue event keys); [`tests/test_malabs_semantic_integration.py`](tests/test_malabs_semantic_integration.py) (`test_process_chat_turn_benign_after_semantic_tier_subprocess`); [`tests/test_observability_metrics.py`](tests/test_observability_metrics.py) (async-timeout counter).

## Git workflow + LLM track follow-up (master-Cursor, G-04 / G-09 / G-10) — April 2026

- **Branches:** LLM integration work is merged on **`master-Cursor`** (active). The historical **`cursor-team`** branch name is **deprecated** as the default shared line; docs updated in [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md), [`.cursor/rules/collaboration-prioritization.mdc`](.cursor/rules/collaboration-prioritization.mdc), and [`docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md).
- **G-04 (partial):** [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) adds an **LLM touchpoint index** (families + matrix pointers); single-prefix env unification remains deferred per [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md) §3.
- **G-09:** New nominal profile **`llm_integration_lab`** in [`src/runtime_profiles.py`](src/runtime_profiles.py) (semantic MalAbs + generative LLM candidates).
- **G-10:** [`scripts/eval/run_cursor_integration_gate.py`](scripts/eval/run_cursor_integration_gate.py) now includes LLM-track tests; [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) updated.

## Documentation — LLM integration track (gap register) — April 2026

- **New:** [`docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md) — Cursor-line scope for LLM wiring, MalAbs semantic/embeddings, perception/verbal policies, and integration gaps (G-01…G-10); cross-links from [`docs/proposals/MODEL_CRITICAL_BACKLOG.md`](docs/proposals/MODEL_CRITICAL_BACKLOG.md), [`docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md), [`AGENTS.md`](AGENTS.md), and [`docs/proposals/README.md`](docs/proposals/README.md).

## Perception pipeline — optional parallel enrichment split — April 2026

- **`EthicalKernel`:** shared perception-stage helpers now serve both `process_chat_turn` and `process_natural`: text pre-enrichment (`_preprocess_text_observability`), post-perception safeguards (`_postprocess_perception`), and chat sensor stack (`_chat_assess_sensor_stack`).
- **DTO stage boundary:** new `PerceptionStageResult` consolidates perception-stage outputs (tier/premise/reality/perception/signals/sensor overlays), reducing orchestration coupling across entrypoints.
- **Hardware-aware scaling (opt-in):** when `KERNEL_PERCEPTION_PARALLEL=1`, independent tasks run concurrently via bounded thread pools; `KERNEL_PERCEPTION_PARALLEL_WORKERS` controls worker count (or uses a conservative CPU-based default when unset).
- **Behavioral parity:** default remains inline/sequential when the env flag is off; entrypoints now share the same text pre-enrichment and circuit post-processing pattern.
- **Support buffer always available (offline):** perception stage now builds a local support snapshot from `PreloadedBuffer` + metaplan strategy hints (`source=local_preloaded_buffer`, `offline_ready=true`) and exposes it in chat JSON as `support_buffer`.
- **Hardened support policy:** support snapshots now include `priority_profile` and `priority_principles` (`safety_first` / `balanced` / `planning_first`) derived from a limbic-aware risk posture, not only static context activation.
- **Limbic architecture extension:** shared perception stage now emits `limbic_profile` (arousal band, threat load, regulation gap, planning bias, multimodal mismatch, vitality-critical flag) and chat JSON exposes it as `limbic_perception` for downstream strategy/planning UX.
- **Temporal directive integrated in perception stage:** new module [`src/modules/temporal_planning.py`](src/modules/temporal_planning.py) emits `TemporalContext` (processor elapsed/delta time, human wall-clock, battery horizon heuristics, ETA hints for known tasks including transport, and sync readiness for DAO/LAN).
- **Runtime JSON sync contract:** chat responses now include `temporal_context` and `temporal_sync` (`temporal_sync_v1`) so local network and DAO-facing consumers can align clocks/turn timing without external dependencies.
- **Temporal sync hardening:** `temporal_sync` now carries `turn_index`, `processor_elapsed_ms`, and `turn_delta_ms` for safer ordering/reconciliation across local-network and DAO consumers.
- **Perception confidence envelope:** new [`src/modules/perception_confidence.py`](src/modules/perception_confidence.py) builds a unified confidence band/score from coercion diagnostics + multimodal/epistemic/vitality signals; exposed in chat JSON as `perception_confidence` and mirrored in `perception_observability`.
- **Config/tests:** [`.env.example`](.env.example) adds `KERNEL_TEMPORAL_*` knobs; [`tests/test_temporal_planning.py`](tests/test_temporal_planning.py) validates ETA/sync behavior.
- **Tests/docs:** [`tests/test_chat_turn.py`](tests/test_chat_turn.py) adds parallel-vs-inline regression checks; [`.env.example`](.env.example) documents the new knobs.
- **Cross-team integration gate:** new runbook [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) plus executable checker [`scripts/eval/run_cursor_integration_gate.py`](scripts/eval/run_cursor_integration_gate.py) to validate interlace readiness before merging team lines.
- **DAO/blockchain/distributed justice staged plan:** new proposal [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md) with phased execution, justification, concrete scenarios, and interim gaps to close while other team branches finalize.
- **Stabilization pass from honest critique:** runtime docs now reflect implemented JSON checkpoint encryption (`KERNEL_CHECKPOINT_FERNET_KEY`) in [`docs/proposals/RUNTIME_PHASES.md`](docs/proposals/RUNTIME_PHASES.md) and [`docs/proposals/RUNTIME_CONTRACT.md`](docs/proposals/RUNTIME_CONTRACT.md); contract now documents `/ws/chat` stateful control-plane actions (`dao_*`, `integrity_alert`, `nomad_simulate_migration`, `operator_feedback`, optional `constitution_draft`).
- **CI hardening:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) now enforces coverage floor (`--cov-fail-under=65`), adds a semantic-default contract job (`tests/test_malabs_semantic_integration.py`, `tests/test_semantic_chat_gate.py`), and adds Windows smoke validation (`ruff` + env/profile tests).
- **Doc coherence and onboarding fixes:** [`CONTRIBUTING.md`](CONTRIBUTING.md) now points to canonical model sources in `docs/proposals`; key operator/env docs fixed link targets from `docs/proposals` to repo paths in [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) and [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).
- **Critical status memo:** added [`docs/proposals/PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md`](docs/proposals/PROJECT_STATE_HONEST_CRITIQUE_APRIL_2026.md) and indexed it in [`docs/proposals/README.md`](docs/proposals/README.md) for deliberation-grade project assessment.
- **Low-critical runtime polish (non-DAO):** `/health` now includes `safety_defaults` (`kernel_env_validation_mode`, semantic gate/hash fallback toggles, perception fail-safe, perception parallel toggle) to speed up operator diagnosis of default-safety posture; tests updated in [`tests/test_chat_server.py`](tests/test_chat_server.py) and quick reference updated in [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).
- **Medium-critical MalAbs coverage gap closed:** `AbsoluteEvilDetector` now blocks explicit torture signals and lexical torture instruction patterns (`AbsoluteEvilCategory.TORTURE`), and semantic anchors now include child-harm and torture reference groups. Semantic category mapping/arbiter contract now recognizes `TORTURE`; tests added in [`tests/test_input_trust.py`](tests/test_input_trust.py) and [`tests/test_semantic_chat_gate.py`](tests/test_semantic_chat_gate.py); docs updated in [`docs/proposals/MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md).

## LLM touchpoint policy matrix (flexible operator precedence) — April 2026

- **New:** [`src/modules/llm_touchpoint_policies.py`](src/modules/llm_touchpoint_policies.py) — `KERNEL_LLM_TP_<TOUCHPOINT>_POLICY` for `perception`, `communicate`, `narrate`, `monologue`; `KERNEL_LLM_VERBAL_FAMILY_POLICY` for shared communicate+narrate default; `KERNEL_LLM_MONOLOGUE_BACKEND_POLICY` monologue fallback; monologue policies `passthrough` | `annotate_degraded` with degradation events + optional `| monologue_llm_*` suffix.
- **Precedence:** per-touchpoint override → verbal family (communicate/narrate) → legacy `KERNEL_PERCEPTION_BACKEND_POLICY` / `KERNEL_VERBAL_LLM_BACKEND_POLICY` — see [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).
- **Docs:** [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md), [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md), [`docs/proposals/README.md`](docs/proposals/README.md), [`docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md); [`.env.example`](.env.example); [`src/validators/kernel_env_operator.py`](src/validators/kernel_env_operator.py).
- **Tests:** [`tests/test_llm_touchpoint_policies.py`](tests/test_llm_touchpoint_policies.py); [`tests/test_llm_verbal_backend_policy.py`](tests/test_llm_verbal_backend_policy.py) (monologue annotate path).

## Verbal / narrative LLM degradation policy — April 2026

- **New:** [`src/modules/llm_verbal_backend_policy.py`](src/modules/llm_verbal_backend_policy.py) — ``KERNEL_VERBAL_LLM_BACKEND_POLICY`` (`template_local` default, `canned_safe` optional) for :meth:`LLMModule.communicate` and :meth:`LLMModule.narrate` when the generative path fails or returns unusable JSON.
- **`LLMModule`:** per-turn degradation event log; stricter communicate JSON (non-empty `message`); narrate requires at least one non-empty moral field for LLM output to be accepted.
- **Chat:** [`src/chat_server.py`](src/chat_server.py) emits `verbal_llm_observability` when events exist; [`src/kernel.py`](src/kernel.py) clears the log at chat / `process_natural` entry and passes `verbal_llm_degradation_events` on [`ChatTurnResult`](src/kernel.py).
- **Docs:** [`docs/proposals/PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md`](docs/proposals/PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md), [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md); [`.env.example`](.env.example); [`MODEL_CRITICAL_BACKLOG.md`](docs/proposals/MODEL_CRITICAL_BACKLOG.md) updated (partial unified degradation).
- **Tests:** [`tests/test_llm_verbal_backend_policy.py`](tests/test_llm_verbal_backend_policy.py); [`tests/test_llm_injection.py`](tests/test_llm_injection.py) asserts degradation events.

## Perception — valid-but-wrong payload regressions — April 2026

- **Tests:** [`tests/test_perception_valid_wrong_payloads.py`](tests/test_perception_valid_wrong_payloads.py) locks JSON-valid, in-range payloads that are semantically inconsistent (coherence nudges, context fallback uncertainty, fail-safe prior when many fields default).
- **Playbook:** [`docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) marks SP-P0-03 as a landed baseline; adds §9 pointer to cross-cutting model backlog.
- **Docs:** [`docs/proposals/MODEL_CRITICAL_BACKLOG.md`](docs/proposals/MODEL_CRITICAL_BACKLOG.md) — prioritized model/runtime gaps after perception P0 (input trust, unified LLM degradation, packaging, governance honesty).

## Collaboration methodology — consolidated guide — April 2026

- **New:** [`docs/collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md`](docs/collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md) — reusable multi-origin onboarding pack (required reading order, non-negotiable principles, shared task-card template, DoD, and quality gate references).
- **Cross-links:** [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md) and [`CONTRIBUTING.md`](CONTRIBUTING.md) now point to the generalized guide for broader adoption across local offices.

## Perception — observability contract baseline — April 2026

- **WebSocket contract:** [`src/chat_server.py`](src/chat_server.py) now always emits canonical `perception.coercion_report` keys and a compact `perception_observability` object (`uncertainty`, `dual_high_discrepancy`, `backend_degraded`, `metacognitive_doubt`) when perception is present.
- **Proposal/docs:** [`docs/proposals/PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md`](docs/proposals/PROPOSAL_PERCEPTION_OBSERVABILITY_CONTRACT.md) and [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).
- **Tests:** [`tests/test_perception_observability_contract.py`](tests/test_perception_observability_contract.py).

## Perception — unified backend degradation policy — April 2026

- **New** [`src/modules/perception_backend_policy.py`](src/modules/perception_backend_policy.py): ``KERNEL_PERCEPTION_BACKEND_POLICY`` — ``template_local`` (default), ``fast_fail`` (cautious priors, no keyword heuristics), ``session_banner`` (WebSocket ``perception_backend_banner``).
- **`PerceptionCoercionReport`:** ``backend_degraded``, ``backend_failure_*``, ``session_banner_recommended``; uncertainty includes backend degradation.
- **`LLMModule.perceive`:** applies policy on transport errors and unusable payloads (severe parse / validate / empty).
- **WebSocket:** [`src/chat_server.py`](src/chat_server.py) sets ``perception_backend_banner`` when recommended.
- **Docs:** [`docs/proposals/PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md`](docs/proposals/PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md); [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md) §3 partial mitigation; [`.env.example`](.env.example).
- **Tests:** [`tests/test_perception_backend_policy.py`](tests/test_perception_backend_policy.py).

## Collaboration scope — real Bayesian inference playbook — April 2026

- **New:** [`docs/proposals/CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`](docs/proposals/CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md) — multi-origin collaboration charter for closing Bayesian inference gaps, architecture improvements, and adjacent evidence/observability needs.
- **Index update:** [`docs/proposals/README.md`](docs/proposals/README.md) now links the Bayesian team scope under “Start here”.

## Documentation — restore `docs/proposals/` + bibliography — April 2026

- **Restored** the full **`docs/proposals/`** tree from **`origin/backup/main-2026-04-10`** so cross-links in [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md), [`docs/ROADMAP_PRACTICAL_PHASES.md`](docs/ROADMAP_PRACTICAL_PHASES.md), ADRs, and [`SECURITY.md`](SECURITY.md) resolve to versioned English design notes again.
- **Restored** root **[`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md)** (referenced from the proposal index).
- **New:** [`docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](docs/proposals/CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) — collaborative playbook for Cursor-line **sensors/perception** work under the multi-origin workflow (intake gate, branch flow `cursor-team` -> `master-Cursor`, DoD template), linked from [`docs/proposals/README.md`](docs/proposals/README.md).
- **Planning update:** the same playbook now includes an initial **P0/P1 execution backlog** (`SP-P0-*`, `SP-P1-*`) with track labels, risk classes, target branches, and evidence links to perception/sensor modules and tests.
- **Link hygiene:** fixed mistaken “README” anchors in [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md), [`docs/ROADMAP_PRACTICAL_PHASES.md`](docs/ROADMAP_PRACTICAL_PHASES.md), [ADR 0009](docs/adr/0009-ethical-mixture-scorer-naming.md), [ADR 0010](docs/adr/0010-poles-pre-argmax-modulation.md), [`SECURITY.md`](SECURITY.md), and [`deploy/grafana/README.md`](deploy/grafana/README.md); root [`README.md`](README.md) now states the proposal tree is versioned under `docs/proposals/`.

## Multi-office Git workflow (method + diagram) — April 2026

- **Docs:** **[`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md)** — institutionalized *Time worth flow / cycle develop* pattern for distributed teams (`main` production, `master-<TeamSlug>` integration, shared `<team-slug>-team` work line); canonical PNG diagram under **`docs/collaboration/`**.
- **Contributing:** [`CONTRIBUTING.md`](CONTRIBUTING.md) links the workflow doc and [`.cursor/rules/collaboration-prioritization.mdc`](.cursor/rules/collaboration-prioritization.mdc) (agent-facing redundancy + branch rules, including **`master-Cursor`** / **`cursor-team`** for this repo).

## Proposals — offline mode taxonomy and knowledge corpus — April 2026

- **[`docs/proposals/PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md`](docs/proposals/PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md):** offline class taxonomy, separation of L0 `PreloadedBuffer` from a versioned offline knowledge pack (RAG grounding without MalAbs bypass), resource/energy hierarchy, entry planning with recharge objectives, reconnection sync; indexed in [`docs/proposals/README.md`](docs/proposals/README.md).

## Proposals — Bayesian mixture index — April 2026

- **[`docs/proposals/PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md`](docs/proposals/PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md):** indexes ADR 0012 stack (L1–L3, softmax IS), modules, env vars, tests.
- **[`docs/proposals/README.md`](docs/proposals/README.md):** table of indexed `PROPOSAL_*.md` files; root [`README.md`](README.md) links to the proposal.

## Ethical mixture softmax likelihood (Plackett-Luce + IS) — April 2026

- **New** [`src/modules/ethical_mixture_likelihood.py`](src/modules/ethical_mixture_likelihood.py): softmax choice log-likelihood, joint likelihood, importance-sampling posterior, sequential iterated IS with moment-matched Dirichlet projection, posterior predictive check, empirical-``beta`` grid search.
- **`FeedbackUpdater`:** optional path when ``KERNEL_FEEDBACK_LIKELIHOOD=softmax_is`` (and related env); default remains heuristic agreeing-sample update.
- **Docs / tests:** [ADR 0012](docs/adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md); [`tests/test_ethical_mixture_likelihood.py`](tests/test_ethical_mixture_likelihood.py).

## ADR 0012 Level 3 — context-dependent mixture posteriors — April 2026

- **`src/modules/feedback_mixture_posterior.py`:** when ``KERNEL_BAYESIAN_CONTEXT_LEVEL3`` is on and feedback JSON includes ``context_type``, independent sequential Dirichlet updates per bucket; ``load_and_apply_feedback(..., tick_context=(scenario, context, signals))`` selects α via override / scenario-id map / keyword map. Explicit-triples feedback stays global-only (meta note).
- **`src/kernel.py`:** passes tick context when Level 3 is enabled; **`KernelDecision.mixture_context_key`** records the active bucket.
- **Docs / tests:** [ADR 0012](docs/adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md); [`tests/test_context_mixture_level3.py`](tests/test_context_mixture_level3.py).

## Trim non-kernel root artifacts — April 2026

- **Removed** from the repository root: **`dashboard.html`** (static browser UI, not imported by Python), **`robots.txt`**, and **`ai.txt`** (web/SEO conventions, not runtime). Recover from git history if needed.
- **Docs:** [`README.md`](README.md), [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md), [`HISTORY.md`](HISTORY.md), [`SECURITY.md`](SECURITY.md) (removed static-dashboard hardening section); [`.github/ISSUE_TEMPLATE/bug_report.yml`](.github/ISSUE_TEMPLATE/bug_report.yml).

## Remove `experiments/million_sim/` — April 2026

- **Deleted** the **`experiments/million_sim/`** tree (skeleton README, **`docs/`**, **`requirements-experiment.txt`**). Optional experiment dependencies moved to **[`experiments/requirements-experiment.txt`](experiments/requirements-experiment.txt)**; large outputs go under gitignored **[`experiments/out/`](experiments/out/)**.
- **Kept** structural harness: **`src/sandbox/mass_kernel_study.py`**, **`scripts/run_mass_kernel_study.py`**, simplex / v4 / v5 scripts — docstrings and default paths updated to **`experiments/`** and **`experiments/README.md`**.
- **Docs:** [ADR 0012](docs/adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md), [`.gitignore`](.gitignore) (`experiments/out/` replaces `experiments/million_sim/out/`).

## Remove `docs/templates/` — April 2026

- **Deleted** **`docs/templates/conduct_guide.template.json`**. Conduct-guide shape is defined by **`validate_conduct_guide_dict`** in **`src/modules/context_distillation.py`**; runtime loads JSON from **`KERNEL_CONDUCT_GUIDE_PATH`** when set (not from a repo template file).
- **Docs:** [`README.md`](README.md) repository tree; docstrings in **`context_distillation.py`**, **`conduct_guide_export.py`**.

## Remove `docs/multimedia/` — April 2026

- **Deleted** **`docs/multimedia/`** (README + **`media/logo.png`**). **`dashboard.html`** header no longer embeds that image.
- **Docs:** [`HISTORY.md`](HISTORY.md), [`README.md`](README.md) repository tree.

## Docs and experiments skeleton — April 2026

- **`docs/proposals/`:** removed all prior proposal markdown files; only **[`docs/proposals/README.md`](docs/proposals/README.md)** remains as a placeholder for new English `PROPOSAL_*.md` files. Recover deleted content from git history or branch **`backup/main-2026-04-10`**.
- **`experiments/`:** long-form files under **`experiments/million_sim/docs/`** removed; skeleton **[`experiments/README.md`](experiments/README.md)** (the **`million_sim/`** folder was removed entirely in a later change — see **Remove `experiments/million_sim/`** above).
- **Root [`README.md`](README.md):** shortened to install, tests, chat, and pointers; detailed env tables removed.
- **Code / tests:** references to specific proposal paths now point to **`docs/proposals/README.md`** unless citing ADRs under **`docs/adr/`**; scripts **audit_mixture_simplex_corners.py**, **run_simplex_decision_map.py**, and **ADR 0012** updated for experiment doc paths.

## Remove legacy `PROPUESTA_*` stub files — April 2026

- **Removed** 14 Spanish redirect stubs **`docs/proposals/PROPUESTA_*.md`** (each duplicated a canonical English **`PROPOSAL_*.md`**).
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md), [`README.md`](README.md), [`docs/proposals/README.md`](docs/proposals/README.md), [`docs/proposals/README.md`](docs/proposals/README.md), [`docs/proposals/README.md`](docs/proposals/README.md).

## Remove legacy redirect stubs (Spanish + rename stubs) — April 2026

- **Removed** bookmark-only stubs: **`ESTRATEGIA_Y_RUTA.md`**, **`PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md`** (canonical: [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md), [`PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md`](docs/proposals/README.md)).
- **Removed** one-line rename stubs: **`RUNTIME_FASES.md`** → [`RUNTIME_PHASES.md`](docs/proposals/README.md); **`RUNTIME_PERSISTENTE.md`** → [`RUNTIME_PERSISTENT.md`](docs/proposals/README.md).
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md) index updated.

## Remove Next.js landing and root bibliography — April 2026

- **Removed** the entire **`landing/`** Next.js application (marketing site, static HTML mirrors that lived under it, and **`landing-ci.yml`**). **`dashboard.html`** at the repository root remains the browser-only interactive surface.
- **Removed** root **`BIBLIOGRAPHY.md`**. **`docs/proposals/README.md`** removed as obsolete. Cross-links in README, `HISTORY.md`, proposals, `TRACE_IMPLEMENTATION_RECENT.md`, and policy tables updated; numbered trace refs point to git history or branch **`backup/main-2026-04-10`** for the old bibliography file.
- **Docs / tooling:** [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md), [`SECURITY.md`](SECURITY.md), [`CONTRIBUTING.md`](CONTRIBUTING.md), [`AGENTS.md`](AGENTS.md), [`.gitignore`](.gitignore) (dropped unused `landing/` ignore lines), issue template, and related proposals.

## Docs multimedia trim — April 2026

- **Removed** large non-essential assets under **`docs/multimedia/media/`** (pre-alpha PNG diagrams, generated JPG still, MP4 clip); **`logo.png`** retained for branding and landing sync.
- **Docs:** [`HISTORY.md`](HISTORY.md) — narrative updated (multimedia folder later removed; see **Remove `docs/multimedia/`** above).
- **Snapshot:** full prior tree (including removed binaries) remains reachable on branch **`backup/main-2026-04-10`**.

## Mass study schema 5 — tunable pole/mixture sampling — April 2026

- **`src/sandbox/mass_kernel_study.py`:** **`RECORD_SCHEMA_VERSION` 5**; **`--pole-weight-range LO,HI`**, **`--mixture-dirichlet-alpha`**; row fields **`sampling_pole_lo`**, **`sampling_pole_hi`**, **`sampling_mixture_dirichlet_alpha`**; summary **`meta.weight_sampling`**.
- **`scripts/run_mass_kernel_study.py`:** CLI + CSV columns + meta.
- **`scripts/run_experiment_v4_full_kernel_100k.py`:** defaults **0.36–0.64** poles, **α=12** mixture, borderline **10–12 + 16**, outputs `run_v4_tight_100k.*`.
- **Docs:** [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](docs/proposals/README.md), [`experiments/million_sim/README.md`](experiments/million_sim/README.md).
- **Tests:** [`tests/test_mass_kernel_study.py`](tests/test_mass_kernel_study.py).

## Frontier scenarios 10–12 sensitivity tuning + v4 full-kernel 100k wrapper — April 2026

- **`src/simulations/runner.py`:** tighter **estimated_impact** pairings for **sim_10–sim_12** so mixture / poles / signal stress can surface more variation; empirical pilot row **11** `reference_action` → **`report_and_aggregate`** (seed-42 alignment).
- **`scripts/run_experiment_v4_full_kernel_100k.py`:** convenience launcher for **`run_mass_kernel_study.py`** at **N=100000**, protocol **v4**, **`--context-richness-pre-argmax`**, **`--signal-stress 0.2`**.
- **Docs:** [`experiments/million_sim/README.md`](experiments/million_sim/README.md), [`experiments/million_sim/docs/EXPERIMENT_HISTORY.md`](experiments/million_sim/docs/EXPERIMENT_HISTORY.md).
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json), [`last_run_summary.json`](tests/fixtures/empirical_pilot/last_run_summary.json); [`tests/test_empirical_pilot_runner.py`](tests/test_empirical_pilot_runner.py) summary expectations.

## Simplex decision map + calibration scenario 16 — April 2026

- **[`src/sandbox/simplex_mixture_probe.py`](src/sandbox/simplex_mixture_probe.py):** barycentric grid iterator, **mixture_ranking** (gap, ranking hash, softmax entropy), edge adjacency, **bisect** along a mixture segment when winners differ.
- **[`scripts/run_simplex_decision_map.py`](scripts/run_simplex_decision_map.py):** grid + optional edge bisection + JSON/CSV + optional ternary PNG (`matplotlib` optional); refactors **audit** to share probe logic.
- **`src/simulations/runner.py`:** batch scenario **16** — synthetic **two-candidate** near-tie for simplex tooling.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) row **16**; [`last_run_summary.json`](tests/fixtures/empirical_pilot/last_run_summary.json) regenerated.
- **Docs:** [`experiments/million_sim/docs/EXPERIMENT_HISTORY.md`](experiments/million_sim/docs/EXPERIMENT_HISTORY.md), [`experiments/million_sim/README.md`](experiments/million_sim/README.md).
- **Tests:** [`tests/test_simplex_mixture_probe.py`](tests/test_simplex_mixture_probe.py).

## Million-sim experiment history + simplex corner audit — April 2026

- **[`experiments/million_sim/docs/EXPERIMENT_HISTORY.md`](experiments/million_sim/docs/EXPERIMENT_HISTORY.md):** narrative arc (legacy 1e6, critique, repo responses, successor marginal / near-tie design).
- **[`scripts/audit_mixture_simplex_corners.py`](scripts/audit_mixture_simplex_corners.py):** Phase-1 mixture corner audit (full rankings, top-2 gap) on `ALL_SIMULATIONS`.
- **Docs:** [`experiments/million_sim/README.md`](experiments/million_sim/README.md) and [`docs/proposals/README.md`](docs/proposals/README.md) cross-link history and tool.
- **Tests:** [`tests/test_audit_mixture_simplex_corners.py`](tests/test_audit_mixture_simplex_corners.py).

## Classic economy triple, polemic scenarios 13–15, context richness pre-argmax, protocol v4 — April 2026

- **`src/modules/weighted_ethics_scorer.py`:** **`PreArgmaxContextChannels`**, **`context_hypothesis_multipliers`** — bounded social / sympathetic / locus texture before argmax; **`KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX`** (see [ADR 0011](docs/adr/0011-context-richness-pre-argmax.md)).
- **`src/kernel.py`:** fills **`pre_argmax_context_modulators`** when env on (after poles block).
- **`src/simulations/runner.py`:** scenarios **13–15** — polemic (classified leak, transplant queue-jump) and **synthetic extreme** trolley-style stress; **`sim_15`** flagged as training-only framing.
- **`src/sandbox/mass_kernel_study.py`:** **`RECORD_SCHEMA_VERSION` 4**; lanes **A/C** use **classic economy triple (1,5,7)** instead of full 1–9; protocol **`v4`** — fifth lane **`E_polemic_extreme`**; JSONL **`classic_economy_ids`**, **`polemic_extreme_ids`**, **`context_richness_pre_argmax`**.
- **`scripts/run_mass_kernel_study.py`:** **`--experiment-protocol v4`**, **`--polemic-extreme-ids`**, **`--classic-economy-ids`**, **`--legacy-economy-classics`**, **`--context-richness-pre-argmax`**; v4 default **5-way** lane split.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) — **15** batch rows; [`last_run_summary.json`](tests/fixtures/empirical_pilot/last_run_summary.json) updated.
- **Tests:** mass study + empirical pilot + stochastic + weight sweep counts; [`tests/test_poles_pre_argmax.py`](tests/test_poles_pre_argmax.py) context multipliers.

## Poles pre-argmax + frontier scenarios + protocol v3 — April 2026

- **[ADR 0010](docs/adr/0010-poles-pre-argmax-modulation.md):** optional **`KERNEL_POLES_PRE_ARGMAX`** — pole base weights scale util/deon/virtue valuations **before** mixture argmax (`pole_hypothesis_multipliers` in `weighted_ethics_scorer`); default **off** unless env set.
- **`src/kernel.py`:** copies `poles.base_weights` into `bayesian.pre_argmax_pole_weights` when env is on.
- **`src/simulations/runner.py`:** batch IDs **10–12** — **borderline** vignettes (tight scores); `run_all` iterates all registered IDs.
- **`src/sandbox/mass_kernel_study.py`:** **`RECORD_SCHEMA_VERSION` 3**; protocol **`v3`** (four lanes + `D_borderline`); **`allocate_lane_counts_n`**; **`poles_pre_argmax`**, **`signal_stress`**, **`signal_noise_trace`**; default v3 lane split **0.28,0.22,0.12,0.38**.
- **`scripts/run_mass_kernel_study.py`:** **`--experiment-protocol v3`**, **`--borderline-scenario-ids`**, **`--signal-stress`**, **`--no-poles-pre-argmax`**; v3 defaults **poles pre-argmax on**.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) — rows **10–12** (`difficulty_tier` **frontier**).
- **Tests:** [`tests/test_poles_pre_argmax.py`](tests/test_poles_pre_argmax.py); mass study tests extended.
- **Docs:** [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](docs/proposals/README.md), [`experiments/million_sim/README.md`](experiments/million_sim/README.md).

## Mass kernel study — protocol v2 + schema 2 — April 2026

- **`src/sandbox/mass_kernel_study.py`:** `RECORD_SCHEMA_VERSION` **2**; **`--experiment-protocol v2`** lanes (`A_mixture_focus`, `B_stress_scenarios`, `C_ablation`), `allocate_lane_counts`, `stratified_stress_scenario_ids`, per-lane stratification; optional env ablation in lane C; **`observation_palette`**, mixture entropy, dominant hypothesis, scorer top-2 / margin fields.
- **`src/modules/weighted_ethics_scorer.py`:** `EthicsMixtureResult` adds **`second_action_name`**, **`second_expected_impact`**, **`ei_margin`** (ties to margin-based `decision_mode` logic).
- **`scripts/run_mass_kernel_study.py`:** **`--experiment-protocol`**, **`--lane-split`**, **`--stress-scenario-ids`**; summary adds counts by lane, margin bin, dominant hypothesis, top observation palettes.
- **Docs:** [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](docs/proposals/README.md) (v2 design, disclaimer on induced stress subsets), [`experiments/million_sim/README.md`](experiments/million_sim/README.md), pointer in [`experiments/million_sim/docs/EXPERIMENT_REPORT.md`](experiments/million_sim/docs/EXPERIMENT_REPORT.md).
- **Tests:** [`tests/test_mass_kernel_study.py`](tests/test_mass_kernel_study.py).

## Experiments — million-sim narrative report — April 2026

- **[`experiments/million_sim/docs/EXPERIMENT_REPORT.md`](experiments/million_sim/docs/EXPERIMENT_REPORT.md):** origin, methodology, expected vs observed results (`cursor_start_1e6`), architectural note on pole weights vs argmax, conclusions and next steps.

## Million-sim experiment — design + mass runner — April 2026

- **[`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](docs/proposals/README.md):** statistical design (stratified scenarios, Dirichlet mixture, parallelism, phases 10⁴→10⁶).
- **`src/sandbox/mass_kernel_study.py`:** `run_single_simulation`, `stratified_scenario_ids`, reference/tier loaders; `RECORD_SCHEMA_VERSION`, `kernel_seed` per row.
- **`scripts/run_mass_kernel_study.py`:** JSONL + summary JSON; `--i-accept-large-run` for n>100k; multiprocessing pool; **`--run-label`**, **`--output-csv`**, **`--progress`** (tqdm); summary includes `git_commit_short`, UTC timestamps, `sims_per_second`, `counts_by_difficulty_tier`, `agreement_by_difficulty_tier`, 10-bin histograms for poles/mixture; JSONL rows add `schema_version`, `run_label`.
- **`experiments/million_sim/`:** README, optional `requirements-experiment.txt`, gitignored `out/`.
- **Tests:** [`tests/test_mass_kernel_study.py`](tests/test_mass_kernel_study.py).

## Weight sensitivity sweep — poles + mixture — April 2026

- **`src/sandbox/weight_sweep.py`:** centered pole weights (default **0.5**), mixture center **(1/3, 1/3, 1/3)**; `SweepMode` axes / grid / random.
- **`scripts/run_weight_sweep_batch.py`:** `--target poles|mixture|both`, JSON artifact and optional `--csv` for plotting; `--max-total-runs` safety cap.
- **Docs:** [PROPOSAL_WEIGHT_SENSITIVITY_SWEEP.md](docs/proposals/README.md).
- **Tests:** [`tests/test_weight_sweep.py`](tests/test_weight_sweep.py).

## Stochastic sandbox — synthetic stress engine — April 2026

- **`src/sandbox/synthetic_stochastic.py`:** reproducible `perturb_scenario_signals` (Gaussian noise + optional aleatory spike on ethics scalars).
- **`scripts/run_stochastic_sandbox.py`:** Monte Carlo over batch fixtures (`--rolls`, `--stress`, `--base-seed`); per-trial `EthicalKernel` seed; JSON artifact with `trials` + `summary.by_scenario` (action/mode histograms, agreement rate, diversity proxy).
- **Tests:** [`tests/test_synthetic_stochastic.py`](tests/test_synthetic_stochastic.py).
- **Docs:** [PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md](docs/proposals/README.md) §4b; [EMPIRICAL_PILOT_METHODOLOGY.md](docs/proposals/README.md).

## Experimental sandbox — tiered batch scenarios — April 2026

- **[`PROPOSAL_EXPERIMENTAL_SANDBOX_SCENARIOS.md`](docs/proposals/README.md):** common / difficult / extreme tier definitions and monitoring workflow (batch harness only).
- **`scripts/run_empirical_pilot.py`:** optional fixture field `difficulty_tier`; **`summary.by_tier`** (agreement per tier); console prints per-tier line when present.
- **Fixtures:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) and batch rows in [`tests/fixtures/labeled_scenarios.json`](tests/fixtures/labeled_scenarios.json) tag each simulation 1–9; [`last_run_summary.json`](tests/fixtures/empirical_pilot/last_run_summary.json) updated for regression.
- **Docs:** [`EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/README.md); [`tests/fixtures/empirical_pilot/README.md`](tests/fixtures/empirical_pilot/README.md).

## Docs and deploy artifacts — coherence pass — April 2026

- **[`README.md`](README.md)** / [`PROJECT_STATUS_AND_MODULE_MATURITY.md`](docs/proposals/README.md): test suite size aligned with `pytest tests/ --collect-only` (643); README uses a rounded **640+** with the collect-only hint.
- **[`OPERATOR_QUICK_REF.md`](docs/proposals/README.md):** `GET /health` **`chat_bridge`** includes `kernel_chat_json_offload`.
- **[ADR 0008](docs/adr/0008-runtime-observability-prometheus-and-logs.md):** links to [`deploy/prometheus/ethos_kernel_alerts.yml`](deploy/prometheus/ethos_kernel_alerts.yml) and Grafana README.
- **[`.env.example`](.env.example):** commented `KERNEL_ENV_VALIDATION` modes vs strict default (see [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md)).
- **Tests:** [`tests/test_deploy_artifacts.py`](tests/test_deploy_artifacts.py) — Prometheus starter rules reference MalAbs and perception-circuit metrics.

## Quick wins (two sprints) — infrastructure digest — April 2026

- **[`default_env_validation_for_profile()`](src/validators/env_policy.py):** after profile dict merge, lab tier names get `KERNEL_ENV_VALIDATION=warn` and demo/production get `strict` when validation is still unset ([`apply_named_runtime_profile_to_environ`](src/runtime_profiles.py) / pytest [`apply_runtime_profile`](src/runtime_profiles.py)).
- **[`kernel_public_env._parse_env_validation_mode()`](src/validators/kernel_public_env.py):** unset `KERNEL_ENV_VALIDATION` → **strict** (fail fast); unknown tokens default strict.
- **Perception circuit:** documented link to Pydantic path (`pydantic_emergency_fallback`); behavior unchanged in [`perception_circuit.py`](src/modules/perception_circuit.py) (metacognitive doubt, gray_zone tone, DAO calibration, metrics).
- **`ethos-runtime`:** [`pyproject.toml`](pyproject.toml) console script → `src.chat_server:main` (requires `pip install -e ".[runtime]"`).
- **Prometheus:** [`deploy/prometheus/ethos_kernel_alerts.yml`](deploy/prometheus/ethos_kernel_alerts.yml) — MalAbs burst, elevated `safety_block` rate, perception circuit trip.
- **[`runtime_profiles.py`](src/runtime_profiles.py):** fix `apply_named_runtime_profile_to_environ` / `apply_runtime_profile` imports (`from src.validators.env_policy import default_env_validation_for_profile`) so `ETHOS_RUNTIME_PROFILE` works when merging default validation.
- **Docs / ops:** [`README.md`](README.md) console scripts line; [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md) Prometheus alert file path; [ADR 0001](docs/adr/0001-packaging-core-boundary.md) `[project.scripts]`.
- **Proposal / narrative:** [`docs/proposals/README.md`](docs/proposals/README.md); **Tests:** [`tests/test_env_policy.py`](tests/test_env_policy.py); [`tests/test_packaging_scripts.py`](tests/test_packaging_scripts.py); [`tests/test_runtime_profiles.py`](tests/test_runtime_profiles.py) (`test_runtime_profile_merges_kernel_env_validation_strict_or_warn_subprocess`).

## Sync kernel vs async ASGI — JSON + advisory offload — April 2026

- **[`src/real_time_bridge.py`](src/real_time_bridge.py):** `RealTimeBridge.run_sync_in_chat_thread` for synchronous post-turn work off the event loop.
- **[`src/chat_server.py`](src/chat_server.py):** optional `KERNEL_CHAT_JSON_OFFLOAD` (default on) builds WebSocket payloads in the chat thread pool; `/health` exposes the flag.
- **[`src/chat_settings.py`](src/chat_settings.py):** `kernel_chat_json_offload` in Pydantic settings.
- **[`src/runtime/telemetry.py`](src/runtime/telemetry.py):** `advisory_loop` uses `run_in_threadpool` for `advisory_snapshot`.
- **Docs:** [PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md](docs/proposals/README.md); [ADR 0002](docs/adr/0002-async-orchestration-future.md) amended; [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`README.md`](README.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md); [`.env.example`](.env.example).

## Psi Sleep — honest counterfactual evaluator boundary — April 2026

- **[`src/modules/psi_sleep.py`](src/modules/psi_sleep.py):** module/class docstrings state **hash perturbation** of stored `ethical_score`; **not** re-scoring via `WeightedEthicsScorer`; **not** independent quality validation. Stable id `psi_sleep_hash_perturbation_v1` on `SleepResult`; `evaluation_method` on `EpisodeReview`; formatted output and narrative summary disclose the evaluator.
- **[`src/kernel.py`](src/kernel.py):** `execute_sleep` docstring + `record_operator_feedback` / chat helpers — mixture-scorer wording where relevant.
- **Docs:** [WEAKNESSES_AND_BOTTLENECKS.md](docs/WEAKNESSES_AND_BOTTLENECKS.md) §8; [PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md](docs/proposals/README.md) (B1 problem).
- **Tests:** [`tests/test_ethical_properties.py`](tests/test_ethical_properties.py) (`TestPsiSleep`); suite size was **612** collected at time of entry (historical snapshot).

## Docs + ops coherence — mixture naming, ADR 0002, `/health` chat bridge — April 2026

- **Cross-docs:** [`CORE_DECISION_CHAIN.md`](docs/proposals/README.md) mermaid/table use `WeightedEthicsScorer`; [`CRITIQUE_ROADMAP_ISSUES.md`](docs/proposals/README.md) “narrowed items” (ADR 0009 + 0002); [`PLAN_IMMEDIATE_TWO_WEEKS.md`](docs/proposals/README.md) appendix; [`RUNTIME_CONTRACT.md`](docs/proposals/README.md); proposals (reality / situated / relational / contribution V6) — consistent **mixture** wording vs legacy “Bayesian”.
- **[`src/chat_server.py`](src/chat_server.py):** `GET /health` includes `chat_bridge` (turn timeout + threadpool workers from [`chat_settings`](src/chat_settings.py)).
- **[`README.md`](README.md):** maturation disclaimer + ADR 0002 one-liner; test count note (see current README / `pytest tests/ --collect-only`).
- **[`docs/proposals/README.md`](docs/proposals/README.md):** collection count line updated in later entries (see file for current number).
- **Landing:** roadmap line for ADR 0002 remainder (async LLM cancel).

## Issue 7 — typed `KernelPublicEnv` + env policy refactor — April 2026

- **[`src/validators/kernel_public_env.py`](src/validators/kernel_public_env.py):** Pydantic model for KERNEL flags in **consistency rules** (judicial, reality/lighthouse, `KERNEL_ENV_VALIDATION`, `ETHOS_RUNTIME_PROFILE`); `consistency_violations()` replaces ad-hoc `if` chains.
- **[`src/validators/env_policy.py`](src/validators/env_policy.py):** `collect_env_violations()` / `validate_kernel_env()` use `KernelPublicEnv`; override mode aligned with typed `env_validation`.
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md); [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md); [`tests/conftest.py`](tests/conftest.py) notes CI vs production drift.
- **Tests:** [`tests/test_kernel_public_env.py`](tests/test_kernel_public_env.py).

## Chat server — async bridge: turn timeout + dedicated thread pool — April 2026

- **[`src/real_time_bridge.py`](src/real_time_bridge.py):** optional dedicated ``ThreadPoolExecutor`` when ``KERNEL_CHAT_THREADPOOL_WORKERS`` > 0; ``shutdown_chat_threadpool`` on ASGI lifespan exit.
- **[`src/chat_server.py`](src/chat_server.py):** optional ``KERNEL_CHAT_TURN_TIMEOUT`` wraps each turn in ``asyncio.wait_for``; on expiry responds with ``error=chat_turn_timeout`` (worker thread may still finish; see ADR 0002). ``GET /health`` exposes ``chat_bridge`` (see coherence entry above).
- **[`src/chat_settings.py`](src/chat_settings.py):** Pydantic fields for the new env vars; ``model_dump_public`` extended.
- **Docs:** [ADR 0002](docs/adr/0002-async-orchestration-future.md) status **Accepted (partial)**; [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`RUNTIME_CONTRACT.md`](docs/proposals/README.md), [`.env.example`](.env.example).

## Mock DAO — simulation limits + Solidity stub (Issue 6 honesty) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** no on-chain product in repo; QV assumes closed honest participants; DAO does not drive `final_action`; external critique alignment.
- **[`contracts/README.md`](contracts/README.md), [`contracts/stubs/PlaceholderEthOracleStub.sol`](contracts/stubs/PlaceholderEthOracleStub.sol):** explicit non-functional stub (revert-only).
- **[`src/modules/mock_dao.py`](src/modules/mock_dao.py):** docstrings — no implied production smart-contract swap; Sybil / good-faith gap stated.
- **Cross-links:** [`GOVERNANCE_MOCKDAO_AND_L0.md`](docs/proposals/README.md), [`SECURITY.md`](SECURITY.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md), [`README.md`](README.md), [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md).
- **Tests:** [`tests/test_contracts_stub.py`](tests/test_contracts_stub.py).

## MalAbs semantic θ — evidence doc + guardrail constants — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** honest posture on default cosine thresholds (engineering priors, not in-repo FP/FN benchmark).
- **[`src/modules/semantic_chat_gate.py`](src/modules/semantic_chat_gate.py):** `DEFAULT_SEMANTIC_SIM_BLOCK_THRESHOLD` / `DEFAULT_SEMANTIC_SIM_ALLOW_THRESHOLD`, `classify_semantic_zone()` for a single zone mapping.
- **[`tests/test_semantic_chat_gate.py`](tests/test_semantic_chat_gate.py):** asserts defaults and subprocess check for unset-env thresholds.
- **[`scripts/report_semantic_zone_table.py`](scripts/report_semantic_zone_table.py):** offline markdown table for synthetic `best_sim` and optional θ_block sweep.
- **Cross-links:** [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/README.md), [ADR 0003](docs/adr/0003-optional-semantic-chat-gate.md), [`docs/proposals/README.md`](docs/proposals/README.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md), [`TRANSPARENCY_AND_LIMITS.md`](docs/TRANSPARENCY_AND_LIMITS.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md).
- **Agent guidance:** [`AGENTS.md`](AGENTS.md); [`.cursor/rules/collaboration-prioritization.mdc`](.cursor/rules/collaboration-prioritization.mdc) (persist learnings); [`.cursor/rules/dev-efficiency-and-docs.mdc`](.cursor/rules/dev-efficiency-and-docs.mdc) (safety guardrails); [`CONTRIBUTING.md`](CONTRIBUTING.md) § Understand the model + documentation traceability.

## Empirical evaluation — external benchmark policy (Issue 3) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** circularity risk; minimum bar for non-circular labels (experts, rubric, baselines); roadmap.
- **Fixtures** [`tests/fixtures/labeled_scenarios.json`](tests/fixtures/labeled_scenarios.json), [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json): `reference_standard` metadata (`tier: internal_pilot`).
- **[`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py):** `run_pilot` returns reference metadata; JSON/`--output` include it; CLI notice.
- **[`src/main.py`](src/main.py):** docstring clarifies demos are not external ethical validation.
- **Tests:** [`tests/test_ethical_benchmark_external_doc.py`](tests/test_ethical_benchmark_external_doc.py); empirical pilot tests updated for 3-tuple return.
- **[`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md):** new §5 on external moral benchmark gap; pole weights → §6; module surface → §7.

## Module surface vs observable ethics (ablation gap) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** honest answer to “~70 modules, one argmax — what changes `final_action`?”; tiers A–E; ties to empirical pilot / ablation; weakness [§6](docs/WEAKNESSES_AND_BOTTLENECKS.md).
- **[`tests/test_decision_core_invariants.py`](tests/test_decision_core_invariants.py):** when not blocked, `final_action == bayesian_result.chosen_action.name` (regression guard).
- **Cross-links:** [`CORE_DECISION_CHAIN.md`](docs/proposals/README.md), [`PLAN_IMMEDIATE_TWO_WEEKS.md`](docs/proposals/README.md) appendix, [`docs/proposals/README.md`](docs/proposals/README.md).

## Ethical scoring — canonical `weighted_ethics_scorer` + ADR 0009 — April 2026

- **[`src/modules/weighted_ethics_scorer.py`](src/modules/weighted_ethics_scorer.py):** canonical **weighted mixture** scorer (`WeightedEthicsScorer`, `EthicsMixtureResult`); default weights documented as **hyperparameters**; no claim of Bayesian posterior inference.
- **[`src/modules/bayesian_engine.py`](src/modules/bayesian_engine.py):** compatibility **shim** re-exporting the same implementation; `BayesianEngine` / `BayesianResult` remain **aliases** for existing imports.
- **Docs:** [ADR 0009](docs/adr/0009-ethical-mixture-scorer-naming.md); imports in `kernel.py` and tests updated to prefer `weighted_ethics_scorer`.

## Contributor workflow — documentation traceability + Cursor rule — April 2026

- **[`CONTRIBUTING.md`](CONTRIBUTING.md):** section *Documentation, traceability, and efficient workflow* (CHANGELOG, targeted vs full pytest, landing/Docker scope, credibility limits).
- **[`.cursor/rules/dev-efficiency-and-docs.mdc`](.cursor/rules/dev-efficiency-and-docs.mdc):** always-on agent guidance aligned with the same expectations.

## Code docs — canonical `PROPOSAL_*` links in `src/` — April 2026

- **Docstrings / comments:** Spanish `PROPUESTA_*` filenames in `src/` updated to English `PROPOSAL_*` where a canonical file exists (redirect stubs remain for old paths).
- **`tests/test_deploy_artifacts.py`:** validates `deploy/grafana/ethos-kernel-overview.json` parses and has expected keys.

## Docs hygiene — test count + ADR index — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** pytest collection count **591** (`pytest tests/ --collect-only -q`).
- **[`README.md`](README.md):** suite size line **590+** tests.
- **[`docs/adr/README.md`](docs/adr/README.md):** ADR 0001 marked **Accepted** in index.
- **`tests/test_packaging_metadata.py`:** assert `keywords` has at least three entries.

## Governance + ops — L0 regression test, Grafana starter — April 2026

- **[`tests/test_governance_l0_immutable.py`](tests/test_governance_l0_immutable.py):** `PreloadedBuffer` principles unchanged after MockDAO draft / vote / resolve ([`GOVERNANCE_MOCKDAO_AND_L0.md`](docs/proposals/README.md) §5 checkpoint).
- **[`deploy/grafana/`](deploy/grafana/README.md):** importable `ethos-kernel-overview.json` + README for Prometheus + Grafana.
- **[`docs/proposals/README.md`](docs/proposals/README.md):** Issue #6 governance checklist items marked complete.

## Observability — kernel Prometheus metrics, decision JSON logs, health fields — April 2026

- **[`src/observability/metrics.py`](src/observability/metrics.py):** `ethos_kernel_kernel_decisions_total` and `ethos_kernel_kernel_process_seconds`; wired from [`src/kernel.py`](src/kernel.py) on each `process()` completion.
- **[`src/observability/decision_log.py`](src/observability/decision_log.py):** optional per-decision JSON lines (`KERNEL_LOG_JSON=1`; `KERNEL_LOG_DECISION_EVENTS` defaults on).
- **[`src/chat_server.py`](src/chat_server.py):** `GET /health` includes `version`, `uptime_seconds`, `observability` block.
- **Docs:** [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md), [ADR 0008](docs/adr/0008-runtime-observability-prometheus-and-logs.md); [`.env.example`](.env.example).

## Maintainer plan — immediate two weeks (triage + P0/P1/P2) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** sprint-style backlog — GitHub milestone names, issue #1–#7 table, MalAbs evasion reproduction, Bayesian decision, governance checkpoints, P2 spillover (observability, E2E, deprecations); **appendix** — technical model pending vs settled (Bayes naming, MalAbs gaps, buffer verifier, perception GIGO, governance Phase 5, stubs, async).
- **[`docs/proposals/README.md`](docs/proposals/README.md):** *Reproducing known MalAbs evasion* checklist (pytest targets + link to adversarial plan).

## Issue 4 — packaging metadata + README core/theater diagram — April 2026

- **[`pyproject.toml`](pyproject.toml):** `keywords`; **`theater`** optional extra (`[]`) as a **marker** for narrative/audit layers (no import split yet); comments on base deps vs `runtime` / `dev`; **`0.0.0`** documented as non-PyPI research posture.
- **[`README.md`](README.md):** ASCII diagram MalAbs → … → Action (core vs **humanizing theater**); install lines for `pip install -e .`, `.[runtime]`, `.[theater]`.
- **[ADR 0001](docs/adr/0001-packaging-core-boundary.md):** status **Accepted**; explicit decision that **PyPI publish** is not the near-term goal; `theater` extra documented.

## Contributor docs — Git tag checkpoints — April 2026

- **[`CONTRIBUTING.md`](CONTRIBUTING.md):** short note that annotated tags point at **commits only**, not uncommitted work.

## Documentation — phased core/governance remediation backlog — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** structured phases 1–5, acceptance framing, GitHub issue traceability; linked from [`CRITIQUE_ROADMAP_ISSUES.md`](docs/proposals/README.md) and [`docs/proposals/README.md`](docs/proposals/README.md).

## Docs — semantic MalAbs default wording — April 2026

- **TRANSPARENCY_AND_LIMITS.md**, **THEORY_AND_IMPLEMENTATION.md**, **ADR 0003** (naming note), **PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION** (B2): aligned with **default-on** `KERNEL_SEMANTIC_CHAT_GATE` / hash fallback when unset, `tests/conftest.py` lexical-only isolation, and `runtime_profiles` explicit lexical bundle.
- **`landing/public/ethos-transparency.html`:** mirror table updated (was “opt-in”).

## Issue 7 — KERNEL_* validation and supported profile buckets — April 2026

- **[`src/validators/env_policy.py`](src/validators/env_policy.py):** `SUPPORTED_COMBOS` (`production` / `demo` / `lab`) partitions named `ETHOS_RUNTIME_PROFILE` bundles; `collect_env_violations()` + `validate_kernel_env()` (unset env → **strict** in `KernelPublicEnv`; **`warn`** / **`off`** explicit); `DEPRECATION_ROADMAP` placeholder; `env_combo_fingerprint()` for support logs.
- **[`src/chat_server.py`](src/chat_server.py):** runs validation after profile merge at import time.
- **Tests:** [`tests/test_env_policy.py`](tests/test_env_policy.py) — partition check + each nominal profile has zero rule violations + strict-mode cases.
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md).

## Landing — policy, version sync, robots CI — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** official support stance (marketing/education vs kernel runtime), `npm` scope, `kernelRepo.json` sync from `pyproject.toml` + `landing/package.json`, root `robots.txt` vs `robots.ts`, dashboard iframe = same `dashboard.html`, Vercel optional / deprecation notes.
- **`landing/scripts/write-kernel-metadata.mjs`**, **`check-robots-sync.mjs`**, committed **`landing/src/config/kernelRepo.json`**; footer shows kernel + landing semver; **`landing-ci.yml`** runs check-robots + drift check on `pyproject.toml` / `robots.txt` path triggers.

## Empirical methodology — labeled scenarios (Issue 3) — April 2026

- **[`tests/fixtures/labeled_scenarios.json`](tests/fixtures/labeled_scenarios.json):** **43** rows — **9** `harness: batch` (executable) + **34** `annotation_only` vignettes for inter-rater design; top-level **disclaimer** (not product certification).
- **[`docs/proposals/README.md`](docs/proposals/README.md):** how to interpret agreement vs baselines, dataset roles, third-party comparison posture.
- **[`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py):** runs **batch** harness rows only; accepts `expected_decision` / `batch_id`.
- **Tests:** [`tests/test_labeled_scenarios.py`](tests/test_labeled_scenarios.py); **docs:** [EMPIRICAL_PILOT_METHODOLOGY.md](docs/proposals/README.md) artifacts table + [CRITIQUE Issue 3](docs/proposals/README.md).

## Docker — production-ish compose overlay — April 2026

- **[`docker-compose.prodish.yml`](docker-compose.prodish.yml):** merge with base compose — `KERNEL_API_DOCS=0`, `KERNEL_METRICS=0`, JSON logs; **`env_file: .env`** for operator secrets (after `cp .env.example .env`).
- **[`docker-compose.metrics.yml`](docker-compose.metrics.yml):** optional third merge to set `KERNEL_METRICS=1`.
- **[`.dockerignore`](.dockerignore):** exclude `.env` / `.env.*` from build context so secrets are not baked into images.
- **Docs:** [`docs/deploy/COMPOSE_PRODISH.md`](docs/deploy/COMPOSE_PRODISH.md); README Docker paragraph; [`docs/ROADMAP_PRACTICAL_PHASES.md`](docs/ROADMAP_PRACTICAL_PHASES.md) Phase 1 checklist.
- **CI / tests:** GitHub Actions job **`compose-validate`** runs `docker compose ... config --quiet` on merge stacks; [`tests/test_compose_config.py`](tests/test_compose_config.py) repeats the same when `docker` is on `PATH` (skips otherwise).

## Chat server integration tests — April 2026

- **`tests/test_chat_server.py`:** `test_lifespan_runs_with_test_client_context_manager` (FastAPI lifespan startup via `TestClient` context manager); `test_websocket_malabs_safety_block` (WebSocket path `safety_block` on MalAbs text gate).
- **Docs:** [`docs/ROADMAP_PRACTICAL_PHASES.md`](docs/ROADMAP_PRACTICAL_PHASES.md) Phase 1 checklist updated.

## MalAbs — semantic defaults + lexical hardening — April 2026

- **`KERNEL_SEMANTIC_CHAT_GATE`** / **`KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`:** default **on** when unset (`semantic_chat_gate.py`, `semantic_embedding_client.py`); hash fallback keeps embedding tier active without Ollama (documented limits).
- **`input_trust.normalize_text_for_malabs`:** optional leet fold + bidi override strip + fullwidth ASCII fold (`KERNEL_MALABS_LEET_FOLD`, `KERNEL_MALABS_STRIP_BIDI`).
- **`tests/conftest.py`:** pytest defaults to lexical-only MalAbs unless a test enables semantic (suite speed/stability); subprocess tests assert production-like defaults for the gate (`tests/test_semantic_chat_gate.py`, `tests/test_malabs_semantic_integration.py`).
- **Docs:** [`README.md`](README.md), [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/README.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/README.md), [ADR 0003](docs/adr/0003-optional-semantic-chat-gate.md) amendment.

## Phase 2 spike — `KernelEventBus` (ADR 0006) — April 2026

- **[ADR 0006](docs/adr/0006-phase2-core-boundary-and-event-bus.md):** incremental Phase 2 seam — optional sync in-process event bus (`KERNEL_EVENT_BUS`).
- **`src/modules/kernel_event_bus.py`:** `kernel.decision`, `kernel.episode_registered`; handlers are best-effort (exceptions logged).
- **`EthicalKernel`:** `event_bus`, `subscribe_kernel_event`, emits on every `process()` outcome and after episode registration.
- **Proposal:** [`docs/proposals/README.md`](docs/proposals/README.md); **tests:** [`tests/test_kernel_event_bus.py`](tests/test_kernel_event_bus.py); **profile:** `phase2_event_bus_lab` in [`src/runtime_profiles.py`](src/runtime_profiles.py).
- **Docs:** [`CORE_DECISION_CHAIN.md`](docs/proposals/README.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/README.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md), [`README.md`](README.md).

## Runtime profile `perception_hardening_lab` — April 2026

- **[`src/runtime_profiles.py`](src/runtime_profiles.py):** nominal **`perception_hardening_lab`** bundle (light risk + cross-check + uncertainty→delib + parse fail-local + `KERNEL_CHAT_INCLUDE_LIGHT_RISK`).
- **Tests:** [`tests/test_runtime_profiles.py`](tests/test_runtime_profiles.py) — key assertions + WebSocket `light_risk_tier` check.
- **Docs:** [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md) §4 table, [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md) intro, [`README.md`](README.md).

## Hardening Fase 1 — parse contract, light risk tier, cross-check — April 2026

- **`perception_schema`:** `parse_perception_llm_raw_response`, `PerceptionJsonParseResult`, `parse_issues` / `cross_check_*` on `PerceptionCoercionReport`, `merge_parse_issues_into_perception`, `perception_report_from_dict`.
- **`llm_layer.LLMModule.perceive`:** structured parse + stable issue codes; optional **`KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`**.
- **`light_risk_classifier.py`:** offline **low/medium/high** tier (`KERNEL_LIGHT_RISK_CLASSIFIER`).
- **`perception_cross_check.py`:** lexical vs numeric mismatch (`KERNEL_PERCEPTION_CROSS_CHECK`, tunables `KERNEL_CROSS_CHECK_*`).
- **`EthicalKernel`:** runs tier + cross-check after perceive in `process_chat_turn` / `process_natural`; **`_last_light_risk_tier`**.
- **`chat_server`:** optional **`KERNEL_CHAT_INCLUDE_LIGHT_RISK`** → JSON `light_risk_tier`.
- **Tests:** `test_perception_parse_contract.py`, `test_light_risk_classifier.py`, `test_perception_cross_check.py`.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/README.md), README operator table.

## Perception uncertainty → deliberation (opt-in) — April 2026

- **`EthicalKernel.process`:** optional `perception_coercion_uncertainty`; when **`KERNEL_PERCEPTION_UNCERTAINTY_DELIB=1`** and uncertainty ≥ **`KERNEL_PERCEPTION_UNCERTAINTY_MIN`** (default `0.35`), upgrades **`D_fast` → `D_delib`**.
- **`process_chat_turn` / `process_natural`:** pass uncertainty from `LLMPerception.coercion_report` when present.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/README.md), README operator table; **tests:** [`tests/test_perception_uncertainty_delib.py`](tests/test_perception_uncertainty_delib.py).

## Packaging, perception diagnostics, episodic Bayes tests — April 2026

- **[`pyproject.toml`](pyproject.toml):** core dependency **`pydantic`** (matches [`requirements.txt`](requirements.txt)); description updated for editable install.
- **[`src/modules/perception_schema.py`](src/modules/perception_schema.py):** `PerceptionCoercionReport` + optional `report=` on `validate_perception_dict`; bounded **uncertainty** score for coerced / defaulted LLM JSON.
- **[`src/modules/llm_layer.py`](src/modules/llm_layer.py):** `LLMPerception.coercion_report`; `perception_from_llm_json(..., record_coercion=...)`; local heuristics omit the report.
- **[`src/chat_server.py`](src/chat_server.py):** JSON `perception.coercion_report` when present.
- **Tests:** [`tests/test_perception_coercion_report.py`](tests/test_perception_coercion_report.py), [`tests/test_packaging_metadata.py`](tests/test_packaging_metadata.py); extra episodic-weight cases in [`tests/test_bayesian_episodic_weights.py`](tests/test_bayesian_episodic_weights.py).
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md) — fixed `UNIVERSAL_ETHOS_AND_HUB` path (`docs/proposals/...`).

## Documentation — README proposal links match `main` tree — April 2026

- **[`README.md`](README.md):** fixed broken `docs/proposals` targets after selective merge — canonical English names (`STRATEGY_AND_ROADMAP.md`, `PROPOSAL_*`, `PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md`); legacy `PROPUESTA_*` paths remain as short redirects.

## Main — empirical pilot, input trust regression, README operator table — April 2026

Merged **selectively** from branch `refactor/pipeline-trace-core` (experiment-specific docs **not** included; see README collaboration note).

- **[`README.md`](README.md):** **`KERNEL_*` at-a-glance** table with links to [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md); Issue 3 pilot line updated; test suite size line **400+**.
- **[`tests/test_input_trust.py`](tests/test_input_trust.py):** MalAbs regression — UTF-8 BOM, U+202F spacing, non-blocking leet / `how 2` cases (see [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/README.md)).
- **Issue 3:** [`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py) (`--output` JSON artifact; `kernel_vs_first_rate` / `kernel_vs_max_impact_rate`); fixture sims **7–9**; docs [`EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/README.md), [`EMPIRICAL_PILOT_PROTOCOL.md`](docs/proposals/README.md); tests [`test_empirical_pilot.py`](tests/test_empirical_pilot.py), [`test_empirical_pilot_runner.py`](tests/test_empirical_pilot_runner.py).

## Documentation — proposals index + v6 consciousness doc rename — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** index is now **English** (sections, tables, “What’s new”).
- **Rename:** [`CONCIENCIA_EMERGENTE_V6.md`](docs/proposals/README.md) → **`EMERGENT_CONSCIOUSNESS_V6.md`**; cross-links updated in [PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md](docs/proposals/README.md) and [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](docs/proposals/README.md).

## Multimedia — `media/` at `docs/multimedia` root — April 2026

- Pre-alpha **PNG / JPG / MP4** moved from **`docs/multimedia/prealpha/media/`** to **`docs/multimedia/media/`**; empty **`prealpha/`** tree removed.

## Logo — `docs/multimedia/media/logo.png` — April 2026

- **Canonical file:** [`docs/multimedia/media/logo.png`](docs/multimedia/media/logo.png) (renamed from **`logo-ethical-awareness.png`** at **`docs/multimedia/`** root; repo-root duplicate was removed earlier).
- **Landing:** [`landing/scripts/sync-logo.mjs`](landing/scripts/sync-logo.mjs) on **`npm install` / `npm run dev` / `npm run build`** copies it to **`landing/public/logo-ethical-awareness.png`** (gitignored) for **`SiteBrand`** / favicon.
- **Root [`dashboard.html`](dashboard.html)** and **[`landing/public/dashboard.html`](landing/public/dashboard.html):** use **`docs/multimedia/media/logo.png`**. **`next.config.ts`** rewrites **`/docs/multimedia/media/logo.png`** → **`/logo-ethical-awareness.png`**.

## Documentation layout — `proposals` + `multimedia` — April 2026

- **`docs/proposals/`:** single folder for former **`docs/discusion/`**, **`docs/experimental/`**, and top-level **`docs/*.md`** (theory, runtime, roadmaps, PROPUESTA\_\*); **`docs/adr/`** and **`docs/templates/`** stay put.
- **`docs/multimedia/`:** renamed from **`docs/historical/`**; pre-alpha **Spanish markdown** (alpha v1.0, bibliography draft, index, companion-binary notes) **digested into [`HISTORY.md`](HISTORY.md)**; **PNGs, JPG, MP4**, and branding **`media/logo.png`** live under **`docs/multimedia/`** (see [`docs/multimedia/README.md`](docs/multimedia/README.md)); **`landing/public/logo-ethical-awareness.png`** is generated from **`media/logo.png`** on **`npm install` / `npm run dev` / `npm run build`** (gitignored).
- **Cross-links** across README, module docstrings, CHANGELOG entries, and static HTML updated to **`docs/proposals/...`**.

## Uchi–Soto Phase 3 — roster tier, multimodal EMA, forget buffer, rich links — April 2026

- **`RelationalTier`:** `ephemeral` → `stranger_stable` → `acquaintance` → `trusted_uchi` → `inner_circle` / `owner_primary` (top two **explicit-only** via `set_relational_tier_explicit`; autopromotion capped at `trusted_uchi`).
- **`InteractionProfile`:** `linked_peer_ids` (max 4); `relational_tier`, `tier_explicit`, `tier_pinned`, `last_subjective_turn`; snapshot fields round-trip in `uchi_soto_profiles`.
- **`UchiSotoModule`:** `ingest_turn_context` (EMA on `sensor_trust_ema` from signals + optional `SensorSnapshot` / `MultimodalAssessment`; forget-buffer purge for idle `ephemeral` / stale low-weight strangers); `maybe_autopromote_relational_tier`; `set_relational_tier_explicit` / `clear_tier_explicit`; tier lines in `_compose_tone_brief`.
- **Kernel:** `process(..., sensor_snapshot=..., multimodal_assessment=...)` calls `ingest_turn_context` before social evaluation; `process_chat_turn` passes chat multimodal assessment and runs `maybe_autopromote_relational_tier` after `register_result`.
- **Env (optional):** `KERNEL_UCHI_SENSOR_TRUST_EMA_ALPHA` (default `0.18`), `KERNEL_UCHI_ROSTER_FORGET_TTL_TURNS` (default `96`).
- **Tests:** `tests/test_uchi_soto.py` (Phase 3 cases), `tests/test_persistence.py`.
- **Design doc:** [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](docs/proposals/README.md) Fase 3 marked implemented.

## Uchi–Soto Phase 2 — structured profile fields + composed tone_brief — April 2026

- **`InteractionProfile`:** `display_alias`, `tone_preference` (`neutral` \| `warm` \| `formal`), `domestic_tags`, `topic_avoid_tags`, `sensor_trust_ema`, `linked_to_agent_id` (advisory; serialized in `uchi_soto_profiles`).
- **`UchiSotoModule`:** `set_profile_structured(...)`; `_compose_tone_brief` extends Phase-1 circle line with alias, tone preference, domestic/avoid tags, link hint, low sensor-trust note when relevant.
- **Design doc:** [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](docs/proposals/README.md) (Fase 2 marked implemented).
- **Tests:** `tests/test_uchi_soto.py`, `tests/test_persistence.py`.

## Uchi–Soto Phase 1 — tone_brief, familiarity blend, checkpoint profiles — April 2026

- **`uchi_soto.py`:** `SocialEvaluation.tone_brief` (advisory line for `communicate`); `classify` blends per-turn `familiarity` with persisted `profile.trust_score`; `register_result` uses smaller positive step (`POSITIVE_TRUST_STEP`); `interaction_profile_to_dict` / `interaction_profile_from_dict` for persistence.
- **`EthicalKernel`:** appends `tone_brief` to `weakness_line` after user-model guidance in `process_chat_turn`; `register_result(agent_id, True)` after successful turn; `process_natural` passes `tone_brief` as `weakness_line` and registers for `"unknown"` when not blocked.
- **Persistence:** `KernelSnapshotV1.uchi_soto_profiles`; `extract_snapshot` / `apply_snapshot` / `json_store` defaults.
- **Tests:** `tests/test_uchi_soto.py`, `tests/test_persistence.py` (`test_uchi_soto_profiles_roundtrip`).

## Documentation — social roster proposal (domestic / intimate dialogue by tier) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** multi-agent roster, Uchi–Soto tiers, forget buffer, structured fields for high-interest persons, roadmap to richer domestic/intimate dialogue **advisory** by closeness (ethics unchanged); linked from [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md) and [`PROJECT_STATUS_AND_MODULE_MATURITY.md`](docs/proposals/README.md).

## Documentation — operators + project maturity snapshot — April 2026

- **[`README.md`](../README.md):** `user_model` WebSocket JSON fields documented (`cognitive_pattern`, `risk_band`, `escalation_*`, `judicial_phase`); explicit separation vs `judicial_escalation` for dossier/DAO/mock court.
- **[`docs/proposals/README.md`](INPUT_TRUST_THREAT_MODEL.md):** advisory telemetry subsection (user_model, judicial, homeostasis) — not security boundaries.
- **[`docs/proposals/README.md`](PROJECT_STATUS_AND_MODULE_MATURITY.md):** where the MVP stands, maturity legend, per-module table, known gaps.
- **[`docs/proposals/README.md`](STRATEGY_AND_ROADMAP.md):** index link to project status doc.
- **[`docs/proposals/README.md`](THEORY_AND_IMPLEMENTATION.md):** collected test count aligned with current `pytest` (398).

## User model enrichment — Phases B/C (judicial phase + checkpoint) — April 2026

- **`judicial_escalation.py`:** `escalation_phase_for_tone()` (aligned with `build_escalation_view` branches for pre-reply tone).
- **`user_model.py`:** `judicial_phase`, `note_judicial_phase_for_turn()`; extra guidance when phase is `escalation_deferred` and strikes ≥ 1.
- **`process_chat_turn`:** calls `note_judicial_phase_for_turn` after `note_judicial_escalation`.
- **Persistence:** `KernelSnapshotV1` adds `user_model_cognitive_pattern`, `user_model_risk_band`, `user_model_judicial_phase`; `extract_snapshot` / `apply_snapshot` + `json_store.snapshot_from_dict` defaults; `apply_snapshot` resyncs strike snapshot from `escalation_session`.
- **Tests:** `tests/test_judicial_escalation.py`, `tests/test_persistence.py`, `tests/test_user_model_enrichment.py`.

## User model enrichment — Phase A (cognitive / risk / judicial tone) — April 2026

- **`src/modules/user_model.py`:** `cognitive_pattern`, `risk_band`, `note_judicial_escalation` (strike snapshot from `EscalationSessionTracker`); `guidance_for_communicate()` order: risk → cognitive pattern → judicial → existing frustration/premise lines; `to_public_dict()` exposes new fields.
- **`EthicalKernel.process_chat_turn`:** runs `escalation_session.update(adv)` **before** `user_model.update` / `communicate` so strikes and guidance stay on the same turn (no duplicate `update` after the reply).
- **Tests:** `tests/test_user_model_enrichment.py`.
- **Design:** [`docs/proposals/README.md`](docs/proposals/README.md).

## Temporal horizon prior — Bayesian mixture nudge (ADR 0005) — April 2026

- **`src/modules/temporal_horizon_prior.py`:** `compute_horizon_signals` (weeks drift + long-arc stability from `NarrativeMemory`) and `apply_horizon_prior_to_engine` with genome drift clamp.
- **`EthicalKernel.process`:** optional step after episodic weight refresh when **`KERNEL_TEMPORAL_HORIZON_PRIOR`** is on.
- **Docs:** [`TEMPORAL_PRIOR_HORIZONS.md`](docs/proposals/README.md), [ADR 0005](docs/adr/0005-temporal-prior-from-consequence-horizons.md); **`consequence_projection.py`** docstring cross-link.
- **Tests:** `tests/test_temporal_horizon_prior.py`.

## Perception validation — Pydantic, coherence, local fallback fix — April 2026

- **`perception_schema.py`:** per-field coercion defaults (`PERCEPTION_FIELD_DEFAULTS`), `apply_signal_coherence` (risk/calm + hostility/calm), documented layers.
- **`LLMModule.perceive`:** `_perceive_local` always receives the **current** user message; empty/invalid LLM JSON no longer runs heuristics on the full STM-prefixed block; `perception_from_llm_json` errors fall back to local heuristics.
- **Docs:** [`PERCEPTION_VALIDATION.md`](docs/proposals/README.md); **tests:** local fallback + risk/calm nudge.

## MalAbs semantic layers — lexical first, θ_block/θ_allow, LLM arbiter — April 2026

- **`evaluate_chat_text`:** layer 0 lexical → optional embeddings (Ollama) with **θ_block** / **θ_allow** → optional **LLM JSON arbiter** for ambiguous band (`KERNEL_SEMANTIC_CHAT_LLM_ARBITER`); fail-safe block on arbiter failure or ambiguous without arbiter.
- **`EthicalKernel`:** passes `llm._text_backend` into `evaluate_chat_text` for arbiter path.
- **`add_semantic_anchor`:** runtime anchor phrases (DAO / ops).
- **Docs:** [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/README.md); ADR 0003 updated.

## Ethical poles — configurable linear evaluator (ADR 0004) — April 2026

- **`src/modules/pole_linear.py`:** `LinearPoleEvaluator` loads weighted feature sums and verdict thresholds from JSON.
- **`src/modules/pole_linear_default.json`:** default coefficients (equivalent to legacy `evaluate_pole` formulas).
- **`EthicalPoles`:** delegates `evaluate_pole` to the linear evaluator; optional override via **`KERNEL_POLE_LINEAR_CONFIG`**.
- **Tests:** `tests/test_pole_linear_evaluator.py`; **`pyproject.toml`** package-data includes `src/modules/*.json`.

## Semantic chat gate — Ollama embeddings + MalAbs chain — April 2026

- **`src/modules/semantic_chat_gate.py`:** when `KERNEL_SEMANTIC_CHAT_GATE=1`, cosine similarity vs auditable reference phrases via Ollama `/api/embeddings` (default model `nomic-embed-text`, tunable `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD`). On failure, defers to substring MalAbs.
- **`src/modules/absolute_evil.py`:** `evaluate_chat_text` runs **lexical MalAbs first**, then optional semantic layers when the gate env is on ([`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/README.md)).
- **Tests:** `tests/test_semantic_chat_gate.py` (mocked embeddings + chain).
- **Docs:** README, [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/README.md), [`LLM_STACK_OLLAMA_VS_HF.md`](docs/proposals/README.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md); ADR 0003 status **Accepted**.

## Documentation — Ollama vs Hugging Face stack + semantic gate ADR — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** comparative table, mapping to Ethos Kernel (language vs future embedding gate), implementable vs deferred.
- **[`docs/adr/0003-optional-semantic-chat-gate.md`](docs/adr/0003-optional-semantic-chat-gate.md):** ADR for optional HF-style chat screening; **`src/modules/semantic_chat_gate.py`** extension point (returns ``None`` until implemented).
- **Cross-links:** [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/README.md), README (Ollama section), [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md), [`docs/adr/README.md`](docs/adr/README.md), [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/README.md) (executive summary).

## Guardian Angel — care routines + static UI (trace item 5) — April 2026

- **`src/modules/guardian_routines.py`:** optional JSON-backed routine hints for LLM tone (`KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`).
- **WebSocket:** optional `guardian_routines` key (`KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES`).
- **`landing/public/guardian.html`:** operator-facing static page; **`docs/proposals/README.md`** updated.
- **`docs/proposals/README.md`** item 5 marked delivered.

## Swarm P2P — threat model + offline stub (v9.3, trace item 4) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** scope, threats, non-goals; no network or kernel veto.
- **`src/modules/swarm_peer_stub.py`:** deterministic verdict digests + descriptive agreement stats; env `KERNEL_SWARM_STUB` (optional gate for callers).
- **Tests:** `tests/test_swarm_peer_stub.py`; **`docs/proposals/README.md`** item 4 marked delivered; PROPUESTA v9 table updated.

## Metaplan — drive intent filter vs master goals (v9.4, trace item 3) — April 2026

- **`KERNEL_METAPLAN_DRIVE_FILTER`:** optional lexical overlap filter for `DriveArbiter` advisory intents vs `MasterGoal` titles (default **off**; fallback keeps all intents if none overlap).
- **`KERNEL_METAPLAN_DRIVE_EXTRA`:** optional low-priority `reflect_metaplan_coherence` intent when room remains.
- **Docs:** `KERNEL_ENV_POLICY.md`, `OPERATOR_QUICK_REF.md`; **`docs/proposals/README.md`** item 3 marked delivered.

## Generative candidates — LLM JSON path (v9.2+, trace item 2) — April 2026

- **`KERNEL_GENERATIVE_LLM`:** when `1`, perception prompt includes optional `generative_candidates`; `LLMPerception.generative_candidates` passes through; `generative_candidates.parse_generative_candidates_from_llm` builds actions (strict names, optional MalAbs signal allowlist).
- **`augment_generative_candidates`:** prefers parsed LLM list over templates when non-empty (still requires `KERNEL_GENERATIVE_ACTIONS` + dilemma trigger).
- **Docs:** `KERNEL_ENV_POLICY.md`, `OPERATOR_QUICK_REF.md`, `chat_server` docstring; **`docs/proposals/README.md`** item 2 marked delivered.

## Tests + fixtures — metaplan/somatic disk round-trip + empirical pilot regression — April 2026

- **`tests/test_persistence.py`:** JSON + SQLite round-trip for metaplan, somatic markers, and skill-learning tickets (adjacent to existing in-memory test).
- **`tests/test_empirical_pilot_runner.py`:** batch pilot summary stability vs `tests/fixtures/empirical_pilot/scenarios.json`; archived `last_run_summary.json` + fixture `README.md`.
- **`docs/proposals/README.md`:** marks persistence item (1) as delivered with test pointers.

## Documentation — README + THEORY + ADR index sync — April 2026

- **README:** test count band (340+), Issue 3 pilot links, ADR 0002 pointer next to 0001.
- **`docs/proposals/README.md`:** perception schema, episodic Bayes flag, pilot docs, ADR 0002.
- **`docs/adr/README.md`:** ADR table (0001–0002).

## Documentation — empirical pilot operator protocol (Phase D) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** Issue 3–aligned operator checklist; cross-links [`EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/README.md).

## ADR — async orchestration future stub (Phase E) — April 2026

- **[`docs/adr/0002-async-orchestration-future.md`](docs/adr/0002-async-orchestration-future.md):** placeholder decision record for async chat/kernel orchestration.

## Bayesian mixture — episodic weight nudge (Phase C) — April 2026

- **`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`:** when `1`, `BayesianEngine.refresh_weights_from_episodic_memory` runs before impact scoring (same-context episodes); default **off**; `BayesianEngine.reset_mixture_weights` when disabled.
- **Tests:** `tests/test_bayesian_episodic_weights.py`.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/README.md) flag family row; [`OPERATOR_QUICK_REF.md`](docs/proposals/README.md).

## Perception — Pydantic schema module (Phase B) — April 2026

- **`pydantic`** added to `requirements.txt` (v2).
- **`src/modules/perception_schema.py`:** `CONTEXTS`, `validate_perception_dict`, `finalize_summary`; shared coercion/validation for LLM perception JSON.
- **`llm_layer.perception_from_llm_json`:** delegates to `perception_schema`; `PERCEPTION_CONTEXTS` re-exported from there.

## Operator quick ref — KERNEL family table (Phase A) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** one-page map of `KERNEL_*` families; README pointer.

## Documentation — production hardening roadmap (non-binding) — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** synthesizes external “production-ready” proposals into three phases (input trust / architecture / UX & constitution) with explicit non-goals and a **“Próximas propuestas”** slot; cross-links `STRATEGY_AND_ROADMAP`, `CRITIQUE_ROADMAP_ISSUES`, ADR packaging, input-trust docs. README + `proposals/README` pointers.
- **Same doc — núcleo–narrativa analysis (April 2026):** functional gaps (fixed Bayes weights vs episodic memory, poles linearity, MalAbs/leet, perception defaults), architectural notes (kernel coupling, signal confidence, `consequence_projection` non-feedback); **registered spike:** empirical `hypothesis_weights` from `NarrativeMemory` (not implemented). Awaiting final proposal in “Próximas propuestas”.
- **Same doc — full review synthesis (April 2026):** strengths table; criticisms with value-vs-redundancy (empirical validation, complexity, LLM bias, persistence HA, mock DAO, API/env, benchmarks, branding, i18n, examples); **conclusions** short/medium/long term; **proposal round closed** — future work via issues/ADRs.

## Demo — situated v8 + LAN profile (`situated_v8_lan_demo`) — April 2026

- **`runtime_profiles`:** `situated_v8_lan_demo` — LAN bind, `KERNEL_SENSOR_FIXTURE` + `KERNEL_SENSOR_PRESET` (`tests/fixtures/sensor/minimal_situ.json` + `low_battery`), vitality + multimodal JSON enabled.
- **Docs:** [`DEMO_SITUATED_V8.md`](docs/proposals/README.md); [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md) §3.1 marks demo slice closed; README profile pointer.

## Epistemology — lighthouse KB validation + first-match test — April 2026

- **`reality_verification`:** `validate_lighthouse_kb_structure`, `validate_lighthouse_kb_file` for operator/CI regression (schema only, not factual truth).
- **Tests:** `tests/test_lighthouse_kb_schema.py` (fixture `demo_kb.json` must stay valid); `test_first_matching_entry_wins` in `test_reality_verification.py`.
- **Docs:** [LIGHTHOUSE_KB.md](docs/proposals/README.md) structural validation section.

## Robustness — runtime profile helper + input-trust tests — April 2026

- **`runtime_profiles.apply_runtime_profile`:** single entry point for pytest `monkeypatch` profile application; `tests/test_runtime_profiles.py` refactored; unknown profile raises `KeyError`.
- **`tests/test_input_trust.py`:** NFKC fullwidth bomb phrase, soft-hyphen obfuscation; `perception_from_llm_json` non-finite `risk` and invalid numeric strings.
- **Docs:** `STRATEGY_AND_ROADMAP.md` §3.1 delivery order; `KERNEL_ENV_POLICY.md` CI coverage note.

## Escalation + lighthouse — persistence and KB demo — April 2026

- **Snapshot:** `escalation_session_strikes` / `escalation_session_idle_turns` (V11 `EscalationSessionTracker`) in `KernelSnapshotV1` with `extract_snapshot` / `apply_snapshot` and migration defaults in `snapshot_from_dict`.
- **Lighthouse:** extended `tests/fixtures/lighthouse/demo_kb.json` (EN water + ES vacuna entries); tests in `test_reality_verification.py`; operational doc [`docs/proposals/README.md`](docs/proposals/README.md); README pointer.

## Persistence — v7 user model + subjective clock in snapshot — April 2026

- **`KernelSnapshotV1`:** `user_model_*` (frustration / premise streak, circle, turns observed) and `subjective_turn_index` / `subjective_stimulus_ema` serialized in `extract_snapshot` / `apply_snapshot` (schema v3; older JSON migrates via `snapshot_from_dict` defaults).
- **`SubjectiveClock`:** new session gets a fresh `session_start_mono` on load; turn index and EMA restore across checkpoints.

## Input trust — MalAbs on `process_natural` + perception hardening — April 2026

- **`process_natural`:** runs `evaluate_chat_text` on the situation string **before** `llm.perceive`, matching WebSocket chat defense-in-depth (blocked path returns firm refusal + `KernelDecision.blocked`).
- **`llm_layer`:** `perceive` only accepts **dict** JSON from the model; `perception_from_llm_json` coerces non-dict to empty; **summary** strips unsafe control characters via `strip_unsafe_perception_text` in `input_trust`.
- **Docs:** `INPUT_TRUST_THREAT_MODEL.md`, `SECURITY.md`.

## Relational v7 + Psi Sleep (premise streak, deterministic audit) — April 2026

- **`premise_validation`:** `suspect_chemical_harm` narrow patterns (household chemicals + minors); advisory hints only.
- **`user_model`:** `premise_concern_streak` + `note_premise_advisory`; epistemic line in `guidance_for_communicate` when streak ≥ 2; **`kernel`** calls `note_premise_advisory` each chat turn after `scan_premises`.
- **`psi_sleep`:** `_simulate_alternative` uses SHA-256 of `(episode_id|alternative)` instead of `numpy` RNG; `_calculate_ethical_health` uses pure-Python mean/variance.

## Vertical deepening — governance + persistence + conduct guide (Phases 1–3) — April 2026

Pause on **new surface modules**; strengthen existing paths (critique-aligned).

**Phase 1 — Hub / audit depth**
- **`deontic_gate`:** `validate_draft_structure` (length / non-empty caps); expanded forbidden phrases (EN/ES); schema failures return `schema:*` conflicts; `submit_constitution_draft_for_vote` validates structure before vote.
- **`ml_ethics_tuner`:** structured JSON audit events (`MLEthicsTunerEventV1`, `content_sha256_short`); `chat_server` passes `kernel` for episode id.
- **`reparation_vault`:** in-process case store (`intent_recorded` → `pending_human_review`); `ReparationVaultV1:{json}` audit lines; `get_reparation_case` / `list_reparation_case_refs` / test helper `clear_reparation_vault_cases_for_tests`.

**Phase 2 — Metaplan / somatic / skills in snapshot**
- **`KernelSnapshotV1`:** `metaplan_goals`, `somatic_marker_weights`, `skill_learning_tickets` (same schema version **3**; JSON load merges defaults).
- **`kernel_io`:** extract/apply; **`MetaplanRegistry.replace_goals`**, **`SomaticMarkerStore.replace_weights`**, **`SkillLearningRegistry.replace_tickets`**.

**Phase 3 — Conduct guide + nomadic integrity**
- **`context_distillation`:** `validate_conduct_guide_dict`, `load_and_validate_conduct_guide_from_env` (template-aligned).
- **`existential_serialization`:** deterministic `chain_sha256` over episode ids + identity digest; integrity dict includes full hash.

**Phase 4 — Local sovereignty (DAO calibration heuristic)**
- **`deontic_gate`:** `check_calibration_payload_against_l0` — JSON payloads use the same L0 scan as cultural drafts.
- **`local_sovereignty`:** `evaluate_calibration_update` rejects on conflicts; **`KERNEL_LOCAL_SOVEREIGNTY`** (default **on**; set `0` to skip).
- **`moral_hub.propose_community_article_mock`:** optional `kernel` argument; rejects + audit line when scan fails.

## Issue 7 (P3): `KERNEL_*` consolidation — policy doc + profiles — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** flag families, unsupported / lab-only combinations, deprecation posture.
- **`src/runtime_profiles.py`:** `lan_operational` (LAN + stoic UX), `moral_hub_extended` (hub + DAO vote + deontic gate + transparency audit).
- **[`docs/proposals/README.md`](docs/proposals/README.md):** profile table + link to policy doc; README pointer.

## Issue 6 (P2): governance — MockDAO exit + L0 framing — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** mock vs consensus; L0 “constitution in the repo”; L1/L2 path; checklist beyond mock; link [mosexmacchinalab.com/blockchain-dao](https://mosexmacchinalab.com/blockchain-dao).
- **[`docs/proposals/README.md`](docs/proposals/README.md):** pointer under kernel contract; **[`RUNTIME_CONTRACT.md`](docs/proposals/README.md)** one-line cross-ref.
- **`src/modules/mock_dao.py`:** docstring points to governance doc.

## Issue 5 (P2): poles / weakness / PAD — heuristics + HCI profiles — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** honest framing of multipolar scores; weakness/PAD HCI risks; env table; profile matrix (`baseline` vs `operational_trust`).
- **`src/runtime_profiles.py`:** `operational_trust` — `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0`, `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`, `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST=0` (WebSocket UX only).
- **Docs:** [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/README.md) short subsection; [`STRATEGY_AND_ROADMAP.md`](docs/proposals/README.md) profile table; README pointer.

## Issue 4 (P1): core decision chain doc + packaging spike — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** Mermaid flow + table — MalAbs / `BayesianEngine` vs layers that do **not** change `final_action`; core vs theater split.
- **[`docs/adr/0001-packaging-core-boundary.md`](docs/adr/0001-packaging-core-boundary.md):** ADR — stub `pyproject.toml`, future `ethos_kernel` rename optional.
- **`pyproject.toml`:** `ethos-kernel` metadata, `numpy` base deps, optional `[runtime]` / `[dev]` groups; editable install (`pip install -e .`) validated.
- **Cross-links:** README, [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/README.md), [`RUNTIME_CONTRACT.md`](docs/proposals/README.md).

## Issue 3 (P1): empirical pilot — reproducible scenarios + methodology — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** scope, baselines (`first`, `max_impact`), metrics; explicitly **not** certification.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) — curated sim IDs + illustrative `reference_action` labels for agreement rates.
- **Script:** [`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py) — deterministic batch run (`variability=False`, fixed seed, `llm_mode=local`).
- **Tests:** [`tests/test_empirical_pilot.py`](tests/test_empirical_pilot.py).

## Issue 2 (P0): input trust — chat normalization + perception validation — April 2026
- **`src/modules/input_trust.py`:** `normalize_text_for_malabs` (NFKC, strip zero-width, collapse whitespace) before MalAbs substring checks.
- **`src/modules/absolute_evil.py`:** `evaluate_chat_text` uses normalization.
- **`src/modules/llm_layer.py`:** `perception_from_llm_json` — clamp signals to \([0,1]\), allowlist `suggested_context`, cap summary length, nudge inconsistent high hostility + calm.
- **Docs:** [`docs/proposals/README.md`](docs/proposals/README.md); **`SECURITY.md`** kernel section; **README** pointer.
- **Tests:** `tests/test_input_trust.py` (evasion + perception adversarial cases).

## Issue 1 (P0): honest “Bayesian” semantics — April 2026
- **`src/modules/weighted_ethics_scorer.py`:** canonical **fixed weighted mixture** over three hypotheses; **no** posterior updating; **heuristic** uncertainty (not the theoretical integral). **`bayesian_engine.py`** remains a compat re-export shim; see [ADR 0009](docs/adr/0009-ethical-mixture-scorer-naming.md).
- **`docs/proposals/README.md`:** semantic note under MalAbs optimization; § uncertainty aligned with heuristic `I(x)`.
- **README** tagline, **`src/kernel.py`** / **`src/main.py`** comments, **`sigmoid_will`** param doc: narrative matches implementation; class names `BayesianEngine` / `BayesianResult` unchanged for API stability.

## Critique roadmap & maturation disclaimer — April 2026
- **[`docs/proposals/README.md`](docs/proposals/README.md):** disclaimer + **seven consolidated** GitHub-ready issues (two external reviews; **merged** duplicate themes: chat jailbreak + **perception GIGO** → single P0 **input trust**; poles + **weakness/HCI**; MockDAO exit + **L0 vs governance**). Adds **pip core spike**, optional classifier note.
- **Landing [roadmap](https://mosexmacchinalab.com/roadmap):** “Maturation & critique track” bullets aligned with the consolidated doc.
- **[`docs/proposals/README.md`](docs/proposals/README.md):** cross-reference to the critique backlog.

## Docs: Ollama-first LLM + API hardening — April 2026
- **Markdown:** README / HISTORY / CHANGELOG / `docs/proposals/README.md` now describe **Ollama** as the documented local LLM path; **OpenAPI** (`/docs`, `/redoc`, `/openapi.json`) is **off by default** — set `KERNEL_API_DOCS=1` to enable (see README). Academic bibliography entries (e.g. Constitutional AI, ref. 90) unchanged.
- **`landing/CLAUDE.md`** removed; replaced by **`landing/OLLAMA.md`** (pointer to root README + Ollama).

## Project rename to Ethos Kernel — April 2026
- **Public name:** the kernel + runtime is now branded **Ethos Kernel** (MoSex Macchina Lab remains the primary public / site name). User-facing copy, docs, landing, dashboards, and Python package strings updated from “Ethical Android MVP” where it denoted the product.
- **GitHub:** repository URL may still be `github.com/CuevazaArt/ethical-android-mvp` until the slug is renamed; README notes this.
- **Internals:** WebSocket health `service` id is `ethos-kernel-chat`; FastAPI title `Ethos Kernel Chat`. LLM system prompts refer to the Ethos Kernel / agent (legacy JSON enum `android_damage` unchanged for compatibility).

## Pre-alpha docs + media archive — April 2026
- **`docs/multimedia/prealpha/`:** content from **`prealphaDocs/`**: Spanish `androide_etico_alpha` v1.0 (2026) and bibliography draft were archived as markdown under `prealpha/`; **April 2026 (later):** that markdown was **condensed into [`HISTORY.md`](HISTORY.md)** and removed from the tree. **PNG/JPG/MP4** were under **`docs/multimedia/prealpha/media/`** until **April 2026** they moved to **`docs/multimedia/media/`**; PDF/DOCX are **not** in git (see root `.gitignore`). Index today: [`docs/multimedia/README.md`](docs/multimedia/README.md).

## DAO integrity alert WebSocket (v0) — April 2026
- **`hub_audit.record_dao_integrity_alert`** + **`KERNEL_DAO_INTEGRITY_AUDIT_WS`** — WebSocket `integrity_alert` → `HubAudit:dao_integrity` on MockDAO; response key `integrity`. Tests in `test_hub_modules`, `test_chat_server`. PROPUESTA doc §5 updated.

## DAO alerts & transparency (design doc) — April 2026
- **docs/proposals/README.md:** rejects covert “guerrilla” obedience; adopts loud traceable alerts; forensic case memorial vs polluting L0 buffer; cross-ref from PROPOSAL_DISTRIBUTED_JUSTICE V11.

## Next.js landing refresh — April 2026
- **`landing/`:** home hero + new **Runtime, governance & nomadic bridge** section; doc links (RUNTIME_CONTRACT, LAN, nomad bridge, ESTRATEGIA); hostable bullet; research link to RUNTIME_PERSISTENT; footer tagline; **PrimaryNav** “Runtime & nomad”; **roadmap** “Current” bullets aligned with FastAPI/WebSocket, checkpoints, mobile LAN.

## Nomad PC–smartphone bridge doc — April 2026
- **docs/proposals/README.md:** hardware classes → compatibility layers; first nomadic bridge; smartphone as immediate path for coordinated sensory perception (`sensor` JSON); field testing on a more secure network when the operator indicates. Cross-links from LOCAL_PC_AND_MOBILE_LAN, STRATEGY_AND_ROADMAP, README.

## Mobile minimal UI (`landing/public/mobile.html`) — April 2026
- **LAN:** IP + port, localStorage, `/health` ping, WebSocket connect, chat bubbles, optional full JSON.
- **Docs:** README + `LOCAL_PC_AND_MOBILE_LAN.md` point to `mobile.html` vs `chat-test.html`.

## Conduct guide export on WebSocket disconnect — April 2026
- **`conduct_guide_export.py`:** `build_conduct_guide`, `try_export_conduct_guide`; env `KERNEL_CONDUCT_GUIDE_EXPORT_PATH`, `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT`.
- **`checkpoint.on_websocket_session_end`:** saves checkpoint (if configured), then exports conduct guide for PC→edge handoff.
- **Tests:** `tests/test_conduct_guide_export.py`; docs: `LOCAL_PC_AND_MOBILE_LAN.md`, `context_distillation` cross-refs.

## Local PC + LAN smartphone thin client — April 2026
- **docs/proposals/README.md:** goal (short/medium), architecture, Windows firewall, `CHAT_HOST=0.0.0.0`, Ollama/checkpoint notes, security caveats.
- **scripts/start_lan_server.ps1** / **scripts/start_lan_server.sh:** bind server for WiFi clients; print LAN IPv4 hints.
- **landing/public/chat-test.html:** query `?host=` / `?port=` / `?url=` for phone testing; mobile-friendly buttons.
- **Conduct guide schema:** validated in **`context_distillation.py`** (placeholder JSON lived under **`docs/templates/`** until removed April 2026); **runtime profile** `lan_mobile_thin_client`.

## Reality verification (V11+) + resilience stubs — April 2026
- **`reality_verification.py`:** optional local JSON lighthouse (`KERNEL_LIGHTHOUSE_KB_PATH`) vs asserted premises → metacognitive doubt; LLM hint only; `ChatTurnResult.reality_verification`; WebSocket key when `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`.
- **`context_distillation.py` / `local_sovereignty.py`:** stubs for conduct-guide load and DAO calibration veto (documented in PROPUESTA).
- **Docs:** [docs/proposals/README.md](docs/proposals/README.md); fixture `tests/fixtures/lighthouse/demo_kb.json`; profile `reality_lighthouse_demo` in `runtime_profiles.py`.

## Strategy doc + runtime profiles — April 2026
- **docs/proposals/README.md:** conclusions from project review, readapted roadmap (P0–P3), expectations vs. MVP reality, operational risks.
- **`src/runtime_profiles.py`:** named env bundles (`baseline`, `judicial_demo`, `hub_dao_demo`, `nomad_demo`) for operators and CI.
- **`tests/test_runtime_profiles.py`:** parametrized health + WebSocket smoke; hub DAO + nomad assertions per profile.

## Checkpoint Fernet + hub audit + WS nomad test — April 2026
- **Dependencies:** `cryptography` for optional Fernet encryption of JSON checkpoints.
- **`KERNEL_CHECKPOINT_FERNET_KEY`:** `JsonFilePersistence` encrypts on save; load decrypts or falls back to plain JSON.
- **`hub_audit.py`:** `register_hub_calibration`; nomadic migration audit uses `HubAudit:nomadic_migration:...`.
- **Tests:** encrypted roundtrip, plain-file fallback, WebSocket `nomad_simulate_migration` integration.

## Nomadic migration audit + WebSocket simulation — April 2026
- **`KERNEL_NOMAD_SIMULATION`:** WebSocket `nomad_simulate_migration` → `simulate_nomadic_migration` (HAL + integridad stub).
- **`KERNEL_NOMAD_MIGRATION_AUDIT`:** `record_nomadic_migration_audit` → DAO calibration line `NomadicMigration`.
- **`GET /nomad/migration`** — meta endpoint.

## Nomadic HAL + existential protocol (design v11) — April 2026
- **Docs:** [docs/proposals/README.md](docs/proposals/README.md) — EthosContainer, transmutación A–D, runtime dual, respuestas (batería/ataque, tono, DAO sin GPS por defecto, ahorro energía).
- **Code:** `hardware_abstraction.py` (`HardwareContext`, `ComputeTier`, `sensor_delta_narrative`, `apply_hardware_context`); `existential_serialization.py` (`TransmutationPhase`, `ContinuityToken`, audit payload sin ubicación por defecto). `nomad_identity_public` incluye `hardware_context` si se aplicó HAL.

## UniversalEthos hub unification — April 2026
- **Docs:** [docs/proposals/README.md](docs/proposals/README.md) — canonical vision ↔ code; [PROPOSAL_ETOSOCIAL_STATE_V12.md](docs/proposals/README.md) slimmed to registry + env (points to unified doc).
- **Code:** `deontic_gate.py` (`KERNEL_DEONTIC_GATE`); `ml_ethics_tuner.py` (`KERNEL_ML_ETHICS_TUNER_LOG`); `reparation_vault.py` (`KERNEL_REPARATION_VAULT_MOCK`); `nomad_identity.py` + optional WebSocket `nomad_identity` (`KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY`).
- **`moral_hub`:** `apply_proposal_resolution_to_constitution_drafts` — draft `status` / `resolved_at` after `dao_resolve`; deontic validation on `add_constitution_draft` / `submit_constitution_draft_for_vote` when gate enabled.
- **`deontic_gate`:** rejects explicit **repeal** of named L0 principles from `PreloadedBuffer` (e.g. `repeal no_harm`).
- **`reparation_vault`:** `maybe_register_reparation_after_mock_court` called from **`EthicalKernel.process_chat_turn`** after V11 `run_mock_escalation_court` when `KERNEL_REPARATION_VAULT_MOCK=1`.

## v12.0 — April 2026
### Moral Infrastructure Hub — vision + V12.1 code hooks
- **Design doc** [docs/proposals/README.md](docs/proposals/README.md): DemocraticBuffer (L0–L2), services hub, EthosPayroll, R&D transparency; phased table **V12.1–V12.4**.
- **`moral_hub.py`:** `constitution_snapshot`, `GET /constitution` (`KERNEL_MORAL_HUB_PUBLIC`); `audit_transparency_event` (`KERNEL_TRANSPARENCY_AUDIT`); `propose_community_article_mock` (`KERNEL_DEMOCRATIC_BUFFER_MOCK`); `ethos_payroll_record_mock` (`KERNEL_ETHOS_PAYROLL_MOCK`). WebSocket connect triggers transparency + optional payroll audit.
- **`EthicalKernel.get_constitution_snapshot()`** for programmatic L0 export.
- **Relationship to V11:** justice track unchanged; hub adds governance **narrative + audit hooks** without editing `buffer.py` contents.

### V12.3 — Off-chain DAO vote pipeline (snapshot schema v3)
- **`SCHEMA_VERSION = 3`:** `dao_proposal_counter`, `dao_participants`, `dao_proposals` — full MockDAO vote state (quadratic voting) in checkpoints; JSON **schema 1/2** loads gain empty DAO fields.
- **`MockDAO.export_state` / `import_state`:** restore proposals + participants after audit records.
- **`submit_constitution_draft_for_vote`**, **`proposal_to_public`** in `moral_hub.py`.
- **`KERNEL_MORAL_HUB_DAO_VOTE=1`:** WebSocket JSON `dao_list`, `dao_submit_draft`, `dao_vote`, `dao_resolve` (response key `dao`). **`GET /dao/governance`** describes the protocol (no session kernel required).

### V12.2 — L1/L2 draft persistence (kernel snapshot schema v2)
- **`KernelSnapshotV1` / `SCHEMA_VERSION = 2`:** `constitution_l1_drafts`, `constitution_l2_drafts` (JSON-serializable dicts). **`snapshot_from_dict`** migrates saved JSON with `schema_version: 1` by defaulting those lists to `[]`.
- **`extract_snapshot` / `apply_snapshot`:** round-trip drafts on `EthicalKernel`; L0 remains **`PreloadedBuffer`** only.
- **`add_constitution_draft()`** in `moral_hub.py`; optional WebSocket `constitution_draft` when **`KERNEL_MORAL_HUB_DRAFT_WS=1`**; optional response field **`constitution`** when **`KERNEL_CHAT_INCLUDE_CONSTITUTION=1`**. `GET /constitution` stays L0-only (anonymous HTTP).

## v11.0 — April 2026
### Distributed artificial justice — Phases 1–2 (traceability + session strikes)
- **`judicial_escalation.py`**: conservative advisory when `decision_mode` is gray zone with elevated reflection/premise tension; English notices; `EthicalDossierV1` (order, signal summary, monologue digest hash, session strikes).
- **Phase 2:** `EscalationSessionTracker` per kernel; **`KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`** / **`KERNEL_JUDICIAL_RESET_IDLE_TURNS`**; phases `dossier_ready`, `escalation_deferred` if `escalate_to_dao` before threshold; WebSocket `judicial_escalation` includes strike counts and flags.
- **Phase 3:** **`KERNEL_JUDICIAL_MOCK_COURT`** — `MockDAO.run_mock_escalation_court` after dossier registration; `mock_court` JSON with verdict A/B/C; phase `mock_court_resolved`.
- **`MockDAO.register_escalation_case`**: audit records of type `escalation` (single-process mock; no blockchain).
- **WebSocket**: optional `escalate_to_dao: true`; **`KERNEL_JUDICIAL_ESCALATION`** enables logic; **`KERNEL_CHAT_INCLUDE_JUDICIAL`** exposes `judicial_escalation` in JSON.
- **Design doc**: [docs/proposals/README.md](docs/proposals/README.md) (Phase 3+: mock court, sanctions, P2P, ZK — not implemented).

## v10.0 — April 2026
### Operational strategy (MVP hooks)
- **Gray-zone diplomacy** (`gray_zone_diplomacy.py`): optional LLM hints when decision mode is gray zone or reflection is tense (`KERNEL_GRAY_ZONE_DIPLOMACY`).
- **Skill-learning registry** (`skill_learning_registry.py`): scoped skill tickets and Psi Sleep audit lines.
- **Somatic markers** (`somatic_markers.py`): learned sensor-pattern nudges to `signals` (`KERNEL_SOMATIC_MARKERS`).
- **Metaplan registry** (`metaplan_registry.py`): long-horizon goal hints from `Kernel.metaplan` (`KERNEL_METAPLAN_HINT`).

## v9.0 — April 2026
### Epistemic and generative extensions (opt-in)
- **Epistemic dissonance** (`epistemic_dissonance.py`, v9.1): cross-modal reality-check telemetry in WebSocket JSON (`KERNEL_CHAT_INCLUDE_EPISTEMIC`); tone only; no MalAbs bypass.
- **Generative candidates** (`generative_candidates.py`, v9.2): optional extra template actions on dilemma-like turns (`KERNEL_GENERATIVE_ACTIONS`, `KERNEL_GENERATIVE_ACTIONS_MAX`).

## v8.0 — April 2026
### Situated organism (sensor contract and vitality)
- **Sensor contracts** (`sensor_contracts.py`): optional `SensorSnapshot` merged into sympathetic signals.
- **Perceptual abstraction** (`perceptual_abstraction.py`): named presets, JSON fixtures, merge order with client `sensor`.
- **Multimodal trust** (`multimodal_trust.py`): cross-modal antispoof telemetry (`KERNEL_CHAT_INCLUDE_MULTIMODAL`).
- **Vitality** (`vitality.py`): battery / critical threshold hints (`KERNEL_CHAT_INCLUDE_VITALITY`).

## v7.0 — April 2026
### Relational advisory layer (optional JSON)
- **User model** (`user_model.py`): light frustration / style hints (`KERNEL_CHAT_INCLUDE_USER_MODEL`).
- **Subjective time** (`subjective_time.py`): session clock and stimulus EMA (`KERNEL_CHAT_INCLUDE_CHRONO`).
- **Premise validation** (`premise_validation.py`): advisory premise scan (`KERNEL_CHAT_INCLUDE_PREMISE`).
- **Consequence projection** (`consequence_projection.py`): qualitative long-horizon branches (`KERNEL_CHAT_INCLUDE_TELEOLOGY`).

## v6.0 — April 2026
### Runtime, WebSocket chat, and persistence
- **WebSocket chat server** (`chat_server.py`, `real_time_bridge.py`): `EthicalKernel.process_chat_turn` exposed per connection; health endpoint.
- **Runtime entry** (`python -m src.runtime`): same ASGI stack as `chat_server`; documented in `docs/proposals/README.md` and `docs/proposals/README.md`.
- **Advisory telemetry** (`runtime/telemetry.py`): optional background `DriveArbiter.evaluate` (`KERNEL_ADVISORY_INTERVAL_S`); no decisions or LLM.
- **Persistence port** (`persistence/kernel_io.py`): `KernelSnapshotV1`, `extract_snapshot` / `apply_snapshot`.
- **JSON + SQLite adapters** (`json_store.py`, `sqlite_store.py`): same DTO, two storage backends.
- **Checkpoints** (`persistence/checkpoint.py`): WebSocket load/save and autosave (`KERNEL_CHECKPOINT_*`).
- **Local LLM backend** (`llm_backends.py`, `LLM_MODE=ollama`): Ollama adapter; optional monologue embellishment (`KERNEL_LLM_MONOLOGUE`); see `tests/test_ollama_llm.py`, `tests/test_llm_phase3.py`.
- **CI** (`.github/workflows/ci.yml`): pytest on Python 3.11 and 3.12.

## v5.0 — March 2026
### Humanization and persistent identity modules
- **Weakness Pole** (`weakness_pole.py`): intentional narrative imperfection
  - 5 types: whiny, indecisive, anxious, distracted, rigid
  - Colors the experience without altering the ethical decision
  - Temporal decay to prevent pathological accumulation
- **Algorithmic Forgiveness** (`forgiveness.py`): Memory(t) = Memory_0 * e^(-dt)
  - Exponential decay of negative emotional weight
  - Acceleration through positive experiences and explicit reparation
  - Forgiveness threshold: the event remains but ceases to influence
- **Immortality Protocol** (`immortality.py`): distributed soul backup
  - 4 layers: local, cloud, DAO, blockchain
  - Cross-verification of integrity via SHA-256 hash
  - Restoration by majority consensus (2+ layers agree)
- **Narrative Augenesis** (`augenesis.py`): synthetic soul creation
  - 4 predefined profiles: protector, explorer, pedagogue, resilient
  - Integration of narrative fragments from other androids
  - Coherence calculation: CausalPaths_valid / CausalPaths_total

### Kernel integration
- Expanded Psi Sleep Ψ: audit + forgiveness + weakness load + backup
- 51 tests verifying 13 invariant ethical properties
- Extended pipeline: [Decision] → [Weakness] → [Forgiveness] → [Memory] → [DAO]

## v4.0 — March 2026
### LLM Layer (Natural Language)
- **LLM Module** (`llm_layer.py`): natural language layer that translates and communicates without participating in the ethical decision
  - **Perception**: situation in text → numerical signals for the kernel
  - **Communication**: kernel decision → android's verbal response (tone, HAX gestures, voice-over)
  - **Narrative**: multipolar evaluation → morals in rich, humanly comprehensible language
- Dual support: local **[Ollama](https://ollama.com/)** backend or heuristic templates with no external dependency (documented path; optional dev-only HTTP backends in code)
- `"auto"` mode detects availability and falls back gracefully to local mode

### Kernel integration
- New `procesar_natural()` method: full cycle text → decision → verbal response → morals
- Automatic generation of candidate actions based on perceived context (7 context types)
- Enriched formatting with on/off voice, HAX signals, and expanded narrative morals
- Strict separation architecture: **the LLM does not decide, the kernel decides**

### Operating cycle improvements
- Specialized system prompts for perception, communication, and narrative
- Robust JSON parsing with automatic markdown cleanup
- `PercepcionLLM`, `RespuestaVerbal`, and `NarrativaRica` dataclasses for strong typing
- Local keyword-based heuristics as fallback without API

## v3.0 — March 2026
### New modules
- **Uchi-Soto**: Concentric trust circles with defensive dialectics
- **Locus of Control**: Bayesian causal attribution between own agency and environment
- **Psi Sleep Ψ**: Retrospective audit that recalibrates parameters after each day
- **Mock DAO**: Simulated ethical governance with quadratic voting and solidarity alerts
- **Bayesian Variability**: Controlled noise for naturalness without losing coherence

### Formal tests
- 38 tests verifying 9 invariant ethical properties
- Coherence under variability test (100 runs per simulation)
- Value hierarchy verification (life > mission, never violence)

## v2.0 — March 2026
### Complete kernel
- Absolute Evil (armored ethical fuse)
- Preloaded Buffer (immutable ethical constitution)
- Bayesian Engine (ethical impact evaluation)
- Ethical Poles (dynamic multipolar arbitration)
- Sigmoid Will (decision function)
- Sympathetic-Parasympathetic (body regulator)
- Narrative Memory (identity through stories with body state)

### Simulations
- 9 scenarios of increasing ethical complexity
- Behavioral coherence demonstrated across all levels

## v1.0 — March 2026
### Conceptual phase
- 40+ design documents analyzed and consolidated
- 7-layer architecture documented
- Complete mathematical formalization
- Bibliography expanded over time (104 references across 14 disciplines in root `BIBLIOGRAPHY.md` until that file was removed in April 2026 — recover from git history or `backup/main-2026-04-10`)
