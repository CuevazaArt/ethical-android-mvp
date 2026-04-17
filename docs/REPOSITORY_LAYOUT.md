# Repository layout and language split

GitHub **language statistics** reflect **file counts and sizes across the whole repo**, not the runtime dependency graph of the kernel.

## What is core (mandatory for kernel work)

| Area | Role |
|------|------|
| **`src/`** | Ethos Kernel and runtime: **Python only**. This is the supported core for ethics logic, WebSocket server, persistence, CLI, and CI. |
| **`tests/`** | Python test suite; **required** for any change that affects behavior. |
| **`requirements.txt`** / **`requirements-dev.txt`** | Primary install path for the kernel and CI. |
| **`pyproject.toml`** | Packaging metadata; `pip install -e .` for editable install. |

Contributors who only ship kernel features **do not** need Node.js, npm, or TypeScript.

## What is adjacent (optional)

| Area | Role |
|------|------|
| **`contracts/`** | **Optional transparency only:** README + non-functional Solidity **stub** — kernel governance demos are **Python** (`mock_dao.py`). No `forge`/Hardhat in default CI. See [`contracts/README.md`](../contracts/README.md). |
| **`experiments/`** | Optional research harnesses (not required for kernel or CI). See [`experiments/README.md`](../experiments/README.md). |

## End-to-end (browser) testing

Full **browser E2E** (e.g. Playwright against a live `chat_server`) is **not** part of the default CI matrix today. Adding true E2E is a follow-up (separate job, optional secrets, longer runtime).

This repository snapshot does **not** include a separate **`landing/`** Next.js app; static operator surfaces under [`src/static/`](../src/static/) (e.g. phone relay) are served by the Python ASGI app when enabled. If your team keeps a **standalone** frontend elsewhere, run its Playwright suite against a **staging** `chat_server` URL; track that harness in the frontend repo, not in kernel `pytest`.

**Manual smoke checklist (kernel + HTTP, no browser required):**

1. Install dev deps and run the suite (or `python scripts/eval/run_cursor_integration_gate.py` for the cross-team subset).
2. Start the server: `python -m src.chat_server` (default `http://127.0.0.1:8765`).
3. **`GET /health`** — expect JSON including `version` and observability flags.
4. **WebSocket** — connect to `ws://127.0.0.1:8765/ws/chat`, send a minimal JSON chat payload; expect a structured turn response (contract patterns in [`tests/test_chat_server.py`](../tests/test_chat_server.py)).

The CI job **windows-smoke** runs [`tests/test_runtime_profiles.py`](../tests/test_runtime_profiles.py) and [`tests/test_env_policy.py`](../tests/test_env_policy.py) on Windows to catch profile + **`KERNEL_ENV_VALIDATION`** strict regressions outside Linux-only paths.
