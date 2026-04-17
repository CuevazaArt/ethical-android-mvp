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
2. **Async bridge vs HTTP:** Chat turns use `asyncio.wait_for` around synchronous kernel work; **cooperative cancellation** skips further sync LLM HTTP after the async deadline (G-05 partial; [`llm_http_cancel.py`](../../src/modules/llm_http_cancel.py)); in-flight HTTP is still bounded by read timeout ([ADR 0002](../adr/0002-async-orchestration-future.md)). Operators still need **measurable** signals when the async deadline fires while worker threads may continue.
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

### Phase 3 — Cancellation Cooperativa y Desmonolitización de I/S (G-05 P0)

**Goal:** Resolver el cuello de botella sincrónico en `kernel.py`. Cuando `KERNEL_CHAT_TURN_TIMEOUT` expire, no solo incrementar la métrica, sino ejecutar una **cancelación cooperativa HTTP real**. Esto implica migrar el I/O de inferencia desde `httpx` sincrónico dentro del hilo worker a `httpx.AsyncClient` gestionado de forma nativa por el event loop, interrumpiendo proactivamente la sobrecarga de inferencia local/remota.

**Done when:**
- El Worker Pool no se satura por conexiones inferencia zombis después del timeout.
- Abstracción de Handlers de red asíncronos fuera del objeto `EthicalKernel` monolítico.
- Documentado en [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md).

### Phase 4 — Lexical → semantic → perception chain

**Goal:** One subprocess integration test proves a **benign** `process_chat_turn` completes with perception after MalAbs semantic defaults (hash fallback, fast-fail HTTP), matching [`test_malabs_semantic_integration.py`](../../tests/test_malabs_semantic_integration.py) environment strategy.

**Done when:** Test lives beside existing MalAbs semantic integration tests and passes in CI.

### Phase 5 — Focused regression command

**Goal:** Script listing LLM-vertical tests for fast local/CI optional runs ([`scripts/eval/run_llm_vertical_tests.py`](../../scripts/eval/run_llm_vertical_tests.py)).

**Done when:** Script exits non-zero on failure; documented in this file and cross-team gate doc.

**Targets include:** G-05 cooperative cancel ([`tests/test_llm_http_cancel.py`](../../tests/test_llm_http_cancel.py), [`tests/test_chat_async_llm_cancel.py`](../../tests/test_chat_async_llm_cancel.py), [`tests/test_chat_turn_abandon.py`](../../tests/test_chat_turn_abandon.py)) alongside verbal/touchpoint/MalAbs/operator metrics tests. Empirical pilot regression ([`tests/test_empirical_pilot_runner.py`](../../tests/test_empirical_pilot_runner.py)) lives in [`run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) only — too slow for this focused vertical by default ([Issue #3](PLAN_IMMEDIATE_TWO_WEEKS.md) / [`EMPIRICAL_METHODOLOGY.md`](EMPIRICAL_METHODOLOGY.md)).

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
- **2026-04-16:** Phase 5 — [`run_llm_vertical_tests.py`](../../scripts/eval/run_llm_vertical_tests.py) includes cooperative-cancel tests through `test_chat_turn_abandon`; [`run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) extends the gate with `test_empirical_pilot_runner` (Issue 3); [`CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md) list aligned. Phase 3 — abandoned-turn metric + ADR 0002 alignment in [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md).
