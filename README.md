# Ethos Kernel

[![CI](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CuevazaArt/ethical-android-mvp/graph/badge.svg)](https://codecov.io/gh/CuevazaArt/ethical-android-mvp)

**MoSex Macchina Lab** — open **kernel + runtime** for a model of artificial ethical agency: traceable governance hooks (DAO / hub audit), persistence, WebSocket chat, and a large **pytest** suite (CI on Python **3.11 / 3.12**).

**Documentation:** design notes and proposal index: [`docs/proposals/README.md`](docs/proposals/README.md) (e.g. [`PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md`](docs/proposals/PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK.md)). Architecture decisions live in [`docs/adr/`](docs/adr/README.md). Narrative history: [`HISTORY.md`](HISTORY.md) · changes: [`CHANGELOG.md`](CHANGELOG.md). Layout: [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md). The full proposal tree is versioned under **`docs/proposals/`**. **Academic bibliography** (104+ refs) and the **Next.js landing** app live on branch **`main-whit-landing`** — this **`main`** line stays kernel-first and landing-free.

**Kernel / runtime line:** ethical core **v5** through **v12** hub / persistence / advisory features — see `HISTORY.md` for the version story.

This project is also listed in [Spanish](https://github.com/CuevazaArt/androide-etico-mvp).

## What it does

- **WebSocket chat:** `python -m src.chat_server` or `python -m src.runtime` — JSON over `/ws/chat`; optional `KERNEL_*` layers (see `src/chat_server.py` docstring and `src/chat_settings.py`).
- **Batch simulations:** `python -m src.main` — legacy harness for regression scenarios.
- **Experiments (optional):** [`experiments/README.md`](experiments/README.md).
- **Ethical scoring:** Candidate actions are ranked using a **weighted mixture** over three stylized viewpoints (utilitarian / deontological / virtue). The names `BayesianEngine` and `KERNEL_BAYESIAN_*` refer to that mixture layer and optional bounded adjustments — **not** unconstrained “full Bayes” over a latent world model. See [ADR 0009](docs/adr/0009-ethical-mixture-scorer-naming.md) and [THEORY_AND_IMPLEMENTATION.md](docs/proposals/THEORY_AND_IMPLEMENTATION.md).

## Quick start

### Prerequisites

- Python 3.9+
- pip

### Install

```bash
git clone https://github.com/CuevazaArt/ethical-android-mvp.git
cd ethical-android-mvp
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Unix: source .venv/bin/activate
pip install -r requirements.txt
# pip install -e ".[runtime]"   # FastAPI / uvicorn / httpx for chat server
# pip install -e ".[theater]"   # Marker for narrative/DAO/PAD layers (no extra deps)
```

### Run simulations

```bash
python -m src.main
python -m src.main --sim 3
```

### Run tests (same as CI)

```bash
pip install -r requirements.txt -r requirements-dev.txt
pytest tests/ -v
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
```

### Environment validation (`KERNEL_*` combinations)

After optional `ETHOS_RUNTIME_PROFILE` merge, the chat server applies **`KERNEL_ENV_VALIDATION`**: **`strict`** (default), **`warn`**, or **`off`**. In **strict** mode, incompatible flag combinations fail fast at startup (see [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md)). From an editable install, run **`ethos config --strict`** to exit non-zero on the same rules without starting the server ([`CONTRIBUTING.md`](CONTRIBUTING.md)).

### Real-time chat (WebSocket)

```bash
python -m src.chat_server
# http://127.0.0.1:8765/health  —  ws://127.0.0.1:8765/ws/chat
```

Optional: `ETHOS_RUNTIME_PROFILE=lan_operational` (see [`src/runtime_profiles.py`](src/runtime_profiles.py)). Docker: [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml), [`docs/deploy/COMPOSE_PRODISH.md`](docs/deploy/COMPOSE_PRODISH.md) (includes **staging verification** for `/health` and `/metrics`).

### Essential KERNEL_* flags (quick reference)

| Flag | Purpose | Example Value |
|------|---------|----------------|
| `KERNEL_ENV_VALIDATION` | Enforce strict config checks | `strict` \| `warn` |
| `KERNEL_SEMANTIC_CHAT_GATE` | Enable semantic (embedding) layer for MalAbs | `1` (default off) |
| `KERNEL_PERCEPTION_COERCION_REPORTING` | Include coercion analysis in chat output | `1` |
| `KERNEL_PERCEPTION_UNCERTAINTY_DELIB` | Force deliberate mode on high uncertainty | `1` |
| `KERNEL_METRICS` | Enable Prometheus metrics scraping | `1` (default off) |
| `KERNEL_LOG_JSON` | Structured JSON logging | `1` |
| `KERNEL_LOG_LEVEL` | Logging verbosity | `INFO` \| `DEBUG` |
| `KERNEL_CHAT_TURN_TIMEOUT` | Timeout per turn (seconds) | `30` |
| `KERNEL_MORAL_HUB_ENABLE` | Enable governance hub + DAO | `1` |
| `KERNEL_CHECKPOINT_ENABLED` | Snapshot state to disk | `1` |
| `ETHOS_RUNTIME_PROFILE` | Load bundled config (lab/demo/production) | `lab` |

**Full reference:** [`docs/proposals/KERNEL_ENV_POLICY.md`](docs/proposals/KERNEL_ENV_POLICY.md) · **operator CLI:** `python -m src.ethos_cli config` (after `pip install -e .`).

## Modular architecture (overview)

```
src/
├── modules/          # Ethical pipeline, LLM, sensors, hub, persistence helpers
├── simulations/      # Batch scenario runner
├── persistence/      # Snapshots (JSON / SQLite)
├── kernel.py         # EthicalKernel orchestration + process_chat_turn
├── chat_server.py    # FastAPI WebSocket
├── runtime_profiles.py
└── main.py
```

Psi Sleep, moral hub, judicial escalation, and other subsystems are documented in code and in [`docs/adr/`](docs/adr/README.md).

## Repository structure

```
.
├── .github/           # CI, issue templates
├── docs/
│   ├── proposals/     # PROPOSAL_*.md + README index
│   └── adr/           # Architecture decision records
├── experiments/       # Optional research harnesses
├── src/
├── tests/
├── CHANGELOG.md
├── CONTRIBUTING.md
├── HISTORY.md
├── LICENSE
├── SECURITY.md
├── README.md
└── requirements.txt
```

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md). Security: [`SECURITY.md`](SECURITY.md).

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

## MoSex Macchina Lab · Ex Machina Foundation — 2026

**MoSex Macchina Lab** — public project name ([mosexmacchinalab.com](https://mosexmacchinalab.com)). **Ethos Kernel** — technical name of this repository (GitHub slug may remain `ethical-android-mvp`). **Ex Machina Foundation** — research in computational ethics and civic robotics.
