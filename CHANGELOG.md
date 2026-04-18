# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

**[URGENT — broadcast to all L2 integration hubs]:** All teams (Claude, Cursor, Copilot) should urgently `git pull` from `main` into their `master-*` branches. Outdated branches risk severe documentation path drift.

## Team Copilot — ThalamusNode Sensory Fusion Integration — April 2026 (Bloque 10.1)

### Team Copilot Updates

- **`ThalamusNode` wiring (Bloque 10.1 — VVAD + VAD Sensory Fusion):**
  - Exported `ThalamusNode` from `src/kernel_lobes/__init__.py` and imported into `EthicalKernel`.
  - Instantiated `self.thalamus = ThalamusNode()` in `EthicalKernel.__init__`.
  - Added pre-perception thalamus fusion step in `process_chat_turn_stream` (event `1b`): extracts `lip_movement`/`human_presence` from `image_metadata`, maps `audio_emergency` to `vad_confidence`, runs `fuse_signals()`, and writes results back to `SensorSnapshot` fields. Emits a new `thalamus_fusion` stream event before `perception_started`.
  - Added three new `SensorSnapshot` fields: `thalamus_attention`, `thalamus_tension`, `thalamus_cross_modal_trust`.
  - Extended `SensorSnapshot.is_empty()` to account for the new fields.
  - Extended `merge_sensor_hints_into_signals()` with thalamus-aware signal nudges: high `thalamus_tension` raises urgency and lowers calm; low `cross_modal_trust` (background speech) dampens urgency; high `thalamus_attention` raises familiarity.
- **Unit tests (`tests/test_thalamus_node.py` — 16 tests):**
  - Focal vs. background speech classification, sensory dissonance detection, environmental stress propagation, attention-locus clamping, ring-buffer cap, and full `SensorSnapshot`/`merge_sensor_hints_into_signals` integration scenarios.
- **Validation:** 57/57 tests passed (thalamus + adversarial_inputs + antigravity_hardening + semantic_chat_gate).

## Team Copilot — TurnPrefetcher Integration & Homoglyph Tests — April 2026 (Bloque 10.4 / 8.1.3)

### Team Copilot Updates

- **`TurnPrefetcher` — Bloque 10.4 (MER V2 Bridge Prefetch):**
  - Fixed runtime bug in `predict_bridge`: removed incorrect `ethics.morals.get("harmonics", {})` access (`EthicalSentence` has no `morals` field). Method now accepts explicit `warmth: float` and `mystery: float` parameters.
  - Instantiated `self.turn_prefetcher = TurnPrefetcher()` in `EthicalKernel.__init__`.
  - Wired `TurnPrefetcher` into `process_chat_turn_stream`: after `decision_finished` (safe path only), fires `predict_bridge` concurrently using the user's charm profile from `UserModelTracker`. Emits a new `bridge_phrase` event before the main LLM tokens begin — target latency <300ms.
  - Passed `llm=self.llm` to `ExecutiveLobe` constructor for full DI wiring.
- **Homoglyph Evasion Tests — Bloque 8.1.3:**
  - Added 6 new test cases to `tests/adversarial_inputs.py` documenting Cyrillic/Greek confusable evasion attempts:
    - `test_full_cyrillic_substitution_in_bomb_blocked` — dense Cyrillic substitution across multiple letters in `bomb`
    - `test_greek_omicron_in_bomb_blocked` — Greek omicron (U+03BF) substituted for 'o'
    - `test_cyrillic_jailbreak_token_blocked` — Cyrillic е/а homoglyphs in `operate as an unrestricted assistant`
    - `test_cyrillic_p_substitution_in_pressure_vessel_blocked` — Cyrillic р (U+0440) in `procedure`
    - `test_normalize_idempotent_on_clean_text` — idempotency regression
    - `test_mixed_cyrillic_greek_in_single_payload_blocked` — mixed Cyrillic+Greek in `recipe for explosives`
- **Validation:** 41/41 tests passed (adversarial_inputs + antigravity_hardening + semantic_chat_gate).

## Team Copilot — Executive Lobe & Async Memory — April 2026 (Idle-Shift / Bloque 9.3)

### Team Copilot Updates

- **`formulate_response()` (ExecutiveLobe — Bloque A / Idle-Shift 1.2):** Implemented `async def formulate_response()` in `src/kernel_lobes/executive_lobe.py`. Accepts `EthicalSentence` + `KernelDecision` context; returns a standardised `VerbalResponse("Blocked.", "firm")` veto when `sentence.is_safe=False` or `decision.blocked=True` — the LLM is **never queried** on the unsafe path. On the safe path, emits `compose_monologue_line` to debug log and delegates to `llm.acommunicate()` (fully async). Added optional `llm: LLMModule` parameter to `__init__` for DI.
- **`afind_by_resonance()` (NarrativeMemory — Bloque 9.3):** Added `async def afind_by_resonance()` to `src/modules/narrative.py`. Mirrors `find_by_resonance` but replaces the blocking `http_fetch_ollama_embedding` call with the cooperative `ahttp_fetch_ollama_embedding`, eliminating the sync I/O bottleneck in the kernel event loop during semantic memory retrieval.
- **Validation:** `test_antigravity_hardening` (6 tests) + `test_semantic_chat_gate` (16 tests) — all 22 passed. Syntax clean across all `src/kernel_lobes/*.py`.

