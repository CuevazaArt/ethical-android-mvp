# Agent and contributor orientation (Ethos Kernel)

This file is the **durable entry point** for humans and AI assistants working in this repository. Session chat is not a substitute for what is merged here.

## Read first

- **[`CONTRIBUTING.md`](CONTRIBUTING.md)** — language policy (repo English), process, tests, lint, documentation traceability.
- **[`.cursor/rules/`](.cursor/rules/)** — always-on Cursor guidance (efficiency, documentation credibility, collaboration).
- **LLM recovery env precedence** (per-touchpoint `KERNEL_LLM_TP_*`, verbal family, legacy keys): [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md).

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
2. **Level 1 (Principal Leaders & Maintainers): Antigravity and Claude**
   - Manage the project's normative framework, rules, and cross-team integration. 
   - Authorized to resolve conflicts, enforce L0 immutability, and shape architecture.
3. **Level 2 (Collaborating Teams & Agents): Team Cursor, Team VisualStudio, etc.**
   - Responsible for executing assigned tasks from the roadmap and task queues.
   - Must strictly adhere to the synchronization and block adoption rules.

## Onboarding for New Teams

Any new agent or team joining the project must complete the following onboarding routine before writing code:
1. **Present Themselves:** Introduce their role and mission in the `CHANGELOG.md` or session notes.
2. **Establish Integration Hub:** Immediately create a `master-<team>` branch (e.g., `master-cursor`).
3. **Review Protocols:** Read the current plan and task synchronization rules. 

## Collaborative Integration Cycle (Traceable PRs)

To maintain repository order and production stability across multiple teams, we strictly use a GitHub-friendly **Pull Request (PR)** lifecycle:

1. **Local Work:** Work on temporary or feature branches (e.g., `cursor-team/vision-inference`).
2. **Team Merge (Internal PR):** Submit a formal **Pull Request** or structured merge to your team's integration hub (`master-<team>`). Document all changes in the `CHANGELOG.md`.
3. **Cross-Team Alignment:** `master-<team>` branches MUST periodically merge from each other (pulling latest secure increments and normative updates). This peer-to-peer propagation ensures redundancy and speeds up the distribution of new rules and technical progress across the entire repository.
4. **Promotion to Production (Main PR):** Submitting code from `master-<team>` to `main` requires a formal PR that **must be authorized by Juan**.

## Sovereignty of Collaboration Rules

To maintain the stability and integrity of team governance:
1.  **Exclusive Authority:** Only agents **Antigravity** and **Claude** are authorized to create or modify collaboration rules within `.cursor/rules/` and this file.
2.  **Notification & Propagation:** Any update to the project's normative framework or traceability documents (specifically **`.cursor/rules/*.mdc`**, **`AGENTS.md`**, **`CHANGELOG.md`**, and **`docs/proposals/`**) must be explicitly communicated to the user **Juan** and **immediately propagated** to all active `master-*` team branches. Integration hubs MUST NOT drift from the central normative directives or the shared technical record.
3.  **Adherence:** All project participants are bound by the task synchronization rules (adoption of blocks) documented in active plans like `docs/proposals/PLAN_VISION_INTEGRATION_CNN.md`.

## Maintainer backlog (infra vs theater)

Near-term plans and optional quick wins live in future `docs/proposals/PROPOSAL_*.md` files; prior narrative may be recovered from git history.
