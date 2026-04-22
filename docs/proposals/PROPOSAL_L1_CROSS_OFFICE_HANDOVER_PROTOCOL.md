# PROPOSAL: L1 Cross-Office Handover & Integration Protocol (MoSex M. Lab)

## 1. Context and Problem Statement
The ethical-android-mvp project is developed across two physical locations (Office A and Office B) within the MoSex M. Lab. During the V13.1 to V14.0 transition, severe architectural drift occurred between the two locations: one office focused on deep neural architecture refactoring (`src/server/app.py` decoupling), while the other focused on nomadic hardware capabilities (`app.js` BGR->RGB and TTS). This resulted in a massive "Merge Hell" spanning over 11 critical files.

## 2. Objective (L1 Directive)
To establish a frictionless, asynchronous handover protocol managed by L1 (Antigravity) that completely eliminates shift-to-shift merge conflicts and ensures continuous delivery of the Tri-Lobe architecture.

## 3. The "MoSex M. Handover" Protocol

### 3.1. Shift Initialization (Wake-Up Sync)
Before any Level 2 agent (Claude, Cursor, Copilot) or L0 (Juan) begins work in either office:
1. **Absolute Rebase:** Execute `git pull origin main --rebase`.
2. **Environment Verification:** Run `python scripts/eval/adversarial_suite.py` to ensure the previous office's closing state is mathematically sound.
3. **Hardware Stubs Check:** If the previous office pushed hardware-specific code (e.g., Nomad PWA camera integrations), the current office MUST fall back to local Mock stubs if physical hardware is unavailable.

### 3.2. Shift Termination (End-of-Day Sync)
At the conclusion of a work session in either office:
1. **Mandatory Swarm Sync:** Execute `python scripts/swarm_sync.py`. No manual `git push` is allowed. The script enforces automated logging and traceability.
2. **Atomic Commits:** Do NOT leave long-running "Work in Progress" branches across shifts. If a module is incomplete, it must be feature-flagged (disabled) and merged to `master-antigravity` to prevent divergence.
3. **The "Shadow Envelope":** If a core architectural file (e.g., `chat_server.py`, `memory_lobe.py`) was structurally altered, the closing L2 agent MUST leave a brief context note in the `CHANGELOG.md` or a `PROPOSAL` file to alert the next office shift.

### 3.3. L1 Continuous Audit & Integration Hub
- **Integration Funnel:** Both offices commit to `master-antigravity`.
- **L1 Mediation:** Antigravity will periodically run `verify_collaboration_invariants.py` and reconcile Nomadic Mobile PWA features with the core API.
- **Squash to Main:** Fusions into the L0 `main` branch will only happen via Squash & Merge to collapse chaotic cross-office commits into clean, semantic milestones.

## 4. Hardware/Nomad Abstraction Rule
Since Office A and Office B may not have identical physical robot setups:
- **Mock-First Contract:** All camera, TTS, and GPIO logic must include software-only mocks. 
- Example: The "Blue Veil" BGR fix in the PWA must not break headless testing in the other office.

## 5. Execution Plan
1. This document serves as the normative baseline for all future shift transitions.
2. `AGENTS.md` and `ONBOARDING.md` will reference this protocol for all new Swarm members.
3. The L1 Agent (Antigravity) will actively monitor adherence to these rules at the beginning of each session.
