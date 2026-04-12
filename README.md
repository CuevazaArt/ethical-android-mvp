# Ethos Kernel

[![CI](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CuevazaArt/ethical-android-mvp/graph/badge.svg)](https://codecov.io/gh/CuevazaArt/ethical-android-mvp)

**MoSex Macchina Lab** — open **kernel + runtime** for a model of artificial ethical agency: traceable governance hooks (DAO / hub audit), persistence, WebSocket chat, and a large **pytest** suite (CI on Python **3.11 / 3.12**).

**Documentation:** add design notes under [`docs/proposals/README.md`](docs/proposals/README.md). Architecture decisions live in [`docs/adr/`](docs/adr/README.md). Narrative history: [`HISTORY.md`](HISTORY.md) · changes: [`CHANGELOG.md`](CHANGELOG.md). Layout: [`docs/REPOSITORY_LAYOUT.md`](docs/REPOSITORY_LAYOUT.md). Older long-form proposal text may be recovered from **git history** or backup branches (e.g. `backup/main-2026-04-10`).

**Kernel / runtime line:** ethical core **v5** through **v12** hub / persistence / advisory features — see `HISTORY.md` for the version story.

This project is also listed in [Spanish](https://github.com/CuevazaArt/androide-etico-mvp).

## What it does

- **WebSocket chat:** `python -m src.chat_server` or `python -m src.runtime` — JSON over `/ws/chat`; optional `KERNEL_*` layers (see `src/chat_server.py` docstring and `src/chat_settings.py`).
- **Batch simulations:** `python -m src.main` — legacy harness for regression scenarios.
- **Static dashboard:** open [`dashboard.html`](dashboard.html) in a browser (no server).
- **Experiments (optional):** [`experiments/README.md`](experiments/README.md).

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

### Real-time chat (WebSocket)

```bash
python -m src.chat_server
# http://127.0.0.1:8765/health  —  ws://127.0.0.1:8765/ws/chat
```

Optional: `ETHOS_RUNTIME_PROFILE=lan_operational` (see [`src/runtime_profiles.py`](src/runtime_profiles.py)). Docker: [`Dockerfile`](Dockerfile), [`docker-compose.yml`](docker-compose.yml), [`docs/deploy/COMPOSE_PRODISH.md`](docs/deploy/COMPOSE_PRODISH.md).

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
│   ├── proposals/     # Design proposals (skeleton — add PROPOSAL_*.md here)
│   ├── adr/           # Architecture decision records
│   └── templates/     # JSON templates
├── experiments/       # Optional research harnesses
├── src/
├── tests/
├── dashboard.html
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
