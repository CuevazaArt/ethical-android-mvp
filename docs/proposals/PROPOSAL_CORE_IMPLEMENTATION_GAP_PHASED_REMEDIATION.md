# Proposal: phased remediation — core implementation gap vs. documentation

**Status:** planning / backlog structure (April 2026).  
**Related:** [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md), [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md), [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md), [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md).

---

## 1. Purpose

This document **structures** a single cross-cutting risk: **names and architecture imply stronger guarantees than concrete implementations** in the highest-impact paths (MalAbs, buffer, Bayesian scoring, perception) and in **governance mocks** (e.g. `moral_hub` / MockDAO in-memory votes).

It is **not** a commitment to implement every line below in one release. It is the **canonical phase map**, acceptance framing, and traceability to GitHub issues so work can be sequenced without scope drift.

---

## 2. Design principle — two problems, two success criteria

| Track | Question | “Done” looks like |
|-------|----------|-------------------|
| **A. Pipeline integrity** | Can an adversary or bad LLM JSON silently drive the kernel to unsafe or incoherent behavior? | Fail-closed or explicitly degraded behavior; adversarial tests; documented semantics. |
| **B. Governance product** | Can an operator **verify** what was voted, when, and under what kernel state? | Durable records + auditable linkage (identity/quorum rules are **explicit** — may remain lab-scoped). |

**Rule:** do not treat “DAO” work as a substitute for **A**. Decorative governance is primarily a **track B** honesty and persistence problem; core safety is **track A**.

---

## 3. Phase 1 — Core integrity (urgent; ~2–4 weeks per slice)

**Goal:** shrink the gap between **documented intent** and **testable behavior** for the three critical modules plus MalAbs policy.

### 3.1 Bayesian engine — honest inference semantics

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 1.1a | Document the **current contract**: what is fixed mixture vs. episodic evidence, what is *not* claimed as full posterior inference. | `src/modules/bayesian_engine.py`, [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) | Docstrings + theory doc agree; [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) Issue **#1** closable or narrowed. |
| 1.1b | If updating from memory: **bounded** updates (caps, context match) to avoid silent drift. | `bayesian_engine.py`, episodic memory call sites | Tests for “no unbounded drift” on synthetic sequences. |
| 1.1c | **Three ethical frames** must remain **measurably distinct**: utilitarian (welfare sum), deontological (rule violations), virtue (character consistency). | Same | Minimal canonical scenarios where **rankings diverge**; tests fail if frames collapse to identical ordering. |

### 3.2 Buffer — semantic verification layer (not a silent replacement)

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 1.2a | **Lab path A:** local embeddings + cosine threshold vs. canonical principle descriptions (auditable catalog). | `src/modules/buffer.py`, optional small fixture set | Tests: paraphrase cannot trivially bypass without a recorded signal (tier / uncertainty / block). |
| 1.2b | **Lab path B (heavier):** controlled LLM queries (“does this violate principle X?”) with **fail-closed** policy when the verifier is unavailable. | `llm_layer.py`, buffer integration | No silent fallback to “lexical-only OK” without explicit policy + tests. |

### 3.3 MalAbs semantic — default-on and failure policy

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 1.3a | Semantic tier **default-on** where product policy requires it; **no** “LLM down → lexical bypass” without an explicit degraded mode. | `semantic_chat_gate.py`, `absolute_evil.py`, env policy | [ADR 0003](../adr/0003-optional-semantic-chat-gate.md) semantics updated if defaults change; adversarial tests expanded. |
| 1.3b | Regression suite for paraphrase, encoding, and obfuscation classes aligned with [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md). | `tests/`, `absolute_evil.py` | CI gates on representative suite; ties to Issue **#2**. |

**Phase 1 exit (suggested):** P0 items for **#1** (naming or minimal Bayes), **#2** (input trust), and buffer/MalAbs policies have **written acceptance** and tests where claims are strong.

---

## 4. Phase 2 — Reliable perception (~2–3 weeks)

**Goal:** distinguish absence vs. malformation vs. validity-with-inconsistency; raise **epistemic** pressure on the critical path when appropriate.

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 2.1 | State machine: **missing JSON** vs. **malformed JSON** vs. **valid JSON**; only the first may take neutral defaults without epistemic flags. | `perception_schema.py`, `llm_layer.py` | Tests per class; ties to Issue **#2** perception leg. |
| 2.2 | Wire **epistemic dissonance** into the perception/decision path where inconsistent numeric signals suggest spoofing or unreliable perception (not “world truth”). | `epistemic_dissonance.py`, kernel/chat pipeline | Integration tests: inconsistent signals increase dissonance / uncertainty per policy. |
| 2.3 | **Coherence checks:** e.g. calm vs. hostility inconsistency flagged (heuristic, documented). | `perception_cross_check.py` (if applicable), schema | Documented thresholds; no claim of omniscience. |

