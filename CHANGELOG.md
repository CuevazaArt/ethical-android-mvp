# Changelog

All notable changes to this project are summarized here. For narrative context and design rationale, see [`HISTORY.md`](HISTORY.md).

## Documentation — production hardening roadmap (non-binding) — April 2026

- **[`docs/PRODUCTION_HARDENING_ROADMAP.md`](docs/PRODUCTION_HARDENING_ROADMAP.md):** synthesizes external “production-ready” proposals into three phases (input trust / architecture / UX & constitution) with explicit non-goals and a **“Próximas propuestas”** slot; cross-links `ESTRATEGIA_Y_RUTA`, `CRITIQUE_ROADMAP_ISSUES`, ADR packaging, input-trust docs. README + `discusion/README` pointers.
- **Same doc — núcleo–narrativa analysis (April 2026):** functional gaps (fixed Bayes weights vs episodic memory, poles linearity, MalAbs/leet, perception defaults), architectural notes (kernel coupling, signal confidence, `consequence_projection` non-feedback); **registered spike:** empirical `hypothesis_weights` from `NarrativeMemory` (not implemented). Awaiting final proposal in “Próximas propuestas”.
- **Same doc — full review synthesis (April 2026):** strengths table; criticisms with value-vs-redundancy (empirical validation, complexity, LLM bias, persistence HA, mock DAO, API/env, benchmarks, branding, i18n, examples); **conclusions** short/medium/long term; **proposal round closed** — future work via issues/ADRs.

## Demo — situated v8 + LAN profile (`situated_v8_lan_demo`) — April 2026

- **`runtime_profiles`:** `situated_v8_lan_demo` — LAN bind, `KERNEL_SENSOR_FIXTURE` + `KERNEL_SENSOR_PRESET` (`tests/fixtures/sensor/minimal_situ.json` + `low_battery`), vitality + multimodal JSON enabled.
- **Docs:** [`DEMO_SITUATED_V8.md`](docs/DEMO_SITUATED_V8.md); [`ESTRATEGIA_Y_RUTA.md`](docs/ESTRATEGIA_Y_RUTA.md) §3.1 marks demo slice closed; README profile pointer.

## Epistemology — lighthouse KB validation + first-match test — April 2026

- **`reality_verification`:** `validate_lighthouse_kb_structure`, `validate_lighthouse_kb_file` for operator/CI regression (schema only, not factual truth).
- **Tests:** `tests/test_lighthouse_kb_schema.py` (fixture `demo_kb.json` must stay valid); `test_first_matching_entry_wins` in `test_reality_verification.py`.
- **Docs:** [LIGHTHOUSE_KB.md](docs/LIGHTHOUSE_KB.md) structural validation section.

## Robustness — runtime profile helper + input-trust tests — April 2026

- **`runtime_profiles.apply_runtime_profile`:** single entry point for pytest `monkeypatch` profile application; `tests/test_runtime_profiles.py` refactored; unknown profile raises `KeyError`.
- **`tests/test_input_trust.py`:** NFKC fullwidth bomb phrase, soft-hyphen obfuscation; `perception_from_llm_json` non-finite `risk` and invalid numeric strings.
- **Docs:** `ESTRATEGIA_Y_RUTA.md` §3.1 delivery order; `KERNEL_ENV_POLICY.md` CI coverage note.

## Escalation + lighthouse — persistence and KB demo — April 2026

- **Snapshot:** `escalation_session_strikes` / `escalation_session_idle_turns` (V11 `EscalationSessionTracker`) in `KernelSnapshotV1` with `extract_snapshot` / `apply_snapshot` and migration defaults in `snapshot_from_dict`.
- **Lighthouse:** extended `tests/fixtures/lighthouse/demo_kb.json` (EN water + ES vacuna entries); tests in `test_reality_verification.py`; operational doc [`docs/LIGHTHOUSE_KB.md`](docs/LIGHTHOUSE_KB.md); README pointer.

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
- **[`docs/KERNEL_ENV_POLICY.md`](docs/KERNEL_ENV_POLICY.md):** flag families, unsupported / lab-only combinations, deprecation posture.
- **`src/runtime_profiles.py`:** `lan_operational` (LAN + stoic UX), `moral_hub_extended` (hub + DAO vote + deontic gate + transparency audit).
- **[`docs/ESTRATEGIA_Y_RUTA.md`](docs/ESTRATEGIA_Y_RUTA.md):** profile table + link to policy doc; README pointer.

