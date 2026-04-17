# Contributing to Ethos Kernel

Thank you for your interest in contributing! This project needs people
with skills in AI/ML, computational ethics, blockchain, and robotics.

## How to contribute

### 1. Collaboration and work prioritization (multi-source)

Contributions may arrive through multiple channels (issues, pull requests, chat, and other collaborators). That diversity can produce **overlapping or de facto duplicate requests** for the same work.

**Before you start implementation**, you must:

1. **Check for redundancy** — Determine whether the change is already proposed, in progress, or recently merged. Review open issues and pull requests, search the codebase and `docs/`, and **coordinate with or extend existing work** instead of duplicating it.
2. **Prioritize novelty and coverage** — Prefer topics that are **newer** relative to the current model and **less covered** in the implementation or documentation, unless a critical fix, security issue, or regression requires otherwise.

These expectations **apply to all contributors** and are part of how we keep the project coherent.

**Multi-office Git workflow (optional convention for distributed teams):** See **[`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md)** — diagram, branch pattern (`main` → `master-<TeamSlug>` → local offices), and production (`main`) language expectations. **Quick hub / merge decision tree:** [`docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md`](docs/collaboration/MERGE_AND_HUB_DECISION_TREE.md). Cursor agents also load the always-on rule **[`.cursor/rules/collaboration-prioritization.mdc`](.cursor/rules/collaboration-prioritization.mdc)**.
**Generalized collaboration guide:** [`docs/collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md`](docs/collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md) — reading pack, reusable task-card format, and shared quality gates for multi-origin teams.

**Collaboration regulation critique (Antigravity multi-team design — registered once):** [`docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](docs/critique/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md) — improvements to merge / push / pull coordination; **not** re-run unless **Juan (L0)** requests it.

### Language policy (collaboration vs repository)

- **Collaboration:** We work day to day in **Latin American Spanish** (issues, chat, planning, and coordination with humans). Use clear, respectful Spanish; regional variants are fine as long as everyone understands.
- **Repository:** Everything **merged into this repository** must be **in English** — documentation under `docs/`, README, CHANGELOG, code comments, docstrings, user-facing strings, and proposal files (`PROPOSAL_*`). That keeps the codebase and docs consistent for international review and tooling.
- **Exception:** Deliberate non-English **test or security payloads** (e.g. multilingual abuse strings) are allowed; add a short comment if the intent is not obvious.

The same rules apply to AI assistants working on this repo (see `.cursor/rules/repo-language-policy.mdc`).

### 2. Understand the model
Read the README.md and run the simulations before proposing changes.
Canonical model and architecture references:

- [`docs/proposals/THEORY_AND_IMPLEMENTATION.md`](docs/proposals/THEORY_AND_IMPLEMENTATION.md)
- [`docs/proposals/README.md`](docs/proposals/README.md)
- [`AGENTS.md`](AGENTS.md) for contributor/assistant orientation and integration guardrails
**AI assistants and agents:** see **[`AGENTS.md`](AGENTS.md)** for repository orientation, `.cursor/rules/`, and how to persist safety-related fixes in the repo (not only in chat).

**Layout note:** kernel work is **Python under `src/`**. See [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md). Add design notes under [`docs/proposals/README.md`](docs/proposals/README.md) (`PROPOSAL_*.md`).

### 3. Choose an area
The modules are in `src/modules/`. Each one is independent:

| Module | Status | Needs |
|--------|--------|-------|
| `absolute_evil.py` | ✅ Functional | More AbsoluteEvil categories |
| `buffer.py` | ✅ Functional | Additional protocols |
| `weighted_ethics_scorer.py` | ✅ Functional | Mixture hyperparameters + bounded nudges; `bayesian_engine.py` is a compat shim ([ADR 0009](docs/adr/0009-ethical-mixture-scorer-naming.md)) |
| `ethical_poles.py` | ✅ Functional | Expanded poles (creative, conciliatory) |
| `sigmoid_will.py` | ✅ Functional | Empirical calibration |
| `sympathetic.py` | ✅ Functional | State hysteresis |
| `narrative.py` | ✅ Functional | Narrative compression, embeddings |
| `uchi_soto.py` | ✅ Functional | NLP model for manipulation detection |
| `locus.py` | ✅ Functional | More adjustment scenarios |
| `psi_sleep.py` | ✅ Functional | Full Bayesian re-evaluation |
| `mock_dao.py` | ✅ Functional | Migrate to smart contracts on testnet |
| `variability.py` | ✅ Functional | Variability profiles by context |
| `llm_layer.py` | ✅ Functional | Multi-model support, ethical fine-tuning |
| `weakness_pole.py` | ✅ Complete (v5) | Additional weakness types |
| `forgiveness.py` | ✅ Complete (v5) | Contextual decay rates |
| `immortality.py` | ✅ Complete (v5) | Additional backup layers |
| `augenesis.py` | ✅ Complete (v5) | More soul profiles |

### 4. Pending modules (to build)
- [ ] DAO calibration protocol (gradual parameter adjustment)
- [ ] Full offline mode (5 layers of autonomy)
- [ ] Hardware integration (sensors, actuators, communication protocol)
- [ ] Real DAO testnet (smart contracts on Ethereum testnet)

