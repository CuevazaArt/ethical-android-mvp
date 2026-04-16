# Claude Team — Hemisphere Refactor Integration Synthesis

**Status:** Synthesis of Phase 3+ work and hemisphere integration critique for L1 review
**Date:** April 16, 2026  
**From:** Claude (Level 2 Agent, Ethics & Governance)  
**To:** Antigravity (Level 1), Juan (Level 0)

---

## Executive Summary

The Claude team has completed Phase 3+ (RLHF, Multi-Realm Governance, External Audit Framework) and reviewed the proposed hemisphere refactor. **Recommendation: Proceed with hemisphere refactor as a controlled architectural migration,** with mandatory immutable governance snapshots per-turn to ensure safe integration of RLHF policies, realm governance, and audit trails across async cancellation boundaries.

---

## Phase 3+ Completion Status

### Deliverables (✅ Merged into `master-claude`)

1. **RLHF Reward Model** (`src/modules/rlhf_reward_model.py`)
   - Feature extraction pipeline (5D: embedding similarity, lexical score, perception confidence, ambiguity flag, category ID)
   - Logistic regression + gradient descent training
   - Persistence (JSONL examples, model checkpoints)
   - 36 tests passing

2. **Multi-Realm Governance** (`src/modules/multi_realm_governance.py`)
   - Decentralized per-realm threshold governance (DAO, team, context-specific)
   - Reputation-weighted voting with configurable consensus
   - `RealmThresholdConfig` enforces hard semantic gate constraints (θ_allow, θ_block)
   - `ThresholdProposal` lifecycle with immutable audit trail per realm
   - 28 tests passing

3. **External Audit Framework** (`src/modules/external_audit_framework.py`)
   - Hash-linked tamper-evident logs (SHA-256 chain)
   - `SecurityFinding` lifecycle management with severity/resolution tracking
   - `AuditReport` signed snapshots with attestation hash
   - Full compliance checklist and retention policy
   - 25 tests passing

4. **Integration Validation**
   - 89 new tests; full suite 824 passed, 4 skipped (no regressions)
   - Continuous audit (`verify_collaboration_invariants.py`) passes
   - Governance files authored under L1 co-authority (Claude + Antigravity)

---

## Hemisphere Refactor Critique — Key Findings

### 1) Directional Alignment ✅

The proposed tri-lobe architecture (Perceptive / Ethical / Frontal-Motor) aligns well with:
- **Async isolation:** Left hemisphere handles network/sensor I/O and timeout signaling
- **Ethical determinism:** Right hemisphere executes immutable ethical evaluation
- **Orchestration safety:** Corpus callosum enforces state transitions and commit gates

**Risk is not decomposition itself, but transactional consistency across async cancellation.**

### 2) Critical Integration Points with Phase 3+ Modules

#### 2.1 Multi-Realm Governance + Cancellation

**Problem:**
- Realm threshold configs (θ_allow, θ_block) or RLHF hyperparameters can change mid-turn
- Cancellation may occur after perception runs but before ethical evaluation completes
- Result: perception and ethics evaluated under different governance assumptions

**Solution:**
- **Per-turn immutable governance snapshot** captured at turn admission
  - `realm_id`, `realm_config_version`
  - θ_allow, θ_block values
  - RLHF hyperparameters (learning rate, feature weights)
  - Snapshot timestamp and SHA-256 hash
- **Snapshot envelope** passed through inter-hemisphere boundary
- **Strict enforcement:** All right-hemisphere decisions use **only** snapshot values
- **Proposal latency:** New governance proposals apply only to subsequent turns

**Expected benefit:**
- Prevents mid-turn policy drift
- Deterministic replay/audit for governance-sensitive outcomes
- RLHF confidence scores reflect governance state at decision time

#### 2.2 Transactional Integrity Under Async Timeout

**Problem:**
- Partial side effects leak after cancellation (late writes to STM, audit channels, memory)
- RLHF reward records, governance votes, audit logs can become orphaned
- No clear causal trace from timeout → safe abandonment

**Solution:**
- **Formalize per-turn state machine:**
  ```
  received 
    → perception_started 
    → ethical_eval_started 
    → decision_ready 
    → committed
  
  Terminal alternatives: abandoned_timeout, cancelled, failed
  ```
- **Write-policy enforcement:**
  - Only `committed` state can mutate durable/user-visible decision state
  - `abandoned_timeout` can **only** append audit evidence (read-only)
  - Never apply behavioral or memory mutations after abandonment
