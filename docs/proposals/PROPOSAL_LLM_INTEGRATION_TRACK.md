# LLM integration track — ownership, scope, and gap register

**Status:** Active team scope (Cursor line).  
**Owner:** Cursor shared development line (`cursor-team` → `master-Cursor`), per [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md).  
**Language:** This file is the **English** durable record; day-to-day coordination may use Spanish.

**Purpose:** Assign and maintain focus on **LLM incorporation** (inference wiring), **adjacent layers** (MalAbs semantic, embeddings, perception/verbal policies), and **integration** (kernel ↔ chat ↔ observability). Complements [`MODEL_CRITICAL_BACKLOG.md`](MODEL_CRITICAL_BACKLOG.md) with **LLM-specific** closure items.

---

## 1) Scope (what this track owns)

| Layer | Role | Primary code / docs |
|-------|------|----------------------|
| **Completion JSON** | Perceive / communicate / narrate / optional monologue | [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py), [`src/modules/llm_backends.py`](../../src/modules/llm_backends.py) |
| **Policy + precedence** | Touchpoint degradation, verbal family, perception override | [`src/modules/llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py), [`llm_verbal_backend_policy.py`](../../src/modules/llm_verbal_backend_policy.py), [`perception_backend_policy.py`](../../src/modules/perception_backend_policy.py) |
| **Structured perception** | Parse, coerce, coherence, dual vote | [`perception_schema.py`](../../src/modules/perception_schema.py), [`perception_dual_vote.py`](../../src/modules/perception_dual_vote.py), [`perception_cross_check.py`](../../src/modules/perception_cross_check.py) |
| **Generative action sketches** | `generative_candidates` from perception JSON | [`generative_candidates.py`](../../src/modules/generative_candidates.py) |
| **Semantic MalAbs** | Embeddings + optional arbiter LLM after lexical | [`semantic_chat_gate.py`](../../src/modules/semantic_chat_gate.py), [`semantic_embedding_client.py`](../../src/modules/semantic_embedding_client.py), [`absolute_evil.py`](../../src/modules/absolute_evil.py) |
| **Chat integration** | WebSocket payloads, timeouts, offload | [`chat_server.py`](../../src/chat_server.py), [`real_time_bridge.py`](../../src/real_time_bridge.py) |
| **Observability** | Histograms, coercion reports, verbal events | [`observability/metrics.py`](../../src/observability/metrics.py), [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) |

**Out of scope for this track (cross-reference only):** full Bayesian inference redesign ([`CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`](CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md)), on-chain DAO, hardware drivers.

---

## 2) Gap register (close or explicitly defer)

Items are **ordered by integration leverage** (unblocks operators and tests first). IDs are stable for issues/PRs.

| ID | Gap | Evidence / risk | Suggested closure |
|----|-----|-----------------|-------------------|
| **G-01** | **Unified degradation story for embedding transport** vs main chat completion path | [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 — embedding path has retries/circuit; perception/verbal have `KERNEL_LLM_TP_*` matrix | Document operator mapping in [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) § Related; optional: single `KERNEL_LLM_EMBEDDING_POLICY` alias + tests (no behavior change until agreed) |
| **G-02** | **Semantic MalAbs** (embed + optional LLM arbiter) failure semantics not aligned with verbal `verbal_llm_observability` | Same §3; operators see MalAbs trace but not the same JSON shape as verbal events | Add small **audit subsection** in [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md): what is logged/metrics on embed vs arbiter failure; optional chat field behind flag |
| **G-03** | **`process_natural`** returns `(decision, response, narrative)` without `verbal_llm_degradation_events` | [`kernel.py`](../../src/kernel.py) resets degradation log and runs `communicate`/`narrate`, but tuple API does not expose events | Extend return type or add `kernel._last_verbal_llm_degradation_events` documented accessor for harnesses; or document “chat-only observability” as limitation |
| **G-04** | **Single env surface** across all LLM touchpoints | Still aspirational per [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 | Keep matrix as source of truth; defer mega-unification until G-01–G-02 resolved |
| **G-05** | **Cooperative LLM cancel** under async chat | [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §1; [`ADR 0002`](../adr/0002-async-orchestration-future.md) | Research spike: bound in-flight httpx; document interaction with `KERNEL_CHAT_TURN_TIMEOUT` / `OLLAMA_TIMEOUT` |
| **G-06** | **Generative candidates** trust: LLM-suggested actions share MalAbs path but perception JSON can still be GIGO | [`generative_candidates.py`](../../src/modules/generative_candidates.py), [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) | Fuzz + regression tests for malformed `generative_candidates`; document caps in [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md) |
| **G-07** | **Dual perception vote** second backend: separate `OllamaCompletion` — policy when primary host is degraded | [`perception_dual_vote.py`](../../src/modules/perception_dual_vote.py) | Align failure_reason metadata with `apply_backend_degradation_meta` when second sample fails; test subprocess |
| **G-08** | **Input trust end-to-end** (Issue #2): lexical + semantic + perception cross-check + uncertainty | [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md), [`MODEL_CRITICAL_BACKLOG.md`](MODEL_CRITICAL_BACKLOG.md) | Scenario tests spanning MalAbs + perception coercion_report; link from [`SECURITY.md`](../../SECURITY.md) |
| **G-09** | **Profile bundles** for LLM-heavy demos | [`runtime_profiles.py`](../../src/runtime_profiles.py) | Ensure named profiles document LLM + semantic + perception flags together; CI smoke already covers some paths |
| **G-10** | **Cross-team integration gate** for LLM-affecting merges | [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) | Run `scripts/eval/run_cursor_integration_gate.py` when touching `llm_layer`, `semantic_chat_gate`, or chat JSON contracts |

---

## 3) Definition of done (per gap item)

- **Code:** Named constants or explicit policy branch; no silent behavior change without `CHANGELOG.md` when operator-visible.  
- **Tests:** At least one targeted test or subprocess check for new env behavior.  
- **Docs:** Update matrix or this register; link from [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) if JSON or env changes.

---

## 4) Related documents

- [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)  
- [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §9 (model backlog pointer)  
- [`LLM_STACK_OLLAMA_VS_HF.md`](LLM_STACK_OLLAMA_VS_HF.md)  
- [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md) (ethics vs LLM boundary)

---

## 5) Changelog

- **2026-04-14:** Initial gap register and track ownership for Cursor LLM integration scope.
