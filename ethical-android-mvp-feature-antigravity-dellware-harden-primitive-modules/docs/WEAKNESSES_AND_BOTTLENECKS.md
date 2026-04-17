# Weaknesses and bottlenecks

This note is an **honest inventory** for operators and reviewers: known limits of the current architecture and naming. It complements the consolidated backlog in [CRITIQUE_ROADMAP_ISSUES.md](proposals/CRITIQUE_ROADMAP_ISSUES.md) and the forward-looking [PRODUCTION_HARDENING_ROADMAP.md](proposals/PRODUCTION_HARDENING_ROADMAP.md). It is **not** a commitment order for fixes.

---

## 1. Synchronous ethic core under an async runtime

**Observation.** The decision pipeline (`EthicalKernel.process`, `process_chat_turn`) is **synchronous** and mixes CPU-ish work (e.g. Bayesian-style scoring, narrative bookkeeping, optional reflection stacks) with blocking-style I/O inside the same call stack (e.g. LLM HTTP when configured).

**What exists today.** The main **WebSocket chat** path uses [`RealTimeBridge`](../src/real_time_bridge.py), which runs `process_chat_turn` in a **worker thread** (Starlette ``run_in_threadpool`` by default, or a **dedicated** pool when ``KERNEL_CHAT_THREADPOOL_WORKERS`` > 0), so the **asyncio event loop** accepts new connections while a turn runs ([`chat_server`](../src/chat_server.py)). Optional ``KERNEL_CHAT_TURN_TIMEOUT`` bounds the **async** wait and returns JSON ``chat_turn_timeout`` when exceeded; the handler sets a **cooperative cancel** event so sync LLM backends skip **further** blocking HTTP in that thread ([`llm_http_cancel`](../src/modules/llm_http_cancel.py)), calls [`abandon_chat_turn`](../src/kernel.py) so late workers skip STM / ``wm.add_turn``, and (when ``KERNEL_CHAT_ASYNC_LLM_HTTP=1``) passes the same event into [`process_chat_turn_async`](../src/kernel.py) so the thread running [`EthicalKernel.process`](../src/kernel.py) shares cancel scope and can **exit cooperatively** at several checkpoints (not OS-preempted inside one long native call). An **in-flight** sync ``httpx`` request is still not cancelled mid-read unless **async** LLM HTTP is enabled (use ``OLLAMA_TIMEOUT`` for sync). **Psi Sleep** is not on the per-message chat path; when async code needs it, use [`RealTimeBridge.run_execute_sleep`](../src/real_time_bridge.py). **WebSocket disconnect** runs checkpoint save and conduct-guide export through the same offload helper so teardown does not block the loop for other sessions.

**Remaining risks.**

- **Thread-pool queueing:** Many concurrent sessions compete for worker threads; tail latency grows under burst load even though the loop stays responsive — tune ``KERNEL_CHAT_THREADPOOL_WORKERS`` and host limits.
- **CPU saturation:** Heavy turns still consume OS threads and CPU; this is not “free” async scalability.
- **In-flight LLM cancellation:** Optional ``KERNEL_CHAT_ASYNC_LLM_HTTP`` on the chat path uses ``httpx.AsyncClient`` for Ollama/HTTP JSON and passes the cancel event into the thread that runs ``process``; Anthropic ``api`` mode uses ``AsyncAnthropic`` for ``acompletion`` when the SDK is installed. The default worker-thread path only skips **subsequent** sync completions after the async deadline.
- **Other entry points:** Batch harnesses, tests, or future HTTP handlers must **not** call the kernel directly on the event loop if latency isolation matters — mirror the bridge pattern (including ``run_execute_sleep`` for Psi Sleep) or document the trade-off.

**Pointers:** [ADR 0002 — async orchestration (partial)](adr/0002-async-orchestration-future.md) — cooperative cancel **partial** (thread-local event + sync backend checks + abandon + async-path ``process`` checkpoints); async HTTP for in-flight cancel on Ollama/HTTP JSON; align ``OLLAMA_TIMEOUT`` with ``KERNEL_CHAT_TURN_TIMEOUT`` for tighter wall-clock bounds; [PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md](proposals/PROPOSAL_SYNC_KERNEL_ASYNC_ASGI_BRIDGE.md) (thread offload for chat turns, WebSocket JSON, advisory telemetry); [PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md](proposals/PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md) (runtime must not block the kernel on network I/O without a future async design).

---

## 2. “Bayesian” naming vs the running implementation

