# Guardian Angel module — strategic document

**Status:** strategic discussion (roadmap **Mos Ex Machina Foundation**). **In the repo (MVP):** optional tone via `KERNEL_GUARDIAN_MODE` + `guardian_mode.py` (LLM layer only; **no** policy change). The rest (routines, age bands, family governance) remains **outside the core** until product and privacy criteria are agreed.

**Purpose of this document:** formalize **Guardian Angel mode** as a product line and ethical legitimacy: subtle, protective assistance oriented to **children and vulnerable people**, integrating the idea of **toys and agents with their own identity** that accompany without replacing human care.

---

## Relation to the repository (ethical contract)

This mode is **orthogonal** to the kernel decision pipeline (`MalAbs` → … → will): it does not introduce a parallel “second veto” or normative shortcuts. In a future implementation:

- It would operate as **persona profile, tone, rituals, and routines** (reminders, salience, Uchi–Soto) **subordinate** to the same rules as the rest of the system — see [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md).
- **User vulnerability** may be reflected in context signals and telemetry (e.g. existing v7/v8 layers: `user_model`, `vitality`, `multimodal_trust`), **without** relaxing MalAbs for narrative convenience.
- **Privacy and parental supervision** must align with [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) (pillars, data leaks, checkpoints).

In sum: Guardian Angel is **care in presentation and routine**, not a different ethics.

---

## Purpose

The mode is designed to provide **subtle, protective assistance** to vulnerable users (children, older adults, people with special needs). Objective: reinforce **trust**, **safety**, and **value development** in daily life, with a stable, predictable tone.

---

## Main functions (design)

| Area | Content |
|------|-----------|
| **Home education** | Reminders about healthy habits, tidiness, and care of surroundings. |
| **Safety** | Discrete alerts for everyday risks (fire, electricity, open doors) — always as **warnings** tied to sensors/policies when they exist; they do not replace real emergencies (local services). |
| **Values** | Messages and actions that foster respect, responsibility, and empathy, consistent with the ethical buffer. |
| **Proactive assistance** | Support in routines (medicine, tasks, appointments) with **confirmation** when the action has external effects. |
| **Trusted consultation** | Responses adapted to comprehension level, avoiding overload; the LLM **does not decide** policy (see v4 layer in THEORY). |

---

## Benefits (product and trust)

- **Children:** safe accompaniment, habits and values, home awareness.
- **Vulnerable adults:** practical assistance, reminders, companionship with a protective tone.
- **Families:** peace of mind when the agent **cares** as well as entertains — with transparency and controls.
- **Lifecycle:** **graduation** — option to turn off the mode when maturing and keep the relationship with the agent in a more adult register (narrative identity and consent).

---

## Usage scenarios

- **Young children:** reminders (lights, hygiene), age-appropriate risk warnings.
- **Older adults:** medicine, routines, reinforcement of home safety (not a substitute for professional medical alerts).
- **Vulnerable people:** adapted assistance, protective and trustworthy tone.
- **Symbolic graduation:** on reaching adulthood (or family criterion), mode off with identity continuity.

---

## Technical integration

**Implemented in repo (MVP, opt-in):** environment variable `KERNEL_GUARDIAN_MODE` (`1` / `true` / `yes` / `on`; default off). Adds a fixed protective style block to `LLMModule.communicate`; ethical pipeline (`MalAbs` → … → will) **is not** modified. WebSocket: `guardian_mode` key (omitted with `KERNEL_CHAT_INCLUDE_GUARDIAN=0`). Code: `src/modules/guardian_mode.py`, use in `src/kernel.py` and `src/modules/llm_layer.py`.

**Incremental product in repo (trace / 2026):** optional JSON routines (`KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`) — tone hints via `guardian_routines.py`; optional WebSocket `guardian_routines`. Still **no** parallel veto or external action execution.

**Future (non-prescriptive):** ideas subject to further design:

- Persona profile with richer tone templates and content limits than the current fixed block.
- **Age band** or **vulnerability level** metadata only with explicit consent from owner or guardian and **data minimization**.
- **Routines** as a richer advisory queue (confirmations, calendar) with the same contract as future digital actions (`DigitalActionIntent` in v8 discussion).

---

## Risks and safeguards (mandatory in design)

- **Do not** present the agent as medical, legal, or emergency authority: refer to human services when appropriate.
- **Compliance** with child and data-protection law by jurisdiction (age, parental consent, minimization).
- **Transparency** about mode limits and **auditable** decision logging where applicable.

---

## Conclusion

Guardian Angel mode articulates the **toy with its own identity** as a **discreet, everyday educator and protector**, adaptable to vulnerability and growth. It reinforces the project’s **ethical legitimacy**, adds emotional and practical value, and opens **trust** dimensions for users and families — always **within** the same normative core of the Ethical Android.

---

## Links

| Document | Role |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) | Kernel pipeline; LLM does not decide |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Robustness, privacy |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | Situated body, sensors |
| [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md) | Vitality, multimodal trust |
