# PROPOSAL — Ethical core logic evolution (track B)

**Status:** proposal — **B1 partially implemented** (feedback ledger, WebSocket `operator_feedback`, Psi Sleep mixture apply behind flags); **B2 partially implemented** (nominal profiles: semantic gate + hash fallback; degradation table in `MALABS_SEMANTIC_LAYERS.md`).  
**Scope:** deepen **deliberation-grade** ethics without pretending full Bayesian inference or unbreakable safety. Complements [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md), [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md), and the episodic-weight spike in [PRODUCTION_HARDENING_ROADMAP.md](PRODUCTION_HARDENING_ROADMAP.md).

---

## B1. Psi Sleep v2 — from audit-only to **bounded** mixture updates

### Problem

Today, **Psi Sleep** ([`PsiSleep`](../src/modules/psi_sleep.py)) mainly:

- Reviews recent [`NarrativeEpisode`](../src/modules/narrative.py) rows and **simulates** pruned alternatives using a **deterministic hash perturbation** (MVP audit, not a second forward pass through `BayesianEngine`).
- Emits **global recalibrations** that `execute_sleep` applies to **`pruning_threshold`** and **locus `caution`** ([`EthicalKernel.execute_sleep`](../src/kernel.py)), not to **`hypothesis_weights`**.

Separately, during **`process`**, optional **`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`** calls [`BayesianEngine.refresh_weights_from_episodic_memory`](../src/modules/bayesian_engine.py): a **bounded blend** toward a heuristic target derived from **ethical_score** statistics of same-context episodes. That is **not** user-feedback-aware and **not** tied to the nightly Psi Sleep cycle.

### Proposal

**Goal:** Make the **end-of-day** (or scheduled) consolidation window the **canonical** place to fold **outcome evidence** into **`hypothesis_weights`**, with explicit **auditability** and **safety caps**.

1. **Feedback channel (explicit)**  
   - Define a minimal operator or user signal: e.g. *approve*, *dispute*, *harm_report* (exact enum TBD), attached to **session**, **episode id**, or **turn id** — **no** requirement to store raw chat in the audit log if policy forbids it; hashes/ids only where possible.

2. **Confusion-style ledger**  
   - Persist a rolling structure (e.g. JSON or SQLite table) classifying **decision outcomes** vs **feedback**:
     - Rows: predicted regime (e.g. `decision_mode`, gray-zone flag) × outcome label × count (and optional stratification by `context`).
     - This is a **calibration aid**, not a medical or legal confusion matrix.

3. **Update rule (honest naming)**  
   - Map ledger statistics to a **target mixture** vector (3-way or future *k*-way), then apply the **same style of bounded blend** already used in `refresh_weights_from_episodic_memory` (blend factor, normalization, fallback when data sparse).
   - Optionally **unify** episodic score-based refresh and feedback-based refresh behind one function with **documented precedence** (e.g. feedback overrides sparse episodes).

4. **Invocation**  
   - Run the weight update inside **`execute_sleep`** (after or merged with current Psi Sleep findings), or behind a new flag **`KERNEL_PSI_SLEEP_UPDATE_MIXTURE=1`** so batch simulations stay reproducible without surprise drift.

5. **Invariants**  
   - **MalAbs / buffer** never relaxed by this path.  
   - Respect [`identity_integrity`](../src/modules/identity_integrity.py) / genome drift caps (`KERNEL_ETHICAL_GENOME_MAX_DRIFT` in [`kernel.py`](../src/kernel.py)) for any persisted weights.  
   - **Regression:** invariant ethical properties and golden scenarios must remain green; tuning is **opt-in** in CI until stabilized.

### Deliverables (when implemented)

- Schema for feedback + ledger + migration from “no feedback” deployments.
- Unit tests: empty ledger → no change; synthetic ledger → expected bounded movement; cap enforcement.
- Operator doc: what feedback means, abuse risks (gaming weights), and retention.

---

## B2. Semantic chat gate — from optional bolt-on to **default input-trust** in perception

### Problem

