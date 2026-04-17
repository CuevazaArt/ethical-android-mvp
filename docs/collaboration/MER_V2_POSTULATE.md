# MER V2 postulate — multi-team exchange ritual (normative bundle)

**Status:** Working label for documentation and cross-team briefings. **Not** a second governance authority: L0/L1 rules in [`AGENTS.md`](../../AGENTS.md) and [`.cursor/rules/collaboration-prioritization.mdc`](../../.cursor/rules/collaboration-prioritization.mdc) remain authoritative.

**MER V2** (**M**ulti-team **E**xchange **R**itual, revision **2**) is the **name** for the collaboration package that **stabilized after** the one-time regulation critique ([`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](../critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md)) and the quick-reference decision tree. On `master-antigravity` and aligned hubs, the same ideas appear under **Integration Funnel**, **Integration Pulse**, **MERGE-PREVENT-01**, and recommendations **R-1–R-5** — MER V2 is a **single umbrella term** for onboarding and release notes.

---

## What MER V2 asserts (testable)

| Element | Where it lives |
|--------|----------------|
| Hub vs `main` vs L1 staging | [`MERGE_AND_HUB_DECISION_TREE.md`](MERGE_AND_HUB_DECISION_TREE.md) |
| Peer `master-*` sync (Rule C-1) | [`MULTI_OFFICE_GIT_WORKFLOW.md`](MULTI_OFFICE_GIT_WORKFLOW.md) |
| **Minimum Integration Pulse** triggers (R-3) | [`MERGE_AND_HUB_DECISION_TREE.md`](MERGE_AND_HUB_DECISION_TREE.md) § *Minimum Integration Pulse triggers* |
| Direct push hygiene (R-4) | Same doc § *Direct push to `master-<team>` vs PR* |
| Merge commit prefixes `merge(sync):` / `merge(integration):` / `merge(main):` (R-5) | Same doc § *Merge commit message convention* |
| Anti–merge-hell rules | [`AGENTS.md`](../../AGENTS.md) § *Cross-Team Conflict Prevention (MERGE-PREVENT-01)* |
| Optional local guard | `python scripts/eval/verify_collaboration_invariants.py` (see decision tree) |

---

## Critical review (limitations)

1. **L1 throughput:** Serializing merges through `master-antigravity` reduces collisions but can **queue** work when L1 review is slow. Mitigation already sketched in [`AGENTS.md`](../../AGENTS.md) (*Antigravity Fast-Track* toward `master-antigravity` when tests are green); teams should still **not** bypass the staged hub for `main`.
2. **Soft R-4:** The 24h follow-up PR/issue after a direct push is **policy**, not CI. **Drift risk** if teams forget; leads should spot-check `git log` on hub branches.
3. **Optional peer sync:** R-3 triggers are **conditional**; hubs can still diverge if nobody runs [`scripts/git/sync_peer_masters_preview.sh`](../../scripts/git/sync_peer_masters_preview.sh) / [`.ps1`](../../scripts/git/sync_peer_masters_preview.ps1). **Practical default:** run at **session start** when any shared file (`CHANGELOG.md`, `src/kernel.py`) might be touched.
4. **Naming:** “MER V2” does **not** appear as a string on every branch; this file is the **canonical** definition so agents can grep `MER_V2_POSTULATE.md` instead of guessing acronyms.

---

## Sync checklist for `master-*` teams (Cursor, Claude, Copilot, Visual Studio, …)

1. `git fetch origin`
2. Preview peers: `scripts/git/sync_peer_masters_preview.ps1` (or `.sh`)
3. Merge needed peer hubs into **your** `master-<team>` with `merge(sync): …` when taking their work
4. Refresh from `origin/main` periodically (`merge(main): …`) so production intent does not drift
5. Land logical blocks on your hub (tests + `CHANGELOG` + proposal pointer) before starting unrelated work
6. Open PR **to `master-antigravity`** when the block is ready for L1 integration; **`main`** only with **L0** approval

---

## Relation to other “MER*” strings in the repo

- **MERGE-PREVENT-01** in [`AGENTS.md`](../../AGENTS.md) is a **concrete rule set** (anti-duplication, CHANGELOG islands, staggered integration). MER V2 **includes** it as part of the normative bundle.
- **MER** in other contexts (e.g. “merge” in prose) is unrelated; use this document’s title when you mean **MER V2**.

---

*Last aligned with `origin/master-antigravity` collaboration docs (decision tree, multi-office workflow, critique R-1–R-5). Update this file if L1 renames the bundle or adds CI enforcement for R-4.*
