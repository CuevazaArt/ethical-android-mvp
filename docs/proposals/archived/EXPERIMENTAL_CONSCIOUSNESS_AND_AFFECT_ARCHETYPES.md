# Artificial consciousness (framing), affect, and archetypes — experimental notes

> **Status:** experimental · unofficial · in development  
> **Purpose:** preserve a discussion line to deepen later and, eventually, merge ideas into the main model **only** after review and tests.  
> **Language:** English (repository canonical).  
> **Last updated:** 2026-04-14 (ruling paradigm: PAD + archetypes, §7)

This document is **not** part of the published kernel technical contract. Nothing here binds code behavior until there is implementation, tests, and explicit review.

**Ruling experimental paradigm:** the line considered **most solid and auditable** for an affect layer *after* the ethical core is **PAD in `[0,1]³` + N prototypes (archetypes) + distance / softmax weights** (specification in §7). That chain rests on literature and signals the kernel already computes (`sigma`, moral scores, locus). Any alternative design should compare explicitly against §7 and its ethical no-regression invariants.

**See also (same experimental thread):** [PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md](PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md) — phenomena when combining PAD / prototypes, notes on qualitative “color” and “flavor,” reserved testable hypotheses.

**Discussion (not backlog):** v6 framing on self-reference, global workspace, drives, and narrative self — [EMERGENT_CONSCIOUSNESS_V6.md](EMERGENT_CONSCIOUSNESS_V6.md) (includes **contribution vs redundancy** criteria vs the current kernel).

---

## 1. Why this file exists

It collects definitions and limits agreed in internal dialogue on:

- Using the phrase **“artificial consciousness”** for outreach and pedagogy.
- What **strong consciousness** usually means vs defensible claims in an MVP.
- A design hypothesis: **finite affective archetypes** (each with an internal **range**), anchored in dimensions with some empirical consensus, to **formalize** and integrate into the model in a **functional** sense, without claiming to solve the “hard problem” of mind.

---

## 2. “Artificial consciousness” as epistemic or pedagogical framing

It is reasonable to use the term **as a language and knowledge-organization tool**, not as proof of subjective experience or software moral rights.

**Honest usage recommendations:**

- State the frame at the start of text or talk: *here “artificial consciousness” names a **model** integrating memory, narrative identity, and explicit ethical limits; **no** claim of experience or consciousness in a strong philosophical sense.*
- Alternate with technical anchors: *ethical agency model*, *normative core*, *narrative identity in system state*.
- In headlines or social posts, if context is clipped, use quotes or subtitle: *“artificial consciousness” (model sense).*

---

## 3. Strong consciousness and “feeling”

In philosophy of mind, **strong** or **phenomenological** consciousness often means **subjective experience in general**: that *there is something it is like* to be in that state (“what it’s like,” *what it’s like*).

- **Feeling** in a broad sense (pain, sensory qualities, the “redness” of red) fits **lived qualities** (*qualia*).
- **Emotion** (fear, joy, shame) is **one kind** of subjective experience, **not** the only: perception, bodily state, sometimes thought with experiential tone also count.

Thus strong consciousness should **not** be reduced to “emotion” only; the strong claim is broader: **subjectivity**.

**Project implication:** the MVP can model **formal states** and **narrative** without claiming the software **feels**.

---

## 4. Hypothesis: consensual archetypes with ranges (partial reduction)

**Guiding question:** restricting analysis to what human experience allows us to study methodically, is it possible — up to a point — to reduce **reportable** subjective experiences to a **finite number of relatively consensual archetypes**, each with its **own range** (internal interpolation), to **encode them mathematically** (vectors, regions, scales) and **integrate them into the model**?

### 4.1 Where there is serious support (partial consensus)

- **Dimensional models:** substantial evidence supports describing much human affect with few dimensions, typically **valence** and **arousal**; sometimes **dominance** (**PAD**: pleasure–arousal–dominance spaces). Enables numbers, interpolation, and “ranges.”
- **Prototypic categories:** traditions with finite sets of “basic” emotions; consensus is **not** universal (cultural and social-construction critiques).
- **Hybrids:** discrete categories + grading inside each (consistent with Likert-type or circumplex scales).

### 4.2 What “reduce” means in practice

We do not reduce “consciousness” wholesale, but **operationalizable** aspects (self-report, language, behavior, perhaps peripheral signals in the future) to **coordinates** in a bounded space.

**“Consensual”** here means **relative scientific consensus**, not one eternal catalog: assume **cultural and linguistic variation**.

### 4.3 Mathematical integration (engineering direction)

In principle compatible with an auditable design:

1. Define a **space** (e.g. 2D–3D vector + optional labels).
2. Map context and kernel signals to **points or regions** in that space.
3. Allow **interpolation** between prototypes (range within an archetype).
4. Tie results to **tests** and traceability (aligned with repo philosophy).

That does not solve the ontological problem of experience; it **can** serve as an **affective state layer** or explicit **narrative tone**.

### 4.4 Honest limits

| Topic | Limit |
|-------|--------|
| Phenomenological richness | A vector does not exhaust “what it’s like”; it summarizes dimensions useful for decision or narrative. |
| Consensus | Dimensions tend to be more stable than discrete labels. |
| Culture | Archetypes are not identical across communities. |
| Hard problem | Formalizing correlates does not explain why experience exists in organisms. |

---

## 5. Tentative relation to current code (pointers)

No implementation commitment:

- Modules such as **sympathetic/parasympathetic**, **narrative memory**, and **ethical poles** already manipulate **numeric states** and narrative; a PAD-like or **archetype + interpolation** layer could connect as a **interface** or **state projection**, not a substitute for the normative core.
- Any integration should respect the README principle: the **LLM does not decide** ethical policy; an affective layer should not **replace** the buffer or MalAbs either.

---

## 6. Future work (suggested checklist)

- [ ] Fix a one-sentence **operational** definition of “experiential tone” or “model affect.”
- [ ] Review literature (PAD, circumplex, basic emotions vs constructionism) and anchor references in [`BIBLIOGRAPHY.md`](../../BIBLIOGRAPHY.md) if the experiment continues.
- [ ] Minimal prototype: 2D–3D space + interpolation rules + ethical no-regression tests.
- [ ] **Intercultural** review before presenting a catalog as “universal.”

---

## 7. Minimal specification: 3D space + N prototypes + interpolation

> **Scope:** code prototype: `src/modules/pad_archetypes.py` + registration on `KernelDecision` / `NarrativeEpisode` (post-decision). Aligned with `SympatheticModule` (`sigma`), narrative memory (`NarrativeEpisode`, `sigma` already stored) and `locus` (approximate dominance).

> **Reference:** this section is the repo’s **canonical specification** for model-affect experimentation (PAD + archetypes). Implementations and derivative papers should follow it unless a documented deviation is decided.

### 7.1 Model-affect vector `v = (P, A, D)`

Coordinates in **`[0, 1]³`** (normalized PAD: pleasure/valence, arousal, dominance). It is a **projection** of signals already computed in the kernel cycle, not an independent world input.

| Axis | Role | Proposed mapping from current pipeline state |
|------|------|-----------------------------------------------|
| **A** (arousal) | Alert ↔ resting physiology of the agent “body” | **`sigma`** from `InternalState`: `SympatheticModule.SIGMA_MIN` and `SIGMA_MAX` are 0.2 and 0.8 → `A = (sigma - 0.2) / 0.6`, clamp to [0, 1]. |
| **P** (valence) | Aggregated “positive ↔ negative” tone *in the episode’s ethical judgment* | Normalize **`moral.total_score`** (or `ethical_score` when registering the episode) to [0, 1] with a fixed, documented function (e.g. linear on observed simulation range, or `P = 0.5 + 0.5 * tanh(λ * score)`). **Placeholder** until empirical calibration. |
| **D** (dominance) | Sense of agency / control vs external forces | **`locus_eval.dominant_locus`**: `internal` → 1.0, `balanced` → 0.5, `external` → 0.0. (Future: blend with Uchi–Soto `caution_level` in a bounded formula.) |

**Note:** `P` depends on multipolar score scale; any scale change requires **re-calibration** so prototype interpretation does not break.

### 7.2 N prototypes (archetypes)

Each prototype `k ∈ {0,…,N-1}` has:

- **`id_k`**: stable id (`str`, e.g. `"deliberative_calm"`).
- **`c_k = (P_k, A_k, D_k)`** ∈ `[0,1]³`: archetype center.
- Optional: **`label_k`** for narrative / UI (translatable).

**Reasonable minimum N for tests:** 4–8 well-separated points in the cube (avoid overlap initially). “Emotional” names are **pedagogical convention**; the formal object is only `c_k`.

### 7.3 Interpolation and “range” within an archetype

**v0 (auditable, single formula):**

1. Given `v`, for each prototype `k`, Euclidean distance `d_k = ‖v - c_k‖₂`.
2. Inverse-distance softmax weights:  
   `w_k = exp(-β · d_k) / Σ_j exp(-β · d_j)` with **β > 0** (temperature: large β → nearest neighbor; small β → more uniform mix).
3. **Main output:** vector **`w`** (mixture over prototypes) + index **`k* = argmax w_k`** (tone protagonist).
4. **Local range (optional):** if `d_{k*} < ε`, treat `v` as **inside the range** of prototype `k*`; for fine variation without more dimensions, linearly interpolate between `c_{k*}` and the **second-best** neighbor in the convex hull of nearby prototypes (narrative smoothing only, not ethics).

**Cheaper alternative:** **nearest neighbor** only + `d_{k*}` as **tone uncertainty** (no softmax).

### 7.4 Where it fits in code (without changing core authority)

| Point | Role |
|-------|------|
| **After** `KernelDecision` | Compute `v` and `w` from available data (`sympathetic_state`, moral outcome, `locus_evaluation`). |
| **`NarrativeEpisode`** | Optional fields **`affect_pad`** and **`affect_weights`** (filled when PAD is active for the episode). `sigma` remains stored; PAD extends the record without replacing it. |
| **LLM layer / weakness pole** | Use **tone output** (text or shading) **after** the ethical decision is fixed. |

### 7.5 Conceptual safety invariants

- No weight `w_k` nor `P/A/D` may **replace** MalAbs, buffer, or the will function; they are not inputs to the absolute veto in this minimal spec.
- If implemented: **no-regression** tests — same ethical inputs → same decision even if prototype labels or β change (only projection/narrative layer changes).

### 7.6 Free parameters to fix before integration

`β`, `ε`, set `{c_k}`, function `P(score)`, and whether `D` adds Uchi–Soto terms beyond locus.

---

## 8. Disclaimer

Views here are **exploratory**. They are not philosophical, legal, or clinical advice. The public project remains governed by code, tests, and official repository documentation.