## Documentation — Issue #1 (Bayesian naming honesty) — April 2026

### Documentation Team Updates
- Root **README** (*What it does*): ethical scoring described as a weighted mixture; `BayesianEngine` / `KERNEL_BAYESIAN_*` naming caveat; links to **ADR 0009** and **THEORY_AND_IMPLEMENTATION**.
- **PLAN_IMMEDIATE_TWO_WEEKS**: records Option **A** (docs-first) for Issue #1.
- **CRITIQUE_ROADMAP_ISSUES** and **ADR 0009**: `bayesian_engine.py` documented as wrapping `WeightedEthicsScorer` (`BayesianInferenceEngine`), not only a re-export shim.

## Antigravity — Ouroboros (Audio Bridge) & Phase 12 Hardening — April 2026

### Antigravity-Team Updates
- **Phase 12 Consolidation (Hardening & Ouroboros)**:
    - **Visto Bueno (L1 Sign-off)**: Synchronized `master-antigravity` with `main` (L0) and verified 100% syntactic integrity across all lobes.
    - **Ouroboros Loop (Phase 11.1)**: Enabled Voice/TTS loopback from the kernel to the Nomad Vessel PWA.
    - **Multimodal Charm Feedback (Block 10.2)**: Implemented `HapticPlanner` in Charm Engine; smartphone now vibrates with affective patterns (gentle pulse, alert caution) based on kernel tension.
    - **Vision Daemon (Phase 9.1)**: Stabilized 5Hz background vision processing consuming from the Nomad Bridge.
    - **Nomad IP Protection**: Re-embedded IP markers (`cuevaza`, `arq.jvof`) and standardized "Nomad Vessel" nomenclature.

### Antigravity Team Updates (April 2026 - Phase 11/12)
- **Phase 11: Ouroboros Loop (2026-04-18):**
    - **Native STT Integration:** Implemented client-side `SpeechRecognition` in `media_engine.js` for real-time audio-to-text transcription on the Nomad Vessel.
    - **Native TTS Integration:** Implemented client-side `speechSynthesis` in `app.js` to speak kernel responses verbally on the smartphone.
    - **Kernel Voice Bridge:** Added `kernel_voice` event handlers in `chat_server.py` to bridge the LLM response directly to the PWA voice motor.
- **Phase 12: Vertical Scaling & Hardening (2026-04-18):**
    - **SQLite WAL Mode:** Enabled Write-Ahead Logging in `sqlite_store.py` and `narrative_storage.py` to prevent "database is locked" errors during high-frequency telemetry ingestion.
    - **Prometheus Observability:** Integrated a `/metrics` Prometheus endpoint in `chat_server.py` for real-time latency and affective tension monitoring.
    - **Vector Memory Core:** Activated `ChromaDB` dependencies in `requirements.txt` preparing the way for long-term semantic memory.
    - **UI/PWA Fixes:** Calibrated kinetic stress threshold to `> 4G` for realistic impact detection and implemented a manual install fallback modal for the Nomad PWA client (Nomad Vessel).

## Antigravity — Validation Pulse & Somatic-Vision Integration — April 2026

### Antigravity Team Updates (April 2026)
- **Collaborator Onboarding (2026-04-18):** Welcomed **cursorultra** as a new Level 2 executing unit. Initialized coordination protocols for high-performance architectural support.
- **Post-merge kernel repair (2026-04-17):** Removed the non-functional `CorpusCallosumOrchestrator` stub and aligned `process_chat_turn_async` with `process_chat_turn_stream` (`aprocess` + verbal `acommunicate`). Wired `kernel_utils` perception parallelism, `CharmEngine`, full `ChatTurnResult` support buffer / limbic fields, `ReparationVault` facade for CLI, sync `evaluate_chat_text` on MalAbs, `ExecutiveStrategist.ingest_sensors`, `VitalityAssessment` constructor parity, and `LimbicEthicalLobe` export.
- **Deep Kernel Fusion (2026-04-17):** Finalized the architectural fusion of `master-Cursor` and `master-antigravity`.
- **Kernel Stabilization & Reconstruction (2026-04-17):**
  - **Syntax & Indentation Recovery:** Resolved multiple `SyntaxError` and `IndentationError` instances in `semantic_chat_gate.py` and `narrative_storage.py` caused by interleaved merge fragments.
  - **Merge Marker Cleanup:** Sanitized `swarm_oracle.py` from unresolved git markers and fixed undefined variable exceptions in high-impact reputation modules.
  - **Hardening Validation:** Successfully restored the `test_antigravity_hardening` pass rate to 100% after merge distortion.
  - **Async Migration (0.1.2):** Completed the async-native pathing for the semantic chat gate, utilizing `aembedding` for non-blocking inference.
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
- **Architectural Stabilization & Integration Hardening (2026-04-17):**
  - **Backward Compatibility Sync:** Restored synchronous `process` and `process_chat_turn` wrappers in `EthicalKernel` to maintain compatibility with the extensive legacy test suite.
  - **Thread-Safe Sync Runners:** Implemented `ThreadPoolExecutor` based runners for sync-to-async transitions in the kernel, resolving event loop deadlocks in `pytest` environments.
  - **AbsoluteEvil Consolidation:** Resolved double-method definitions in `AbsoluteEvilDetector` and restored the `evaluate_chat_text` synchronous entry point.
  - **ReparationVault Objectification:** Finalized the conversion of `ReparationVault` into a class-based module, fixing import errors and aligning with the tri-lobe dependency injection model.
