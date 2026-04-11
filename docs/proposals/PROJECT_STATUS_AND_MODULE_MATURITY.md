# Project status and module maturity

**Update:** April 2026 · **Tests:** `pytest` collects **411** tests in the `tests/` tree.

This document summarizes **where** the Ethos Kernel MVP is today and an honest reading of **maturity** by area (does not replace ADRs or `RUNTIME_CONTRACT.md`).

---

## 1. Where we are (synthesis)

| Dimension | Status |
|-------------|--------|
| **Ethical core** | MalAbs → buffer → Bayes → poles → will pipeline; decisions with invariant tests. |
| **Real-time chat** | WebSocket `/ws/chat`, MalAbs text + validated perception (Pydantic/coherence), advisory layers under flags. |
| **Input trust** | Lexical MalAbs first; optional semantic layers (embeddings / LLM arbiter); bounded perception and field coherence. |
| **User model (light ToM)** | Phases A–C implemented: cognitive patterns, risk band, judicial phase for tone, persistence in snapshot. |
| **Justice / DAO (demo)** | Per-session escalation, mock dossier, optional simulated tribunal; **off-chain** governance in this repo. |
| **Persistence** | `KernelSnapshotV1` (schema v3 with new backward-compatible fields), JSON optionally Fernet. |
| **Operation** | Many `KERNEL_*` variables; nominal profiles in `runtime_profiles.py`; policy in `KERNEL_ENV_POLICY.md`. |

**Reading:** the product is a **research and demonstration runtime** with auditable traces; it is not a content moderation product nor a legal certification system.

---

## 2. Maturity legend

| Level | Meaning |
|-------|---------|
| **Solid** | Covered by regression tests; clear usage contract in docs; stable main path. |
| **Demo** | Functional for demos and development; requires environment tuning or LLM tuning; do not promise "production" without profile. |
| **Experimental** | Behind `KERNEL_*` or opt-in; API or heuristics may evolve. |
| **Stub / partial** | Narrative surface or API present; real physical or distributed integration out of scope. |

---

## 3. Maturity by area (modules and subsystems)

| Area | Files / entry | Maturity | Notes |
|------|----------------------|---------|--------|
| **Kernel orchestration** | `kernel.py` (`process`, `process_chat_turn`, `process_natural`) | **Solid** | Orchestrates the graph; chat and natural tests. |
| **MalAbs (text)** | `absolute_evil.py`, `input_trust.py` | **Solid** | List + normalization; dedicated tests. |
| **Semantic MalAbs** | `semantic_chat_gate.py`, `absolute_evil` layers | **Demo** | Depends on Ollama/embeddings; documented fallbacks. |
| **LLM perception** | `llm_layer.py`, `perception_schema.py` | **Solid** | Pydantic validation, coherence, local fallback. |
| **Bayes / buffer / poles** | `bayesian_engine.py`, `buffer.py`, `ethical_poles.py`, `pole_linear.py` | **Solid** | Decision core with tests; configurable linear poles (ADR 0004). |
| **Reflection / salience / PAD** | `ethical_reflection.py`, `salience_map.py`, `pad_archetypes.py` | **Demo** | Read for audit and tone; does not veto action. |
| **User model (ToM)** | `user_model.py` | **Demo** | Heuristics + tone; persisted in snapshot; see `USER_MODEL_ENRICHMENT.md`. |
| **Uchi–Soto** | `uchi_soto.py` | **Demo** | Phases 1–3: composed `tone_brief`, `set_profile_structured`, `ingest_turn_context` (EMA + forgetting), `RelationalTier`, `linked_peer_ids`, checkpoint; see [PROPUESTA_ROSTER…](PROPOSAL_SOCIAL_ROSTER_AND_HIERARCHICAL_RELATIONS.md). |
| **Multi-agent social roster** | `uchi_soto.py` (persisted) | **Demo** | Core roster in profiles + tiers; narrative extension in linked proposal. |
| **Judicial escalation** | `judicial_escalation.py` | **Demo** | Per-session, strikes, public views; mock DAO, no real network. |
| **Narrative memory / identity** | `narrative.py`, `narrative_identity.py` | **Solid** | Episodes and digest; checkpoints. |
| **Subjective time** | `subjective_time.py` | **Demo** | Continuity in snapshot; bounded effect. |
| **Chronobiology** | `subjective_time` + chat fields | **Demo** | Optional telemetry. |
| **Sensors / multimodal / vitality** | `sensor_contracts`, `multimodal_trust`, `vitality.py` | **Demo** | Fused signals; heuristic antispoof. |
| **Epistemic / reality / lighthouse** | `epistemic_dissonance.py`, `reality_verification.py` | **Experimental** | Tone and local KB; limits in docs. |
| **Generative candidates** | `generative_candidates.py` | **Experimental** | Traceable actions; same MalAbs. |
| **v10 operational** | `metaplan_registry`, `somatic_markers`, `gray_zone_diplomacy` | **Experimental** | Flags; no policy veto. |
| **DAO mock / hub / constitution** | `mock_dao.py`, `moral_hub`, `constitution` HTTP | **Demo** | State in JSON/SQLite by feature; hub-type audit. |
| **Persistence** | `persistence/schema.py`, `kernel_io.py`, `json_store.py` | **Solid** | Round-trip tested; v1→v3 migration. |
| **Chat server** | `chat_server.py` | **Solid** | Smoke + integration tests. |
| **Guardian Angel** | `guardian_mode.py` | **Experimental** | Opt-in; tone only. |
| **Psi sleep / genome** | `psi_sleep.py`, drift env | **Demo** | Drift limits tested where applicable. |

---

## 4. Known gaps (not forgotten)

1. **Configuration surface:** many `KERNEL_*`; operational maturity depends on **profiles** (`runtime_profiles.py`) and honest documentation.
2. **LLM ≠ guarantee:** perception and model text are **bounded inputs**, not ground truth.
3. **Governance:** DAO and tribunal in repo are **mock / demo**, not real distributed consensus.
4. **Deployment security:** checkpoint Fernet, bind LAN, etc. are documented; "production" hardening follows **separate roadmap** (`PRODUCTION_HARDENING_ROADMAP.md`).

---

## 5. References

- Strategy and risks: [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md)
- Decision chain: [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md)
- Runtime contract: [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)
- Input threat model: [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)
- User model enrichment: [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md)
- Changelog: [CHANGELOG.md](../CHANGELOG.md)

---

*Orientation document; align with code changes in CHANGELOG and tests.*
