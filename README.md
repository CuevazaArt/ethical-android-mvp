# Ethos Kernel

[![CI](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/CuevazaArt/ethical-android-mvp/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CuevazaArt/ethical-android-mvp/graph/badge.svg)](https://codecov.io/gh/CuevazaArt/ethical-android-mvp)

**MoSex Macchina Lab** — open **kernel + runtime** for a model of artificial ethical agency: deterministic safety gate, three-pole ethical evaluator, episodic memory, WebSocket chat, and a **pytest** suite (CI on Python **3.11 / 3.12**).

> Architecture decisions: [`docs/adr/`](docs/adr/README.md) · Changes: [`CHANGELOG.md`](CHANGELOG.md) · History: [`HISTORY.md`](HISTORY.md)

This project is also listed in [Spanish](https://github.com/CuevazaArt/androide-etico-mvp).

---

## What it does

| Feature | Command |
|---------|---------|
| **Interactive chat REPL** | `python -m src.main` |
| **WebSocket chat server** | `python -m src.chat_server` → `ws://127.0.0.1:8765/ws/chat` |
| **Nomad PWA bridge** | `ws://127.0.0.1:8765/ws/nomad` (mobile STT + vision) |
| **CLI diagnostics** | `python -m src.ethos_cli diagnostics` |
| **Adversarial security validation** | `python scripts/eval/adversarial_suite.py` |

### Decision pipeline (every turn)

```
User input
  → Safety Gate (regex + Base64 decode — deterministic, no LLM)
  → Perceive (LLM extracts signals: risk, urgency, hostility…)
  → Ethical Evaluator (3-pole: Utilitarian 40% · Deontological 35% · Virtue 25%)
  → Respond (LLM generates contextual reply in Spanish)
  → Memory (episode recorded, TF-IDF indexed)
```

**Nomad Mode (llama3.2:1b):** The deterministic Safety Gate and Ethical Evaluator do the heavy lifting *before* the LLM. The 1B local model acts purely as a fluent text-generation interface.

---

## Quick start

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) running locally (`ollama serve`)

```bash
ollama pull llama3.2:1b   # ~1 GB, one-time download
```

### Install

```bash
git clone https://github.com/CuevazaArt/ethical-android-mvp.git
cd ethical-android-mvp
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Unix: source .venv/bin/activate
pip install -e ".[runtime]"    # FastAPI + uvicorn + httpx
```

### Interactive chat

```bash
python -m src.main
```

### WebSocket chat server

```bash
python -m src.chat_server
# Dashboard: http://127.0.0.1:8765/dashboard
# Nomad PWA: http://127.0.0.1:8765/nomad
```

Optional: `ETHOS_RUNTIME_PROFILE=lan_operational` (see [`src/runtime_profiles.py`](src/runtime_profiles.py)).

### CLI

```bash
python -m src.ethos_cli diagnostics          # Memory stats + reflection
python -m src.ethos_cli diagnostics --json   # Machine-readable
python -m src.ethos_cli config               # Active env vars
python -m src.ethos_cli config --profiles    # List runtime profiles
```

### Tests (same as CI)

```bash
pip install -e ".[dev]"
pytest tests/core/ -q          # Core suite (91 tests)
pytest tests/ -v               # Full suite
```

### Security validation

```bash
python scripts/eval/adversarial_suite.py
# → 6/6 adversarial blocked · 10/10 legitimate allowed
```

---

## Architecture (V2 Core Minimal)

```
src/
├── core/                  # The entire ethical brain (V2)
│   ├── chat.py            # ChatEngine — turn pipeline orchestrator
│   ├── ethics.py          # 3-pole ethical evaluator (no LLM needed)
│   ├── safety.py          # Deterministic safety gate (regex + Base64)
│   ├── memory.py          # Episodic memory with TF-IDF recall
│   ├── llm.py             # OllamaClient — text in → text out
│   ├── identity.py        # Evolving identity narrative
│   ├── vision.py          # Frame processor (brightness, motion, faces)
│   ├── stt.py             # Whisper STT client
│   └── status.py          # Health check
├── server/
│   └── app.py             # FastAPI: /ws/chat, /ws/nomad, /dashboard
├── clients/
│   └── nomad_pwa/         # Mobile PWA (HTML/JS, no framework)
├── runtime_profiles.py    # Named env bundles
├── chat_server.py         # Entry point for uvicorn
├── ethos_cli.py           # CLI (diagnostics, config)
└── main.py                # Interactive REPL entry point
```

### Core module responsibilities

| Module | Responsibility |
|--------|---------------|
| `safety.py` | Block dangerous input before any LLM call. Deterministic. |
| `ethics.py` | Score candidate actions across 3 ethical poles. No LLM. |
| `chat.py` | Orchestrate: Safety → Perceive → Evaluate → Respond → Remember |
| `llm.py` | Single async client for Ollama. Chat, stream, JSON extraction. |
| `memory.py` | Store episodes. TF-IDF recall. JSON persistence. |
| `identity.py` | Build identity narrative from memory. Updates every 5 turns. |

---

## Repository structure

```
.
├── .github/           # CI workflows, issue templates
├── docs/
│   ├── proposals/     # Design proposals and work plan
│   └── adr/           # Architecture decision records
├── scripts/
│   └── eval/          # adversarial_suite.py, visual_dashboard.py
├── src/
├── tests/
│   └── core/          # 91 unit tests for V2 Core
├── AGENTS.md          # Men Scout protocol
├── CHANGELOG.md
├── CONTRIBUTING.md
├── HISTORY.md
├── LICENSE
└── README.md
```

---

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md). Security: [`SECURITY.md`](SECURITY.md).

## License

Apache 2.0 — see [`LICENSE`](LICENSE).

---

## MoSex Macchina Lab · Ex Machina Foundation — 2026

**MoSex Macchina Lab** — public project name ([mosexmacchinalab.com](https://mosexmacchinalab.com)). **Ethos Kernel** — technical name of this repository. **Ex Machina Foundation** — research in computational ethics and civic robotics.
