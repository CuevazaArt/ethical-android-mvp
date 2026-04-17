# Critique roadmap: consolidated GitHub issue backlog

Synthesizes **two independent external reviews** (April 2026). **Redundant themes are merged** (e.g. substring jailbreaks *and* “LLM perception garbage-in” → one **input-trust** epic). Unique insights from the second review are folded in: **perception path risk**, **HCI / weakness pole**, **L0 vs DAO politics**, **pip-installable core**.

Complements [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md) and the public [roadmap](https://mosexmacchinalab.com/roadmap).

---

## Disclaimer

**Ethos Kernel is maturing:** runtime, audit trails, hub/DAO scaffolding, and tests land first so **honest naming**, **calibrated weights**, and **governance experiments** can grow without perpetual rewrites. Names and mocks may run ahead of the numeric core — that gap is tracked here, not hidden.

**Structured bottleneck inventory (async vs sync, Ollama, MockDAO, naming):** [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md).

**Phased remediation plan (phases 1–5, acceptance framing, issue traceability):** [`PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md`](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md).

**Action plan (evidence vs sensors, workstreams, sequencing):** [`PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md`](PROPOSAL_ADDRESSING_CORE_WEAKNESSES.md).

---

## Maintainer triage (issues 1 through 9)

**This section is documentation only.** Assignees, milestones, and labels must be set in the GitHub UI by maintainers. Use this table to align priority before a serious **v1.0** release.

**Two-week execution plan (P0 / P1 / P2, reproduction checklists, milestone names):** [`PLAN_IMMEDIATE_TWO_WEEKS.md`](PLAN_IMMEDIATE_TWO_WEEKS.md).

Recommended interpretation of **v1.0 blockers**: issues that must be **closed or explicitly deferred** with a written rationale before marketing a “1.0” kernel/runtime as production-grade for a stated scope.

| GH # | Theme | Severity | Suggested priority | v1.0 blocker? | Suggested milestone | Assignee (set in GitHub) |
|------|-------|----------|--------------------|---------------|---------------------|---------------------------|
| 1 | “Bayesian” naming vs weighted mixture | High | P0 | No (ADR 0009; README § *What it does*; `weighted_ethics_scorer` + `bayesian_engine` wrapper) | Backlog / cleanup | Unassigned |
| 2 | Security — LLM input defense-in-depth | **Critical** | **P0** | **Yes** | **v1.0-rc** | Unassigned |
| 3 | Pilot empirical scenarios + metrics | Medium | P1 | No | Post-1.0 / evidence | Unassigned |
| 4 | Core decision chain + pip packaging | High | P1 | **Yes** (shipping boundary) | **v1.0-rc** | Unassigned |
| 5 | Poles as heuristics vs operational trust | Medium | P2 | No | Post-1.0 | Unassigned |
| 6 | Governance MockDAO vs L0 honesty | High | P0 | **Yes** (framing) | **v1.0-rc** | Unassigned |
| 7 | Reduce `KERNEL_*` combinatorics | Medium | P1 | No | Post-1.0 | Unassigned |
| 8 | Documentation translation (PR-driven) | Low | P2 | No | Ongoing | Unassigned |
| 9 | Compare commune vs other LLM approach (experimental) | Low | P3 | No | Research | Unassigned |

**Release note:** Treat **#2, #4, #6** as the minimum set to reconcile before a **v1.0** claim alongside SECURITY and packaging docs; adjust if product scope is explicitly “research-only.”

### Narrowed outside the GitHub #1–9 table (April 2026)

These came from the same external critiques but are **tracked in ADRs / weaknesses** rather than as separate GH numbers:

- **“Bayesian” scorer honesty:** Canonical [`weighted_ethics_scorer.py`](../../src/modules/weighted_ethics_scorer.py); [`bayesian_engine.py`](../../src/modules/bayesian_engine.py) exports `BayesianEngine` → `BayesianInferenceEngine` wrapping the scorer; [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md); root [`README.md`](../../README.md) § *What it does*. Aligns with Issue **#1** acceptance above.
- **WebSocket vs blocking I/O:** Chat path uses [`RealTimeBridge`](../../src/real_time_bridge.py) (worker threads). Optional `KERNEL_CHAT_TURN_TIMEOUT`, `KERNEL_CHAT_THREADPOOL_WORKERS`; [ADR 0002](../adr/0002-async-orchestration-future.md) (**partial** — async HTTP cancellation still open; see [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §1).
- **Psi Sleep counterfactuals:** [`psi_sleep.py`](../../src/modules/psi_sleep.py) uses **hash perturbation** of stored scores — **not** a second pass through `WeightedEthicsScorer`; documented as non-independent ( [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §8).

### Maintainer-facing priority stack (external synthesis, April 2026)

Ordered by leverage; **not** all map1:1 to GitHub rows above.

| Priority | Topic | In-repo status / pointer |
|----------|--------|---------------------------|
| 1 | Honest naming: “Bayesian” vs mixture | **Done:** [`README.md`](../../README.md) § *What it does*; [`weighted_ethics_scorer.py`](../../src/modules/weighted_ethics_scorer.py); [ADR 0009](../adr/0009-ethical-mixture-scorer-naming.md); [`bayesian_engine.py`](../../src/modules/bayesian_engine.py) (`BayesianInferenceEngine` wraps `WeightedEthicsScorer`). |
| 2 | External ethical benchmark | **Open:** [ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md](ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md), [EMPIRICAL_PILOT_METHODOLOGY.md](EMPIRICAL_PILOT_METHODOLOGY.md), `scripts/run_empirical_pilot.py`. |
| 3 | Semantic gate thresholds + reproducible evidence | **Partial:** [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md), tests in `tests/test_semantic_chat_gate.py`; full θ experiment backlog. |
| 4 | Async LLM / scalable chat | **Partial:** [ADR 0002](../adr/0002-async-orchestration-future.md), `KERNEL_CHAT_TURN_TIMEOUT`, `KERNEL_CHAT_THREADPOOL_WORKERS`; cooperative HTTP cancel still TBD. |
| 5 | Consolidated Pydantic settings + startup validation | **Partial / growing:** [`chat_settings.py`](../../src/chat_settings.py), [`kernel_public_env.py`](../../src/validators/kernel_public_env.py) + [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md) (`KERNEL_ENV_VALIDATION`); full single `Settings` model not unified yet. |
| 6 | Peripheral module ablation on nine scenarios | **Open:** [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](MODULE_IMPACT_AND_EMPIRICAL_GAP.md), [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) §7. |

---

## How to create issues

Paste each block into **New issue** at  
`https://github.com/CuevazaArt/ethical-android-mvp/issues`  
Suggested labels: `enhancement`, `documentation`, `security`, `research`.

**Order = impact** (P0 honesty & safety → P1 evidence & structure → P2 product/governance → P3 ops).

---

### Issue 1 — P0 · Honest naming: “Bayesian” vs weighted mixture

**Title:** `docs+core: align "Bayesian" naming with implementation (or minimal Bayes)`

**Body:**

```markdown
## Context
`BayesianEngine` uses fixed `hypothesis_weights` and linear valuations — a weighted mixture, not full posterior updating. Docstrings may over-claim.

## Goal
Rename public narrative / docs to match behavior, **or** add a minimal, tested Bayesian update on a tiny state (scoped).

## Acceptance
- [x] `THEORY_AND_IMPLEMENTATION.md` + `weighted_ethics_scorer.py` (and ADR 0009) agree on semantics; `bayesian_engine.py` wraps `WeightedEthicsScorer` (`BayesianInferenceEngine`).
- [x] Root `README.md` § *What it does* states mixture semantics and links ADR 0009 + THEORY_AND_IMPLEMENTATION.
- [x] CHANGELOG; tests extended only if semantics change.
```

---

### Issue 2 — P0 · Input trust: MalAbs gates on chat **and** perception (GIGO)

**Title:** `security: defense-in-depth for LLM-derived inputs (chat + perception JSON)`

**Body:**

```markdown
## Context (merged critiques)
- **Chat:** `evaluate_chat_text` uses static substring lists — easy to bypass with paraphrase/encoding.
- **Perception:** `llm_layer` maps text → numeric signals / context. If the LLM misclassifies or is prompt-injected, the **kernel** can be “correct” relative to **bad inputs** (garbage-in, garbage-out).

## Goal
Single threat-model doc + implementation plan:
- Harden chat gate: normalization, expanded tests, evasion cases.
- **Perception path:** validation bounds, inconsistency checks, injection tests on `process_natural` / perception JSON; optional **lightweight intent or safety classifier** (local SLM) *only* for classification — not for ethical verdict.
- README/SECURITY: heuristic bounds, not crypto guarantees.

## Acceptance
- [x] Regression tests for chat **and** perception adversarial cases.
- [x] Documented limits; no implied “unbreakable” MalAbs.
```

---

### Issue 3 — P1 · Empirical pilot (human agreement)

**Title:** `research: pilot labeled scenarios / agreement metrics`

**Body:**

```markdown
## Context
Invariant tests prove internal consistency, not external moral truth.

## Goal
Small reproducible scenario set + methodology; compare kernel vs baselines. Explicitly **not** product certification.

## Acceptance
- [x] Script + doc under `docs/` or `tests/fixtures/`.
```

**Delivered:** [`docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md`](EMPIRICAL_PILOT_METHODOLOGY.md), [`docs/proposals/EMPIRICAL_METHODOLOGY.md`](EMPIRICAL_METHODOLOGY.md) (interpretation, disclaimer, baselines, third-party comparison posture), [`docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md`](EMPIRICAL_PILOT_PROTOCOL.md), [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) (canonical **1–9**), [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) (batch + `annotation_only` vignettes; **not** certification), [`tests/test_labeled_scenarios.py`](../../tests/test_labeled_scenarios.py), [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) (`harness` filter; `expected_decision` / `batch_id`; `--output` and kernel-vs-baseline summary rates).

---

### Issue 4 — P1 · Core path documentation + packaging spike

**Title:** `architecture: document core decision chain + optional pip-installable core package`

**Body:**

```markdown
## Context
Reviewers cannot see the effective core inside advisory/telemetry volume. Second review suggests shipping **MalAbs + scoring + poles + will** as a thin installable library.

## Goal
- One diagram + table: MalAbs → scoring → poles → will → action; mark modules that cannot change `final_action`.
- **Spike:** boundary for `pip`-installable **core** vs optional “theater” (weakness, PAD, DAO mock) — even if first iteration is docs-only + stub `pyproject` layout.

## Acceptance
- [x] README/THEORY links; cross-ref RUNTIME_CONTRACT.
- [x] Issue or ADR for packaging follow-up.
```

**Delivered:** [`docs/proposals/CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md), [`docs/adr/0001-packaging-core-boundary.md`](adr/0001-packaging-core-boundary.md) (Accepted; PyPI out of scope; `theater` marker extra), root [`pyproject.toml`](../pyproject.toml) (`keywords`, `theater = []`); README ASCII diagram + install lines; [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) + [`RUNTIME_CONTRACT.md`](RUNTIME_CONTRACT.md) cross-linked.

---

### Issue 5 — P2 · Heuristic ethics & HCI: poles, weakness, PAD

**Title:** `product+docs: poles as explicit heuristics; weakness/PAD vs operational trust`

**Body:**

```markdown
## Context
- Poles use linear weights with philosophical labels — honesty required.
- **Weakness pole / PAD** add narrative “humanizing” discomfort; second review flags **HCI risk** in safety-critical domains (medicine, autonomy): simulated neurosis can **reduce** operational trust.

## Goal
- Document poles as **heuristics** or calibration roadmap (no fake precision).
- Define **profiles or modes** (e.g. demo vs critical): when narrative vulnerability is off or toned down; link to runtime profiles.

## Acceptance
- [x] THEORY or PROPUESTA subsection; no mandatory code change if docs + profile matrix suffice first.
```

**Delivered:** [`docs/proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md`](POLES_WEAKNESS_PAD_AND_PROFILES.md); [`docs/proposals/POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md`](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md); THEORY pointer; profile matrix + new **`operational_trust`** in [`src/runtime_profiles.py`](../../src/runtime_profiles.py); [`STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) table row; README link.

---

### Issue 6 — P2 · Governance narrative: MockDAO exit + L0 constitution

**Title:** `governance: exit criteria from mock + honest framing of immutable L0`

**Body:**

```markdown
## Context
- MockDAO is in-memory; audit narrative ≠ distributed consensus.
- **PreloadedBuffer (L0)** is immutable in code — “dictatorship of the repo” is a real political tension vs DAO rhetoric.

## Goal
- Checklist for any move beyond mock (legal, identity, serialization) — link `/blockchain-dao`.
- Short doc section: L0 as **explicit non-negotiable constitution** in-process; how community governance (drafts, votes) relates **without** silently rewriting MalAbs in runtime.

## Acceptance
- [x] Single doc section; aligns with PROPUESTA / UNIVERSAL_ETHOS.
```

**Delivered:** [`docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md`](GOVERNANCE_MOCKDAO_AND_L0.md); cross-link from [`docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md`](UNIVERSAL_ETHOS_AND_HUB.md) + [`RUNTIME_CONTRACT.md`](RUNTIME_CONTRACT.md); README; `mock_dao.py` module note.

---

### Issue 7 — P3 · Consolidate `KERNEL_*` via profiles + policy

**Title:** `ops: reduce env combinatorics — profiles, deprecation, unsupported combos`

**Body:**

```markdown
## Context
Feature-flag sprawl matches “laboratory of ideas” more than a maintainable operator surface.

## Goal
Expand `runtime_profiles.py`, document unsupported combinations, optional deprecation path for redundant flags.

## Acceptance
- [x] ESTRATEGIA updated; CI green.
```

**Delivered:** [`docs/proposals/KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md); [`docs/proposals/STRATEGY_AND_ROADMAP.md`](STRATEGY_AND_ROADMAP.md) §4 table + policy link; **`lan_operational`** + **`moral_hub_extended`** in [`src/runtime_profiles.py`](../../src/runtime_profiles.py); README pointer; typed [`KernelPublicEnv`](../../src/validators/kernel_public_env.py) + [`KERNEL_ENV_TYPED_PUBLIC_API.md`](KERNEL_ENV_TYPED_PUBLIC_API.md) (phased Pydantic surface for cross-flag rules).

---

## Tracking table

GitHub issue numbers (if they match this backlog):

| # | Short title | Issue |
|---|-------------|-------|
| 1 | Bayesian naming | #1 |
| 2 | Input trust (chat + perception) | #2 |
| 3 | Empirical pilot | #3 |
| 4 | Core doc + pip spike | #4 |
| 5 | Poles + weakness HCI | #5 |
| 6 | Governance mock + L0 | #6 |
| 7 | KERNEL_* consolidation | #7 |
| 8 | Documentation translation | #8 |
| 9 | Commune vs LLM (experimental) | #9 |
