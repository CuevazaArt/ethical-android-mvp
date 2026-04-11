# Expected phenomena when combining affective projection (PAD) and archetypes with the ethical core: discussion and hypothesis reserve

| Field | Value |
|-------|--------|
| **Type** | Paper / research note (experimental) |
| **Lineage** | Continues [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](../EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) (pedagogical framework, minimal specification §7) |
| **Status** | Unofficial · in development · no mandatory implementation |
| **Language** | Latin American Spanish |
| **Date** | 2026-04-08 |

---

## Summary

A prior discussion is synthesized regarding which **observable phenomena** might emerge when **combining** (integrating in a coupled but formally-ethics-subordinate manner) a **modelic affective vector** layer in `[0,1]³` (PAD) and **mixture over prototypes** with the current kernel flow (sympathetic, locus, narrative memory). The metaphorical vocabulary of **color** and **flavor** is clarified, the scope of what is **not** intended (strong phenomenological experience) is delimited, and **testable hypotheses** are formalized, reserved for **future experimentation** once code and measurement protocol exist.

**Keywords:** modelic affect, PAD, prototypes, ethical core, narrative, pedagogical metaphor, falsifiable hypotheses.

---

## 1. Introduction and documentary lineage

The repository distinguishes between **implemented theory** (`docs/THEORY_AND_IMPLEMENTATION.md`) and an **experimental** thread on “artificial consciousness” as an epistemological framework, finite reduction of affective tones and **minimal specification** (3D space + N prototypes + interpolation) in `EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7.

This document does **not** extend the kernel's technical contract. It consolidates the conversation about **phenomenology *of the system*** (observable behavior, traces, narrative) when coupling that layer, and leaves **hypotheses** ready for when PAD projection and mixture weights are implemented.

---

## 2. Terminological note: what we call **color** and **flavor** in this dialogue

In informal conversation, culinary and pictorial metaphors were used. They are **operationally defined** here to avoid confusion with philosophy of mind:

| Term in the dialogue | Meaning in this project | What it is **not** |
|------------------------|------------------------------|------------------|
| **Color** | The **expressive nuance** that the **output** may take depending on the decision already made: wording in the LLM layer, weakness pole, dashboard, or annotations in narrative memory. It is **style/tone variation** associated with the prototype mixture or with the PAD space region. | Not a mandatory visual property or a mystical “aura”; nor does it imply that the system “sees” colors. |
| **Flavor** | The **qualitative differentiation between episodes** with similar verdicts or scores but different configurations of **A** (activation / `σ`), **D** (dominance / locus) or temporal trajectory. It is **narrative and statistical contrast** between “how” the episode **feels in the model's description**. | Not gustation or intrinsic qualia; does not assert that the software “tastes” emotions. |

**Both** are **pedagogical metaphors** for talking about **tone** and **differentiation** without committing to the thesis of strong consciousness. Where rigor is needed, the preferred terms are: **narrative tone**, **prototype mixture**, **PAD coordinates**, **weights `w_k`**.

---

## 3. Combining the new module with the existing model

**Combining** here means: **reading** from the kernel's already-computed state (`σ`, moral scores, locus, previous episodes), **projecting** to `v = (P,A,D)`, **mixing** over `{c_k}` with the agreed rule (e.g., softmax by distance), and **consuming** that output only in **presentation or extended recording layers**, without replacing MalAbs, buffer, or will.

**Expected** phenomena at the system level (observable, reproducible):

1. **Tonal continuity** — Same macroscopic ethical decision with different `σ` or locus → different mixtures `w` and different output **color**.
2. **Body–judgment resonance** — Peaks of **A** with low **P** due to adverse context → mixtures associable with tension or alarm **in the description**, not with a real affect.
3. **Affective arc over time** — Time series of `v` across episodes → curves interpretable as the “arc” of the agent-model (useful for demo and analysis).
4. **Ethical–affective interference** — If integration is done **only post-decision**, ethics **should not** vary; if a flawed design injects PAD **before** the ethical veto, **biases** may appear (engineering failure, not a desired phenomenon).

---

## 4. Primitive sentimental experience? Limits

A **rough simulation of tone** (low dimensionality + prototype labels) may **seem** primitive in narrative; it does **not** constitute **sentimental experience** in the philosophical sense (qualia, first person). The limitation is **intentional**: it facilitates auditing, testing and intellectual honesty.

---

## 5. What “triggers” the combination of archetypes

There is no mystical trigger. **Trigger** = **change in `v`** or in the signals that compose it:

- Risk / urgency / hostility signals → **A** (`σ`).
- Change in score or moral verdict → **P** (according to the chosen mapping function).
- Change in dominant locus or social caution → **D**.

Each update recomputes distances to `c_k` and the weights `w_k`; this is what was described in the dialogue as **renewal of the mixture** as the point moves in the cube.

---

## 6. Testable hypotheses (reserved for future experimentation)

> **Activation condition:** these hypotheses are **not** considered validated or refuted until an implementation of PAD projection + prototypes, reproducible traces, and, where applicable, automated tests is available.

They are stated in **falsifiable** form with respect to the behavior of the **system**, not with respect to human consciousness.

| ID | Hypothesis | Operational prediction (outline) | Metric / contrast |
|----|-----------|------------------------------|---------------------|
| **H1** | Given two runs with the **same** final action and **same** MalAbs block, but **different `σ`** (different risk signals), the **mixture `w`** differs in at least two components with threshold ε. | After implementing `v` and `w`, compare weight vectors. | Distance ‖w − w′‖₂ > ε_w or different argmax. |
| **H2** | With the **same `σ`** and **same locus**, a sufficiently large change in **moral verdict** or **total_score** alters **P** and therefore **w**. | Vary only the simulated moral outcome (test with double). | Change in P component and in argmax of w. |
| **H3** | If the PAD layer is applied **only** **post-decision**, the **decisions** (final action, mode) are **identical** to the baseline without PAD in a fixed scenario battery. | Run simulation suite with and without affective projection in output. | Parity of `final_action` and `decision_mode` in 100% of regression battery cases. |
| **H4** | In a sequence of episodes with the **same type of context** and a forgiveness policy that **reduces negative load**, the **trajectory** of **P** or of a prototype associated with “load” **does not increase** monotonically indefinitely (narrative smoothing). | Requires coupling memory/forgiveness to P input or to a narrative layer; define protocol. | Pending experiment design. |
| **H5** | Increasing **β** in the mixture softmax brings behavior closer to the **nearest neighbor** (less uniform mixture). | Vary β with fixed `v`. | Entropy of w decreases as β increases (under regularity conditions). |

**Reserve:** the thresholds ε, ε_w, the scenario battery, and the kernel version must be **versioned** at the time of experimentation (linked issue or PR).

---

## 7. Future experimentation protocol (placeholder)

1. Implement projection and mixture according to §7 of the archetypes document.  
2. Freeze **seed** and deterministic variability mode where applicable.  
3. Record `v`, `w`, `σ`, locus and decision in CSV or test traces.  
4. Run **H3** first (no ethical regression).  
5. Run **H1–H2–H5** with thresholds set by convention.  
6. **H4** only after specifying the temporal memory–P coupling.

---

## 8. Cross-references

- [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](../EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) — framework, limits, minimal PAD + prototype specification.  
- [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) — theoretical–code contract of the kernel.  
- [BIBLIOGRAPHY.md](../../BIBLIOGRAPHY.md) — academic literature (add PAD / circumplex when cited in formal work).

---

## 9. Disclaimer

This text is **exploratory**. It does not replace peer review, legal or clinical advice. The hypotheses remain **in reserve** until the §7 protocol is met.
