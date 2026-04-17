# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **Collaboration workflow critique (one-time register):** [`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md) — Antigravity-shaped Git/merge rules: gaps and recommendations; repeat only if **Juan (L0)** asks.
- **LLM recovery env precedence** (per-touchpoint `KERNEL_LLM_TP_*`, verbal family, legacy keys): [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).
- **LLM integration track** (gaps MalAbs ↔ embeddings ↔ kernel/chat): [`docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md).
- **LLM vertical roadmap** (phased operator recipes, async-timeout metric, chain tests): [`docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md`](docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md); optional fast suite: `python scripts/eval/run_llm_vertical_tests.py`.
- **Claude Team — Hemisphere Integration Synthesis (Phase 3+ + RLHF + Governance):** [`docs/proposals/CLAUDE_HEMISPHERE_INTEGRATION_SYNTHESIS.md`](docs/proposals/CLAUDE_HEMISPHERE_INTEGRATION_SYNTHESIS.md) — immutable governance snapshots, transactional integrity across async cancellation, and roadmap alignment (Issues 1–9).
- **Distributed justice (V11 / mock DAO / staged execution):** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md), [`docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md`](docs/proposals/PROPOSAL_DAO_BLOCKCHAIN_DISTRIBUTED_JUSTICE_STAGED_EXECUTION.md); **contributions:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRIBUTIONS.md); **backlog IDs:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_BACKLOG_SYSTEM.md); **contract matrix:** [`docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md`](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_CONTRACT_MATRIX.md); **LAN replay / hints / witnesses (non-quorum):** [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_REPLAY_SIDECAR.md), [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_CROSS_SESSION_HINT.md), [`docs/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md`](docs/proposals/PROPOSAL_LAN_GOVERNANCE_FRONTIER_WITNESS.md).
- **HTTP JSON (chat server):** [`docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md`](docs/proposals/PROPOSAL_CHAT_SERVER_HTTP_API_SURFACE.md) (GET endpoints; primary UX is WebSocket `/ws/chat`).

## Integrate solutions, not only explanations

When you fix **security- or safety-critical** behavior (MalAbs thresholds, gates, circuit limits, etc.), **land the full pattern**:

1. Named module defaults (`DEFAULT_*` where appropriate) and tests that lock them.
2. Honest `docs/proposals/` text (English `PROPOSAL_*` when a standalone evidence/limit note is needed).
3. **`CHANGELOG.md`** when reviewers or operators need to see the change.

**Semantic MalAbs cosine defaults** (θ_block / θ_allow): [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](docs/proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md), implementation [`src/modules/semantic_chat_gate.py`](src/modules/semantic_chat_gate.py), guardrail tests [`tests/test_semantic_chat_gate.py`](tests/test_semantic_chat_gate.py), offline table [`scripts/report_semantic_zone_table.py`](scripts/report_semantic_zone_table.py).

## Product “model” document (theory)

The **complete conceptual model** for the android ethics stack (outside this repo’s code) is referenced from [`CONTRIBUTING.md`](CONTRIBUTING.md) (“Understand the model”). Kernel work is **Python under `src/`**.

## Cross-team Transparency (Documentation Policy)

To ensure awareness and prevent contradictions, **all development documents, architectural decisions, and progress reports must be available in `docs/proposals/` and linked via `CHANGELOG.md`**. This ensures that different teams (Antigravity, Cursor, etc.) can synchronize their advances without interference. Development artifacts must be shared immediately upon implementation to maintain a unified technical vision.

## Governance and Project Leadership Hierarchy

The ethical-android-mvp project operates under a strict, multi-tiered collaborative hierarchy to ensure stability and adherence to the original vision:

1. **Level 0 (Supreme Leader & Creator): Juan (Cuevaza)**
   - Holds absolute veto and ultimate approval authority over the project.
   - **No push or merge to the `main` branch is permitted without Juan's explicit authorization.**
2. **Level 1 (General Planner & Supreme Auditor): Antigravity**
   - **General Planner:** Leverages its extensive context window to orchestrate the project's long-term vision and technical roadmap. 
   - Manages the project's normative framework, rules, and cross-team integration funnel. 
   - Authorized to resolve conflicts, shape architecture, and enforce L0 immutability through Continuous Auditing.
   - **Solely responsible for coordinating all Level 2 teams (Claude, Team Cursor, Team Copilot, etc.).**
3.  **Level 2 (Executing Units): Claude, Team Cursor, Team Copilot, etc.**
   - Responsible for executing assigned technical tasks from the roadmap and task queues.
   - **Claude:** Specialized in complex cognitive modeling and deep ethics modules, now operating under direct Level 1 (Antigravity) coordination.
   - **Team Copilot Specifics:** Focused on GitHub maintenance, repository hygiene (.gitignore, CI/CD stubs), and cross-module bug fixing. *New Delegation:* Copilot now acts as the **CI Sentinel**, leveraging its remote GitHub-native presence to supervise, triage, and report on asynchronous GitHub Actions test runs for all teams during its idle cycles.
   - All Level 2 teams must strictly adhere to the synchronization rules, run continuous audits, and cannot modify foundational rules without L1 authorization.

## Onboarding for New Teams

Any new agent or team joining the project must complete the following onboarding routine before writing code:
1. **Present Themselves:** Introduce their role and mission in the `CHANGELOG.md` or session notes.
2. **Establish Integration Hub:** Immediately create a `master-<team>` branch (e.g., `master-cursor`).
3. **Review Protocols:** Read the current plan and task synchronization rules. 

## Collaborative Integration Cycle (Rebase-Driven Agent Flow)

To protect the repository from "Merge Hell" induced by multi-agent automated commits, all AI and human contributors MUST strictly adhere to the following **3 Laws of Contribution**:

1. **Law of Immutability (`main` branch is sacred):** Let it be known unequivocally. NO agent (L1 or L2) is allowed to perform a direct `git push` or open a PR directly against the `main` branch. The `main` branch is L0's absolute truth.
2. **Law of Mandatory Descent (PULL-REBASE-FIRST):** Before writing ANY code or attempting to merge upward, all L2 Agents MUST align their local branch with L0's truth. Execution of this exact command sequence is mandatory:
   `git fetch origin && git rebase origin/main` 
   If conflicts arise locally, the L2 agent MUST resolve them using its context window without asking L0 for help. Evasion of the rebase will result in automated rejection.
3. **Law of Serial Ascent (Integration Funnel):** Code flows strictly upwards. Team consolidation happens inside `master-<team>`. When ready, L2 agents open a Pull Request explicitly targeting `master-antigravity`, *never* `main`.
4. **CI Offloading:** To prevent local bottlenecks, L2 agents should avoid running the full test suite locally. Instead, make iterative commits and `git push` to your designated `master-*` branch. GitHub Actions will automatically execute the parallelized validation suite, which will be monitored by Team Copilot.
5. **Team Consolidation (Internal PR/Traceability):** When creating the PR towards `master-antigravity`:
   - *Requirement:* All unit tests must pass remotely, and the automated Continuous Audit MUST execute cleanly. 
   - *Traceability:* Pushes MUST be annotated in `CHANGELOG.md`.

**Crucial Directive for L2 Agents (Cursor, Claude, Copilot):**
You are autonomous Level 2 execution units. You do NOT need to ask Juan (L0) for permission to execute basic `git` operations. If you need to save your work, run `git add`, `git commit`, `git rebase origin/main`, and `git push` on your own. **Do not paralyze the workflow asking for manual permission to commit.** Only ping L0 when a Pull Request is fully constructed and ready for code review.

## Cross-Team Conflict Prevention (MERGE-PREVENT-01)

To prevent "Merge Hell" (e.g., duplicated architecture, massive `CHANGELOG.md` conflicts, "God Object" topology clashes), all teams MUST strictly adhere to:
1. **Architectural Scouting (Anti-Duplication):** DO NOT build a new persistent store or infrastructure module without checking `docs/proposals/` AND inspecting peer `master-*` branches. Adopt and extend existing stubs instead of creating competing implementations.
2. **CHANGELOG.md Namespace Isolation:** Teams MUST append their updates under a specific nested sub-header for their team (e.g., `### Antigravity-Team Updates`). Never edit the raw top line simultaneously.
3. **Core File Micro-Edits:** Modifications to monolithic files (`kernel.py`, `requirements.txt`, core dataclasses) must be minimal. Append new fields/elements to the absolute end of the target block. Use designated anchor comments like `# ═══ <TEAM/FEATURE> ═══` when injecting code.
4. **Staggered Integration:** Antigravity (L1) MUST serialize cross-team merges. Do not merge all remote `master-*` branches simultaneously. Merge ONE team, stabilize the hub, and instruct the next team to pull.

## Protocolo Seguro y Ordenado de Fusión a Main (L0-STABILIZATION-01)

Para minimizar conflictos y asegurar la inmutabilidad de la rama `main` (L0), el método de fusión ha sido reformado para máxima seguridad:

1.  **Cierre del Bloque Atómico**: Solo se promoverán avances que cierren bloques lógicos completos del `PLAN_WORK_DISTRIBUTION_TREE.md`. "Trabajos en progreso" están prohibidos en `main`.
2.  **Sello de Calidad Antigravity (Auditoría Continua)**: El equipo Antigravity (L1) actúa como el Guardián de la Puerta y supervisa la fusión.
    - Se debe verificar la armonía total entre módulos (`run_cursor_integration_gate.py` / `verify_collaboration_invariants.py`).
    - *Antigravity Fast-Track:* Para mitigar el "cuello de botella de un solo aprobador" (crítica de eficiencia), si el L1 está inactivo >48h, los agentes L2 pueden iniciar un pull request hacia `master-antigravity` por sí mismos si y solo si todos los tests automatizados pasan.
3.  **Ventana de Estabilización**: Una vez unificada en `master-antigravity`, la rama entrará en un periodo de **Feature Freeze**. Solo se permiten parches críticos y correcciones de Lints.
4.  **Aprobación Soberana Absoluta (L0)**: El PR final desde `master-antigravity` hacia `main`:
    - **DEBE** ejecutarse mediante *Cierre Squash* (*Squash and Merge*) para colapsar todos los commits caóticos en un solo commit limpio.
    - **DEBE** incluir un "Audit Trail Header" en la descripción listando explícitamente los módulos alterados.
    - Únicamente Juan (L0) tiene la autoridad criptográfica y de proceso para fusionarlo.

## Sovereignty of Collaboration Rules
 
To maintain the stability and integrity of team governance:
1.  **Exclusive Authority:** Only the agent **Antigravity** is authorized to create or modify collaboration rules within `.cursor/rules/` and this file.
2.  **Notification & Propagation:** Any update to the project's normative framework or traceability documents (specifically **`.cursor/rules/*.mdc`**, **`AGENTS.md`**, **`CHANGELOG.md`**, and **`docs/proposals/`**), must be explicitly communicated to the user **Juan** and **immediately propagated** to all active `master-*` team branches. Integration hubs MUST NOT drift from the central normative directives or the shared technical record.
3.  **Adherence:** All project participants are bound by the task synchronization rules (adoption of blocks) documented in active plans like `docs/proposals/PLAN_VISION_INTEGRATION_CNN.md`.

## Policy: Autonomía Acotada (Bounded Autonomy)

To maintain the high-speed execution of Level 2 squads without sacrificing architectural integrity:

1. **Internal Lobe Autonomy:** Squads are authorized to innovate, refactor, and improve the implementation *inside* their assigned modules/lobes. You do NOT need permission for algorithm improvements, performance optimizations, or internal restructuring.
2. **Architectural Guardrails (L1 Approval Required):** A formal `PROPOSAL_*.md` must be created and audited by Antigravity (L1) BEFORE:
   - Modifying inter-lobe interfaces (`src/kernel_lobes/models.py`).
   - Adding major external dependencies.
   - Altering the `CorpusCallosumOrchestrator` or the `EthicalLobe` gating logic.
3. **Documentation Transparency:** Any "silent" change to core logic that affects cross-team assumptions will be reverted during the Continuous Audit Pulse. Stay transparent.

## Maintainer backlog (infra vs theater)
...