**Observation.** Canonical code is [`weighted_ethics_scorer.py`](../src/modules/weighted_ethics_scorer.py): a **fixed convex combination** of stylized hypotheses with **bounded optional nudges** (e.g. episodic weight refresh). There is **no** continuous online posterior update from streaming evidence in the sense of full Bayesian inference. `BayesianEngine` is a **historical alias**; `bayesian_engine.py` is a compat shim ([ADR 0009](adr/0009-ethical-mixture-scorer-naming.md)).

**Why it matters.** The old name `BayesianEngine` and early docs can be read as promising calibrated posteriors; the implementation is deliberately simpler for testability and transparency.

**Pointers:** [README.md](../README.md) (maturation disclaimer); [THEORY_AND_IMPLEMENTATION.md](proposals/THEORY_AND_IMPLEMENTATION.md) (explicit “no Bayesian updating” note); [CRITIQUE_ROADMAP_ISSUES.md](proposals/CRITIQUE_ROADMAP_ISSUES.md) Issue 1.

---

## 3. Local inference (Ollama) and failure modes

**Observation.** Ollama (and similar local servers) are strong for **sovereignty**, but the stack does not ship a **full circuit-breaker / degradation policy** for all inference failures: slow hosts, repeated HTTP errors, or **structurally valid JSON that is semantically wrong** for perception.

**What exists today.** Configurable timeouts (e.g. `OLLAMA_TIMEOUT`), Pydantic validation and coercion in [`perception_schema`](../src/modules/perception_schema.py), lexical cross-checks in [`perception_cross_check`](../src/modules/perception_cross_check.py), and heuristic fallbacks for some bad LLM outputs **reduce** but do not **eliminate** bad states. Optional **dual LLM perception** ([`perception_dual_vote`](../src/modules/perception_dual_vote.py), profile `perception_adv_consensus_lab`) runs a second structured sample (different temperature and/or `KERNEL_PERCEPTION_DUAL_OLLAMA_MODEL`); large hostility/risk disagreement inflates coercion uncertainty so `KERNEL_PERCEPTION_UNCERTAINTY_DELIB` can force `D_delib`. That mitigates **some** lone-model hallucinations but is **not** an independent ground-truth check — two samples can still agree on a false high-threat parse. Semantic **embedding** transport has its own retry/circuit patterns in [`semantic_embedding_client`](../src/modules/semantic_embedding_client.py); the **main chat perception** path is not uniformly covered to the same degree.

**Gap.** A single operator-visible policy for “backend unhealthy → fast-fail / template mode / session banner” across **all** LLM touchpoints is still aspirational.

**Pointers:** [INPUT_TRUST_THREAT_MODEL.md](proposals/INPUT_TRUST_THREAT_MODEL.md); [MALABS_SEMANTIC_LAYERS.md](proposals/MALABS_SEMANTIC_LAYERS.md); [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) (cosine defaults: not empirically calibrated in-repo); [PERCEPTION_VALIDATION.md](proposals/PERCEPTION_VALIDATION.md).

---

## 4. MockDAO: local governance simulation, not distributed consensus

**Observation.** `MockDAO` and related hub flows are **in-process / SQLite-backed demos**. They provide traceability and UX for constitution drafts, votes, and audit lines — **not** on-chain finality, BFT, or real P2P governance. There is **no** production Solidity in this repo; quadratic voting **assumes** a closed, honest participant table (no Sybil model).

**Why it matters.** Operators must not equate mock votes with production-grade distributed policy or legal authority. The **scalar ethical choice** (`final_action`) does **not** flow from DAO votes in the current architecture — see [MOCK_DAO_SIMULATION_LIMITS.md](proposals/MOCK_DAO_SIMULATION_LIMITS.md). Because the ledger lives in the **same process** as the kernel, a compromised runtime can corrupt **both** decision state and audit history; there is no cryptographic separation of powers.

**Mitigation (partial).** Set `KERNEL_AUDIT_SIDECAR_PATH` so [`MockDAO.register_audit`](../src/modules/mock_dao.py) mirrors each row as JSONL on disk — use tight file permissions or ship logs to a separate system. This is **not** a signed append-only service; see [PRODUCTION_HARDENING_ROADMAP.md](proposals/PRODUCTION_HARDENING_ROADMAP.md) for stronger governance posture.

