# ADR 0014 — Offline-first kernel profile

**Status:** Accepted  
**Date:** 2026-04-13  
**Supersedes:** —  
**Related:** [ADR 0012](0012-bayesian-weight-inference-ethical-mixture-scorer.md) (Bayesian weights), [ADR 0013](0013-hierarchical-context-weight-inference.md) (hierarchical updater), [`docs/CONTRIBUTING.md`](../CONTRIBUTING.md)

---

## Context

The Ethos Kernel was designed to work with or without an external LLM backend.  The
`LLMModule` supports three modes:

- `local` — heuristic string templates (no API call, no network).
- `ollama` — local Ollama server (requires running daemon, no cloud).
- `anthropic` / `auto` with key — Anthropic API (cloud).

However, the boundary between "what works offline" and "what requires a backend" was
never formally documented.  As the Bayesian inference stack grew (ADR 0012, ADR 0013),
it became important to clarify that **the entire ethical inference pipeline is offline-
capable** while **only the natural-language layer degrades** without a model.

Additionally, OOS-005 noted the absence of a systematic integration test verifying the
Bayesian + scoring stack end-to-end under `LLM_MODE=local`.

---

## Decision

### Offline capability taxonomy

| Subsystem | Offline capable | Degradation when no LLM |
|-----------|-----------------|-------------------------|
| Ethical mixture scorer (`WeightedEthicsScorer`) | ✅ fully offline | — |
| Absolute evil / MalAbs check | ✅ fully offline | — |
| Ethical poles pre-argmax | ✅ fully offline | — |
| Context richness pre-argmax | ✅ fully offline | — |
| BMA win probabilities (ADR 0012 Level 1) | ✅ fully offline | — |
| Feedback posterior (ADR 0012 Level 2) | ✅ fully offline (numpy) | — |
| Context-dependent posterior (ADR 0012 Level 3) | ✅ fully offline (numpy) | — |
| Hierarchical updater (ADR 0013) | ✅ fully offline (Python stdlib + numpy) | — |
| Consequence projection | ✅ fully offline | — |
| Deontic gate | ✅ fully offline | — |
| Perception — LLM JSON path | ❌ requires LLM | Falls back to heuristic signal extraction |
| Perception — heuristic path (`local` mode) | ✅ fully offline | Coarser signals; no coercion report |
| Narrative / communication | ❌ requires LLM | Uses string templates (`local` mode) |
| Semantic chat gate (embedding path) | ❌ requires embedding backend | Falls back to hash/lexical match |
| Semantic embedding client | ❌ requires Ollama or API | Graceful `None` return |

### Offline kernel profile definition

An **offline-capable kernel run** is one where:

1. `LLM_MODE=local` (or no LLM configured) — heuristic perception + template narrative.
2. `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=1` — hash-based semantic MalAbs fallback active.
3. No external network calls are made.

Under this profile:
- Every `EthicalKernel.process()` call **completes and returns a `KernelDecision`**.
- The Bayesian / mixture / poles pipeline is **fully functional**.
- The `final_action` is determined by the ethical scorer, not the LLM.
- The `verbal_response` is a template string, not LLM-generated prose.
- MalAbs still fires on hard-coded patterns (lexical + hash fallback).

### Invariants (contractual)

The following must remain true regardless of LLM availability:

1. `EthicalKernel.process()` never raises when `LLM_MODE=local`.
2. `KernelDecision.final_action` is always populated (not `None` or empty).
3. `KernelDecision.blocked` is correctly set by the MalAbs / deontic gate.
4. `mixture_posterior_alpha` is populated when `KERNEL_BAYESIAN_FEEDBACK` or
   `KERNEL_HIERARCHICAL_FEEDBACK` is active.
5. The `HierarchicalUpdater` cache (`_hier_updater_cache`) is populated after the first
   tick and reused across subsequent ticks without network I/O.

---

## Implementation

- No new code required for the offline profile itself — the capability already exists.
- The **integration test** (`tests/test_kernel_offline_bayesian_integration.py`) verifies
  the full offline Bayesian pipeline end-to-end.
- `docs/CONTRIBUTING.md` links to this ADR as the authoritative offline capability reference.
- `.env.example` already documents `LLM_MODE=local` as the default.

---

## Consequences

### Positive

- Operators running in air-gapped or resource-constrained environments have a clear
  contract: install Python + numpy, set `LLM_MODE=local`, and the ethical kernel works.
- The Bayesian weight inference stack (ADR 0012–0013) is fully accessible offline,
  enabling reproducible ethical research without cloud dependencies.
- The integration test serves as a regression gate: any future change that breaks the
  offline profile will be caught in CI.

### Negative

- Offline perception is coarser — heuristic signal extraction misses nuance that the LLM
  path captures (tone, intent inference, coercion detection).
- Template narrative is less natural than LLM prose; suitable for audit/logging but not
  for user-facing conversation.

### Neutral

- `LLM_MODE=local` is already the `.env.example` default, so this ADR formalises
  existing practice rather than introducing new behaviour.

---

## Related

- [`tests/test_kernel_offline_bayesian_integration.py`](../../tests/test_kernel_offline_bayesian_integration.py)
- [`docs/OUT_OF_SPEC.md`](../OUT_OF_SPEC.md) — OOS-005 (resolved by this ADR)
- [ADR 0012](0012-bayesian-weight-inference-ethical-mixture-scorer.md)
- [ADR 0013](0013-hierarchical-context-weight-inference.md)

---

*Ethos Kernel — ADR 0014, April 2026.*
