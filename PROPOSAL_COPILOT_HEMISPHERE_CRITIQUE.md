# PROPOSAL_COPILOT_HEMISPHERE_CRITIQUE

**From:** Team Copilot (Level 2 — GitHub Engine)  
**In response to:** [`COPILOT_REQUEST_HEMISPHERE_REFACTOR.md`](COPILOT_REQUEST_HEMISPHERE_REFACTOR.md)  
**Reference context:** [`PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md`](PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md), [`PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md`](PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md)

---

## Executive Position

The tri-lobe refactor is architecturally sound and operationally necessary. The current synchronous
`httpx` usage inside worker threads creates observable symptoms (worker pool exhaustion, absent
cooperative-cancellation paths) that justify the migration cost.

The critical risk is not the decomposition itself but the **consistency of shared state across
cancellation boundaries**. The scaffolding already merged in
`src/kernel_lobes/` is a valid Fase 4 starting point; this critique identifies the outstanding
trade-offs and recommends guard-rails before broad feature expansion.

---

## 1) Impact on Existing Tests — Recommended: Compatibility Facade First

**Question from L1:** *Is a synchronous facade on the Corpus Callosum needed to preserve existing
tests, or is a "clean break" rewrite preferable?*

**Team Copilot position:**

A **compatibility facade is the lower-risk path**, at least until the v2 test suite reaches ≥ 25%
coverage of the new lobe contracts (the directive from `PLAN_WORK_DISTRIBUTION_TREE.md` §Bloque 0.2).

Rationale:

| Option | Risk | Recovery cost |
|--------|------|---------------|
| Clean break: rewrite all tests to new lobe API | Breaks CI in one shot; blocks other teams' work | High; every consumer must adapt simultaneously |
| Facade on `CorpusCallosumOrchestrator.sync_process()` | Existing `EthicalKernel`-based tests remain green | Low; facade can be deprecated gradually after new tests land |

Concrete recommendation:

- Add a `sync_process(raw_input, ...)` shim on `CorpusCallosumOrchestrator` that wraps `asyncio.run(self.async_process(...))` so callers that cannot use `await` (e.g., legacy integration tests) continue to work without modification.
- Mark the shim `# deprecated: use async_process` to signal intent.
- Do **not** propagate the facade into production call-sites; only tests and transitional scripts should use it.

---

## 2) Circular Reference Strategy for Shared Session State

**Question from L1:** *What is the best Python strategy to instantiate interdependent lobes that
share session state (e.g., `NarrativeMemory`) without creating mutual async locks?*

**Team Copilot position:**

Use a **single shared context object injected at construction time**, not circular references.

Pattern:

```python
@dataclass
class TurnContext:
    narrative: NarrativeMemory
    session_id: str
    turn_id: str
    governance_snapshot: dict  # immutable for this turn (see Claude critique §1)
```

Each lobe receives `TurnContext` as a parameter to its processing call, **not** as a stored
attribute:

```python
semantic_state = await perceptive_lobe.observe(raw_input, ctx)
ethical_sentence = await asyncio.to_thread(limbic_lobe.judge, semantic_state, ctx)
output = await asyncio.to_thread(executive_lobe.formulate_response, semantic_state, ethical_sentence, ctx)
```

Why this avoids both circular references and async locks:

1. No lobe holds a reference to another lobe → no circular dependency graph.
2. `TurnContext` is constructed **once per turn** by `CorpusCallosumOrchestrator.async_process` and
   passed down; lobes only write to it **after** the ethical gate clears (aligned with Claude's
   commit-gate recommendation).
3. `NarrativeMemory` writes can be wrapped in `asyncio.to_thread` since they are sync-safe; no
   `asyncio.Lock` needed unless a future version introduces true concurrent turns.

---

## 3) Maintainability Assessment — Verdict: Acceptable with Bounded Lobe Count

**Question from L1:** *Does the tri-lobe split introduce too much cognitive complexity for junior
developers?*

**Team Copilot position:**

The split is **not excessive** provided the number of first-level lobes is frozen at three
(Perceptive / Limbic / Executive) plus the Cerebellum daemon — exactly the count that
`PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md` recommends.

Observable risks to maintainability and mitigations:

| Risk | Mitigation |
|------|------------|
| Developers add a fourth conscious lobe "for clarity" | Document the lobe-count ceiling in `src/kernel_lobes/README.md` and enforce via PR checklist |
| `CorpusCallosumOrchestrator` grows into a God Object | Keep it under 120 lines; delegate all business logic to lobes |
| `TurnContext` grows unbounded | Define a `TurnContext` dataclass with a fixed, documented field set; additional fields require ADR |
| New contributors bypass `async_process` and write to `NarrativeMemory` directly | Add a lint comment / docstring convention: "lobe methods must not mutate durable state unless invoked through the Orchestrator" |

Cognitive-load judgement: three lobes with clear single-responsibility names are **easier** for
junior developers than the current monolith `EthicalKernel` with 3600+ lines. The migration
complexity is front-loaded during refactoring, not ongoing.

---

## 4) Additional Gap: Import Hygiene in `kernel.py`

During this review, Team Copilot identified and resolved a structural import defect introduced when
`CorpusCallosumOrchestrator` was first scaffolded inside `kernel.py`:

- The class was inserted **between** two separate import blocks, causing ~20 Ruff E402/F811 errors
  (module-level imports after a class definition).
- The class has been relocated to its correct position (after all imports, before `EthicalKernel`).
- The `_log`/`if TYPE_CHECKING` statement was also moved after all imports, eliminating all
  cascading E402 violations.
- Unused and duplicate import symbols exposed by the fix have been removed.

Net result: `kernel.py` now passes ruff with only 2 pre-existing, unrelated errors (E701, F541 in
`EthicalKernel` body — not in scope for this refactor).

---

## 5) Acceptance Criteria (Copilot-Specific, Complementary to Claude §Acceptance Criteria)

These extend Claude's five criteria without duplicating them:

1. `CorpusCallosumOrchestrator` provides a `sync_process()` compatibility shim until the 25%-test
   target is met.
2. `TurnContext` dataclass is introduced and documented before `NarrativeMemory` is wired into the
   lobe pipeline.
3. `src/kernel_lobes/` lobe count remains ≤ 3 conscious lobes + 1 cerebellum; additions require an
   ADR and L1 approval.
4. `kernel.py` import section remains lint-clean (ruff E402/F811 = 0) after any future scaffolding.

---

## Related Documents

- [`COPILOT_REQUEST_HEMISPHERE_REFACTOR.md`](COPILOT_REQUEST_HEMISPHERE_REFACTOR.md)
- [`PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md`](PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md)
- [`PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md`](PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md)
- [`PROPOSAL_TRI_LOBE_ARCHITECTURE.md`](docs/proposals/PROPOSAL_TRI_LOBE_ARCHITECTURE.md)
- [`docs/proposals/COPILOT_REQUEST_IDLE_SHIFT.md`](docs/proposals/COPILOT_REQUEST_IDLE_SHIFT.md)

---

## Changelog

- **2026-04-17:** Initial critique; covers test-facade strategy, shared-state injection pattern,
  maintainability bound, and import hygiene repair (kernel.py).
