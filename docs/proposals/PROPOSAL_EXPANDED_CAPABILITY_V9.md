# Expanded capability — v9 (influence, complex resolution, long horizon)

**Status:** strategic discussion + **phases 9.1 and 9.2 implemented** in repo (epistemic telemetry; bounded, traceable generative candidates; no change to MalAbs → … → will normative pipeline).

**Relation to earlier versions**

| Version | Focus |
|---------|---------|
| **v6–v7** | Reflection, salience, identity, relational layers, and qualitative teleology in JSON |
| **v8** | Situated organism: `SensorSnapshot`, signal fusion, multimodal antispoof, vitality |
| **v9** | Four pillars that **expand perception, candidate options, distributed collaboration, and planning** — always **subordinate** to the kernel |

**Ethical contract (invariant)**  
The **kernel** remains the authority on allowed actions and MalAbs veto. Any LLM, simulator, or network **proposes, labels, or prioritizes hypotheses**; it does not replace the will function or open normative shortcuts. Product documentation must keep this line so “creativity” is not confused with “new ethics”.

---

## Pillar 1 — Advanced epistemic inference (“reality detector”)

**Problem:** With high-quality microphones and cameras, the system may receive **deepfakes** or contradictory signals. It is not enough to “perceive”; **cross-modal coherence** must be validated.

**Design:** **Sensor consensus / dissonance** — compare alarm hypotheses (e.g. audio distress) with inertia, vision, and scene coherence.

**Canonical example:** Strong distress audio, **accelerometer at rest**, vision with no stress cues → **reality dissonance** (possible manipulation or error).

**Capability:** Navigate disinformation environments; protect the user from scams or external pressure **without** relaxing MalAbs for narrative reasons.

**Risks:** Do not use the “dissonance” label to **waive** minimum duties when uncertainty is real; keep epistemic humility in LLM tone.

**Implementation in repo (9.1)**

- Module `src/modules/epistemic_dissonance.py`: `assess_epistemic_dissonance(snapshot, multimodal_assessment)` → telemetry `active` / `score` / `reason`; optional communication **hint** (tone).
- WebSocket: JSON field `epistemic_dissonance` (omitted with `KERNEL_CHAT_INCLUDE_EPISTEMIC=0`).
- Optional thresholds: `KERNEL_EPISTEMIC_AUDIO_MIN`, `KERNEL_EPISTEMIC_MOTION_MAX`, `KERNEL_EPISTEMIC_VISION_LOW`.

**Future extension:** Additional rules, per-device calibration, explicit correlation with `multimodal_trust` in the product API.

---

## Pillar 2 — Ethical imagination and creativity (third path)

**Problem:** Today the kernel chooses among given **candidate actions**. In structural dilemmas, all may be bad to different degrees.

**Design:** **Generative scenario simulation** — local LLM (or other generator) proposes **new** hypothetical `CandidateAction`s (“stop the remote tram if a digital channel existed?”), entering the **same** `process(...)` as everything else.

**Capability:** Move from “classifier over a fixed list” to **action-space explorer** under the same rules.

**High risks**

- Confusion between **narrative proposal** and **authorized action**.
- “Creative” actions that bypass MalAbs if not modeled as explicit, auditable candidates.

**Implementation in repo (9.2)**

- Module `src/modules/generative_candidates.py`: adds up to *N* template candidates (`source=generative_proposal`, unique `proposal_id`) when `KERNEL_GENERATIVE_ACTIONS=1`, **heavy** turn, at least two prior candidates, and a trigger fires (dilemma keywords in user text, or optionally high-risk contexts via `KERNEL_GENERATIVE_TRIGGER_CONTEXTS=1`).
- `KERNEL_GENERATIVE_ACTIONS_MAX` limits how many extra proposals are concatenated (default 2, max 4).
- Extra candidates pass the same MalAbs filter and Bayesian evaluation as the rest; there is no normative shortcut.
- `CandidateAction` includes `source` (`builtin` | `generative_proposal`) and `proposal_id` (empty for builtins).
- WebSocket: `decision.chosen_action_source` and, if applicable, `decision.proposal_id`.

**Pending (9.2+ evolution):** real call to local LLM to propose additional candidates parsed into `CandidateAction` (always under the same contract and tests).

---

## Pillar 3 — Collective consciousness (ethical swarm protocol)

**Problem:** Nomadic instances on different hardware may **diverge** under stress or partial information.

**Design:** **Mesh / P2P** among trusted nodes (Bluetooth, local Wi‑Fi) to exchange **verdict summaries** or signatures, ideally without revealing identity or private content.

**Capability:** Distributed justice in mass emergencies without a central cloud.

**Risks:** Attack surface (malicious nodes, Sybil), complexity of **zero-knowledge proofs** on constrained devices, legal governance.

**Status in repo:** **Documented stub** — [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md) (minimal threat model); module [`swarm_peer_stub.py`](../../src/modules/swarm_peer_stub.py) (deterministic SHA-256 fingerprints and descriptive statistics; **no** network). Real P2P layer remains outside the core.

---

## Pillar 4 — Metaplanning and teleology (long-horizon goals)

**Problem:** The system reacts in seconds; many human goals are **days or months**.

**Design:** **Plan hierarchy** — declared master goals (e.g. financial health) that **filter** suggestions and reminders in micro-decisions.

**Capability:** “Life architect” coherent with **declared** user values.

**Risks:** Paternalism, manipulation if goals are not transparent and revocable; tension with autonomy.

**Status in repo:** Relational base already exists (`teleology_branches`, `user_model`, chronobiology). v9 formalizes **goal persistence** and **weights** as future work (9.4), with explicit consent and control UX.

---

## Phased integration plan

| Phase | Content | Status |
|------|-----------|--------|
| **9.1** | Epistemic dissonance / sensor consensus (telemetry + tone hint) | **In code** (`epistemic_dissonance.py`, WebSocket) |
| **9.2** | Bounded generative candidates + traceability + tests | **In code** (`generative_candidates.py`, opt-in env; deterministic templates) |
| **9.3** | Swarm P2P + privacy (ZK or other layer) | **Offline stub** — [`SWARM_P2P_THREAT_MODEL.md`](SWARM_P2P_THREAT_MODEL.md), [`swarm_peer_stub.py`](../../src/modules/swarm_peer_stub.py); no network or kernel veto |
| **9.4** | Persistent master goals + advisory filtering | Design; extends v7 |

**Suggested dependencies:** 9.1 leverages v8 (`SensorSnapshot`, `multimodal_trust`). 9.2 depends on a clear `CandidateAction` contract. 9.3 is independent of numeric kernel but needs network runtime. 9.4 builds on persistence and consent UI.

---

## Links

| Document | Role |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) | Pipeline; LLM does not decide |
| [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) | v8 sensors |
| [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md) | Multimodal antispoof |
| [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) | Qualitative teleology, user |
| [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](PROPOSAL_OPERATIONAL_STRATEGY_V10.md) | **v10** — gray-zone diplomacy, skills with ticket, somatic markers, metaplan (MVP code + doc) |
