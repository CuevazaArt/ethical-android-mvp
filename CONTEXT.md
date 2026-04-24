# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-23

## Active block

**V2.1 — Chat Terminal**: `python -m src.core.chat` opens an interactive REPL that talks to Ollama.

## Open blocks (Fase α — Core Vivo)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.1 | Chat Terminal | 🔨 IN PROGRESS | Ollama running |
| V2.2 | Ethical Perception | ⏳ Waiting | V2.1 closed |
| V2.3 | Functional Memory | ⏳ Waiting | V2.2 closed |
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
