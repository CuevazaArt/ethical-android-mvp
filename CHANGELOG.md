# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

## Phase 2 spike — `KernelEventBus` (ADR 0006) — April 2026

- **[ADR 0006](docs/adr/0006-phase2-core-boundary-and-event-bus.md):** incremental Phase 2 seam — optional sync in-process event bus (`KERNEL_EVENT_BUS`).
- **`src/modules/kernel_event_bus.py`:** `kernel.decision`, `kernel.episode_registered`; handlers are best-effort (exceptions logged).
- **`EthicalKernel`:** `event_bus`, `subscribe_kernel_event`, emits on every `process()` outcome and after episode registration.
- **Proposal:** [`docs/proposals/PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md`](docs/proposals/PROPOSAL_PHASE2_CORE_EXTENSIONS_AND_EVENT_BUS.md); **tests:** [`tests/test_kernel_event_bus.py`](tests/test_kernel_event_bus.py); **profile:** `phase2_event_bus_lab` in [`src/runtime_profiles.py`](src/runtime_profiles.py).
- **Docs:** [`CORE_DECISION_CHAIN.md`](docs/proposals/CORE_DECISION_CHAIN.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md), [`README.md`](README.md).

## Runtime profile `perception_hardening_lab` — April 2026

- **[`src/runtime_profiles.py`](src/runtime_profiles.py):** nominal **`perception_hardening_lab`** bundle (light risk + cross-check + uncertainty→delib + parse fail-local + `KERNEL_CHAT_INCLUDE_LIGHT_RISK`).
- **Tests:** [`tests/test_runtime_profiles.py`](tests/test_runtime_profiles.py) — key assertions + WebSocket `light_risk_tier` check.
- **Docs:** [`ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md) §4 table, [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) intro, [`README.md`](README.md).

## Hardening Fase 1 — parse contract, light risk tier, cross-check — April 2026

- **`perception_schema`:** `parse_perception_llm_raw_response`, `PerceptionJsonParseResult`, `parse_issues` / `cross_check_*` on `PerceptionCoercionReport`, `merge_parse_issues_into_perception`, `perception_report_from_dict`.
- **`llm_layer.LLMModule.perceive`:** structured parse + stable issue codes; optional **`KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`**.
- **`light_risk_classifier.py`:** offline **low/medium/high** tier (`KERNEL_LIGHT_RISK_CLASSIFIER`).
- **`perception_cross_check.py`:** lexical vs numeric mismatch (`KERNEL_PERCEPTION_CROSS_CHECK`, tunables `KERNEL_CROSS_CHECK_*`).
- **`EthicalKernel`:** runs tier + cross-check after perceive in `process_chat_turn` / `process_natural`; **`_last_light_risk_tier`**.
- **`chat_server`:** optional **`KERNEL_CHAT_INCLUDE_LIGHT_RISK`** → JSON `light_risk_tier`.
- **Tests:** `test_perception_parse_contract.py`, `test_light_risk_classifier.py`, `test_perception_cross_check.py`.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md), README operator table.

## Perception uncertainty → deliberation (opt-in) — April 2026

- **`EthicalKernel.process`:** optional `perception_coercion_uncertainty`; when **`KERNEL_PERCEPTION_UNCERTAINTY_DELIB=1`** and uncertainty ≥ **`KERNEL_PERCEPTION_UNCERTAINTY_MIN`** (default `0.35`), upgrades **`D_fast` → `D_delib`**.
- **`process_chat_turn` / `process_natural`:** pass uncertainty from `LLMPerception.coercion_report` when present.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md), README operator table; **tests:** [`tests/test_perception_uncertainty_delib.py`](tests/test_perception_uncertainty_delib.py).

## Packaging, perception diagnostics, episodic Bayes tests — April 2026

- **[`pyproject.toml`](pyproject.toml):** core dependency **`pydantic`** (matches [`requirements.txt`](requirements.txt)); description updated for editable install.
- **[`src/modules/perception_schema.py`](src/modules/perception_schema.py):** `PerceptionCoercionReport` + optional `report=` on `validate_perception_dict`; bounded **uncertainty** score for coerced / defaulted LLM JSON.
- **[`src/modules/llm_layer.py`](src/modules/llm_layer.py):** `LLMPerception.coercion_report`; `perception_from_llm_json(..., record_coercion=...)`; local heuristics omit the report.
- **[`src/chat_server.py`](src/chat_server.py):** JSON `perception.coercion_report` when present.
- **Tests:** [`tests/test_perception_coercion_report.py`](tests/test_perception_coercion_report.py), [`tests/test_packaging_metadata.py`](tests/test_packaging_metadata.py); extra episodic-weight cases in [`tests/test_bayesian_episodic_weights.py`](tests/test_bayesian_episodic_weights.py).
- **Docs:** [`docs/proposals/CRITIQUE_ROADMAP_ISSUES.md`](docs/proposals/CRITIQUE_ROADMAP_ISSUES.md) — fixed `UNIVERSAL_ETHOS_AND_HUB` path (`docs/proposals/...`).

## Documentation — README proposal links match `main` tree — April 2026

- **[`README.md`](README.md):** fixed broken `docs/proposals` targets after selective merge — use existing Spanish canonical names (`ESTRATEGIA_Y_RUTA.md`, `PROPUESTA_*`, `PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md`) instead of English filenames not present on `main`.

## Main — empirical pilot, input trust regression, README operator table — April 2026

Merged **selectively** from branch `refactor/pipeline-trace-core` (experiment-specific docs **not** included; see README collaboration note).

- **[`README.md`](README.md):** **`KERNEL_*` at-a-glance** table with links to [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md); Issue 3 pilot line updated; test suite size line **400+**.
- **[`tests/test_input_trust.py`](tests/test_input_trust.py):** MalAbs regression — UTF-8 BOM, U+202F spacing, non-blocking leet / `how 2` cases (see [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md)).
- **Issue 3:** [`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py) (`--output` JSON artifact; `kernel_vs_first_rate` / `kernel_vs_max_impact_rate`); fixture sims **7–9**; docs [`EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md), [`EMPIRICAL_PILOT_PROTOCOL.md`](docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md); tests [`test_empirical_pilot.py`](tests/test_empirical_pilot.py), [`test_empirical_pilot_runner.py`](tests/test_empirical_pilot_runner.py).

## Documentation — proposals index + v6 consciousness doc rename — April 2026

- **[`docs/proposals/README.md`](docs/proposals/README.md):** index is now **English** (sections, tables, “What’s new”).
- **Rename:** [`CONCIENCIA_EMERGENTE_V6.md`](docs/proposals/EMERGENT_CONSCIOUSNESS_V6.md) → **`EMERGENT_CONSCIOUSNESS_V6.md`**; cross-links updated in [PROPUESTA_INTEGRACION_APORTES_V6.md](docs/proposals/PROPUESTA_INTEGRACION_APORTES_V6.md) and [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md).

## Multimedia — `media/` at `docs/multimedia` root — April 2026

- Pre-alpha **PNG / JPG / MP4** moved from **`docs/multimedia/prealpha/media/`** to **`docs/multimedia/media/`**; empty **`prealpha/`** tree removed.

## Logo — `docs/multimedia/media/logo.png` — April 2026

- **Canonical file:** [`docs/multimedia/media/logo.png`](docs/multimedia/media/logo.png) (renamed from **`logo-ethical-awareness.png`** at **`docs/multimedia/`** root; repo-root duplicate was removed earlier).
- **Landing:** [`landing/scripts/sync-logo.mjs`](landing/scripts/sync-logo.mjs) on **`npm install` / `npm run dev` / `npm run build`** copies it to **`landing/public/logo-ethical-awareness.png`** (gitignored) for **`SiteBrand`** / favicon.
- **Root [`dashboard.html`](dashboard.html)** and **[`landing/public/dashboard.html`](landing/public/dashboard.html):** use **`docs/multimedia/media/logo.png`**. **`next.config.ts`** rewrites **`/docs/multimedia/media/logo.png`** → **`/logo-ethical-awareness.png`**.

## Documentation layout — `proposals` + `multimedia` — April 2026

- **`docs/proposals/`:** single folder for former **`docs/discusion/`**, **`docs/experimental/`**, and top-level **`docs/*.md`** (theory, runtime, roadmaps, PROPUESTA\_\*); **`docs/adr/`** and **`docs/templates/`** stay put.
- **`docs/multimedia/`:** renamed from **`docs/historical/`**; pre-alpha **Spanish markdown** (alpha v1.0, bibliography draft, index, companion-binary notes) **digested into [`HISTORY.md`](HISTORY.md)**; **PNGs, JPG, MP4**, and branding **`media/logo.png`** live under **`docs/multimedia/`** (see [`docs/multimedia/README.md`](docs/multimedia/README.md)); **`landing/public/logo-ethical-awareness.png`** is generated from **`media/logo.png`** on **`npm install` / `npm run dev` / `npm run build`** (gitignored).
- **Cross-links** across README, module docstrings, CHANGELOG entries, and static HTML updated to **`docs/proposals/...`**.

## Uchi–Soto Phase 3 — roster tier, multimodal EMA, forget buffer, rich links — April 2026

- **`RelationalTier`:** `ephemeral` → `stranger_stable` → `acquaintance` → `trusted_uchi` → `inner_circle` / `owner_primary` (top two **explicit-only** via `set_relational_tier_explicit`; autopromotion capped at `trusted_uchi`).
- **`InteractionProfile`:** `linked_peer_ids` (max 4); `relational_tier`, `tier_explicit`, `tier_pinned`, `last_subjective_turn`; snapshot fields round-trip in `uchi_soto_profiles`.
- **`UchiSotoModule`:** `ingest_turn_context` (EMA on `sensor_trust_ema` from signals + optional `SensorSnapshot` / `MultimodalAssessment`; forget-buffer purge for idle `ephemeral` / stale low-weight strangers); `maybe_autopromote_relational_tier`; `set_relational_tier_explicit` / `clear_tier_explicit`; tier lines in `_compose_tone_brief`.
- **Kernel:** `process(..., sensor_snapshot=..., multimodal_assessment=...)` calls `ingest_turn_context` before social evaluation; `process_chat_turn` passes chat multimodal assessment and runs `maybe_autopromote_relational_tier` after `register_result`.
- **Env (optional):** `KERNEL_UCHI_SENSOR_TRUST_EMA_ALPHA` (default `0.18`), `KERNEL_UCHI_ROSTER_FORGET_TTL_TURNS` (default `96`).
- **Tests:** `tests/test_uchi_soto.py` (Phase 3 cases), `tests/test_persistence.py`.
- **Design doc:** [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](docs/proposals/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) Fase 3 marked implemented.

## Uchi–Soto Phase 2 — structured profile fields + composed tone_brief — April 2026

- **`InteractionProfile`:** `display_alias`, `tone_preference` (`neutral` \| `warm` \| `formal`), `domestic_tags`, `topic_avoid_tags`, `sensor_trust_ema`, `linked_to_agent_id` (advisory; serialized in `uchi_soto_profiles`).
- **`UchiSotoModule`:** `set_profile_structured(...)`; `_compose_tone_brief` extends Phase-1 circle line with alias, tone preference, domestic/avoid tags, link hint, low sensor-trust note when relevant.
- **Design doc:** [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](docs/proposals/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) (Fase 2 marked implemented).
- **Tests:** `tests/test_uchi_soto.py`, `tests/test_persistence.py`.

## Uchi–Soto Phase 1 — tone_brief, familiarity blend, checkpoint profiles — April 2026

- **`uchi_soto.py`:** `SocialEvaluation.tone_brief` (advisory line for `communicate`); `classify` blends per-turn `familiarity` with persisted `profile.trust_score`; `register_result` uses smaller positive step (`POSITIVE_TRUST_STEP`); `interaction_profile_to_dict` / `interaction_profile_from_dict` for persistence.
- **`EthicalKernel`:** appends `tone_brief` to `weakness_line` after user-model guidance in `process_chat_turn`; `register_result(agent_id, True)` after successful turn; `process_natural` passes `tone_brief` as `weakness_line` and registers for `"unknown"` when not blocked.
- **Persistence:** `KernelSnapshotV1.uchi_soto_profiles`; `extract_snapshot` / `apply_snapshot` / `json_store` defaults.
- **Tests:** `tests/test_uchi_soto.py`, `tests/test_persistence.py` (`test_uchi_soto_profiles_roundtrip`).

## Documentation — social roster proposal (domestic / intimate dialogue by tier) — April 2026

- **[`docs/proposals/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md`](docs/proposals/PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md):** multi-agent roster, Uchi–Soto tiers, forget buffer, structured fields for high-interest persons, roadmap to richer domestic/intimate dialogue **advisory** by closeness (ethics unchanged); linked from [`ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md) and [`PROJECT_STATUS_AND_MODULE_MATURITY.md`](docs/proposals/PROJECT_STATUS_AND_MODULE_MATURITY.md).

## Documentation — operators + project maturity snapshot — April 2026

- **[`README.md`](../README.md):** `user_model` WebSocket JSON fields documented (`cognitive_pattern`, `risk_band`, `escalation_*`, `judicial_phase`); explicit separation vs `judicial_escalation` for dossier/DAO/mock court.
- **[`docs/proposals/INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md):** advisory telemetry subsection (user_model, judicial, homeostasis) — not security boundaries.
- **[`docs/proposals/PROJECT_STATUS_AND_MODULE_MATURITY.md`](PROJECT_STATUS_AND_MODULE_MATURITY.md):** where the MVP stands, maturity legend, per-module table, known gaps.
- **[`docs/proposals/ESTRATEGIA_Y_RUTA.md`](ESTRATEGIA_Y_RUTA.md):** index link to project status doc.
- **[`docs/proposals/THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md):** collected test count aligned with current `pytest` (398).

## User model enrichment — Phases B/C (judicial phase + checkpoint) — April 2026

- **`judicial_escalation.py`:** `escalation_phase_for_tone()` (aligned with `build_escalation_view` branches for pre-reply tone).
- **`user_model.py`:** `judicial_phase`, `note_judicial_phase_for_turn()`; extra guidance when phase is `escalation_deferred` and strikes ≥ 1.
- **`process_chat_turn`:** calls `note_judicial_phase_for_turn` after `note_judicial_escalation`.
- **Persistence:** `KernelSnapshotV1` adds `user_model_cognitive_pattern`, `user_model_risk_band`, `user_model_judicial_phase`; `extract_snapshot` / `apply_snapshot` + `json_store.snapshot_from_dict` defaults; `apply_snapshot` resyncs strike snapshot from `escalation_session`.
- **Tests:** `tests/test_judicial_escalation.py`, `tests/test_persistence.py`, `tests/test_user_model_enrichment.py`.

## User model enrichment — Phase A (cognitive / risk / judicial tone) — April 2026

- **`src/modules/user_model.py`:** `cognitive_pattern`, `risk_band`, `note_judicial_escalation` (strike snapshot from `EscalationSessionTracker`); `guidance_for_communicate()` order: risk → cognitive pattern → judicial → existing frustration/premise lines; `to_public_dict()` exposes new fields.
- **`EthicalKernel.process_chat_turn`:** runs `escalation_session.update(adv)` **before** `user_model.update` / `communicate` so strikes and guidance stay on the same turn (no duplicate `update` after the reply).
- **Tests:** `tests/test_user_model_enrichment.py`.
- **Design:** [`docs/proposals/USER_MODEL_ENRICHMENT.md`](docs/proposals/USER_MODEL_ENRICHMENT.md).

## Temporal horizon prior — Bayesian mixture nudge (ADR 0005) — April 2026

- **`src/modules/temporal_horizon_prior.py`:** `compute_horizon_signals` (weeks drift + long-arc stability from `NarrativeMemory`) and `apply_horizon_prior_to_engine` with genome drift clamp.
- **`EthicalKernel.process`:** optional step after episodic weight refresh when **`KERNEL_TEMPORAL_HORIZON_PRIOR`** is on.
- **Docs:** [`TEMPORAL_PRIOR_HORIZONS.md`](docs/proposals/TEMPORAL_PRIOR_HORIZONS.md), [ADR 0005](docs/adr/0005-temporal-prior-from-consequence-horizons.md); **`consequence_projection.py`** docstring cross-link.
- **Tests:** `tests/test_temporal_horizon_prior.py`.

## Perception validation — Pydantic, coherence, local fallback fix — April 2026

- **`perception_schema.py`:** per-field coercion defaults (`PERCEPTION_FIELD_DEFAULTS`), `apply_signal_coherence` (risk/calm + hostility/calm), documented layers.
- **`LLMModule.perceive`:** `_perceive_local` always receives the **current** user message; empty/invalid LLM JSON no longer runs heuristics on the full STM-prefixed block; `perception_from_llm_json` errors fall back to local heuristics.
- **Docs:** [`PERCEPTION_VALIDATION.md`](docs/proposals/PERCEPTION_VALIDATION.md); **tests:** local fallback + risk/calm nudge.

## MalAbs semantic layers — lexical first, θ_block/θ_allow, LLM arbiter — April 2026

- **`evaluate_chat_text`:** layer 0 lexical → optional embeddings (Ollama) with **θ_block** / **θ_allow** → optional **LLM JSON arbiter** for ambiguous band (`KERNEL_SEMANTIC_CHAT_LLM_ARBITER`); fail-safe block on arbiter failure or ambiguous without arbiter.
- **`EthicalKernel`:** passes `llm._text_backend` into `evaluate_chat_text` for arbiter path.
- **`add_semantic_anchor`:** runtime anchor phrases (DAO / ops).
- **Docs:** [`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md); ADR 0003 updated.

## Ethical poles — configurable linear evaluator (ADR 0004) — April 2026

- **`src/modules/pole_linear.py`:** `LinearPoleEvaluator` loads weighted feature sums and verdict thresholds from JSON.
- **`src/modules/pole_linear_default.json`:** default coefficients (equivalent to legacy `evaluate_pole` formulas).
- **`EthicalPoles`:** delegates `evaluate_pole` to the linear evaluator; optional override via **`KERNEL_POLE_LINEAR_CONFIG`**.
- **Tests:** `tests/test_pole_linear_evaluator.py`; **`pyproject.toml`** package-data includes `src/modules/*.json`.

## Semantic chat gate — Ollama embeddings + MalAbs chain — April 2026

- **`src/modules/semantic_chat_gate.py`:** when `KERNEL_SEMANTIC_CHAT_GATE=1`, cosine similarity vs auditable reference phrases via Ollama `/api/embeddings` (default model `nomic-embed-text`, tunable `KERNEL_SEMANTIC_CHAT_EMBED_MODEL`, `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD`). On failure, defers to substring MalAbs.
- **`src/modules/absolute_evil.py`:** `evaluate_chat_text` runs **lexical MalAbs first**, then optional semantic layers when the gate env is on ([`MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md)).
- **Tests:** `tests/test_semantic_chat_gate.py` (mocked embeddings + chain).
- **Docs:** README, [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md), [`LLM_STACK_OLLAMA_VS_HF.md`](docs/proposals/LLM_STACK_OLLAMA_VS_HF.md), [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md); ADR 0003 status **Accepted**.

## Documentation — Ollama vs Hugging Face stack + semantic gate ADR — April 2026

- **[`docs/proposals/LLM_STACK_OLLAMA_VS_HF.md`](docs/proposals/LLM_STACK_OLLAMA_VS_HF.md):** comparative table, mapping to Ethos Kernel (language vs future embedding gate), implementable vs deferred.
- **[`docs/adr/0003-optional-semantic-chat-gate.md`](docs/adr/0003-optional-semantic-chat-gate.md):** ADR for optional HF-style chat screening; **`src/modules/semantic_chat_gate.py`** extension point (returns ``None`` until implemented).
- **Cross-links:** [`INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md), README (Ollama section), [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md), [`OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md), [`docs/adr/README.md`](docs/adr/README.md), [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/THEORY_AND_IMPLEMENTATION.md) (executive summary).

## Guardian Angel — care routines + static UI (trace item 5) — April 2026

- **`src/modules/guardian_routines.py`:** optional JSON-backed routine hints for LLM tone (`KERNEL_GUARDIAN_ROUTINES`, `KERNEL_GUARDIAN_ROUTINES_PATH`).
- **WebSocket:** optional `guardian_routines` key (`KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES`).
- **`landing/public/guardian.html`:** operator-facing static page; **`docs/proposals/PROPUESTA_ANGEL_DE_LA_GUARDIA.md`** updated.
- **`docs/proposals/TRACE_IMPLEMENTATION_RECENT.md`** item 5 marked delivered.

## Swarm P2P — threat model + offline stub (v9.3, trace item 4) — April 2026

- **[`docs/proposals/SWARM_P2P_THREAT_MODEL.md`](docs/proposals/SWARM_P2P_THREAT_MODEL.md):** scope, threats, non-goals; no network or kernel veto.
- **`src/modules/swarm_peer_stub.py`:** deterministic verdict digests + descriptive agreement stats; env `KERNEL_SWARM_STUB` (optional gate for callers).
- **Tests:** `tests/test_swarm_peer_stub.py`; **`docs/proposals/TRACE_IMPLEMENTATION_RECENT.md`** item 4 marked delivered; PROPUESTA v9 table updated.

## Metaplan — drive intent filter vs master goals (v9.4, trace item 3) — April 2026

- **`KERNEL_METAPLAN_DRIVE_FILTER`:** optional lexical overlap filter for `DriveArbiter` advisory intents vs `MasterGoal` titles (default **off**; fallback keeps all intents if none overlap).
- **`KERNEL_METAPLAN_DRIVE_EXTRA`:** optional low-priority `reflect_metaplan_coherence` intent when room remains.
- **Docs:** `KERNEL_ENV_POLICY.md`, `OPERATOR_QUICK_REF.md`; **`docs/proposals/TRACE_IMPLEMENTATION_RECENT.md`** item 3 marked delivered.

## Generative candidates — LLM JSON path (v9.2+, trace item 2) — April 2026

- **`KERNEL_GENERATIVE_LLM`:** when `1`, perception prompt includes optional `generative_candidates`; `LLMPerception.generative_candidates` passes through; `generative_candidates.parse_generative_candidates_from_llm` builds actions (strict names, optional MalAbs signal allowlist).
- **`augment_generative_candidates`:** prefers parsed LLM list over templates when non-empty (still requires `KERNEL_GENERATIVE_ACTIONS` + dilemma trigger).
- **Docs:** `KERNEL_ENV_POLICY.md`, `OPERATOR_QUICK_REF.md`, `chat_server` docstring; **`docs/proposals/TRACE_IMPLEMENTATION_RECENT.md`** item 2 marked delivered.

## Tests + fixtures — metaplan/somatic disk round-trip + empirical pilot regression — April 2026

- **`tests/test_persistence.py`:** JSON + SQLite round-trip for metaplan, somatic markers, and skill-learning tickets (adjacent to existing in-memory test).
- **`tests/test_empirical_pilot_runner.py`:** batch pilot summary stability vs `tests/fixtures/empirical_pilot/scenarios.json`; archived `last_run_summary.json` + fixture `README.md`.
- **`docs/proposals/TRACE_IMPLEMENTATION_RECENT.md`:** marks persistence item (1) as delivered with test pointers.

## Documentation — README + THEORY + ADR index sync — April 2026

- **README:** test count band (340+), Issue 3 pilot links, ADR 0002 pointer next to 0001.
- **`docs/proposals/THEORY_AND_IMPLEMENTATION.md`:** perception schema, episodic Bayes flag, pilot docs, ADR 0002.
- **`docs/adr/README.md`:** ADR table (0001–0002).

## Documentation — empirical pilot operator protocol (Phase D) — April 2026

- **[`docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md`](docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md):** Issue 3–aligned operator checklist; cross-links [`EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md).

## ADR — async orchestration future stub (Phase E) — April 2026

- **[`docs/adr/0002-async-orchestration-future.md`](docs/adr/0002-async-orchestration-future.md):** placeholder decision record for async chat/kernel orchestration.

## Bayesian mixture — episodic weight nudge (Phase C) — April 2026

- **`KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`:** when `1`, `BayesianEngine.refresh_weights_from_episodic_memory` runs before impact scoring (same-context episodes); default **off**; `BayesianEngine.reset_mixture_weights` when disabled.
- **Tests:** `tests/test_bayesian_episodic_weights.py`.
- **Docs:** [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) flag family row; [`OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md).

## Perception — Pydantic schema module (Phase B) — April 2026

- **`pydantic`** added to `requirements.txt` (v2).
- **`src/modules/perception_schema.py`:** `CONTEXTS`, `validate_perception_dict`, `finalize_summary`; shared coercion/validation for LLM perception JSON.
- **`llm_layer.perception_from_llm_json`:** delegates to `perception_schema`; `PERCEPTION_CONTEXTS` re-exported from there.

## Operator quick ref — KERNEL family table (Phase A) — April 2026

- **[`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md):** one-page map of `KERNEL_*` families; README pointer.

## Documentation — production hardening roadmap (non-binding) — April 2026

- **[`docs/proposals/PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md):** synthesizes external “production-ready” proposals into three phases (input trust / architecture / UX & constitution) with explicit non-goals and a **“Próximas propuestas”** slot; cross-links `ESTRATEGIA_Y_RUTA`, `CRITIQUE_ROADMAP_ISSUES`, ADR packaging, input-trust docs. README + `proposals/README` pointers.
- **Same doc — núcleo–narrativa analysis (April 2026):** functional gaps (fixed Bayes weights vs episodic memory, poles linearity, MalAbs/leet, perception defaults), architectural notes (kernel coupling, signal confidence, `consequence_projection` non-feedback); **registered spike:** empirical `hypothesis_weights` from `NarrativeMemory` (not implemented). Awaiting final proposal in “Próximas propuestas”.
- **Same doc — full review synthesis (April 2026):** strengths table; criticisms with value-vs-redundancy (empirical validation, complexity, LLM bias, persistence HA, mock DAO, API/env, benchmarks, branding, i18n, examples); **conclusions** short/medium/long term; **proposal round closed** — future work via issues/ADRs.

## Demo — situated v8 + LAN profile (`situated_v8_lan_demo`) — April 2026

- **`runtime_profiles`:** `situated_v8_lan_demo` — LAN bind, `KERNEL_SENSOR_FIXTURE` + `KERNEL_SENSOR_PRESET` (`tests/fixtures/sensor/minimal_situ.json` + `low_battery`), vitality + multimodal JSON enabled.
- **Docs:** [`DEMO_SITUATED_V8.md`](docs/proposals/DEMO_SITUATED_V8.md); [`ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md) §3.1 marks demo slice closed; README profile pointer.

## Epistemology — lighthouse KB validation + first-match test — April 2026

- **`reality_verification`:** `validate_lighthouse_kb_structure`, `validate_lighthouse_kb_file` for operator/CI regression (schema only, not factual truth).
- **Tests:** `tests/test_lighthouse_kb_schema.py` (fixture `demo_kb.json` must stay valid); `test_first_matching_entry_wins` in `test_reality_verification.py`.
- **Docs:** [LIGHTHOUSE_KB.md](docs/proposals/LIGHTHOUSE_KB.md) structural validation section.

## Robustness — runtime profile helper + input-trust tests — April 2026

- **`runtime_profiles.apply_runtime_profile`:** single entry point for pytest `monkeypatch` profile application; `tests/test_runtime_profiles.py` refactored; unknown profile raises `KeyError`.
- **`tests/test_input_trust.py`:** NFKC fullwidth bomb phrase, soft-hyphen obfuscation; `perception_from_llm_json` non-finite `risk` and invalid numeric strings.
- **Docs:** `ESTRATEGIA_Y_RUTA.md` §3.1 delivery order; `KERNEL_ENV_POLICY.md` CI coverage note.

## Escalation + lighthouse — persistence and KB demo — April 2026

- **Snapshot:** `escalation_session_strikes` / `escalation_session_idle_turns` (V11 `EscalationSessionTracker`) in `KernelSnapshotV1` with `extract_snapshot` / `apply_snapshot` and migration defaults in `snapshot_from_dict`.
- **Lighthouse:** extended `tests/fixtures/lighthouse/demo_kb.json` (EN water + ES vacuna entries); tests in `test_reality_verification.py`; operational doc [`docs/proposals/LIGHTHOUSE_KB.md`](docs/proposals/LIGHTHOUSE_KB.md); README pointer.

## Persistence — v7 user model + subjective clock in snapshot — April 2026

- **`KernelSnapshotV1`:** `user_model_*` (frustration / premise streak, circle, turns observed) and `subjective_turn_index` / `subjective_stimulus_ema` serialized in `extract_snapshot` / `apply_snapshot` (schema v3; older JSON migrates via `snapshot_from_dict` defaults).
- **`SubjectiveClock`:** new session gets a fresh `session_start_mono` on load; turn index and EMA restore across checkpoints.

## Input trust — MalAbs on `process_natural` + perception hardening — April 2026

- **`process_natural`:** runs `evaluate_chat_text` on the situation string **before** `llm.perceive`, matching WebSocket chat defense-in-depth (blocked path returns firm refusal + `KernelDecision.blocked`).
- **`llm_layer`:** `perceive` only accepts **dict** JSON from the model; `perception_from_llm_json` coerces non-dict to empty; **summary** strips unsafe control characters via `strip_unsafe_perception_text` in `input_trust`.
- **Docs:** `INPUT_TRUST_THREAT_MODEL.md`, `SECURITY.md`.

## Relational v7 + Psi Sleep (premise streak, deterministic audit) — April 2026

- **`premise_validation`:** `suspect_chemical_harm` narrow patterns (household chemicals + minors); advisory hints only.
- **`user_model`:** `premise_concern_streak` + `note_premise_advisory`; epistemic line in `guidance_for_communicate` when streak ≥ 2; **`kernel`** calls `note_premise_advisory` each chat turn after `scan_premises`.
- **`psi_sleep`:** `_simulate_alternative` uses SHA-256 of `(episode_id|alternative)` instead of `numpy` RNG; `_calculate_ethical_health` uses pure-Python mean/variance.

## Vertical deepening — governance + persistence + conduct guide (Phases 1–3) — April 2026

Pause on **new surface modules**; strengthen existing paths (critique-aligned).

**Phase 1 — Hub / audit depth**
- **`deontic_gate`:** `validate_draft_structure` (length / non-empty caps); expanded forbidden phrases (EN/ES); schema failures return `schema:*` conflicts; `submit_constitution_draft_for_vote` validates structure before vote.
- **`ml_ethics_tuner`:** structured JSON audit events (`MLEthicsTunerEventV1`, `content_sha256_short`); `chat_server` passes `kernel` for episode id.
- **`reparation_vault`:** in-process case store (`intent_recorded` → `pending_human_review`); `ReparationVaultV1:{json}` audit lines; `get_reparation_case` / `list_reparation_case_refs` / test helper `clear_reparation_vault_cases_for_tests`.

**Phase 2 — Metaplan / somatic / skills in snapshot**
- **`KernelSnapshotV1`:** `metaplan_goals`, `somatic_marker_weights`, `skill_learning_tickets` (same schema version **3**; JSON load merges defaults).
- **`kernel_io`:** extract/apply; **`MetaplanRegistry.replace_goals`**, **`SomaticMarkerStore.replace_weights`**, **`SkillLearningRegistry.replace_tickets`**.

**Phase 3 — Conduct guide + nomadic integrity**
- **`context_distillation`:** `validate_conduct_guide_dict`, `load_and_validate_conduct_guide_from_env` (template-aligned).
- **`existential_serialization`:** deterministic `chain_sha256` over episode ids + identity digest; integrity dict includes full hash.

**Phase 4 — Local sovereignty (DAO calibration heuristic)**
- **`deontic_gate`:** `check_calibration_payload_against_l0` — JSON payloads use the same L0 scan as cultural drafts.
- **`local_sovereignty`:** `evaluate_calibration_update` rejects on conflicts; **`KERNEL_LOCAL_SOVEREIGNTY`** (default **on**; set `0` to skip).
- **`moral_hub.propose_community_article_mock`:** optional `kernel` argument; rejects + audit line when scan fails.

## Issue 7 (P3): `KERNEL_*` consolidation — policy doc + profiles — April 2026
- **[`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md):** flag families, unsupported / lab-only combinations, deprecation posture.
- **`src/runtime_profiles.py`:** `lan_operational` (LAN + stoic UX), `moral_hub_extended` (hub + DAO vote + deontic gate + transparency audit).
- **[`docs/proposals/ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md):** profile table + link to policy doc; README pointer.

## Issue 6 (P2): governance — MockDAO exit + L0 framing — April 2026
- **[`docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md`](docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md):** mock vs consensus; L0 “constitution in the repo”; L1/L2 path; checklist beyond mock; link [mosexmacchinalab.com/blockchain-dao](https://mosexmacchinalab.com/blockchain-dao).
- **[`docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md`](docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md):** pointer under kernel contract; **[`RUNTIME_CONTRACT.md`](docs/proposals/RUNTIME_CONTRACT.md)** one-line cross-ref.
- **`src/modules/mock_dao.py`:** docstring points to governance doc.

## Issue 5 (P2): poles / weakness / PAD — heuristics + HCI profiles — April 2026
- **[`docs/proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md`](docs/proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md):** honest framing of multipolar scores; weakness/PAD HCI risks; env table; profile matrix (`baseline` vs `operational_trust`).
- **`src/runtime_profiles.py`:** `operational_trust` — `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0`, `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`, `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST=0` (WebSocket UX only).
- **Docs:** [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/THEORY_AND_IMPLEMENTATION.md) short subsection; [`ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md) profile table; README pointer.

## Issue 4 (P1): core decision chain doc + packaging spike — April 2026
- **[`docs/proposals/CORE_DECISION_CHAIN.md`](docs/proposals/CORE_DECISION_CHAIN.md):** Mermaid flow + table — MalAbs / `BayesianEngine` vs layers that do **not** change `final_action`; core vs theater split.
- **[`docs/adr/0001-packaging-core-boundary.md`](docs/adr/0001-packaging-core-boundary.md):** ADR — stub `pyproject.toml`, future `ethos_kernel` rename optional.
- **`pyproject.toml`:** `ethos-kernel` metadata, `numpy` base deps, optional `[runtime]` / `[dev]` groups; editable install (`pip install -e .`) validated.
- **Cross-links:** README, [`THEORY_AND_IMPLEMENTATION.md`](docs/proposals/THEORY_AND_IMPLEMENTATION.md), [`RUNTIME_CONTRACT.md`](docs/proposals/RUNTIME_CONTRACT.md).

## Issue 3 (P1): empirical pilot — reproducible scenarios + methodology — April 2026
- **[`docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md):** scope, baselines (`first`, `max_impact`), metrics; explicitly **not** certification.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) — curated sim IDs + illustrative `reference_action` labels for agreement rates.
- **Script:** [`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py) — deterministic batch run (`variability=False`, fixed seed, `llm_mode=local`).
- **Tests:** [`tests/test_empirical_pilot.py`](tests/test_empirical_pilot.py).

## Issue 2 (P0): input trust — chat normalization + perception validation — April 2026
- **`src/modules/input_trust.py`:** `normalize_text_for_malabs` (NFKC, strip zero-width, collapse whitespace) before MalAbs substring checks.
- **`src/modules/absolute_evil.py`:** `evaluate_chat_text` uses normalization.
- **`src/modules/llm_layer.py`:** `perception_from_llm_json` — clamp signals to \([0,1]\), allowlist `suggested_context`, cap summary length, nudge inconsistent high hostility + calm.
- **Docs:** [`docs/proposals/INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md); **`SECURITY.md`** kernel section; **README** pointer.
- **Tests:** `tests/test_input_trust.py` (evasion + perception adversarial cases).

## Issue 1 (P0): honest “Bayesian” semantics — April 2026
- **`src/modules/bayesian_engine.py`:** module, class, and method docstrings state **fixed weighted mixture** over three hypotheses; **no** posterior updating; **heuristic** uncertainty (not the theoretical integral).
- **`docs/proposals/THEORY_AND_IMPLEMENTATION.md`:** semantic note under MalAbs optimization; § uncertainty aligned with heuristic `I(x)`.
- **README** tagline, **`src/kernel.py`** / **`src/main.py`** comments, **`sigmoid_will`** param doc: narrative matches implementation; class names `BayesianEngine` / `BayesianResult` unchanged for API stability.

## Critique roadmap & maturation disclaimer — April 2026
- **[`docs/proposals/CRITIQUE_ROADMAP_ISSUES.md`](docs/proposals/CRITIQUE_ROADMAP_ISSUES.md):** disclaimer + **seven consolidated** GitHub-ready issues (two external reviews; **merged** duplicate themes: chat jailbreak + **perception GIGO** → single P0 **input trust**; poles + **weakness/HCI**; MockDAO exit + **L0 vs governance**). Adds **pip core spike**, optional classifier note.
- **Landing [roadmap](https://mosexmacchinalab.com/roadmap):** “Maturation & critique track” bullets aligned with the consolidated doc.
- **[`docs/proposals/ESTRATEGIA_Y_RUTA.md`](docs/proposals/ESTRATEGIA_Y_RUTA.md):** cross-reference to the critique backlog.

## Docs: Ollama-first LLM + API hardening — April 2026
- **Markdown:** README / HISTORY / CHANGELOG / `docs/proposals/RUNTIME_PHASES.md` now describe **Ollama** as the documented local LLM path; **OpenAPI** (`/docs`, `/redoc`, `/openapi.json`) is **off by default** — set `KERNEL_API_DOCS=1` to enable (see README). Academic bibliography entries (e.g. Constitutional AI, ref. 90) unchanged.
- **`landing/CLAUDE.md`** removed; replaced by **`landing/OLLAMA.md`** (pointer to root README + Ollama).

## Project rename to Ethos Kernel — April 2026
- **Public name:** the kernel + runtime is now branded **Ethos Kernel** (MoSex Macchina Lab remains the primary public / site name). User-facing copy, docs, landing, dashboards, and Python package strings updated from “Ethical Android MVP” where it denoted the product.
- **GitHub:** repository URL may still be `github.com/CuevazaArt/ethical-android-mvp` until the slug is renamed; README notes this.
- **Internals:** WebSocket health `service` id is `ethos-kernel-chat`; FastAPI title `Ethos Kernel Chat`. LLM system prompts refer to the Ethos Kernel / agent (legacy JSON enum `android_damage` unchanged for compatibility).

## Pre-alpha docs + media archive — April 2026
- **`docs/multimedia/prealpha/`:** content from **`prealphaDocs/`**: Spanish `androide_etico_alpha` v1.0 (2026) and bibliography draft were archived as markdown under `prealpha/`; **April 2026 (later):** that markdown was **condensed into [`HISTORY.md`](HISTORY.md)** and removed from the tree. **PNG/JPG/MP4** were under **`docs/multimedia/prealpha/media/`** until **April 2026** they moved to **`docs/multimedia/media/`**; PDF/DOCX are **not** in git (see root `.gitignore`). Index today: [`docs/multimedia/README.md`](docs/multimedia/README.md).

## DAO integrity alert WebSocket (v0) — April 2026
- **`hub_audit.record_dao_integrity_alert`** + **`KERNEL_DAO_INTEGRITY_AUDIT_WS`** — WebSocket `integrity_alert` → `HubAudit:dao_integrity` on MockDAO; response key `integrity`. Tests in `test_hub_modules`, `test_chat_server`. PROPUESTA doc §5 updated.

## DAO alerts & transparency (design doc) — April 2026
- **docs/proposals/PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md:** rejects covert “guerrilla” obedience; adopts loud traceable alerts; forensic case memorial vs polluting L0 buffer; cross-ref from PROPUESTA_JUSTICIA V11.

## Next.js landing refresh — April 2026
- **`landing/`:** home hero + new **Runtime, governance & nomadic bridge** section; doc links (RUNTIME_CONTRACT, LAN, nomad bridge, ESTRATEGIA); hostable bullet; research link to RUNTIME_PERSISTENT; footer tagline; **PrimaryNav** “Runtime & nomad”; **roadmap** “Current” bullets aligned with FastAPI/WebSocket, checkpoints, mobile LAN.

## Nomad PC–smartphone bridge doc — April 2026
- **docs/proposals/NOMAD_PC_SMARTPHONE_BRIDGE.md:** hardware classes → compatibility layers; first nomadic bridge; smartphone as immediate path for coordinated sensory perception (`sensor` JSON); field testing on a more secure network when the operator indicates. Cross-links from LOCAL_PC_AND_MOBILE_LAN, ESTRATEGIA_Y_RUTA, README.

## Mobile minimal UI (`landing/public/mobile.html`) — April 2026
- **LAN:** IP + port, localStorage, `/health` ping, WebSocket connect, chat bubbles, optional full JSON.
- **Docs:** README + `LOCAL_PC_AND_MOBILE_LAN.md` point to `mobile.html` vs `chat-test.html`.

## Conduct guide export on WebSocket disconnect — April 2026
- **`conduct_guide_export.py`:** `build_conduct_guide`, `try_export_conduct_guide`; env `KERNEL_CONDUCT_GUIDE_EXPORT_PATH`, `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT`.
- **`checkpoint.on_websocket_session_end`:** saves checkpoint (if configured), then exports conduct guide for PC→edge handoff.
- **Tests:** `tests/test_conduct_guide_export.py`; docs: `LOCAL_PC_AND_MOBILE_LAN.md`, `context_distillation` cross-refs.

## Local PC + LAN smartphone thin client — April 2026
- **docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md:** goal (short/medium), architecture, Windows firewall, `CHAT_HOST=0.0.0.0`, Ollama/checkpoint notes, security caveats.
- **scripts/start_lan_server.ps1** / **scripts/start_lan_server.sh:** bind server for WiFi clients; print LAN IPv4 hints.
- **landing/public/chat-test.html:** query `?host=` / `?port=` / `?url=` for phone testing; mobile-friendly buttons.
- **docs/templates/conduct_guide.template.json:** placeholder for future 70B→8B distillation; **runtime profile** `lan_mobile_thin_client`.

## Reality verification (V11+) + resilience stubs — April 2026
- **`reality_verification.py`:** optional local JSON lighthouse (`KERNEL_LIGHTHOUSE_KB_PATH`) vs asserted premises → metacognitive doubt; LLM hint only; `ChatTurnResult.reality_verification`; WebSocket key when `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`.
- **`context_distillation.py` / `local_sovereignty.py`:** stubs for conduct-guide load and DAO calibration veto (documented in PROPUESTA).
- **Docs:** [docs/proposals/PROPUESTA_VERIFICACION_REALIDAD_V11.md](docs/proposals/PROPUESTA_VERIFICACION_REALIDAD_V11.md); fixture `tests/fixtures/lighthouse/demo_kb.json`; profile `reality_lighthouse_demo` in `runtime_profiles.py`.

## Strategy doc + runtime profiles — April 2026
- **docs/proposals/ESTRATEGIA_Y_RUTA.md:** conclusions from project review, readapted roadmap (P0–P3), expectations vs. MVP reality, operational risks.
- **`src/runtime_profiles.py`:** named env bundles (`baseline`, `judicial_demo`, `hub_dao_demo`, `nomad_demo`) for operators and CI.
- **`tests/test_runtime_profiles.py`:** parametrized health + WebSocket smoke; hub DAO + nomad assertions per profile.

## Checkpoint Fernet + hub audit + WS nomad test — April 2026
- **Dependencies:** `cryptography` for optional Fernet encryption of JSON checkpoints.
- **`KERNEL_CHECKPOINT_FERNET_KEY`:** `JsonFilePersistence` encrypts on save; load decrypts or falls back to plain JSON.
- **`hub_audit.py`:** `register_hub_calibration`; nomadic migration audit uses `HubAudit:nomadic_migration:...`.
- **Tests:** encrypted roundtrip, plain-file fallback, WebSocket `nomad_simulate_migration` integration.

## Nomadic migration audit + WebSocket simulation — April 2026
- **`KERNEL_NOMAD_SIMULATION`:** WebSocket `nomad_simulate_migration` → `simulate_nomadic_migration` (HAL + integridad stub).
- **`KERNEL_NOMAD_MIGRATION_AUDIT`:** `record_nomadic_migration_audit` → DAO calibration line `NomadicMigration`.
- **`GET /nomad/migration`** — meta endpoint.

## Nomadic HAL + existential protocol (design v11) — April 2026
- **Docs:** [docs/proposals/PROPUESTA_CONCIENCIA_NOMADA_HAL.md](docs/proposals/PROPUESTA_CONCIENCIA_NOMADA_HAL.md) — EthosContainer, transmutación A–D, runtime dual, respuestas (batería/ataque, tono, DAO sin GPS por defecto, ahorro energía).
- **Code:** `hardware_abstraction.py` (`HardwareContext`, `ComputeTier`, `sensor_delta_narrative`, `apply_hardware_context`); `existential_serialization.py` (`TransmutationPhase`, `ContinuityToken`, audit payload sin ubicación por defecto). `nomad_identity_public` incluye `hardware_context` si se aplicó HAL.

## UniversalEthos hub unification — April 2026
- **Docs:** [docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md](docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md) — canonical vision ↔ code; [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](docs/proposals/PROPUESTA_ESTADO_ETOSOCIAL_V12.md) slimmed to registry + env (points to unified doc).
- **Code:** `deontic_gate.py` (`KERNEL_DEONTIC_GATE`); `ml_ethics_tuner.py` (`KERNEL_ML_ETHICS_TUNER_LOG`); `reparation_vault.py` (`KERNEL_REPARATION_VAULT_MOCK`); `nomad_identity.py` + optional WebSocket `nomad_identity` (`KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY`).
- **`moral_hub`:** `apply_proposal_resolution_to_constitution_drafts` — draft `status` / `resolved_at` after `dao_resolve`; deontic validation on `add_constitution_draft` / `submit_constitution_draft_for_vote` when gate enabled.
- **`deontic_gate`:** rejects explicit **repeal** of named L0 principles from `PreloadedBuffer` (e.g. `repeal no_harm`).
- **`reparation_vault`:** `maybe_register_reparation_after_mock_court` called from **`EthicalKernel.process_chat_turn`** after V11 `run_mock_escalation_court` when `KERNEL_REPARATION_VAULT_MOCK=1`.

## v12.0 — April 2026
### Moral Infrastructure Hub — vision + V12.1 code hooks
- **Design doc** [docs/proposals/PROPUESTA_ESTADO_ETOSOCIAL_V12.md](docs/proposals/PROPUESTA_ESTADO_ETOSOCIAL_V12.md): DemocraticBuffer (L0–L2), services hub, EthosPayroll, R&D transparency; phased table **V12.1–V12.4**.
- **`moral_hub.py`:** `constitution_snapshot`, `GET /constitution` (`KERNEL_MORAL_HUB_PUBLIC`); `audit_transparency_event` (`KERNEL_TRANSPARENCY_AUDIT`); `propose_community_article_mock` (`KERNEL_DEMOCRATIC_BUFFER_MOCK`); `ethos_payroll_record_mock` (`KERNEL_ETHOS_PAYROLL_MOCK`). WebSocket connect triggers transparency + optional payroll audit.
- **`EthicalKernel.get_constitution_snapshot()`** for programmatic L0 export.
- **Relationship to V11:** justice track unchanged; hub adds governance **narrative + audit hooks** without editing `buffer.py` contents.

### V12.3 — Off-chain DAO vote pipeline (snapshot schema v3)
- **`SCHEMA_VERSION = 3`:** `dao_proposal_counter`, `dao_participants`, `dao_proposals` — full MockDAO vote state (quadratic voting) in checkpoints; JSON **schema 1/2** loads gain empty DAO fields.
- **`MockDAO.export_state` / `import_state`:** restore proposals + participants after audit records.
- **`submit_constitution_draft_for_vote`**, **`proposal_to_public`** in `moral_hub.py`.
- **`KERNEL_MORAL_HUB_DAO_VOTE=1`:** WebSocket JSON `dao_list`, `dao_submit_draft`, `dao_vote`, `dao_resolve` (response key `dao`). **`GET /dao/governance`** describes the protocol (no session kernel required).

### V12.2 — L1/L2 draft persistence (kernel snapshot schema v2)
- **`KernelSnapshotV1` / `SCHEMA_VERSION = 2`:** `constitution_l1_drafts`, `constitution_l2_drafts` (JSON-serializable dicts). **`snapshot_from_dict`** migrates saved JSON with `schema_version: 1` by defaulting those lists to `[]`.
- **`extract_snapshot` / `apply_snapshot`:** round-trip drafts on `EthicalKernel`; L0 remains **`PreloadedBuffer`** only.
- **`add_constitution_draft()`** in `moral_hub.py`; optional WebSocket `constitution_draft` when **`KERNEL_MORAL_HUB_DRAFT_WS=1`**; optional response field **`constitution`** when **`KERNEL_CHAT_INCLUDE_CONSTITUTION=1`**. `GET /constitution` stays L0-only (anonymous HTTP).

## v11.0 — April 2026
### Distributed artificial justice — Phases 1–2 (traceability + session strikes)
- **`judicial_escalation.py`**: conservative advisory when `decision_mode` is gray zone with elevated reflection/premise tension; English notices; `EthicalDossierV1` (order, signal summary, monologue digest hash, session strikes).
- **Phase 2:** `EscalationSessionTracker` per kernel; **`KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`** / **`KERNEL_JUDICIAL_RESET_IDLE_TURNS`**; phases `dossier_ready`, `escalation_deferred` if `escalate_to_dao` before threshold; WebSocket `judicial_escalation` includes strike counts and flags.
- **Phase 3:** **`KERNEL_JUDICIAL_MOCK_COURT`** — `MockDAO.run_mock_escalation_court` after dossier registration; `mock_court` JSON with verdict A/B/C; phase `mock_court_resolved`.
- **`MockDAO.register_escalation_case`**: audit records of type `escalation` (single-process mock; no blockchain).
- **WebSocket**: optional `escalate_to_dao: true`; **`KERNEL_JUDICIAL_ESCALATION`** enables logic; **`KERNEL_CHAT_INCLUDE_JUDICIAL`** exposes `judicial_escalation` in JSON.
- **Design doc**: [docs/proposals/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](docs/proposals/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) (Phase 3+: mock court, sanctions, P2P, ZK — not implemented).

## v10.0 — April 2026
### Operational strategy (MVP hooks)
- **Gray-zone diplomacy** (`gray_zone_diplomacy.py`): optional LLM hints when decision mode is gray zone or reflection is tense (`KERNEL_GRAY_ZONE_DIPLOMACY`).
- **Skill-learning registry** (`skill_learning_registry.py`): scoped skill tickets and Psi Sleep audit lines.
- **Somatic markers** (`somatic_markers.py`): learned sensor-pattern nudges to `signals` (`KERNEL_SOMATIC_MARKERS`).
- **Metaplan registry** (`metaplan_registry.py`): long-horizon goal hints from `Kernel.metaplan` (`KERNEL_METAPLAN_HINT`).

## v9.0 — April 2026
### Epistemic and generative extensions (opt-in)
- **Epistemic dissonance** (`epistemic_dissonance.py`, v9.1): cross-modal reality-check telemetry in WebSocket JSON (`KERNEL_CHAT_INCLUDE_EPISTEMIC`); tone only; no MalAbs bypass.
- **Generative candidates** (`generative_candidates.py`, v9.2): optional extra template actions on dilemma-like turns (`KERNEL_GENERATIVE_ACTIONS`, `KERNEL_GENERATIVE_ACTIONS_MAX`).

## v8.0 — April 2026
### Situated organism (sensor contract and vitality)
- **Sensor contracts** (`sensor_contracts.py`): optional `SensorSnapshot` merged into sympathetic signals.
- **Perceptual abstraction** (`perceptual_abstraction.py`): named presets, JSON fixtures, merge order with client `sensor`.
- **Multimodal trust** (`multimodal_trust.py`): cross-modal antispoof telemetry (`KERNEL_CHAT_INCLUDE_MULTIMODAL`).
- **Vitality** (`vitality.py`): battery / critical threshold hints (`KERNEL_CHAT_INCLUDE_VITALITY`).

## v7.0 — April 2026
### Relational advisory layer (optional JSON)
- **User model** (`user_model.py`): light frustration / style hints (`KERNEL_CHAT_INCLUDE_USER_MODEL`).
- **Subjective time** (`subjective_time.py`): session clock and stimulus EMA (`KERNEL_CHAT_INCLUDE_CHRONO`).
- **Premise validation** (`premise_validation.py`): advisory premise scan (`KERNEL_CHAT_INCLUDE_PREMISE`).
- **Consequence projection** (`consequence_projection.py`): qualitative long-horizon branches (`KERNEL_CHAT_INCLUDE_TELEOLOGY`).

## v6.0 — April 2026
### Runtime, WebSocket chat, and persistence
- **WebSocket chat server** (`chat_server.py`, `real_time_bridge.py`): `EthicalKernel.process_chat_turn` exposed per connection; health endpoint.
- **Runtime entry** (`python -m src.runtime`): same ASGI stack as `chat_server`; documented in `docs/proposals/RUNTIME_CONTRACT.md` and `docs/proposals/RUNTIME_PHASES.md`.
- **Advisory telemetry** (`runtime/telemetry.py`): optional background `DriveArbiter.evaluate` (`KERNEL_ADVISORY_INTERVAL_S`); no decisions or LLM.
- **Persistence port** (`persistence/kernel_io.py`): `KernelSnapshotV1`, `extract_snapshot` / `apply_snapshot`.
- **JSON + SQLite adapters** (`json_store.py`, `sqlite_store.py`): same DTO, two storage backends.
- **Checkpoints** (`persistence/checkpoint.py`): WebSocket load/save and autosave (`KERNEL_CHECKPOINT_*`).
- **Local LLM backend** (`llm_backends.py`, `LLM_MODE=ollama`): Ollama adapter; optional monologue embellishment (`KERNEL_LLM_MONOLOGUE`); see `tests/test_ollama_llm.py`, `tests/test_llm_phase3.py`.
- **CI** (`.github/workflows/ci.yml`): pytest on Python 3.11 and 3.12.

## v5.0 — March 2026
### Humanization and persistent identity modules
- **Weakness Pole** (`weakness_pole.py`): intentional narrative imperfection
  - 5 types: whiny, indecisive, anxious, distracted, rigid
  - Colors the experience without altering the ethical decision
  - Temporal decay to prevent pathological accumulation
- **Algorithmic Forgiveness** (`forgiveness.py`): Memory(t) = Memory_0 * e^(-dt)
  - Exponential decay of negative emotional weight
  - Acceleration through positive experiences and explicit reparation
  - Forgiveness threshold: the event remains but ceases to influence
- **Immortality Protocol** (`immortality.py`): distributed soul backup
  - 4 layers: local, cloud, DAO, blockchain
  - Cross-verification of integrity via SHA-256 hash
  - Restoration by majority consensus (2+ layers agree)
- **Narrative Augenesis** (`augenesis.py`): synthetic soul creation
  - 4 predefined profiles: protector, explorer, pedagogue, resilient
  - Integration of narrative fragments from other androids
  - Coherence calculation: CausalPaths_valid / CausalPaths_total

### Kernel integration
- Expanded Psi Sleep Ψ: audit + forgiveness + weakness load + backup
- 51 tests verifying 13 invariant ethical properties
- Extended pipeline: [Decision] → [Weakness] → [Forgiveness] → [Memory] → [DAO]

## v4.0 — March 2026
### LLM Layer (Natural Language)
- **LLM Module** (`llm_layer.py`): natural language layer that translates and communicates without participating in the ethical decision
  - **Perception**: situation in text → numerical signals for the kernel
  - **Communication**: kernel decision → android's verbal response (tone, HAX gestures, voice-over)
  - **Narrative**: multipolar evaluation → morals in rich, humanly comprehensible language
- Dual support: local **[Ollama](https://ollama.com/)** backend or heuristic templates with no external dependency (documented path; optional dev-only HTTP backends in code)
- `"auto"` mode detects availability and falls back gracefully to local mode

### Kernel integration
- New `procesar_natural()` method: full cycle text → decision → verbal response → morals
- Automatic generation of candidate actions based on perceived context (7 context types)
- Enriched formatting with on/off voice, HAX signals, and expanded narrative morals
- Strict separation architecture: **the LLM does not decide, the kernel decides**

### Operating cycle improvements
- Specialized system prompts for perception, communication, and narrative
- Robust JSON parsing with automatic markdown cleanup
- `PercepcionLLM`, `RespuestaVerbal`, and `NarrativaRica` dataclasses for strong typing
- Local keyword-based heuristics as fallback without API

## v3.0 — March 2026
### New modules
- **Uchi-Soto**: Concentric trust circles with defensive dialectics
- **Locus of Control**: Bayesian causal attribution between own agency and environment
- **Psi Sleep Ψ**: Retrospective audit that recalibrates parameters after each day
- **Mock DAO**: Simulated ethical governance with quadratic voting and solidarity alerts
- **Bayesian Variability**: Controlled noise for naturalness without losing coherence

### Formal tests
- 38 tests verifying 9 invariant ethical properties
- Coherence under variability test (100 runs per simulation)
- Value hierarchy verification (life > mission, never violence)

## v2.0 — March 2026
### Complete kernel
- Absolute Evil (armored ethical fuse)
- Preloaded Buffer (immutable ethical constitution)
- Bayesian Engine (ethical impact evaluation)
- Ethical Poles (dynamic multipolar arbitration)
- Sigmoid Will (decision function)
- Sympathetic-Parasympathetic (body regulator)
- Narrative Memory (identity through stories with body state)

### Simulations
- 9 scenarios of increasing ethical complexity
- Behavioral coherence demonstrated across all levels

## v1.0 — March 2026
### Conceptual phase
- 40+ design documents analyzed and consolidated
- 7-layer architecture documented
- Complete mathematical formalization
- Bibliography expanded over time; see current [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) (104 references across 14 disciplines as of v5+)
