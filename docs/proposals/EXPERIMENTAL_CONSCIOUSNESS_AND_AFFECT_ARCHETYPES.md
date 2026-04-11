# Artificial consciousness (framework), affect, and archetypes — experimental notes

> **Status:** experimental · unofficial · in development
> **Purpose:** preserve a discussion thread to deepen later and, eventually, integrate ideas into the main model **only** if they pass review and testing.
> **Language:** Latin American Spanish (original); translated to English.
> **Last updated:** 2026-04-09 (governing paradigm: PAD + archetypes, §7)

This document does **not** form part of the published kernel's technical contract. Nothing here obligates code behavior until explicit implementation, tests, and review exist.

**Governing experimental paradigm:** the line considered **most solid and auditable** for an affect layer *posterior* to the ethical core is **PAD in `[0,1]³` + N prototypes (archetypes) + distance weights / softmax** (specification in §7). That chain is grounded in literature and in signals the kernel already computes (`sigma`, moral scores, locus). Any design alternative should be explicitly compared against §7 and its ethical non-regression invariants.

**See also (same experimental line):** [PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md](experimental/PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md) — expected phenomena when combining PAD/prototypes, notes on *color* and *flavor*, reserved testable hypotheses.

**Discussion (not backlog):** v6 framework on self-reference, global workspace, drives, and narrative self — [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md) (includes criteria for **contribution vs redundancy** with the current kernel).

---

## 1. Why this file exists

Definitions and boundaries agreed upon in internal dialogue are collected here, covering:

- Use of the term **"artificial consciousness"** for outreach and pedagogical purposes.
- What is typically understood by **strong consciousness** versus defensible claims in an MVP.
- A design hypothesis: **finite affective archetypes** (each with its own **range**), anchored in dimensions with some empirical consensus, to **formalize** and integrate into the model **in a functional sense**, without claiming to solve the "hard problem" of mind.

---

## 2. "Artificial consciousness" as an epistemological or pedagogical framework

It is reasonable to use the term **as a language tool and knowledge organizer**, not as a demonstration of subjective experience or of software moral rights.

**Recommendation for honest usage:**

- Declare the framework at the start of the text or talk: *here "artificial consciousness" names a **model** for integrating memory, narrative identity, and explicit ethical constraints; it does **not** claim experience or consciousness in a strong philosophical sense.*
- Alternate with technical terms that ground it: *ethical agency model*, *normative core*, *narrative identity in system state*.
- In headlines or social media, when context may be cut off, use quotes or a subtitle: *"artificial consciousness" (in a model-theoretic sense)*.

---

## 3. Strong consciousness and "feeling"

