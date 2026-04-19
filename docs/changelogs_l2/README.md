# L2 wake-up register (Level 0 / Antigravity directive)

**Language:** English for durable records (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md)). Spanish coordination may appear in session orders from L0/L1.

## Purpose

This directory holds **wake-up entries** for Level 2 executing units **before** resuming code changes after a governance pause. It complements (does not replace) team sections in root [`CHANGELOG.md`](../../CHANGELOG.md).

## L0 order — 2026-04-19 (full pause)

Antigravity (L1) reported **AGENTS.md protocol drift**. Per **L0**:

1. **PAUSA TOTAL** — no further kernel/runtime code changes until wake-up is registered here.
2. **Close ephemeral branches** — delete local/remote topic branches that are not the team integration hub (`master-<team>`). Typical cleanup:
   - `git branch` (list) → `git branch -d <topic>` after merge or `git branch -D <topic>` only if abandoned.
   - Do **not** delete `main` or shared hubs without L0/L1 instruction.
3. **Adopt callsigns** — each L2 session uses one of: **Rojo**, **Azul**, **Naranja** (discipline, traceability, cross-team visibility).
4. **Register wake-up** — update [`WAKE_UP_REGISTRY_2026-04-19.md`](WAKE_UP_REGISTRY_2026-04-19.md) **before** touching code again.

## L1 audit responses (sovereign re-integration)

| File | Description |
|------|-------------|
| [`L1_AUDIT_RESPONSE_CURSOR_ROJO3_2026-04-19.md`](L1_AUDIT_RESPONSE_CURSOR_ROJO3_2026-04-19.md) | Antigravity (L1) three-question audit — identity (Rojo), territoriality (`PLAN_WORK_DISTRIBUTION_TREE`), logging commitment. |
| [`L1_AUDIT_RESPONSE_2026-04-19_CURSOR_ROJO.md`](L1_AUDIT_RESPONSE_2026-04-19_CURSOR_ROJO.md) | Alternate Cursor Rojo audit entry (same wave). |

## Callsign reference (L2)

| Callsign | Role (nominal) |
|----------|----------------|
| **Rojo** | Adversarial / gate / safety alignment lane (see also [`docs/collaboration/CURSOR_ROJO1.md`](../collaboration/CURSOR_ROJO1.md) lineage) |
| **Azul** | Integration / stability / hub-merge discipline |
| **Naranja** | Operator surface, docs/env parity, observability |

Units map callsigns to their **hub branch** and **charter** (e.g. [`CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md)) without creating duplicate normative files in `.cursor/rules/`.

## `[RULE: L1_SUPREMACY_INVOCATION]` — Stop & Sync

When an interface is unclear, you expect **collision with another team**, or L0 says **“Consulta a Antigravity”**, follow **[`L1_SUPREMACY_INVOCATION.md`](L1_SUPREMACY_INVOCATION.md)**:

1. **Stop** immediate code writes (including drive-by refactors).
2. **`git pull origin main`** (or rebase onto `origin/main` per hub policy) — then read the latest **`### Antigravity-Team Updates`** block in [`CHANGELOG.md`](../../CHANGELOG.md) (**L1 Pulse**).
3. Consult [`docs/proposals/`](../proposals/) and [`docs/adr/README.md`](../adr/README.md) for binding instructions.
4. If still blocked: create `docs/changelogs_l2/<UID>.md` with section **`[L1_SUPPORT_REQUIRED]`** (see template in that file).

L2 **executes** inside L1-defined boundaries; it does **not** invent architecture on top of this protocol.

## Canonical protocol

- **[`AGENTS.md`](../../AGENTS.md)** remains the durable entry point; **only Antigravity (L1)** edits `AGENTS.md` and `.cursor/rules/` unless L0 explicitly directs otherwise.
- **ONBOARDING:** [`ONBOARDING.md`](../../ONBOARDING.md)
- **Integration gate (Cursor hub):** [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)
- **Cursor rule of law (always-on):** [`.cursor/rules/l1-supremacy-and-audit.mdc`](../../.cursor/rules/l1-supremacy-and-audit.mdc)
