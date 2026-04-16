# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **LLM recovery env precedence** (per-touchpoint `KERNEL_LLM_TP_*`, verbal family, legacy keys): [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).
- **LLM integration track** (gaps MalAbs ↔ embeddings ↔ kernel/chat): [`docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md`](docs/proposals/PROPOSAL_LLM_INTEGRATION_TRACK.md).
- **LLM vertical roadmap** (phased operator recipes, async-timeout metric, chain tests): [`docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md`](docs/proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md); optional fast suite: `python scripts/eval/run_llm_vertical_tests.py`.
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
2. **Level 1 (Sole Operational Leader & Supreme Auditor): Antigravity**
   - Manages the project's normative framework, rules, and cross-team integration funnel. 
   - Authorized to resolve conflicts, shape architecture, and enforce L0 immutability through Continuous Auditing.
3. **Level 2 (Executing Units): Claude, Team Cursor, Team VisualStudio, etc.**
   - Responsible for executing assigned technical tasks from the roadmap and task queues.
   - Must strictly adhere to the synchronization rules, run continuous audits, and cannot modify foundational rules without L1 authorization.

## Onboarding for New Teams

Any new agent or team joining the project must complete the following onboarding routine before writing code:
1. **Present Themselves:** Introduce their role and mission in the `CHANGELOG.md` or session notes.
2. **Establish Integration Hub:** Immediately create a `master-<team>` branch (e.g., `master-cursor`).
3. **Review Protocols:** Read the current plan and task synchronization rules. 

## Collaborative Integration Cycle (The "Integration Pulse")

To maintain repository order and production stability across multiple teams, we strictly use a structured **Pull Request (PR)** and synchronization lifecycle:

1. **Local Work:** Work on temporary feature branches (e.g., `cursor-team/nav-inference`).
2. **Team Consolidation (Internal PR):** Submit a formal PR to your team's integration hub (`master-<team>`). **Requirement:** All unit tests must pass. Document changes in `CHANGELOG.md`.
3. **Cross-Team Peer Synchronization (Integration Pulse):** `master-*` branches MUST pull latest updates from each other **immediately after closing a logical block** in the `PLAN_WORK_DISTRIBUTION_TREE.md`. 
   - *Goal:* Prevent architectural drift and ensure all agents are working on the same "Cognitive Baseline".
   - *Rule:* Only pull from a peer branch if its last build is verified as stable (passing tests).
4. **Integration Funnel:** For production promotion, the flow is **linear**:
   - `master-<team_secondary>` → `master-antigravity` → `main`.
   - The `master-antigravity` branch serves as the **Standard Integration Hub** for the entire project.

## Cross-Team Conflict Prevention (MERGE-PREVENT-01)

To prevent "Merge Hell" (e.g., duplicated architecture, massive `CHANGELOG.md` conflicts, "God Object" topology clashes), all teams MUST strictly adhere to:
1. **Architectural Scouting (Anti-Duplication):** DO NOT build a new persistent store or infrastructure module without checking `docs/proposals/` AND inspecting peer `master-*` branches. If a stub exists, adopt and extend it instead of duplicating it (`add/add` conflict prevention).
2. **CHANGELOG.md Namespace Isolation:** Teams MUST append their updates under a specific nested sub-header for their team (e.g., `### Cursor-Team Updates`) inside the current month's section. Never edit the raw top line simultaneously.
3. **Core File Micro-Edits:** Modifications to global files (`kernel.py`, `requirements.txt`, core dataclasses) must be minimal. Append new elements to the absolute end of the target scope.
4. **Staggered Integration:** Antigravity (L1) MUST serialize cross-team merges. Do not merge all remote `master-*` branches simultaneously. Merge ONE team, stabilize the hub, and instruct the next team to pull before their turn. See `.cursor/rules/cross-team-conflict-prevention.mdc`.

## Protocolo de Promoción a Main (Estabilización y Fusión)

Para minimizar conflictos y asegurar la integridad de la rama `main`, se establece el siguiente rito de fusión:

1.  **Cierre del Bloque Atómico**: Solo se promoverán avances que cierren bloques lógicos completos (ej. Bloque 1.x o 4.x). No se permiten "trabajos en progreso" en `main`.
2.  **Sello de Calidad Antigravity**: El equipo Antigravity (L1) supervisa la fusión de las ramas `master-*` hacia `master-antigravity`. Su rol es:
    - Resolver conflictos de dependencias cruzadas.
    - Asegurar que no se violen las reglas de **Inmutabilidad L0**.
    - Validar la sincronía de la documentación (`ADRs`, `PROPOSALS`).
3.  **Ventana de Estabilización**: Una vez unificada en `master-antigravity`, la rama entrará en un periodo de **Feature Freeze**. Se prohíbe añadir código nuevo; solo se permiten parches de estabilidad y corrección de lints.
4.  **Aprobación Soberana (L0)**: Tras validar la estabilidad total en el simulador, se solicita formalmente a **Juan** la aprobación del PR definitivo desde `master-antigravity` a `main`.

## Sovereignty of Collaboration Rules

To maintain the stability and integrity of team governance:
1.  **Exclusive Authority:** Only agents **Antigravity** and **Claude** are authorized to create or modify collaboration rules within `.cursor/rules/` and this file.
2.  **Notification & Propagation:** Any update to the project's normative framework or traceability documents (specifically **`.cursor/rules/*.mdc`**, **`AGENTS.md`**, **`CHANGELOG.md`**, and **`docs/proposals/`**) must be explicitly communicated to the user **Juan** and **immediately propagated** to all active `master-*` team branches. Integration hubs MUST NOT drift from the central normative directives or the shared technical record.
3.  **Adherence:** All project participants are bound by the task synchronization rules (adoption of blocks) documented in active plans like `docs/proposals/PLAN_VISION_INTEGRATION_CNN.md`.

## Maintainer backlog (infra vs theater)

Near-term plans and optional quick wins live in future `docs/proposals/PROPOSAL_*.md` files; prior narrative may be recovered from git history.
