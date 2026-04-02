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

## v5.0 — March 2026 | Humanization and persistent identity (current version)

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
- [ ] DAO calibration protocol (gradual parameter adjustment on testnet)
- [ ] Full offline mode (5 layers of autonomy)
- [ ] Hardware integration (sensors, actuators, communication protocol)
- [ ] Real DAO testnet (smart contracts on Ethereum testnet)

---

Ex Machina Foundation — 2026
