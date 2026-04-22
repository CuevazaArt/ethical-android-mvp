# Social roster, relational hierarchy, and domestic / intimate dialogue — proposal

**Status:** design + **implementation** (April 2026) — Phases 1–3 in `uchi_soto.py` (persisted profiles, `tone_brief`, structured Phase 2, Phase 3: multimodal EMA toward `sensor_trust_ema`, forget buffer, `RelationalTier` + explicit promotion, `linked_peer_ids`).  
**Scope:** extend narrative and identity with a **collection of people** (stable `agent_id`, e.g. session user, guest, anonymous id), **profiled** by accumulated experience, interaction, sensory signals, and **Uchi–Soto circle**, without replacing MalAbs, buffer, Bayes, or will.

**Relationship to existing code:** `UchiSotoModule` (`src/modules/uchi_soto.py`) already keeps `InteractionProfile` per agent and `TrustCircle`; `UserModelTracker` models the session’s **current** interlocutor; `NarrativeIdentityTracker` models the **android’s** identity. This proposal describes the persistent **multi-agent roster layer** and **tone policies** by closeness.

---

## 1. Goals

1. Record a **relationship tree or ladder** (not only per-turn classification): from **strangers in a fast forget-buffer** to **unforgettable figures** (e.g. primary owner, close family, trusted friends), with explicit promotion and demotion rules.
2. Allow **storing relevant data** about people of **highest narrative interest** (preferences, shared domestic context, routines, agreed intimacy boundaries — always **privacy and consent** by design) so that, **over time**, the system can **increase domestic and intimate dialogue capacity** according to the **closeness circle**, without confusing “intimate” with relaxing ethics.
3. Expose **advisory conduct tuning** (tone, explanatory depth, pacing, lexical familiarity) **derived** from relational tier and stored data, with **documented secondary implications** (privacy, audit, over-familiarity risk).

---

## 2. Design principles

| Principle | Content |
|-----------|---------|
| **Ethics first** | MalAbs and policy veto are not disabled by closeness; the roster is **not** a back door. |
| **Consent** | Moves to “intimate” or “owner” tiers should anchor to **explicit rituals** (mock DAO, env, UI), not chat frequency alone. |
| **Data minimization** | By default: aggregates and episode references; raw user text is **not** required to tier up. |
| **Operational transparency** | What is stored and for which tier must be **inspectable** (JSON, conduct-guide export, checkpoint). |

---

## 3. Conceptual model

### 3.1 Per-person input (`agent_id`)

- **Relational tier** (ordinal): e.g. `ephemeral` → `stranger_stable` → `acquaintance` → `trusted_uchi` → `inner_circle` → `owner_primary` (or explicit mapping to `TrustCircle` in `uchi_soto.py`).
- **Aggregate axes:** interaction mass (turns/time window), EMA valence (positive/negative), sensor coherence (multimodal), shared episodic salience.
- **Fast forget-buffer:** low-weight entries without relevance decay by TTL or inactivity; **purged** or compressed to a scalar summary.
- **Unforgettable:** normative “pin” or hard rules (e.g. `dao_validated`, `KERNEL_*`) so they do not depend only on frequency.

### 3.2 Data for people of highest interest

For high tiers (and only where policy and consent allow), the system should **register structured fields** (not unbounded free dump), for example:

- **Domestic:** usual room/space, stably mentioned routines, tone preferences (formal/warm).
- **Relational:** accepted name or alias, optional links (`linked_to` for family narrative).
- **Boundaries:** topics marked do-not-address or confirm-first (tag list, no unnecessary sensitive text).
- **Sensory:** context-trust EMA (no audio/video recording; only **already aggregated** v8 pipeline signals).

**End goal:** enrich **domestic and intimate dialogue** (shared vocabulary, continuity, warmth proportional to circle) **without** increasing default ethical risk: intimacy is **style and context**, not a security bypass.

### 3.3 Hierarchy tree

A full genealogy graph is not required initially: a **total order** on tiers plus **optional edges** (“related to X”) for narrative suffices. The **view** to the LLM can be an ordered list + tone rules per level.

---

## 4. Technical integration (suggested roadmap)

| Phase | Content |
|-------|---------|
| **Phase 1** | **Done:** extended `UchiSotoModule` — `agent_id` → profile + `trust_score` + familiarity blend; base `tone_brief` by circle; `register_result`; `uchi_soto_profiles` in snapshot. |
| **Phase 2** | **Done:** structured fields on `InteractionProfile` (`display_alias`, `tone_preference`, `domestic_tags`, `topic_avoid_tags`, `sensor_trust_ema`, `linked_to_agent_id`); `_compose_tone_brief` uses them in close/inner uchi (and tone preference in broad uchi); `set_profile_structured()`; same snapshot serialization. |
| **Phase 3** | **Done:** `ingest_turn_context` — EMA on `sensor_trust_ema` (signals + `place_trust` + multimodal state); `KERNEL_UCHI_*` for α and TTL; forget buffer (cold `ephemeral` / `stranger_stable`); `RelationalTier` with bounded autopromotion and `set_relational_tier_explicit` / `tier_pinned`; `linked_peer_ids` in `tone_brief`. |

**Hook points:** `EthicalKernel.process` / `process_chat_turn` (`agent_id` already exists); `identity` / monologue; `premise_advisory` and MalAbs **unchanged** in veto logic.

---

## 5. Secondary implications

1. **Privacy:** roster and domestic fields in optional encrypted checkpoint (Fernet); conduct-guide export with redaction.
2. **Relational security:** manipulation or sustained hostility can **block** tier promotion despite high interaction.
3. **Product:** real multi-user may need **multiple sessions** or agent picker on client; one WebSocket = one active `agent_id` is the current pattern.
4. **Expectation:** “intimate dialogue” **increases warmth and continuity** in tone; it does **not** promise fulfilling requests unauthorized by the core.

---

## 6. Cross-references

- [PROPOSAL_RELATIONAL_EVOLUTION_V7.md](PROPOSAL_RELATIONAL_EVOLUTION_V7.md) — light ToM and session; `user_model.py`.
- [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md) — per-turn enrichment (cognitive pattern, risk, judicial).
- [PROJECT_STATUS_AND_MODULE_MATURITY.md](PROJECT_STATUS_AND_MODULE_MATURITY.md) — current MVP maturity.
- `src/modules/uchi_soto.py` — `InteractionProfile`, `TrustCircle` — base to extend.

---

*Ex Machina Foundation — design document; align implementation with CHANGELOG and tests.*
