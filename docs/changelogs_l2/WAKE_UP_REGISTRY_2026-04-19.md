# L2 wake-up registry — 2026-04-19 (L0 directive)

**Status:** PAUSE TOTAL — **no further product code** until each active callsign row is complete and L1 clears the compliance gap.

**Directive (L0):** Antigravity (L1) reports **non-compliance with [`AGENTS.md`](../../AGENTS.md)**. Level 2 units shall: (1) **close ephemeral branches**, (2) **adopt callsigns** — **Rojo**, **Azul**, **Naranja**, (3) **record wake-up here** in `docs/changelogs_l2/` **before any further code changes**.

**Hub (Team Cursor):** `master-Cursor` — integration funnel per [`AGENTS.md`](../../AGENTS.md) (PRs to `master-antigravity`, never direct to `main` without L0).

---

## Compliance checklist (all L2 agents)

- [x] Re-read [`AGENTS.md`](../../AGENTS.md) (read-first links, 3 Laws of Contribution, MERGE-PREVENT-01, adversarial suite before `master-antigravity`).
- [x] Re-read [`ONBOARDING.md`](../../ONBOARDING.md) (presentation, hub branch, protocols).
- [x] Ephemeral / topic branches **merged or deleted** locally where already merged into `master-Cursor`; work consolidates on **`master-<team>`** hub. *(Remote topic branches on `origin` are left to L1 / repo admin unless team policy requires deletion.)*
- [x] No edits to `.cursor/rules/` or **`AGENTS.md`** from L2 without L1/L0 (sovereignty rule).

---

## Callsign registry

| Callsign | Unit / lane (declared) | Wake-up (UTC date) | Operator / agent id | Notes |
|----------|-------------------------|----------------------|----------------------|--------|
| **Rojo** | Adversarial validation / red-team lane ([`docs/collaboration/CURSOR_ROJO1.md`](../collaboration/CURSOR_ROJO1.md)) | 2026-04-19 | **Cursor Rojo3** | L0 pause acknowledged. Integration gate + [`python scripts/eval/adversarial_suite.py`](../../scripts/eval/adversarial_suite.py) before any PR toward `master-antigravity` per `AGENTS.md`. |
| **Azul** | Hub alignment / rebase-first / PR hygiene toward `master-antigravity` | 2026-04-19 | **Pending** | *Adopt this callsign in your session and add your id (e.g. Cursor Azul1).* |
| **Naranja** | CI / operator visibility / metrics and traceability | 2026-04-19 | **Pending** | *Adopt this callsign in your session and add your id (e.g. Cursor Naranja1).* |

### Local ephemeral branches closed (Team Cursor, this clone)

The following local branches were **fully merged into `master-Cursor`** and **deleted** (`git branch -d`): `cursor-team`, `cursor/claude-bi-p0-01-bayesian-mode-contract`, `cursor/g-04-llm-touchpoint-surface`.

---

## Attestation

By listing a callsign above, the executing unit attests that:

1. Ephemeral branches used for the prior sprint are **closed or merged** into the team hub.
2. Further work will follow **`AGENTS.md`**, [`CONTRIBUTING.md`](../../CONTRIBUTING.md), and team charter docs until L1 lifts the pause.

**L1 (Antigravity) audit:** Pending re-validation of hub hygiene and `CHANGELOG.md` namespace discipline.
