# Claude Team Playbook — Real Bayesian Ethical Inference

**Status:** active scope charter for collaborative multi-origin work under:

- [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md)
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- [`AGENTS.md`](../../AGENTS.md)

This playbook defines how the team closes gaps between the current mixture scorer and a stronger, evidence-honest Bayesian inference architecture.

## 1) Mission

Deliver Bayesian capability that is technically honest, testable, and operator-legible:

1. Close known gaps in current Bayesian language vs implemented behavior.
2. Propose and land architecture seams for true posterior-based inference.
3. Improve adjacent needs required for safe operation (evidence, observability, policy clarity).

## 2) Scope boundaries

### In scope

- Ethical mixture weight uncertainty and posterior updates (`Dirichlet` / likelihood paths).
- Context-aware posterior routing and contradiction detection quality.
- Bayesian telemetry surfaced to operators and tests.
- Architecture interfaces that allow stronger Bayesian engines without breaking default behavior.

### Out of scope

- Governance/on-chain delivery tracks.
- Hardware/sensor transport implementation details (except inference interface requirements).
- Marketing claims beyond in-repo evidence.

## 3) Current gap map (starting point)

Primary references:

- [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md) — naming honesty.
- [ADR 0012](../adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md) — Levels 1–3.
- [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) — external review synthesis.

Open technical tension to resolve:

1. **Inference depth gap:** Level 1/2/3 exists, but default runtime still behaves mostly as a fixed mixture path.
2. **Evidence gap:** posterior quality depends on feedback quality and calibration assumptions; uncertainty communication is still uneven.
3. **Architecture gap:** Bayesian paths should be first-class, composable components (not scattered optional hooks) while preserving backward compatibility.
4. **Operator gap:** Bayesian diagnostics should be explicit enough for runtime decisions, not only for offline interpretation.

## 4) Multi-origin collaboration operating mode

### Intake gate (mandatory)

Every candidate task must include:

- `redundancy_check`: where the same work is already tracked.
- `novelty_or_coverage`: why this closes a real gap now.
- `risk_class`: `critical` | `high` | `normal`.
- `target_branch`: from `cursor-team` using branch naming below.

### Branch conventions (from `cursor-team`)

- `cursor/bayes-core-<topic>`
- `cursor/bayes-evidence-<topic>`
- `cursor/bayes-architecture-<topic>`
- `cursor/bayes-docs-<topic>`

### Integration flow

`cursor-team` -> `master-Cursor` -> `main` (maintainer/release step only).

## 5) Execution backlog (P0/P1/P2)

### P0 — critical integrity and operator clarity

#### BI-P0-01 — Bayesian mode contract (runtime-safe and explicit)

- **Goal:** define a single runtime contract for Bayesian operation modes (telemetry-only, posterior-assisted, posterior-driven).
- **Deliverables:** named constants/env contract, tests for defaults and override behavior, docs update.
- **Acceptance:** no silent behavior switch; operator can tell active Bayesian mode from decision artifacts.

#### BI-P0-02 — Posterior consistency guardrails

- **Goal:** formalize contradiction and low-evidence states as first-class runtime statuses.
- **Deliverables:** deterministic statuses, test coverage across compatible/contradictory feedback sets, docs for remediation.
- **Acceptance:** contradictory feedback cannot pass as “normal posterior update.”

### P1 — architecture and evidence hardening

#### BI-P1-01 — Bayesian inference engine seam

- **Goal:** introduce an explicit engine boundary so Bayesian inference evolves independently from legacy weighted scorer internals.
- **Deliverables:** interface module, default adapter preserving current behavior, integration tests.
- **Acceptance:** no regressions with default mode off; architecture allows future full posterior engine.

#### BI-P1-02 — Likelihood evidence profile matrix

- **Goal:** document and test supported likelihood families and their evidence posture.
- **Deliverables:** proposal section + tests for softmax/IS path assumptions and failure modes.
- **Acceptance:** no empirical overclaim; each likelihood mode has explicit operator caveats.

### P2 — adjacent needs and research-grade reliability

#### BI-P2-01 — Bayesian observability contract

- **Goal:** stable, minimal telemetry schema for posterior state, contradiction flags, and decision uncertainty.
- **Deliverables:** docs + runtime emission points + test assertions on schema presence.
- **Acceptance:** dashboards or logs can reliably detect degraded Bayesian conditions.

#### BI-P2-02 — Scenario quality and calibration debt register

- **Goal:** maintain an explicit debt register for posterior calibration quality and scenario coverage.
- **Deliverables:** proposal appendix or dedicated doc + links from roadmap and changelog.
- **Acceptance:** reviewers can separate implemented capability from unverified calibration claims.

## 6) Definition of done

A Bayesian task is complete only when all apply:

1. Code changes land with named defaults and backward-compatible behavior gates.
2. Tests assert defaults, overrides, and contradiction/failure paths.
3. Docs in `docs/proposals/` are updated with honest evidence posture.
4. `CHANGELOG.md` records operator-visible impact.
5. Integration follows branch policy and review flow.

## 7) Adjacent architecture needs (tracked dependencies)

- Consistent env validation for Bayesian-related flags.
- Shared uncertainty semantics across kernel decision, chat response, and operator surfaces.
- Reproducible offline scripts for posterior diagnostics tied to the same constants as runtime.

This playbook is the default working agreement for Bayesian inference tasks assigned to the team.
