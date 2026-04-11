# Hardening roadmap toward serious deployment (non-binding)

**Status:** **proposal + synthesis** — complements [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) and the critique backlog [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md). **Does not** replace the runtime contract or promise "production" certification until explicit acceptance criteria and tests exist.

**Purpose:** capture the **value** of hardening perception, data contracts, modularity, and honest UX **without** hiding limits: the kernel remains an **auditable MVP**; any new layer must be documented as a **heuristic** where appropriate ([`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)).

---

## What the repository already covers (to avoid redundancy)

| Topic | Location |
|-------|----------|
| MalAbs honesty / GIGO | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`SECURITY.md`](../SECURITY.md) |
| Bounded perception + tests | `src/modules/llm_layer.py`, `tests/test_input_trust.py` |
| Lighthouse / epistemic doubt (tone) | [`LIGHTHOUSE_KB.md`](LIGHTHOUSE_KB.md), `reality_verification.py` |
| Runtime profiles + CI | [`src/runtime_profiles.py`](../src/runtime_profiles.py), `tests/test_runtime_profiles.py` |
| Core / packaging boundary | [`adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md) |
| L0 vs DAO / drafts | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) |
| HCI / weakness | [`POLES_WEAKNESS_PAD_AND_PROFILES.md`](POLES_WEAKNESS_PAD_AND_PROFILES.md) |
| "Bayesian" = fixed mixture, not full posterior | [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) Issue 1 + [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) |

---

## Core–narrative analysis (April 2026) — value vs redundancy

Synthesis of internal review: **what adds value** versus what is already stated in the repo and **what not to duplicate**.

### Functional findings

| Observation | Adds documentary value? | Redundancy / nuance |
|-------------|---------------------------|----------------------|
| **`BayesianEngine`** uses three fixed-weight hypotheses (`hypothesis_weights`, e.g., `[0.4, 0.35, 0.25]`) that are not updated from **`NarrativeMemory`** | **Yes** — makes explicit the *gap* "learns narratively, does not recalibrate priors numerically." | Issue 1 already aligns **naming** and semantics; here the new nuance is **using episodes for weights**, not just renaming. |
| **`EthicalPoles`** with simple linear formula (`benefit * 0.6 + vulnerability * 0.4 - risk * 0.2` in heuristic) and little use of **action name** | **Yes** — clarifies the MVP multipolar limit. | Coherent with explicit multipolar in theory; not marketed as a deep semantic model. |
| **Chat text MalAbs** vulnerable to **leet/variants** (`b0mb`, `how 2`) | **Partially redundant** with [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) (paraphrase, homoglyphs). | The **leet** example is a useful reminder to prioritize **additional normalization** or optional layer; does not replace the "not infallible" warning. |
| **LLM perception** as a single point of failure; bad JSON → signals **by default** near "calm" | **Yes** — risk of **silent GIGO**. | Partially covered by clamps + tests + `epistemic_dissonance` in parallel; the gap is **explicitly marking perception uncertainty** in the pipeline (future spike). |

### Architectural findings

| Observation | Adds documentary value? | Redundancy / nuance |
|-------------|---------------------------|----------------------|
| **`EthicalKernel.__init__`** couples many concrete modules; no abstract-type interfaces | **Yes** — reinforces Phase 2 of this roadmap and the [packaging ADR](adr/0001-packaging-core-boundary.md). | Already recognized as "mock" DAO; value is **formalizing contract** when a second implementer exists. |
| Signals without **confidence intervals**; `epistemic_dissonance` compensates **in parallel** | **Yes** — future design: uncertainty **in** the signal vector vs only a separate layer. | Honest documentation; implementation is research. |
| **`consequence_projection`** only narrative; does not feed back into Bayes | **Yes** — aligns with "qualitative teleology, no Monte Carlo" contract in v7. | Not a bug if the product does not promise to close the loop; closing it would be a **scope change**. |

### Value register — high-impact spike

**Proposal:** use **`NarrativeMemory`** (last *N* episodes, grouped by **context** or similar) to derive an **empirical distribution** of ethical scores and **adjust `hypothesis_weights`** before each Bayesian evaluation (with limits, smoothing, and non-regression tests).

