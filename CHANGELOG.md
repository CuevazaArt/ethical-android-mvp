# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

**Note:** Older sections below may still **link** to paths that were later removed (for example `experiments/million_sim/`, `docs/multimedia/`, root `dashboard.html`, `landing/`). Those links are **historical**; recover files from git history or backup branches if you need them.

**[URGENT — broadcast to all L2 integration hubs]:** All teams (Claude, Cursor, Copilot) should urgently `git pull` from `main` into their `master-*` branches. Outdated branches risk severe documentation path drift.

## [2026-04-20] Session 14: Nomad Hardening & Clinical Overhaul
### Added
- **Local VAD Implementation (Task 13.2)**: Integrated RMS-based Voice Activity Detection in `media_engine.js`. Audio transmission is now gated locally in the PWA, reducing bridge saturation.
- **Auto-Discovery (Task 14.1)**: Implemented mDNS advertisement in `chat_server.py` using `zeroconf_discovery.py`. Nomad PWA can now find the kernel on the LAN without IP entry.
- **Anti-NaN Hardening (Buffer B.1.1)**: Injected `math.isfinite` guards and defensive clipping in `sigmoid_will.py` and `ethical_poles.py` to prevent mathematical destabilization.

### Updated
- **Clinical Dashboard (Task 14.2)**: Complete overhaul of the L0 interface (`dashboard.js`, `index.html`, `dashboard.css`). Removed decorative 3D elements in favor of tabulated telemetry feeds (Latencies, Sigma, VAD Status).
- `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`: Synchronized task completion status.

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
    *   **Semantic Gate Cleanup**: Inyectadas guardas `math.isfinite` en los umbrales de similitud coseno.
    *   **Multimodal Trust Resilience**: Reparado el `NameError` en logs de latencia. 
    *   **Numerical Stability**: Sincronizadas las guardas Anti-NaN en `weighted_ethics_scorer.py` y `kernel_formatters.py`.

### Cursor Ultra (cursorultra) Team Updates (2026-04-18 - Phase 9)
- **Module S.1 (Nomad vision path):** gated background `NomadVisionConsumer` behind `KERNEL_NOMAD_VISION_CONSUMER`; started from `chat_server` lifespan.
- **Architectural Hardening (Pulse):** Finalized core kernel stabilization following the April 2026 rebase.
- **HMAC Signatures**: Integrated HMAC-SHA256 cryptographic handshake for Nomad Bridge connections.

... (Rest of the previous logs) ...