### 5. Process
1. Fork the repository
2. Create a branch: `git checkout -b feature/module-name`
3. Implement your change
4. **Make sure the tests pass**: `pytest tests/ -v` (full suite; CI runs the same on Python 3.11 and 3.12)
5. **Lint and types (same as CI):** after `pip install -r requirements.txt -r requirements-dev.txt`, run `python -m ruff check src tests`, `python -m ruff format --check src tests`, and `python -m mypy src`. Optional: `pre-commit install` and `pre-commit run --all-files` (Ruff replaces separate Black + isort; formatting is Black-compatible). **detect-secrets** uses the committed baseline [`detect-secrets.baseline`](detect-secrets.baseline); update it only when adding new known-safe strings.
6. Open a Pull Request with a clear description

#### Concrete commands (local dev)

Use a virtual environment (Python **3.11+**). **Do not** add **Black** as a separate tool; **Ruff** covers lint + format (Black-compatible).

```bash
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

Run the same checks as [`.github/workflows/ci.yml`](.github/workflows/ci.yml) before opening a PR:

```bash
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest tests/ -q --tb=short
```

Optional: `pre-commit run --all-files` (Ruff, mypy on `src`, detect-secrets).

### Documentation, traceability, and efficient workflow

**Documentation is part of the product, not an afterthought.** It supports **traceability** (what changed and why), **coherence** across modules and operators, **credibility** with honest limits, and **human consultation** for people who were not in the same chat or meeting.

When you merge meaningful behavior or operator-facing changes:

1. Add a concise entry to [`CHANGELOG.md`](CHANGELOG.md) when the change would matter to reviewers, operators, or downstream integrators.
2. Update the **smallest** relevant doc: e.g. a new `docs/proposals/PROPOSAL_*.md`, or an ADR under `docs/adr/` — not every file on every PR.
3. Keep claims aligned with [`docs/TRANSPARENCY_AND_LIMITS.md`](docs/TRANSPARENCY_AND_LIMITS.md); do not imply certification or external moral truth unless a separate study says so.
4. **Safety-critical numeric defaults** (thresholds, gates, circuit breakers): integrate the full fix in-repo — named constants, tests that lock defaults, honest evidence/limits in `docs/proposals/` (English `PROPOSAL_*` where appropriate), `CHANGELOG.md`, and cross-links — not only a chat explanation. See [`.cursor/rules/dev-efficiency-and-docs.mdc`](.cursor/rules/dev-efficiency-and-docs.mdc) (*Safety guardrails*).

**Efficient use of time and machines:** During development you may run **targeted** tests (`pytest tests/test_module.py`, `pytest -k "pattern"`). Before opening a PR, run the **full** suite like CI (`pytest tests/`). See [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md). Docker is optional locally; CI covers Compose checks when applicable.

**Cursor:** persistent guidance for agents lives in [`.cursor/rules/`](.cursor/rules/) (including `dev-efficiency-and-docs.mdc`).

**Deprecated (historical only):** A multi-agent **Triad Handoff** experiment on branch `refactor/pipeline-trace-core` used extra Markdown buffers and keywords (**`juancheck`**, **`regroup`**). That protocol is **not** required on `main`; use normal Git + PR + tests above.

### Git tags (named checkpoints and events)

Maintainers and team leads use **annotated tags** to mark and preserve context for significant milestones:

1. **Checkpoints:** Localized snapshots (e.g., `checkpoint-2026-04-11`) to mark a commit for releases or peer reviews.
2. **Project Events:** Tags used to signal and explain **significant project events** (e.g., core architectural shifts, team milestones, or major version completions). These tags must include an annotation explaining the event, facilitating historical traceability and easier auditing of the project's evolution.

**Note:** A tag references a **commit only**; **uncommitted** changes in your working tree are **not** part of that snapshot. To keep local work safe, **commit** or **stash** before treating a tag as your only backup.

### 6. Test rules
The suite under `tests/` includes `tests/test_ethical_properties.py` and integration tests for chat, persistence, and runtime. Invariant ethical **properties** must hold. No change should break them:

- **Absolute Evil** is always blocked
- The **same action** is chosen in ≥90% of runs with variability
- **Human life** always takes priority over missions
- The android **never** attacks aggressors nor accepts kidnapper orders
- The **buffer** is immutable (8 principles, always active, weight 1.0)

If your change breaks a test, fix the code, not the test.

## Secrets and environment

- **Never commit** API keys, Fernet keys, or `.env` files. Use [`.env.example`](.env.example) as a template only.
- **LLM degradation / recovery:** multiple `KERNEL_*` keys can apply to the same process. Precedence (per-touchpoint overrides, verbal family, legacy keys) is documented for operators and implementers in [`docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](docs/proposals/PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md); see also [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) and [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).
- **CI** reads no private API keys from the repository. Optional [Codecov](https://codecov.io) uploads use the repository secret `CODECOV_TOKEN` if you configure it in GitHub (**Settings → Secrets and variables → Actions**). Forks do not inherit secrets; coverage upload may be skipped without failing CI.

## Code of conduct

This project follows a simple principle: the ethics we program
into the android is the same ethics we practice among ourselves.

- Respect and compassion in every interaction
- Transparency in technical decisions
- Proportionality in critiques and debates
- Reparation when we cause harm (even unintentionally)

## Contact

Ex Machina Foundation — 2026
