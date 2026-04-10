# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

## Nomadic migration audit + WebSocket simulation — April 2026
- **`KERNEL_NOMAD_SIMULATION`:** WebSocket `nomad_simulate_migration` → `simulate_nomadic_migration` (HAL + integridad stub).
- **`KERNEL_NOMAD_MIGRATION_AUDIT`:** `record_nomadic_migration_audit` → DAO calibration line `NomadicMigration`.
- **`GET /nomad/migration`** — meta endpoint.

## Nomadic HAL + existential protocol (design v11) — April 2026
- **Docs:** [docs/discusion/PROPUESTA_CONCIENCIA_NOMADA_HAL.md](docs/discusion/PROPUESTA_CONCIENCIA_NOMADA_HAL.md) — EthosContainer, transmutación A–D, runtime dual, respuestas (batería/ataque, tono, DAO sin GPS por defecto, ahorro energía).
- **Code:** `hardware_abstraction.py` (`HardwareContext`, `ComputeTier`, `sensor_delta_narrative`, `apply_hardware_context`); `existential_serialization.py` (`TransmutationPhase`, `ContinuityToken`, audit payload sin ubicación por defecto). `nomad_identity_public` incluye `hardware_context` si se aplicó HAL.

## UniversalEthos hub unification — April 2026
- **Docs:** [docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md](docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md) — canonical vision ↔ code; [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md) slimmed to registry + env (points to unified doc).
- **Code:** `deontic_gate.py` (`KERNEL_DEONTIC_GATE`); `ml_ethics_tuner.py` (`KERNEL_ML_ETHICS_TUNER_LOG`); `reparation_vault.py` (`KERNEL_REPARATION_VAULT_MOCK`); `nomad_identity.py` + optional WebSocket `nomad_identity` (`KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY`).
- **`moral_hub`:** `apply_proposal_resolution_to_constitution_drafts` — draft `status` / `resolved_at` after `dao_resolve`; deontic validation on `add_constitution_draft` / `submit_constitution_draft_for_vote` when gate enabled.
- **`deontic_gate`:** rejects explicit **repeal** of named L0 principles from `PreloadedBuffer` (e.g. `repeal no_harm`).
- **`reparation_vault`:** `maybe_register_reparation_after_mock_court` called from **`EthicalKernel.process_chat_turn`** after V11 `run_mock_escalation_court` when `KERNEL_REPARATION_VAULT_MOCK=1`.

## v12.0 — April 2026
### Moral Infrastructure Hub — vision + V12.1 code hooks
- **Design doc** [docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md](docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md): DemocraticBuffer (L0–L2), services hub, EthosPayroll, R&D transparency; phased table **V12.1–V12.4**.
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
- **Design doc**: [docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md) (Phase 3+: mock court, sanctions, P2P, ZK — not implemented).

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
- **Runtime entry** (`python -m src.runtime`): same ASGI stack as `chat_server`; documented in `docs/RUNTIME_CONTRACT.md` and `docs/RUNTIME_PHASES.md`.
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
- Dual support: Anthropic API (Claude) when key is available, local templates with no external dependency
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
