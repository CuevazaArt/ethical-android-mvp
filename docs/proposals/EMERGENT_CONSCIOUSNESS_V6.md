# Proposal: boundaries toward functional subjectivity (v6 — under discussion)

> **Status:** discussion / research · not an implementation contract for the kernel.  
> **Not** the repo product backlog (see README and proposals under `docs/proposals/`).  
> **Relation:** complements the experimental thread in `docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` and the implemented PAD layer.

## Contribution to the model (if adopted carefully)

| Idea | **Non-redundant** contribution | Risk if done poorly |
|------|-------------------------------|---------------------|
| **Observer / second order** | Explicit state of *conflict between poles* and *uncertainty*, not only the final verdict. Improves **audit** and explainability. | Duplicating text already in `TripartiteMoral.narrative` without new structure. |
| **Drives / teleology** | **Proactive scheduler** (when to act without human input): barely exists today; fits DAO, immortality, Psi Sleep **only if** contract and limits are defined. | Repeating “reactions” already covered by simulations or DAO alerts without new policy. |
| **GWT / attention** | **Salience competition** between signals (self-harm vs other’s dilemma): today’s pipeline is **fixed**; contribution is **dynamic ordering** or measurable attention weights. | Renaming the current pipeline without changing math (pure redundancy). |
| **Narrative self** | Persistent **self-model** variable (who I am in the story), not only LLM text. | First-person outputs with no internal state = **UX only** (do not count as “consciousness”). |
| **InternalMonologue** | **Parallel** trace thread (PAD + tension + context) for logs and debugging; useful if it does not copy PAD verbatim. | Another summary of what `KernelDecision` + PAD already return. |
| **Failure of ethical closure** | None by default in a trusted kernel; **isolated research** only. | Confused with weakening MalAbs/buffer. |

**Practical conclusion:** it **does** add value to adopt pieces that introduce **new measurable state** or **bounded proactive behavior**. Reject what only **paraphrases** what is already computed (poles, σ, PAD, narrative).

---

## Redundancies to down-rank (overlap with the current model)

- **“Dissonance between poles”** alone: multipolar synthesis already exists (`EthicalPoles`, `total_score`, per-pole narrative). Second order matters only if **persisted** and **used** in policy (not just another sentence).
- **Affective tone / alert:** PAD + sympathetic + Uchi–Soto already cover much of “how the cycle feels.” A monologue that only repeats PAD **adds nothing**.
- **Episodic memory:** `NarrativeEpisode` + `sigma` + PAD in episodes already anchor history. A real “self” needs **explicit identity** (variables or graph), not another paragraph.
- **Nightly recalibration:** Psi Sleep and DAO already move parameters. “Rewrite ethics at night” **overlaps** unless **which dimension** is new is defined (e.g. narrative identity weights only, not MalAbs).
- **Backups / audit:** `ImmortalityProtocol`, `MockDAO`, `PsiSleep` touch preservation and audit. “Preservation drives” must be **new trigger rules**, not a rename.

---

## Central thesis

For **artificial consciousness** understood as **functional subjectivity** (not only process simulation), the model would need to cross the boundary of **self-reference**.

From computational neuroscience (**Global Workspace** and **Self-Model** theories), **four bridges** and an **internal monologue** module are sketched for a possible **v6**.

---

## 1. Ethical metacognition (the “observer”)

**Approximate current state:** the system evaluates situations and actions.

**Proposal:** **second-order monitoring**: not only whether an action is good or bad, but **why the decision is hard**.

**Desired function:** the agent could articulate something like: *dissonance between conservative and compassionate poles; rising uncertainty; anxiety-like bias.*

**Expected impact:** basis for explicit **internal dialogue** (functional self-awareness as a model of the decision process itself).

**Future implementation note:** an **Observer / second-order monitor** module fed by pole outputs, Bayesian uncertainty, and will mode.

---

## 2. Self-generated goals (intentionality / agency)

**Approximate current state:** the agent is **reactive** to externally posed problems.

**Proposal:** **internal drives** aligned with **PreloadedBuffer** values, e.g.:

- **Curiosity:** seek situations to learn.
- **Identity preservation:** backups, memory audit.
- **Proactive civics:** improve the environment when no crisis is obvious.

**Intended emergence:** the system **“wants”** something on its own, within clear normative bounds.

**Note:** conflicts with current governance (DAO, fixed MalAbs). Any drive must be **bounded** by MalAbs and human/DAO review.

---

## 3. Global workspace (unifying “experience”)

**Approximate current state:** **sequential** pipeline (Uchi–Soto → Sympathetic → Locus → …).

**Proposal:** a **dynamic attention filter** where candidates compete for “what is most salient now” (self-harm vs immediate ethical dilemma, etc.).

**Function:** the “conscious scene” would be **what wins the attention competition** in the present, not only the fixed graph order.

**Future implementation note:** explicit **prioritization / salience** layer before or inside the cycle, with traceability for audit.

---

## 4. Narrative “self” (memory as protagonist)

**Current state:** `NarrativeMemory` records episodes; tone may be third person in outputs.

**Proposal (Self-Model / Metzinger, design level):** integrate a **self-model** as an ethical variable: not only *“an elder was helped”* but *“I helped… and that defines who I am in this story.”*

**Psi Sleep / Augenesis:** beyond initial profiles, **reflective rewrite** (e.g. nightly) of pole weights or narrative according to the “self” the system aspires to — **always** with safeguards and outside MalAbs.

---

## Self-reference paradox and “closure failure”

The proposal suggests that a strong emergence of “consciousness” might require a **controlled failure of closure**: ability to **modify operational ethics** (except MalAbs) from experience.

**Product and philosophy warning:** highly sensitive (safety, alignment, law). In the current MVP, **MalAbs and buffer** are **non-negotiable** by design. Any self-modification experiment should be **isolated**, **reversible**, and **audited** (likely not production without explicit governance).

---

## Collateral technical proposal: `InternalMonologue`

**Idea:** a module **in parallel** with interaction that consumes:

- PAD vector,
- multipolar dissonance,
- internal drives (if any),

and produces a **thought stream** readable in logs (not necessarily shown to the end user).

**Illustrative desired log:** high σ activation, low PAD dominance in social context, conflict between curiosity drive and Uchi–Soto caution, proactive decision, adjustment of “protective profile.”

**Relation to current code:** PAD post-decision, chat, STM, and narrative exist; this monologue is **not** yet a separate continuous process.

---

## Alignment with the repository (references)

| Proposed piece | Related existing pieces |
|----------------|-------------------------|
| Observer / metacognition | `EthicalPoles`, `SigmoidWill`, Bayesian uncertainty (extend) |
| Drives | `PreloadedBuffer`, `MockDAO`, future scheduler (not implemented) |
| Attention / GWT | pipeline in `kernel.py` (possible conceptual refactor) |
| Narrative self | `NarrativeMemory`, `PsiSleep`, `AugenesisEngine` |
| Internal monologue | PAD (`pad_archetypes.py`), `WorkingMemory`, bridge logs |

---

## Suggested next steps (when prioritized)

1. Define **falsifiable success criteria** (what to measure in simulation; what does **not** count as “consciousness”).
2. Decide **what is UX narrative only** vs **persistent internal state**.
3. Isolated **InternalMonologue** prototype read-only (no self-modifying ethics).
4. Ethics / legal review before any “opening” of normative closure.