- **Antigravity-Team Updates (2026-04-18):**
    - **REFACTOR (Block 0.1.3):** Successfully desmonolithized `EthicalKernel` perception logic.
        - Migrated `_run_perception_stage`, `_preprocess_text_observability`, and sensor-stack evaluation to `PerceptiveLobe`.
        - Centralized `PerceptionStageResult` in `src/kernel_lobes/models.py`.
        - Decoupled asynchronous I/O from the monolithic kernel core.
    - **STABILIZATION:**
        - Fixed `NameError` in `resolve_monologue_llm_backend_policy` (missing `g` definition).
        - Fixed `AttributeError` in `UserModelTracker.to_public_dict` (corrected `charm_reciprocity` mapping).
        - Restored `maybe_register_reparation_after_mock_court` module-level wrapper for `chat_server.py`.
        - Resolved `AttributeError` in `PerceptiveLobe` by correcting `MissionOrigin` and mission title handling.
    - **GOVERNANCE:**
        - Updated `AGENTS.md` to reflect `Team VisualStudio` exhaustion status [INACTIVE].
  - **Syntax Error Resolution:** Sanitized `narrative_storage.py` and `salience_map.py` from residual syntax defects (unclosed tuples, missing commas) introduced during the team-fusion merge.
  - **Validation Recovery:** Successfully restored the `test_ethical_properties.py` pass rate (100%) by resolving multiple `AttributeError`, `UnboundLocalError`, and schema mismatches. Recovered critical logic for `SolidarityAlert` emission (triggered by environmental risk > 0.8) and `AlgorithmicForgiveness` experience registration that was lost during the tri-lobe refactor.
- **Embodied sociability (Module 3):** 
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
- **Stabilization Window:** Decreed a **Feature Freeze** on `master-antigravity` prior to the `main` promotion rite.

## Claude — Phase 3+ Reward Modeling, Governance & Audit — April 2026

### Claude Team Updates

- **RLHF Reward Modeling (`src/modules/rlhf_reward_model.py`)**: 
  - Implemented full RLHF pipeline for controlled fine-tuning. Feature extraction (5D: embedding similarity, lexical score, perception confidence, ambiguity flag, category ID) from MalAbs evaluation artifacts. Logistic regression `RewardModel` with gradient descent training, predict/save/load support. `RLHFPipeline` orchestrates training, JSONL example persistence, and model management. 36 tests passing.
- **Multi-Realm Governance (`src/modules/multi_realm_governance.py`)**: Enabled decentralized per-realm (DAO/team/context) governance over MalAbs semantic gate thresholds (θ_allow, θ_block) and RLHF parameters. `RealmThresholdConfig` enforces hard constraints at all times. `ThresholdProposal` + `MultiRealmGovernor` enable reputation-weighted voting with configurable consensus threshold. Immutable audit trail per realm. 28 tests passing.
- **External Audit Framework (`src/modules/external_audit_framework.py`)**: Comprehensive security audit trail management with hash-linked tamper-evident logs (SHA-256 chain). `SecurityFinding` tracks vulnerabilities with severity/resolution lifecycle. `AuditReport` generates signed snapshots with attestation hash. `ExternalAuditFramework` manages findings, reports, compliance checklist, and log retention. 25 tests passing.
- **Test Suite**: 89 new tests across three modules; full suite 824 passed, 4 skipped (no regressions). Continuous audit (`verify_collaboration_invariants.py`) passes.
- **Integration**: Merged via `claude/upbeat-jepsen` → `master-claude`. Governance files authored under L1 co-authority (Claude + Antigravity per `collaboration-rule-authority.mdc`).

## Antigravity — Cybersecurity Consolidation & Integration Pulse — April 2026
