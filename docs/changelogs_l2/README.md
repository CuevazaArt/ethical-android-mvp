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
4. **Register wake-up** — append to [`WAKEUP_REGISTER.md`](WAKEUP_REGISTER.md) **before** touching code again.

## Callsign reference (L2)

| Callsign | Role (nominal) |
|----------|----------------|
| **Rojo** | Adversarial / gate / safety alignment lane (see also [`docs/collaboration/CURSOR_ROJO1.md`](../collaboration/CURSOR_ROJO1.md) lineage) |
| **Azul** | Integration / stability / hub-merge discipline |
| **Naranja** | Operator surface, docs/env parity, observability |

Units map callsigns to their **hub branch** and **charter** (e.g. [`CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md)) without creating duplicate normative files in `.cursor/rules/`.

## Canonical protocol

- **[`AGENTS.md`](../../AGENTS.md)** remains the durable entry point; **only Antigravity (L1)** edits `AGENTS.md` and `.cursor/rules/` unless L0 explicitly directs otherwise.
- **ONBOARDING:** [`ONBOARDING.md`](../../ONBOARDING.md)
- **Integration gate (Cursor hub):** [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)
