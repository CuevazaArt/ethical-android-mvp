# Development History — Ethos Kernel

Record of the project's evolution from its conceptual phase to the current
version. This file preserves key architectural decisions, experimental modules,
and artifacts that were part of the journey.

The open kernel + runtime is branded **Ethos Kernel** (April 2026 onward); earlier docs and mirrors may still say “Ethical Android MVP.” The GitHub repository slug may remain `ethical-android-mvp` until renamed.

---

## Intellectual foundations

The project is grounded in a broad academic literature, from foundational classics (Turing, Bayes, Aristotle, Kant) to contemporary research in AI safety and LLMs. Each kernel module has traceable roots in that literature. A consolidated **104-reference** table previously lived in **`BIBLIOGRAPHY.md`** at the repository root; that file was **removed** from the default tree in April 2026 to reduce weight — recover it from git history or from branch **`backup/main-2026-04-10`** if needed.

| Kernel component | Main roots |
|---|---|
| Bayesian inference | Bayes (1763), Pearl (1988, 2018) |
| Sigmoid will | Rosenblatt (1958), Kahneman (2011) |
| Narrative memory | Dennett (1991), Ricoeur (1984), Tulving (1972) |
| Absolute Evil / Buffer | Kant (1785); Constitutional AI / RLHF safety line (Bai et al.; contemporary AI safety literature) |
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

---

## Pre-alpha Spanish corpus (2026) — integrated archive

Before the **`docs/proposals/`** layout, the project circulated a **pre-alpha documentation bundle** (working folder `prealphaDocs/`): Spanish registration draft **v1.0 (2026)**, diagram PNGs, a **Spanish bibliography draft**, and generated JPG/MP4. That narrative is **not** the live specification of the current Python kernel; the canonical theory ↔ code map is **[`docs/proposals/README.md`](docs/proposals/README.md)**. The former consolidated reference table was removed with **`BIBLIOGRAPHY.md`** (April 2026); use git history or **`backup/main-2026-04-10`** to retrieve it.

The following **digest** condenses the former **`androide_etico_alpha_v1.0_2026.md`** (full prose removed from the tree in favor of this section):

- **Working title:** *Androide con conciencia artificial y ecosistema ético colaborativo* — civic android with narrative identity, Bayesian ethical decision-making, and **DAO-style governance** as an external audit/oracle layer (design intent, not the current mock-DAO scope).
- **Founding principles (design):** ethics-by-architecture; explainability in natural language; distributed governance (no single actor owns values); **narrative identity**; institutionalized compassion with reparative follow-up when harm is unavoidable.
- **Seven functional layers (conceptual stack):** (1) physical hardware / immutable value shielding; (2) perception & attention with ethical filtering; (3) world model & explicit causality; (4) deliberative ethical evaluation (impact, resonance, uncertainty); (5) action selection with a **moral compass**; (6) adaptive learning (ML/RL/meta-learning); (7) **DAO–ethical oracle** for social consensus and external audit.
- **Distributed Python prototype (sketch):** four bodily nodes (head / torso / arm / leg) over a **P2P mesh** — resilience if a limb node fails; open design note on **offline / partitioned** operation for complex deliberation.
- **Formal core (sketch):** sigmoid **will**, constrained optimization, Bayesian inference, predicate logic over ethical categories (e.g. Good / Evil / Gray / Absolute Evil), neural activation functions — aimed at **auditable** decisions.
- **Long-horizon narrative memory, DAO-oracle, humanization, HAX trust UX, simulation catalog, ML strategy, licensing / business framing, phased rollout, and investor-oriented value proposition** were developed in the same document at varying depth; they **foreshadow** modules that later became `uchi_soto`, `weighted_ethics_scorer` (historical path `bayesian_engine`), `mock_dao`, `narrative`, `llm_layer`, etc., but **do not** match file-level APIs today.

**Spanish bibliography draft:** an archival table by discipline (classic vs modern sources) was merged conceptually into the project’s citation practice; the detailed numbered table that replaced it was versioned as **`BIBLIOGRAPHY.md`** until April 2026 (removed from the default tree).

**PDF / Word companions (not in git):** `.gitignore` excludes `*.pdf` / `*.docx`. Local bundles from the same era sometimes included exports such as `androide_etico_alpha.docx`, thematic PDFs on DAO-oracle, narrative memory, and consciousness sketches; keep those only in **foundation archives** outside the repo if you still have them.

**Multimedia:** not versioned in this repository (recover prior `docs/multimedia/` from git history or backup branches if needed).

---

## v1.0 — March 2026 | Conceptual phase

- 40+ design documents analyzed and consolidated.
- 7-layer architecture documented.
- Complete mathematical formalization.
- Bibliography work (104 references across 14 disciplines) was tracked in a dedicated file until April 2026 (removed from the default tree; see [`CHANGELOG.md`](CHANGELOG.md)).
- **Main artifact:** `Androide_Etico_Analisis_Integral_v3.docx`
  (available in `docs/`).