**Lexical MalAbs** is fast and auditable but **easily evaded** by paraphrase, homoglyphs, and multilingual phrasing ([INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)). If hostile **intent** reaches **`perceive` → `process`** unchanged, deliberation operates on **already poisoned** signals.

Today, [`semantic_chat_gate`](../src/modules/semantic_chat_gate.py) runs only when **`KERNEL_SEMANTIC_CHAT_GATE`** is enabled (default off in code paths that read env). Architecturally it already sits **after** lexical MalAbs and **before** full chat deliberation — good — but operators must **opt in**, so many deployments remain lexical-only.

### Proposal

**Goal:** Treat **embedding (and optional LLM arbiter) semantic gating** as part of the **standard perception / input-trust stack**, not an exotic add-on — while keeping **fail-safe** behavior when embeddings or Ollama are down.

1. **Policy default**  
   - Move **nominal** runtime profiles toward **`KERNEL_SEMANTIC_CHAT_GATE=1`** for chat surfaces that face the open internet or untrusted users; keep **lexical-only** profiles for lab, air-gapped, or latency-critical demos **explicitly named** in [`runtime_profiles.py`](../src/runtime_profiles.py).

2. **Degradation ladder**  
   - If embed transport fails or circuit breaker opens: **block ambiguous** band, **fall back** to lexical-only, or **fail closed** — behavior must be **one documented ladder** (per [MALABS_SEMANTIC_LAYERS.md](MALABS_SEMANTIC_LAYERS.md)), not ad-hoc per call site.

3. **Latency and ops**  
   - Document extra round-trip cost; recommend timeouts and local embedding models; align with [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) (inference fragility).

4. **False positives**  
   - Keep **θ_block / θ_allow** tunable; add **telemetry** (counts: semantic_block, semantic_allow, arbiter_call) for calibration without logging user text.

5. **Non-goals**  
   - Semantic gate does **not** replace MalAbs; it **narrows** the lexical bypass surface. **No** claim of “intent understood” in a cognitive sense — remain **heuristic** in docs and UI.

### Deliverables (when implemented)

- Profile + CHANGELOG entry for default-on migration path.
- Integration tests: gate on/off; degraded backend → expected ladder.
- Update [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md) “unsupported combos” if new defaults interact with hub or chat JSON contracts.

---

## Related code and docs

| Piece | Location |
|-------|----------|
| Psi Sleep | [`src/modules/psi_sleep.py`](../src/modules/psi_sleep.py), `execute_sleep` in [`src/kernel.py`](../src/kernel.py) |
| Mixture weights (episodic) | [`BayesianEngine.refresh_weights_from_episodic_memory`](../src/modules/bayesian_engine.py), `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS` |
| Semantic gate | [`src/modules/semantic_chat_gate.py`](../src/modules/semantic_chat_gate.py), MalAbs chat path in [`absolute_evil.py`](../src/modules/absolute_evil.py) |
| Snapshot persistence of weights | [`kernel_io.py`](../src/persistence/kernel_io.py), immortality backup |
| Async / thread bridge | [`real_time_bridge.py`](../src/real_time_bridge.py) — extra embed latency still runs inside the same turn thread unless future ADR splits I/O |

---

## Acceptance criteria (proposal-level)

- [x] B1 and B2 can be adopted **independently** (flags or profiles).  
- [x] No merge path weakens **Absolute Evil** or **buffer** principles (weights path only; MalAbs unchanged).  
- [x] Numeric drift is **bounded** by `hypothesis_weights_allowed` + genome reference; **reversible** via snapshot / immortality restore.  
- [x] Documentation uses **honest** terms: “bounded mixture update”, not “true posterior” unless the math is implemented.

**Remaining (future work):** richer confusion matrix by `context`; correlate feedback rows with episode ids in persistence. **Done (telemetry):** `ethos_kernel_semantic_malabs_outcomes_total` when `KERNEL_METRICS=1` ([`metrics.py`](../../src/observability/metrics.py)).

---

*MoSex Macchina Lab — ethical core logic track B.*
