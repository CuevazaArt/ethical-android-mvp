# Out-of-spec situations register

This file is the **canonical place** to log known architectural gaps, violated
invariants, heuristic compromises, and deferred design decisions.  It is
updated whenever a contributor detects a situation that does not conform to
the system's stated design — whether or not a fix is immediately planned.

Each entry has:
- **ID** — sequential, never reassigned.
- **Status** — `open` | `mitigated` | `resolved` | `accepted` (accepted = known trade-off, no fix planned).
- **Severity** — `high` | `medium` | `low` | `informational`.
- **ADR reference** — when the situation is connected to an existing ADR.

---

## OOS-001 — τ blending in HierarchicalUpdater is heuristic, not fully Bayesian

**Status:** accepted  
**Severity:** informational  
**ADR:** [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13  

**Description:** The per-context/global blend fraction `τ(n) = τ_max · (1 - exp(-n/3))`
is an engineering heuristic.  A formal hierarchical Dirichlet process (HDP) would derive
the blend weight from the data, not from a fixed exponential schedule.  The heuristic is
deliberate (see ADR 0013 Consequences > Negative), but it means the system cannot claim
full probabilistic coherence at the hierarchical level.

**Resolution path:** If calibration data shows systematic bias, replace the τ schedule
with a proper HDP or empirical-Bayes estimate of the mixing weight.  Currently out of
scope; the heuristic gives qualitatively correct behaviour for the scenarios tested.

---

## OOS-002 — HierarchicalUpdater only supports explicit-triples path at kernel-tick time

**Status:** open  
**Severity:** medium  
**ADR:** [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13  

**Description:** The `KERNEL_HIERARCHICAL_FEEDBACK` kernel integration uses
`build_scenario_candidates_map`, which returns `None` when any referenced scenario lacks
`hypothesis_override` on all candidates.  In that case the hierarchical block silently
does nothing (falls through to the pre-existing weight).  This means hierarchical
context-dependent learning is **unavailable for mixture-ranking scenarios** (those without
explicit triples, e.g. scenarios 1–16).

**Workaround:** Use `KERNEL_BAYESIAN_FEEDBACK` + `KERNEL_BAYESIAN_CONTEXT_LEVEL3` for
mixture-ranking scenarios (ADR 0012 Level 3 path).

**Resolution path:** Implement a `HierarchicalUpdater` variant that wraps
`feedback_mixture_posterior.sequential_alpha_update` (the numpy + mixture_ranking path)
for scenarios without `hypothesis_override`.  Track as future ADR 0014 or extension of
ADR 0013.

---

## OOS-003 — HierarchicalUpdater reloads feedback from scratch on every kernel tick

**Status:** open  
**Severity:** medium  
**ADR:** [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13  

**Description:** The current kernel integration builds a fresh `HierarchicalUpdater` and
calls `ingest_feedback` on every `EthicalKernel.process()` call.  This means the
hierarchical posterior is **recomputed from scratch on every tick**, which is correct for
reproducibility but wasteful for production.

**Resolution path:** Cache the `HierarchicalUpdater` instance on `EthicalKernel` and
invalidate when the feedback file changes (mtime or content hash).  This requires a
lightweight file-change watcher or explicit `reload_feedback()` API.

---

## OOS-004 — ADR 0012 Level 3 (feedback_mixture_posterior) and ADR 0013 are not unified

**Status:** open  
**Severity:** low  
**ADR:** [0012](adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md), [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13  

**Description:** Two independent per-context mechanisms exist:
1. ADR 0012 Level 3 (`KERNEL_BAYESIAN_CONTEXT_LEVEL3`) — numpy + mixture_ranking path,
   per-context sequential α updates, bucket classifier.
2. ADR 0013 (`KERNEL_HIERARCHICAL_FEEDBACK`) — explicit-triples path, τ-blended
   global+local posteriors, canonical context taxonomy.

They can be enabled simultaneously (neither blocks the other) but may interfere —
the last one to run overwrites `self.bayesian.hypothesis_weights`.  There is no
defined priority rule.

**Resolution path:** Define a clear precedence order in `kernel.py` and document it in a
single ADR that supersedes both per-context mechanisms.  Proposed priority:
`KERNEL_HIERARCHICAL_FEEDBACK` > `KERNEL_BAYESIAN_CONTEXT_LEVEL3` > `KERNEL_BAYESIAN_FEEDBACK`.
Add a warning when both are enabled simultaneously.

---

## OOS-005 — Offline mode has no formal ADR

**Status:** open  
**Severity:** low  
**ADR:** none  
**Detected:** 2026-04-13  

**Description:** The `LLMModule` has a `"local"` mode that uses heuristic string templates
when no API key or Ollama endpoint is available.  This mode is the de-facto offline path
for the ethical inference stack.  However:
- There is no ADR documenting the decision and its constraints.
- `LLM_MODE=local` is not systematically tested for all perception/narrative paths.
- The interaction between offline mode and Bayesian weight inference (which is fully
  offline / numpy-only) is not documented.

**Resolution path:** Create ADR 0014 — "Offline-first kernel profile: local LLM mode and
pure-Python inference stack".  Document which kernel features are available in offline
mode, which degrade gracefully, and which require an LLM backend.  Add at least one
integration test that verifies the Bayesian + ethical scoring stack works end-to-end
with `LLM_MODE=local`.

---

## OOS-006 — RECORD_SCHEMA_VERSION bump (5 → 6) not backwards-compatible for consumers reading old JSONL

**Status:** accepted  
**Severity:** informational  
**ADR:** [0012](adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)  
**Detected:** 2026-04-13  

**Description:** JSONL files produced before schema v6 do not contain `bma_*` fields.
Consumers that expect these fields will receive `None` / `KeyError`.  This is a
forward-only schema change.

**Resolution path:** Document in `experiments/README.md` that older JSONL files are v5
and lack BMA columns.  Add a migration note to the changelog.  Accepted as intentional —
old experiment runs are archived in `experiments/out/` and do not need re-processing.

---

## OOS-007 — LOO calibration script (run_likelihood_calibration.py) requires explicit-triples scenarios

**Status:** open  
**Severity:** low  
**ADR:** [0012](adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md)  
**Detected:** 2026-04-13  

**Description:** `scripts/run_likelihood_calibration.py` uses
`build_scenario_candidates_map` and will exit with an error message for feedback files
that reference scenarios without `hypothesis_override` (i.e. any scenario not in
scenarios 17–19 or similar explicit-triple sets).  This limits usability for operators
who want to calibrate on real-world feedback against arbitrary scenarios.

**Resolution path:** Add a `--mixture-ranking` flag to the LOO script that falls back to
the `mixture_ranking` path (numpy + full scorer) when explicit triples are unavailable,
with a warning about the performance cost.

---

*Last updated: 2026-04-13 — Ethos Kernel contributors.*