| Advantage | Risk / condition |
|---------|---------------------|
| Moves from static to **experience→prior** without inventing a new LLM | Must avoid **unwanted drift** and **overfitting** to history biases; reproducibility (`VariabilityEngine`, seeds). |
| Fits with existing snapshot/persistence of weights | Requires specification: window *N*, decay, freeze by operator profile. |

**Status:** *registered as direction*; **not** implemented here. Fits with Issue 1 (Bayesian semantics) and with [`HISTORY.md`](../HISTORY.md) / CHANGELOG if spiked.

---

## Comprehensive review — strengths (value register)

| Strength | Why it matters |
|-------------|-----------------|
| **Explicit computational ethical agency** (philosophy, decision, test verifiability) | Rare in OSS; fits [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) and README purpose. |
| **Modularity with clear ethical roles** (Uchi–Soto, buffer, locus, Psi Sleep, etc.) | Facilitates per-module audit; "who sets `final_action`" table in [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md). |
| **Dense documentation** (theory, history v1–v12, `docs/proposals/`, bibliography) | Academically transparent; reduces "black box." |
| **Multiple surfaces** (batch, WebSocket, static dashboard, landing) | Demonstrates real runtime without coupling to a single UI. |
| **Large test suite** (invariants, integration, persistence) | Foundation for regression; does not replace external validation (see Issue 3 in critique). |

---

## Comprehensive review — critiques (value vs redundancy)

