# LLM integration track — ownership, scope, and gap register

**Status:** Active team scope (Cursor line).  
**Owner:** Cursor integration line **`master-Cursor`** (active); the historical branch name `cursor-team` is deprecated — per [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md).  
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

| ID | Gap | Status | Notes / evidence |
|----|-----|--------|-------------------|
| **G-01** | Embedding transport vs chat completion operator mapping | **Closed (docs)** | [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) — section *Embedding transport vs chat completion*. |
| **G-02** | MalAbs semantic observability vs `verbal_llm_observability` | **Closed (docs)** | [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md) — subsection *Observability: MalAbs semantic vs chat verbal_llm_observability*. |
| **G-03** | `process_natural` verbal degradation not exposed | **Closed (code)** | [`EthicalKernel.last_natural_verbal_llm_degradation_events`](../../src/kernel.py) property; snapshot after communicate/narrate; `None` if MalAbs blocks before LLM. Tests: [`tests/test_process_natural_verbal_observability.py`](../../tests/test_process_natural_verbal_observability.py). |
| **G-04** | Single env surface for all LLM touchpoints | **Closed (docs + tests + code)** | **Prefix unification** (renaming every legacy `KERNEL_PERCEPTION_*` / `KERNEL_VERBAL_*` knob) remains deferred — see [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3. **Delivered:** canonical index in [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) (*LLM touchpoint index*); unified fallback `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` + `raw_global_default_policy()` in [`llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py) with resolver wiring in [`perception_backend_policy.py`](../../src/modules/perception_backend_policy.py), [`llm_verbal_backend_policy.py`](../../src/modules/llm_verbal_backend_policy.py); `GET /health` → `llm_degradation` ([`chat_server.py`](../../src/chat_server.py)). **Drift guards:** [`tests/test_llm_policy_docs_consistency.py`](../../tests/test_llm_policy_docs_consistency.py), [`tests/test_llm_touchpoint_policies.py`](../../tests/test_llm_touchpoint_policies.py). |
| **G-05** | Cooperative LLM cancel under async chat | **Implemented (opt-in async HTTP)** | Default: thread-local cancel + sync `httpx` ([`llm_http_cancel.py`](../../src/modules/llm_http_cancel.py)); timeout → `abandon_chat_turn` + skip STM. Optional `KERNEL_CHAT_ASYNC_LLM_HTTP`: [`process_chat_turn_async`](../../src/kernel.py) + `httpx.AsyncClient` + same cancel `Event` on the `process` thread; cooperative exit from [`process`](../../src/kernel.py) at checkpoints; Anthropic `acompletion` → `AsyncAnthropic` when available ([`ADR 0002`](../adr/0002-async-orchestration-future.md)). |
| **G-06** | Generative candidates GIGO | **Closed (tests + docs)** | [`tests/test_generative_candidates.py`](../../tests/test_generative_candidates.py); [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md) §3a. |
| **G-07** | Dual perception second sample failure metadata | **Closed (code)** | [`LLMModule._maybe_apply_perception_dual_vote`](../../src/modules/llm_layer.py) merges `perception_dual_second_*` parse issues on failure. Tests: [`tests/test_perception_dual_vote_failure.py`](../../tests/test_perception_dual_vote_failure.py). |
| **G-08** | Input trust chain smoke | **Closed (test)** | [`tests/test_input_trust.py`](../../tests/test_input_trust.py) `test_chat_safe_turn_coercion_report_chain`; [`SECURITY.md`](../../SECURITY.md) link to this track. |
| **G-09** | Profile bundles for LLM-heavy demos | **Closed (code)** | [`runtime_profiles.py`](../../src/runtime_profiles.py) includes **`llm_integration_lab`** (semantic MalAbs + `KERNEL_GENERATIVE_LLM` / generative actions) alongside existing bundles (`perception_hardening_lab`, `untrusted_chat_input`, `perception_adv_consensus_lab`, …). |
| **G-10** | Cross-team integration gate | **Closed (script)** | [`scripts/eval/run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) includes LLM-track + empirical pilot (`test_empirical_pilot_runner`) + chat abandon tests per [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md); CI job **semantic-default-contract** runs `test_empirical_pilot_runner` alongside MalAbs semantic tests (`.github/workflows/ci.yml`). |
| **G-11** | LLM vertical roadmap (operator recipes, timeout metric, chain tests, focused script) | **Closed (docs + code)** | [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md); [`scripts/eval/run_llm_vertical_tests.py`](../../scripts/eval/run_llm_vertical_tests.py) includes `test_chat_turn_abandon` (G-05); empirical pilot stays on [`run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) only. |

---

## 3) Definition of done (per gap item)

- **Code:** Named constants or explicit policy branch; no silent behavior change without `CHANGELOG.md` when operator-visible.  
- **Tests:** At least one targeted test or subprocess check for new env behavior.  
- **Docs:** Update matrix or this register; link from [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) if JSON or env changes.

---

## 4) Related documents

- [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)  
- [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md) (phased operator + observability + tests)  
- [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §9 (model backlog pointer)  
- [`PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md`](PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md) (presentation-tier conversational UX vs ethics core; kernel seam map)  
- [`LLM_STACK_OLLAMA_VS_HF.md`](LLM_STACK_OLLAMA_VS_HF.md)  
- [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md) (ethics vs LLM boundary)

---

## 5) Changelog

- **2026-04-14:** Initial gap register and track ownership for Cursor LLM integration scope.
- **2026-04-14:** Closed G-01, G-02 (documentation); G-03 (`last_natural_verbal_llm_degradation_events`); G-06 (tests + perception doc); G-07 (dual-sample parse issues); G-05 (operator note); G-08 (smoke test + security link).
- **2026-04-14:** Merged LLM track into **`master-Cursor`** (active line); deprecated **`cursor-team`** as default. G-04 index in `KERNEL_ENV_POLICY.md`; G-09 `llm_integration_lab` profile; G-10 gate extended with LLM-track tests.
- **2026-04-14:** G-11 — [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md) and implementations for phases 1–5 (`kernel_env_operator` monologue key, operator recipes, async-timeout metric, MalAbs→chat perception subprocess test, `run_llm_vertical_tests.py`).
- **2026-04-15 (master-Cursor):** G-04 **closed** — `ENV_LLM_GLOBAL_DEFAULT_POLICY` / `raw_global_default_policy()` in [`llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py); perception / verbal / monologue resolvers apply step-4 fallback after legacy keys (invalid legacy falls through); [`tests/test_llm_touchpoint_policies.py`](../../tests/test_llm_touchpoint_policies.py) extended.
- **2026-04-16 (master-Cursor):** G-04 — added [`tests/test_llm_policy_docs_consistency.py`](../../tests/test_llm_policy_docs_consistency.py); Issue #4 — added [`tests/test_core_packaging_boundary_docs.py`](../../tests/test_core_packaging_boundary_docs.py) for ADR 0001 / `pyproject` / `CORE_DECISION_CHAIN.md` invariants.
- **2026-04-16 (master-Cursor):** G-04 — `KERNEL_LLM_GLOBAL_DEFAULT_POLICY` optional fallback for perception / verbal / monologue resolvers ([`llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py), [`perception_backend_policy.py`](../../src/modules/perception_backend_policy.py), [`llm_verbal_backend_policy.py`](../../src/modules/llm_verbal_backend_policy.py)); matrix + [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 updated.
- **2026-04-16 (master-Cursor):** Maturation — `GET /health` exposes `llm_degradation`; profile **`llm_staging_conservative`**; [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md) + [`SUPPORTED_COMBOS`](../../src/validators/env_policy.py) lab tier; integration gate runs [`tests/test_llm_touchpoint_policies.py`](../../tests/test_llm_touchpoint_policies.py).
- **2026-04-16 (master-Cursor):** G-05 — cooperative cancel **partial**: [`llm_http_cancel.py`](../../src/modules/llm_http_cancel.py), bridge + WebSocket + sync backends; ADR 0002 updated; semantic θ — [`tests/test_semantic_threshold_proposal_doc_alignment.py`](../../tests/test_semantic_threshold_proposal_doc_alignment.py); merge `master-antigravity` → `master-Cursor`.
- **2026-04-16 (master-Cursor):** G-05 — ``KERNEL_CHAT_ASYNC_LLM_HTTP`` + [`process_chat_turn_async`](../../src/kernel.py) + `acompletion` / `aperceive` / `acommunicate` / `anarrate` for cancellable async HTTP (Ollama/HTTP JSON); ADR 0002 §5–8.
- **2026-04-16 (master-Cursor):** G-05 follow-up — `cancel_event` on async chat path, `_process_chat_cooperative` + `ChatTurnCooperativeAbort`, `abandon_chat_turn` / `ethos_kernel_chat_turn_abandoned_effects_skipped_total`, Anthropic `AsyncAnthropic` `acompletion`; ADR 0002 + operator docs aligned.
- **2026-04-16 (master-Cursor):** ADR 0015 / I1–I5 documentation closure — [`PROPOSAL_INTEGRATION_SPRINT_I1_I5.md`](PROPOSAL_INTEGRATION_SPRINT_I1_I5.md) land record; **I2** kernel emission of `EVENT_KERNEL_WEIGHTS_UPDATED` when hierarchical feedback composes mixture weights ([`src/kernel.py`](../../src/kernel.py) `_emit_kernel_weights_updated`, [`feedback_trust_weight()`](../../src/modules/weight_authority.py)); next Cursor slice queued in [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §9.
- **2026-04-17 (master-Cursor):** Issue **#3** — [`run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) default fixture → [`labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json); [`EMPIRICAL_METHODOLOGY.md`](EMPIRICAL_METHODOLOGY.md) implementation status; [`MODULE_IMPACT_AND_EMPIRICAL_GAP.md`](MODULE_IMPACT_AND_EMPIRICAL_GAP.md) pointer.
- **2026-04-17 (master-Cursor):** Issue **#4** — extended [`tests/test_core_packaging_boundary_docs.py`](../../tests/test_core_packaging_boundary_docs.py) (`pyproject.toml` extras + `Documentation` URL); ADR 0001 / [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md) traceability.
- **2026-04-17 (master-Cursor):** Issue **#7** — [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) implementation status; [`test_warn_logs_violations_without_raise`](../../tests/test_env_policy.py); P1 checklist in [`PLAN_IMMEDIATE_TWO_WEEKS.md`](PLAN_IMMEDIATE_TWO_WEEKS.md); next milestone **P2** polish in [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §9 (G-04 closed).
- **2026-04-17 (master-Cursor):** **P2** — [`COMPOSE_PRODISH.md`](../../docs/deploy/COMPOSE_PRODISH.md) health/metrics consistency row; [`REPOSITORY_LAYOUT.md`](../../docs/REPOSITORY_LAYOUT.md) landing caveat; [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) §4 deprecation; [`test_deprecation_roadmap_has_no_extra_keys`](../../tests/test_deprecation_warnings.py).
- **2026-04-17 (master-Cursor):** Documentation — [`PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md`](PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md) cross-linked from [`CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`](CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md) §6/§9 and this file §4 (presentation-tier planning; does not change gap register G-01…G-11).
- **2026-04-17 (master-Cursor):** Field test — [`PROPOSAL_FIELD_TEST_PLAN.md`](PROPOSAL_FIELD_TEST_PLAN.md) §12 readiness gate (F1 smartphone LAN); [ADR 0017](../adr/0017-smartphone-sensor-relay-bridge.md) checklist reconciled; `.env.example` `KERNEL_FIELD_*` block.
