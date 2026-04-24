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

**V2.16 — Dashboard Identity Telemetry**: Exponer el perfil de identidad en `/api/status` y visualizarlo en el dashboard.

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
| V2.11 | Whisper STT server-side | ✅ CLOSED | V2.10 closed |
| V2.12 | Vision frame processing | ✅ CLOSED | V2.11 closed |
| V2.13 | Vision → Kernel context | ✅ CLOSED | V2.12 closed |
| V2.14 | Nomad PWA HTTPS | ✅ CLOSED | V2.13 closed |
| V2.15 | Identity Neuroplasticity | ✅ CLOSED | V2.14 closed |
| V2.16 | Dashboard Identity Telemetry | 🔨 IN PROGRESS | V2.15 closed |

## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,status}.py` |
| Server | `src/server/app.py` |
| Nomad PWA | `src/clients/nomad_pwa/{index.html,app.js,media_engine.js,style.css,sw.js}` |
| Tests | `tests/core/` (77 tests) |
| Run | `uvicorn src.server.app:app --port 8000` |
| Chat | `http://localhost:8000/` |
| Dashboard | `http://localhost:8000/dashboard` |
| Nomad | `http://[LAN-IP]:8000/nomad` |

## Recent changes

- **2026-04-24 Fase α:** V2.1-V2.4. 5 core modules, 53 tests.
- **2026-04-24 Fase β:** V2.5-V2.7. WebSocket chat, streaming, dashboard.
- **2026-04-24 V2.9 CLOSED (Fase γ COMPLETA):** Audio VAD en Nomad PWA. `media_engine.js`: SpeechRecognition con `interimResults`, VAD gate (RMS+onset+hangover), plain-text send a `turn_stream()` (protocolo V2). `style.css`: `.mic-active` ring pulsante + `.streaming-bubble` cursor parpadeante. Tests: 53 passed.
- **2026-04-24 V2.10 CLOSED:** STT to Chat pipeline. Full-duplex voice loop con preemption (`speechSynthesis.cancel()` en interim) y feedback visual explícito de cruce de red. Tests: 53 passed.
- **2026-04-24 V2.11 CLOSED:** `src/core/stt.py` — WhisperSTT con faster-whisper opcional, fallback graceful, Anti-NaN, latencia log. `app.py`: handler `audio_pcm` en /ws/nomad + `stt_available` en /api/status. Tests: 57 passed.
- **2026-04-24 PODA MAYOR:** Eliminados 232 tests V1 + 10 directorios src/ V1 (modules, nervous_system, persistence, runtime, sandbox, observability, settings, validators, simulations, utils) + 10 archivos src/server/ V1. Ninguno era importado por app.py. Órgano V2 puro.
- **2026-04-24 V2.12 CLOSED:** `src/core/vision.py` — VisionEngine procesa JPEG base64, extrae brillo/movimiento/rostros con latencia perf_counter y Anti-NaN. Handler `vision_frame` en /ws/nomad → envía `vision_signals` al cliente. 11 tests en test_vision.py. 68 passed.
- **2026-04-24 V2.13 CLOSED:** `chat.py` refactorizado con `_build_system()` — Single Source of Truth para system prompt. `turn_stream(vision_context=dict|None)` inyecta entorno físico (luz, movimiento, rostros) al prompt. `app.py`: `_last_vision` cacheado por conexión, pasado en los 3 handlers (chat_text, user_speech, audio_pcm). 68 passed.
- **2026-04-24 V2.14 CLOSED:** `scripts/gen_cert.py` — cert RSA-2048 auto-firmado con SAN (Python-puro, `cryptography`), idempotente. `README_HTTPS.md` con 5 pasos (Android/iOS). Demo: SHA256 verificado, SSL context OK, 68 passed.
- **2026-04-24 V2.15 CLOSED:** `src/core/identity.py` — clase `Identity` con `update(memory)` + `narrative()`. Perfil persiste en `~/.ethos/identity.json`. Detecta tendencia ética (mejorando/estable/deteriorando), contextos y acciones dominantes, ratio de safety blocks. Anti-NaN en todos los cálculos. Integrado en `_build_system()` de `chat.py`. 77 passed (9 tests nuevos).
