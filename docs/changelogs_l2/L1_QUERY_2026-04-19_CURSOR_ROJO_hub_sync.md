# L2 support note — 2026-04-19 — Cursor Rojo (hub sync / seal)

**Language:** English (durable record per [`CONTRIBUTING.md`](../../CONTRIBUTING.md)).

## [L1_SUPPORT_REQUIRED]

- **Context:** Team Cursor merged `origin/main` into `master-Cursor`, resolved conflicts (narrative Phase 13 from `main`; Cursor chat/perception path preserved where intended). **`scripts/seal_manifest.py`** was aligned with **`SecureBoot.compute_file_hash`** (RoT anchor prefix) so `src/MANIFEST.json` matches runtime secure boot. Smoke tests passed; branch **pushed** to `origin/master-Cursor` (merge commit `ebd308e`).

- **Interface / collision:** `.cursor/rules/02-autonomous-git.mdc` instructs **PULL-REBASE-FIRST** before push. Running **`git rebase origin/main`** from `master-Cursor` attempted to replay a **very long** series of commits (not a short linear tip) and produced conflicts on early history. The rebase was **aborted**; the integration path used was **`git merge origin/main`** (already completed and pushed).

- **What was read:** Latest **`### Antigravity-Team Updates`** in root [`CHANGELOG.md`](../../CHANGELOG.md); [`L1_SUPREMACY_INVOCATION.md`](L1_SUPREMACY_INVOCATION.md); [`AGENTS.md`](../../AGENTS.md) (integration funnel `master-antigravity` → `main`).

- **Question for Antigravity (L1):**
  1. For **long-lived hub branches** (`master-Cursor`, etc.) that periodically absorb `main`, should L2 treat **`git merge origin/main`** as the **supported** sync when **`git rebase origin/main`** would replay an unbounded commit count and risk mass conflicts?
  2. Is **`master-Cursor` → `master-antigravity` PR** acceptable **now** (post-merge, seal fix), or should **`run_cursor_integration_gate.py`** / full adversarial suite be **green on record** before opening the PR?

- **Hub branch:** `master-Cursor`

---

**Registered by:** Cursor Rojo (L2), 2026-04-19.
