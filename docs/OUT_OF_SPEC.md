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

**Status:** mitigated  
**Severity:** medium  
**ADR:** [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13 · **Mitigated:** 2026-04-13  

**Description:** The `KERNEL_HIERARCHICAL_FEEDBACK` kernel integration uses
`build_scenario_candidates_map`, which returns `None` when any referenced scenario lacks
`hypothesis_override` on all candidates.

**Mitigation (2026-04-13):** When `build_scenario_candidates_map` returns `None`, the
kernel now falls back to `load_and_apply_feedback` (mixture_ranking path, same as ADR 0012
Level 3) with the current tick context.  This gives context-dependent semantics for
non-explicit-triples scenarios, albeit via the global Level-3 mechanism rather than the
full hierarchical global+local structure.  A sentinel `"mixture_ranking_fallback"` is
stored in the cache to avoid rebuilding each tick.

**Remaining gap:** The per-context local updater (`HierarchicalUpdater._contexts`) is
not populated for mixture-ranking fallback scenarios; only the global posterior is used
with Level-3 context selection.  Full per-context local posteriors for mixture-ranking
require a deeper refactor (see ADR 0013 extension plan).

---

## OOS-003 — HierarchicalUpdater reloads feedback from scratch on every kernel tick

**Status:** resolved  
**Severity:** medium  
**ADR:** [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13 · **Resolved:** 2026-04-13  

**Description:** The original kernel integration built a fresh `HierarchicalUpdater` on
every `EthicalKernel.process()` call.

**Resolution:** `EthicalKernel` now maintains three cache fields:
`_hier_updater_cache`, `_hier_cache_fb_path`, `_hier_cache_mtime`.  The updater is
rebuilt only when the feedback file path changes or its `st_mtime` differs from the
cached value.  Verified by `test_offline_hierarchical_cache_reuse` (ADR 0014 invariant 5).

---

## OOS-004 — ADR 0012 Level 3 (feedback_mixture_posterior) and ADR 0013 are not unified

**Status:** mitigated  
**Severity:** low  
**ADR:** [0012](adr/0012-bayesian-weight-inference-ethical-mixture-scorer.md), [0013](adr/0013-hierarchical-context-weight-inference.md)  
**Detected:** 2026-04-13 · **Mitigated:** 2026-04-13  

**Description:** Two independent per-context mechanisms existed with no defined priority
when both were enabled simultaneously.

**Mitigation (2026-04-13):** A precedence warning is now emitted at `WARNING` level in
`kernel.py` when `KERNEL_HIERARCHICAL_FEEDBACK` is active alongside
`KERNEL_BAYESIAN_FEEDBACK` or `KERNEL_BAYESIAN_CONTEXT_LEVEL3`.  The canonical precedence
is documented as: **HIERARCHICAL > CONTEXT_LEVEL3 > BAYESIAN_FEEDBACK**.  The warning
message includes `(OOS-004)` for traceability.  Verified by
`test_precedence_warning_logged`.

**Remaining gap:** The two mechanisms are still separate code paths; unification into a
single ADR is deferred (no blocking issue in current usage).

---

## OOS-005 — Offline mode has no formal ADR

**Status:** resolved  
**Severity:** low  
**ADR:** [0014](adr/0014-offline-first-kernel-profile.md)  
**Detected:** 2026-04-13 · **Resolved:** 2026-04-13  

**Description:** No formal ADR documented the offline capability boundary.

**Resolution:** ADR 0014 — "Offline-first kernel profile" — formalises the capability
taxonomy, defines the five contractual invariants, and is backed by
`tests/test_kernel_offline_bayesian_integration.py` (6 tests covering ADR 0014 invariants
1–5, BMA offline, and the OOS-004 precedence warning).

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

---

## Changelog

| Date | ID | Change |
|------|----|--------|
| 2026-04-13 | OOS-001 | Registered (accepted — heuristic τ is deliberate) |
| 2026-04-13 | OOS-002 | Registered open; mitigated same day via mixture_ranking fallback |
| 2026-04-13 | OOS-003 | Registered open; resolved same day via mtime cache |
| 2026-04-13 | OOS-004 | Registered open; mitigated same day via precedence warning |
| 2026-04-13 | OOS-005 | Registered open; resolved same day via ADR 0014 |
| 2026-04-13 | OOS-006 | Registered (accepted — schema migration, not a defect) |
| 2026-04-13 | OOS-007 | Registered open (LOO calibration explicit-triples limitation) |

*Last updated: 2026-04-13 — Ethos Kernel contributors.*
