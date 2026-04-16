# ADR 0013: Core Decision Chain Boundaries and Segmentation (Issue 4)

**Status:** Proposed  
**Owner:** Cursor / Antigravity

## Context

The Ethos Kernel integrates multiple modules with different roles: some are critical for the deterministic moral verdict (`final_action`), while others are "theater" (narrative, humanization, transparency). To ensure security and maintainability, we must formally segment these layers.

## Decision

We define two primary tiers for the codebase:

### 1. `ethos-core` (Policy and Logic)
These modules are **immutable** in their effect on the final action selection unless the `WeightedEthicsScorer` chooses otherwise.
- `src/kernel.py` (Orchestration)
- `src/modules/input_trust.py` (Validation)
- `src/modules/absolute_evil.py` (MalAbs Veto)
- `src/modules/buffer.py` (L0 Constitution)
- `src/modules/bayesian_engine.py` / `src/modules/weighted_ethics_scorer.py` (Inference/Choice)
- `src/modules/uchi_soto.py` (Social Context)
- `src/modules/llm_layer.py` (Perception subset - generating signals)

### 2. `ethos-vanguard` / `theater` (Narrative and UX)
These modules run **after** the decision or provide **advisory** signals that do not change the chosen action.
- `src/modules/poles.py` (Multipolar coloring)
- `src/modules/sigmoid_will.py` (Will/Mode selection)
- `src/modules/weakness_pole.py` (Humanizing slips/hesitation)
- `src/modules/narrative.py` / `src/modules/memory.py` (Identity)
- `src/modules/mock_dao.py` (Governance simulation)
- `src/modules/salience_map.py` (Attention visualization)

## Implementation Details

1.  **Dependency Rule:** Core modules must not depend on Theater modules. Theater modules may depend on Core summaries (`KernelDecision`).
2.  **Packaging:** `pyproject.toml` remains a single package for research simplicity, but the `theater` extra will be used to denote dependencies required only for narrative generation (e.g., if we split heavy NLP models).
3.  **Strict Mode:** `EthicalKernel` will support a "minimal" run mode that skips all Theater modules for high-frequency or safety-critical deployments.

## Consequences

- Improved auditability: Reviewers can ignore "theater" code when verifying the safety of the decision path.
- Clearer roadmap: Extensions like "Complex Memory" or "DAO Governance" are explicitly marked as secondary to the decision core.
