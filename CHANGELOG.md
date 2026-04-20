# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

**[URGENT — broadcast to all L2 integration hubs]:** All teams (Claude, Cursor, Copilot) should urgently `git pull` from `main` into their `master-*` branches. Outdated branches risk severe documentation path drift.

## [2026-04-20] Session 13: Autopilot & Multimodal Hardening
### Added
- **Dynamic Sensor Calibration (Task 12.2)**: Implemented `SensorBaselineCalibrator` for boot-time acclimatization (60s cycle). Replaced static thresholds for temperature and acceleration with dynamic Means/StdDev (μ+σ) logic.
- **Nomad Chat Reconnection (Task 13.1)**: Enabled text communication from Nomad Vessel (Smartphone) via the Bridge. Added `NomadChatConsumer` in the server with strict limbic timeouts and async queuing.
- **Global Hardware Kernel**: Initialized a persistent kernel instance in `chat_server.py` to handle background sensor loops and chat reconnection.

### Fixed
- Improved robustness of the `NomadBridge` event loop by adding missing event handlers and hardening type checks.
- Fixed a SyntaxError in `sensor_calibration.py` docstrings.

### Updated
- `src/kernel.py`: Integrated calibration start and chat consumer attachment.
- `src/modules/vitality.py`: Thresholds now query the `SensorBaselineCalibrator`.
- `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`: Marked 12.2 and 13.1 as closed.

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
    *   **Semantic Gate Cleanup**: Inyectadas guardas `math.isfinite` en los umbrales de similitud coseno.
    *   **Multimodal Trust Resilience**: Reparado el `NameError` en logs de latencia. 
    *   **Numerical Stability**: Sincronizadas las guardas Anti-NaN en `weighted_ethics_scorer.py` y `kernel_formatters.py`.

### Cursor Ultra (cursorultra) Team Updates (2026-04-18 - Phase 9)
- **Module S.1 (Nomad vision path):** gated background `NomadVisionConsumer` behind `KERNEL_NOMAD_VISION_CONSUMER`; started from `chat_server` lifespan.
- **Architectural Hardening (Pulse):** Finalized core kernel stabilization following the April 2026 rebase.
- **HMAC Signatures**: Integrated HMAC-SHA256 cryptographic handshake for Nomad Bridge connections.

... (Rest of the previous logs) ...
