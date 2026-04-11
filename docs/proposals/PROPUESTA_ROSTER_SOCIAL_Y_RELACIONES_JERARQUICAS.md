# Social roster, relational hierarchy, and domestic / intimate dialogue — proposal

**Status:** design + **partial implementation** (April 2026) — Phases 1–2 in `uchi_soto.py` (persisted profiles, `tone_brief`, Phase 2 structured fields); Phase 3 pending (fine multimodal EMA, rich `linked_to`).  
**Scope:** extend narrative and identity with a **collection of people** (by stable `agent_id`, e.g. session user, guest, anonymous identifier), **profiled** by accumulated experiences, interaction, sensory signals, and **Uchi–Soto circle**, without replacing MalAbs, buffer, Bayes, or will.

**Relationship with existing code:** `UchiSotoModule` (`src/modules/uchi_soto.py`) already maintains `InteractionProfile` per agent and `TrustCircle`; `UserModelTracker` models the **current** session interlocutor; `NarrativeIdentityTracker` models the **android's identity**. This proposal describes the persistent **multi-agent roster layer** and the **tone policies** by proximity.

---

## 1. Objective

1. Register a **tree or ranking of relationships** (not just instantaneous classification in a turn): from **unknowns in a fast-forgetting buffer** to **unforgettable figures** (e.g. primary owner, close family, trusted friends), with explicit promotion and demotion rules.
2. Allow **storing relevant data** about people of **greatest interest** to the narrative (preferences, shared domestic contexts, routines, agreed intimacy limits — always with **privacy and consent** by design), so that **in the long term** the system can **increase domestic and intimate dialogue capability** according to the **proximity circle**, without confusing "intimate" with relaxing ethics.
3. Expose **advisory behavior-adjustment functions** (tone, explanatory depth, rhythm, lexical familiarity) **derived** from the relational tier and stored data, with **secondary implications** documented (privacy, auditing, risk of over-familiarity).

---

## 2. Design principles

| Principle | Content |
|-----------|-----------|
| **Ethics first** | MalAbs and policy veto are not deactivated by proximity; the roster is **not** a back door. |
| **Consent** | Promotions to "intimate" or "owner" tiers must be anchorable to **explicit rituals** (mock DAO, env, UI), not just chat frequency. |
| **Data minimization** | By default: aggregates and references to episodes; raw user text is **not** required for tier promotion. |
| **Operational transparency** | What data is stored and for which tier must be **inspectable** (JSON, export conduct guide, checkpoint). |

---

## 3. Conceptual model

### 3.1 Entry per person (`agent_id`)

- **Relational tier** (ordinal): e.g. `ephemeral` → `stranger_stable` → `acquaintance` → `trusted_uchi` → `inner_circle` → `owner_primary` (or explicit mapping to `TrustCircle` in `uchi_soto.py`).
- **Aggregated axes:** interaction mass (turns/time window), EMA valence (positive/negative), sensory coherence (multimodal), shared episodic salience.
- **Fast-forgetting buffer:** entries with low weight and no relevance signal decay by TTL or inactivity; they are **purged** or compressed to a scalar summary.
- **Unforgettables:** normative "pin" or hard rules (e.g. `dao_validated`, `KERNEL_*`) so they do not depend solely on the frequency algorithm.

### 3.2 Relevant data for people of greatest interest

For high tiers (and only where policy and consent allow), the system should be able to **record structured fields** (not a boundless free dump), for example:

- **Domestic:** usual room/space, stably mentioned routines, tone preferences (formal/warm).
- **Relational:** accepted name or alias, optional links (`linked_to` for family narrative).
- **Limits:** topics marked as not to address or only with confirmation (tag list, no unnecessarily sensitive text).
- **Sensory:** context trust EMA (no audio/video recording; only **already-aggregated signals** from the v8 pipeline).

**Ultimate objective:** enrich the **domestic and intimate dialogue layer** (shared vocabulary, continuity, warmth proportional to the circle) **without** increasing ethical risk by default: intimacy is **style and context**, not a security bypass.

### 3.3 Hierarchical tree

A complete genealogical graph is not required at the start: a **total tier order** plus **optional edges** ("related to X") for narrative suffices. The **LLM view** can be an ordered list + tone rules per level.

---

## 4. Technical integration (suggested roadmap)

| Phase | Content |
|------|-----------|
| **Phase 1** | **Done:** `UchiSotoModule` extended — `agent_id` → profile + `trust_score` + familiarity blend; base `tone_brief` by circle; `register_result`; persistence of `uchi_soto_profiles` in snapshot. |
| **Phase 2** | **Done:** structured fields in `InteractionProfile` (`display_alias`, `tone_preference`, `domestic_tags`, `topic_avoid_tags`, `sensor_trust_ema`, `linked_to_agent_id`); `_compose_tone_brief` incorporates them in close uchi/core (and tone preference in broad uchi); `set_profile_structured()`; serialization in the same snapshot. |
| **Phase 3** | Pending: **automatic** multimodal EMA toward `sensor_trust_ema`; decay / forgetting buffer; explicit tier promotion as full roster. |

**Hook points:** `EthicalKernel.process` / `process_chat_turn` (`agent_id` already exists); `identity` / monologue; `premise_advisory` and MalAbs **unchanged** in veto logic.

---

## 5. Secondary implications

1. **Privacy:** roster and domestic fields in optionally encrypted checkpoint (Fernet); conduct guide export with wording.
2. **Relational security:** sustained manipulation or hostility can **block** tier promotion even with high interaction volume.
3. **Product:** real multi-user may require **multiple sessions** or an agent selector in the client; one WebSocket = one active `agent_id` is the current pattern.
4. **Expectation:** "intimate dialogue" **increases warmth and continuity** in tone; it **does not** promise fulfillment of requests unauthorized by the core.

---

## 6. Cross-references

- [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) — lightweight ToM and session; `user_model.py`.
- [USER_MODEL_ENRICHMENT.md](../USER_MODEL_ENRICHMENT.md) — per-turn enrichment (cognitive pattern, risk, judicial).
- [PROJECT_STATUS_AND_MODULE_MATURITY.md](../PROJECT_STATUS_AND_MODULE_MATURITY.md) — current MVP maturity.
- `src/modules/uchi_soto.py` — `InteractionProfile`, `TrustCircle` — base to extend.

---

*Ex Machina Foundation — design document; align implementation with CHANGELOG and tests.*
