# Collaborative Method Generalization Guide

This guide consolidates the shared collaboration method for **multi-origin local teams** and provides a reusable onboarding pack for any office working on this repository.

For an exportable, executive-friendly version of the same operating model, see
[`SWARM_WORK_MODEL_MANIFESTO.md`](SWARM_WORK_MODEL_MANIFESTO.md).
For a formal long-form reference intended for cross-organization adoption, see
[`WHITEPAPER_SWARM_OPERATING_MODEL.md`](WHITEPAPER_SWARM_OPERATING_MODEL.md).

## 1) Required reading pack (before implementation)

Every contributor (human or agent) should review, in this order:

1. [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — language, process, quality gates, traceability.
2. [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md) — branch roles and promotion flow.
3. [`AGENTS.md`](../../AGENTS.md) — durable expectations for integrated fixes.
4. [`.cursor/rules/`](../../.cursor/rules/) — always-on rules (prioritization, documentation discipline, language policy).
5. Team playbooks under `docs/proposals/` for active scopes.
6. [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](../proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) — when changing or tuning **LLM recovery** env vars (`KERNEL_LLM_TP_*`, verbal family, perception/verbal legacy keys), use this matrix so staging and production stay aligned.

## 2) Non-negotiable working principles

- **Redundancy check first:** do not duplicate open or recently merged work.
- **Novelty and coverage:** prioritize less-covered, higher-leverage gaps unless critical regressions require immediate action.
- **Repository language policy:** collaboration may be Spanish; merged repository artifacts are English (except explicit fixture/security exceptions).
- **Traceability over chat memory:** close the loop in code, tests, docs, and changelog.

## 3) Branch discipline (generalized)

- `main`: production line.
- `master-<TeamSlug>`: team integration hub.
- `<team-slug>-team`: day-to-day collaborative line.

Promotion flow: `<team-slug>-team` -> `master-<TeamSlug>` -> `main` (maintainer release action).

## 4) Shared task card format

Use this template in issues and PR descriptions:

```text
ID:
Source:
Track label:
Risk class:
Redundancy check:
Owner office:
Target branch:
Definition of done:
Evidence links:
```

## 5) Definition of done (minimum)

An item is complete only when:

1. Code behavior is implemented with named defaults (when relevant).
2. Tests lock defaults and override paths.
3. Minimal, correct docs are updated (proposal or ADR when needed).
4. `CHANGELOG.md` records operator-visible impact.
5. Branch integration follows the multi-office workflow.

## 6) Style and quality resources (share this pack)

Use and share these references across local offices:

- `python -m ruff check src tests`
- `python -m ruff format --check src tests`
- `python -m mypy src`
- `python -m pytest tests/ -q --tb=short`

If a team adopts internal checklists, keep them aligned to this pack to avoid drift.

## 7) Generalization protocol for new teams

When a new team scope starts:

1. Create a scope playbook under `docs/proposals/` with mission, scope, backlog, and DoD.
2. Link it from `docs/proposals/README.md`.
3. Add a concise changelog entry for discoverability.
4. Reuse this guide’s task card and branch discipline.

This document is intended as the common baseline to keep collaboration orderly as contributors and origins increase.
