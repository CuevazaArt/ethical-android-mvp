# Hardening roadmap toward serious deployment (non-binding)

**Status:** **proposal + synthesis** — complements [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) and the critique backlog [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md). It **does not** replace the runtime contract or promise “production” certification until acceptance criteria and tests exist.

**Purpose:** capture the **value** of hardening perception, data contracts, modularization, and honest UX **without** hiding limits: the kernel remains an **auditable MVP**; any new layer must be documented as **heuristic** where appropriate ([`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)).

---

## What the repository already covers (avoid duplication)

| Topic | Where |
|-------|--------|
| MalAbs / GIGO honesty | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`SECURITY.md`](../SECURITY.md) |
| Bounded perception + tests | `src/modules/llm_layer.py`, `tests/test_input_trust.py` |
| Perception: coercion report + opt-in threshold → `D_delib` | `src/modules/perception_schema.py` (`PerceptionCoercionReport`), `src/kernel.py` (`KERNEL_PERCEPTION_UNCERTAINTY_*`), `tests/test_perception_coercion_report.py`, `tests/test_perception_uncertainty_delib.py` |
| LLM parse + lexical risk + cross-check (Phase 1) | `parse_perception_llm_raw_response`, `light_risk_classifier.py`, `perception_cross_check.py`, `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`, tests `test_perception_parse_contract.py` / `test_light_risk_classifier.py` / `test_perception_cross_check.py` |
| Lighthouse / epistemic doubt (tone) | [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md), `reality_verification.py` |
| Runtime profiles + CI | [`src/runtime_profiles.py`](../src/runtime_profiles.py), `tests/test_runtime_profiles.py` |
| Core / packaging boundary | [`adr/0001-packaging-core-boundary.md`](../adr/0001-packaging-core-boundary.md) |
| L0 vs DAO / drafts | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) |
| HCI / weakness | [`POLES_WEAKNESS_PAD_AND_PROFILES.md`](POLES_WEAKNESS_PAD_AND_PROFILES.md) |
| “Bayesian” = fixed mixture, not full posterior | [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) Issue 1 + [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) |
| **Bottlenecks / weaknesses** (sync core vs async, Ollama, MockDAO, naming) — inventory in English, single place | [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) |

Do not duplicate long paragraphs on those topics here: keep detail there and use this roadmap for phases and synthesis.

---

## Core–narrative analysis (April 2026) — value vs redundancy

Internal review synthesis: **what adds** vs what is already in the repo and **what not to duplicate**.

### Functional findings

| Observation | Documentary value? | Redundancy / nuance |
|-------------|-------------------|---------------------|
| **`BayesianEngine`** uses three hypotheses with fixed weights (`hypothesis_weights`, e.g. `[0.4, 0.35, 0.25]`) not updated from **`NarrativeMemory`** | **Yes** — states the gap “learns narratively, does not recalibrate numeric priors.” | Issue 1 already aligns **naming** and semantics; the new nuance is **using episodes for weights**, not rename only. |
| **`EthicalPoles`** with simple linear formula (`benefit * 0.6 + vulnerability * 0.4 - risk * 0.2` in heuristics) and little use of **action name** | **Yes** — clarifies multipolar MVP limits. | Coherent with explicit multipolar theory; not sold as deep semantic model. |
| **MalAbs text** vulnerable to **leet variants** (`b0mb`, `how 2`) | **Partially redundant** with [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) (paraphrase, homoglyphs). | The **leet** example is a useful reminder to prioritize **extra normalization** or an optional layer; not a substitute for “not infallible.” |
| **LLM perception** as single point of failure; bad JSON → **default** signals near “calm” | **Yes** — **silent GIGO** risk. | Partially covered by clamps + tests + parallel `epistemic_dissonance`; **delivered spike:** coercion report + `uncertainty` in chat JSON; **opt-in** `KERNEL_PERCEPTION_UNCERTAINTY_DELIB` can promote `D_fast` → `D_delib` (not MalAbs nor a “second auditor LLM”). |

### Architectural findings

| Observation | Documentary value? | Redundancy / nuance |
|-------------|-------------------|---------------------|
| **`EthicalKernel.__init__`** couples many concrete modules; no `AbstractDAO`-style interfaces | **Yes** — reinforces Phase 2 of this roadmap and [packaging ADR](../adr/0001-packaging-core-boundary.md). | “Mock” DAO already acknowledged; value is **formalizing contracts** when a second implementer exists. |
| Signals without **confidence intervals**; `epistemic_dissonance` compensates **in parallel** | **Yes** — future design: uncertainty **in** the signal vector vs only a side layer. | Honest documentation; implementation is research. |
| **`consequence_projection`** narrative-only; does not feed Bayes | **Yes** — matches “qualitative teleology, no Monte Carlo” in v7. | Not a bug if the product does not promise closing the loop; closing it is **scope change**. |

### Value register — relatively high-impact spike

**Proposal:** use **`NarrativeMemory`** (last *N* episodes, grouped by **context** or similar) to derive an **empirical distribution** of ethical scores and **adjust `hypothesis_weights`** before each mixture evaluation (with bounds, smoothing, and no-regression tests).

| Benefit | Risk / condition |
|---------|------------------|
| Moves from static to **experience→prior** without inventing a new LLM | Avoid unwanted **drift** and **overfitting** to history bias; reproducibility (`VariabilityEngine`, seeds). |
| Fits existing snapshot / weight persistence | Needs spec: window *N*, decay, freeze per operator profile. |

**Status:** *recorded as direction*; **not** implemented here. Fits Issue 1 (mixture semantics) and [`HISTORY.md`](../HISTORY.md) / CHANGELOG if a spike lands.

---

## Integrated review — strengths (value register)

| Strength | Why it matters |
|----------|----------------|
| **Explicit computational ethical agency** (philosophy, decision, test verifiability) | Uncommon in OSS; fits [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) and README purpose. |
| **Modularity with clear ethical roles** (Uchi–Soto, buffer, locus, Psi Sleep, …) | Enables per-module audit; “who sets `final_action`” table in [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md). |
| **Dense documentation** (theory, history v1–v12, `docs/proposals/`, bibliography) | Academically transparent; less “black box.” |
| **Multiple surfaces** (batch, WebSocket, static dashboard, landing) | Shows real runtime without one mandatory UI. |
| **Large test suite** (invariants, integration, persistence) | Regression base; not external validation (see critique Issue 3). |

---

## Integrated review — criticisms (value vs redundancy)

| Criticism | Documentary value | Redundancy / nuance |
|-----------|-------------------|---------------------|
| **No external “ethical ground truth”** — simulations ≠ real world | **Central, not redundant** as reminder. | Explicitly covered by [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) **Issue 3** (empirical pilot); “correct” is **open by design** in applied philosophy. |
| **Complexity** — critical modules vs narrative? | **Yes** — pushes a “criticality map” for onboarding. | Partially mitigated by [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md); Psi Sleep / weakness are **advisory** by contract. |
| **LLM: perception and communication as bias** | **Yes** — consistent with GIGO. | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) + tone layers; no claim of LLM neutrality. |
| **Persistence** — corruption, concurrency, audit across snapshots | **Yes** as *product gaps* if multi-client HA is promised. | [`RUNTIME_PERSISTENT.md`](RUNTIME_PERSISTENT.md) states limits; round-trip tests exist; **corruption/concurrency** are optional MVP-lab extensions. |
| **Mock DAO / “governance” not on-chain** | **Yes** — avoids hype. | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) and README already frame **mock / off-chain**. |
| **Input trust** — heuristics not fully detailed in README | **Partial** — README links `INPUT_TRUST`; fine matrix lives in docs. | Possible improvement: **summary table** in README (deep link). |
| **Ad-hoc API / many `KERNEL_*`** | **Yes** — integration friction. | [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) + profiles; optional OpenAPI with `KERNEL_API_DOCS` (see policy). |
| **Platform metrics** (repo age, issue count) | **Low** — time-varying; **not** kernel quality evidence. | Ignore as stable-doc evidence. |
| **No benchmarks vs baselines** | **Yes**. | Issue 3 + “Non-goals” (no certification from simulation alone). |
| **Branding** (repo slug vs Ethos Kernel vs lab) | **Yes** — barrier for new readers. | Record in README “Naming” or HISTORY; **no** immediate repo rename required. |
| **Mixed ES/EN** | **Yes** for global contributors. | Canonical filenames are `PROPOSAL_*.md` (English); `PROPUESTA_*.md` are legacy redirects; migrate remaining Spanish bodies to English over time. |
| **Few “real dialogue” examples** | **Yes** — pedagogy. | Case studies = editorial work; can link LAN demos. |

---

## Conclusions for improvements (operational synthesis)

These conclusions **do not** replace [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) or the backlog; they order priorities **after** rounds already recorded (technical robustness, lighthouse epistemology, v8 demo).

### Short term (high signal / low friction)

1. **Scope honesty:** keep visible that the core is an **MVP verifiable in tests**, not “certified ethics” — README + Issue 3.
2. **Integration and operators:** keep densifying [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) and profiles; consider a **minimal `KERNEL_*` table** in README (link to long doc).
3. **Perception:** surface JSON failures / uncertainty in pipeline (spikes listed in Phase 1 below).
4. **Persistence:** add **opt-in** corruption/concurrency tests only if a concrete deployment requires them (do not block the lab).

### Medium term

1. **Empirical validation** — Issue 3: annotator / expert protocol agreement, **without** claiming universal moral truth.
2. **Comparative benchmarks** — baselines (rules, LLM-only, kernel) and **agreed** metrics (not a single “ethical correctness”).
3. **Onboarding:** “module → critical vs advisory” map from `CORE_DECISION_CHAIN` + runtime contract.
4. **Language:** canonical filenames `PROPOSAL_*.md` (English); legacy Spanish redirects remain stubs; translate remaining Spanish-only bodies incrementally.

### Long term

1. **Real governance** — only with a threat model and need; the repo **does not** mandate blockchain.
2. **Certification / external audit** — possible framework; outside current code scope unless product explicitly decides.

### Reflection (record)

Tension between **verifiable formalism** and **situated ethics** is inherent; the project handles it best when limits are documented (simulations, mocks, heuristics). “Internal beauty without external impact” is mitigated with **empirical pilot** and **honest benchmarks**, not only more modules.

---

## Phase 1 — Input trust and perception (0–3 months *indicative*)

**Goal:** reduce GIGO and trivial attacks **without** replacing the normative core with an opaque model.

| Proposal | Value | Conditions / risks |
|----------|--------|----------------------|
| **Optional lightweight classifier** (e.g. risk labels, no long text generation) **alongside** list-based MalAbs | Defense in depth vs paraphrase; offline possible. | Dependencies, latency, false positives; must be **opt-in** (`KERNEL_*`), CI-reproducible, and **not** “infallible moderation.” |
| **Strong LLM output contract** (Pydantic / JSON Schema on APIs) | Fail validation before Bayes; aligns with structured perception. | **Delivered spike:** `parse_perception_llm_raw_response` + `parse_issues` on `coercion_report`; `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL` for parse failures; tests `test_perception_parse_contract.py`. Pydantic/coercion remain the numeric layer. |
| **Second perception check** (e.g. discrepancy → `D_delib` or uncertainty flag) | Coherent with perception as attack surface. | **Delivered spike (no second LLM):** `KERNEL_LIGHT_RISK_CLASSIFIER` + `KERNEL_PERCEPTION_CROSS_CHECK` set `cross_check_discrepancy` and raise `uncertainty` (combinable with `KERNEL_PERCEPTION_UNCERTAINTY_DELIB`); tests `test_light_risk_classifier.py`, `test_perception_cross_check.py`. |

**Explicit backlog link:** epic **input trust** in [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) (chat + perception).

---

## Phase 2 — Architecture: core vs extensions (3–6 months *indicative*)

**Goal:** integrations (e.g. robotics) that only need **signals → decision** without dragging full narrative/DAO.

| Proposal | Value | Conditions / risks |
|----------|--------|----------------------|
| **`ethos-core` vs `ethos-extensions` package** (or monorepo equivalent) | Matches packaging ADR; reduces coupling. | Large refactor; criterion: which tests define **ethical core** vs telemetry. **Doc spike:** [`adr/0006-phase2-core-boundary-and-event-bus.md`](../adr/0006-phase2-core-boundary-and-event-bus.md), [`PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md). |
| **Local event bus (pub/sub)** for memory, DAO, PAD, etc. | Isolate secondary subsystem failures. | **Incremental spike delivered:** opt-in synchronous `KernelEventBus` (`KERNEL_EVENT_BUS`), `kernel.decision` and `kernel.episode_registered` events; see ADR 0006, `src/modules/kernel_event_bus.py`, `tests/test_kernel_event_bus.py`, `phase2_event_bus_lab` profile. Async / multiprocess remains **out of scope**. |

---

## Phase 3 — UX and constitution (6+ months *indicative*)

**Goal:** human trust and auditable governance **without** encoding philosophy in one opaque file.

| Proposal | Value | Conditions / risks |
|----------|--------|----------------------|
| **Weakness → epistemic transparency** (model/sensor limits instead of “simulated emotion” in critical domains) | Honest HCI (Issue 5). | Copy + product contract change; not only `weakness_pole` refactor. |
| **Externalized L0** (versioned YAML/JSON) | Audit without reading Python; base for future signatures/DAO. | Tensions with “L0 in code” today; needs **threat model**, migration, load-identical tests. |

---

## Non-goals (explicit)

- Replace MalAbs or the buffer with a **single** ML classifier without traceability and regression tests.
- Promise **absolute safety** or infallible moderation (see [`SECURITY.md`](../SECURITY.md)).
- Treat this document as a **commercial SLA** or certification commitment.

---

## Closing the proposal round (documentation)

Entries on **“production v2”**, **core–narrative**, and **integrated review (strengths / critiques / conclusions)** are **archived** here as a single record. New product ideas should open **issues** or ADRs; do not duplicate long lists here except as synthesis.

For scope changes or code spikes: [`CHANGELOG.md`](../CHANGELOG.md) + PR.

---

## Cross-references

- [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) — P0–P3 priorities and robustness → epistemology → demo order (§3.1).
- [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) — flag combinations.
- [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) — normative pipeline.

*Living document — align substantive changes with HISTORY/CHANGELOG when spikes land or phases close.*