| Critique | Documentary value | Redundancy / nuance |
|---------|-------------------|----------------------|
| **No external "ethical truth"** — simulations are not the real world | **Central and non-redundant** as a reminder. | Explicitly covered by [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) **Issue 3** (empirical pilot); "correct" criterion is **open by design** in applied philosophy. |
| **Complexity** — critical modules vs narrative? | **Yes** — pushes toward a "criticality map" for onboarding. | Partially mitigated by [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md); modules like Psi Sleep / weakness are **advisory** by contract. |
| **LLM: perception and communication as bias** | **Yes** — coherent with GIGO. | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md) + tone layers; no promise of LLM neutrality. |
| **Persistence** — corruption, concurrency, inter-snapshot audit | **Yes** as *product gaps* if multi-client HA is promised. | [`RUNTIME_PERSISTENT.md`](RUNTIME_PERSISTENT.md) already sets limits; round-trip tests exist; **corruption/concurrency** are optional non-MVP lab extensions. |
| **Mock DAO / "governance" not on-chain** | **Yes** — avoids hype. | [`GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md) and README already frame **mock / off-chain**. |
| **Input trust** — heuristics not detailed in README | **Partial** — README links `INPUT_TRUST`; fine matrix lives in docs. | Possible improvement: **summary table** in README (deep link). |
| **Ad-hoc API / many `KERNEL_*`** | **Yes** — integration friction. | [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) + profiles; optional OpenAPI with `KERNEL_API_DOCS` (see policy). |
| **Platform metrics** (repo age, issue count) | **Low** — change over time; **not** quality indicators. | Ignore as evidence in stable documentation. |
| **No benchmarks vs baselines** | **Yes**. | Issue 3 + "No objectives" section (no simulation-alone certification). |
| **Branding** (repo slug vs Ethos Kernel vs lab) | **Yes** — barrier for new readers. | Register in README "Naming" or HISTORY; **no** immediate rename obligation. |
| **ES/EN mixed** | **Yes** for global contributions. | Bilingual index or `docs/en/` folder as incremental improvement. |
| **Few examples of "real" dialogue** | **Yes** — improves pedagogy. | Case studies = editorial work; can link to LAN demos. |

---

## Conclusions for improvements (operational synthesis)

These conclusions **do not** replace [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) or the backlog; they order priorities **after** already-registered rounds (technical robustness, lighthouse epistemology, v8 demo).

### Short term (higher signal / lower friction)

1. **Scope honesty:** keep visible that the core is **MVP verifiable in tests**, not "certified ethics" — README + Issue 3.
2. **Integration and operators:** continue densifying [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) and profiles; consider **minimal `KERNEL_*` table** in README (links to long doc).
3. **Perception:** mark JSON failures / uncertainty in pipeline (spikes already listed in Phase 1 of this document).
4. **Persistence:** add **opt-in** corruption/concurrency tests only if a concrete deployment demands it (do not block lab).

### Medium term

1. **Empirical validation** — Issue 3: protocol with annotators / experts, **without** conflating with universal moral truth.
2. **Comparative benchmarks** — define baselines (rules, LLM-only, kernel) and **agreed** metrics (not single "ethical correctness").
3. **Onboarding:** map "module → critical vs advisory" derived from `CORE_DECISION_CHAIN` + runtime contract.
4. **Language:** index of proposals ES → EN or short English summaries in header of each `PROPUESTA_*.md`.

### Long term

1. **Real governance** — only if there are threat models and necessity; repo **does not** mandate blockchain.
2. **Certification / external audit** — possible framework; outside current code scope unless explicit product decision.

### Reflection (register)

The tension between **verifiable formalism** and **situated ethics** is inherent; the project assumes it better when documenting limits (simulations, mocks, heuristics). The risk of "internal beauty without external impact" is mitigated by **empirical pilot** and **honest benchmarks**, not just more modules.

---

## Phase 1 — Input trust and perception (0–3 months *orientative*)

**Goal:** reduce GIGO and trivial attacks **without** replacing the normative core with an opaque model.

| Proposal | Value | Conditions / risks |
|-----------|--------|------------------------|
| **Optional lightweight classifier** (e.g., risk tags, not text generation) **alongside** MalAbs lists | Defense-in-depth against paraphrase; offline possible. | Dependencies, latency, false positives; must be **opt-in** (`KERNEL_*`), reproducible CI, and **not** "infallible moderation." |
| **Strong LLM output contract** (Pydantic / JSON Schema in APIs) | Validation failure before Bayes; aligns with structured perception. | Code already has clamping; the jump is **schema + explicit errors** + tests. |
| **Dual perception check** (e.g., discrepancy → `D_delib` or uncertainty flag) | Coherent with perception-as-attack-vector critique. | Auditor cannot be "another unlimited LLM"; define thresholds and tests. |

**Explicit backlog link:** epic issue **input trust** in [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) (chat + perception).

---

## Phase 2 — Architecture: core vs extensions (3–6 months *orientative*)

**Goal:** integrations (e.g., robotics) that only need **signals → decision** without dragging narrative/DAO.

| Proposal | Value | Conditions / risks |
|-----------|--------|------------------------|
| **Package `ethos-core` vs `ethos-extensions`** (or equivalent in monorepo) | Aligned with packaging ADR; reduces coupling. | Large refactor; criterion: which tests define the **ethical core** vs telemetry. |
| **Local pub/sub event bus** for memory, DAO, PAD, etc. | Isolate secondary subsystem failures. | Order, determinism and current sync tests; incremental design (no big-bang rewrite). |

---

## Phase 3 — UX and constitution (6+ months *orientative*)

**Goal:** human trust and auditable governance **without** dictating philosophy from a single opaque file.

| Proposal | Value | Conditions / risks |
|-----------|--------|------------------------|
| **Weakness → epistemic transparency** (model/sensor limits instead of "simulated emotion" in critical domains) | Coherent with honest HCI (Issue 5). | Copy change + product contract; not just `weakness_pole` refactor. |
| **L0 externalized** (versioned YAML/JSON) | Audit without reading Python; foundation for future signatures/DAO. | Tensions with "L0 in code" today; requires **threat model**, migration, and identical-load tests. |

---

## Non-objectives (explicit)

- Replace MalAbs or the buffer with a **single** untraced ML classifier without regression tests.
- Promise **absolute security** or infallible moderation (see [`SECURITY.md`](../SECURITY.md)).
- Confuse this document with a **commercial** SLA commitment or certification.

---

## Closing the proposal round (documentary)

Entries for **"production v2"**, **core–narrative**, and **comprehensive review (strengths / critiques / conclusions)** are **archived** in this file as a single record. New product ideas should open **issues** or specific ADRs; do not duplicate long lists here unless summarized.

For scope changes or code spikes: [`CHANGELOG.md`](../CHANGELOG.md) + PR.

---

## Cross-references

- [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) — P0–P3 priorities and robustness → epistemology → demo order (§3.1).
- [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) — flag combinations.
- [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) — normative pipeline.

*Living document — align substantial changes with HISTORY/CHANGELOG when spikes execute or phases close.*
