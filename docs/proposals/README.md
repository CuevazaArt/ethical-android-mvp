# `docs/proposals/` — design and operations

This directory holds **versioned design notes** for the Ethos Kernel: proposals, runtime contracts, theory ↔ code maps, and operator guides.

**Canonical filenames:** use English `PROPOSAL_*.md` for standalone proposals (see [`CONTRIBUTING.md`](../../CONTRIBUTING.md) language policy).

The previous long-form proposal set was removed from this branch to keep the tree minimal; recover it from **git history** or backup branches (e.g. `backup/main-2026-04-10`) if needed.

## Indexed proposals (this branch)

| Document | Summary |
|----------|---------|
| [`PROPOSAL_001_HARDENIDO_DE_MODULOS_PRIMITIVOS.md`](PROPOSAL_001_HARDENIDO_DE_MODULOS_PRIMITIVOS.md) | Antigravity: Plan para el endurecimiento de módulos primitivos. |
| [`PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md`](PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md) | Antigravity: Pilar de la Mente (Arquitectura Cognitiva y Narrativa). Tiers 1-3. |
| [`PROPOSAL_003_NARRATIVE_HARDENING_ANALYSIS.md`](PROPOSAL_003_NARRATIVE_HARDENING_ANALYSIS.md) | Antigravity: Hardening analysis (Encryption, Integrity, Uchi-Soto). |
| [`PROPOSAL_004_NARRATIVE_IDENTITY_REFLECTION.md`](PROPOSAL_004_NARRATIVE_IDENTITY_REFLECTION.md) | Antigravity: Espejo Narrativo (Identity Reflection layer). |
| [`PROPOSAL_005_NARRATIVE_RESILIENCE_AND_HIERARCHY.md`](PROPOSAL_005_NARRATIVE_RESILIENCE_AND_HIERARCHY.md) | Antigravity: Resiliencia Narrativa y Jerarquía de Memoria. |
| [`PROPOSAL_008_METACOGNITIVE_CURIOSITY.md`](PROPOSAL_008_METACOGNITIVE_CURIOSITY.md) | Cursor: Curiosidad Metacognitiva y Alineación Epistémica. |
| [`PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md`](PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md) | Antigravity: Justicia Distribuida y Gobernanza Blockchain (Sovereign Ethics). |
| [`ANTIGRAVITY_COLLABORATION_GUIDE.md`](ANTIGRAVITY_COLLABORATION_GUIDE.md) | Antigravity: Collaboration guide and operational workflows. |
| [`PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md`](PROPOSAL_BAYESIAN_FEEDBACK.md) | ADR 0012 stack: BMA (L1), feedback posteriors (L2), context buckets (L3), softmax / importance-sampling likelihood, env vars, tests, link to ADR 0012. |

## Architecture decisions (ADR)

Normative technical decisions live under [`docs/adr/`](../adr/README.md), not under `PROPOSAL_*`. For Bayesian mixture work, start with **[ADR 0012](../adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)**.

## Adding new material

1. Add a new English `PROPOSAL_<TOPIC>.md` for self-contained design or operations notes.
2. Link it from this README in the table above.
3. If the change is a **decision** (alternatives, consequences), prefer a new or updated ADR under `docs/adr/`.
