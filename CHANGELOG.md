# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

## Antigravity — Validation Pulse & Somatic-Vision Integration — April 2026

### Antigravity Team Updates (April 2026)

### [Planificación: Desmonolitización de Kernel.py] - 2026-04-16
#### Changed
- Rediseño drástico del roadmap (`PLAN_WORK_DISTRIBUTION_TREE.md` y `PROPOSAL_LLM_VERTICAL_ROADMAP.md`) tras identificar debilidades estructurales severas (P0) en el runtime asíncrono y la inflación de gobernanza simulada.
- Adopción de la **Directiva Paridad 75/25 de L0**: Limitando el TDD rígido a un 25% para concentrarse agresivamente en resolución pragmática de vulnerabilidades.
- Presentación de **Arquitectura de Lóbulos/Hemisferios** para separar el frontend perceptivo asíncrono (`httpx.AsyncClient`) del modelo de decisión matemática sincrónico.

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
- **Somatic Infrastructure (Module S5):** Fully implemented the Somatic Profile integration. 

## Claude — Phase 3+ Reward Modeling, Governance & Audit — April 2026

### Claude Team Updates

- **RLHF Reward Modeling (`src/modules/rlhf_reward_model.py`)**: Implemented full RLHF pipeline for controlled fine-tuning. Feature extraction (5D: embedding similarity, lexical score, perception confidence, ambiguity flag, category ID) from MalAbs evaluation artifacts. Logistic regression `RewardModel` with gradient descent training, predict/save/load support. `RLHFPipeline` orchestrates training, JSONL example persistence, and model management. 36 tests passing.
- **Multi-Realm Governance (`src/modules/multi_realm_governance.py`)**: Enabled decentralized per-realm (DAO/team/context) governance over MalAbs semantic gate thresholds (θ_allow, θ_block) and RLHF parameters. `RealmThresholdConfig` enforces hard constraints at all times. `ThresholdProposal` + `MultiRealmGovernor` enable reputation-weighted voting with configurable consensus threshold. Immutable audit trail per realm. 28 tests passing.
- **External Audit Framework (`src/modules/external_audit_framework.py`)**: Comprehensive security audit trail management with hash-linked tamper-evident logs (SHA-256 chain). `SecurityFinding` tracks vulnerabilities with severity/resolution lifecycle. `AuditReport` generates signed snapshots with attestation hash. `ExternalAuditFramework` manages findings, reports, compliance checklist, and log retention. 25 tests passing.
- **Test Suite**: 89 new tests across three modules; full suite 824 passed, 4 skipped (no regressions). Continuous audit (`verify_collaboration_invariants.py`) passes.
