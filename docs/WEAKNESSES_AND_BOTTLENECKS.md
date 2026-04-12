# Weaknesses and bottlenecks

This note is an **honest inventory** for operators and reviewers: known limits of the current architecture and naming. It complements the consolidated backlog in [`docs/proposals/CRITIQUE_ROADMAP_ISSUES.md`](proposals/CRITIQUE_ROADMAP_ISSUES.md) and the forward-looking [`docs/proposals/PRODUCTION_HARDENING_ROADMAP.md`](proposals/PRODUCTION_HARDENING_ROADMAP.md). It is **not** a commitment order for fixes.

---

## 1. Synchronous ethic core under an async runtime

**Observation.** The decision pipeline (`EthicalKernel.process`, `process_chat_turn`) is **synchronous** and mixes CPU-ish work (e.g. Bayesian-style scoring, narrative bookkeeping, optional reflection stacks) with blocking-style I/O inside the same call stack (e.g. LLM HTTP when configured).

**What exists today.** The main **WebSocket chat** path uses [`RealTimeBridge`](../src/real_time_bridge.py), which runs `process_chat_turn` in a **worker thread** via `asyncio.to_thread`, so the **asyncio event loop** is not blocked for that entry point ([`chat_server`](../src/chat_server.py)).

**Remaining risks.**

- **Thread-pool queueing:** Many concurrent chat sessions still compete for the default executor; tail latency grows under burst load even though the loop stays responsive.
- **CPU saturation:** Heavy turns still consume OS threads and CPU; this is not “free” async scalability.
- **Other entry points:** Batch harnesses, tests, or future HTTP handlers must **not** call the kernel directly on the event loop if latency isolation matters — mirror the bridge pattern or document the trade-off.

**Pointers:** [ADR 0002 — async orchestration (future)](adr/0002-async-orchestration-future.md); [PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md](proposals/PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md) (runtime must not block the kernel on network I/O without a future async design).

---

## 2. “Bayesian” naming vs the running implementation

**Observation.** The engine is a **fixed convex combination** of stylized hypotheses with **bounded optional nudges** (e.g. episodic weight refresh). There is **no** continuous online posterior update from streaming evidence in the sense of full Bayesian inference.

**Why it matters.** The name `BayesianEngine` and surrounding docs can be read as promising calibrated posteriors; the implementation is deliberately simpler for testability and transparency.

**Pointers:** [README.md](../README.md) (maturation disclaimer); [THEORY_AND_IMPLEMENTATION.md](proposals/THEORY_AND_IMPLEMENTATION.md) (explicit “no Bayesian updating” note); [CRITIQUE_ROADMAP_ISSUES.md](proposals/CRITIQUE_ROADMAP_ISSUES.md) Issue 1.

---

## 3. Local inference (Ollama) and failure modes

**Observation.** Ollama (and similar local servers) are strong for **sovereignty**, but the stack does not ship a **full circuit-breaker / degradation policy** for all inference failures: slow hosts, repeated HTTP errors, or **structurally valid JSON that is semantically wrong** for perception.

**What exists today.** Configurable timeouts (e.g. `OLLAMA_TIMEOUT`), Pydantic validation and coercion in [`perception_schema`](../src/modules/perception_schema.py), and heuristic fallbacks for some bad LLM outputs **reduce** but do not **eliminate** bad states. Semantic **embedding** transport has its own retry/circuit patterns in [`semantic_embedding_client`](../src/modules/semantic_embedding_client.py); the **main chat perception** path is not uniformly covered to the same degree.

**Gap.** A single operator-visible policy for “backend unhealthy → fast-fail / template mode / session banner” across **all** LLM touchpoints is still aspirational.

**Pointers:** [INPUT_TRUST_THREAT_MODEL.md](proposals/INPUT_TRUST_THREAT_MODEL.md); [MALABS_SEMANTIC_LAYERS.md](proposals/MALABS_SEMANTIC_LAYERS.md); [PERCEPTION_VALIDATION.md](proposals/PERCEPTION_VALIDATION.md).

---

## 4. MockDAO: local governance simulation, not distributed consensus

**Observation.** `MockDAO` and related hub flows are **in-process / SQLite-backed demos**. They provide traceability and UX for constitution drafts, votes, and audit lines — **not** on-chain finality, BFT, or real P2P governance.

**Why it matters.** Operators must not equate mock votes with production-grade distributed policy or legal authority.

**Pointers:** [RUNTIME_CONTRACT.md](proposals/RUNTIME_CONTRACT.md); [GOVERNANCE_MOCKDAO_AND_L0.md](proposals/GOVERNANCE_MOCKDAO_AND_L0.md); [UNIVERSAL_ETHOS_AND_HUB.md](proposals/UNIVERSAL_ETHOS_AND_HUB.md).

---

## 5. Pole linear weights and context multipliers (heuristic)

**Observation.** Multipolar scores load from configurable linear JSON ([ADR 0004](adr/0004-configurable-linear-pole-evaluator.md)) and combine with `EthicalPoles` base and context weights. The numbers are **design choices** (including legacy parity for the default JSON), not the output of a documented human-judgment calibration study.

**Why it matters.** Calling these weights “validated” or implying statistical grounding from the small default empirical pilot (nine batch scenarios) would **overclaim**: the pilot targets **action-level** agreement templates, not identification of many free parameters in pole telemetry.

**Pointers:** [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](proposals/POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md); [POLES_WEAKNESS_PAD_AND_PROFILES.md](proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md); [EMPIRICAL_PILOT_METHODOLOGY.md](proposals/EMPIRICAL_PILOT_METHODOLOGY.md).

---

## Related

- [CORE_DECISION_CHAIN.md](proposals/CORE_DECISION_CHAIN.md) — who sets `final_action`.
- [TRANSPARENCY_AND_LIMITS.md](TRANSPARENCY_AND_LIMITS.md) — user-facing guarantees and limits.
