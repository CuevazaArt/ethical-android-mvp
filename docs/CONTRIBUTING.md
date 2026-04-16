# Contributing to Ethos Kernel

This guide supplements the repository README and ADR index. It is normative for all contributors — human and AI alike.

---

## Language policy

| Location | Language |
|----------|----------|
| All source code, docstrings, test identifiers, comments | **English** |
| ADRs, proposals, deploy docs, changelogs | **English** |
| Internal discussion, planning, review notes | Spanish Latino (team default) |

---

## Branch naming

```
<type>/<short-slug>          # e.g. feat/hierarchical-updater
fix/<issue-slug>
chore/<task-slug>
claude/<worktree-name>       # AI-agent worktrees (auto-named)
```

---

## Commit message style

```
<type>(<scope>): <imperative summary>

Body (optional): what changed and why.
Breaking changes prefix body with "BREAKING CHANGE:".

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>   # when AI-assisted
```

Types: `feat` `fix` `refactor` `test` `docs` `chore` `perf` `ci`.

---

## GitHub tag / release convention

Tags mark **stable, auditable snapshots** of the system.  
They are the primary mechanism for reproducibility, external audit, and rollback.

### When to create a tag

A tag **must** be created when any of the following occurs:

| Trigger | Tag format | Example |
|---------|-----------|---------|
| A new ADR moves from *Proposed → Accepted* **and** its implementation is merged and all tests pass | `adr/<number>-<slug>` | `adr/0012-bayesian-weight-inference` |
| A major architectural refactor lands (kernel pipeline, new module category, schema migration) | `refactor/<YYYY-MM>-<slug>` | `refactor/2026-04-inference-stack` |
| A milestone from the practical roadmap is achieved (Phase 0 complete, Phase 1 complete…) | `milestone/<phase>-<YYYY-MM>` | `milestone/phase1-2026-04` |
| A research experiment produces a reproducible result set (mass study, sensitivity sweep) | `experiment/<version>-<YYYY-MM-DD>` | `experiment/v5-2026-04-12` |
| A production release candidate | `v<semver>-rc<N>` | `v0.9.0-rc1` |
| A production release | `v<semver>` | `v0.9.0` |
| A significant safety/governance boundary change (absolute-evil list, governance constants) | `safety/<YYYY-MM>-<slug>` | `safety/2026-04-malabs-hardening` |

### When **not** to create a tag

- Routine commits (docs typos, test fixture additions, chore changes).
- Work-in-progress branches or worktrees.
- Partial implementations where tests do not fully pass.

### How to create a tag

```bash
# Annotated tag (required — lightweight tags are not accepted for audit)
git tag -a adr/0012-bayesian-weight-inference \
    -m "ADR 0012 accepted: Bayesian mixture weight inference (Levels 1-3 + Phase D)"
git push origin adr/0012-bayesian-weight-inference
```

The annotation message must include:
1. ADR/milestone/experiment reference.
2. One-line summary of what the tag represents.
3. Test status at tag time ("all tests passing", "N tests passing / M skipped").

### Tag lifecycle rule

Tags are **immutable** once pushed to `origin`.  
If a tagged commit is found to have a critical defect:
1. Fix forward in a new commit.
2. Create a new tag with a `-hotfix` suffix.
3. Never delete or force-move a tag that has been pushed.

### Viewing tags

```bash
git tag -l "adr/*"          # all ADR tags
git tag -l "experiment/*"   # all experiment snapshots
git show adr/0012-bayesian-weight-inference  # annotation + commit
```

---

## ADR lifecycle

1. **Proposed** — draft in `docs/adr/`; may have partial or no implementation.
2. **Accepted** — implementation merged, all tests passing; tag `adr/<n>-<slug>` created.
3. **Superseded** — replaced by a newer ADR; original file kept with forward link.
4. **Deprecated** — feature removed; file kept for audit trail.

---

## File placement

| Artifact | Location |
|----------|----------|
| Architecture decision records | `docs/adr/` |
| Operator proposals / design notes | `docs/proposals/` |
| Experiment scripts (non-CI, long-running) | `scripts/` |
| Experiment outputs (JSONL, CSV, reports) | `experiments/out/` *(gitignored)* |
| Deploy assets (Compose, Grafana, Dockerfiles) | `docs/deploy/` + repo root |
| Source modules | `src/modules/` |
| Sandbox / research utilities | `src/sandbox/` |
| Simulation fixtures | `src/simulations/` |
| Feedback fixtures for tests | `tests/fixtures/feedback/` |

When adding a new category that does not fit any existing folder, note it here so future collaborators understand the decision.

---

## New modules checklist

- [ ] Module has a module-level docstring explaining purpose, env vars, and ADR reference.
- [ ] Public symbols are in `__all__`.
- [ ] At least one test in `tests/test_<module_name>.py`.
- [ ] `src/modules/__init__.py` updated if the module is part of the public API.
- [ ] `.env.example` updated with any new `KERNEL_*` variables (commented).
- [ ] ADR created or updated if the module changes system behavior.

---

## Out-of-spec situations register

Known gaps and situations requiring future resolution are tracked in
[`docs/OUT_OF_SPEC.md`](OUT_OF_SPEC.md).  
When you detect an architectural gap, a broken invariant, or a known compromise,
add an entry there rather than leaving a `TODO` comment buried in code.

---

*Ethos Kernel — Contributing guide, April 2026.*
