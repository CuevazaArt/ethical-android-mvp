# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-23

## Active block

**V2.4 — Safety Gate**: `src/core/safety.py` bloquea input adversarial antes de que llegue al LLM.

## Open blocks (Fase α — Core Vivo)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.1 | Chat Terminal | ✅ CLOSED | Ollama running |
| V2.2 | Ethical Perception | ✅ CLOSED | V2.1 closed |
| V2.3 | Functional Memory | ✅ CLOSED | V2.2 closed |
| V2.4 | Safety Gate | 🔨 IN PROGRESS | V2.3 closed |

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
- **2026-04-24 V2.2 CLOSED:** 3 tests de integración añadidos en `test_ethics.py`: sanitización de contexto, pipeline completo emergencia médica, pipeline completo interacción hostil. Tests: 19 passed.
- **2026-04-24 V2.3 CLOSED:** 3 tests de integración de memoria añadidos en `test_memory.py`: acumulación por turno, recall por contexto, scores finitos. + 3 tests V2.3 en `test_chat.py`: cross-session persistence, recall injection into LLM prompt, reflection. Fix empty-Memory falsy bug. Tests: 34 passed.
