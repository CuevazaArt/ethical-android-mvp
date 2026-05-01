# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos V2 Core Minimal (Fase 17 COMPLETA)
- **Architecture:** `src/core/` → `src/server/` (zero legacy)
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-28 (Fase 25 — Voice Pipeline Hardened / Sherpa-ONNX)
- **Visión canónica:** `docs/VISION_NOMAD.md`

## Fase α ✅ · Fase β ✅ · Fase γ ✅ · Fase δ ✅ · Fase 16 ✅ · Fase 17 ✅ · Fase 18 ✅

## Estado Actual (Abril 2026)

- **Fase:** 23 (Nomad Native Android SDK Transition) - COMPLETA ✅
- **Logro:** Setup de Core Android (Gradle/Compose) y Servicios en primer plano funcionales.
- **Siguiente Paso:** Implementación del SDK de Colonización (App-Parásito) y Protocolo de Malla (Mesh).

## Strategic Pivot (L1 Watchtower, 2026-04-30)

- **Execution focus changed:** Desktop-first Flutter convergence for the next delivery wave.
- **Freeze rule:** Mobile Nomad and browser dashboards are frozen for net-new features; only security/health maintenance is allowed.
- **Commercial priority:** Mature audio perception, video perception, and voice loop in a controlled desktop environment before reopening cross-platform expansion.
- **Non-negotiable architecture rule:** `src/core/` remains platform-agnostic and is the only business-logic authority.
- **Re-entry condition:** Mobile/web expansion resumes only when desktop readiness gates (stability, latency, demo reliability, packaging) are met and documented.

## Desktop Migration Progress (Block 50.1, 2026-04-30)

- **Status:** CLOSED ✅
- **Deliverable:** `src/clients/flutter_desktop_shell` boots as a desktop shell and shows live kernel connection state.
- **Transport baseline:** Heartbeat via `GET /api/ping` and health payload retrieval via `GET /api/status`.
- **Resilience proof:** On backend outage the client enters retry mode and reconnects automatically after server restart (bounded short backoff).
- **Validation:** `flutter analyze` + `flutter test` (desktop shell module) passed locally.

## Bloques Activos

- **V2.95-V2.97: SHERPA-ONNX WAKE WORD & VOICE HARDENING** - CLOSED ✅
  - Integrated Sherpa-ONNX v1.13.0 (4 ABIs, .so + API JAR).
  - Implemented real `VoiceEngine.kt` with continuous background KWS (Wake word: "Ethos").
  - Hardened `TtsEngine.kt` with emulator fallbacks (es-ES → en-US).
  - Fixed resource leaks (OkHttpClient) and race conditions (@Volatile) in `NomadService.kt`.
  - Automated binary sync in `sync_engine.py` and project-wide formatting with `ruff.toml`.
  - **Evidencia:** `Logcat: WAKE WORD DETECTED: 'ethos' -> Triggering cognitive cycle`.

- **V2.94: VOICE PIPELINE SCAFFOLDING (TTS + Listening)** - CLOSED ✅
  - Created `TtsEngine.kt` (Android TTS) and `VoiceEngine.kt` (Continuous AudioRecord).
  - Wired `ChatViewModel` for automatic vocal response.
  - Background listening enabled in `NomadService`.

- **V2.93: SLM ENGINE INFILTRATION (llama.cpp)** - CLOSED ✅
  - Automated `llama.cpp` source syncing and `CMakeLists.txt` generation.
  - Implemented real `llama_model`/`llama_context` lifecycle in `llama-jni.cpp`.
  - Tokenization and decoding loop ready for local GGUF execution.

- **V2.92: MEMORY CONTINUITY (Persistence ↔ Chat)** - CLOSED ✅
- **V2.91: CI ECONOMY DIRECTIVE** - CLOSED ✅
- **V2.90: HYBRID COGNITION & HARDWARE AWARENESS** - CLOSED ✅
- **V2.87: LLAMA.CPP JNI SCAFFOLDING** - CLOSED ✅
- **V2.86: NOMAD PERSISTENCE SETUP (ROOM DB)** - CLOSED ✅
- **V2.85: ETHOS KERNEL ON-DEVICE (Fase 24a)** - CLOSED ✅

## Hoja de Ruta (Roadmap V2) — Ejecución Incremental

### Fase 24b — Persistencia + SLM ✅ COMPLETA
- ✅ Room DB para memoria, identidad, roster.
- ✅ Hybrid Cognition & Hardware Awareness (Tiers: POCKET/NOMAD/CENTINELA).
- ✅ llama.cpp Inferencia real (Backend NDK completo).
- **🚪 GATE PASSED:** La app Android soporta el ciclo completo de inferencia nativa vía llama.cpp.

### Fase 25 — Voice Pipeline (IN PROGRESS)
- ✅ Sherpa-ONNX v1.13.0 Integration (Native KWS).
- ✅ Wake Word "Ethos" functional in background (Low latency, silent).
- ✅ TTS fallback and lifecycle hardening.
- ⬜ Sherpa-ONNX STT (Speech-to-Text) to replace WebSocket pulse.
- ⬜ Full vocal turn (STT → Inference → TTS) without screen interaction.
- **🚪 GATE 1 PASSED:** Saying "Ethos" in the background triggers a server pulse via WebSocket and a local log confirmation.

### Fase 25+ — Proactividad y Sensores
- ⬜ SalienceDetector + ProactiveEngine.
- ⬜ GPS, acelerómetro, CameraX.
- **🚪 GATE:** Ethos comenta proactivamente algo sobre el entorno sin que el usuario pregunte. En dispositivo real.

## System health (2026-04-28)

- **Tests:** 221/221 ✅ (backend) + 25+ on-device gate tests (field-verified)
- **Ruff:** Clean (`ruff check: 0`)
- **Voice:** Sherpa-ONNX v1.13.0 KWS (Local) + Native Android TTS (Hardened)
- **Ethics:** Basada en precedentes (CBR, 36 casos)
- **Memory:** Híbrida (Semantic Embeddings + TF-IDF fallback)
- **Pipeline:** Single-Call Hardened (Fase 24a complete)

> **Visión Nómada (Canónica):** Ver `docs/VISION_NOMAD.md`.
