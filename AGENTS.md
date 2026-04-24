# Agent and Contributor Orientation (Ethos Kernel)

This file is the entry point for humans and AI assistants working in this repository.

## Read first

- **[`CONTEXT.md`](CONTEXT.md) — START HERE.** Current state, open tasks, key files. (~30 lines — saves tokens.)
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — language policy, process, tests, lint, documentation traceability.
- [`docs/architecture/TRI_LOBE_CORE.md`](docs/architecture/TRI_LOBE_CORE.md) — Mermaid diagrams for cognitive flows.
- [`docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`](docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md) — full backlog history (mostly closed blocks).

## Authority

1. **Juan (L0):** Absolute authority. Only person who can merge to `main`.
2. **Project rules:** This file + `CONTRIBUTING.md` define the normative framework. Rules are enforced by CI and L0 review.
3. **AI agents:** Stateless executors. Pick tasks from the backlog, execute, commit, move on. No permission needed for internal module work.

## Git workflow

1. **Before writing code:** `git pull origin main --rebase`
2. **Never push to `main` directly.** All work goes to feature branches or integration hubs.
3. **Squash merge to `main`** is L0-only.
4. Use `scripts/swarm_sync.py --block <ID> --msg "<description>"` to commit and log completed blocks.

## Code quality rules (Boy Scout)

Every intervention must proactively apply:

1. **Harden-In-Place:** Fill empty `try/except` blocks, add type hints, sanitize inputs.
2. **Anti-NaN:** If you touch math or latency logic, ensure results cannot be `NaN` or `Inf`. Use `math.isfinite()`.
3. **Latency metrics:** New loops or sensory paths must log latency with `time.perf_counter()`.
4. **Zero dead code:** If you find obsolete mocks, legacy stubs, or replaced code — delete it.

## Architectural guardrails

A `PROPOSAL_*.md` in `docs/proposals/` is required BEFORE:
- Modifying inter-lobe interfaces (`src/kernel_lobes/models.py`)
- Adding major external dependencies
- Altering the `CorpusCallosumOrchestrator` or `EthicalLobe` gating logic

Internal module improvements, optimizations, and bug fixes do NOT need proposals.

## Security gate

Run `python scripts/eval/adversarial_suite.py` periodically (recommended: every 3 completed blocks). No new features until security tests pass with 0 failures.

## Documentation

- Update `CHANGELOG.md` for user-visible or architecture-relevant changes.
- Update Mermaid diagrams in `docs/architecture/` when modifying inter-lobe logic.
- Keep claims aligned with `docs/TRANSPARENCY_AND_LIMITS.md`.
- All repository content must be in **English** (per `CONTRIBUTING.md`).

## Integrate solutions, not explanations

When fixing security-critical behavior (thresholds, gates, circuit limits):
1. Named module defaults (`DEFAULT_*`) and tests that lock them.
2. Honest `docs/proposals/PROPOSAL_*` text when evidence is needed.
3. `CHANGELOG.md` entry when operators need to see the change.

## Disclaimer

Any reference to third-party trademarks is purely for descriptive purposes and does not imply affiliation or endorsement.
