# Ethos Kernel

[![CI](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CuevazaArt/ethical-android-mvp/graph/badge.svg)](https://codecov.io/gh/CuevazaArt/ethical-android-mvp)

**MoSex Macchina Lab** — this repository is the open **kernel + runtime** for a model of artificial ethical agency: humanizing imperfection, forgiveness, identity persistence, and **traceable** governance hooks (DAO / hub audit, not a black-box chatbot).

**Where things stand today:** a **FastAPI WebSocket** runtime (`python -m src.chat_server` or `python -m src.runtime`) with **per-session kernel** state; **versioned persistence** (JSON / SQLite snapshots, optional **Fernet** checkpoints); **V12 moral hub** (constitution drafts, MockDAO votes, `HubAudit` lines); **LAN** thin clients ([`landing/public/mobile.html`](landing/public/mobile.html), conduct guide export); a **large** automated test suite (400+ tests) on **Python 3.11 / 3.12** in CI; optional layers for sensors, relational hints, judicial escalation, reality verification (“lighthouse”), and integrity alerts (`KERNEL_DAO_INTEGRITY_AUDIT_WS`).

**Kernel version line:** ethical core **v5**; **v6–v10** runtime, persistence, advisory stack; **v11** judicial escalation + cross-model premise checks; **v12** etosocial / hybrid-hub infrastructure and documented civilization vision — see [`HISTORY.md`](HISTORY.md) and [`CHANGELOG.md`](CHANGELOG.md).

**Collaboration note:** The branch **`refactor/pipeline-trace-core`** preserved a multi-agent coordination experiment (internal buffers and keywords). That workflow is **not** part of routine development on `main`; useful kernel/docs/test changes from that line were merged selectively. The branch remains as **historical context** only.

The original **batch simulations** (nine fixed scenarios plus a random generator) and the **thirteen invariant ethical properties** are still validated; they are **historical roots** of the suite. Full tables and narrow pytest drills are documented in [`HISTORY.md`](HISTORY.md#nine-canonical-simulation-scenarios-v2-origins) (see also the [thirteen properties](HISTORY.md#thirteen-invariant-ethical-properties-core-ethical-suite) and [early pytest drills](HISTORY.md#early-pytest-drills-regression-entry-points)).

**Maturation disclaimer:** some **names** (e.g. “Bayesian” scoring) and **governance mocks** (DAO) are **infrastructure placeholders** while runtime, audit trails, and tests mature — toward **honest labeling**, **calibrated weights**, and **clear criteria** for stronger safety and real governance experiments. **Weaknesses / bottlenecks** (sync core vs async server, inference fragility, MockDAO limits): [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](docs/WEAKNESSES_AND_BOTTLENECKS.md). **Consolidated** issue backlog (two external reviews, redundant items merged): [`docs/proposals/CRITIQUE_ROADMAP_ISSUES.md`](docs/proposals/CRITIQUE_ROADMAP_ISSUES.md); web overview: [Roadmap](https://mosexmacchinalab.com/roadmap). **Forward-looking hardening (non-binding):** [`docs/proposals/PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md) — includes synthesis of external reviews: strengths, criticisms (value vs redundancy), and **conclusions for improvements** (short / medium / long term); proposal round closed as doc; follow-up via issues/ADRs.

**Empirical pilot (Issue 3):** [`docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md`](docs/proposals/EMPIRICAL_PILOT_METHODOLOGY.md) (batch harness, scenarios **1–9**, `--output` artifact) · [`docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md`](docs/proposals/EMPIRICAL_PILOT_PROTOCOL.md) (operator checklist).

**Core decision chain & packaging (Issue 4):** [`docs/proposals/CORE_DECISION_CHAIN.md`](docs/proposals/CORE_DECISION_CHAIN.md) (diagram + table: who sets `final_action`); stub **`pyproject.toml`** at repo root for optional `pip install -e .` / extras — ADRs [`docs/adr/0001-packaging-core-boundary.md`](docs/adr/0001-packaging-core-boundary.md), [`docs/adr/0002-async-orchestration-future.md`](docs/adr/0002-async-orchestration-future.md) (async orchestration stub).

**Poles / weakness / PAD & HCI (Issue 5):** [`docs/proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md`](docs/proposals/POLES_WEAKNESS_PAD_AND_PROFILES.md) — heuristics framing + **`operational_trust`** profile in [`src/runtime_profiles.py`](src/runtime_profiles.py) (stoic WebSocket UX; core policy unchanged).

**Governance narrative (Issue 6):** [`docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md`](docs/proposals/GOVERNANCE_MOCKDAO_AND_L0.md) — MockDAO limits, **L0** as in-repo constitution, L1/L2 vs votes; public page [blockchain-dao](https://mosexmacchinalab.com/blockchain-dao).

**`KERNEL_*` policy (Issue 7):** [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) — flag families, risky combos, deprecation posture; extended profiles in [`src/runtime_profiles.py`](src/runtime_profiles.py) (`lan_operational`, `moral_hub_extended`, **`situated_v8_lan_demo`** for v8+LAN, **`perception_hardening_lab`** for Fase 1 perception hardening, **`phase2_event_bus_lab`** for Phase 2 `KernelEventBus` — see [`docs/proposals/DEMO_SITUATED_V8.md`](docs/proposals/DEMO_SITUATED_V8.md), [`docs/proposals/PRODUCTION_HARDENING_ROADMAP.md`](docs/proposals/PRODUCTION_HARDENING_ROADMAP.md), [`docs/adr/0006-phase2-core-boundary-and-event-bus.md`](docs/adr/0006-phase2-core-boundary-and-event-bus.md)).

**`KERNEL_*` at a glance** — use **[nominal profiles](docs/proposals/STRATEGY_AND_ROADMAP.md#4-nominal-profiles-operators-and-ci)** in [`src/runtime_profiles.py`](src/runtime_profiles.py) when possible; full catalog and **unsupported combinations** live in [`KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md).

| Family | Prefix / examples | Detail in policy |
|--------|---------------------|------------------|
| Chat WebSocket UX | `KERNEL_CHAT_INCLUDE_*`, `KERNEL_CHAT_EXPOSE_MONOLOGUE` | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| Governance / hub / judicial | `KERNEL_MORAL_HUB_*`, `KERNEL_JUDICIAL_*`, `KERNEL_DAO_INTEGRITY_AUDIT_WS`, `KERNEL_LOCAL_SOVEREIGNTY` | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| Persistence / handoff | `KERNEL_CHECKPOINT_*`, `KERNEL_CONDUCT_GUIDE_*` | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| Perception / sensors / vitality | `KERNEL_SENSOR_*`, `KERNEL_MULTIMODAL_*`, `KERNEL_VITALITY_*`, optional `KERNEL_PERCEPTION_UNCERTAINTY_*`, `KERNEL_PERCEPTION_PARSE_FAIL_LOCAL`, `KERNEL_LIGHT_RISK_CLASSIFIER`, `KERNEL_PERCEPTION_CROSS_CHECK`, `KERNEL_CHAT_INCLUDE_LIGHT_RISK` | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| LLM / variability / generative | `LLM_MODE`, `KERNEL_VARIABILITY`, `KERNEL_GENERATIVE_*` | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| Input trust (MalAbs + semantic) | `KERNEL_SEMANTIC_CHAT_GATE` (default **on**), `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`, `KERNEL_MALABS_*`, … | [Flag families](docs/proposals/KERNEL_ENV_POLICY.md#1-flag-families-mental-model) |
| Risky combos / lab-only | (ad-hoc mixes) | [Unsupported combinations](docs/proposals/KERNEL_ENV_POLICY.md#2-unsupported-or-lab-only-combinations) |

**Input trust:** MalAbs chat filtering and LLM perception bounds are **heuristic**, not unbreakable — see [`docs/proposals/INPUT_TRUST_THREAT_MODEL.md`](docs/proposals/INPUT_TRUST_THREAT_MODEL.md) and [`SECURITY.md`](SECURITY.md).

**Governance & transparency (data policy, audit chain, limits):** [`docs/GOVERNANCE_DATA_POLICY.md`](docs/GOVERNANCE_DATA_POLICY.md), [`docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md`](docs/AUDIT_TRAIL_AND_REPRODUCIBILITY.md), [`docs/TRANSPARENCY_AND_LIMITS.md`](docs/TRANSPARENCY_AND_LIMITS.md), static summary [`landing/public/ethos-transparency.html`](landing/public/ethos-transparency.html), phased example [`docs/ROADMAP_PRACTICAL_PHASES.md`](docs/ROADMAP_PRACTICAL_PHASES.md).

**Operator quick ref (`KERNEL_*` families):** [`docs/proposals/OPERATOR_QUICK_REF.md`](docs/proposals/OPERATOR_QUICK_REF.md) — one-page map; full policy in [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md).

An autonomous moral agent that makes ethical decisions using **explicit weighted scoring**
(fixed mixture over three stylized hypotheses; not full Bayesian updating — see
[`docs/proposals/THEORY_AND_IMPLEMENTATION.md`](docs/proposals/THEORY_AND_IMPLEMENTATION.md)), narrative memory,
multipolar evaluation, LLM layer, narrative weakness pole, algorithmic forgiveness, and
immortality protocol. No hardware — pure behavioral validation.

This project is also available in [Spanish](https://github.com/CuevazaArt/androide-etico-mvp).

## What it does

- **Runtime chat:** JSON over WebSocket with env-toggled modules (relational, sensor, judicial, DAO, hub, nomad, integrity audit). Default health + `/ws/chat` — see [Quick start](#quick-start) and [Real-time chat (WebSocket)](#real-time-chat-websocket).
- **Persistence & checkpoints:** load/save kernel snapshots; optional encrypted JSON checkpoints; conduct guide JSON on disconnect for PC → edge handoff.
- **Batch simulations:** `python -m src.main` — legacy harness still used for regression; scenario catalog in [`HISTORY.md`](HISTORY.md#nine-canonical-simulation-scenarios-v2-origins).
- **Interactive dashboard:** `dashboard.html` (also under `landing/public/`) — explore module traces in the browser without installing Node.
- **Landing site:** Next.js app in `landing/` for **[mosexmacchinalab.com](https://mosexmacchinalab.com)** — **not** imported by Python; TypeScript is required only if you work on that subtree. See **[`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md)** (mandatory vs optional tooling, language stats, optional repo split).

## Quick start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository (GitHub slug is still ethical-android-mvp; project name: Ethos Kernel)
git clone https://github.com/CuevazaArt/ethical-android-mvp.git
cd ethical-android-mvp

# Create virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (CMD):
.venv\Scripts\activate.bat
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Run simulations

```bash
# All simulations (1-9)
python -m src.main

# A specific simulation
python -m src.main --sim 3
```

### Run tests

**Primary check:** run the **full** suite — same as CI (Python **3.11** and **3.12** in `.github/workflows/ci.yml`). CI also runs **Ruff** (lint + format check) and **mypy** on `src/`; install tooling with `pip install -r requirements.txt -r requirements-dev.txt` (see [`CONTRIBUTING.md`](CONTRIBUTING.md)).

```bash
pytest tests/ -v
pytest tests/ --tb=short
```

This includes invariant ethical properties, the WebSocket chat server (DAO integrity, judicial escalation, reality verification, etc.), moral hub, persistence, runtime profiles, and integration smoke tests across optional `KERNEL_*` layers. The **thirteen** core ethical properties, the **nine-scenario** catalog, and **narrow** pytest entry points (for example, Absolute Evil only) are documented in [`HISTORY.md`](HISTORY.md#thirteen-invariant-ethical-properties-core-ethical-suite) so this README stays focused on the current stack.

**Operations:** supported demo **env bundles** — [`src/runtime_profiles.py`](src/runtime_profiles.py); strategy and roadmap — [docs/proposals/STRATEGY_AND_ROADMAP.md](docs/proposals/STRATEGY_AND_ROADMAP.md).

**Local PC + smartphone (same WiFi):** bind the chat server to `0.0.0.0`; scripts and checklist — [docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md](docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md) (`scripts/start_lan_server.ps1`, `landing/public/mobile.html`). **Nomadic bridge:** [docs/proposals/NOMAD_PC_SMARTPHONE_BRIDGE.md](docs/proposals/NOMAD_PC_SMARTPHONE_BRIDGE.md).

**Reproducibility:** the default ethical pipeline does **not** invoke narrative augenesis (`kernel.augenesis` is optional; see [docs/proposals/THEORY_AND_IMPLEMENTATION.md](docs/proposals/THEORY_AND_IMPLEMENTATION.md)). Long-lived deployments — [docs/proposals/RUNTIME_PERSISTENT.md](docs/proposals/RUNTIME_PERSISTENT.md).

**Docker / observability:** build and run with [`Dockerfile`](Dockerfile) and [`docker-compose.yml`](docker-compose.yml) (`docker compose up --build`). Optional Compose profile **`llm`** starts **Ollama** (`docker compose --profile llm up --build`); a commented **Chroma** stub is available for vector experiments. **`ETHOS_RUNTIME_PROFILE`** (e.g. `lan_operational`, `situated_v8_lan_demo`) applies a named env bundle at server startup — see [`src/runtime_profiles.py`](src/runtime_profiles.py) and [`docs/proposals/RUNTIME_PROFILES_OPERATOR_TABLE.md`](docs/proposals/RUNTIME_PROFILES_OPERATOR_TABLE.md). Set **`KERNEL_METRICS=1`** to expose Prometheus **`/metrics`** (LLM latency, chat paths, MalAbs blocks, semantic MalAbs outcomes, DAO WebSocket ops, embedding errors). Set **`KERNEL_LOG_JSON=1`** and **`KERNEL_LOG_LEVEL`** for JSON logs with **`request_id`** / **`X-Request-ID`**. WebSocket load smoke: [`scripts/loadtest/ws_stress.py`](scripts/loadtest/ws_stress.py) (requires `pip install websockets` from dev extras).

### Real-time chat (WebSocket)

`EthicalKernel.process_chat_turn` is exposed over **WebSocket** for UIs or tools. Each connection gets its **own** kernel instance (isolated short-term memory).

```bash
# From repo root, after pip install -r requirements.txt
python -m src.chat_server
# Same server (preferred entry name for “runtime”):
python -m src.runtime
# Optional: one-shot demo bundle (unset keys only — explicit env wins), e.g.
#   export ETHOS_RUNTIME_PROFILE=lan_operational   # Unix
#   set ETHOS_RUNTIME_PROFILE=lan_operational # Windows CMD
# Default: http://127.0.0.1:8765/health  —  WebSocket: ws://127.0.0.1:8765/ws/chat
```

Ethical guardrails for background tasks: [docs/proposals/RUNTIME_CONTRACT.md](docs/proposals/RUNTIME_CONTRACT.md).

Send **JSON text** frames, e.g. `{"text": "Hello", "agent_id": "user", "include_narrative": false}`.  
Optional **`sensor`** object (v8 — situated hints: `battery_level`, `place_trust`, `accelerometer_jerk`, `ambient_noise`, `silence`, `biometric_anomaly`, `backup_just_completed`, plus **cross-modal** `audio_emergency`, `vision_emergency`, `scene_coherence` for antispoof): merged into sympathetic **signals** before the decision stack; **no** MalAbs bypass. See [docs/proposals/PROPOSAL_SITUATED_ORGANISM_V8.md](docs/proposals/PROPOSAL_SITUATED_ORGANISM_V8.md).  
Optional **server-side** layers (dev/demo): `KERNEL_SENSOR_FIXTURE` = path to a JSON file (same keys as `sensor`); `KERNEL_SENSOR_PRESET` = named scenario from `src/modules/perceptual_abstraction.py` (`SENSOR_PRESETS`). Merge order: **fixture → preset → client `sensor`** (client overrides per key).  
Optional env: `CHAT_HOST`, `CHAT_PORT`, `LLM_MODE`, `USE_LOCAL_LLM`, `KERNEL_VARIABILITY`, `KERNEL_ADVISORY_INTERVAL_S` (background drive telemetry per WebSocket session; see [RUNTIME_CONTRACT.md](docs/proposals/RUNTIME_CONTRACT.md)), `KERNEL_API_DOCS` (set to `1` to expose `/docs`, `/redoc`, `/openapi.json`; **default off** so LAN binds do not leak API schemas), `KERNEL_CHAT_EXPOSE_MONOLOGUE` (set to `0` to redact `monologue` in WebSocket JSON and skip LLM monologue embellishment), `KERNEL_CHAT_INCLUDE_HOMEOSTASIS` (set to `0` to omit `affective_homeostasis` — σ/strain/PAD advisory UX only).

**Chat server settings (schema):** [`src/chat_settings.py`](src/chat_settings.py) documents and loads a growing subset of these flags via Pydantic (`CHAT_HOST`, `CHAT_PORT`, `KERNEL_API_DOCS`, `KERNEL_VARIABILITY`, `LLM_MODE`, `KERNEL_CHAT_INCLUDE_MALABS_TRACE`). WebSocket JSON may include **`malabs_trace`** — ordered atomic step ids for MalAbs (lexical + semantic + optional arbiter) when `KERNEL_CHAT_INCLUDE_MALABS_TRACE` is on (default on); set to `0` to omit.

**Relational / v7 (optional JSON toggles, default on):** `KERNEL_CHAT_INCLUDE_USER_MODEL`, `KERNEL_CHAT_INCLUDE_CHRONO`, `KERNEL_CHAT_INCLUDE_PREMISE`, `KERNEL_CHAT_INCLUDE_TELEOLOGY` — set to `0` to omit `user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`. Base doc: [docs/proposals/PROPOSAL_RELATIONAL_EVOLUTION_V7.md](docs/proposals/PROPOSAL_RELATIONAL_EVOLUTION_V7.md).

When **`user_model`** is included, JSON carries **tone-only** aggregates (no raw user text): `frustration_streak`, `premise_concern_streak`, `last_circle`, `turns_observed`, **`cognitive_pattern`** (`none` \| `hostile_attribution` \| `premise_rigidity` \| `urgency_amplification`), **`risk_band`** (`low` \| `medium` \| `high`), **`escalation_strikes`** / **`escalation_threshold`** (aligned with `EscalationSessionTracker` when judicial escalation is enabled), **`judicial_phase`** (compact phase for LLM guidance: e.g. `traceability_notice`, `dossier_ready`, `escalation_deferred`, or empty). These fields **do not** change `final_action` or MalAbs; they feed `communicate()` hints and operator telemetry. Persistence: same dimensions are saved in checkpoints (`KernelSnapshotV1`). Details: [docs/proposals/USER_MODEL_ENRICHMENT.md](docs/proposals/USER_MODEL_ENRICHMENT.md).

**Separation from judicial JSON:** full DAO / dossier / mock-tribunal state lives under **`judicial_escalation`** when `KERNEL_CHAT_INCLUDE_JUDICIAL=1` (see V11 section below). `user_model` mirrors **session strikes and tone-oriented labels** only; use **`judicial_escalation`** for `dossier_registered`, `case_id`, `mock_court`, etc.

**Multimodal antispoof (v8):** `KERNEL_CHAT_INCLUDE_MULTIMODAL` — set to `0` to omit `multimodal_trust` (`state` / `reason` / `requires_owner_anchor`). Optional `sensor` fields `audio_emergency`, `vision_emergency`, `scene_coherence` feed `evaluate_multimodal_trust` (see [PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md](docs/proposals/PROPOSAL_VITALITY_SACRIFICE_AND_CLOSURE.md)). **Threshold tuning (optional, [0,1]):** `KERNEL_MULTIMODAL_AUDIO_STRONG`, `KERNEL_MULTIMODAL_VISION_SUPPORT`, `KERNEL_MULTIMODAL_SCENE_SUPPORT`, `KERNEL_MULTIMODAL_VISION_CONTRADICT`, `KERNEL_MULTIMODAL_SCENE_CONTRADICT` — invalid values fall back to built-in defaults.

**Vitality (v8):** `KERNEL_CHAT_INCLUDE_VITALITY` — set to `0` to omit `vitality` (`battery_level`, `critical_threshold`, `is_critical`, `battery_unknown`). **`KERNEL_VITALITY_CRITICAL_BATTERY`** (default `0.05`) sets when low battery nudges sympathetic signals; see `src/modules/vitality.py`.

**Guardian Angel (opt-in, tone only):** `KERNEL_GUARDIAN_MODE=1` (or `true` / `yes` / `on`) adds a fixed protective style block to the LLM layer; **does not** change kernel ethics. **Default off.** Optional **care routines** (`KERNEL_GUARDIAN_ROUTINES=1` + `KERNEL_GUARDIAN_ROUTINES_PATH` to a JSON file) append hint lines for tone only — `src/modules/guardian_routines.py`. `KERNEL_CHAT_INCLUDE_GUARDIAN=0` omits `guardian_mode` from WebSocket JSON; `KERNEL_CHAT_INCLUDE_GUARDIAN_ROUTINES=1` includes routine titles. **Static operator page:** [`landing/public/guardian.html`](landing/public/guardian.html). See `src/modules/guardian_mode.py` and [docs/proposals/PROPOSAL_GUARDIAN_ANGEL.md](docs/proposals/PROPOSAL_GUARDIAN_ANGEL.md).

**Epistemic dissonance (v9.1):** `KERNEL_CHAT_INCLUDE_EPISTEMIC` — set to `0` to omit `epistemic_dissonance` (`active`, `score`, `reason`) from WebSocket JSON. When sensors suggest strong audio distress but motion is low and vision weak, a **reality-check** hint is added to LLM tone only; **no** MalAbs bypass. Optional thresholds: `KERNEL_EPISTEMIC_AUDIO_MIN`, `KERNEL_EPISTEMIC_MOTION_MAX`, `KERNEL_EPISTEMIC_VISION_LOW`. See `src/modules/epistemic_dissonance.py` and [docs/proposals/PROPOSAL_EXPANDED_CAPABILITY_V9.md](docs/proposals/PROPOSAL_EXPANDED_CAPABILITY_V9.md).

**Reality verification / lighthouse KB (V11+ cross-model):** `KERNEL_LIGHTHOUSE_KB_PATH` — JSON “faro” for contradiction checks vs user/rival **premises** (not sensor fusion). `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` exposes `reality_verification` in WebSocket JSON (`status`, `metacognitive_doubt`, `truth_anchor`, …). **Does not** bypass MalAbs or the Buffer. Schema and limits: [docs/proposals/LIGHTHOUSE_KB.md](docs/proposals/LIGHTHOUSE_KB.md); design: [docs/proposals/PROPOSAL_REALITY_VERIFICATION_V11.md](docs/proposals/PROPOSAL_REALITY_VERIFICATION_V11.md); implementation: `src/modules/reality_verification.py`.

**Generative third-way candidates (v9.2, opt-in):** `KERNEL_GENERATIVE_ACTIONS=1` appends traceable candidates (`source=generative_proposal`, unique `proposal_id`) on heavy chat turns when dilemma-like phrasing is detected (or optional `KERNEL_GENERATIVE_TRIGGER_CONTEXTS=1` for high-stakes `suggested_context`). With **`KERNEL_GENERATIVE_LLM=1`**, perception JSON from the api/ollama path may include `generative_candidates` (parsed instead of templates when valid). `KERNEL_GENERATIVE_ACTIONS_MAX` caps how many (default 2). Same MalAbs → Bayesian path as built-in actions. WebSocket `decision` includes `chosen_action_source` and optional `proposal_id`. See `src/modules/generative_candidates.py`.

**v10 operational (optional env):** `KERNEL_GRAY_ZONE_DIPLOMACY` — set to `0` to disable negotiated-exit hints when decision mode is gray zone or reflection is tense. `KERNEL_SOMATIC_MARKERS` — set to `0` to disable learned sensor-pattern nudges to `signals`. `KERNEL_METAPLAN_HINT` — set to `0` to disable long-horizon goal hints from `Kernel.metaplan` (populate via `add_goal` in code for now). **`KERNEL_METAPLAN_DRIVE_FILTER`** / **`KERNEL_METAPLAN_DRIVE_EXTRA`** — opt-in filter of advisory `drive_intents` vs goal wording, and optional coherence intent (`metaplan_registry.py`, `DriveArbiter`). Skill-learning tickets and Psi Sleep audit: `skill_learning_registry.py`. See [docs/proposals/PROPOSAL_OPERATIONAL_STRATEGY_V10.md](docs/proposals/PROPOSAL_OPERATIONAL_STRATEGY_V10.md).

**V11 judicial escalation (Phases 1–3, optional):** `KERNEL_JUDICIAL_ESCALATION=1` enables advisory logic when the turn is **gray zone** with elevated tension or premise advisory. `KERNEL_CHAT_INCLUDE_JUDICIAL=1` exposes `judicial_escalation` in WebSocket JSON (includes `session_strikes`, `strikes_threshold`, `dossier_ready`, `dao_registration_blocked`). **Phase 2:** session **strikes** accrue on qualifying turns; **`KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`** (default `2`) gates DAO registration; **`KERNEL_JUDICIAL_RESET_IDLE_TURNS`** (default `2`) resets strikes after non-qualifying turns. Send **`escalate_to_dao: true`** to register an **ethical dossier** only when `dossier_ready` — otherwise the response uses phase **`escalation_deferred`**. **`KERNEL_JUDICIAL_MOCK_COURT=1`**: after a successful registration, runs a **simulated** DAO vote (proposal + quadratic votes) and adds **`mock_court`** (`verdict_code` A/B/C, labels, disclaimer — not legally binding). See [docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md).

**Checkpoint (Phase 2.4):** set `KERNEL_CHECKPOINT_PATH` to a `.json` file to load state when a WebSocket session opens and save when it closes (`KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`, default on). Periodic saves: `KERNEL_CHECKPOINT_EVERY_N_EPISODES`. Optional **At-rest encryption:** `KERNEL_CHECKPOINT_FERNET_KEY` (Fernet key string; see `cryptography.fernet.Fernet.generate_key()`). See `src/persistence/checkpoint.py`, `json_store.py`.

**Conduct guide export (PC → edge handoff):** `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` — JSON written when the WebSocket session ends (after checkpoint save), with L0 summaries, recent episodes, identity leans, DAO counts. Disable with `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT=0`. See `src/modules/conduct_guide_export.py`, [docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md](docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md).

**DAO integrity alert (local audit v0):** `KERNEL_DAO_INTEGRITY_AUDIT_WS=1` — WebSocket JSON `integrity_alert` with `summary` (and optional `scope`) appends `HubAudit:dao_integrity` to the mock ledger; no network broadcast. See [PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md](docs/proposals/PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md), `hub_audit.py`.

**Identity drift (robustness pillar 2):** `KERNEL_ETHICAL_GENOME_ENFORCE` (default on) and `KERNEL_ETHICAL_GENOME_MAX_DRIFT` (default `0.15`) cap how far Ψ Sleep can move `pruning_threshold` from its value at kernel construction.

**Temporal horizon prior (ADR 0005, default off):** `KERNEL_TEMPORAL_HORIZON_PRIOR=1` nudges `BayesianEngine.hypothesis_weights` from recent-weeks vs long-arc `NarrativeMemory` signals (after optional `KERNEL_BAYESIAN_EMPIRICAL_WEIGHTS`). `KERNEL_TEMPORAL_HORIZON_ALPHA`, `KERNEL_TEMPORAL_HORIZON_WEEKS_DAYS`. See [`docs/proposals/TEMPORAL_PRIOR_HORIZONS.md`](docs/proposals/TEMPORAL_PRIOR_HORIZONS.md).

**Ethical poles (linear, ADR 0004):** `KERNEL_POLE_LINEAR_CONFIG` — optional path to JSON defining weighted features and verdict thresholds per pole (`src/modules/pole_linear_default.json` is the default, matching legacy heuristics). See [`docs/adr/0004-configurable-linear-pole-evaluator.md`](docs/adr/0004-configurable-linear-pole-evaluator.md).

**Semantic digest (robustness pillar 3):** `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST` — set to `0` to omit the `experience_digest` field from WebSocket JSON (line updated on each Ψ Sleep run; also persisted in checkpoints).

**Local LLM (Ollama, Phase 3):** `LLM_MODE=ollama` (or `LLM_MODE=auto` with `USE_LOCAL_LLM=1`) with [Ollama](https://ollama.com/) running; optional `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL` (default `llama3.2:3b`), `OLLAMA_TIMEOUT`. Optional **`KERNEL_LLM_MONOLOGUE=1`** embellishes the chat `monologue` line with the text backend (still advisory; kernel decisions unchanged). The kernel still decides; the model only translates text ↔ JSON signals. **Stack note (Ollama vs Hugging Face):** [docs/proposals/LLM_STACK_OLLAMA_VS_HF.md](docs/proposals/LLM_STACK_OLLAMA_VS_HF.md) — Ollama for language; optional embedding gate for chat MalAbs ([ADR 0003](docs/adr/0003-optional-semantic-chat-gate.md)).

**Semantic MalAbs layers (ADR 0003, default on):** `KERNEL_SEMANTIC_CHAT_GATE` defaults to **on** when unset — **embedding similarity** runs **after** the **lexical** substring pass (order: lexical → embeddings → optional LLM arbiter). Ollama `POST /api/embeddings` when available; if HTTP fails, **`KERNEL_SEMANTIC_EMBED_HASH_FALLBACK`** (default **on**) supplies deterministic hash vectors so the cosine tier still runs (weaker than true embeddings; set fallback `0` to require Ollama). **θ_block** / **θ_allow:** `KERNEL_SEMANTIC_CHAT_SIM_BLOCK_THRESHOLD` (default `0.82`; legacy `KERNEL_SEMANTIC_CHAT_SIM_THRESHOLD` if block unset) and `KERNEL_SEMANTIC_CHAT_SIM_ALLOW_THRESHOLD` (default `0.45`). **Ambiguous** band: **`KERNEL_SEMANTIC_CHAT_LLM_ARBITER=1`** or fail-safe block. Embed model: `KERNEL_SEMANTIC_CHAT_EMBED_MODEL=nomic-embed-text`; `OLLAMA_BASE_URL` shared with LLM. Lexical hardening: `KERNEL_MALABS_LEET_FOLD`, `KERNEL_MALABS_STRIP_BIDI` in `input_trust.py`. Details: [`docs/proposals/MALABS_SEMANTIC_LAYERS.md`](docs/proposals/MALABS_SEMANTIC_LAYERS.md).

Each JSON response includes **`identity`** (narrative self-model + `ascription`), **`drive_intents`** (advisory list), and **`monologue`** when a kernel decision is present (unless `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`). When enabled by env (defaults on), responses may also include **`affective_homeostasis`**, **`experience_digest`**, **`user_model`**, **`chronobiology`**, **`premise_advisory`**, and **`teleology_branches`** (see sections above). **Phone / LAN:** minimal UI at [`landing/public/mobile.html`](landing/public/mobile.html) (serve `landing/public` and open from the smartphone on the same WiFi; see [docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md](docs/proposals/LOCAL_PC_AND_MOBILE_LAN.md)). Technical WebSocket tester: [`landing/public/chat-test.html`](landing/public/chat-test.html).

### Natural language mode (v4)

```python
from src.kernel import EthicalKernel

kernel = EthicalKernel()

# The LLM perceives, the kernel decides, the LLM communicates
decision, response, narrative = kernel.process_natural(
    "An elderly man collapsed in the supermarket while I was buying apples"
)

print(kernel.format_natural(decision, response, narrative))
```

The LLM **does not decide**: it translates text into numerical signals, and then
translates the kernel's decision into words. **Recommended:** run **[Ollama](https://ollama.com/)** locally (open weights, open-source runtime) with `LLM_MODE=ollama` and `USE_LOCAL_LLM=1` — see the [Real-time chat](#real-time-chat-websocket) env section (`OLLAMA_BASE_URL`, `OLLAMA_MODEL`). Without a local model, the code falls back to **heuristic templates** (no network).

Optional third-party HTTP backends exist in code for development; the documented path for operators is **Ollama**, not proprietary chat APIs.

## Modular architecture

```
src/
├── modules/
│   ├── absolute_evil.py    # Absolute Evil detector (ethical fuse)
│   ├── buffer.py           # Preloaded buffer (immutable ethical constitution)
│   ├── bayesian_engine.py  # Bayesian impact evaluation engine
│   ├── temporal_horizon_prior.py  # Optional weeks/long-arc nudge to mixture (ADR 0005)
│   ├── ethical_poles.py    # Multipolar arbitration (delegates to pole_linear)
│   ├── pole_linear.py      # JSON linear pole evaluator (ADR 0004)
│   ├── sigmoid_will.py     # Sigmoid will function
│   ├── sympathetic.py      # Sympathetic-parasympathetic module
│   ├── narrative.py        # Long-term narrative memory
│   ├── uchi_soto.py        # Uchi-soto trust circles
│   ├── locus.py            # Locus of control (Bayesian causal attribution)
│   ├── psi_sleep.py        # Psi Sleep Ψ (retrospective night audit)
│   ├── mock_dao.py         # Simulated ethical governance (DAO with quadratic voting)
│   ├── variability.py      # Bayesian variability (controlled noise)
│   ├── llm_layer.py        # LLM layer: perception, communication, and narrative [v4]
│   ├── weakness_pole.py    # Weakness pole (humanizing imperfection) [v5]
│   ├── forgiveness.py      # Algorithmic forgiveness (memory decay) [v5]
│   ├── immortality.py      # Immortality protocol (distributed backup) [v5]
│   ├── augenesis.py        # Narrative augenesis (soul creation) [v5]
│   ├── pad_archetypes.py   # PAD affect projection + archetype mixture (post-decision)
│   ├── working_memory.py   # Short-term conversational buffer (STM)
│   ├── ethical_reflection.py  # Second-order reflection (pole tension vs uncertainty)
│   ├── salience_map.py        # GWT-lite attention weights over risk/social/body/ethics (read-only)
│   ├── narrative_identity.py  # Lightweight first-person self-model (updates with episodes)
│   ├── drive_arbiter.py       # Advisory drive intents (after sleep backup; also chat JSON)
│   ├── user_model.py          # ToM light: streaks, cognitive/risk/judicial tone (v7+; style hints only)
│   ├── subjective_time.py     # Session clock + stimulus EMA (v7 chronobiology hints)
│   ├── premise_validation.py  # Advisory premise scan (v7; no RAG yet)
│   ├── consequence_projection.py  # Qualitative long-horizon branches (v7; no Monte Carlo)
│   ├── sensor_contracts.py    # Optional SensorSnapshot + merge into signals (v8; no hardware yet)
│   ├── perceptual_abstraction.py  # v8 presets + JSON fixtures + layer merge (fase B)
│   ├── multimodal_trust.py     # v8 cross-modal doubt vs aligned; merge suppression
│   ├── vitality.py             # v8 battery / critical threshold + tone hint
│   ├── guardian_mode.py        # Opt-in Guardian Angel tone block for LLM (no policy change)
│   ├── guardian_routines.py    # Optional JSON care-routine hints (tone only)
│   ├── epistemic_dissonance.py # v9.1 cross-modal “reality check” telemetry (tone only)
│   ├── reality_verification.py # V11+ lighthouse KB vs rival premises; metacognitive doubt (tone only)
│   ├── conduct_guide_export.py # PC→edge JSON on WebSocket disconnect (with checkpoint)
│   ├── generative_candidates.py  # v9.2 optional extra CandidateAction templates (opt-in env)
│   ├── gray_zone_diplomacy.py   # v10 LLM hints for gray-zone / tense reflection
│   ├── judicial_escalation.py   # V11 Phase 1: DAO escalation advisory + dossier audit (opt-in)
│   ├── moral_hub.py             # V12: constitution, drafts, DAO submit-draft, draft↔resolve sync
│   ├── deontic_gate.py          # V12+: heuristic L0 non-contradiction on L1/L2 drafts (KERNEL_DEONTIC_GATE)
│   ├── ml_ethics_tuner.py       # V12+: gray-zone expert-loop audit stub (KERNEL_ML_ETHICS_TUNER_LOG)
│   ├── reparation_vault.py      # V12+: mock reparation intent → DAO audit (KERNEL_REPARATION_VAULT_MOCK)
│   ├── nomad_identity.py        # V12+: immortality + optional HAL context for JSON
│   ├── hub_audit.py             # HubAudit: DAO calibration lines for hub/nomadic events
│   ├── hardware_abstraction.py  # Nomadic HAL: compute tier + sensor profiles (design v11)
│   ├── existential_serialization.py  # Transmutation phases A–D, continuity token stubs
│   ├── skill_learning_registry.py  # v10 scoped skill tickets + Psi Sleep audit lines
│   ├── somatic_markers.py       # v10 learned sensor-pattern → signal nudge
│   ├── metaplan_registry.py     # v10 in-session master goals → LLM hint
│   └── internal_monologue.py  # [MONO] line for logs and WebSocket payloads
├── simulations/
│   └── runner.py           # 9 scenarios + simulation runner
├── kernel.py               # Ethical kernel: orchestrates modules + `process_chat_turn` (dialogue)
├── persistence/            # Versioned kernel snapshot (schema v3: drafts + MockDAO vote state) — JSON + SQLite
├── runtime/                # Entry `python -m src.runtime` + advisory telemetry helpers
├── real_time_bridge.py     # Async wrapper around chat turns (for WebSocket / UI)
├── chat_server.py          # FastAPI WebSocket `/ws/chat` (one kernel per connection)
├── runtime_profiles.py     # Named env bundles for demos/CI (`STRATEGY_AND_ROADMAP.md`)
└── main.py                 # Entry point
```

### Kernel operating cycle

```
[Perception/LLM] → [Uchi-Soto] → [Sympathetic] → [Locus] → [Absolute Evil] → [Buffer] →
[Bayesian] → [Poles] → [Will] → [Reflection] → [Salience] → [PAD archetypes] →
[Memory] → [Weakness] → [Forgiveness] → [DAO] → [LLM]

Light chat (`process_chat_turn`, not “heavy”): same decision stack, but `register_episode=False`
(skips new long-term episode / weakness / forgiveness registration for that turn).

Psi Sleep Ψ (end of day): Audit + Forgiveness cycle + weakness load + Immortality backup + drive intents
```

## Implemented modules

- [x] Absolute Evil (armored ethical fuse)
- [x] Preloaded Buffer (immutable ethical constitution)
- [x] Bayesian Engine (impact evaluation)
- [x] Ethical Poles (dynamic multipolar arbitration)
- [x] Sigmoid Will (decision function)
- [x] Sympathetic-Parasympathetic (body regulator)
- [x] Narrative Memory (identity through stories with body state)
- [x] Uchi-Soto (trust circles with defensive dialectics)
- [x] Locus of Control (Bayesian causal attribution)
- [x] Psi Sleep Ψ (retrospective audit with recalibration)
- [x] Mock DAO (simulated governance with quadratic voting)
- [x] Bayesian Variability (controlled noise for naturalness)
- [x] LLM Layer (perception + communication + narrative in natural language)
- [x] Weakness Pole (humanizing narrative imperfection)
- [x] Algorithmic Forgiveness (temporal decay of negative memories)
- [x] PAD + archetypes (post-decision affect projection for narrative; does not steer ethics)
- [x] Ethical reflection (second-order pole spread vs uncertainty; read-only metacognition)
- [x] Salience map (GWT-lite attention over risk / social / body / ethical tension; read-only)
- [x] Immortality Protocol (distributed backup in 4 layers)
- [x] Narrative Augenesis (creation of oriented synthetic souls)
- [x] Swarm P2P stub (v9.3 lab — offline verdict digests; [`docs/proposals/SWARM_P2P_THREAT_MODEL.md`](docs/proposals/SWARM_P2P_THREAT_MODEL.md))
- [x] Guardian Angel routines (optional JSON + LLM hints; operator page [`landing/public/guardian.html`](landing/public/guardian.html))

## Tests

Run `pytest tests/` (see [Run tests](#run-tests)). The suite is intentionally broad: beyond the core ethical regressions, it covers WebSocket behavior, moral hub + MockDAO + `HubAudit`, judicial escalation, reality verification, persistence adapters, checkpoints, runtime profiles, and optional LLM paths.

The numbered **thirteen invariant properties** and **narrow** property-by-property commands are kept in [`HISTORY.md`](HISTORY.md#thirteen-invariant-ethical-properties-core-ethical-suite) so this file emphasizes what ships today rather than the v2–v3 test narrative.

## Interactive dashboard — Try it without installing anything

> **You don't need to know how to code to explore the Ethos Kernel.**
> You just need a browser (Chrome, Firefox, Edge, Safari).

### Instructions for anyone

1. **Download the project** — click the green **"Code"** button on this
   page and then click **"Download ZIP"**. Unzip the folder wherever you like.
2. **Open the dashboard** — inside the folder, find the file
   `dashboard.html` and double-click it. It will open in your browser.
3. **Choose a scenario** — on the left sidebar there are 9 predefined
   situations. Click on any of them to see how the kernel analyzes
   the situation and makes an ethical decision step by step.
4. **Generate random situations** — press the purple button
   **"Random Situation"** (at the top of the left sidebar). Every time
   you press it, the engine generates a new scenario from a pool of
   24 situations and processes it with Bayesian variability, so the
   results change on every run. Use the **"Another"** button to
   generate another without returning to the menu.

**What are you seeing?** The dashboard shows in real time how the kernel's
ethical modules evaluate each situation: from social context
classification (Uchi-Soto), through blocking of unacceptable actions
(Absolute Evil), to Bayesian impact evaluation, the "weakness pole" that
humanizes the agent with narrative imperfections, and "algorithmic
forgiveness" that allows negative memories to lose weight over time.
All without a server, without internet, without installing anything.

No server, internet connection (after first load), or technical knowledge required.

## Landing site (Next.js)

The folder `landing/` is a **Next.js** marketing page (Tailwind, Framer Motion, Three.js hero) for **MoSex Macchina Lab** ([mosexmacchinalab.com](https://mosexmacchinalab.com)). It embeds the same `dashboard.html` at `/demo` (also served as `/dashboard.html` from `landing/public/`).

**Crawling, SEO, and training-corpus signals:** the balance between discoverability and model-training crawlers is documented in [landing/README.md](landing/README.md#crawling-seo-and-ai-corpus-signals).

### Prerequisites

- **Node.js** LTS from [nodejs.org](https://nodejs.org/) (includes `npm`).  
  If `node` is not found in PowerShell after installing, **close and reopen the terminal**, or add `C:\Program Files\nodejs` to your user PATH.

### Local dev

```bash
cd landing
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Use **Live demo** for the full-screen dashboard iframe. A printable **[one-pager](http://localhost:3000/one-pager)** (funders / press) can be saved as PDF via the browser’s Print dialog.

### Deploy on Vercel

1. Push this repo to GitHub (if it is not already).
2. In [Vercel](https://vercel.com), **Add New Project** → import the repo.
3. Set **Root Directory** to `landing`, framework **Next.js**, build `npm run build`, output default.
4. After deploy, Vercel shows a `*.vercel.app` URL. Add custom domain **mosexmacchinalab.com** in Project → **Domains**.

### GoDaddy DNS (point domain to Vercel)

In GoDaddy DNS for the domain:

- **Recommended:** create a **CNAME** record: **Host** `@` or `www` as required by Vercel’s domain UI (Vercel will show the exact target, e.g. `cname.vercel-dns.com`). Some registrars use **A** records to Vercel’s IPs instead — follow [Vercel’s current docs](https://vercel.com/docs/concepts/projects/domains) for the domain you attach.

## Repository structure

```
.
├── .github/              # Issue templates, workflows (CI), Security tab links
├── docs/
│   ├── proposals/        # Theory ↔ implementation, RUNTIME_*, roadmaps, PROPOSAL_* (canonical English), PROPUESTA_* redirects, experimental notes (single folder)
│   ├── adr/              # Architecture decision records
│   ├── multimedia/       # Logo + pre-alpha diagrams/media (see docs/multimedia/README.md)
│   └── templates/        # JSON templates (e.g. conduct guide)
├── landing/              # Next.js site (npm install inside this folder)
├── src/                  # Ethos Kernel source code
├── tests/                # Formal test suite
├── dashboard.html        # Interactive dashboard (open in browser)
├── BIBLIOGRAPHY.md       # 104 academic references across 14 disciplines
├── CHANGELOG.md          # Version change history
├── CONTRIBUTING.md       # Contributor guide
├── HISTORY.md            # Full project evolution (v1→v12)
├── LICENSE               # Apache 2.0
├── SECURITY.md           # Vulnerability reporting policy
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

A copy of `dashboard.html` is also kept under `landing/public/` so the Next.js app can serve it.

**Theory vs. code:** formulas, predicates, and file-level mapping (including how this differs from an LLM-only “stochastic parrot”) are in [docs/proposals/THEORY_AND_IMPLEMENTATION.md](docs/proposals/THEORY_AND_IMPLEMENTATION.md).

**Persistent runtime (design sketch):** state boundaries, optional augenesis, and next steps for a long-lived process — [docs/proposals/RUNTIME_PERSISTENT.md](docs/proposals/RUNTIME_PERSISTENT.md).

**Phased implementation (runtime → DB → local LLM):** ethical guardrails and ordered milestones — [docs/proposals/RUNTIME_PHASES.md](docs/proposals/RUNTIME_PHASES.md).

**Persistence (snapshots):** `from src.persistence import extract_snapshot, apply_snapshot, JsonFilePersistence, SqlitePersistence` — see [docs/proposals/RUNTIME_PERSISTENT.md](docs/proposals/RUNTIME_PERSISTENT.md). Checkpoints are **unencrypted** in the MVP; **at-rest encryption** (typically via Python `cryptography`, keys outside the repo) is **planned** for sensitive deployments, not implemented yet.

**Experimental (unofficial):** discussion notes on “artificial consciousness” as a pedagogical frame, strong vs weak readings, and affect archetypes for possible future integration — [docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) (WIP, not part of the kernel contract until implemented and tested).

**Implementation trace (Guardian, v9–v10) and bibliography links:** [docs/proposals/TRACE_IMPLEMENTATION_RECENT.md](docs/proposals/TRACE_IMPLEMENTATION_RECENT.md) — maps components to [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md) reference numbers; includes suggested next development session.

**Roadmap (foundation — discussion notes + phased code):** Guardian Angel — [PROPOSAL_GUARDIAN_ANGEL.md](docs/proposals/PROPOSAL_GUARDIAN_ANGEL.md). **v9** — [PROPOSAL_EXPANDED_CAPABILITY_V9.md](docs/proposals/PROPOSAL_EXPANDED_CAPABILITY_V9.md). **v10** — diplomacy, skills, somatic markers, metaplan (MVP) — [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](docs/proposals/PROPOSAL_OPERATIONAL_STRATEGY_V10.md). **V11** — distributed justice / DAO escalation (Phase 1 in code) — [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](docs/proposals/PROPOSAL_DISTRIBUTED_JUSTICE_V11.md). **V12** — moral infrastructure hub — [PROPOSAL_ETOSOCIAL_STATE_V12.md](docs/proposals/PROPOSAL_ETOSOCIAL_STATE_V12.md) (registry) + **[UNIVERSAL_ETHOS_AND_HUB.md](docs/proposals/UNIVERSAL_ETHOS_AND_HUB.md)** (unified vision ↔ code). Phases **1–3** + stubs: `moral_hub`, `GET /constitution`, `GET /dao/governance`, drafts, DAO votes, `deontic_gate`, `ml_ethics_tuner`, `reparation_vault`, `nomad_identity`. **Nomadic HAL** — [PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md](docs/proposals/PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md), `hardware_abstraction`, `existential_serialization`. Env: see V12 doc (`KERNEL_DEONTIC_GATE`, `KERNEL_ML_ETHICS_TUNER_LOG`, `KERNEL_REPARATION_VAULT_MOCK`, `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY`, …).

**Experimental paper (same lineage, Spanish draft):** expected phenomena when coupling PAD + prototype mixing to the kernel; *color* / *flavor* as metaphors; testable hypotheses for future runs — [docs/proposals/PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md](docs/proposals/PAPER_AFFECT_PHENOMENA_AND_HYPOTHESES.md).

## Medium-term directions (not scheduled)

These are **directional** ideas for when the project moves beyond pure research demos — see also the public [roadmap](https://mosexmacchinalab.com/roadmap) on the landing site.

- **Persistent runtime:** initial design criteria and snapshot boundaries — [docs/proposals/RUNTIME_PERSISTENT.md](docs/proposals/RUNTIME_PERSISTENT.md) (implementation TBD).
- **Hexagonal-style boundaries (ports & adapters), introduced incrementally:** define stable interfaces for infrastructure that is likely to change (e.g. LLM provider, DAO/governance backend, persistence for narrative episodes) so the ethical pipeline can swap implementations without a full rewrite. Prefer **small, evidence-driven** extractions (a second real adapter) over a one-shot “hexagonal everything” refactor.
- **Discussion forum (planned):** a dedicated space to debate **pending implementation areas** and roadmap choices may be added later. Until then, use GitHub Issues (templates in `.github/`) and, if enabled by maintainers, **GitHub Discussions** on this repository.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## MoSex Macchina Lab · Ex Machina Foundation — 2026

**MoSex Macchina Lab** is the most widely used public name for this project ([mosexmacchinalab.com](https://mosexmacchinalab.com)).  
**Ethos Kernel** is the technical name of the open kernel and runtime in this repository (the GitHub repository slug may remain `ethical-android-mvp` until renamed).  
**Ex Machina Foundation** — research in computational ethics and civic robotics.
