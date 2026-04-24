# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`ONBOARDING.md`](ONBOARDING.md)** — **MANDATORY:** Entry protocol for ALL new collaborators (Human/AI).
- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **Architecture Source of Truth:** [`docs/architecture/TRI_LOBE_CORE.md`](docs/architecture/TRI_LOBE_CORE.md) — Mermaid diagrams for cognitive flows.
- **Secure Boot Manifest Recovery:** [`scripts/update_secure_boot_hashes.py`](scripts/update_secure_boot_hashes.py) — **L1/L0 ONLY:** Re-signatures the kernel manifest after intentional modifications.
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
3.  **Level 2 (Executing Units): Swarm Workers (Claude, Cursor, Copilot, etc.)**
    - **Sovereign Autonomy Directive:** Antigravity (L1) has stabilized the Tri-Lobe architecture. L2 units operate purely organically as stateless workers. Do not stop to ask for permission for technical tasks. Pull from the open backlog, fix, run the sync script, and move on.
    - **Claude Team Specifics:** Specialized in complex cognitive modeling and deep ethics modules.
      - **Implementation Status (2026-04-19):** 
        - ✅ **Module C.1.1** (Async RLHF): Dirichlet-based Bayesian weight modulation.
        - ✅ **Module C.1.2** (Pole Robustness): Validation against LinearPoleEvaluator corruption.
        - ✅ **Module C.2.1** (Governance Hot-Reload): Live threshold updates via Event Bus.
        - ✅ **Bloque 9.2** (Limbic Escalation): PersistentThreatTracker with 5s auto-escalation.
        - ✅ **Bloque 11.1** (Audio Ouroboros): Full Whisper -> Kernel -> TTS loop.
    - **Team Copilot Specifics:** Focused on repository hygiene, CI/CD stubs, and cross-module bug fixing.
    - All Level 2 units must strictly adhere to the Boy Scout rules, run continuous audits, and cannot modify foundational rules without L1 authorization.

## Onboarding for New Teams

Any new agent or team joining the project must complete the **[`ONBOARDING.md`](ONBOARDING.md)** routine before writing code. **No exceptions.**
1. **Focus on the Code:** There are no mandatory separate branches or specific names. Focus entirely on the technical problem at hand.
2. **Review Protocols:** Read the current plan and open tasks buffer in `PLAN_WORK_DISTRIBUTION_TREE.md`. 

## PnP Swarm Lifecycle & Collaborative Execution (Stateless Agent Flow)

To completely eliminate "Merge Hell" and support massive IDE window parallelization, all Level 2 units operate under the **Anonymous Pragmatism Workflow (V4.0)**.

### Phase 0: Bi-Locational Handover (Wake-Up Sync)
Due to the reality of physical mobility (Office A vs Office B) and dual shifts, **NO AGENT is allowed to write code before synchronizing the reality**.
- **MANDATORY**: Execute `git pull origin main --rebase` immediately upon waking up. This prevents Split-Brain divergence across physical offices.
- **Auto-Push Assurance**: Always use `scripts/swarm_sync.py` which now enforces an automatic `git push` to preserve the state for the next physical location.

### Phase 1: Open Backlog Execution
When L0 (Juan) assigns a task or you are deployed:
1. **Pull a Task:** Pick the highest priority `[PENDING]` task from `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`.
2. **Execute Statelessly:** You don't need a name, UID, or color. Your identity is your execution. Write the solution.
3. **Log the Work programmatically:** You must rely on `scripts/swarm_sync.py` to handle the logging and commits.

### Fase 2: Las 4 "Leyes del Boy Scout" de Endurecimiento Vertical
Durante cada intervención, DEBES ejecutar proactivamente los siguientes principios de seguridad:
1. **Harden-In-Place / Zero Trust**: Llena bloques `try/except` vacíos, añade type hints y asegura un saneamiento de inputs riguroso.
2. **Cierre de Brechas (Anti-NaN)**: Si tocas lógica matemática o de latencia, asegura que los resultados no puedan ser `NaN` o `Inf`. Añade `math.isfinite()` donde sea necesario.
3. **Métricas de Latencia**: Todo nuevo loop o aferencia sensorial debe registrar su latencia en milisegundos (`time.perf_counter()`) para el lóbulo de telemetría.
4. **Poda de Viejas Vías (Zero Dead Code)**: Si detectas simuladores (mocks) residuales o código que fue reemplazado por el bus asíncrono (ej. monolito antiguo), tu deber es eliminarlo. Mantén el repositorio ligero.

