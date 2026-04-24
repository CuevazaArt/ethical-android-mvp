# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos 2.0 (Rebuild from core)
- **Architecture:** Concentric layers — core → server → clients → extensions
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-24

## Fase α ✅ · Fase β ✅ · Fase γ ✅

## Active block

**V2.11 — Whisper STT server-side**: Migrar STT local a backend usando Whisper para mejor robustez.

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
| V2.8 | Nomad PWA | ✅ |
| **Fase γ COMPLETA** — Nomad PWA + VAD activo. Siguiente: Fase δ (streaming HTTPS / sync identidad).

## Open blocks (Fase δ — Audio/Vision pipeline)

| Block | Name | Status | Depends on |
|-------|------|--------|------------|
| V2.10 | STT→Chat pipeline | ✅ CLOSED | V2.9 closed |
| V2.11 | Whisper STT server-side | 🔨 IN PROGRESS | V2.10 closed |
| V2.12 | Vision frame processing | ⏳ Waiting | V2.11 closed |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,status}.py` |
| Server | `src/server/app.py` |
| Nomad PWA | `src/clients/nomad_pwa/{index.html,app.js,media_engine.js,style.css,sw.js}` |
| Tests | `tests/core/` (53 tests) |
| Run | `uvicorn src.server.app:app --port 8000` |
| Chat | `http://localhost:8000/` |
| Dashboard | `http://localhost:8000/dashboard` |
| Nomad | `http://[LAN-IP]:8000/nomad` |

## Recent changes

- **2026-04-24 Fase α:** V2.1-V2.4. 5 core modules, 53 tests.
- **2026-04-24 Fase β:** V2.5-V2.7. WebSocket chat, streaming, dashboard.
- **2026-04-24 V2.9 CLOSED (Fase γ COMPLETA):** Audio VAD en Nomad PWA. `media_engine.js`: SpeechRecognition con `interimResults`, VAD gate (RMS+onset+hangover), plain-text send a `turn_stream()` (protocolo V2). `style.css`: `.mic-active` ring pulsante + `.streaming-bubble` cursor parpadeante. Tests: 53 passed.
- **2026-04-24 V2.10 CLOSED:** STT to Chat pipeline. Full-duplex voice loop con preemption (`speechSynthesis.cancel()` en interim) y feedback visual explícito de cruce de red. Tests: 53 passed.
