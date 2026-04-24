# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-23

## Active block

**V2.3 — Functional Memory**: Memory persistence + cross-session recall in chat.

## Open blocks (Fase α — Core Vivo)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.1 | Chat Terminal | ✅ CLOSED | Ollama running |
| V2.2 | Ethical Perception | ✅ CLOSED | V2.1 closed |
| V2.3 | Functional Memory | 🔨 IN PROGRESS | V2.2 closed |
| V2.4 | Safety Gate | ⏳ Waiting | V2.3 closed |

## Key files for current work

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat}.py` |
| Tests | `tests/core/` |
| Blueprint | See Ethos 2.0 Blueprint artifact |
| V1 reference | `git checkout v15-archive-full-vision -- <path>` |

## Recent changes

- **2026-04-23:** Ethos 2.0 initiated. Core files created. V1 archived at `v15-archive-full-vision`.
- **2026-04-24 V2.1 CLOSED:** `python -m src.core.chat` REPL verified — 5-turn conversation log captured. Bugs fixed: (1) `suggested_context` enum echo en `Signals.from_dict` → sanitized to allowlist en `ethics.py`. (2) STM history injected into system prompt en `chat.py`. Tests: 16 passed.
- **2026-04-24 V2.2 CLOSED:** 9 chat integration tests (test_chat.py) + 3 memory integration tests (test_memory.py). Fix critical bug: empty Memory objects were falsy due to `__len__=0`, causing `memory or Memory()` to silently discard passed-in memory. Tests: 31 passed.
