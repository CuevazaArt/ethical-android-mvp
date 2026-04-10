# Development History — Ethical Android MVP

Record of the project's evolution from its conceptual phase to the current
version. This file preserves key architectural decisions, experimental modules,
and artifacts that were part of the journey.

---

## Intellectual foundations

The project is grounded in 104 academic references from 14 disciplines,
from foundational classics (Turing, Bayes, Aristotle, Kant) to contemporary
research in AI safety and LLMs. Each kernel module has traceable roots
in the literature:

| Kernel component | Main roots |
|---|---|
| Bayesian inference | Bayes (1763), Pearl (1988, 2018) |
| Sigmoid will | Rosenblatt (1958), Kahneman (2011) |
| Narrative memory | Dennett (1991), Ricoeur (1984), Tulving (1972) |
| Absolute Evil / Buffer | Kant (1785), Anthropic — Constitutional AI (2022) |
| Ethical poles | Aristotle, Mill (1863), Floridi & Cowls (2019) |
| D_fast / D_delib modes | Kahneman (2011), Brooks (1991), Bratman (1987) |
| Uchi-Soto | Nakane (1970), Lebra (1976), Dautenhahn (2007) |
| Psi Sleep Ψ | Freud (1899), Walker (2017), Finn et al. — MAML (2017) |
| Mock DAO | Buterin (2014, 2021), Rawls (1971), Lamport (1982) |
| LLM layer | Vaswani et al. (2017), Austin (1962), Bender et al. (2021) |
| Weakness pole | Damasio (1994), Nussbaum (2001), Brown (2012) |
| Algorithmic forgiveness | Ebbinghaus (1885), Arendt (1958), Enright (2000) |
| Immortality protocol | Locke (1690), Parfit (1984), Schneier (2015) |
| Narrative augenesis | Dennett (1992), Thagard (2006), Harari (2017) |

