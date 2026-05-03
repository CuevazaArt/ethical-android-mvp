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

## 5. Modality Extension Point (PENDING_HARDWARE)

`CharterEvaluator.evaluate()` now accepts `modality: str = "text"`.
When the Sony A5100/A6000 camera and microphone arrive, the voice and vision
pipelines will pass `modality="voice"` or `modality="vision"` to enable
stricter veto thresholds for non-text inputs (which are harder to sanitize).

No differentiated logic is implemented yet.  The parameter is present solely
to avoid a breaking API change when hardware support lands.

---

## 6. Copyright Note

All corpus entries are **original paraphrases** of the cited sources.
No verbatim text from Rawls, Aristotle, Beauchamp & Childress, Kant, or any
other copyrighted work appears in any file.  Only the author name and a
short section reference are included as attribution.
