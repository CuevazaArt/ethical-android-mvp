# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-24

## Fase α — COMPLETE ✅

All core modules functional and tested.

## Active block

**V2.5 — WebSocket Chat**: FastAPI + WebSocket server on localhost:8000.

## Closed blocks (Fase α — Core Vivo)

| Block | Name | Status | Tests |
|-------|------|--------|-------|
| V2.1 | Chat Terminal | ✅ CLOSED | 19 |
| V2.2 | Ethical Perception | ✅ CLOSED | 31 |
| V2.3 | Functional Memory | ✅ CLOSED | 34 |
| V2.4 | Safety Gate | ✅ CLOSED | 53 |

## Open blocks (Fase β — Server)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.5 | WebSocket Chat | ⏳ Waiting | Fase α complete |
| V2.6 | Streaming | ⏳ Waiting | V2.5 closed |
| V2.7 | Dashboard Minimal | ⏳ Waiting | V2.6 closed |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety}.py` |
| Tests | `tests/core/{test_ethics,test_memory,test_chat,test_safety}.py` |
| Status | `python -m src.core.status` |

## Recent changes

- **2026-04-23:** Ethos 2.0 initiated. Core files created. V1 archived at `v15-archive-full-vision`.
- **2026-04-24 V2.1 CLOSED:** Chat terminal REPL verified. Bugs fixed: context enum sanitization, STM history injection.
- **2026-04-24 V2.2 CLOSED:** 9 chat integration tests + fix empty-Memory falsy bug.
- **2026-04-24 V2.3 CLOSED:** Cross-session persistence, recall injection, reflection verified.
- **2026-04-24 V2.4 CLOSED:** Safety gate — 7 danger categories, Unicode sanitization, evasion resistance. 19 safety tests. Fase α COMPLETE.
