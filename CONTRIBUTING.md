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

### 2. Understand the model
Read the README.md and run the simulations before proposing changes.
The complete model document is in `/docs/Androide_Etico_Analisis_Integral_v3.docx`.

### 3. Choose an area
The modules are in `src/modules/`. Each one is independent:

| Module | Status | Needs |
|--------|--------|-------|
| `absolute_evil.py` | ✅ Functional | More AbsoluteEvil categories |
| `buffer.py` | ✅ Functional | Additional protocols |
| `bayesian_engine.py` | ✅ Functional | Optional scoped Bayesian update or calibrated mixture (honest naming first — see CHANGELOG) |
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

**Deprecated (historical only):** A multi-agent **Triad Handoff** experiment on branch `refactor/pipeline-trace-core` used extra Markdown buffers and keywords (**`juancheck`**, **`regroup`**). That protocol is **not** required on `main`; use normal Git + PR + tests above.

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
