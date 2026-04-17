# Model-critical backlog (execution order)

**Purpose:** A short, **prioritized** stack for work that affects **trust, safety, and shipping honesty** across the kernel—not only the sensors/perception track. It complements [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §9 and the wider tables in [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md).

**LLM-specific gap register (incorporation, adjacent layers, integration):** [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) — assigned to the Cursor shared line; use for sequencing MalAbs ↔ embeddings ↔ perception/verbal work. **Phased vertical expansion (operator + observability + tests):** [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md).

**Not a commitment order for every contributor:** use this to **sequence** when perception P0 baselines are landed and you need the next highest-leverage model/runtime gaps.

---

## Priority stack (highest leverage first)

| Order | Theme | Why it is model-critical | Primary pointers |
|------|--------|---------------------------|------------------|
| 1 | **LLM input trust (defense-in-depth)** | GIGO on chat and structured perception can poison decisions and narratives; MalAbs and perception hardening are partially independent surfaces. | [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) Issue **#2**; [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md); [SECURITY.md](../../SECURITY.md) |
| 2 | **Unified LLM degradation posture** | **Partial:** perception (`KERNEL_PERCEPTION_BACKEND_POLICY`) and verbal/narrative (`KERNEL_VERBAL_LLM_BACKEND_POLICY`, `verbal_llm_observability`) are baseline; monologue, embedding transport, and a single env surface remain future work. | [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §3; [PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md](PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md); [PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md](PROPOSAL_LLM_VERBAL_DEGRADATION_POLICY.md) |
| 3 | **Core decision chain + packaging boundary** | Operators need a clear “what ships as the kernel” story; avoids implied guarantees outside the tested entry path. | [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) Issue **#4**; [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) |
| 4 | **Governance mock honesty (MockDAO vs L0)** | **Done:** Misread DAO demos as production authority or as the source of `final_action`. | [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) Issue **#6**; [MOCK_DAO_SIMULATION_LIMITS.md](MOCK_DAO_SIMULATION_LIMITS.md); integration guard **IT-06** ([`tests/integration/test_cross_tier_decisions.py`](../../tests/integration/test_cross_tier_decisions.py)); doc drift tests [`test_governance_mock_honesty_docs.py`](../../tests/test_governance_mock_honesty_docs.py). |

## Next tier (high value, not v1.0 blockers for every scope)

- **Semantic gate evidence:** [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md); tests under `tests/test_semantic_chat_gate.py`.
- **Async LLM / cooperative cancel:** [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §1; [ADR 0002](../adr/0002-async-orchestration-future.md).
- **Peripheral module ablation:** [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](MODULE_IMPACT_AND_EMPIRICAL_GAP.md); [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §7.

## Near-term execution detail

For **two-week** checklists and milestone naming, use [`PLAN_IMMEDIATE_TWO_WEEKS.md`](PLAN_IMMEDIATE_TWO_WEEKS.md).
