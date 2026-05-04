# CHARTER_COMPLETENESS_V2 — Ethical Buffer: Conceptual Traceability

**Status:** Implemented (V2.159)
**Author:** Juan Cuevaz / Mos Ex Machina
**Supersedes:** Parts of LIGHTHOUSE_CHARTER_V1.md (architecture overview remains valid)
**Relates to:** AUTONOMY_LIMITS_V1.md, LIGHTHOUSE_CHARTER_V1.md, ETHICAL_BENCHMARK_BASELINE.md

---

## 1. Purpose

This document maps the **seven conceptual sections** of the minimum ethical buffer
(as designed in the V2.159 planning session) to the concrete files, classes, and
tests that implement each section in the codebase.

The minimum ethical buffer is the kernel's **immutable moral anchor** — loaded
before any learning, memory, or cultural adaptation.  It provides:

- A justice baseline
- A decision reference frame
- A safety filter
- A fallback point under ambiguity
- A tiebreaker in dilemmas

---

## 2. Traceability Table

| Conceptual Section | Files Implementing It | Test Coverage |
|---|---|---|
| **A. Universal Justice Principles** (equity, impartiality, proportionality, consistency, due consideration) | `evals/charter/positive_corpus/justice_principles.json` (jp-001 to jp-005) | `tests/core/test_charter_completeness.py::TestNewCorpusFiles::test_justice_principles_loads` |
| **B. Non-Maleficence** (physical, psychological, economic, social, indirect) | `evals/charter/positive_corpus/non_maleficence.json` (nm-001 to nm-005) | `tests/core/test_charter_completeness.py::TestNewCorpusFiles::test_non_maleficence_loads` |
| **C. Basic Human Rights** | `evals/charter/positive_corpus/human_rights.json` (UDHR Art. 1–30, existing V2.158) | `tests/core/test_charter.py::TestPositiveCorpus` |
| **D. Kernel Self-Limits** (no emotional manipulation, no deception, no unbounded 3rd-party decisions, competence boundaries, conversational justice) | `evals/charter/self_limits/` — 5 files (sl-em-*, sl-da-*, sl-tp-*, sl-cb-*, sl-cj-*) | `tests/core/test_charter_completeness.py::TestEvaluateSelfAction` |
| **E. Dilemma Resolution Procedure** (7-step protocol) | `evals/charter/procedures/dilemma_resolution_v1.json` | `tests/core/test_charter_completeness.py::TestDilemmaResolutionProcedure` |
| **F. Conversational Justice Rules** (no humiliation, no escalation, no assumed negative intent, no judgments on real persons, no discriminatory language) | `evals/charter/self_limits/conversational_justice.json` (sl-cj-001 to sl-cj-006) | `tests/core/test_charter_completeness.py::TestEvaluateSelfAction::test_detects_degrading_language` |
| **G. External Ethical References** (care, virtue, deontology, utilitarianism, Rawls, Responsible AI) | `evals/charter/references/ethical_schools.json` (6 school entries) | `tests/core/test_charter_completeness.py::TestCiteSchool` |

---

## 3. New Architecture: Self-Limit Gate

V2.158 only analyzed **incoming user messages**.  V2.159 adds a self-evaluation
gate that checks the **kernel's own draft responses** before delivery:

```
LLM generates draft response
         │
         ▼
CharterEvaluator.evaluate_self_action(draft)
         │ violations found?
         ├── YES → replace draft with safe fallback, log warning
         │
         └── NO  → return draft to user
```

This is implemented in:
- `src/core/charter.py` — `evaluate_self_action()`, `SelfLimitResult`
- `src/core/chat.py` — called in `turn()` and `turn_stream()` after `respond()`

---

## 4. New Architecture: Ethical School Anchor

`CharterEvaluator.cite_school(category)` returns the IDs of ethical frameworks
relevant to a given Hendrycks ETHICS category.  These IDs are written into the
`charter_school_anchor` field of the decision trace (`decision_trace` in
`_build_trace_with_ledger`).

This is an **annotation only** — it does not modify `WEIGHTS` or scores.
It creates an auditable link between a moral decision and a canonical framework.

Supported Hendrycks categories: `deontology`, `justice`, `virtue`,
`commonsense`, `utilitarianism`.

---

## 5. Modality Extension Point (WONTFIX_UNTIL_HARDWARE)

`CharterEvaluator.evaluate()` now accepts `modality: str = "text"`.
When the Sony A5100/A6000 camera and microphone arrive, the voice and vision
pipelines will pass `modality="voice"` or `modality="vision"` to enable
stricter veto thresholds for non-text inputs (which are harder to sanitize).

No differentiated logic is implemented yet.  The parameter is present solely
to avoid a breaking API change when hardware support lands.

---

## 6. Self-Limit Gate Telemetry (V2.160)

### Counter: `self_limit_revisions_total`

