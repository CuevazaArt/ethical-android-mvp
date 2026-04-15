# Multi-office Git workflow (*Time worth flow — cycle develop*)

This note **institutionalizes** a Git branching pattern for **distributed teams** (several local offices or agent pools) that share one GitHub repository. It is the same **conceptual model** as the team diagram below.

![Time worth flow — cycle develop: production main, team integration branch, local offices merge inward, then promote to main](./git-workflow-time-worth-flow-cycle-develop.png)

## Purpose

- Give **analogous teams** a **single, copyable convention**: where to integrate day to day, how locals relate to production, and how promotion to `main` is supposed to happen.
- Keep **production** (`main`) **stable and reviewable**, while allowing **parallel work** on a team integration line.

## Branch model (generic)

| Layer | Branch pattern | Role |
|--------|----------------|------|
| **Production** | `main` | Canonical line on GitHub. Treat as **production**: public-facing material that lives on this line (for example marketing or reference pages), bibliography, and **all merged repo-facing text** must follow the **English-only** merge policy in [`CONTRIBUTING.md`](../../CONTRIBUTING.md). |
| **Team integration** | `master-<TeamSlug>` | Hub for a named team (replace `<TeamSlug>` with a short identifier, e.g. `Cursor`, `LabEast`). Cut from `main`. **Local offices merge here** when work is ready for the shared line—not directly to `main` unless maintainers say otherwise. |
| **Shared team work** | `<team-slug>-team` | Optional but recommended: day-to-day branch cut from `master-<TeamSlug>` (use a **lowercase slug**, e.g. `cursor-team`). Multiple clones pull this line (or topic branches from it), then integrate back into `master-<TeamSlug>`. |

**Example (this repository, Cursor org):** `master-Cursor` ← from `main`; historical shared line `cursor-team` ← from `master-Cursor` (**deprecated** — see below).

### This repository — active line (2026)

- **Integration hub:** **`master-Cursor`** is the **active** branch for Cursor org work; merge reviewed changes here (or open PRs into it).
- **Deprecated:** the separate branch name **`cursor-team`** is **no longer** the default day-to-day line. Prefer **topic branches from `master-Cursor`** (or short-lived forks) and integrate back into **`master-Cursor`**. Do not rely on new work landing only on `cursor-team`.

## Operations (summary)

1. **Refresh integration from production** — Regularly align `master-<TeamSlug>` with `main` (diagram “clone” / sync: e.g. merge or rebase from `origin/main` per team policy) so the hub does not drift from production intent.
2. **Locals → integration** — Each office merges reviewed work into `master-<TeamSlug>` (or opens PRs into it).
3. **Integration → production** — Promotion `master-<TeamSlug>` → `main` is a **maintainer / release** action (merge or rebase per policy). Follow normal PR review and [`CONTRIBUTING.md`](../../CONTRIBUTING.md).

Exact commands depend on branch protection and remote layout; prefer the same patterns as the rest of the project.

## Agent and IDE guidance

For **Cursor** and other agents, the durable rule text (redundancy checks, safety expectations, and this workflow) lives in:

- [`.cursor/rules/collaboration-prioritization.mdc`](../../.cursor/rules/collaboration-prioritization.mdc)
- **Generalized onboarding pack:** [`COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md`](COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md) (required reading order, task card, DoD, and quality gate references).
- **Cursor integration gate:** [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) (cross-team interlace readiness and reproducible checks).

## Language policy reminder

- **Human collaboration** may use **Latin American Spanish** (and other languages) off-repo.
- **Everything merged into this repository** remains **English** unless an explicit exception applies (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md)).
