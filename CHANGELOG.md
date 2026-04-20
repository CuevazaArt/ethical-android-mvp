# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

**[URGENT — broadcast to all L2 integration hubs]:** All teams (Claude, Cursor, Copilot) should urgently `git pull` from `main` into their `master-*` branches. Outdated branches risk severe documentation path drift.

## [2026-04-20] Session 17: Distributed Nervous System & Monolith Guillotine (Ethos V13.0)
### Added/Integrated
- **The Guillotine (Phase C):** Obliterated the monolithic `src/kernel.py` God Class. Replaced it with `EthosKernel`, a distributed facade that orchestrates 4 asynchronous mnemonic lobes.
- **Nervous System Bus:** Integrated `CorpusCallosum` (Event Bus) as the primary cognitive transport layer.
- **Async Lobe Activation:** Fully transitioned Perceptive, Limbic, Executive, and Cerebellum lobes to a non-blocking, bus-aware operational model.
- **Traceability Chain:** Implemented `ref_pulse_id` across the nervous system to link stimuli to motor responses in a distributed environment.
- **Latency Telemetry:** Injected real-time latency tracking in each lobe's reactive handlers (Swarm Rule 3).
- **Legacy Compatibility:** Maintained backward compatibility with `RealTimeBridge` and `chat_server.py` via asynchronous entry points and legacy aliases.

### Fixed
- **Circular Imports:** Resolved a complex circular dependency chain between `CorpusCallosum`, `models.py`, and the Mnemonic Lobes using `TYPE_CHECKING` and future annotations.
- **Import Dead Code:** Removed broken `apply_nomad_telemetry_if_enabled` import in `perception_lobe.py` that was blocking system boot.
- **Adversarial Suite Sync:** Modernized the security test suite to support the new asynchronous distributed startup sequence.

## [2026-04-20] Session 16: Final Swarm Consolidation & Tri-Lobe Unification

### Fixed
- **Initialization Race Condition:** Resolved the conflict between high-frequency vision polling and background audio ingestion.
- **Type Safety Drift:** Hardened input sanitization and types in `absolute_evil.py` to prevent structural crashes during swarm merges.

## [2026-04-20] Session 15: Swarm Stabilization & Cryptographic Recovery
### Added
- **Secure Boot Recovery (scripts/update_secure_boot_hashes.py):** Created a mandatory L1 utility to re-sign the kernel manifest after architectural hardening pulses.
- **Numerical Hardening (Buffer B.1.1):** Applied strict `math.isfinite` guards and overflow protection to `sigmoid_will.py` and Bayesian likelihood modules.
- **Strict Typing (Buffer B.2.1):** Implemented full Type Hinting in `audio_adapter.py` and `vision_adapter.py` for MyPy compliance.
- **Architecture Traceability (Buffer B.3.1):** Updated `docs/architecture/TRI_LOBE_CORE.md` (Mermaid) and `kernel_utils.py` documentation.

### Fixed
- **System Integrity:** Resolved "Chain of trust broken" state caused by hardening modifications.

## [2026-04-20] Session 14: Nomad Hardening & Clinical Overhaul
### Added
- **Local VAD Implementation (Task 13.2)**: Integrated RMS-based Voice Activity Detection in `media_engine.js`. Audio transmission is now gated locally in the PWA, reducing bridge saturation.
- **Auto-Discovery (Task 14.1)**: Implemented mDNS advertisement in `chat_server.py` using `zeroconf_discovery.py`. Nomad PWA can now find the kernel on the LAN without IP entry.
- **Anti-NaN Hardening (Buffer B.1.1)**: Injected `math.isfinite` guards and defensive clipping in `sigmoid_will.py` and `ethical_poles.py` to prevent mathematical destabilization.

### Updated
- **Clinical Dashboard (Task 14.2)**: Complete overhaul of the L0 interface (`dashboard.js`, `index.html`, `dashboard.css`). Removed decorative 3D elements in favor of tabulated telemetry feeds (Latencies, Sigma, VAD Status).
- `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`: Synchronized task completion status.

