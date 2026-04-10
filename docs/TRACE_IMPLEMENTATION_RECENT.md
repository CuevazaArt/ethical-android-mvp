# Traceability: recent implementations (Guardian, v9, v10, V11 Phase 1)

This document **consolidates** components and concepts added in the recent work cycle, with **bibliographic support** in the repository format: numbered references per **[BIBLIOGRAPHY.md](../BIBLIOGRAPHY.md)** (index at the end of that file).

**Coherence:** None of these layers alter the normative pipeline **MalAbs → … → will**; they are telemetry, LLM tone, explicit candidates, or bounded signals, as documented in [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) and the linked PROPUESTA notes.

---

## Component → code → support

| Concept | Implementation (module / integration) | Bibliographic support (refs.) |
|---------|--------------------------------------|-------------------------------|
| **Guardian Angel mode** (opt-in protective tone) | `src/modules/guardian_mode.py`; `KERNEL_GUARDIAN_MODE`; `process_chat_turn` → `communicate` | AI in society and value alignment [15], [17]; human–agent interaction and trust [67], [69]. |
| **Epistemic dissonance / sensory consensus** (v9.1) | `src/modules/epistemic_dissonance.py`; after `multimodal_trust`; JSON `epistemic_dissonance` | Uncertainty and information [21]; causal reasoning / coherence across sources [24], [25]; sensors and estimation [61]; interpretability limits under contradictory signals [71]. |
| **Generative candidates** (“third way”, v9.2) | `src/modules/generative_candidates.py`; `CandidateAction.source` / `proposal_id`; `KERNEL_GENERATIVE_ACTIONS` | Empirical moral dilemmas and trade-offs [18]; rational agents and plan space [31]; fast vs deliberative modes [41]. |
| **Gray-zone diplomacy** (v10) | `src/modules/gray_zone_diplomacy.py`; hints in `weakness_line`; `KERNEL_GRAY_ZONE_DIPLOMACY` | Deliberation under cognitive tension [41]; discourse ethics and rational agreement [73]; explainability and transparency [15]. |
| **Skill-learning registry** (v10) | `src/modules/skill_learning_registry.py`; audit in `execute_sleep` | Governance and capability scope [74]; principle-based AI frameworks [15]; “constitutional” alignment and behavior bounds [90]. |
| **Somatic markers** (v10) | `src/modules/somatic_markers.py`; `apply_somatic_nudges` on `signals` | Somatic markers and emotion in decision [91]; cybernetics and sensor–attitude loop [59]; simple sensor vehicles [60]. |
| **Metaplan / master goals** (v10, session) | `src/modules/metaplan_registry.py`; optional hint to LLM | Persistent plans and intention [33]; agents and planning [31]. |
| **Multimodal antispoof** (v8 context) | `src/modules/multimodal_trust.py` (existing; v9.1 combines) | Same line as epistemic dissonance [21], [24], [61]. |
| **Judicial escalation / dossier → DAO audit** (V11 Phases 1–2) | `judicial_escalation.py` + `EscalationSessionTracker` on kernel; strike gating; `MockDAO.register_escalation_case`; WebSocket `escalate_to_dao` | Governance, audit trails, institutional trust [15], [74]; discourse ethics [73]. |

---

## Related design documents

| Document | Contents |
|----------|----------|
| [discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md](discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md) | Product and contract — Guardian Angel |
| [discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | v9 pillars (epistemic, generative, swarm, metaplanning) |
| [discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md) | Diplomacy, skills, soma, operational metaplan (MVP) |
| [discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) | V11 governance: escalation phases, experimental topics (sanctions, P2P, ZK) |
| [discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md](discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md) | V12 vision: etosocial hub / hybrid institutions (no code) |

---

## Next development session (proposed plan)

Suggested priorities aligned with the repo and PROPUESTA notes:

1. **Persist goals and markers** — Extend `KernelSnapshotV1` or an auxiliary field for `MetaplanRegistry` and, if applicable, `SomaticMarkerStore` weights; checkpoint round-trip tests. *Support:* narrative continuity [40], [97], [98]; persistence [104].

2. **v9.2+ generative with local LLM** — Parse candidates from model JSON under `KERNEL_GENERATIVE_LLM=1`; MalAbs property tests. *Support:* [81]–[83], [31].

3. **v9.4 metaplanning** — Explicit advisory filtering vs `MasterGoal` in `drive_intents` or extra hints; documented consent. *Support:* [33], [17], [15].

4. **v9.3 swarm** — Only with a threat model; prototype outside the core. *Support:* [52], [57], [58].

5. **Guardian Angel (product)** — Routines and UI; no change to ethical veto. *Support:* [67]–[70], [15].

---

*Ex Machina Foundation — implementation traceability; align with [BIBLIOGRAPHY.md](../BIBLIOGRAPHY.md) for full academic citations.*
