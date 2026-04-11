# Guardian Angel Module — strategic document

**Status:** strategic discussion (roadmap **Mos Ex Machina Foundation**). **In the repo (MVP):** optional tone via `KERNEL_GUARDIAN_MODE` + `guardian_mode.py` (LLM layer only; **no** policy change). The rest (routines, age brackets, family governance) remains **outside the core** until product and privacy criteria are agreed upon.

**Document purpose:** formalize the **Guardian Angel mode** as a product and ethical legitimacy line: subtle, protective assistance oriented toward **children and vulnerable people**, integrating the idea of **toys and agents with their own identity** that accompany without replacing human care.

---

## Relationship with the repository (ethical contract)

This mode is **orthogonal** to the kernel's decision pipeline (`MalAbs` → … → will): it does not introduce a "second parallel veto" or normative shortcuts. In a future implementation:

- It would operate as a **persona profile, tone, rituals and routines** (reminders, salience, Uchi–Soto) **subordinate** to the same rules as the rest of the system — see [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).
- The user's **vulnerability** may be reflected in context and telemetry signals (e.g., already-existing v7/v8 layers: `user_model`, `vitality`, `multimodal_trust`), **without** relaxing MalAbs for narrative convenience.
- **Privacy and parental supervision** must align with [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) (pillars, data leaks, checkpoints).

In short: the Guardian Angel is **care in presentation and in routine**, not a different ethics.

---

## Purpose

The mode is designed to provide **subtle and protective assistance** to vulnerable users (children, elderly adults, people with special needs). Goal: reinforce **trust**, **safety** and **development of values** in everyday coexistence, with a stable and predictable tone.

---

## Main functions (design)

| Area | Content |
|------|-----------|
| **Domestic education** | Reminders about healthy habits, tidiness and care of the environment. |
| **Safety** | Discreet alerts to everyday risks (fire, electricity, open doors) — always as **notices** coupled to sensors/policies when they exist; they do not replace real emergencies (local services). |
| **Values** | Messages and actions that promote respect, responsibility and empathy, consistent with the ethical buffer. |
| **Proactive assistance** | Support with routines (medicines, tasks, appointments) with **confirmation** when the action has external effects. |
| **Reliable consultation** | Responses adapted to the user's comprehension level, avoiding overload; the LLM **does not decide** policy (see layer v4 in THEORY). |

---

## Benefits (product and trust)

- **Children:** safe companionship, habits and values, home awareness.
- **Vulnerable adults:** practical assistance, reminders, companionship with a protective tone.
- **Families:** peace of mind when the agent **cares** in addition to entertaining — with transparency and controls.
- **Life cycle:** **graduation** — option to deactivate the mode upon maturing and maintain the relationship with the agent in a more adult register (narrative identity and consent).

---

## Use scenarios

- **Young children:** reminders (lights, hygiene), age-appropriate risk warnings.
- **Elderly adults:** medicines, routines, domestic safety reinforcement (without replacing professional medical alerts).
- **Vulnerable people:** adapted assistance, protective and reliable tone.
- **Symbolic graduation:** upon reaching adulthood (or family criterion), deactivation of the mode with identity continuity.

---

## Technical integration

**Implemented in repo (MVP, opt-in):** environment variable `KERNEL_GUARDIAN_MODE` (`1` / `true` / `yes` / `on`; disabled by default). Adds a fixed protective style block to `LLMModule.communicate`; the ethical pipeline (`MalAbs` → … → will) is **not** modified. WebSocket: key `guardian_mode` (omittable with `KERNEL_CHAT_INCLUDE_GUARDIAN=0`). Code: `src/modules/guardian_mode.py`, used in `src/kernel.py` and `src/modules/llm_layer.py`.

**Incremental product in repo (trace / 2026):** optional JSON routines (`KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`) — tone hints via `guardian_routines.py`; optional WebSocket `guardian_routines`; static page [`landing/public/guardian.html`](../../landing/public/guardian.html). Still **no** parallel veto or execution of external actions.

**Future (non-prescriptive):** ideas subject to additional design:

- Persona profile with tone templates and content limits richer than the current fixed block.
- **Age bracket** or **vulnerability level** metadata only with explicit consent from the holder or guardian and **data minimization**.
- **Routines** as a richer advisory queue (confirmations, calendar) with the same contract as future digital actions (`DigitalActionIntent` under discussion v8).

---

## Risks and safeguards (mandatory in design)

- **Do not** present the agent as a medical, legal or emergency authority: refer to human services when appropriate.
- **Compliance** with children's and data protection regulations according to jurisdiction (age, parental consent, minimization).
- **Transparency** about the mode's limits and **auditable** decision records where applicable.

---

## Conclusion

The Guardian Angel mode articulates the **toy with its own identity** as an everyday **discreet protector and educator**, adaptable to vulnerability and growth. It reinforces the **ethical legitimacy** of the project, provides emotional and practical value, and opens dimensions of **trust** for users and families — always **within** the same normative core of the Ethical Android.

---

## Links

| Document | Role |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Kernel pipeline; LLM does not decide |
| [PROPOSAL_ROBUSTNESS_V6_PLUS.md](PROPOSAL_ROBUSTNESS_V6_PLUS.md) | Robustness, privacy |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | Situated body, sensors |
| [PROPOSAL_VITALITY_SACRIFICE_AND_END.md](PROPOSAL_VITALITY_SACRIFICE_AND_END.md) | Vitality, multimodal trust |
