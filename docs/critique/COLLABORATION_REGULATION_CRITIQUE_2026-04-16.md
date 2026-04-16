# Collaboration regulation — design critique (Antigravity multi-team model)

**Status:** Registered **once** (2026-04-16). **Do not duplicate** this exercise unless **Juan (L0)** explicitly requests a refresh. Updates to governance rules themselves remain the remit of authorized maintainers per [`.cursor/rules/collaboration-rule-authority.mdc`](../../.cursor/rules/collaboration-rule-authority.mdc).

**Subject:** The collaboration and Git workflow package institutionalized by the Antigravity-led integration model: [`.cursor/rules/collaboration-prioritization.mdc`](../../.cursor/rules/collaboration-prioritization.mdc), [`.cursor/rules/cross-team-conflict-prevention.mdc`](../../.cursor/rules/cross-team-conflict-prevention.mdc), [`.cursor/rules/team-task-synchronization.mdc`](../../.cursor/rules/team-task-synchronization.mdc), and [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md) (including Rule **C-1** incremental sync).

**Audience:** maintainers, L1 integrators, and Level-2 execution teams tuning *how* merges, commits, pushes, and pulls happen without renegotiating *who* owns `main`.

---

## 1. What the design gets right

1. **Clear separation of roles** — `main` as protected production, `master-<team>` as integration hubs, topic branches for work units. That matches how multiple agent pools and humans actually branch in one repo.
2. **Explicit L0 gate on `main`** — Avoids silent “agent promoted to production” narratives; aligns with honest shipping posture.
3. **Rule C-1 (fetch → inspect peer `master-*` → merge with `merge(sync):` prefix)** — Makes *pull discipline* legible in `git log`, not only in chat. The conventional commit subject prefix improves forensics when bisecting integration noise.
4. **Integration Pulse + Linearization Funnel** — Correct intuition: architectural conflicts should be resolved on a **staging** line (`master-antigravity` in the rule text) before `main`, and peer hubs should not diverge for long.
5. **Merge-prevention rules** — Team-scoped `CHANGELOG` subheaders, append-only edits on shared “god” files, and **staggered** integration reduce catastrophic `add/add` conflicts. These are operational, not ceremonial.
6. **Traceability expectation** — `docs/proposals/` + `CHANGELOG.md` for merged work closes the gap between chat and repository truth.

---

## 2. Friction and ambiguity (risks to flow)

### 2.1 Two “centers of gravity” in prose

The always-on rule describes a **single** funnel target (`master-antigravity`) for all Level-2 teams, while [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md) also centers **`master-Cursor`** as the active Cursor hub. New contributors can reasonably ask: *Is my daily integration target my team hub, Antigravity, or both?*

**Risk:** duplicate merges (same logical change merged twice through different paths) or skipped Antigravity staging because the mental model was “Cursor-only.”

### 2.2 Rule C-1 dry-run vs real merges

The workflow suggests `git merge --no-commit --no-ff` then `git merge --abort` for inspection. That is valid, but **easy to get wrong under stress** (abort forgotten, dirty tree, partial conflict state). The doc warns, but automation is thin.

**Risk:** accidental partial state or confusion when switching between dry-run and real merge in the same session.

### 2.3 “Every logical block” pulse frequency is subjective

“SHOULD frequently pull / merge peer `master-*`” lacks a **minimum observable cadence** (e.g., time-boxed sync window, or “before each PR that touches `src/kernel.py`”). Subjective frequency drifts to “when we remember.”

**Risk:** hubs diverge until a painful integration week; violates the original intent of Rule C-1.

### 2.4 PR discipline vs direct push to `master-<team>`

Rules mandate a GitHub PR cycle for traceability; many labs still **push directly** to integration branches when moving fast. The gap between *documented* and *actual* practice is not always acknowledged.

**Risk:** reviewers cannot reconstruct rationale; `CHANGELOG` entries become the only audit trail—good if present, brittle if forgotten.

### 2.5 Windows / PowerShell portability

Examples use bash `for` loops and `grep`. Contributors on Windows shells hit friction unless Git Bash or WSL is assumed.

**Risk:** Rule C-1 is skipped not by intent but by copy-paste failure.

---

## 3. Recommendations (incremental; no authority change)

These **do not** replace L0 approval for `main`; they tighten **coordination mechanics**.

| ID | Recommendation | Rationale |
|----|------------------|-----------|
| **R-1** | Publish a **one-page decision tree**: “If you are team X, default integration branch is `master-X`; Antigravity staging is required **before** `main` promotion, and peer sync is **into your hub** unless L1 declares a merge window.” Link it from `collaboration-prioritization.mdc` and `MULTI_OFFICE_GIT_WORKFLOW.md`. | **Done:** [`MERGE_AND_HUB_DECISION_TREE.md`](../collaboration/MERGE_AND_HUB_DECISION_TREE.md) (linked from [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md)). |
| **R-2** | Add a **optional script** (e.g. `scripts/git/sync_peer_masters.ps1` + `.sh`) that wraps: `git fetch origin`, lists `origin/master-*` not in `HEAD`, and exits non-zero on conflict dry-run—so agents and humans share one path. | **Partial:** [`sync_peer_masters_preview.sh`](../../scripts/git/sync_peer_masters_preview.sh) + [`.ps1`](../../scripts/git/sync_peer_masters_preview.ps1) — **read-only** preview (`git fetch` + `git log HEAD..peer`); no auto-merge. Conflict dry-run left to explicit `git merge --no-commit` per Rule C-1. |
| **R-3** | Define **minimum pulse triggers** (examples): before any PR touching `CHANGELOG.md` top section; before any PR touching `src/kernel.py`; or weekly for active hubs. Keep them as **triggers**, not arbitrary calendars. | Makes “frequent” measurable. |
| **R-4** | When direct push to `master-<team>` is used, require **PR within 24h** or a linked issue summarizing commits (maintainer policy). | Bridges fast execution and reviewability without banning push. |
| **R-5** | In integration merges, standardize not only `merge(sync):` but **`merge(integration):`** when merging **from** Antigravity staging into a team hub after L1 stabilization—distinguishes “peer catch-up” from “promotion prep.” | Cleaner archaeology in `git log`. |

---

## 4. Relation to existing automation

- **Cursor integration gate:** [`scripts/eval/run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) already encodes a **reproducible** subset of cross-team readiness; expand references from collaboration docs so “gate green” is treated as a **sync checkpoint**, not a side quest.
- **Collaboration invariants:** [`scripts/eval/verify_collaboration_invariants.py`](../../scripts/eval/verify_collaboration_invariants.py) supports merge-marker and `CHANGELOG` namespace checks—surface these in onboarding as **pre-push** hooks for hubs that see frequent doc churn.

---

## 5. Closing

The Antigravity-shaped regulation is **directionally correct**: protected `main`, team hubs, peer pulls, staggered integration, and explicit traceability. The highest-leverage improvements are **clarifying the hub vs funnel story**, **lowering the cost of safe peer sync** (scripts + triggers), and **closing the PR vs push gap** with lightweight accountability—without diluting L0 control of production.

---

*MoSex Macchina Lab — collaboration process critique. Registered 2026-04-16; single-shot unless L0 requests renewal.*
