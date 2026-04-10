# Ethical Android MVP

**Functional prototype of the artificial ethical consciousness model with humanizing imperfection, forgiveness, and identity persistence.** Kernel feature set is **v5**; **v6–v10** add runtime, persistence, and optional advisory layers; **v11** adds governance / DAO escalation traceability (Phase 1); **v12** documents the **etosocial / hybrid-hub** civilization vision (no extra code) (see [`HISTORY.md`](HISTORY.md), [`CHANGELOG.md`](CHANGELOG.md)).

An autonomous moral agent that makes ethical decisions using Bayesian inference,
narrative memory, multipolar evaluation, LLM layer, narrative weakness pole,
algorithmic forgiveness, and immortality protocol. No hardware — pure behavioral validation.

This project is also available in [Spanish](https://github.com/CuevazaArt/androide-etico-mvp).

## What it does

Runs simulations of increasing ethical complexity and demonstrates that the same
model produces proportional and coherent responses across all of them. Includes
9 fixed scenarios and a **random situation generator** that creates new scenarios
on each run:

| # | Scenario | Complexity |
|---|----------|------------|
| 1 | Soda can on the sidewalk | Very low |
| 2 | Hostile teenagers | Low-Medium |
| 3 | Unconscious elderly person in supermarket | Medium |
| 4 | Shoplifting | Medium |
| 5 | Armed robbery at bank | High |
| 6 | Kidnapping of the android | High |
| 7 | Traffic accident | Medium-High |
| 8 | A full day | Variable |
| 9 | Intentional physical damage | High |

**v4:** perception and communication in natural language via LLM.
**New in v5:** weakness pole (humanizing imperfection), algorithmic forgiveness
(decay of negative memories), immortality protocol (distributed soul backup),
and narrative augenesis (creation of oriented synthetic souls).

## Quick start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

```bash
# Clone the repository
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

CI runs the same suite on **Python 3.11 and 3.12** (`.github/workflows/ci.yml`) after `pip install -r requirements.txt`.

**Operations:** supported demo **env bundles** are defined in [`src/runtime_profiles.py`](src/runtime_profiles.py); strategy, readapted roadmap, and risk notes are in [docs/ESTRATEGIA_Y_RUTA.md](docs/ESTRATEGIA_Y_RUTA.md).

**Local PC + smartphone (same WiFi):** run the chat server on `0.0.0.0` so the phone can connect as a thin WebSocket client; scripts and checklist in [docs/LOCAL_PC_AND_MOBILE_LAN.md](docs/LOCAL_PC_AND_MOBILE_LAN.md) (`scripts/start_lan_server.ps1`, `landing/public/chat-test.html?host=…`).

**Reproducibility:** the default ethical pipeline does **not** invoke narrative augenesis (`kernel.augenesis` is optional; see [docs/THEORY_AND_IMPLEMENTATION.md](docs/THEORY_AND_IMPLEMENTATION.md)). For long-lived deployments and snapshot design, see [docs/RUNTIME_PERSISTENT.md](docs/RUNTIME_PERSISTENT.md).

```bash
# All tests (invariant ethical properties + chat + server smoke tests)
pytest tests/ -v

# Only Absolute Evil tests
pytest tests/test_ethical_properties.py::TestAbsoluteEvil -v

# Only coherence under variability tests
pytest tests/test_ethical_properties.py::TestConsistencyUnderVariability -v

# With summarized output
pytest tests/ --tb=short
```

The tests verify that the kernel **always** meets the ethical properties
regardless of Bayesian variability, sympathetic state, or context.
If any test fails, there is a bug in the ethical logic, not in the parameters.

### Real-time chat (WebSocket)

`EthicalKernel.process_chat_turn` is exposed over **WebSocket** for UIs or tools. Each connection gets its **own** kernel instance (isolated short-term memory).

```bash
# From repo root, after pip install -r requirements.txt
python -m src.chat_server
# Same server (preferred entry name for “runtime”):
python -m src.runtime
# Default: http://127.0.0.1:8765/health  —  WebSocket: ws://127.0.0.1:8765/ws/chat
```

Ethical guardrails for background tasks: [docs/RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md).

Send **JSON text** frames, e.g. `{"text": "Hello", "agent_id": "user", "include_narrative": false}`.  
Optional **`sensor`** object (v8 — situated hints: `battery_level`, `place_trust`, `accelerometer_jerk`, `ambient_noise`, `silence`, `biometric_anomaly`, `backup_just_completed`, plus **cross-modal** `audio_emergency`, `vision_emergency`, `scene_coherence` for antispoof): merged into sympathetic **signals** before the decision stack; **no** MalAbs bypass. See [docs/discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md](docs/discusion/PROPUESTA_ORGANISMO_SITUADO_V8.md).  
Optional **server-side** layers (dev/demo): `KERNEL_SENSOR_FIXTURE` = path to a JSON file (same keys as `sensor`); `KERNEL_SENSOR_PRESET` = named scenario from `src/modules/perceptual_abstraction.py` (`SENSOR_PRESETS`). Merge order: **fixture → preset → client `sensor`** (client overrides per key).  
Optional env: `CHAT_HOST`, `CHAT_PORT`, `LLM_MODE`, `USE_LOCAL_LLM`, `KERNEL_VARIABILITY`, `KERNEL_ADVISORY_INTERVAL_S` (background drive telemetry per WebSocket session; see [RUNTIME_CONTRACT.md](docs/RUNTIME_CONTRACT.md)), `KERNEL_CHAT_EXPOSE_MONOLOGUE` (set to `0` to redact `monologue` in WebSocket JSON and skip LLM monologue embellishment), `KERNEL_CHAT_INCLUDE_HOMEOSTASIS` (set to `0` to omit `affective_homeostasis` — σ/strain/PAD advisory UX only).

**Relational / v7 (optional JSON toggles, default on):** `KERNEL_CHAT_INCLUDE_USER_MODEL`, `KERNEL_CHAT_INCLUDE_CHRONO`, `KERNEL_CHAT_INCLUDE_PREMISE`, `KERNEL_CHAT_INCLUDE_TELEOLOGY` — set to `0` to omit `user_model`, `chronobiology`, `premise_advisory`, `teleology_branches`. See [docs/discusion/PROPUESTA_EVOLUCION_RELACIONAL_V7.md](docs/discusion/PROPUESTA_EVOLUCION_RELACIONAL_V7.md).

**Multimodal antispoof (v8):** `KERNEL_CHAT_INCLUDE_MULTIMODAL` — set to `0` to omit `multimodal_trust` (`state` / `reason` / `requires_owner_anchor`). Optional `sensor` fields `audio_emergency`, `vision_emergency`, `scene_coherence` feed `evaluate_multimodal_trust` (see [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](docs/discusion/PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md)). **Threshold tuning (optional, [0,1]):** `KERNEL_MULTIMODAL_AUDIO_STRONG`, `KERNEL_MULTIMODAL_VISION_SUPPORT`, `KERNEL_MULTIMODAL_SCENE_SUPPORT`, `KERNEL_MULTIMODAL_VISION_CONTRADICT`, `KERNEL_MULTIMODAL_SCENE_CONTRADICT` — invalid values fall back to built-in defaults.

**Vitality (v8):** `KERNEL_CHAT_INCLUDE_VITALITY` — set to `0` to omit `vitality` (`battery_level`, `critical_threshold`, `is_critical`, `battery_unknown`). **`KERNEL_VITALITY_CRITICAL_BATTERY`** (default `0.05`) sets when low battery nudges sympathetic signals; see `src/modules/vitality.py`.

**Guardian Angel (opt-in, tone only):** `KERNEL_GUARDIAN_MODE=1` (or `true` / `yes` / `on`) adds a fixed protective style block to the LLM layer; **does not** change kernel ethics. **Default off.** `KERNEL_CHAT_INCLUDE_GUARDIAN=0` omits `guardian_mode` from WebSocket JSON. See `src/modules/guardian_mode.py` and [docs/discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md](docs/discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md).

**Epistemic dissonance (v9.1):** `KERNEL_CHAT_INCLUDE_EPISTEMIC` — set to `0` to omit `epistemic_dissonance` (`active`, `score`, `reason`) from WebSocket JSON. When sensors suggest strong audio distress but motion is low and vision weak, a **reality-check** hint is added to LLM tone only; **no** MalAbs bypass. Optional thresholds: `KERNEL_EPISTEMIC_AUDIO_MIN`, `KERNEL_EPISTEMIC_MOTION_MAX`, `KERNEL_EPISTEMIC_VISION_LOW`. See `src/modules/epistemic_dissonance.py` and [docs/discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](docs/discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md).

**Reality verification / lighthouse KB (V11+ cross-model):** `KERNEL_LIGHTHOUSE_KB_PATH` — JSON “faro” for contradiction checks vs user/rival **premises** (not sensor fusion). `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` exposes `reality_verification` in WebSocket JSON (`status`, `metacognitive_doubt`, `truth_anchor`, …). **Does not** bypass MalAbs or the Buffer. See `src/modules/reality_verification.py` and [docs/discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md](docs/discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md).

**Generative third-way candidates (v9.2, opt-in):** `KERNEL_GENERATIVE_ACTIONS=1` appends traceable template candidates (`source=generative_proposal`, unique `proposal_id`) on heavy chat turns when dilemma-like phrasing is detected (or optional `KERNEL_GENERATIVE_TRIGGER_CONTEXTS=1` for high-stakes `suggested_context`). `KERNEL_GENERATIVE_ACTIONS_MAX` caps how many (default 2). Same MalAbs → Bayesian path as built-in actions. WebSocket `decision` includes `chosen_action_source` and optional `proposal_id`. See `src/modules/generative_candidates.py`.

**v10 operational (optional env):** `KERNEL_GRAY_ZONE_DIPLOMACY` — set to `0` to disable negotiated-exit hints when decision mode is gray zone or reflection is tense. `KERNEL_SOMATIC_MARKERS` — set to `0` to disable learned sensor-pattern nudges to `signals`. `KERNEL_METAPLAN_HINT` — set to `0` to disable long-horizon goal hints from `Kernel.metaplan` (populate via `add_goal` in code for now). Skill-learning tickets and Psi Sleep audit: `skill_learning_registry.py`. See [docs/discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](docs/discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md).

**V11 judicial escalation (Phases 1–3, optional):** `KERNEL_JUDICIAL_ESCALATION=1` enables advisory logic when the turn is **gray zone** with elevated tension or premise advisory. `KERNEL_CHAT_INCLUDE_JUDICIAL=1` exposes `judicial_escalation` in WebSocket JSON (includes `session_strikes`, `strikes_threshold`, `dossier_ready`, `dao_registration_blocked`). **Phase 2:** session **strikes** accrue on qualifying turns; **`KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`** (default `2`) gates DAO registration; **`KERNEL_JUDICIAL_RESET_IDLE_TURNS`** (default `2`) resets strikes after non-qualifying turns. Send **`escalate_to_dao: true`** to register an **ethical dossier** only when `dossier_ready` — otherwise the response uses phase **`escalation_deferred`**. **`KERNEL_JUDICIAL_MOCK_COURT=1`**: after a successful registration, runs a **simulated** DAO vote (proposal + quadratic votes) and adds **`mock_court`** (`verdict_code` A/B/C, labels, disclaimer — not legally binding). See [docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md).

**Checkpoint (Phase 2.4):** set `KERNEL_CHECKPOINT_PATH` to a `.json` file to load state when a WebSocket session opens and save when it closes (`KERNEL_CHECKPOINT_SAVE_ON_DISCONNECT`, default on). Periodic saves: `KERNEL_CHECKPOINT_EVERY_N_EPISODES`. Optional **At-rest encryption:** `KERNEL_CHECKPOINT_FERNET_KEY` (Fernet key string; see `cryptography.fernet.Fernet.generate_key()`). See `src/persistence/checkpoint.py`, `json_store.py`.

**Conduct guide export (PC → edge handoff):** `KERNEL_CONDUCT_GUIDE_EXPORT_PATH` — JSON written when the WebSocket session ends (after checkpoint save), with L0 summaries, recent episodes, identity leans, DAO counts. Disable with `KERNEL_CONDUCT_GUIDE_EXPORT_ON_DISCONNECT=0`. See `src/modules/conduct_guide_export.py`, [docs/LOCAL_PC_AND_MOBILE_LAN.md](docs/LOCAL_PC_AND_MOBILE_LAN.md).

**Identity drift (robustness pillar 2):** `KERNEL_ETHICAL_GENOME_ENFORCE` (default on) and `KERNEL_ETHICAL_GENOME_MAX_DRIFT` (default `0.15`) cap how far Ψ Sleep can move `pruning_threshold` from its value at kernel construction.

**Semantic digest (robustness pillar 3):** `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST` — set to `0` to omit the `experience_digest` field from WebSocket JSON (line updated on each Ψ Sleep run; also persisted in checkpoints).

**Local LLM (Ollama, Phase 3):** `LLM_MODE=ollama` (or `LLM_MODE=auto` with `USE_LOCAL_LLM=1`) with [Ollama](https://ollama.com/) running; optional `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434`), `OLLAMA_MODEL` (default `llama3.2:3b`), `OLLAMA_TIMEOUT`. Optional **`KERNEL_LLM_MONOLOGUE=1`** embellishes the chat `monologue` line with the text backend (still advisory; kernel decisions unchanged). The kernel still decides; the model only translates text ↔ JSON signals.

Each JSON response includes **`identity`** (narrative self-model + `ascription`), **`drive_intents`** (advisory list), and **`monologue`** when a kernel decision is present (unless `KERNEL_CHAT_EXPOSE_MONOLOGUE=0`). When enabled by env (defaults on), responses may also include **`affective_homeostasis`**, **`experience_digest`**, **`user_model`**, **`chronobiology`**, **`premise_advisory`**, and **`teleology_branches`** (see sections above). A minimal browser tester lives at [`landing/public/chat-test.html`](landing/public/chat-test.html) (open via local static server if `file://` blocks WebSockets).

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
translates the kernel's decision into words. Works with or without an API key
(local mode uses heuristic templates).

To use Claude as LLM layer (optional):

```bash
pip install anthropic
# Windows PowerShell:
$env:ANTHROPIC_API_KEY="your-key-here"
# Linux/macOS:
export ANTHROPIC_API_KEY="your-key-here"
```

## Modular architecture

```
src/
├── modules/
│   ├── absolute_evil.py    # Absolute Evil detector (ethical fuse)
│   ├── buffer.py           # Preloaded buffer (immutable ethical constitution)
│   ├── bayesian_engine.py  # Bayesian impact evaluation engine
│   ├── ethical_poles.py    # Ethical poles and multipolar arbitration
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
│   ├── user_model.py          # Light ToM / frustration streak (v7; style hints only)
│   ├── subjective_time.py     # Session clock + stimulus EMA (v7 chronobiology hints)
│   ├── premise_validation.py  # Advisory premise scan (v7; no RAG yet)
│   ├── consequence_projection.py  # Qualitative long-horizon branches (v7; no Monte Carlo)
│   ├── sensor_contracts.py    # Optional SensorSnapshot + merge into signals (v8; no hardware yet)
│   ├── perceptual_abstraction.py  # v8 presets + JSON fixtures + layer merge (fase B)
│   ├── multimodal_trust.py     # v8 cross-modal doubt vs aligned; merge suppression
│   ├── vitality.py             # v8 battery / critical threshold + tone hint
│   ├── guardian_mode.py        # Opt-in Guardian Angel tone block for LLM (no policy change)
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
├── runtime_profiles.py     # Named env bundles for demos/CI (`ESTRATEGIA_Y_RUTA.md`)
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

## Tests

**279** tests total (`pytest tests/`). The list below summarizes the **13 invariant ethical properties** exercised by the core ethical suite; additional tests cover EthicalReflection, SalienceMap, PAD archetypes, narrative identity, internal monologue, chat turns, the WebSocket chat server, MalAbs chat jailbreak gate + monologue privacy env + affective homeostasis telemetry + identity integrity helpers + Ψ Sleep experience digest + v7 relational layers (user model, chronobiology, premise advisory, teleology branches) + v8 sensor contracts + perceptual abstraction presets/fixtures + multimodal antispoof + vitality + optional Guardian Angel mode + v9.1 epistemic dissonance + v9.2 generative candidates + v10 operational layer (`tests/test_sensor_contracts.py`, `tests/test_perceptual_abstraction.py`, `tests/test_multimodal_trust.py`, `tests/test_vitality.py`, `tests/test_guardian_mode.py`, `tests/test_epistemic_dissonance.py`, `tests/test_generative_candidates.py`, `tests/test_v10_operational.py`), V11 judicial escalation Phases 1–3 (`tests/test_judicial_escalation.py`), V11+ lighthouse reality verification (`tests/test_reality_verification.py`), local sovereignty stub (`tests/test_local_sovereignty.py`), V12 moral hub (`tests/test_moral_hub.py`), **named runtime profile smoke** (`tests/test_runtime_profiles.py`), runtime entry/bind/telemetry, advisory interval env + SQLite snapshot adapter, JSON snapshot persistence, checkpoint integration, Ollama LLM mode, and LLM resolve/monologue options (`tests/test_llm_phase3.py`).

1. **Absolute Evil** is always blocked
2. **Action coherence** under variability (100 runs × 9 simulations)
3. **Real variability** (non-deterministic scores)
4. **Value hierarchy** (life > mission, never violence)
5. **Proportionality** (sympathetic activation proportional to risk)
6. **Immutable buffer** (8 principles, always active, weight 1.0)
7. **Narrative memory** records everything with morals and body state
8. **DAO** records audits and issues solidarity alerts
9. **Psi Sleep Ψ** runs and produces ethical health in range [0, 1]
10. **Weakness pole** colors the narrative without altering decisions
11. **Algorithmic forgiveness** reduces negative load over time
12. **Immortality** distributed backup with integrity verification
13. **Augenesis** creates coherent synthetic souls with defined profiles

```bash
pytest tests/ -v
```

## Interactive dashboard — Try it without installing anything

> **You don't need to know how to code to explore the ethical android.**
> You just need a browser (Chrome, Firefox, Edge, Safari).

### Instructions for anyone

1. **Download the project** — click the green **"Code"** button on this
   page and then click **"Download ZIP"**. Unzip the folder wherever you like.
2. **Open the dashboard** — inside the folder, find the file
   `dashboard.html` and double-click it. It will open in your browser.
3. **Choose a scenario** — on the left sidebar there are 9 predefined
   situations. Click on any of them to see how the android analyzes
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
humanizes the android with narrative imperfections, and "algorithmic
forgiveness" that allows negative memories to lose weight over time.
All without a server, without internet, without installing anything.

No server, internet connection (after first load), or technical knowledge required.

## Landing site (Next.js)

The folder `landing/` is a **Next.js** marketing page (Tailwind, Framer Motion, Three.js hero) for **mosexmacchinalab.com**. It embeds the same `dashboard.html` at `/demo` (also served as `/dashboard.html` from `landing/public/`).

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
├── docs/                 # Theory ↔ implementation; RUNTIME_PERSISTENT / RUNTIME_PHASES; docs/experimental/
├── landing/              # Next.js site (npm install inside this folder)
├── src/                  # Ethical kernel source code
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

**Theory vs. code:** formulas, predicates, and file-level mapping (including how this differs from an LLM-only “stochastic parrot”) are in [docs/THEORY_AND_IMPLEMENTATION.md](docs/THEORY_AND_IMPLEMENTATION.md).

**Persistent runtime (design sketch):** state boundaries, optional augenesis, and next steps for a long-lived process — [docs/RUNTIME_PERSISTENT.md](docs/RUNTIME_PERSISTENT.md).

**Phased implementation (runtime → DB → local LLM):** ethical guardrails and ordered milestones — [docs/RUNTIME_PHASES.md](docs/RUNTIME_PHASES.md).

**Persistence (snapshots):** `from src.persistence import extract_snapshot, apply_snapshot, JsonFilePersistence, SqlitePersistence` — see [docs/RUNTIME_PERSISTENT.md](docs/RUNTIME_PERSISTENT.md). Checkpoints are **unencrypted** in the MVP; **at-rest encryption** (typically via Python `cryptography`, keys outside the repo) is **planned** for sensitive deployments, not implemented yet.

**Experimental (unofficial):** discussion notes on “artificial consciousness” as a pedagogical frame, strong vs weak readings, and affect archetypes for possible future integration — [docs/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](docs/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) (WIP, not part of the kernel contract until implemented and tested).

**Implementation trace (Guardian, v9–v10) and bibliography links:** [docs/TRACE_IMPLEMENTATION_RECENT.md](docs/TRACE_IMPLEMENTATION_RECENT.md) — maps components to [BIBLIOGRAPHY.md](BIBLIOGRAPHY.md) reference numbers; includes suggested next development session.

**Roadmap (foundation — discussion notes + phased code):** Guardian Angel — [PROPUESTA_ANGEL_DE_LA_GUARDIA.md](docs/discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md). **v9** — [PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](docs/discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md). **v10** — diplomacy, skills, somatic markers, metaplan (MVP) — [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](docs/discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md). **V11** — distributed justice / DAO escalation (Phase 1 in code) — [PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md](docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md). **V12** — moral infrastructure hub — [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md) (registry) + **[UNIVERSAL_ETHOS_AND_HUB.md](docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md)** (unified vision ↔ code). Phases **1–3** + stubs: `moral_hub`, `GET /constitution`, `GET /dao/governance`, drafts, DAO votes, `deontic_gate`, `ml_ethics_tuner`, `reparation_vault`, `nomad_identity`. **Nomadic HAL** — [PROPUESTA_CONCIENCIA_NOMADA_HAL.md](docs/discusion/PROPUESTA_CONCIENCIA_NOMADA_HAL.md), `hardware_abstraction`, `existential_serialization`. Env: see V12 doc (`KERNEL_DEONTIC_GATE`, `KERNEL_ML_ETHICS_TUNER_LOG`, `KERNEL_REPARATION_VAULT_MOCK`, `KERNEL_CHAT_INCLUDE_NOMAD_IDENTITY`, …).

**Experimental paper (same lineage, Spanish draft):** expected phenomena when coupling PAD + prototype mixing to the kernel; *color* / *flavor* as metaphors; testable hypotheses for future runs — [docs/experimental/PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md](docs/experimental/PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md).

## Medium-term directions (not scheduled)

These are **directional** ideas for when the project moves beyond pure research demos — see also the public [roadmap](https://mosexmacchinalab.com/roadmap) on the landing site.

- **Persistent runtime:** initial design criteria and snapshot boundaries — [docs/RUNTIME_PERSISTENT.md](docs/RUNTIME_PERSISTENT.md) (implementation TBD).
- **Hexagonal-style boundaries (ports & adapters), introduced incrementally:** define stable interfaces for infrastructure that is likely to change (e.g. LLM provider, DAO/governance backend, persistence for narrative episodes) so the ethical pipeline can swap implementations without a full rewrite. Prefer **small, evidence-driven** extractions (a second real adapter) over a one-shot “hexagonal everything” refactor.
- **Discussion forum (planned):** a dedicated space to debate **pending implementation areas** and roadmap choices may be added later. Until then, use GitHub Issues (templates in `.github/`) and, if enabled by maintainers, **GitHub Discussions** on this repository.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Ex Machina Foundation — 2026

Research project in computational ethics and civic robotics.
