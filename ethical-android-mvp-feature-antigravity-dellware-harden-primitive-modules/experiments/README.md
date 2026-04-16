# `experiments/`

Optional research scripts and study harnesses that are **not** required to run the kernel or CI.

- **Optional deps:** [`requirements-experiment.txt`](requirements-experiment.txt) (after root `requirements.txt`).
- **Generated artifacts:** [`out/`](out/) is gitignored except [`.gitignore`](out/.gitignore); large JSON/CSV/PNG from batch runs go there.

Batch / simplex tools: [`scripts/run_mass_kernel_study.py`](../scripts/run_mass_kernel_study.py), [`scripts/run_simplex_decision_map.py`](../scripts/run_simplex_decision_map.py), and related scripts under [`scripts/`](../scripts/). See root [`README.md`](../README.md) for the main kernel. Prior `experiments/million_sim/` material may be recovered from git history or backup branches.
