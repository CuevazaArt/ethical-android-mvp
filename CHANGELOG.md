# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

## Antigravity — Validation Pulse & Somatic-Vision Integration — April 2026

### Antigravity Team Updates (April 2026)

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

### [v1.1-alpha-swarm] - 2026-04-16
#### Added
- **Governance Reform:** Antigravity promoted to Sole Operational Leader (Level 1); Claude reclassified as Level 2 Executing Unit.
- **Módulo 6: Swarm Ethics & peer-to-peer Governance (I1-I7)**.
- Implementado `FrontierWitnessManager` para verificación sensorial distribuida.
- Implementado `SwarmOracle` para persistencia de reputación LAN cross-session.
- Expandido `SwarmNegotiator` con sistema de votación para zonas grises.
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