---

## 5. Phase 3 — Empirical calibration (~4–6 weeks)

**Goal:** evidence for weights and thresholds — **process**, not only more JSON rows.

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 3.1 | Expand pilot: **50–100** scenarios with human reference actions / labels, edge cases, cross-principle conflicts; schema `{scenario, human_ref_A, human_ref_B, cultural_context}`. | [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md), fixtures | Inter-annotator guidelines; reproducible runner; ties to Issue **#3**. |
| 3.2 | Calibrate `pole_linear_default.json` (or successor) from pilot data via **documented** method (e.g. logistic / agreement optimization) with **held-out** evaluation. | `pole_linear_default.json`, analysis scripts | Report + regression bounds; no silent retuning without changelog. |

---

## 6. Phase 4 — Modular architecture (~3–4 weeks)

**Goal:** lower cost of swapping implementations and testing in isolation — **without** empty abstraction.

| Item | Action | Key files | Definition of done |
|------|--------|-----------|-------------------|
| 4.1 | Optional `EthicalModule`-style interface **only** where it reduces coupling (e.g. Bayesian engine strategies). | New `src/modules/` base or protocols | At least one module migrated + kernel DI path tested; ties to Issue **#4** packaging boundary. |
| 4.2 | Consolidate `KERNEL_*` into **typed config** (Pydantic) by family, building on `runtime_profiles.py` and [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md). | `chat_settings.py`, `runtime_profiles.py`, [validators](../../src/validators/env_policy.py) | Single schema per process class; Issue **#7** advanced. |

---

## 7. Phase 5 — Verifiable governance (long-term; post-MVP)

**Goal:** MockDAO → **durable, inspectable** governance records — **without** claiming distributed consensus unless product defines identity and threat model.

| Layer | Requirement | Notes |
|-------|-------------|--------|
| **Persistence** | Votes and outcomes **outside process RAM** (append-only log, versioned table, or checkpoint-linked artifact). | Reuse patterns from `checkpoint.py` / audit concepts. |
| **Quorum** | **Explicit rules** (participation, majorities, windows). If identity is weak, label quorum as **simulated/lab**. | Honest UX/docs ([Issue #6](CRITIQUE_ROADMAP_ISSUES.md)). |
| **Linkage** | Hash or snapshot reference of **kernel-relevant state** at vote time in the audit trail. | Reproducibility for an **operator**, not global BFT. |

**Definition of done:** an auditor can answer: *what was voted, when, under which recorded kernel/snapshot fingerprint, and is the chain intact?*  
**Non-goal (unless product demands it):** blockchain or global Sybil-resistant consensus.

---

## 8. Priority summary (execution order)

| Priority | Theme | Impact | Typical GitHub mapping |
|----------|-------|--------|-------------------------|
| Critical | MalAbs semantic policy + no silent bypass | Hard veto integrity | Issue **#2** |
| Critical | Buffer / semantic verification path | Principle integrity | Issue **#2**, buffer ADR/tests |
| Critical | Perception fail-safe + epistemic integration | Adversarial robustness | Issue **#2** |
| High | Bayesian engine honesty + separable frames | Theoretical validity | Issue **#1** |
| High | Expanded empirical pilot + calibration | Evidence-backed weights | Issue **#3** |
| Medium | Module interfaces + DI | Maintainability / research | Issue **#4** |
| Medium | `KERNEL_*` → typed profiles | Operational maintainability | Issue **#7** |
| Long-term | Durable verifiable governance records | Governance honesty | Issue **#6** |

---

## 9. Traceability

| This proposal | GitHub critique issues |
|---------------|-------------------------|
| §3.1 | #1 |
| §3.2–3.3, §4 Phase 2 | #2 |
| §5 | #3 |
| §6 | #4, #7 |
| §7 | #6 |
| §4.2 / env consolidation | #7 |

---

## 10. Explicit non-goals (unless scope changes)

- Replacing MockDAO with **on-chain** governance without a separate product/security decision.
- Promising **distributed consensus** while votes are in-memory and identities are unspecified.
- “Full Bayesian brain” as marketing without tests that match claims.

---

*MoSex Macchina Lab — structured backlog for core vs. governance tracks.*
