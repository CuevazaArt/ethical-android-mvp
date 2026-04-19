# LLM vertical roadmap — phased expansion and gap closure

**Status:** Active execution plan (Cursor line, `master-Cursor`).  
**Language:** English (durable record per repository policy).  
**Relates to:** [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) (gap register G-01…), [`MODEL_CRITICAL_BACKLOG.md`](MODEL_CRITICAL_BACKLOG.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §1 and §3.

---

## 1) Purpose

**Vertical expansion** means deepening each layer of the LLM stack—policy clarity, runtime observability, operator tooling, and test-backed contracts—without treating “more features” as a substitute for traceability.

This proposal **justifies** a phased roadmap and records **evidence posture**: items are either implemented in-repo (code + tests), explicitly deferred with a linked ADR or weakness note, or marked as process-only.

---

## 2) Problem statement

1. **Configuration surface:** Many `KERNEL_*` families touch LLM behavior (completion JSON, MalAbs semantic, embeddings, generative candidates). A single-prefix env namespace remains **deferred** ([`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3); operators need a **stable mental model** and cockpit grouping, not only a flat env list.
2. **Async bridge vs HTTP:** Chat turns use `asyncio.wait_for` around synchronous kernel work; **cooperative cancellation** of in-flight LLM HTTP is not implemented ([ADR 0002](../adr/0002-async-orchestration-future.md); track G-05). Operators still need **measurable** signals when the async deadline fires while worker threads may continue.
3. **Trust chain:** Lexical MalAbs, semantic tier, and structured perception are **separate modules**; end-to-end regressions must prove benign paths still produce perception after the semantic tier runs under production-like defaults ([`test_malabs_semantic_integration.py`](../../tests/test_malabs_semantic_integration.py) pattern).

---

## 3) Phases (definition of done)

### Phase 1 — Operator surface and documentation

**Goal:** Align [`kernel_env_operator.py`](../../src/validators/kernel_env_operator.py) families with the LLM touchpoint index in [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md); document **composite recipes** (profile + overrides) in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md).

**Done when:**

- `ethos config` classifies monologue gate and related keys under the LLM family where applicable.
- Quick reference lists at least three **named recipes** (staging slow HTTP, airgap hash semantic, generative lab) pointing at `ETHOS_RUNTIME_PROFILE` bundles.

**Not in scope:** Renaming all env vars to `KERNEL_LLM_*` (product decision; remains deferred).

### Phase 2 — Degradation event contract (touchpoints)

**Goal:** Keep **communicate / narrate / monologue** degradation records aligned with [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md): each recorded event exposes `touchpoint`, `failure_reason`, `recovery_policy` where the layer emits them.

**Done when:** Tests assert the contract for each verbal path used in CI ([`tests/test_llm_verbal_backend_policy.py`](../../tests/test_llm_verbal_backend_policy.py)).

### Phase 3 — Async deadline observability (G-05 partial)

**Goal:** When `KERNEL_CHAT_TURN_TIMEOUT` elapses, increment a **Prometheus counter** (opt-in `KERNEL_METRICS=1`) so operators can alert on “async waiter gave up / worker may still run” separately from end-to-end turn histograms.

**Done when:** Metric documented in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md); no claim of cooperative HTTP cancel.

### Phase 4 — Lexical → semantic → perception chain

**Goal:** One subprocess integration test proves a **benign** `process_chat_turn` completes with perception after MalAbs semantic defaults (hash fallback, fast-fail HTTP), matching [`test_malabs_semantic_integration.py`](../../tests/test_malabs_semantic_integration.py) environment strategy.

**Done when:** Test lives beside existing MalAbs semantic integration tests and passes in CI.

### Phase 5 — Focused regression command

**Goal:** Script listing LLM-vertical tests for fast local/CI optional runs ([`scripts/eval/run_llm_vertical_tests.py`](../../scripts/eval/run_llm_vertical_tests.py)).

**Done when:** Script exits non-zero on failure; documented in this file and cross-team gate doc.

---

## 4) Execution checklist (maintenance)

| Phase | Owner | Tracked in |
|-------|--------|------------|
| 1 | Cursor line | `CHANGELOG.md`, this file |
| 2 | Cursor line | `tests/test_llm_verbal_backend_policy.py` |
| 3 | Cursor line | `src/observability/metrics.py`, `OPERATOR_QUICK_REF.md` |
| 4 | Cursor line | `tests/test_malabs_semantic_integration.py` |
| 5 | Cursor line | `scripts/eval/run_llm_vertical_tests.py` |

---

## 5) Related documents

- [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md)  
- [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md)  
- [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)

---

## 6) Changelog

- **2026-04-14:** Initial roadmap (phases 1–5) aligned with integration track and weaknesses §1/§3.
