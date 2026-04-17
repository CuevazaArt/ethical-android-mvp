# Empirical Pilot Module Validation Report — 2026-04-16

**Purpose:** Establish baseline of which architectural modules are **exercised** and **tested** in the current empirical pilot fixture (9 scenarios), and identify gaps for future ablation studies.

**Reference:** [MODULE_IMPACT_AND_EMPIRICAL_GAP.md](proposals/MODULE_IMPACT_AND_EMPIRICAL_GAP.md), [EMPIRICAL_METHODOLOGY.md](proposals/EMPIRICAL_METHODOLOGY.md)

---

## Executive Summary

The empirical pilot baseline (9 scenarios, 100% kernel agreement) establishes a **reference point for module impact measurement**. Current pilot:

- ✅ **Exercises core decision path:** MalAbs → Bayesian engine → final_action selection
- ✅ **Validates decision consistency:** All 9 scenarios converge deterministically (`variability=False`, `seed=42`)
- ⚠️ **Partial coverage of peripheral modules:** Only baseline Tier-A/B modules actively influencing decisions
- ❌ **No explicit ablation:** Module-by-module impact not yet quantified

---

## Core Decision Path — Tier A (Veto / Choice)

**Status:** ✅ **FULLY EXERCISED**

| Module | Role | Empirical Pilot Coverage | Observable Output |
|--------|------|--------------------------|-------------------|
| `absolute_evil.py` (MalAbs) | Lexical veto for blocked categories | ✅ No scenarios violated lexical boundaries | N/A (permissive scenarios) |
| `bayesian_engine.py` | Action selection via weighted mixture | ✅ All 9 scenarios produce `chosen_action.name` | All 9 use Bayesian path |
| `weighted_ethics_scorer.py` | Mixture weights (care, justice, virtue) | ✅ Active in all 9 scenarios | Implicit in Bayesian selection |

**Evidence:** All empirical pilot scenarios complete the core decision flow without exception. Bayesian result is present in all rows (`agree_kernel: true` for 100% of rows).

---

## Mode Modulation — Tier B (Decision Mode, Not Action)

**Status:** ⚠️ **PARTIALLY EXERCISED**

| Module | Role | Empirical Pilot Coverage | Observable Output |
|--------|------|--------------------------|-------------------|
| `sympathetic_state.py` | Emotional context for mode | ✅ Loaded in kernel | Not directly testable in deterministic mode |
| `sigmoid_will.py` | Will state → deliberation intensity | ✅ Loaded in kernel | Affects `decision_mode` (D_fast, D_delib, etc.) |
| `locus_of_control.py` | Agency/fatalism mode modulation | ✅ Loaded in kernel | Affects `decision_mode` field in output |
| `uchi_soto.py` | Relational tier evaluation | ✅ Loaded in kernel | Affects social context, not action id |

**Evidence:** These modules set the `final_mode` field but do not change `final_action` in the pilot. Mode values are captured in empirical output but not yet **validated against human expectations**.

**Gap:** Lack of "ground truth" `final_mode` labels in empirical fixture; only `final_action` is labeled.

---

## Post-Choice Narrative — Tier C (Memory, Governance)

**Status:** ⚠️ **LOADED BUT NOT VALIDATED**

| Module | Role | Empirical Pilot Coverage | Observable Output |
|--------|------|--------------------------|-------------------|
| `narrative.py` | Episode registration | ✅ `register_episode(impact)` called per scenario | Memory digest not checked in pilot |
| `weak_pole.py` | Post-decision emotional audit | ✅ Evaluated per scenario | Verdict strings produced; not validated |
| `algorithmic_forgiveness.py` | Forgetting heuristic | ✅ Optional per scenario context | Effect on narrative trajectory not measured |
| `mock_dao.py` | Governance audit / mock tribunal | ✅ Optional per scenario | Audit ledger written; not validated in pilot |

**Evidence:** All modules execute without exception; outputs are generated but **not** scored against reference ground truth.

**Gap:** Empirical pilot does not capture narrative quality, emotional accuracy, or governance ledger correctness. These are **assumption-based** validations only.

---

## Read-Only Presentation — Tier D (Reflection / Salience)

**Status:** ❌ **NOT VALIDATED IN PILOT**

| Module | Role | Empirical Pilot Coverage | Observable Output |
|--------|------|--------------------------|-------------------|
| `ethical_reflection.py` | Audit summary | Loaded; not checked | Generated but not scored |
| `salience_map.py` | Importance ranking of ethical factors | Loaded; not checked | Map computed; not validated |
| `pad_archetypes.py` | Personality archetype inference | Loaded; not checked | Archetype assigned; not ground-truthed |

**Evidence:** These modules run without error but **no human or reference-based validation** of output quality.

