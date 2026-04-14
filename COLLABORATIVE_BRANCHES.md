# Collaborative Team Branches Convention

> **Effective:** April 14, 2026  
> **Status:** Active Consensus  
> **Teams:** Claude, Antigravity, Cursor (and future teams)

## Overview

This document establishes the standard naming convention and workflow for **collaborative team master branches** in this repository. Each team working on this project maintains its own master branch following a consistent pattern, enabling parallel development while keeping the main branch stable.

## Branch Naming Convention

All collaborative team master branches MUST follow this pattern:

```
master-<team-name>
```

Where `<team-name>` is the lowercase identifier of the team.

### Approved Teams

| Team | Branch | Status |
|------|--------|--------|
| Claude | `master-claude` | ✅ Active |
| Antigravity | `master-antigravity` | ✅ Active |
| Cursor | `master-cursor` | ✅ Active |

### Future Teams

New teams requesting to join MUST create their own `master-<team-name>` branch following this convention before beginning collaborative work. Register here (update this table).

## Workflow Rules

### 1. Team Master Branch Responsibilities

Each `master-*` branch:

- **Consolidates** all active work from team members into a stable collaborative workspace
- **Merges backwards** to `main` only when the work is ready for release/review (via PR)
- **Does NOT require all commits to be merged** — feature branches off a team master are normal
- **Should be production-ready or near-ready** when merged to main

### 2. Starting New Feature Work

When starting a feature as a team:

```bash
# Check out from the team master, not main
git checkout master-claude
git pull origin master-claude
git checkout -b feature/your-feature-name
```

### 3. Integrating Changes into Team Master

When a feature is ready:

```bash
git checkout master-claude
git pull origin master-claude
git merge --no-ff feature/your-feature-name
git push origin master-claude
```

### 4. Merging Team Master to Main

Only merge a team master to `main` when:

- ✅ All features are complete and tested
- ✅ CI passes
- ✅ Documentation is updated
- ✅ Code review is complete

Use a **Pull Request**:

```bash
# Ensure team master is up to date
git checkout master-claude
git pull origin master-claude

# Create PR to main with clear description of changes
gh pr create --base main --head master-claude \
  --title "feat: [team] descriptive title" \
  --body "Summary of team work..."
```

### 5. Avoiding Conflicts Between Teams

- **No cross-team merges** into each other's master branches
- Each team owns their `master-*` branch
- Conflicts happen only when merging to `main` (resolve then)
- If teams need to share code, do it via `main` (merge team master to main, then other team pulls from main)

## Examples

### Example 1: Claude Team Adding a Bayesian Feature

```bash
# Start from team master
git checkout master-claude
git pull origin master-claude

# Create feature branch
git checkout -b feature/bayesian-level-4

# ... work and commit ...

# Merge back to team master
git checkout master-claude
git merge --no-ff feature/bayesian-level-4
git push origin master-claude
```

### Example 2: Two Teams Sharing Code

**Team Claude** merges to main → **Team Antigravity** pulls from main:

```bash
# Claude: Merge ready work to main via PR
git checkout master-claude
gh pr create --base main --head master-claude

# Antigravity: Pull Claude's work via main
git checkout master-antigravity
git pull origin main  # Gets Claude's latest
git merge origin/main  # Integrate into Antigravity's work
```

## Historical Context

- **Before April 14, 2026:** Team branches used pattern `claude/feature-name`, `claude/another-feature`
- **April 14, 2026:** Consolidated all `claude/*` branches into single `master-claude`
- **Reason:** Clearer separation of team ownership, reduced branch clutter, easier to track team readiness

### Migration Notes

Old branches (`claude/upbeat-jepsen`, `claude/wizardly-bhabha`, `claude/friendly-wing`) are now **deprecated**. Their content has been consolidated into `master-claude`. These branches may be deleted after the transition is confirmed.

## FAQ

**Q: Can a feature branch branch off a team master?**  
A: Yes! Feature branches should typically branch off the team master, not main.

**Q: What if two teams need to work on the same file?**  
A: Coordinate via `main` — merge team master to main when stable, then the other team integrates from main.

**Q: Can we have nested feature branches?**  
A: Keep it simple: `master-*` ← feature branches. Don't nest deeper unless essential.

**Q: What about release branches?**  
A: Releases are cut from `main` (not team masters). Bugfixes can be cherry-picked back to team masters if needed.

## Governance

This convention was established by consensus among all active teams:

- **Proposer:** Claude Team  
- **Reviewed by:** Project maintainers  
- **Effective date:** April 14, 2026  
- **Status:** Binding for all collaborative work on this repository

To propose changes to this convention, open an issue or PR and coordinate with all team leads.

---

**Next steps:** Antigravity and Cursor teams should create their `master-antigravity` and `master-cursor` branches following this same pattern.
