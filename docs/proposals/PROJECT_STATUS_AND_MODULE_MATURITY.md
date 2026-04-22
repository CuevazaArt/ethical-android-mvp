# Project status and module maturity

**Updated:** April 2026 · **Tests:** `pytest` collects **~640+** tests under `tests/` (run `pytest tests/ --collect-only` for the exact count).

This document summarizes **where** the Ethos Kernel MVP stands today and gives an honest read of **maturity** by area (it does not replace ADRs or `RUNTIME_CONTRACT.md`).

---

## 1. Where we are (summary)

| Dimension | Status |
|-------------|--------|
| **Ethical core** | **Distributed Tri-Lobe (V13):** Orchestrated by `CorpusCallosum` bus across 5 autonomous lobes (L0-L5). |
| **Real-time chat** | **Nomadic Autonomy (V13.1):** Zero-API voice responses (TTS) and proactive intents via MotivationEngine. |
| **Input trust** | Lexical + Semantic MalAbs (distributec); hardened vision (BGR to RGB) and Agility EMA smoothing. |
| **User model (ToM)** | Integrated into the Executive Lobe; checked against Identity Integrity for narrative coherence. |
| **Justice / DAO (demo)** | **Memory Lobe (L5):** Persistent DAO/Reputation audit ledger integrated into the nervous bus. |
| **Persistence** | Distributed biographic pruning and biographic identity snapshots. |
| **Operations** | `KERNEL_TRI_LOBE_ENABLED=1` for async distributed mode; `KERNEL_NOMAD_MODE=1` for field operation. |

**Takeaway:** the system has evolved from a monolithic research prototype into a **distributed, self-driven autonomous agent architecture** ready for nomadic field testing on mobile hardware.

---

## 2. Maturity legend

| Level | Meaning |
|-------|-------------|
| **Solid** | Covered by regression tests; clear usage contract in docs; main path stable. |
| **Demo** | Works for demos and development; needs environment or LLM tuning; do not promise “production” without a profile. |
| **Experimental** | Behind `KERNEL_*` or opt-in; API or heuristics may evolve. |
| **Stub / partial** | Narrative or API surface present; real physical or distributed integration out of scope. |

---

## 3. Maturity by area (modules and subsystems)

| Area | Files / entry | Maturity | Notes |
|------|----------------------|---------|--------|
| **Kernel orchestration** | `kernel.py` (`process`, `process_chat_turn`, `process_natural`) | **Solid** | Orchestrates the graph; chat and natural tests. |
| **MalAbs (text)** | `absolute_evil.py`, `input_trust.py` | **Solid** | Lists + normalization; dedicated tests. |
| **Semantic MalAbs** | `semantic_chat_gate.py`, `absolute_evil` layers | **Demo** | Depends on Ollama/embeddings; fallbacks documented. |
| **LLM perception** | `llm_layer.py`, `perception_schema.py` | **Solid** | Pydantic validation, coherence, local fallback. |
| **Mixture / buffer / poles** | `weighted_ethics_scorer.py`, `bayesian_engine.py` (compat), `buffer.py`, `ethical_poles.py`, `pole_linear.py` | **Solid** | Fixed weighted blend + bounded nudges (not full Bayes; ADR 0009); linear poles (ADR 0004). |
| **Reflection / salience / PAD** | `ethical_reflection.py`, `salience_map.py`, `pad_archetypes.py` | **Demo** | Read for audit and tone; do not block action. |
| **User model (ToM)** | `user_model.py` | **Demo** | Heuristics + tone; persisted in snapshot; see `USER_MODEL_ENRICHMENT.md`. |
| **Uchi–Soto** | `uchi_soto.py` | **Demo** | Phases 1–3: composite `tone_brief`, `set_profile_structured`, `ingest_turn_context` (EMA + decay), `RelationalTier`, `linked_peer_ids`, checkpoint; see [PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md](PROPOSAL_SOCIAL_ROSTER_HIERARCHICAL_RELATIONS.md). |
| **Multi-agent social roster** | `uchi_soto.py` (persisted) | **Demo** | Core roster in profiles + tiers; narrative extension in linked proposal. |
| **Judicial escalation** | `judicial_escalation.py` | **Demo** | Session, strikes, public views; mock DAO, no real network. |
| **Narrative memory / identity** | `narrative.py`, `narrative_identity.py` | **Solid** | Episodes and digest; checkpoints. |
| **Subjective time** | `subjective_time.py` | **Demo** | Continuity in snapshot; bounded effect. |
| **Chronobiology** | `subjective_time` + chat fields | **Demo** | Optional telemetry. |
| **Sensors / multimodal / vitality** | `sensor_contracts`, `multimodal_trust`, `vitality.py` | **Demo** | Fused signals; heuristic antispoof. |
| **Epistemic / reality / lighthouse** | `epistemic_dissonance.py`, `reality_verification.py` | **Experimental** | Tone and local KB; limits in docs. |
| **Generative candidates** | `generative_candidates.py` | **Experimental** | Traceable actions; MalAbs unchanged. |
| **Operational v10** | `metaplan_registry`, `somatic_markers`, `gray_zone_diplomacy` | **Experimental** | Flags; no policy veto. |
| **Mock DAO / hub / constitution** | `mock_dao.py`, `moral_hub`, constitution HTTP | **Demo** | State in JSON/SQLite per feature; hub-style audit. |
| **Persistence** | `persistence/schema.py`, `kernel_io.py`, `json_store.py` | **Solid** | Round-trip tested; v1→v3 migration. |
| **Chat server** | `chat_server.py` | **Solid** | Smoke + integration tests. |
| **Guardian Angel** | `guardian_mode.py` | **Experimental** | Opt-in; tone only. |
| **Psi sleep / genome** | `psi_sleep.py`, drift env | **Demo** | Drift limits tested where applicable. |

---

## 4. Known gaps (not forgotten)

1. **Configuration surface:** many `KERNEL_*`; operational maturity depends on **profiles** (`runtime_profiles.py`) and honest documentation.
2. **LLM ≠ guarantee:** model perception and text are **bounded inputs**, not ground truth.
3. **Governance:** DAO and tribunal in-repo are **mock / demo**, not real distributed consensus.
4. **Deployment security:** Fernet checkpoint, LAN bind, etc. are documented; “production” hardening remains a **separate roadmap** (`PRODUCTION_HARDENING_ROADMAP.md`).

---

## 5. References

- Strategy and risks: [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md)
- Decision chain: [CORE_DECISION_CHAIN.md](CORE_DECISION_CHAIN.md)
- Runtime contract: [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md)
- Input threat model: [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)
- User model enrichment: [USER_MODEL_ENRICHMENT.md](USER_MODEL_ENRICHMENT.md)
- Changelog: [CHANGELOG.md](../CHANGELOG.md)

---

*Orientation document; keep aligned with code changes in CHANGELOG and tests.*