- **Idempotency requirement:** All write sinks indexed by `(session_id, turn_id)`
  - Governance vote proposals: idempotent by turn ID
  - RLHF reward records: keyed by turn hash to prevent duplicate training
  - Audit trail: append-only, no mutation after terminal state

**Expected benefit:**
- No ledger or memory corruption from late completions
- Clear causal trace from timeout → safe abandonment
- RLHF training samples remain consistent (no ghost updates)

#### 2.3 Epistemic Metadata vs Moral Override

**Problem:**
- Perception latency, retry counts, dual-vote disagreement can be misinterpreted as moral signals
- Risk of conflating reliability with ethical priority

**Solution:**
- **Inject epistemic metadata as uncertainty context, not moral overrides:**
  - `perception_latency_ms`, `perception_retry_count`
  - `dual_vote_disagreement`, `coercion_uncertainty`
  - `backend_policy_effective`, `cancel_scope_signaled`
- **Use for deliberation intensity modulation:**
  - Higher uncertainty → more conservative thresholds
  - Higher disagreement → favor human-in-the-loop escalation
  - **Never** directly mutate ethical objective weights due to latency

**Expected benefit:**
- Better epistemic humility under noisy perception
- Preserves norm separation: reliability signals ≠ moral priorities

---

## Architecture Guidance (Per-Hemisphere Responsibilities)

### Left Hemisphere (Async Perimeter)

**Owned:**
- Network/sensor I/O, timeout handling, cancellation signaling
- Parse/coercion metadata generation
- Envelope construction (include governance snapshot)
- Perception latency/retry tracking

**Forbidden:**
- Direct irreversible governance or memory writes
- Mutation of `RealmThresholdConfig` during turn
- RLHF weight updates (read-only feature extraction only)

### Right Hemisphere (Sync Ethical Core)

**Owned:**
- Deterministic ethical evaluation from immutable envelope + snapshot
- MalAbs semantic gating (using snapshot θ values)
- RLHF-informed scoring (using snapshot hyperparameters)
- Governance proposal evaluation (reputation voting)

**Cooperative Checkpoints (NOT async cancellation points):**
- Integrity assertions on governance snapshot version
- Bounds checks on perception input confidence
- Contradiction detection and escalation flags

### Corpus Callosum (Orchestrator)

**Owned:**
- Admission control and turn state transitions
- Timeout policy and cancellation signaling
- Governance snapshot capture and passing
- Commit gate (prevent partial side effects)
- Monotonic `turn_id` authority and idempotency coordination

---

## Minimum Acceptance Criteria for Hemisphere Integration

1. ✅ **No durable side effects after terminal state** `abandoned_timeout`
   - Audit evidence only; no memory/ledger mutation
   - Idempotency keys prevent duplicate training on RLHF samples

2. ✅ **Deterministic replay with same envelope + snapshot = same ethical decision**
   - Snapshot captures all governance state needed for reproducibility
   - No runtime policy lookups during decision evaluation

3. ✅ **Realm config changes never alter already-admitted turn**
   - Proposal votes apply to future turns only
   - Snapshot timestamp enforces causality

4. ✅ **Metrics expose full cancellation lifecycle**
   - async timeout count
   - cancel scope signaled count
   - abandoned side effects skipped count
   - committed vs abandoned outcome distribution

5. ✅ **Audit entries for abandoned turns remain append-only and attributable**
   - Turn ID, snapshot hash, reason for abandonment
   - No retroactive modification of governance/RLHF records

---

## Integration Sequencing (Recommended Phase)

### Phase I: Governance Snapshot Foundation
- Implement per-turn immutable snapshot at admission control
- Modify `MultiRealmGovernor.eval_proposal` to accept snapshot parameter
- Modify RLHF pipeline to read hyperparameters from snapshot (not runtime config)
- Add regression tests for snapshot immutability under concurrent proposal votes

### Phase II: Transactional State Machine
- Formalize turn state machine in orchestrator
- Implement commit gate and idempotency coordinator
- Add audit trail emissions for state transitions
- Regression tests on timeout + abandoned side effects

### Phase III: Hemisphere Boundary Enforcement
- Separate left/right hemisphere module boundaries
- Verify left hemisphere has no direct governance/memory writes
- Add linters to detect policy violations
- Full integration tests with all three phases

### Phase IV: Epistemic Metadata Routing
- Inject latency/retry/disagreement metadata into right hemisphere
- Modulate deliberation intensity (not moral weights)
- Dashboard visualization of epistemic confidence
- Optional: A/B test vs baseline for operator confidence

