# Merge and hub decision tree (quick reference)

**Purpose:** Remove ambiguity between **your team integration hub**, **peer `master-*` hubs**, and **Antigravity staging** before `main`. Complements [`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md) Rule C-1 and [`.cursor/rules/collaboration-prioritization.mdc`](../../.cursor/rules/collaboration-prioritization.mdc).

**Authority:** Promotion to **`main`** is **only** with **Juan (L0)** approval per [`CONTRIBUTING.md`](../../CONTRIBUTING.md) and collaboration rules.

---

## Where does my day-to-day work land?

| Question | Answer |
|----------|--------|
| I work on a **feature** for my team | Cut a **topic branch** from **`master-<YourTeam>`** (e.g. `master-Cursor`). Open a **PR** into `master-<YourTeam>` when ready. |
| I need **my team’s shared line** updated | Merge **into `master-<YourTeam>`** after review — not directly to `main`. |
| I need **another team’s** recent commits | **Fetch** and **merge (or rebase)** **peer** `origin/master-*` **into your current branch or hub** per Rule C-1 — *after* checking for conflicts. See [`scripts/git/sync_peer_masters_preview.sh`](../../scripts/git/sync_peer_masters_preview.sh) / [`.ps1`](../../scripts/git/sync_peer_masters_preview.ps1). |
| Code should move toward **release** | **Level-2** teams funnel completed blocks into **`master-antigravity`** (L1 integration) **before** `main` promotion, per always-on collaboration rule. Exact timing is a **maintainer / merge window** decision. |
| I need **`main`** updated | **Do not** push to `main` without **explicit L0 authorization**. Open a **PR** to `main` when maintainers agree. |

---

## Order of operations (typical session)

1. **`git fetch origin`**
2. **Inspect** what peer `master-*` branches have that you do not ([`scripts/git/sync_peer_masters_preview.*`](../../scripts/git/))
3. If clean, **merge** peer increment with message `merge(sync): …` (see [`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md))
4. **Rebase or merge `origin/main` into your hub** regularly so production intent does not drift (same workflow doc, step “Refresh integration from production”)
5. Do **your** topic work; **PR** to your **`master-<team>`**
6. **`main`** only via **L0-approved** promotion path

---

## When to stop and coordinate

- **Conflicts** expected in files you are both editing → **issue / thread**, not a blind merge.
- **Unclear** whether Antigravity has already integrated the same change → **check `git log`** and proposals before duplicating work.

---

## Minimum Integration Pulse triggers (R-3)

“Pulse often” becomes actionable if you **sync peer hubs when any** of the following is true (pick what applies; not a calendar mandate):

| Trigger | Action |
|---------|--------|
| You are about to open a **PR** that edits the **top** of [`CHANGELOG.md`](../../CHANGELOG.md) (monthly / team section) | Run peer preview ([`sync_peer_masters_preview.*`](../../scripts/git/)), then merge peers into your hub **before** your PR, or coordinate to avoid `CHANGELOG` collisions. |
| Your PR touches **[`src/kernel.py`](../../src/kernel.py)** (or another shared orchestrator many teams edit) | Same: preview + merge or align in chat **first**. |
| Your hub has been **idle** while other `master-*` branches moved (you are unsure) | Run preview at **session start**; if `git log HEAD..origin/master-<peer>` is non-empty, plan a sync. |
| **End of a logical block** (guardrails, ADR-sized change) | Integration Pulse per [`.cursor/rules/collaboration-prioritization.mdc`](../../.cursor/rules/collaboration-prioritization.mdc): land tests + `CHANGELOG` + proposal pointer on your **`master-<team>`** before starting unrelated work. |

If **none** of these apply and you only touched an isolated module + docs, a full peer merge may still be optional—but do not let hubs diverge for **weeks**.

---

## Direct push to `master-<team>` vs PR (R-4)

Fast pushes happen. **Maintainer-expected hygiene** (not enforced in CI):

- Prefer a **PR** into `master-<team>` for anything non-trivial.
- If you **pushed directly** to the team hub, add a **follow-up PR or linked issue within 24 hours** summarizing commits and rationale (or reference the task card / proposal ID). This preserves reviewability without blocking hotfixes.

---

## Optional pre-push checks (hubs with frequent doc / merge churn)

Before **`git push`** to a shared `master-*` integration branch (especially after resolving merges or editing `CHANGELOG.md`):

- **Merge markers:** ensure no unresolved `<<<<<<<` / `=======` / `>>>>>>>` in tracked files.
- **Collaboration invariants (optional):** `python scripts/eval/verify_collaboration_invariants.py` — merge-marker scan + `CHANGELOG` namespace heuristic (see [`.cursor/rules/l1-supremacy-and-audit.mdc`](../../.cursor/rules/l1-supremacy-and-audit.mdc) for L1 gate expectations).

This does not replace CI or `pytest`; it is a fast local guard for **documentation and merge hygiene**.

---

## Merge commit message convention (R-5)

Use a **prefix** so `git log --oneline` distinguishes sync noise from promotion work:

| Prefix | When |
|--------|------|
| `merge(sync): …` | Catching up **peer** `master-*` (Rule C-1). |
| `merge(integration): …` | Merging **from** `master-antigravity` (or L1 staging) **into** a team hub **after** L1 stabilization—*promotion prep*, not routine peer drift. |
| `merge(main): …` | Refreshing your hub **from** `origin/main` to align with production. |

---

*Derived from [`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](../critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md) recommendations R-1, R-3, R-4, R-5.*
