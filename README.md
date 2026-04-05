# Ethical Android — MVP v5

**Functional prototype of the artificial ethical consciousness model with humanizing imperfection, forgiveness, and identity persistence.**

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

```bash
# All tests (51 tests, 13 invariant ethical properties)
pytest tests/ -v

# Only Absolute Evil tests
pytest tests/test_ethical_properties.py::TestAbsoluteEvil -v

# Only coherence under variability tests
pytest tests/test_ethical_properties.py::TestCoherenceUnderVariability -v

# With summarized output
pytest tests/ --tb=short
```

The tests verify that the kernel **always** meets the ethical properties
regardless of Bayesian variability, sympathetic state, or context.
If any test fails, there is a bug in the ethical logic, not in the parameters.

### Natural language mode (v4)

```python
from src.kernel import KernelEtico

kernel = KernelEtico()

# The LLM perceives, the kernel decides, the LLM communicates
decision, response, narrative = kernel.procesar_natural(
    "An elderly man collapsed in the supermarket while I was buying apples"
)

print(kernel.formatear_natural(decision, response, narrative))
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
│   └── augenesis.py        # Narrative augenesis (soul creation) [v5]
├── simulations/
│   └── runner.py           # 9 scenarios + simulation runner
├── kernel.py               # Ethical kernel: orchestrates the 17 modules
└── main.py                 # Entry point
```

### Kernel operating cycle

```
[Perception/LLM] → [Uchi-Soto] → [Absolute Evil] → [Buffer] →
[Sympathetic] → [Locus] → [Bayesian] → [Poles] → [Will] →
[Decision] → [Weakness] → [Forgiveness] → [Memory] → [DAO] → [LLM]

Psi Sleep Ψ (end of day): Audit + Forgiveness + Immortality Backup
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
- [x] Immortality Protocol (distributed backup in 4 layers)
- [x] Narrative Augenesis (creation of oriented synthetic souls)

## Tests

51 tests that verify 13 invariant ethical properties:

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

**What are you seeing?** The dashboard shows in real time how 17 artificial
ethical intelligence modules evaluate each situation: from social context
classification (Uchi-Soto), through blocking of unacceptable actions
(Absolute Evil), to Bayesian impact evaluation, the "weakness pole" that
humanizes the android with narrative imperfections, and "algorithmic
forgiveness" that allows negative memories to lose weight over time.
All without a server, without internet, without installing anything.

No server, internet connection (after first load), or technical knowledge required.

## Landing site (Next.js)

The folder `landing/` is a **Next.js** marketing page (Tailwind, Framer Motion, Three.js hero) for **mosexmacchinalab.com**. It embeds the same `dashboard.html` at `/demo` (also served as `/dashboard.html` from `landing/public/`).

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
├── .github/              # Issue templates & Security tab links (config.yml)
├── docs/                 # Theory ↔ implementation (see THEORY_AND_IMPLEMENTATION.md)
├── landing/              # Next.js site (npm install inside this folder)
├── src/                  # Ethical kernel source code
├── tests/                # Formal test suite
├── dashboard.html        # Interactive dashboard (open in browser)
├── BIBLIOGRAPHY.md       # 104 academic references across 14 disciplines
├── CHANGELOG.md          # Version change history
├── CONTRIBUTING.md       # Contributor guide
├── HISTORY.md            # Full project evolution (v1→v5)
├── LICENSE               # Apache 2.0
├── SECURITY.md           # Vulnerability reporting policy
├── README.md             # This file
└── requirements.txt      # Python dependencies
```

A copy of `dashboard.html` is also kept under `landing/public/` so the Next.js app can serve it.

**Theory vs. code:** formulas, predicates, and file-level mapping (including how this differs from an LLM-only “stochastic parrot”) are in [docs/THEORY_AND_IMPLEMENTATION.md](docs/THEORY_AND_IMPLEMENTATION.md).

## Medium-term directions (not scheduled)

These are **directional** ideas for when the project moves beyond pure research demos — see also the public [roadmap](https://mosexmacchinalab.com/roadmap) on the landing site.

- **Hexagonal-style boundaries (ports & adapters), introduced incrementally:** define stable interfaces for infrastructure that is likely to change (e.g. LLM provider, DAO/governance backend, persistence for narrative episodes) so the ethical pipeline can swap implementations without a full rewrite. Prefer **small, evidence-driven** extractions (a second real adapter) over a one-shot “hexagonal everything” refactor.
- **Discussion forum (planned):** a dedicated space to debate **pending implementation areas** and roadmap choices may be added later. Until then, use GitHub Issues (templates in `.github/`) and, if enabled by maintainers, **GitHub Discussions** on this repository.

## License

Apache 2.0 — see [LICENSE](LICENSE).

## Ex Machina Foundation — 2026

Research project in computational ethics and civic robotics.