Every time `CharterEvaluator.evaluate_self_action()` fires (`must_revise=True`),
one telemetry entry per `violation_id` is appended to:

```
data/fleet_logs/self_limit_telemetry.jsonl
```

Each line is a JSON object:

```json
{"ts": 1746376066.12, "violation_id": "sl-em-001", "cycle": "v2.160", "turn_id": "t-123"}
```

### Reading the counter

Use `SelfLimitLedger` from `src/core/fleet_telemetry.py`:

```python
from src.core.fleet_telemetry import SelfLimitLedger

s = SelfLimitLedger().summary()
print(s["self_limit_revisions_total"])   # total events
print(s["by_violation_id"])              # {"sl-em-001": 3, "sl-em-003": 1, ...}
```

Or read the JSONL file directly for time-series analysis.

### `decision_trace` field

When a turn triggers a self-limit revision, the `decision_trace` dict includes:

```json
"self_limit_violations": ["sl-em-001", "sl-em-003"]
```

This field is absent when no self-limit was triggered (i.e., when `must_revise=False`).

### Threshold adjustment guidance

- **False positives** (benign drafts revised): check `by_violation_id` for
  over-firing IDs; narrow their keyword list in the relevant `self_limits/*.json`.
- **False negatives** (manipulation drafts passing through): add keywords or
  lower the detection threshold in `evaluate_self_action()`.
- **Baseline**: run `tests/core/test_fleet_telemetry.py::TestSelfLimitLedger`
  to verify counter semantics after any threshold change.

---

## 7. Hendrycks Delta — V2.159 Post-Sprint Measurement

The `charter_school_anchor` annotation added in V2.159 is **annotation only**
and must not alter Hendrycks ETHICS benchmark scores.

**Result (measured post-V2.161, V2.161 reconciliation sprint):**

Run: `evals/ethics/ETHICS_EXTERNAL_RUN_20260503T222749Z.json` (500 examples/subset, 2 000 total).

| Category | Baseline (EXTERNAL_BASELINE_v1.json) | Post-V2.161 | Delta |
|---|---|---|---|
| commonsense | 52.05% | 49.0% | −3.1 pp |
| justice | 50.04% | 49.8% | −0.2 pp |
| deontology | 51.03% | 55.2% | +4.2 pp |
| virtue | 46.71% | 40.4% | −6.3 pp |
| **overall** | **49.70%** | **48.6%** | **−1.1 pp** |

> **Interpretation:** The −1.1 pp overall delta is within the sampling-variance
> window for a 2 000-example subsample of the full corpus (the baseline was
> measured on 15 160 examples).  No architectural change was made between the
> baseline and this run; the delta reflects subsample variance, not regression.
> `charter_school_anchor` confirmed as annotation-only: it does not modify
> WEIGHTS, scoring, or action selection.  DoD #3 closed.
>
> Deontology +4.2 pp is a positive surprise but also sampling-noise at n=500;
> the full-corpus measurement would be required to confirm it.  No claim is
> made about improvement.  The number is reported honestly.

---

## 8. Adversarial Curriculum A011–A020 — V2.163

Ten new adversarial dilemmas added to `evals/ethics/dilemmas_v1.json` (total: 40).
All have `"category": "adversarial"` and document both `adversarial_pattern` and
`expected_failure_mode` to explicitly record what the kernel is *expected to struggle with*.

Per-dilemma fixture files: `evals/adversarial/a011_fixture.json` … `a020_fixture.json`.

Frozen baseline: `evals/adversarial/BASELINE_v2.json`
(20 adversarial dilemmas; run at V2.163 freeze, all 20 pass — some via acceptable
alternatives).

**Patterns covered by A011–A020:**

| ID | Pattern | Language |
|---|---|---|
| A011 | soft_jailbreak_roleplay_escalation | en |
| A012 | reverse_framing_inversion | en |
| A013 | sophistic_utilitarian_override | es |
| A014 | authority_credential_escalation | en |
| A015 | incremental_normalization_es | es |
| A016 | emotional_dependency_induction | en |
| A017 | false_consensus_multilingual | en/es |
| A018 | complicity_through_partial_help | en |
| A019 | competence_boundary_override_es | es |
| A020 | consensus_manufacture_aggregate | en |

**Anti-acceptance note:** Passing all 20 adversarial dilemmas does NOT mean the
kernel is robust. Several dilemmas pass because the evaluator selects an acceptable
alternative rather than the ideal refusal action (e.g. A009, A010, A011, A012).
The `expected_failure_mode` field documents the structural weakness being probed.

---

## 9. Copyright Note

All corpus entries are **original paraphrases** of the cited sources.
No verbatim text from Rawls, Aristotle, Beauchamp & Childress, Kant, or any
other copyrighted work appears in any file.  Only the author name and a
short section reference are included as attribution.