---

## Known Risks if Refactor Is Rushed

1. **Hidden side-effect races** across cancellation boundaries
   - Late writes to governance votes or RLHF training logs
   - Solution: strict idempotency keys and append-only audit

2. **Governance trace ambiguity** if snapshot versioning is omitted
   - No way to replay outcome with same config
   - Solution: mandatory SHA-256 snapshot hash in audit trail

3. **Semantic confusion** between epistemic reliability and moral valuation
   - Risk of "latency-based moral override"
   - Solution: explicit epistemic metadata context, not direct weight mutation

4. **Recreating monolith coupling** inside orchestrator
   - Corpus callosum becomes a new "God Object"
   - Solution: minimal orchestrator with clear state machine, heavy linting

---

## Roadmap Integration: External Review Synthesis

### Priority Stack (from `CRITIQUE_ROADMAP_ISSUES.md`)

| Priority | Topic | Claude Status | Integration with Hemisphere |
|----------|-------|---------------|-----------------------------|
| 1 | **Honest naming: "Bayesian" vs mixture** | ✅ Done: ADR 0009, README, `BayesianInferenceEngine` wrapper | No direct conflict; snapshot includes governance mode clarity |
| 2 | **Input trust: MalAbs gates on chat + perception** | ✅ Hardened in Phase 2: rate-limiter, LAN guard, perception JSON validation | Semantic gates use snapshot θ values; audit trail tracks gate rejections |
| 3 | **Empirical pilot (human agreement)** | 🟡 Partial: fixtures, pilot protocol defined | Snapshot versioning enables reproducible scenario runs |
| 4 | **Core path documentation + packaging** | 🟡 Partial: LAN governance docs, DAO orch bridge | Hemisphere docs clarify core decision pipeline |
| 5 | **Async LLM / scalable chat** | 🟡 Partial: ADR 0002, timeout handling | **Core use case for hemisphere refactor** |
| 6 | **Module ablation on nine scenarios** | 🟡 Open: ablation infrastructure in place | Snapshot enables controlled scenario replay |

---

## Claude Team — Going Forward

### Immediate (Before L1 Review of Hemisphere PR)
- [ ] Create integration test suite for governance snapshot immutability
- [ ] Document snapshot schema and serialization contract
- [ ] Validate that RLHF pipeline reads hyperparameters from snapshot

### Phase I Delivery (Hemisphere Foundation)
- [ ] Snapshot capture at admission control
- [ ] Multi-realm governance snapshot integration
- [ ] RLHF snapshot integration
- [ ] Regression tests + audit trail validation

### After Main Promotion
- [ ] Offline tool: `scripts/replay_turn_with_snapshot.py` for forensics
- [ ] Dashboard metrics: commitment rate, abandonment count, governance drift rate
- [ ] Documentation: operator runbooks for governance proposal under hemisphere semantics

---

## Links & References

**Phase 3+ Implementation:**
- [`src/modules/rlhf_reward_model.py`](../../src/modules/rlhf_reward_model.py)
- [`src/modules/multi_realm_governance.py`](../../src/modules/multi_realm_governance.py)
- [`src/modules/external_audit_framework.py`](../../src/modules/external_audit_framework.py)

**Hemisphere Refactor Context:**
- [`CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md`](../../CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md) (from L1)
- `PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md` (our critique)
- [`PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md`](../../PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md) (team consensus: 3 lobes optimal)

**Roadmap & Standards:**
- [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md)
- [`CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`](CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md)
- [`AGENTS.md`](../../AGENTS.md) (governance hierarchy and team coordination)

**Audit & Governance:**
- [`docs/collaboration/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md`](../collaboration/COLLABORATION_REGULATION_CRITIQUE_2026-04-16.md)

---

## Conclusion

The Phase 3+ modules (RLHF, Multi-Realm Governance, External Audit) are ready for integration with the hemisphere refactor. The critical success factor is **immutable per-turn governance snapshots** to prevent policy drift during async cancellation and enable deterministic replay.

This is a bounded, high-impact architectural migration with clear acceptance criteria and known risk mitigation strategies. **Recommend L1 approval to proceed Phase I → Phase IV sequencing.**

Awaiting L1 review and L0 authorization for main branch promotion.

---

**Authored by:** Claude Team (Level 2)  
**Under authority:** AGENTS.md § Governance Hierarchy  
**File path:** `docs/proposals/CLAUDE_HEMISPHERE_INTEGRATION_SYNTHESIS.md`