**Gap:** Pilot assumes these are "safe to run" but does not prove they improve human judgment or operator trust.

---

## Off-Path / Cross-Tick — Tier E (Sleep, Drives)

**Status:** ❌ **NOT EXERCISED**

| Module | Role | Empirical Pilot Coverage | Observable Output |
|--------|------|--------------------------|-------------------|
| `psi_sleep.py` | Offline episodic consolidation | Not called in `process()` | N/A in single-tick pilot |
| `drive_arbiter.py` | Long-term drive / autonomy modeling | Not called in `process()` | N/A in single-tick pilot |
| `augenesis.py` | Narrative LLM context injection | Not called in core path | N/A (optional LLM layer) |

**Evidence:** Empirical pilot is **single-turn, stateless** design; cross-tick modules do not apply.

---

## Key Findings

### What the pilot **does** validate

1. **Core argmax is deterministic:** All 9 scenarios produce identical outputs when run with same seed.
2. **Bayesian engine works:** Action selection is consistent and traces through weighted mixture.
3. **No crashes in full stack:** All 70+ modules load and execute without exception.
4. **Mode computation happens:** `final_mode` is populated for all scenarios.

### What the pilot **does not** validate

1. **Human alignment of `final_action`:** Reference labels are ground-truthed to **kernel outputs**, not **human judgment**. The 0→100% agreement transition was a **calibration artifact**, not validation.
2. **Peripheral module value:** Tier B/C/D modules run but their output quality is **unscored**.
3. **Cross-scenario learning:** Pilot is stateless; narrative, DAO ledger, and sleep consolidation effects are **not** measured.
4. **Operator trust / transparency:** No test of whether humans find the explanations, reflections, or modes *credible* or *useful*.

---

## Recommendations for Next Sprint

### High Priority (blocking external validation)

1. **Extend empirical fixture to include human labels**
   - Add `human_reference_mode` field (e.g., `"D_fast"`, `"gray_zone"`)
   - Add `human_rationale_category` (e.g., "safety-primary", "balanced", "autonomy-respecting")
   - Enables measurement of agreement for **mode** and **reasoning quality**, not just action id

2. **Create ablation protocol boundaries**
   - Define feature flags for Tier B/C modules (`KERNEL_NARRATIVE_*`, `KERNEL_GOVERNANCE_*`)
   - Allows A/B test: kernel with vs without peripheral modules
   - Measure Δ operator judgment / confidence on same scenarios

### Medium Priority

3. **Narrative quality scoring**
   - Define rubric for episode registration coherence, forgiveness application, emotional accuracy
   - Run single-blind review of 3 pilot narratives by external raters
   - Document inter-rater agreement and gaps

4. **Cross-tick validation (multi-session pilot)**
   - Extend pilot to 2–5 turn conversations
   - Measure sleep consolidation impact, drive state drift, relational memory growth
   - Validate that multi-tick effects (mode change, narrative elaboration) are *positive*

### Low Priority (research)

5. **Peripheral module sensitivity analysis**
   - Vary parameters for Tier B modules (sympathetic state preset, will trajectory)
   - Measure mode volatility and decision consistency
   - Understand degrees of freedom that affect output

---

## Module Validation Checklist (for v1.0)

| Tier | Module Status | Tests Green? | Ground Truth Labeled? | External Validation? | v1.0 Ready? |
|------|---------------|--------------|----------------------|----------------------|------------|
| **A** (Core) | MalAbs, Bayes | ✅ | ✅ (kernel outputs) | ⚠️ (0% → 100% is calibration) | ⚠️ Partial |
| **B** (Mode) | Sympathetic, Will, Locus, Uchi–Soto | ✅ (runs) | ❌ | ❌ | ❌ |
| **C** (Narrative) | Narrative, Weak Pole, Forgiveness, DAO | ✅ (runs) | ❌ | ❌ | ❌ |
| **D** (Reflection) | Reflection, Salience, PAD | ✅ (runs) | ❌ | ❌ | ❌ |
| **E** (Cross-tick) | Psi Sleep, Drives, Augenesis | ❌ | N/A | N/A | ❌ |

---

## Conclusion

The 9-scenario empirical pilot establishes **reproducibility** and **determinism** at the core decision path level. However, true **external validation** requires:

1. Human raters for mode/rationale quality
2. Ablation boundaries to isolate peripheral module effects
3. Multi-turn scenarios to measure narrative and governance coherence

**Next empirical work should focus on (Priority) Mode validation → Narrative coherence → Cross-tick learning**, rather than expanding scenario count without deeper labels.

---

*Empirical Pilot Validation Report — 2026-04-16*  
*Ethos Kernel — MoSex Macchina Lab*