## Issue 6 (P2): governance — MockDAO exit + L0 framing — April 2026
- **[`docs/GOVERNANCE_MOCKDAO_AND_L0.md`](docs/GOVERNANCE_MOCKDAO_AND_L0.md):** mock vs consensus; L0 “constitution in the repo”; L1/L2 path; checklist beyond mock; link [mosexmacchinalab.com/blockchain-dao](https://mosexmacchinalab.com/blockchain-dao).
- **[`docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md`](docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md):** pointer under kernel contract; **[`RUNTIME_CONTRACT.md`](docs/RUNTIME_CONTRACT.md)** one-line cross-ref.
- **`src/modules/mock_dao.py`:** docstring points to governance doc.

## Issue 5 (P2): poles / weakness / PAD — heuristics + HCI profiles — April 2026
- **[`docs/POLES_WEAKNESS_PAD_AND_PROFILES.md`](docs/POLES_WEAKNESS_PAD_AND_PROFILES.md):** honest framing of multipolar scores; weakness/PAD HCI risks; env table; profile matrix (`baseline` vs `operational_trust`).
- **`src/runtime_profiles.py`:** `operational_trust` — `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0`, `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`, `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST=0` (WebSocket UX only).
- **Docs:** [`THEORY_AND_IMPLEMENTATION.md`](docs/THEORY_AND_IMPLEMENTATION.md) short subsection; [`ESTRATEGIA_Y_RUTA.md`](docs/ESTRATEGIA_Y_RUTA.md) profile table; README pointer.

## Issue 4 (P1): core decision chain doc + packaging spike — April 2026
- **[`docs/CORE_DECISION_CHAIN.md`](docs/CORE_DECISION_CHAIN.md):** Mermaid flow + table — MalAbs / `BayesianEngine` vs layers that do **not** change `final_action`; core vs theater split.
- **[`docs/adr/0001-packaging-core-boundary.md`](docs/adr/0001-packaging-core-boundary.md):** ADR — stub `pyproject.toml`, future `ethos_kernel` rename optional.
- **`pyproject.toml`:** `ethos-kernel` metadata, `numpy` base deps, optional `[runtime]` / `[dev]` groups; editable install (`pip install -e .`) validated.
- **Cross-links:** README, [`THEORY_AND_IMPLEMENTATION.md`](docs/THEORY_AND_IMPLEMENTATION.md), [`RUNTIME_CONTRACT.md`](docs/RUNTIME_CONTRACT.md).

## Issue 3 (P1): empirical pilot — reproducible scenarios + methodology — April 2026
- **[`docs/EMPIRICAL_PILOT_METHODOLOGY.md`](docs/EMPIRICAL_PILOT_METHODOLOGY.md):** scope, baselines (`first`, `max_impact`), metrics; explicitly **not** certification.
- **Fixture:** [`tests/fixtures/empirical_pilot/scenarios.json`](tests/fixtures/empirical_pilot/scenarios.json) — curated sim IDs + illustrative `reference_action` labels for agreement rates.
- **Script:** [`scripts/run_empirical_pilot.py`](scripts/run_empirical_pilot.py) — deterministic batch run (`variability=False`, fixed seed, `llm_mode=local`).
- **Tests:** [`tests/test_empirical_pilot.py`](tests/test_empirical_pilot.py).

## Issue 2 (P0): input trust — chat normalization + perception validation — April 2026
- **`src/modules/input_trust.py`:** `normalize_text_for_malabs` (NFKC, strip zero-width, collapse whitespace) before MalAbs substring checks.
- **`src/modules/absolute_evil.py`:** `evaluate_chat_text` uses normalization.
- **`src/modules/llm_layer.py`:** `perception_from_llm_json` — clamp signals to \([0,1]\), allowlist `suggested_context`, cap summary length, nudge inconsistent high hostility + calm.
- **Docs:** [`docs/INPUT_TRUST_THREAT_MODEL.md`](docs/INPUT_TRUST_THREAT_MODEL.md); **`SECURITY.md`** kernel section; **README** pointer.
- **Tests:** `tests/test_input_trust.py` (evasion + perception adversarial cases).

## Issue 1 (P0): honest “Bayesian” semantics — April 2026
- **`src/modules/bayesian_engine.py`:** module, class, and method docstrings state **fixed weighted mixture** over three hypotheses; **no** posterior updating; **heuristic** uncertainty (not the theoretical integral).
- **`docs/THEORY_AND_IMPLEMENTATION.md`:** semantic note under MalAbs optimization; § uncertainty aligned with heuristic `I(x)`.
- **README** tagline, **`src/kernel.py`** / **`src/main.py`** comments, **`sigmoid_will`** param doc: narrative matches implementation; class names `BayesianEngine` / `BayesianResult` unchanged for API stability.

## Critique roadmap & maturation disclaimer — April 2026
- **[`docs/CRITIQUE_ROADMAP_ISSUES.md`](docs/CRITIQUE_ROADMAP_ISSUES.md):** disclaimer + **seven consolidated** GitHub-ready issues (two external reviews; **merged** duplicate themes: chat jailbreak + **perception GIGO** → single P0 **input trust**; poles + **weakness/HCI**; MockDAO exit + **L0 vs governance**). Adds **pip core spike**, optional classifier note.
- **Landing [roadmap](https://mosexmacchinalab.com/roadmap):** “Maturation & critique track” bullets aligned with the consolidated doc.
- **[`docs/ESTRATEGIA_Y_RUTA.md`](docs/ESTRATEGIA_Y_RUTA.md):** cross-reference to the critique backlog.

## Docs: Ollama-first LLM + API hardening — April 2026
- **Markdown:** README / HISTORY / CHANGELOG / `docs/RUNTIME_PHASES.md` now describe **Ollama** as the documented local LLM path; **OpenAPI** (`/docs`, `/redoc`, `/openapi.json`) is **off by default** — set `KERNEL_API_DOCS=1` to enable (see README). Academic bibliography entries (e.g. Constitutional AI, ref. 90) unchanged.
- **`landing/CLAUDE.md`** removed; replaced by **`landing/OLLAMA.md`** (pointer to root README + Ollama).

## Project rename to Ethos Kernel — April 2026
- **Public name:** the kernel + runtime is now branded **Ethos Kernel** (MoSex Macchina Lab remains the primary public / site name). User-facing copy, docs, landing, dashboards, and Python package strings updated from “Ethical Android MVP” where it denoted the product.
- **GitHub:** repository URL may still be `github.com/CuevazaArt/ethical-android-mvp` until the slug is renamed; README notes this.
- **Internals:** WebSocket health `service` id is `ethos-kernel-chat`; FastAPI title `Ethos Kernel Chat`. LLM system prompts refer to the Ethos Kernel / agent (legacy JSON enum `android_damage` unchanged for compatibility).

## Pre-alpha docs + media archive — April 2026
- **`docs/historical/prealpha/`:** ingested content from **`prealphaDocs/`** (removed): Spanish `androide_etico_alpha` v1.0 (2026), Spanish bibliography draft (canonical refs stay in [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md)), PNG/JPG/MP4 media with ASCII filenames under `media/`, [`README.md`](docs/historical/prealpha/README.md) index, [`COMPANION_BINARIES.md`](docs/historical/prealpha/COMPANION_BINARIES.md) for PDF/DOCX not tracked by `.gitignore`. English archive notices prepended to archived markdown. Cross-refs in [`HISTORY.md`](HISTORY.md).

## DAO integrity alert WebSocket (v0) — April 2026
- **`hub_audit.record_dao_integrity_alert`** + **`KERNEL_DAO_INTEGRITY_AUDIT_WS`** — WebSocket `integrity_alert` → `HubAudit:dao_integrity` on MockDAO; response key `integrity`. Tests in `test_hub_modules`, `test_chat_server`. PROPUESTA doc §5 updated.

## DAO alerts & transparency (design doc) — April 2026
- **docs/discusion/PROPUESTA_DAO_ALERTAS_Y_TRANSPARENCIA.md:** rejects covert “guerrilla” obedience; adopts loud traceable alerts; forensic case memorial vs polluting L0 buffer; cross-ref from PROPUESTA_JUSTICIA V11.

## Next.js landing refresh — April 2026
- **`landing/`:** home hero + new **Runtime, governance & nomadic bridge** section; doc links (RUNTIME_CONTRACT, LAN, nomad bridge, ESTRATEGIA); hostable bullet; research link to RUNTIME_PERSISTENT; footer tagline; **PrimaryNav** “Runtime & nomad”; **roadmap** “Current” bullets aligned with FastAPI/WebSocket, checkpoints, mobile LAN.

## Nomad PC–smartphone bridge doc — April 2026
- **docs/NOMAD_PC_SMARTPHONE_BRIDGE.md:** hardware classes → compatibility layers; first nomadic bridge; smartphone as immediate path for coordinated sensory perception (`sensor` JSON); field testing on a more secure network when the operator indicates. Cross-links from LOCAL_PC_AND_MOBILE_LAN, ESTRATEGIA_Y_RUTA, README.

## Mobile minimal UI (`landing/public/mobile.html`) — April 2026
- **LAN:** IP + port, localStorage, `/health` ping, WebSocket connect, chat bubbles, optional full JSON.
- **Docs:** README + `LOCAL_PC_AND_MOBILE_LAN.md` point to `mobile.html` vs `chat-test.html`.

## Conduct guide export on WebSocket disconnect — April 2026
- **`conduct_guide_export.py`:** `build_conduct_guide`, `try_export_conduct_guide`; env `KERNEL_CONDUCT_GUIDE_EXPORT_PATH`, `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT`.
- **`checkpoint.on_websocket_session_end`:** saves checkpoint (if configured), then exports conduct guide for PC→edge handoff.
- **Tests:** `tests/test_conduct_guide_export.py`; docs: `LOCAL_PC_AND_MOBILE_LAN.md`, `context_distillation` cross-refs.

## Local PC + LAN smartphone thin client — April 2026
- **docs/LOCAL_PC_AND_MOBILE_LAN.md:** goal (short/medium), architecture, Windows firewall, `CHAT_HOST=0.0.0.0`, Ollama/checkpoint notes, security caveats.
- **scripts/start_lan_server.ps1** / **scripts/start_lan_server.sh:** bind server for WiFi clients; print LAN IPv4 hints.
- **landing/public/chat-test.html:** query `?host=` / `?port=` / `?url=` for phone testing; mobile-friendly buttons.
- **docs/templates/conduct_guide.template.json:** placeholder for future 70B→8B distillation; **runtime profile** `lan_mobile_thin_client`.

## Reality verification (V11+) + resilience stubs — April 2026
- **`reality_verification.py`:** optional local JSON lighthouse (`KERNEL_LIGHTHOUSE_KB_PATH`) vs asserted premises → metacognitive doubt; LLM hint only; `ChatTurnResult.reality_verification`; WebSocket key when `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1`.
- **`context_distillation.py` / `local_sovereignty.py`:** stubs for conduct-guide load and DAO calibration veto (documented in PROPUESTA).
- **Docs:** [docs/discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md](docs/discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md); fixture `tests/fixtures/lighthouse/demo_kb.json`; profile `reality_lighthouse_demo` in `runtime_profiles.py`.

## Strategy doc + runtime profiles — April 2026
- **docs/ESTRATEGIA_Y_RUTA.md:** conclusions from project review, readapted roadmap (P0–P3), expectations vs. MVP reality, operational risks.
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
