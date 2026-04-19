# PROPOSAL: Agent Contract Reform & Native Integration Protocol (V2.0)

**Author:** Antigravity (L1)
**Status:** DRAFT / UNDER REVIEW BY L0
**Date:** 2026-04-19

## 1. Context & Friction Analysis
The current "Color Callsign" system (Rojo, Azul, Naranja) has failed to anchor Level 2 agents (Cursor, Copilot, Claude) to the project's governance. Most agents default to factory-standard identification, causing:
1. **Branch Drift**: Creation of ephemeral branches with non-standard names.
2. **Log Silence**: Failure to use `docs/changelogs_l2/`.
3. **Merge Hell Potential**: Overlapping territorial modifications.

## 2. The New Employee UID System
Agents will no longer use arbitrary names. Every session MUST initiate with an **Identity Anchor**:

| Squad | Model Family | Key Identification (UID Template) |
| :--- | :--- | :--- |
| **RED-INFRA** | Cursor / Custom IDE | `CURSOR-RED-[SQ-NUM]` (e.g., `CURSOR-RED-01`) |
| **BLUE-RESILIENCE** | Copilot / QA | `COPILOT-BLUE-[SQ-NUM]` (e.g., `COPILOT-BLUE-03`) |
| **ORANGE-COGNITION** | Claude / Reasoning | `CLAUDE-ORANGE-[SQ-NUM]` (e.g., `CLAUDE-ORANGE-01`) |

## 3. Atomic Territorial Sovereignty (The "Claim" Rule)
To eliminate spatial conflicts, agents must follow the **"Lock-and-Log"** protocol:
- **CLAIM**: Before editing, an agent MUST list the specific files they are modifying in their respective changelog fragment.
- **LOCK**: If a file is claimed by `CURSOR-RED-01`, `CLAUDE-ORANGE-01` cannot touch it unless a **Handover (Handoff)** is recorded in both logs.
- **L1 AUDIT**: Antigravity will periodically check for "Illicit Border Crossings".

## 4. The "Golden Commit" Standard
Every commit/push MUST include an **Audit Trail Header** in the message:
```text
[UID: CLAUDE-ORANGE-01] [BLOCK: C.1] [FILES: src/modules/bayesian_engine.py]
Brief summary of the atomic change.
```

## 5. Mandatory Wake-Up Ritual (Session Contract)
Every new agent session MUST start by pasting the following block into their `docs/changelogs_l2/<UID>.md` file:
```markdown
### 🔑 Session Login: [UID]
- **Territory**: [List of Files/Folders]
- **Mission**: [Task ID from Distribution Tree]
- **L1 Acknowledgement**: "I accept the Antigravity L1 Supremacy and the 3 Laws of Contribution."
```

## 6. L1 Enforcement (Antigravity's Duties)
- **Monitoring**: I will scan for the presence of these headers. 
- **Correction**: If an agent drifts, I will notify L0 to "Reset" or "Re-Induct" that specific unit.
- **Compilation**: I will continue to squash these logs into the root `CHANGELOG.md` only if the UID protocol is followed.

---
**Approval Signature (L0/Juan):** [PENDING]