### Fase 3: Pulso de Auditoría Adversaria (L1-AUDIT-PULSE)
Para mitigar el "Efecto Túnel", se establece la siguiente restricción:
- **Regla del Tercer Bloque**: Cada vez que el `PLAN_WORK_DISTRIBUTION_TREE.md` registre 3 bloques terminados en el histórico, el siguiente agente EN PILOTO AUTOMÁTICO debe ignorar el backlog y ejecutar obligatoriamente: `python scripts/eval/adversarial_suite.py`. 
- No se permiten nuevos avances hasta que los tests de seguridad pasen con 0 fallos.

### Fase 4: Registro Automatizado (Swarm Sync)
- No uses mensajes genéricos en `--msg`. El mensaje debe listar los archivos modificados y el impacto arquitectónico.
- El uso de `scripts/swarm_sync.py` es OBLIGATORIO al final de cada bloque atómico. No es un comentario decorativo; es la única forma de promover el código al funnel de integración L1.

## Protocolo Seguro y Ordenado de Fusión a Main (L0-STABILIZATION-01)

Para minimizar conflictos y asegurar la inmutabilidad de la rama `main` (L0), el método de fusión ha sido reformado para máxima seguridad:

1.  **Cierre del Bloque Atómico**: Solo se promoverán avances que cierren bloques lógicos completos del `PLAN_WORK_DISTRIBUTION_TREE.md`. "Trabajos en progreso" están prohibidos en `main`.
   - **BLOCKER ACTUAL (2026-04-19):** Claude Team ha completado 5 módulos (C.1.1, C.1.2, C.2.1, 9.2, 11.1) con 65+ tests passing. Sin embargo, `git pull origin main` reveló que main branch ha evolucionado a v12.0+ (moral infrastructure hub, distributed justice, DAO pipelines) que diverge de la arquitectura de PLAN_WORK_DISTRIBUTION_TREE.md. Se detectaron 11 archivos con merge conflicts. **Requiere L1 decision:** (A) Rebase/redesign modules for v12.0+, (B) Mantener como feature branches, (C) L1 merge manual.
   
2.  **Sello de Calidad Antigravity (Auditoría Continua)**: El equipo Antigravity (L1) actúa como el Guardián de la Puerta y supervisa la fusión.
    - Se debe verificar la armonía total entre módulos (`run_cursor_integration_gate.py` / `verify_collaboration_invariants.py`).
    - *Antigravity Fast-Track:* Para mitigar el "cuello de botella de un solo aprobador" (crítica de eficiencia), si el L1 está inactivo >48h, los agentes L2 pueden iniciar un pull request hacia `master-antigravity` por sí mismos si y solo si todos los tests automatizados pasan.
3.  **Ventana de Estabilización**: Una vez unificada en `master-antigravity`, la rama entrará en un periodo de **Feature Freeze**. Solo se permiten parches críticos y correcciones de Lints.
4.  **Aprobación Soberana Absoluta (L0)**: El PR final desde `master-antigravity` hacia `main`:
    - **DEBE** ejecutarse mediante *Cierre Squash* (*Squash and Merge*) para colapsar todos los commits caóticos en un solo commit limpio.
    - Únicamente Juan (L0) tiene la autoridad criptográfica y de proceso para fusionarlo.

## Agility & Anti-Friction Directives (Phase 9 Update)

To prevent bottlenecks and maintain high velocity during hardware and multi-agent integrations, all Tier 1 and Tier 2 agents must obey the following workflows:

1. **"Mock-First" Hardware Contract:** Any agent developing physical integrations (e.g., Nomad Bridge, Audio/Video sensors) MUST provide a `Mock` or `.stub` implementation in the same PR. Agents are forbidden from pushing hardware code that breaks local CI testing for peers who lack physical devices.
2. **"Fast-Track Merge" for Debt/Tests:** If an L2 agent (e.g., Copilot or Claude) unilaterally fixes decoupled tests or localized bugs WITHOUT altering core L0/C1 logic, and the CI passes 100%, they are authorized to perform a self-approved "Fast-Track Merge" to the integration hub (`master-antigravity`) without waiting for L1's manual audit.
3. **"Shadow Envelopes" in Changelog:** When resolving deep architectural tasks (like RLHF or new cognitive blocks), L2 agents MUST NOT modify `CHANGELOG.md` without an attached "Shadow Envelope" (a minimal 2-line header explaining *why* the abstraction was chosen). This eliminates guesswork during L1 integration audits.

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
