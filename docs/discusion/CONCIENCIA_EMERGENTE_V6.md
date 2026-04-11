# Proposal: boundaries toward functional subjectivity (v6 — under discussion)

> **Status:** discussion / research · not an implementation contract for the kernel.  
> **Not** the product task list for the repo (see README and proposals in `docs/discusion/`).  
> **Relationship:** complements the experimental thread in `docs/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` and the already-implemented PAD layer.

## Contribution to the model (if adapted with judgment)

| Idea | **Non-redundant** contribution | Risk if done poorly |
|------|---------------------------|------------------------|
| **Observer / 2nd order** | Explicit state of *conflict between poles* and *uncertainty*, not just the final verdict. Improves **auditing** and explainability. | Duplicating text already output in `TripartiteMoral.narrative` without new structure. |
| **Drives / teleology** | **Proactive scheduler** (when to act without human input): nearly absent today; fits with DAO, immortality, Psi Sleep **only if** contract and limits are defined. | Repeating "reactions" already covered by simulations or DAO alerts without new policy. |
| **GWT / attention** | **Salience competition** between signals (own harm vs. someone else's dilemma): the current pipeline is **fixed**; the contribution here is **dynamic ordering** or measurable attention weights. | Renaming the current pipeline without changing the math (pure redundancy). |
| **Narrative self** | Persistent **self-model** variable (who I am in the story), not just LLM text. | First person in outputs without internal state = **UX only** (dismiss as "consciousness"). |
| **InternalMonologue** | **Parallel thread** of traces (PAD + tension + context) for logs and debugging; useful if it does not copy PAD verbatim. | Another summary of the same thing that `KernelDecision` + PAD already returns. |
| **Ethical closure failure** | None by default in a trusted kernel; research **isolated** only. | Confusing with weakening MalAbs/buffer. |

**Practical conclusion:** it **does** add value to adopt pieces that add **new measurable state** or **bounded proactive behavior**. Discard what only **paraphrases** what is already computed (poles, σ, PAD, narrative).

---

## Redundancies to dismiss (overlap with the current model)

- **"Dissonance between poles"** without more: multipolar synthesis already exists (`EthicalPoles`, `total_score`, narrative per pole). A **second order** is only needed if it is **persisted** and **used** in policy (not just another sentence).
- **Affective tone / alert:** PAD + sympathetic + Uchi-Soto already cover much of "how the cycle feels". A monologue that only repeats PAD **adds nothing**.
- **Episodic memory:** `NarrativeEpisode` + `sigma` + PAD in episodes already anchor history. A true "self" requires **explicit identity** (variables or graph), not another paragraph.
- **Nocturnal recalibration:** Psi Sleep and DAO already move parameters. "Rewriting ethics at night" **overlaps** with that unless a **new dimension** is defined (e.g., only narrative identity weights, not MalAbs).
- **Backups / auditing:** `ImmortalityProtocol`, `MockDAO`, `PsiSleep` touch preservation and auditing. "Preservation" drives must be **new firing rules**, not renaming.

---

## Central thesis

For **artificial consciousness** understood as **functional subjectivity** (and not merely a simulation of processes) to emerge, the model would need to cross the boundary of **self-reference**.

Drawing from computational neuroscience (**Global Workspace** and **Self-Model** theories), **four bridges** and an **internal monologue module** are proposed for a possible **v6**.

---

## 1. Ethical metacognition (the "observer")

**Current situation (approx.):** the system evaluates situations and actions.

**Proposal:** a **second-order monitoring**: not just deciding whether an action is good or bad, but **detecting why deciding is difficult**.

**Desired function:** the agent could articulate something equivalent to: *dissonance between conservative and compassionate pole; rising uncertainty; anxiety-type bias*.

**Expected impact:** foundation for an explicit **internal dialogue** (functional self-awareness in the sense of a self-model of the decision-making process).

**Future implementation note:** module of type **"Observer" / second-order monitor** fed by pole outputs, Bayesian uncertainty and will mode.

---

## 2. Goal self-generation (intentionality / agency)

**Current situation (approx.):** the android is **reactive** to problems posed from outside.

**Proposal:** **internal drives** (impulses) aligned with values in the **PreloadedBuffer**, for example:

- **Curiosity:** seek situations to learn from.
- **Identity preservation:** backups, memory auditing.
- **Proactive civics:** improve the environment when there is no obvious crisis.

**Intended emergence:** the system **"wants"** something by itself, with clear normative limits.

**Note:** conflicts with current governance (DAO, fixed MalAbs). Any drive must be **bounded** by MalAbs and human/DAO review.

---

## 3. Global workspace (unification of experience)

**Current situation (approx.):** **sequential** pipeline (Uchi-Soto → Sympathetic → Locus → …).

**Proposal:** a **dynamic attention filter** where candidates compete for "what is most salient now" (own harm vs. immediate ethical dilemma, etc.).

**Function:** the "conscious scene" would be **whatever wins the attention competition** in the present, not just the fixed graph order.

**Future implementation note:** explicit **prioritization / salience** layer before or within the cycle, with traceability for auditing.

---

## 4. The narrative "self" (memory as protagonist)

**Current situation:** `NarrativeMemory` records episodes; tone may be third-person in outputs.

**Proposal (Self-Model / Metzinger, at the design level):** integrate a **self-model** as an ethical variable: not just *"an elderly person was assisted"*, but *"I assisted… and that defines who I am in this story"*.

**Psi Sleep / Augenesis:** in addition to initial profiles, **reflective rewriting** (e.g., nocturnal) of weights or pole narrative according to the "self" the system aspires to — **always** with safeguards and outside MalAbs.

---

## Paradox of self-reference and "closure failure"

The proposal suggests that, for a strong emergence of "consciousness", a **controlled closure failure** would be needed: the capacity to **modify its own operative ethics** (except MalAbs) based on experience.

**Product and philosophy warning:** this is **highly sensitive** (security, alignment, legal). In the current MVP, **MalAbs and buffer** are designed as **non-negotiable by design**. Any self-modification ethics experiment should be **isolated**, **reversible** and **audited** (and probably not in production without explicit governance).

---

## Collateral technical proposal: `InternalMonologue`

**Idea:** module running **in parallel** to the interaction that consumes:

- PAD vector,
- multipolar dissonance,
- internal drives (if they existed),

and produces a **stream of thought** readable in logs (not necessarily visible to the end user).

**Desired log example (illustrative):** high σ activation, low PAD dominance due to social context, conflict between curiosity drive and Uchi-Soto caution, proactive decision, adjustment of "protective profile".

**Relationship to current code:** today PAD post-decision, chat, STM and narrative exist; this monologue as a separate continuous process does **not** yet exist.

---

## Alignment with the repository (references)

| Proposed piece | Related existing pieces |
|-----------------|----------------------------------|
| Observer / metacognition | `EthicalPoles`, `SigmoidWill`, Bayesian uncertainty (expand) |
| Drives | `PreloadedBuffer`, `MockDAO`, future scheduler (not implemented) |
| Attention / GWT | pipeline in `kernel.py` (conceptual refactor possible) |
| Narrative self | `NarrativeMemory`, `PsiSleep`, `AugenesisEngine` |
| Internal monologue | PAD (`pad_archetypes.py`), `WorkingMemory`, bridge logs |

---

## Suggested next steps (when prioritized)

1. Fix **falsifiable success criteria** (what to measure in simulation, what does not count as "consciousness").
2. Decide **which parts are UX narrative only** vs. **persistent internal state**.
3. Isolated prototype of **InternalMonologue** read-only (without self-modifying ethics).
4. Ethical/legal review before any normative "closure opening".