**Pointers:** [RUNTIME_CONTRACT.md](proposals/RUNTIME_CONTRACT.md); [GOVERNANCE_MOCKDAO_AND_L0.md](proposals/GOVERNANCE_MOCKDAO_AND_L0.md); [UNIVERSAL_ETHOS_AND_HUB.md](proposals/UNIVERSAL_ETHOS_AND_HUB.md); [`contracts/README.md`](../contracts/README.md).

---

## 5. No external “moral ground truth” benchmark in-repo

**Observation.** Agreement metrics ([`scripts/run_empirical_pilot.py`](../scripts/run_empirical_pilot.py)) use **maintainer-authored** reference actions unless you merge an **expert-panel** dataset. That measures alignment with a **declared** label set, not independent philosophy or law.

**Pointers:** [ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md](proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md); [EMPIRICAL_PILOT_METHODOLOGY.md](proposals/EMPIRICAL_PILOT_METHODOLOGY.md).

---

## 6. Pole linear weights and context multipliers (heuristic)

**Observation.** Multipolar scores load from configurable linear JSON ([ADR 0004](adr/0004-configurable-linear-pole-evaluator.md)) and combine with `EthicalPoles` base and context weights. The numbers are **design choices** (including legacy parity for the default JSON), not the output of a documented human-judgment calibration study.

**Why it matters.** Calling these weights “validated” or implying statistical grounding from the small default empirical pilot (nine batch scenarios) would **overclaim**: the pilot targets **action-level** agreement templates, not identification of many free parameters in pole telemetry.

**Pointers:** [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](proposals/POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md); [POLES_WEAKNESS_PAD_AND_PROFILES.md](proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md); [EMPIRICAL_PILOT_METHODOLOGY.md](proposals/EMPIRICAL_PILOT_METHODOLOGY.md).

---

## 7. Many modules, one argmax — peripheral complexity without ablation evidence

**Observation.** The repo contains a **large** `src/modules` surface (dozens of files) for a core path where **`final_action`** is the mixture scorer’s **chosen candidate name** after MalAbs pruning; poles, weakness, PAD, augenesis, and similar layers often affect **mode**, **narrative**, **LLM tone**, or **post-decision** state — not a second pick among actions.

**Why it matters.** Bugs in “exotic” modules may **not** move `final_action` on standard tests, so **green unit tests** can hide regressions that matter for **UX, trust, or longitudinal behavior**. The project has not yet published a **large ablation** (“disable N modules → measure Δ decision quality”) — that is **evidence debt**, acknowledged as a research gap.

**Pointers:** [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](proposals/MODULE_IMPACT_AND_EMPIRICAL_GAP.md); [CORE_DECISION_CHAIN.md](proposals/CORE_DECISION_CHAIN.md); [`tests/test_decision_core_invariants.py`](../tests/test_decision_core_invariants.py).

---

## 8. Psi Sleep counterfactuals — no independent quality evaluator

**Observation.** [`psi_sleep.py`](../src/modules/psi_sleep.py) assigns **synthetic** counterfactual scores via a **deterministic hash perturbation** of each episode’s stored `ethical_score`. It does **not** re-run [`WeightedEthicsScorer`](../src/modules/weighted_ethics_scorer.py) or reconstruct candidate actions through `process`. Therefore it **cannot** validate the day engine against a second policy, human panel, or external benchmark — and it **does not** detect systematic bugs in the scorer (at most bounded nudges to `pruning_threshold` / locus `caution`).

**Why it matters.** Treating Psi Sleep as “Bayesian night validation” or equivalent to a **model critique** loop would **overclaim**. Honest posture: audit **theater** + reproducible stress signal until an independent evaluator path exists.

**Pointers:** [`PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md`](proposals/PROPOSAL_ETHICAL_CORE_LOGIC_EVOLUTION.md) (B1); [`ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md`](proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md); stable id `psi_sleep_hash_perturbation_v1` on `SleepResult`.

---

## Related

- [CORE_DECISION_CHAIN.md](proposals/CORE_DECISION_CHAIN.md) — who sets `final_action`.
- [TRANSPARENCY_AND_LIMITS.md](TRANSPARENCY_AND_LIMITS.md) — user-facing guarantees and limits.
- **Operator visibility:** Prometheus metrics (`KERNEL_METRICS=1`), structured logs (`KERNEL_LOG_JSON`), and `GET /health` — [OPERATOR_QUICK_REF.md](proposals/OPERATOR_QUICK_REF.md#observability-metrics-and-logs); starter Grafana JSON in [`deploy/grafana/`](../deploy/grafana/README.md).