## [2026-04-19] — Claude Team Integration (NARANJA2)
### Added
- ✅ **Module C.1.1 (RLHF Async Injection):** Dirichlet-based Bayesian weight modulation from RLHF reward signals.
- ✅ **Module C.1.2 (RLHF Pole Robustness):** Validates LinearPoleEvaluator thresholds immutable under RLHF.
- ✅ **Module C.2.1 (Governance Hot-Reload):** Live MalAbs semantic gate threshold updates.
- ✅ **Bloque 9.2 (Limbic Tension Escalation):** PersistentThreatTracker with 3-level auto-escalation (1s/3s/5s stages).
- ✅ **Bloque 11.1 (Audio Ouroboros):** STT→Reasoning→TTS loop (Whisper) for PWA/mobile.

### Decision (L1 Antigravity)
- **Status:** Integrated. The architectural divergence with main v12.0+ was resolved via manual L1 (Antigravity) merge as part of the 2026-04-20 Swarm Integration Pulse. 65+ integration tests verified as passing in the post-merge hub.

---

- Root **README** (*What it does*): ethical scoring described as a weighted mixture; `BayesianEngine` / `KERNEL_BAYESIAN_*` naming caveat.
- **ADR 0009**: `bayesian_engine.py` documented as wrapping `WeightedEthicsScorer` (`BayesianInferenceEngine`).

## [2026-04-20] Session 13: Autopilot & Multimodal Hardening

---

### Antigravity-Team Updates (2026-04-20 - Session 12 Integration)

- [x] **FULL REPOSITORY SYNCHRONIZATION (Phase 9 + S.12)**:
    *   **Consolidated Hardening**: Finalized the merge of `master-antigravity` (Integration Hub) into `main`. Successfully synchronized Phase 9 "Hardened Embodiment" (HMAC Secure Boot, Nomad Bridge Zero-Latency) with Session 11/12 "Vertical Armor" (Anti-NaN, Thermal ACL, InputTrust).
    *   **Secure Boot v2**: Re-implemented HMAC-SHA256 verification in `secure_boot.py` with support for both flat and structured manifests. Resealed the kernel using the Phase 9 generator.
    *   **Lifecycle Stability**: Corrected race conditions and `NameError` bugs in `chat_server.py` lifespan and `semantic_chat_gate.py`.
    *   **Verification**: Passed 100% of the `adversarial_suite.py` on the integrated tri-lobe architecture.

### Antigravity-Team Updates (2026-04-19 - Session 11)

- [x] **BOY SCOUT VERTICAL HARDENING (Finalization Phase)**:
    *   **Absolute Evil Circuit**: Blindada la entrada de `AbsoluteEvilDetector` contra tipos hostiles.
    *   **Input trust & Normalization**: Refactorizada la arquitectura de logs en `input_trust.py`. 
    *   **Semantic Gate Cleanup**: Tarea 17.1: **Decoupling del Sensory Cortex**: Desensamblar `PerceptiveLobe` para mover el procesamiento de texto a un manejador asíncrono y la emisión de sensores a pulsos brutos. (Completado: Antigravity)
    *   **Multimodal Trust Resilience**: Reparado el `NameError` en logs de latencia. 
    *   **Numerical Stability**: Sincronizadas las guardas Anti-NaN en `weighted_ethics_scorer.py` y `kernel_formatters.py`.

### Cursor Ultra (cursorultra) Team Updates (2026-04-18 - Phase 9)
- **Module S.1 (Nomad vision path):** gated background `NomadVisionConsumer` behind `KERNEL_NOMAD_VISION_CONSUMER`; started from `chat_server` lifespan.
- **Architectural Hardening (Pulse):** Finalized core kernel stabilization following the April 2026 rebase.
- **HMAC Signatures**: Integrated HMAC-SHA256 cryptographic handshake for Nomad Bridge connections.

... (Rest of the previous logs) ...
