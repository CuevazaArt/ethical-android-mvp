# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

[URGENTE - BROADCAST A TODOS LOS L2 MASTERS]: Todos los equipos (Claude, Cursor, Copilot) deben hacer un GIT PULL urgente desde MAIN hacia sus MASTERs. Las ramas desactualizadas enfrentarán asincronías severas en el pathing de documentación.

## Documentation — Issue #1 (Bayesian naming honesty) — April 2026

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
- **Lobe Extraction & Somatic Subconscious (2026-04-17):**
  - **Full Desmonolitization:** Extracted Stages 0-5 from `kernel.py` into specialized lobes: `PerceptiveLobe`, `LimbicEthicalLobe`, `ExecutiveLobe`, `CerebellumLobe`, and `MemoryLobe`.
  - **Memory Lobe Expansion:** Absorbed `SelectiveAmnesia` and `ImmortalityProtocol` triggers into `MemoryLobe`, removing cyclic dependencies on the main kernel object.
  - **Somatic Subconscious:** Implemented `CerebellumNode` as a high-frequency (100Hz) background thread for hardware polling (battery, thermal). Enabled hardware-level interrupts that trigger a synthetic `AbsoluteEvil` block during somatic trauma.
  - **Asymmetric Anxiety:** Integrated somatic state feedback into the `LimbicLobe`. Critical hardware states now negatively influence relational tension, simulating irritability in high-stress physical conditions.
- **Integration Pulse (2026-04-16):** Successfully synchronized `master-antigravity` with latest updates from all team hubs (`master-Cursor`, `master-claude`, `master-visualStudio`).
  - Resolved conflicts in `vision_adapter.py` and `vision_capture.py` to preserve device-aware initialization.
  - Consolidated **LAN Governance** (frontier witness, replay sidecar) with **Situated Vision**, **Somatic Infrastructure**, and **Reward Modeling**.
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
- **Multi-Realm Governance (`src/modules/multi_realm_governance.py`)**: Enabled decentralized per-realm (DAO/team/context) governance over MalAbs semantic gate thresholds (θ_allow, θ_block) and RLHF parameters. `RealmThresholdConfig` enforces hard constraints at all times. `ThresholdProposal` + `MultiRealmGovernor` enable reputation-weighted voting with configurable consensus threshold. Immutable audit trail per realm. 28 tests passing.
- **External Audit Framework (`src/modules/external_audit_framework.py`)**: Comprehensive security audit trail management with hash-linked tamper-evident logs (SHA-256 chain). `SecurityFinding` tracks vulnerabilities with severity/resolution lifecycle. `AuditReport` generates signed snapshots with attestation hash. `ExternalAuditFramework` manages findings, reports, compliance checklist, and log retention. 25 tests passing.
- **Test Suite**: 89 new tests across three modules; full suite 824 passed, 4 skipped (no regressions). Continuous audit (`verify_collaboration_invariants.py`) passes.
- **Integration**: Merged via `claude/upbeat-jepsen` → `master-claude`. Governance files authored under L1 co-authority (Claude + Antigravity per `collaboration-rule-authority.mdc`).

## Antigravity — Cybersecurity Consolidation & Integration Pulse — April 2026
