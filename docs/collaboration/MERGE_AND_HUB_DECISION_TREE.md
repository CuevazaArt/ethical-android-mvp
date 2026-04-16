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

*Derived from [`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](../critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md) recommendation R-1.*
