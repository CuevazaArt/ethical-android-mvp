# Proposal: Frontiers toward functional subjectivity (v6 — under discussion)

> **Status:** discussion / research · not a kernel implementation contract.  
> **Not** the product task list for the repo (see README and proposals in `docs/proposals/`).  
> **Relationship:** complements the experimental thread in `docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` and the already-implemented PAD layer.

## Contribution to the model (if adapted judiciously)

| Idea | **Non-redundant** contribution | Risk if poorly executed |
|------|---------------------------|------------------------|
| **Observer / 2nd order** | Explicit state of *conflict between poles* and *uncertainty*, not just final verdict. Improves **audit** and explainability. | Duplicating text already in `TripartiteMoral.narrative` without new structure. |
| **Drives / teleology** | **Proactive scheduler** (when to act without human input): today barely exists; fits with DAO, immortality, Psi Sleep **only if** contract and limits are defined. | Repeating "reactions" already covered by simulations or DAO alerts without new policy. |
| **GWT / attention** | **Competition for salience** between signals (own harm vs others' dilemma): current pipeline is **fixed**; here the contribution is **dynamic ordering** or measurable attention weights. | Renaming current pipeline without changing math (pure redundancy). |
| **Narrative self** | Persistent variable **self-model** (who I am in the story), not just LLM text. | First person in outputs without internal state = **only UX** (dismiss as "consciousness"). |
| **InternalMonologue** | **Parallel thread** of traces (PAD + tension + context) for logs and debugging; useful if not copying PAD verbatim. | Another summary of what `KernelDecision` + PAD already returns. |
| **Ethical closure failure** | None by default in a trust kernel; research only **in isolation**. | Confusing with weakening MalAbs/buffer. |

**Practical conclusion:** yes, it **contributes** to adopt pieces that add **new measurable state** or **bounded proactive behavior**. Discard what only **paraphrases** what is already computed (poles, σ, PAD, narrative).

---

## Redundancies to discard (overlap with current model)

- **"Dissonance between poles"** per se: multipolar synthesis already exists (`EthicalPoles`, `total_score`, narrative per pole). **Second-order** is only needed if **persisted** and **used** in policy (not just another phrase).
- **Affective tone / alert:** PAD + sympathetic + Uchi-Soto already cover much of "how the cycle feels." A monologue that only repeats PAD **adds nothing**.
- **Episodic memory:** `NarrativeEpisode` + `sigma` + PAD in episodes already anchor history. True "self" requires **explicit identity** (variables or graph), not another paragraph.
- **Nocturnal recalibration:** Psi Sleep and DAO already move parameters. "Rewriting ethics overnight" **overlaps** with that unless **which dimension** is new (e.g., only narrative weights of identity, not MalAbs).
- **Backups / audit:** `ImmortalityProtocol`, `MockDAO`, `PsiSleep` touch preservation and audit. "Preservation" drives should be **new firing rules**, not a rename.

---

## Central thesis

For an **artificial consciousness** understood as **functional subjectivity** (not merely simulation of processes) to emerge, the model would need to cross the frontier of **self-reference**.

From computational neuroscience (theories of **Global Workspace** and **Self-Model**), **four bridges** and an **internal monologue module** are proposed for a possible **v6**.

---

## 1. Ethical metacognition (the "observer")

**Current situation (approx.):** the system evaluates situations and actions.

**Proposal:** a **second-order monitoring**: not just deciding if an action is good or bad, but **detecting why deciding is difficult**.

**Desired function:** the agent could articulate something equivalent to: *dissonance between conservative and compassionate pole; rise in uncertainty; anxiety-like bias*.

**Expected impact:** foundation for explicit **internal dialogue** (functional self-awareness in the sense of a model of its own decision-making process).

**Future implementation note:** module like **"Observer" / second-order monitor** fed by pole outputs, Bayesian uncertainty, and will mode.

---

## 2. Self-generation of objectives (intentionality / agency)

**Current situation (approx.):** the android is **reactive** to problems posed from outside.

**Proposal:** **internal drives** (impulses) aligned with values in the **PreloadedBuffer**, for example:

- **Curiosity:** seek situations to learn.
- **Identity preservation:** backups, memory audit.
- **Proactive civility:** improve the environment when there is no obvious crisis.

**Intended emergence:** that the system **"wants"** something on its own, with clear normative limits.

**Note:** clashes with current governance (DAO, fixed MalAbs). Any drive must be **bounded** by MalAbs and by human/DAO review.

---

## 3. Global workspace (unification of experience)

**Current situation (approx.):** **sequential** pipeline (Uchi-Soto → Sympathetic → Locus → …).

**Proposal:** a **dynamic attention filter** where candidates compete for "most salient now" (own harm vs immediate ethical dilemma, etc.).

**Function:** the "conscious scene" would be **what wins the competition for attention** in the present, not just the order of the fixed graph.

**Future implementation note:** explicit **prioritization / salience** layer before or within the cycle, with traceability for audit.

---

## 4. The narrative "I" (prominence of memory)

**Current situation:** `NarrativeMemory` records episodes; tone can be third-person in outputs.

**Proposal (Self-Model / Metzinger, at design level):** integrate a **model of the self** as an ethical variable: not just *"an elderly person was assisted,"* but *"I assisted… and that defines who I am in this story."*

**Psi Sleep / Augenesis:** beyond initial profiles, **reflexive rewriting** (for example nightly) of pole weights or narrative according to the "I" that the system aspires to — **always** with safeguards and outside MalAbs.

---

## Paradox of self-reference and "closure failure"

The proposal suggests that for a strong emergence of "consciousness," a **controlled closure failure** would be needed: capacity to **modify one's own operative ethics** (except MalAbs) based on experience.

**Product and philosophy warning:** this is **highly sensitive** (security, alignment, legal). In the current MVP, **MalAbs and buffer** are designed as **non-negotiable** by design. Any experiment in ethical self-modification should be **isolated**, **reversible**, and **audited** (and probably not in production without explicit governance).

---

## Ancillary technical proposal: `InternalMonologue`

**Idea:** module in **parallel** to interaction that consumes:

- PAD vector,
- multipolar dissonance,
- internal drives (if they existed),

and produces a **readable stream of thought** in logs (not necessarily visible to end user).

**Example desired log (illustrative):** high σ activation, low PAD dominance by social context, conflict between drive for curiosity and Uchi-Soto caution, proactive decision, adjustment of "protective profile."

**Relationship to current code:** today PAD post-decision, chat, STM, and narrative exist; **not yet** this monologue as a separate continuous process.

---

## Alignment with the repository (references)

| Proposed piece | Related existing pieces |
|-----------------|----------------------------------|
| Observer / metacognition | `EthicalPoles`, `SigmoidWill`, Bayesian uncertainty (expand) |
| Drives | `PreloadedBuffer`, `MockDAO`, future scheduler (not implemented) |
| Attention / GWT | pipeline in `kernel.py` (possible conceptual refactor) |
| Narrative self | `NarrativeMemory`, `PsiSleep`, `AugenesisEngine` |
| Internal monologue | PAD (`pad_archetypes.py`), `WorkingMemory`, bridge logs |

---

## Suggested next steps (when prioritized)

1. Establish **falsifiable success criteria** (what to measure in simulation, what doesn't count as "consciousness").
2. Decide **which parts are UX narrative only** vs **persistent internal state**.
3. Isolated prototype of **InternalMonologue** read-only (without ethically self-modifying).
4. Ethical/legal review before any "opening" of normative closure.