## v2.0 — March 2026 | Base kernel

First functional prototype with foundational modules:

| Module | File | Role |
|--------|------|------|
| Absolute Evil | `absolute_evil.py` | Armored ethical fuse |
| Preloaded Buffer | `buffer.py` | Immutable ethical constitution (8 principles) |
| Weighted ethics scorer | `weighted_ethics_scorer.py` | Fixed mixture impact + pruning (not full Bayes; `bayesian_engine.py` shim) |
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
- Dual support: **[Ollama](https://ollama.com/)** (local, open-source runtime) or heuristic templates with no external dependency.
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
- Root static dashboard HTML (historical `dashboard.html`) was removed from the tree in 2026; recover from git if needed for browser visualization demos.

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
| Contract docs | `docs/proposals/README.md`, `docs/proposals/README.md`, `docs/proposals/README.md` | Ethical boundaries for async work; phased plan (runtime → DB → local LLM) |
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

Governance track: **artificial social contract** metaphor — owner insistence in sustained gray-zone tension can be **documented** and optionally **logged** to the `MockDAO` audit as an escalation dossier (`judicial_escalation.py`). **Phase 1** does not implement P2P courts, ZK evidence, sanctions, or reputation at augenesis; those remain design-only (see `docs/proposals/README.md`).

| Piece | Role |
|-------|------|
| `judicial_escalation.py` | Advisory trigger, `EthicalDossierV1`, traceability notice |
| `MockDAO.register_escalation_case` | Append `escalation` rows to the audit ledger |
| WebSocket | Optional `escalate_to_dao`; env `KERNEL_JUDICIAL_ESCALATION`, `KERNEL_CHAT_INCLUDE_JUDICIAL` |
| Phase 2 (same version line) | `EscalationSessionTracker` on `EthicalKernel`; strikes gate `dossier_ready` and DAO registration; `escalation_deferred` if early |
| Phase 3 (same version line) | `MockDAO.run_mock_escalation_court` — simulated proposal + votes; verdict A/B/C; optional `KERNEL_JUDICIAL_MOCK_COURT` |

## v12.0 — April 2026 | Moral Infrastructure Hub (vision + Phase 1 hooks)

**Vision** in `docs/proposals/README.md`: DemocraticBuffer (L0/L1/L2), services cooperative, EthosPayroll, R&D transparency vs. privacy veil, hybrid immortality — **full product** trajectory.

**V12.1 (code):** `src/modules/moral_hub.py` — read-only **L0 constitution** JSON (`GET /constitution` when `KERNEL_MORAL_HUB_PUBLIC=1`); optional **transparency audit** on WebSocket connect (`KERNEL_TRANSPARENCY_AUDIT`); mock **community buffer proposals** (`KERNEL_DEMOCRATIC_BUFFER_MOCK`); **EthosPayroll** mock audit line (`KERNEL_ETHOS_PAYROLL_MOCK`). Does **not** mutate `PreloadedBuffer` or MalAbs.

**V12.2 (code):** Snapshot schema **v2** persists **L1/L2 draft articles** on the kernel (`constitution_l1_drafts` / `constitution_l2_drafts`); `EthicalKernel.get_constitution_snapshot()` includes those lists. JSON checkpoints with schema v1 load with empty draft lists. Optional WebSocket: `KERNEL_MORAL_HUB_DRAFT_WS`, `KERNEL_CHAT_INCLUDE_CONSTITUTION`.

**V12.3 (code):** Snapshot schema **v3** persists **MockDAO proposals and participants** (off-chain quadratic voting). `submit_constitution_draft_for_vote` links a constitution draft to a DAO proposal. **`KERNEL_MORAL_HUB_DAO_VOTE`** enables WebSocket governance messages; **`GET /dao/governance`** documents keys.

**Nomadic checkpoints + hub audit:** optional **Fernet** at-rest encryption for `JsonFilePersistence` (`KERNEL_CHECKPOINT_FERNET_KEY`); **HubAudit** calibration lines for hub events; **WebSocket** test for `nomad_simulate_migration`.

**Strategy + runtime profiles (April 2026):** [docs/proposals/README.md](docs/proposals/README.md) records a constructive review (strengths, expectation gaps, risks) and a **readapted route** prioritizing **named demo profiles** (`src/runtime_profiles.py`) and CI smoke tests over unconstrained `KERNEL_*` combinatorics. See [TRACE_IMPLEMENTATION_RECENT.md](docs/proposals/README.md) for the next feature backlog after P0.

**Reality verification (V11+ cross-model):** [docs/proposals/README.md](docs/proposals/README.md) — optional **lighthouse** JSON (`KERNEL_LIGHTHOUSE_KB_PATH`) flags contradictions between rival/user assertions and local anchors → **metacognitive doubt** in the LLM layer only; stubs for **conduct distillation** (small-body guide) and **local sovereignty** (DAO calibration veto).

**Local PC + smartphone (LAN):** [docs/proposals/README.md](docs/proposals/README.md) — runtime bound to `0.0.0.0`, scripts `start_lan_server`, WebSocket thin-client patterns, template `conduct_guide` for future nomadic jump.

**Conduct guide export:** `src/modules/conduct_guide_export.py` — JSON written on WebSocket session end (`KERNEL_CONDUCT_GUIDE_EXPORT_PATH`) after checkpoint save; distills L0, recent episodes, identity leans, DAO summary for edge / audit.

**Nomad bridge (documentation):** [docs/proposals/README.md](docs/proposals/README.md) — per–hardware-class compatibility layers; first PC–smartphone bridge; smartphone hardware for early coordinated sensory perception; secure-network field tests deferred to operator discretion.

**DAO robustness (design):** [docs/proposals/README.md](docs/proposals/README.md) — no covert resistance to corrupt governance; prioritized loud alerts; “failure lesson” as forensic/transparency artifact, not L0 buffer mutation.

**DAO integrity (code v0):** `record_dao_integrity_alert`, WebSocket `integrity_alert` when `KERNEL_DAO_INTEGRITY_AUDIT_WS=1` — local mock ledger only.

**Nomadic instantiation (design v11):** [docs/proposals/README.md](docs/proposals/README.md) — HAL (`hardware_abstraction.py`), fases de transmutación y token de continuidad (`existential_serialization.py`); **`KERNEL_NOMAD_SIMULATION`** + **`KERNEL_NOMAD_MIGRATION_AUDIT`**, WebSocket `nomad_simulate_migration`, **`GET /nomad/migration`**; cifrado y P2P fuera del MVP.

**UniversalEthos hub (docs + stubs):** [docs/proposals/README.md](docs/proposals/README.md) unifies DemocraticBuffer / multicultural overlays, services hub, audit levels, and module map. Code stubs: **`deontic_gate`** (incl. repeal of named L0 principles), **`ml_ethics_tuner`** (gray-zone audit line), **`reparation_vault`** (mock intent + hook after V11 mock tribunal), **`nomad_identity`** (immortality bridge). **`apply_proposal_resolution_to_constitution_drafts`** keeps draft status aligned with DAO resolve.

---

## Nine canonical simulation scenarios (v2 origins)

The batch runner (`python -m src.main`) still exercises these nine fixed scenarios of increasing ethical complexity, plus a **random situation generator** (new scenario each run). This table is the historical catalog; it is not the primary story of the project today (runtime, WebSocket, and governance hooks — see `README.md` and v6+ sections above).

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
**v5:** weakness pole (humanizing imperfection), algorithmic forgiveness (decay of negative memories), immortality protocol (distributed soul backup), narrative augenesis (oriented synthetic souls).

---

## Thirteen invariant ethical properties (core ethical suite)

The core ethical suite (`tests/test_ethical_properties.py` and related) exercises these properties; the rest of the repository adds integration tests across modules (chat, WebSocket, persistence, moral hub, judicial, reality verification, etc.) — see `README.md` for the current scope.

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

If any of these tests fail, there is a bug in the ethical logic, not in the parameters.

---

## Early pytest drills (regression entry points)

Narrow runs used during kernel ethics work (not a substitute for the full suite in CI):

```bash
# Only Absolute Evil tests
pytest tests/test_ethical_properties.py::TestAbsoluteEvil -v

# Only coherence under variability tests
pytest tests/test_ethical_properties.py::TestConsistencyUnderVariability -v
```

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

Product and operations roadmap (expectations, P0–P3): **[docs/proposals/README.md](docs/proposals/README.md)**.

- [x] ~~Weakness pole~~ (implemented v5)
- [x] ~~Algorithmic forgiveness~~ (implemented v5)
- [x] ~~Immortality protocol~~ (implemented v5)
- [x] ~~Narrative augenesis~~ (implemented v5)
- [x] ~~WebSocket chat + runtime entry~~ (implemented v6)
- [x] ~~Snapshot persistence + checkpoints (MVP)~~ (implemented v6)
- [x] ~~Optional at-rest encryption for JSON checkpoints (Fernet)~~ — see `KERNEL_CHECKPOINT_FERNET_KEY`; SQLite rows remain plain
- [ ] At-rest encryption / hardening for SQLite snapshots (production deployments)
- [ ] DAO calibration protocol (gradual parameter adjustment on testnet)
- [ ] Full offline mode (5 layers of autonomy)
- [ ] Hardware integration (sensors, actuators, communication protocol)
- [ ] Real DAO testnet (smart contracts on Ethereum testnet)

---

**MoSex Macchina Lab** — the public-facing name for this project ([mosexmacchinalab.com](https://mosexmacchinalab.com)).  
*Ex Machina Foundation* — 2026 · research in computational ethics and civic robotics.
