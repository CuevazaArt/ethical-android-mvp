# PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE

## Context

This critique responds to `CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md` from branch
`origin/antigravity/hemisphere-refactor-proposal`.

The proposed split is:

1. Left hemisphere (perceptive): async I/O, cancellation, timeouts.
2. Right hemisphere (ethical/limbic): sync CPU-bound moral engine.
3. Corpus callosum: lightweight orchestrator.

Current repository state already contains partial prerequisites for this model:

- Cooperative chat cancellation and turn abandonment.
- Optional async LLM HTTP path.
- Metrics for timeouts/cancel-scope/abandoned side effects.
- Multi-realm governance with auditable configuration changes.

## Executive Position

The hemisphere refactor is directionally correct and should proceed.
The main risk is not decomposition itself, but transactional consistency across
cancellation boundaries and governance version drift during an in-flight turn.

## Deep Critique

### 1) Multi-realm governance and RLHF under hybrid cancellation

Potential break point:

- `RealmThresholdConfig` or RLHF-related realm parameters could change while a
  turn is in progress, causing perception and ethical evaluation to run under
  different governance assumptions.

Recommendation:

- Introduce a per-turn immutable `governance_snapshot` at turn admission:
  - `realm_id`
  - `realm_config_version`
  - `theta_allow`, `theta_block`
  - RLHF hyperparameters relevant to runtime gating
  - snapshot timestamp and hash
- Pass this snapshot inside the inter-hemisphere envelope and enforce that all
  right-hemisphere decisions for that turn use only snapshot values.
- Apply newly approved realm proposals only to subsequent turns.

Expected benefit:

- Prevents mid-turn policy drift.
- Makes replay/audit deterministic for governance-sensitive outcomes.

### 2) Transactional integrity when async timeout cancels cognitive flow

Potential break point:

- Partial side effects can leak after timeout (late writes to STM, governance
  records, or audit channels) if cancellation is observed too late.

Recommendation:

- Formalize turn state machine and write-policy:
  - `received`
  - `perception_started`
  - `ethical_eval_started`
  - `decision_ready`
  - `committed`
  - terminal alternatives: `abandoned_timeout`, `cancelled`, `failed`
- Enforce side-effect commit gate:
  - Only `committed` can mutate durable or user-visible decision state.
  - `abandoned_timeout` can append audit evidence, but must never apply
    behavioral or memory mutations.
- Require idempotency by `(session_id, turn_id)` for all write sinks.

Expected benefit:

- No ledger or memory corruption from late completions.
- Clear causal trace from timeout to safe abandonment.

### 3) Bayesian/ethical modeling metadata after network-noise extraction

Recommendation:

- Inject epistemic metadata into right hemisphere as uncertainty context,
  not as direct moral score overrides:
  - `perception_latency_ms`
  - `perception_retry_count`
  - `dual_vote_disagreement`
  - `coercion_uncertainty`
  - `backend_policy_effective`
  - `cancel_scope_signaled`
- Use these to modulate deliberation intensity and confidence calibration.
- Do not directly change ethical objective weights solely due to latency.

Expected benefit:

- Better epistemic humility and safer deliberation under noisy perception.
- Preserves norm separation between reliability signals and moral priorities.

## Architecture Guidance

### Left hemisphere (async perimeter)

- Responsibilities: network/sensor I/O, timeout handling, cancellation signaling,
  parse/coercion metadata generation, envelope construction.
- No direct irreversible governance or memory writes.

### Right hemisphere (sync ethical core)

- Responsibilities: deterministic ethical evaluation and policy resolution from
  immutable envelope + snapshot.
- Cooperative checkpoints remain mandatory, but deterministic replay is primary.

### Corpus callosum (orchestrator)

- Admission control, timeout policy, state transitions, and commit gate.
- Monotonic `turn_id` authority and idempotency coordinator.

## Acceptance Criteria (minimum)

1. No durable side effects after terminal state `abandoned_timeout`.
2. Replay with same envelope + snapshot yields same ethical decision.
3. Realm config changes never alter an already admitted turn.
4. Metrics expose the full cancellation lifecycle:
   - async timeout total
   - cancel scope signaled total
   - abandoned side effects skipped total
   - committed vs abandoned turn outcomes
5. Audit entries for abandoned turns remain append-only and attributable.

## Main Risks if Refactor Is Rushed

- Hidden side-effect races across cancellation boundaries.
- Governance trace ambiguity if snapshot versioning is omitted.
- Semantic confusion between epistemic reliability and moral valuation.
- Recreating monolith coupling inside orchestrator if boundaries are not strict.

## Conclusion

Proceed with hemisphere refactor as a controlled architectural migration.
Prioritize immutable turn snapshots, explicit state machine transitions, and
strict commit gating before broad feature expansion. This sequence preserves
governance integrity, auditability, and safety under async cancellation pressure.

