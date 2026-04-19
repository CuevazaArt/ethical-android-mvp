# Module impact and empirical gap (complexity vs observable ethics)

**Audience:** reviewers asking whether ~70 `src/modules` files are justified for a pipeline whose **chosen action name** is ultimately an argmax over MalAbs-survivors in `BayesianEngine`, then **mode** fusion (`SigmoidWill`, sympathetic state, locus, Uchi–Soto, optional perception-uncertainty nudge).

**Honest answer today:** the repository does **not** yet publish a large-scale **ablation study** (“disable 20 exotic modules → measure Δ in human-judged decision quality”). That is **evidence debt**, not a claim that every module is essential.

This document: (1) states what **can** and **cannot** change `KernelDecision.final_action` in `process()`, (2) classifies peripheral modules, (3) ties the gap to the empirical pilot (Issue **#3**).

---

## 1. What actually sets `final_action`?

In `EthicalKernel.process` ([`kernel.py`](../../src/kernel.py)), after MalAbs pruning:

- **`final_action`** is **`bayes_result.chosen_action.name`** (scalar choice path).
- **`EthicalPoles.evaluate`** runs on the **already chosen** name — it updates multipolar **verdicts** for audit/LLM context; it does **not** pick a different candidate action.
- **`WeaknessPole`, `NarrativeMemory.register`, `Forgiveness`, `MockDAO` audit** run **after** `final_action` is fixed (when `register_episode` is true).

So: **many modules are intentionally not on the action-id path.** They affect **narrative**, **telemetry**, **LLM tone**, **memory**, **governance demos**, or **deliberation mode** — not a second argmax over actions.

**`final_mode`** (e.g. `gray_zone`, `D_fast`, `D_delib`) **is** influenced by sympathetic state, will, locus, Uchi–Soto, Bayesian `decision_mode`, and optional perception-uncertainty escalation. That is **observable** in `KernelDecision` but is **not** the same as swapping the action string.

---

## 2. Tiered map (conceptual → policy)

| Tier | Role | Examples | Changes `final_action` name? | Typical tests today |
|------|------|----------|-------------------------------|----------------------|
| **A — Veto / choice** | Drop or rank candidates | MalAbs, `PreloadedBuffer.activate`, `BayesianEngine.evaluate` | **Yes** (MalAbs prune; Bayes argmax) | Properties, scenario tests |
| **B — Mode only** | Deliberation style, not action id | `SigmoidWill`, sympathetic, locus, Uchi–Soto, optional `KERNEL_PERCEPTION_UNCERTAINTY_*` | **No** (name still from Bayes) | Some integration tests |
| **C — Post-choice narrative** | Memory, weakness line, forgiveness, DAO audit strings | `WeaknessPole`, `NarrativeMemory`, `AlgorithmicForgiveness`, `MockDAO` | **No** | Module unit tests; “runs” |
| **D — Read-only presentation** | Reflection, salience, PAD | `EthicalReflection`, `SalienceMap`, `PADArchetypeEngine` | **No** | Smoke / snapshot |
| **E — Other entry points** | Not every `process()` tick | `execute_sleep` (Psi Sleep, drive arbiter, feedback into Bayes weights **later**), chat-only augenesis / monologue | **Indirect** across ticks or **UX only** | Partial |

**Risk called out by reviewers:** Tier **C/D/E** modules can harbor bugs that **do not change** `final_action` on the scenario under test — so **unit tests that only assert “no exception”** do not prove ethical value.

---

## 3. “Exotic” modules named in critique

| Module | Role in architecture | Why it may look like “theater” |
|--------|---------------------|--------------------------------|
| `subjective_time.py` | Feeds turn index into Uchi–Soto / relational context | Effect on **mode** or social eval may be subtle in default scenarios |
| `weakness_pole.py` | Post-decision emotional load; LLM **communication** hints | Does **not** change `final_action` in `process()` |
| `drive_arbiter.py` | Psi Sleep / drive intents (typically `execute_sleep`) | Off the main `process()` argmax path |
| `psi_sleep.py` | Offline consolidation; can feed **episodic** Bayes nudges **later** | Cross-tick; not proven in pilot yet |
| `augenesis.py` | Narrative / LLM flavoring | Not selecting among `CandidateAction` in core path |

None of the above contradicts the **documented** split in [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md) and [ADR 0001](../adr/0001-packaging-core-boundary.md) (“core policy” vs “humanizing theater”). The open question is **empirical**: do they change **operator-relevant** outcomes (tone, escalation, calibration) enough to justify complexity — **not** whether they change the argmax every time.

---

## 4. What would “resolve” the critique empirically?

1. **Ablation protocol (research)**  
   - Fixed scenario suite + human or panel labels (see [EMPIRICAL_PILOT_PROTOCOL.md](EMPIRICAL_PILOT_PROTOCOL.md), [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md)).  
   - **Arms:** (i) minimal kernel wiring / flags off vs (ii) full stack vs (iii) targeted module groups off (requires feature boundaries or DI — [Issue #4](CRITIQUE_ROADMAP_ISSUES.md), phased remediation §4).  
   - **Metrics:** agreement with reference decisions, not only `final_action` string (mode, justification quality may matter).

2. **Regression invariants (engineering)**  
   - Assert architectural rules: e.g. when not blocked, `final_action == bayesian_result.chosen_action.name` ([`tests/test_decision_core_invariants.py`](../../tests/test_decision_core_invariants.py)).  
   - Prevents accidental “theater” from mutating the action id without a deliberate design change.

3. **Honest docs**  
   - [WEAKNESSES_AND_BOTTLENECKS.md](../WEAKNESSES_AND_BOTTLENECKS.md) — peripheral complexity vs measurement.  
   - This file — traceability for “why so many modules.”  
   - [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md) — **Implementation status** table documents what the repo already runs (`run_empirical_pilot.py` + `labeled_scenarios.json`) vs what would still require a dedicated ablation / panel study.

---

## 5. Positioning (not defensive)

- **Complexity without measurement** is a **valid** criticism of the **research product**, not a personal attack on contributors.  
- The codebase **explicitly** separates core argmax from narrative/governance layers; the missing piece is **published ablation + agreement metrics** (Issue **#3**), not another layer of ad hoc modules.

---

*MoSex Macchina Lab — empirical gap register.*
