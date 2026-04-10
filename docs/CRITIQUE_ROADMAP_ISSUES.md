# Critique roadmap: consolidated GitHub issue backlog

Synthesizes **two independent external reviews** (April 2026). **Redundant themes are merged** (e.g. substring jailbreaks *and* “LLM perception garbage-in” → one **input-trust** epic). Unique insights from the second review are folded in: **perception path risk**, **HCI / weakness pole**, **L0 vs DAO politics**, **pip-installable core**.

Complements [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) and the public [roadmap](https://mosexmacchinalab.com/roadmap).

---

## Disclaimer

**Ethos Kernel is maturing:** runtime, audit trails, hub/DAO scaffolding, and tests land first so **honest naming**, **calibrated weights**, and **governance experiments** can grow without perpetual rewrites. Names and mocks may run ahead of the numeric core — that gap is tracked here, not hidden.

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
- [x] `THEORY_AND_IMPLEMENTATION.md` + `bayesian_engine.py` agree on semantics.
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
- [ ] Script + doc under `docs/` or `tests/fixtures/`.
```

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
- [ ] README/THEORY links; cross-ref RUNTIME_CONTRACT.
- [ ] Issue or ADR for packaging follow-up.
```

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
- [ ] THEORY or PROPUESTA subsection; no mandatory code change if docs + profile matrix suffice first.
```

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
- [ ] Single doc section; aligns with PROPUESTA / UNIVERSAL_ETHOS.
```

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
- [ ] ESTRATEGIA updated; CI green.
```

---

## Tracking table

Fill in GitHub issue numbers after creation:

| # | Short title | Issue |
|---|-------------|-------|
| 1 | Bayesian naming | 1|
| 2 | Input trust (chat + perception) | 2|
| 3 | Empirical pilot | 3|
| 4 | Core doc + pip spike | 4|
| 5 | Poles + weakness HCI |5 |
| 6 | Governance mock + L0 | 6|
| 7 | KERNEL_* consolidation |7 |
