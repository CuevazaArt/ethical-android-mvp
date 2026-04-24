# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-24

## Fase α — COMPLETE ✅
## Fase β — COMPLETE ✅

## Active block

**V2.9 — Audio VAD**: Voz activa como input en el Nomad PWA.

## Closed blocks

| Block | Name | Status |
|-------|------|--------|
| V2.1 | Chat Terminal | ✅ |
| V2.2 | Ethical Perception | ✅ |
| V2.3 | Functional Memory | ✅ |
| V2.4 | Safety Gate | ✅ |
| V2.5 | WebSocket Chat | ✅ |
| V2.6 | Streaming | ✅ |
| V2.7 | Dashboard | ✅ |

## Open blocks (Fase γ — Nomad/Audio)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.8 | Nomad PWA | ✅ CLOSED | Fase β complete |
| V2.9 | Audio VAD | 🔨 IN PROGRESS | V2.8 closed |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,status}.py` |
| Server | `src/server/app.py`, `src/server/static/index.html` |
| Tests | `tests/core/{test_ethics,test_memory,test_chat,test_safety}.py` (53 tests) |
| Run | `uvicorn src.server.app:app --port 8000` |
| Dashboard | `http://localhost:8000/dashboard` |

## Recent changes

- **2026-04-24 Fase α:** V2.1-V2.4 closed. 5 core modules, 53 tests, safety gate.
- **2026-04-24 V2.5:** WebSocket chat on localhost:8000 — FastAPI + HTML client.
- **2026-04-24 V2.6:** Streaming — turn_stream() yields tokens progressively.
- **2026-04-24 V2.8 CLOSED:** Nomad PWA servida en `/nomad` + `/nomad/{file}`. `/ws/nomad` acepta telemetría (ping→pong, batería, kinética) y relay de chat. `app.js` actualizado con handler V2 `{type:token}` + `{type:done}` + TTS. Demo: GET /nomad→200 (4145B), /nomad/app.js→200 (41542B). Servidor activo en 0.0.0.0:8000 (LAN). Tests: 53 passed.
