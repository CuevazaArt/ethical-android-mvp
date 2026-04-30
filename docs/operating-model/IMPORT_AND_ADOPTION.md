# Import and Adoption Guide

Use this checklist to import the operating model into another repository, IDE, or organization.

## Option A: Fast bootstrap (copy/paste)

Copy these files into the target repo under `docs/operating-model/`:

- `WHITEPAPER_SWARM_OPERATING_MODEL.md`
- `SWARM_WORK_MODEL_MANIFESTO.md`
- `COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md`
- `MULTI_OFFICE_GIT_WORKFLOW.md`
- `MERGE_AND_HUB_DECISION_TREE.md`
- `MER_V2_POSTULATE.md`

Then update internal links so paths are correct in the target repository.

## Option B: Controlled adoption (recommended)

1. Create a branch in the target repository.
2. Add the operating-model docs in one commit.
3. Open a PR for review with:
   - role mapping (L0/L1/executors -> local equivalents),
   - branch mapping (`main`, integration hubs, feature branches),
   - CI economy mapping (code-change vs docs-only behavior),
   - quality gate command mapping (lint/type/test commands).
4. Merge only after tool owners and release owners approve governance details.

## IDE and platform portability

The model is IDE-agnostic and works with:

- Cursor
- VS Code
- JetBrains IDEs
- terminal-only workflows

It is also CI-platform agnostic:

- GitHub Actions
- GitLab CI
- Jenkins
- Azure Pipelines
- Buildkite

The policy is portable; only syntax changes between platforms.

## Minimum required invariants (do not remove)

1. Protected production promotion.
2. Evidence-based block closure.
3. Pre-push quality gate.
4. Safety-critical full-pattern delivery (code + tests + docs + changelog).
5. Repository-first traceability.

Without these invariants, the method degrades into ad hoc process text.
