# `docs/proposals/` — design and operations

This directory holds **versioned design notes** for the Ethos Kernel: proposals, runtime contracts, theory ↔ code maps, and operator guides.

**Canonical filenames:** use English `PROPOSAL_*.md` for standalone proposals (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md) language policy).

The previous long-form proposal set was removed from this branch to keep the tree minimal; recover it from **git history** or backup branches (e.g. `backup/main-2026-04-10`) if needed.

## Indexed proposals (this branch)

| Document | Summary |
|----------|---------|
| [`PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md`](PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md) | ADR 0012 stack: BMA (L1), feedback posteriors (L2), context buckets (L3), softmax / importance-sampling likelihood, env vars, tests, link to ADR 0012. |

## Architecture decisions (ADR)

Normative technical decisions live under [`docs/adr/`](../adr/README.md), not under `PROPOSAL_*`. For Bayesian mixture work, start with **[ADR 0012](../adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)**.

## Adding new material

1. Add a new English `PROPOSAL_<TOPIC>.md` for self-contained design or operations notes.
2. Link it from this README in the table above.
3. If the change is a **decision** (alternatives, consequences), prefer a new or updated ADR under `docs/adr/`.
