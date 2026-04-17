# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

[URGENTE - BROADCAST A TODOS LOS L2 MASTERS]: Todos los equipos (Claude, Cursor, Copilot) deben hacer un GIT PULL urgente desde MAIN hacia sus MASTERs. Las ramas desactualizadas enfrentarán asincronías severas en el pathing de documentación.

## Cursor — Integration merge (April 2026)

### Cursor Team Updates
- **L1-SUPREMACY-01 compliance:** `AGENTS.md` restored to match `origin/main` — Level 2 must not modify the governance entry file without L0/L1 authorization ([`.cursor/rules/l1-supremacy-and-audit.mdc`](.cursor/rules/l1-supremacy-and-audit.mdc)). Pointers such as **MER V2** remain available at [`docs/collaboration/MER_V2_POSTULATE.md`](docs/collaboration/MER_V2_POSTULATE.md); burst-cancel smoke script: [`scripts/eval/run_burst_cancel_smoke.py`](scripts/eval/run_burst_cancel_smoke.py).
- **Collaboration audit DX:** [`scripts/eval/verify_collaboration_invariants.py`](scripts/eval/verify_collaboration_invariants.py) lists **git-tracked** files via `git ls-files` for merge-marker scans (fast; ignores `node_modules` and other untracked trees); optional `rglob` fallback skips virtualenvs, caches, and nested `ethical-android-mvp-feature-*` copies.
- **Deploy verification:** [`docs/deploy/COMPOSE_PRODISH.md`](docs/deploy/COMPOSE_PRODISH.md) checklist step **3 (Health)** documents optional **`nomad_bridge`** on **`GET /health`** for prodish / LAN operators.
- **HTTP API reference:** Added canonical [`docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) (fixes `AGENTS.md` / operator link target) with **`GET /health` → `nomad_bridge`** and archive cross-links; archive copy points to canonical.
- **Operator traceability:** Documented **`KERNEL_NOMAD_TELEMETRY_VITALITY`** and **`KERNEL_CHAT_INCLUDE_TRANSPARENCY_S10`** in [`docs/ENV_VAR_CATALOG.md`](docs/ENV_VAR_CATALOG.md); short operator subsection in [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md); §1 flag-family rows in [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md). [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) regression list aligned with `scripts/eval/run_cursor_integration_gate.py` (S10, Nomad S.1, vitality).
- **Nomad → Vitality (Module S.2.1):** Latest Nomad ``telemetry`` is mirrored thread-safely in **`NomadBridge.peek_latest_telemetry()`**; **`vitality.merge_nomad_telemetry_into_snapshot`** backfills missing sensor fields before **`assess_vitality`**. Opt out with ``KERNEL_NOMAD_TELEMETRY_VITALITY=0``. Tests: **`tests/test_vitality.py`** (also listed in **`scripts/eval/run_cursor_integration_gate.py`**).
- **Nomad LAN bridge (Module S.1):** Hardened **`src/modules/nomad_bridge.py`** — English contract docstring, safe base64 decode, **`public_queue_stats()`** for operators (`nomad_bridge_queue_stats_v2`: queue depths plus **`latest_telemetry_present`** / **`latest_telemetry_keys`** — key names only, no sensor values); same object exposed under **`GET /health`** as **`nomad_bridge`** for dashboards; extended **`tests/test_nomad_bridge_stream.py`** (vision/audio queue assertions). Cursor integration gate includes this file.
- **Embodied sociability S10 (L1 directive):** Implemented **`src/modules/transparency_s10.py`** for blocks **S10.1** (action narration / explainability), **S10.2** (withdrawal / non-intervention + client privacy hints), **S10.3** (discomfort index + throttle hint), and **S10.4** (operator help-request codes). WebSocket payloads include optional **`transparency_s10`** when `KERNEL_CHAT_INCLUDE_TRANSPARENCY_S10` is on (default on). Tests: `tests/test_transparency_s10.py` (also listed in **`scripts/eval/run_cursor_integration_gate.py`**). Design reference: `docs/archive_v1-7/proposals/PROPOSAL_EMBODIED_SOCIABILITY.md` (Bloque S10).
- **`merge(integration):`** Merged `origin/master-antigravity` into `master-Cursor` (conflict resolution favored L1 where needed). Restored **governance / MalAbs proposal** files under `docs/proposals/` that the L1 merge had removed: `CORE_DECISION_CHAIN.md`, `GOVERNANCE_MOCKDAO_AND_L0.md`, `MOCK_DAO_SIMULATION_LIMITS.md`, `PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md` (tests reference these paths). **`MER_V2_POSTULATE.md`** and MER V2 links in `AGENTS.md` / `CONTRIBUTING.md` retained.
- **Persistence & salience hardening:** Repaired SQLite transaction blocks in [`src/persistence/narrative_storage.py`](src/persistence/narrative_storage.py) (`save_identity_digest`, `save_arc`, `prune_mundane`, `delete_episode`) — correct `with conn:` bodies, explicit `conn.commit()`, and `return` outside the context manager where needed. [`src/modules/salience_map.py`](src/modules/salience_map.py): stable `AXIS_ORDER` typing, uniform attention fallback when raw scores sum to ~0 (`1/len(AXIS_ORDER)`). [`tests/test_temporal_planning.py`](tests/test_temporal_planning.py): `VitalityAssessment` constructor aligned with seven-field vitality model.
- **Nomad telemetry aliases (Module S.2.1):** [`normalize_nomad_telemetry_for_sensor_merge()`](src/modules/vitality.py) maps LAN/mobile shorthand (`battery`, `battery_pct`, `core_temperature_c`, `jerk`, …) onto [`SensorSnapshot`](src/modules/sensor_contracts.py) keys before merge; battery values in **(1, 100]** are treated as legacy percent so they are not clamped to `1.0` by `from_dict`. Doc touch: [`src/modules/nomad_bridge.py`](src/modules/nomad_bridge.py) contract. Tests in [`tests/test_vitality.py`](tests/test_vitality.py).
- **Nomad bridge payload caps (Module S.1):** [`max_vision_frame_bytes()`](src/modules/nomad_bridge.py) / [`max_audio_pcm_bytes()`](src/modules/nomad_bridge.py) enforce **`KERNEL_NOMAD_MAX_VISION_FRAME_BYTES`** (default 5 MiB) and **`KERNEL_NOMAD_MAX_AUDIO_PCM_BYTES`** (default 1 MiB) with a base64 length pre-check so oversized LAN payloads are skipped before decode. Catalog: [`docs/ENV_VAR_CATALOG.md`](docs/ENV_VAR_CATALOG.md) §11; [`.env.example`](.env.example). Tests: [`tests/test_nomad_bridge_stream.py`](tests/test_nomad_bridge_stream.py).

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