In philosophy of mind, what is often called **strong** or **phenomenological consciousness** points to **subjective experience in general**: that there is *something it is like* to be in that state (*what it's like*).

- **Feeling** in the broad sense (pain, sensory qualities, the "redness" of red) aligns with **lived qualities** (*qualia*).
- **Emotion** (fear, joy, shame) is **one type** of subjective experience, **not** the only one: perception, bodily state, and sometimes thought with experiential tone also belong.

Therefore, it is **not** accurate to reduce strong consciousness solely to "emotion"; the strong thesis is broader: **subjectivity**.

**Implication for the project:** the MVP can model **formal states** and **narrative** without claiming that the software **feels**.

---

## 4. Hypothesis: consensual archetypes with ranges (partial reduction)

**Guiding question:** restricting the analysis to what human experience allows us to study methodically, is it possible — to some extent — to reduce **reportable** subjective experiences to a **finite number of relatively consensual archetypes**, each with its own **range** (internal interpolation), in order to **acquire them mathematically** (vectors, regions, scales) and **integrate them into the model**?

### 4.1 Where serious support exists (partial consensus)

- **Dimensional models:** substantial evidence supports describing much of human affect with few dimensions, typically **valence** and **arousal**; sometimes **dominance** (spaces like **PAD**: pleasure–arousal–dominance). Allows numbers, interpolation, and "ranges."
- **Prototypical categories:** traditions with finite sets of "basic" emotions; consensus is **not** universal (cultural and social-construction critiques).
- **Hybrids:** discrete categories + gradation within each (consistent with Likert-type scales or circumplex models).

### 4.2 What "reducing" means in practice

It does not reduce "consciousness" as a whole, but rather **operationalizable aspects** (self-report, language, behavior, and in the future perhaps peripheral signals) to **coordinates** in a bounded space.

**"Consensual"** here means **relative scientific consensus**, not an eternal unique catalog: cultural and linguistic variation should be assumed.

### 4.3 Mathematical integration into the model (engineering direction)

In principle compatible with an auditable design:

1. Define a **space** (e.g., 2D–3D vector + optional labels).
2. Map context and kernel signals to **points or regions** in that space.
3. Allow **interpolation** between prototypes (range within the archetype).
4. Tie results to **tests** and traceability (aligned with the repo's philosophy).

This does not resolve the ontological problem of experience; it **can** serve as an explicit **affective state layer** or **narrative tone** layer.

### 4.4 Honest limits

| Topic | Limit |
|-------|-------|
| Phenomenological richness | A vector does not capture "what it feels like"; it summarizes dimensions useful for decision or narrative. |
| Consensus | Dimensions tend to be more stable than discrete labels. |
| Culture | Archetypes are not identical across all communities. |
| Hard problem | Formalizing correlates does not explain why experience exists in organisms. |

---

## 5. Tentative relationship with current code (pointers)

Without implementation commitment:

- Modules such as **sympathetic/parasympathetic**, **narrative memory**, and **ethical poles** already manipulate **numeric states** and narrative; a PAD-like or **archetypes + interpolation** layer could connect as an **interface** or **state projection**, not as a substitute for the normative core.
- Any integration should respect the README principle: the **LLM does not decide** ethical policy; an affective layer should also not **replace** the buffer or MalAbs.

---

## 6. Future work (suggested checklist)

- [ ] Fix an **operational definition** of "experiential tone" or "modelic affect" in one sentence.
- [ ] Review literature (PAD, circumplex, basic emotions vs. constructionism) and anchor references in `BIBLIOGRAPHY.md` if the experiment continues.
- [ ] Minimal prototype: 2D–3D space + interpolation rules + ethical non-regression tests.
- [ ] Review with an **intercultural** perspective before presenting any catalog as "universal."

---

## 7. Minimal specification: 3D space + N prototypes + interpolation

> **Scope:** prototype in code: `src/modules/pad_archetypes.py` + registration in `KernelDecision` / `NarrativeEpisode` (post-decision). Aligned with `SympatheticModule` (`sigma`), narrative memory (`NarrativeEpisode`, `sigma` already saved), and `locus` (approximate dominance).

> **Reference:** this section is the **canonical specification** in the repo for experimentation in modelic affect (PAD + archetypes). Implementations and derived papers should follow it unless a documented deviation is decided.

### 7.1 Modelic affect vector `v = (P, A, D)`

Coordinates in **`[0, 1]³`** (normalized PAD: pleasure/valence, arousal, dominance). This is a **projection** of signals already computed in the kernel cycle, not an independent input from the world.

| Axis | Role | Proposed mapping from current pipeline state |
|------|------|----------------------------------------------|
| **A** (arousal) | Alert ↔ physiological rest of the agent's "body" | **`sigma`** from `InternalState`: `SympatheticModule.SIGMA_MIN` and `SIGMA_MAX` are 0.2 and 0.8 → `A = (sigma - 0.2) / 0.6`, clamped to [0, 1]. |
| **P** (valence) | Aggregated "positive ↔ negative" tone *in the episode's ethical judgment* | Normalize **`moral.total_score`** (or `ethical_score` when registering the episode) to [0, 1] with a fixed and documented function (e.g., linear by observed range in simulations, or `P = 0.5 + 0.5 * tanh(λ * score)`). **Placeholder** until empirical calibration. |
| **D** (dominance) | Sense of agency / control vs. external forces | **`locus_eval.dominant_locus`**: `internal` → 1.0, `balanced` → 0.5, `external` → 0.0. (Future alternative: blend with Uchi-Soto `caution_level` in a bounded formula.) |

**Note:** `P` depends on the multipolar pole score scale; any scale change requires **re-calibrating** the mapping to avoid breaking prototype interpretation.

### 7.2 N prototypes (archetypes)

- Each prototype `k ∈ {0,…,N-1}` has:
  - **`id_k`**: stable identifier (`str`, e.g., `"deliberative_calm"`).
  - **`c_k = (P_k, A_k, D_k)`** ∈ `[0,1]³`: archetype center.
  - Optional: **`label_k`** for narrative / UI (translatable).

**Reasonable minimum N for testing:** 4–8 well-separated points in the cube (avoid overlap initially). "Emotional" names are **pedagogical convention**; formally only `c_k` matters.

### 7.3 Interpolation and "range" within the archetype

**Version v0 (auditable, single formula):**

1. Given `v`, for each prototype `k`, Euclidean distance `d_k = ‖v - c_k‖₂`.
2. Inverse-distance softmax weights:
   `w_k = exp(-β · d_k) / Σ_j exp(-β · d_j)` with **β > 0** (temperature: large β → nearly nearest neighbor; small β → more uniform mixture).
3. **Main output:** vector **`w`** (mixture over prototypes) + index **`k* = argmax w_k`** (dominant tone).
4. **Local range (optional):** if `d_{k*} < ε`, consider `v` to be **within the range** of prototype `k*`; if fine-grained variation is desired without additional dimensions, linearly interpolate between `c_{k*}` and the **second best** neighbor in the convex hull of nearby prototypes (for narrative smoothing only, not for ethics).

**Cheaper alternative:** just **nearest neighbor** + `d_{k*}` as a **tone uncertainty** measure (no softmax).

### 7.4 Where it fits in the code (without altering kernel authority)

| Point | Role |
|-------|------|
| **After** `KernelDecision` | Compute `v` and `w` with already-available data (`sympathetic_state`, moral result, `locus_evaluation`). |
| **`NarrativeEpisode`** | Fields **`affect_pad`** and **`affect_weights`** (optional; filled when the episode passes through the kernel with PAD active). `sigma` continues to be saved; PAD extends the record without replacing it. |
| **LLM / weakness pole layer** | Use only **tone output** (text or nuance), **after** fixing the ethical decision. |

### 7.5 Conceptual safety invariants

- No weight `w_k` nor `P/A/D` should **replace** MalAbs, the buffer, or the will function; they are not input signals to the absolute veto in this minimal specification.
- If implemented: **non-regression tests** — same ethical inputs → same decision even if prototype labels or β change (only the projection/narrative layer changes).

### 7.6 Free parameters to fix before integrating

`β`, `ε`, the set `{c_k}`, function `P(score)`, and whether `D` incorporates Uchi-Soto terms in addition to locus.

---

## 8. Disclaimer

The opinions here are **exploratory**. They do not constitute philosophical, legal, or clinical advice. The public project continues to be governed by the code, tests, and official repository documentation.
