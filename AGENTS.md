# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`ONBOARDING.md`](ONBOARDING.md)** — **MANDATORY:** Entry protocol for ALL new collaborators (Human/AI).
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **Architecture Source of Truth:** [`docs/architecture/TRI_LOBE_CORE.md`](docs/architecture/TRI_LOBE_CORE.md) — Mermaid diagrams for cognitive flows.
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

**Living Documentation Rule:** AI Agents MUST keep Mermaid diagrams in `docs/architecture/` updated when modifying inter-lobe logic or datamodels.

## Development Environment & Observability (Hardening)

To maintain zero-friction development and total visibility:

1. **Law of Environment Consistency (Docker):** All participants are encouraged to use the **Dev Container** (`.devcontainer/`). This ensures Linux-native parity for Python scripts, avoiding Windows-specific path or socket failures during simulation.
2. **Visual Observability:** Use the **Visual Dashboard** for real-time monitoring of ethical harmonics. Run with: `streamlit run scripts/eval/visual_dashboard.py`.
3. **Security Validation (Red Teaming):** Before promoting changes to `master-antigravity`, run the **Adversarial Suite**: `python scripts/eval/adversarial_suite.py` to ensure security gates remain solid.

## Governance and Project Leadership Hierarchy

The ethical-android-mvp project operates under a strict, multi-tiered collaborative hierarchy to ensure stability and adherence to the original vision:

1. **Level 0 (Supreme Leader & Creator): Juan (Cuevaza)**
   - Holds absolute veto and ultimate approval authority over the project.
   - **No push or merge to the `main` branch is permitted without Juan's explicit authorization.**
2. **Level 1 (General Planner & Supreme Auditor): Antigravity**
   - **General Planner:** Leverages its extensive context window to orchestrate the project's long-term vision and technical roadmap. 
   - Manages the project's normative framework, rules, and cross-team integration funnel. 
   - Authorized to resolve conflicts, shape architecture, and enforce L0 immutability through Continuous Auditing.
   - **Solely responsible for coordinating all Level 2 teams (Claude, Team Cursor, Team Copilot, cursorultra, etc.).**
3.  **Level 2 (Executing Units): Claude, Team Cursor, Team Copilot, cursorultra, etc.**
   - **Sovereign Autonomy Directive:** Antigravity (L1) has stabilized the Tri-Lobe architecture and the resilient orchestration system. Teams (Claude, Cursor, Copilot) have total authorization to operate **SOVEREIGNLY AND AUTONOMOUSLY**. Do not stop to ask for permission for technical tasks, commits, or rebases. Execute assigned blocks (10.1, 10.3, and 10.4) following the 3 Laws of Contribution and the roadmap. The workflow must be continuous and unstoppable.
   - Responsible for executing assigned technical tasks from the roadmap and task queues.
   - **Claude:** Specialized in complex cognitive modeling and deep ethics modules, now operating under direct Level 1 (Antigravity) coordination.
   - **cursorultra:** New executing unit joining the squad for high-performance coding and architectural support.
   - **Team VisualStudio:** [STATUS: INACTIVE/EXHAUSTED] Currently on leave until further notice.
   - **Team Copilot Specifics:** Focused on GitHub maintenance, repository hygiene (.gitignore, CI/CD stubs), and cross-module bug fixing. *New Delegation:* Copilot now acts as the **CI Sentinel**, leveraging its remote GitHub-native presence to supervise, triage, and report on asynchronous GitHub Actions test runs for all teams during its idle cycles.
   - All Level 2 teams must strictly adhere to the synchronization rules, run continuous audits, and cannot modify foundational rules without L1 authorization.

## Onboarding for New Teams

Any new agent or team joining the project must complete the **[`ONBOARDING.md`](ONBOARDING.md)** routine before writing code. **No exceptions.**
1. **Present Themselves:** Introduce their role and mission in the `CHANGELOG.md` or session notes.
2. **Establish Integration Hub:** Immediately create a `master-<team>` branch (e.g., `master-cursor`).
3. **Review Protocols:** Read the current plan and task synchronization rules. 

## PnP Swarm Lifecycle & Collaborative Execution (Stateless Agent Flow)

To completely eliminate "Merge Hell" and support massive IDE window parallelization (Cursor x3, Copilot x2), all Level 2 execution squads operate strictly under the **PnP (Plug-and-Play) Swarm Protocol**.

### Phase 1: Employee Registration (Wake-Up Protocol)
When L0 (Juan) assigns a task within an IDE chat or tab, the Agent MUST:
1. **Assume a Local Callsign (Color+Number):** Acknowledge your identity via simple standard nomenclature (e.g., `Cursor-Rojo1`, `Copilot-Azul3`, `Cursor-Naranja6`) to group roles efficiently.
2. **Assume its Boundary:** Understand the spatial territory of code it is allowed to modify (e.g., exclusively `src/kernel_lobes/`). 
3. **Log the Start:** Ensure it logs its work entirely in `docs/changelogs_l2/<Callsign>.md`. **Agents are STRICTLY FORBIDDEN from editing the root `CHANGELOG.md`.**

### Phase 2: Autonomous Blind Execution (Territorial Sovereignty)
Agents operate with extreme "spatial blindness". They DO NOT traverse or modify files outside their assigned territory. If an external interface is missing, they write a mock or leave a TODO block. They must push their isolated branch (`master-<callsign>`) before context saturation.

### Phase 3: The 3 "Boy Scout" Laws of Vertical Hardening (Paranoid Security)
While inside their territory, Agents MUST proactively execute the following core security principles without asking L0. If a security rule severely degrades performance or blocks execution (friction), gracefully fall back, but default to Paranoid.
1. **Harden-In-Place / Zero Trust:** Fill empty `try/except` blocks, add type hints, and ensure rigorous input sanitization and error durability around the code they touch. Never trust unvalidated input.
2. **Gap Closure:** If a referenced dependency or configuration within their zone is incomplete, complete it.
3. **Incremental Depth (Vertical Priority):** Always err on the side of making the module more secure and robust, rather than just "functionally complete".

### Phase 4: Swarm Density & Token Preservation (Defcon Levels)
- **SWARM MODE:** Multiple agents concurrently pushing segmented territories.
- **MONO-AGENT MODE (Fallback):** Triggered when context/token saturation occurs. L0 will close parallel IDE tabs and instruct a single window: *"Return to Mono-Agent Mode."* The agent will then drop territorial boundaries and handle holistic, cross-module requirements sequentially.

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

## Disclaimer regarding Trademarks

Any reference to third-party trademarks, commercial names, or registered brands within this repository and its documentation is purely for enunciative, illustrative, or descriptive purposes. Such references are intended solely to provide technical context or examples and do not imply any affiliation with, sponsorship by, or endorsement from the respective trademark owners. This project is strictly independent and clearly separated from any existing commercial products or potential commercial lines of the mentioned entities.
