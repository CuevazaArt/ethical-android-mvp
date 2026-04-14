# Cursor team mission — sensors and perception

**Status:** charter for the **Cursor** integration line (`master-Cursor` / `cursor-team`). This document scopes **analysis, design discussion, planning, implementation, and tests** for how the kernel ingests and trusts **sensor-derived and LLM-mediated perception**.

## Scope

1. **Structured perception** — JSON from `LLMModule.perceive`, validation (`perception_schema`), cross-checks (`perception_cross_check`), dual-sample paths (`perception_dual_vote`), and uncertainty-driven deliberation (`KERNEL_PERCEPTION_UNCERTAINTY_DELIB`).
2. **Input trust** — normalization, MalAbs lexical + optional semantic gates, and the threat model for **valid-but-wrong** structured outputs.
3. **Situated / hardware-facing design** — alignment with the situated-organism proposal (sensor fusion, vitality, agency) without claiming hardware is implemented until code and tests land.

## Out of scope (for other tracks)

- On-chain DAO / testnet governance (see `mock_dao.py`, `MOCK_DAO_SIMULATION_LIMITS.md`).
- Promotion to `main` without maintainer release process (see `docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`).

## Primary references

| Topic | Document / code |
|--------|-----------------|
| Perception pipeline | [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md), [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py) |
| Input trust + MalAbs | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md), [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) |
| Known limits | [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 (local inference / degradation policy gap) |
| Situated model (theory) | [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md) |
| Module backlog (Spanish collaboration, English repo) | [`CONTRIBUTING.md`](../../CONTRIBUTING.md) — pending modules and `src/modules/` table |

## Deliverable pattern

Follow [`AGENTS.md`](../../AGENTS.md) and [`.cursor/rules/dev-efficiency-and-docs.mdc`](../../.cursor/rules/dev-efficiency-and-docs.mdc): **named defaults**, **tests** for behavior and env overrides, **honest** proposal notes when changing thresholds or safety posture, and **`CHANGELOG.md`** when operator expectations change.