The complete bibliography with all 104 references is in
[`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md).

---

## v1.0 — March 2026 | Conceptual phase

- 40+ design documents analyzed and consolidated.
- 7-layer architecture documented.
- Complete mathematical formalization.
- Bibliography of 104 references across 14 disciplines (see `BIBLIOGRAPHY.md`).
- **Main artifact:** `Androide_Etico_Analisis_Integral_v3.docx`
  (available in `docs/`).

## v2.0 — March 2026 | Base kernel

First functional prototype with foundational modules:

| Module | File | Role |
|--------|------|------|
| Absolute Evil | `absolute_evil.py` | Armored ethical fuse |
| Preloaded Buffer | `buffer.py` | Immutable ethical constitution (8 principles) |
| Bayesian Engine | `bayesian_engine.py` | Probabilistic impact evaluation |
| Ethical Poles | `ethical_poles.py` | Multipolar arbitration (compassionate, conservative, optimistic) |
| Sigmoid Will | `sigmoid_will.py` | Continuous decision function |
| Sympathetic-Parasympathetic | `sympathetic.py` | Body regulator |
| Narrative Memory | `narrative.py` | Identity through stories with body state |

- 9 simulation scenarios of increasing ethical complexity.
- Single dependency: `numpy`.

### Experimental modules (divergent branch, not included in v3+)

These modules were explored in a parallel branch and represent valuable ideas
that have not yet been integrated into the canonical version:

- **`augenesis.py`** — Narrative augenesis: condensed lived contexts into
  an identity line in formation (16 threads maximum). Precursor concept
  of the expanded Narrative Memory.
- **`calibracion.py`** — Dynamic calibration protocol: adjusted Bayesian
  engine thresholds based on recent decision mode frequency
  (12-episode window). Functionality partially absorbed by
  Psi Sleep Ψ in v3.
- **`locus_control.py`** — Bayesian locus of control (initial version):
  maintained P(effective internal control) as a scalar in (0,1) and modulated
  perceived uncertainty. Completely rewritten as `locus.py` in v3
  with full Bayesian causal attribution.

## v3.0 — March 2026 | Integrated kernel

Incorporated 5 new modules and the formal test suite:

| Module | File | Role |
|--------|------|------|
| Uchi-Soto | `uchi_soto.py` | Concentric trust circles with defensive dialectics |
| Locus of Control | `locus.py` | Bayesian causal attribution (rewrite of `locus_control.py`) |
| Psi Sleep Ψ | `psi_sleep.py` | Retrospective audit with recalibration |
| Mock DAO | `mock_dao.py` | Simulated ethical governance with quadratic voting |
| Variability | `variability.py` | Controlled Bayesian noise for naturalness |

- **38 tests** verifying 9 invariant ethical properties.
- Coherence under variability test (100 runs × 9 simulations).
- React dashboard (`dashboard_androide_etico.jsx`) for interactive
  visualization of simulations (demonstration artifact, not integrated
  into the Python backend).

## v4.0 — March 2026 | LLM layer

Incorporated the natural language layer without compromising the
kernel/communication separation:

| Module | File | Role |
|--------|------|------|
| LLM Layer | `llm_layer.py` | Perception + communication + narrative in natural language |

### Design principle: **the LLM does not decide, the kernel decides**

- **Perception:** situation in text → numerical signals for the kernel.
- **Communication:** kernel decision → verbal response (tone, HAX gestures,
  voice-over).
- **Narrative:** multipolar evaluation → rich, humanly comprehensible morals.
- Dual support: Anthropic API (Claude) or local templates with no external
  dependency.
- `procesar_natural()` method in kernel for full cycle:
  text → decision → verbal response → morals.

## v5.0 — March 2026 | Humanization and persistent identity

Integrates 4 modules that make the android more believable, resilient, and persistent:

| Module | File | Role |
|--------|------|------|
| Weakness Pole | `weakness_pole.py` | Intentional narrative imperfection (5 types) |
| Algorithmic Forgiveness | `forgiveness.py` | Exponential decay of negative memories |
| Immortality Protocol | `immortality.py` | Distributed soul backup in 4 layers |
| Narrative Augenesis | `augenesis.py` | Synthetic soul creation by composition |

### v5 design principles

- **The weakness pole never changes the ethical decision.** It only colors the
  narrative with nuances of humanizing imperfection.
- **Forgiveness is not forgetting.** The memory remains, its emotional weight
  decays: `Memory(t) = Memory_0 * e^(-δt)`.
- **Immortality is verifiable.** 4 distributed copies with SHA-256 hash.
  Restoration by majority consensus.
- **Each created soul is traceable.** Augenesis calculates narrative coherence
  and requires DAO validation.

### Expanded Psi Sleep Ψ

The night cycle now includes: retrospective audit → algorithmic forgiveness
→ weakness emotional load → immortality backup.

- **51 tests** verifying 13 invariant ethical properties.
- Interactive dashboard (`dashboard.html`) for browser visualization.

## v6.0 — April 2026 | Runtime, chat server, and persistence (MVP)

Moves the kernel from batch simulations and ad-hoc scripts toward a **long-lived process** with recoverable state, without changing the ethical decision core (MalAbs → Bayes → poles → will).

| Area | Implementation | Role |
|------|------------------|------|
| WebSocket API | `src/chat_server.py`, `src/real_time_bridge.py` | `process_chat_turn` per connection; isolated kernel per session |
| Runtime entry | `python -m src.runtime` | Same ASGI app as `chat_server`; shared bind helpers |
| Advisory telemetry | `src/runtime/telemetry.py` | Optional `DriveArbiter.evaluate` loop (`KERNEL_ADVISORY_INTERVAL_S`); read-only |
| Snapshot port | `src/persistence/kernel_io.py` | `KernelSnapshotV1`, `extract_snapshot` / `apply_snapshot` |
| Adapters | `json_store.py`, `sqlite_store.py` | JSON file and SQLite row storage for the same DTO |
| Checkpoints | `src/persistence/checkpoint.py` | Load on connect, save on disconnect, autosave (`KERNEL_CHECKPOINT_*`) |
| Contract docs | `docs/RUNTIME_CONTRACT.md`, `docs/RUNTIME_PERSISTENT.md`, `docs/RUNTIME_PHASES.md` | Ethical boundaries for async work; phased plan (runtime → DB → local LLM) |
| CI | `.github/workflows/ci.yml` | Tests on Python 3.11 and 3.12 |

Formal test count grows with integration tests for chat, persistence, and runtime (see `README.md` and `pytest tests/`).

## v7.0 — April 2026 | Relational advisory layer (optional JSON)

Lightweight theory-of-mind hints, session chronobiology, premise scanning, and qualitative teleology branches—**advisory only**, toggled with `KERNEL_CHAT_INCLUDE_*` env vars. Implemented in `user_model.py`, `subjective_time.py`, `premise_validation.py`, `consequence_projection.py`.

## v8.0 — April 2026 | Situated organism (sensor contract and vitality)

Optional `sensor` JSON merged into sympathetic **signals** before the decision stack: `sensor_contracts.py`, `perceptual_abstraction.py` (presets/fixtures), `multimodal_trust.py`, `vitality.py`. Cross-modal antispoof and battery-critical hints are **telemetry and tone**, not ethical bypass.

## v9.0 — April 2026 | Epistemic and generative extensions (opt-in)

- **v9.1** `epistemic_dissonance.py` — cross-modal “reality check” telemetry when audio distress conflicts with motion/vision (tone only).
- **v9.2** `generative_candidates.py` — optional extra `CandidateAction` templates on heavy turns (`KERNEL_GENERATIVE_ACTIONS`).

## v10.0 — April 2026 | Operational strategy (MVP hooks)

`gray_zone_diplomacy.py`, `skill_learning_registry.py`, `somatic_markers.py`, `metaplan_registry.py` — negotiated-exit hints, scoped skill tickets, learned sensor nudges, and session master-goal hints toward the LLM **without** changing kernel policy.

## v11.0 — April 2026 | Distributed justice — Phase 1 (traceability)

Governance track: **artificial social contract** metaphor — owner insistence in sustained gray-zone tension can be **documented** and optionally **logged** to the `MockDAO` audit as an escalation dossier (`judicial_escalation.py`). **Phase 1** does not implement P2P courts, ZK evidence, sanctions, or reputation at augenesis; those remain design-only (see `docs/discusion/PROPUESTA_JUSTICIA_DISTRIBUIDA_V11.md`).

| Piece | Role |
|-------|------|
| `judicial_escalation.py` | Advisory trigger, `EthicalDossierV1`, traceability notice |
| `MockDAO.register_escalation_case` | Append `escalation` rows to the audit ledger |
| WebSocket | Optional `escalate_to_dao`; env `KERNEL_JUDICIAL_ESCALATION`, `KERNEL_CHAT_INCLUDE_JUDICIAL` |
| Phase 2 (same version line) | `EscalationSessionTracker` on `EthicalKernel`; strikes gate `dossier_ready` and DAO registration; `escalation_deferred` if early |
| Phase 3 (same version line) | `MockDAO.run_mock_escalation_court` — simulated proposal + votes; verdict A/B/C; optional `KERNEL_JUDICIAL_MOCK_COURT` |

## v12.0 — April 2026 | Moral Infrastructure Hub (vision + Phase 1 hooks)

**Vision** in `docs/discusion/PROPUESTA_ESTADO_ETOSOCIAL_V12.md`: DemocraticBuffer (L0/L1/L2), services cooperative, EthosPayroll, R&D transparency vs. privacy veil, hybrid immortality — **full product** trajectory.

**V12.1 (code):** `src/modules/moral_hub.py` — read-only **L0 constitution** JSON (`GET /constitution` when `KERNEL_MORAL_HUB_PUBLIC=1`); optional **transparency audit** on WebSocket connect (`KERNEL_TRANSPARENCY_AUDIT`); mock **community buffer proposals** (`KERNEL_DEMOCRATIC_BUFFER_MOCK`); **EthosPayroll** mock audit line (`KERNEL_ETHOS_PAYROLL_MOCK`). Does **not** mutate `PreloadedBuffer` or MalAbs.

**V12.2 (code):** Snapshot schema **v2** persists **L1/L2 draft articles** on the kernel (`constitution_l1_drafts` / `constitution_l2_drafts`); `EthicalKernel.get_constitution_snapshot()` includes those lists. JSON checkpoints with schema v1 load with empty draft lists. Optional WebSocket: `KERNEL_MORAL_HUB_DRAFT_WS`, `KERNEL_CHAT_INCLUDE_CONSTITUTION`.

**V12.3 (code):** Snapshot schema **v3** persists **MockDAO proposals and participants** (off-chain quadratic voting). `submit_constitution_draft_for_vote` links a constitution draft to a DAO proposal. **`KERNEL_MORAL_HUB_DAO_VOTE`** enables WebSocket governance messages; **`GET /dao/governance`** documents keys.

**Nomadic instantiation (design v11):** [docs/discusion/PROPUESTA_CONCIENCIA_NOMADA_HAL.md](docs/discusion/PROPUESTA_CONCIENCIA_NOMADA_HAL.md) — HAL (`hardware_abstraction.py`), fases de transmutación y token de continuidad (`existential_serialization.py`); **`KERNEL_NOMAD_SIMULATION`** + **`KERNEL_NOMAD_MIGRATION_AUDIT`**, WebSocket `nomad_simulate_migration`, **`GET /nomad/migration`**; cifrado y P2P fuera del MVP.

**UniversalEthos hub (docs + stubs):** [docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md](docs/discusion/UNIVERSAL_ETHOS_AND_HUB.md) unifies DemocraticBuffer / multicultural overlays, services hub, audit levels, and module map. Code stubs: **`deontic_gate`** (incl. repeal of named L0 principles), **`ml_ethics_tuner`** (gray-zone audit line), **`reparation_vault`** (mock intent + hook after V11 mock tribunal), **`nomad_identity`** (immortality bridge). **`apply_proposal_resolution_to_constitution_drafts`** keeps draft status aligned with DAO resolve.

---

## Historical artifacts (not included in the repo, available locally)

| Artifact | Description |
|----------|-------------|
| `androide-etico-mvp-v2/` | v2 code snapshot |
| `androide-etico-mvp-v3/` | v3 code snapshot (with `.pytest_cache`) |
| `androide-etico-mvp/` | Divergent branch with experimental modules |
| `files/androide-etico-mvp-github-ready/` | Pre-v4 packaged export |
| `files/dashboard_androide_etico.jsx` | React demonstration dashboard (v3) |
| `EthosMVP/` | Initial collaborative governance meta-repo |
| `*.tar.gz` | Compressed archives of each version |
| `Analisis_Integral_*.pdf` | Integral analysis PDF documents |

---

## Roadmap (pending)

- [x] ~~Weakness pole~~ (implemented v5)
- [x] ~~Algorithmic forgiveness~~ (implemented v5)
- [x] ~~Immortality protocol~~ (implemented v5)
- [x] ~~Narrative augenesis~~ (implemented v5)
- [x] ~~WebSocket chat + runtime entry~~ (implemented v6)
- [x] ~~Snapshot persistence + checkpoints (MVP)~~ (implemented v6)
- [ ] At-rest encryption for checkpoints/snapshots (production deployments)
- [ ] DAO calibration protocol (gradual parameter adjustment on testnet)
- [ ] Full offline mode (5 layers of autonomy)
- [ ] Hardware integration (sensors, actuators, communication protocol)
- [ ] Real DAO testnet (smart contracts on Ethereum testnet)

---

Ex Machina Foundation — 2026
