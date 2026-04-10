# Critique follow-up: disclaimer & GitHub issue backlog

This document records an **external technical critique** (April 2026) and turns it into **ordered work items**. It complements [ESTRATEGIA_Y_RUTA.md](ESTRATEGIA_Y_RUTA.md) and the public [roadmap](https://mosexmacchinalab.com/roadmap).

---

## Disclaimer (read this first)

**Ethos Kernel is maturing.** The repository already ships a serious invariant-tested decision pipeline, runtime, persistence, and governance **mocks** — but several **names and narratives** run ahead of the current numeric core (e.g. “Bayesian” as a weighted mixture, DAO as in-memory mock). **We are deliberately building infrastructure first:** runtime profiles, audit trails, hub/DAO scaffolding, optional encryption, LAN clients — so that **calibrated weights**, **stronger safety boundaries**, and **paths toward real governance** can land without rewriting the world every month.

Nothing here promises a finished moral philosophy or on-chain democracy tomorrow. It **does** commit to **honest labeling**, **testable claims**, and a **published backlog** (below) you can track on GitHub Issues.

---

## How to create the issues

`gh` may not be installed locally. For each block below, use **New issue** on  
`https://github.com/CuevazaArt/ethical-android-mvp/issues`  
and paste **Title** and **Body**. Suggested labels: `enhancement`, `documentation`, `security`, `research` (create if missing).

Issues are ordered by **impact** (honesty & safety first, then evidence, then structure & governance narrative).

---

### Issue 1 — P0 · Terminology: Bayesian engine vs weighted mixture

**Title:** `docs+core: align "Bayesian" naming with implementation (or implement minimal Bayes)`

**Body:**

```markdown
## Context
The critique notes that `BayesianEngine` uses fixed `hypothesis_weights` and linear valuations — a weighted mixture, not full posterior updating. The docstrings/formulas suggest more than the code delivers.

## Goal
- Either **rename** the public API / docs to match behavior (e.g. weighted ethical scoring under a fixed mixture), **or**
- Implement a **minimal, documented** Bayesian update on a tiny state (e.g. confidence/impact priors) with tests — scoped so it does not explode complexity.

## Acceptance
- [ ] `THEORY_AND_IMPLEMENTATION.md` + `bayesian_engine.py` header describe the same object without over-claiming.
- [ ] CHANGELOG entry.
- [ ] Tests unchanged or extended for any new semantics.
```

---

### Issue 2 — P0 · Safety: harden `evaluate_chat_text` (jailbreak / weapon strings)

**Title:** `security: strengthen chat-text gate beyond substring lists`

**Body:**

```markdown
## Context
`evaluate_chat_text` relies on fixed phrase lists; trivial paraphrases can bypass.

## Goal
Defense in depth: normalization, expanded coverage, optional lightweight classifier or local model path — with tests for evasion patterns. Document threat model: heuristic MalAbs gate, not cryptographic security.

## Acceptance
- [ ] Regression tests for paraphrases / edge cases.
- [ ] README/SECURITY note on limits.
```

---

### Issue 3 — P1 · Evidence: pilot empirical validation (human agreement)

**Title:** `research: pilot benchmark / human-labeled scenarios for kernel decisions`

**Body:**

```markdown
## Context
Invariant tests check internal consistency, not alignment with external moral ground truth.

## Goal
Small, ethical review–friendly dataset of scenarios + inter-rater or expert labels; compare kernel vs baselines. Publish methodology limits (no "objective morality" claim).

## Acceptance
- [ ] Reproducible script + doc under `docs/` or `tests/fixtures/`.
- [ ] Clear scope: exploratory, not product certification.
```

---

### Issue 4 — P1 · Architecture: document & package "core path" vs advisory layers

**Title:** `docs: single "core decision path" map vs advisory/telemetry modules`

**Body:**

```markdown
## Context
Many modules are tone-only or post-decision; reviewers struggle to see the ~effective core.

## Goal
One diagram + table in README or THEORY: MalAbs → scoring → poles → will → action; list modules that cannot change `final_action` unless contract says otherwise.

## Acceptance
- [ ] Linked from README.
- [ ] Cross-links to RUNTIME_CONTRACT advisory rules.
```

---

### Issue 5 — P2 · Calibration: ethical poles as named linear weights

**Title:** `design: justify or calibrate pole linear weights (or relabel as heuristics)`

**Body:**

```markdown
## Context
Poles apply fixed linear transforms; philosophical labels exceed the mechanism.

## Goal
Document as heuristics OR define a calibration roadmap (expert labels, sensitivity analysis). No fake precision.

## Acceptance
- [ ] PROPUESTA or THEORY subsection + optional issue split for data collection.
```

---

### Issue 6 — P2 · Governance: mock DAO → criteria for "beyond mock"

**Title:** `governance: document exit criteria from MockDAO to external / testnet experiments`

**Body:**

```markdown
## Context
MockDAO is in-memory; useful for audit narrative, not distributed consensus.

## Goal
Threat model + legal/partner gates + technical criteria (serialization, identity) **before** any chain talk. Link blockchain-dao page.

## Acceptance
- [ ] Single doc section + checklist; no code promise.
```

---

### Issue 7 — P3 · Operations: reduce `KERNEL_*` combinatorial debt

**Title:** `ops: consolidate KERNEL_* surface via profiles + deprecation policy`

**Body:**

```markdown
## Context
Many env flags; risk of unsupported combinations.

## Goal
Expand `runtime_profiles.py` coverage, document unsupported combos, optional deprecation path for redundant flags.

## Acceptance
- [ ] ESTRATEGIA table updated.
- [ ] CI still green.
```

---

## Tracking

After creating issues on GitHub, add **this table** (issue numbers are filled in manually):

| Order | Title (short) | GitHub issue |
|-------|----------------|--------------|
| 1 | Bayesian / naming | # |
| 2 | Chat-text safety | # |
| 3 | Empirical pilot | # |
| 4 | Core vs advisory docs | # |
| 5 | Poles calibration | # |
| 6 | DAO exit criteria | # |
| 7 | KERNEL_* consolidation | # |
