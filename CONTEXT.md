# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos V2 Core Minimal (Fase 17 COMPLETA)
- **Architecture:** `src/core/` → `src/server/` (zero legacy)
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-28 (Fase 24a — Kernel Ético On-Device)
- **Visión canónica:** `docs/VISION_NOMAD.md`

## Fase α ✅ · Fase β ✅ · Fase γ ✅ · Fase δ ✅ · Fase 16 ✅ · Fase 17 ✅ · Fase 18 ✅

## Estado Actual (Abril 2026)
- **Fase:** 23 (Nomad Native Android SDK Transition) - COMPLETA ✅
- **Logro:** Setup de Core Android (Gradle/Compose) y Servicios en primer plano funcionales.
- **Siguiente Paso:** Implementación del SDK de Colonización (App-Parásito) y Protocolo de Malla (Mesh).

## Bloques Activos
- **V2.85: ETHOS KERNEL ON-DEVICE (Fase 24a)** - ACTIVE 🔨
  - Created `core/EthosSignals.kt` — Kotlin port of `Signals` dataclass.
  - Created `core/EthosPerception.kt` — Full port of deterministic classifier (20+ rules, negation, boosters, hypothetical dampening).
  - Created `core/EthosSafety.kt` — Full port of sanitization + danger detection (11 bilingual patterns, leet-speak, Unicode stripping).
  - Created `core/EthosKernelGate.kt` — Integration gate (25+ tests via Logcat).
  - Wired gate into `MainActivity.kt` → runs on every app launch.
  - Created directory stubs: `conversation/`, `sensory/`, `data/`, `inference/`.
  - Files: `core/EthosSignals.kt`, `core/EthosPerception.kt`, `core/EthosSafety.kt`, `core/EthosKernelGate.kt`, `MainActivity.kt`.
  - **🚪 GATE:** Pending Logcat verification in Android Studio emulator.
- **V2.84b-d: UX FIXES + RESEARCH** - CLOSED ✅
  - Fixed vault loop (backend `vault_key: null` → `""`).
  - Muted SpeechRecognizer beeps via AudioManager hack.
  - Injected Meta WhatsApp warm persona prompt.
  - Boosted TTS volume +50%.
  - Integrated external OSS tech review.
- **V2.82: NOMAD CHAT PRODUCTION UI (3 Ciclos)** - CLOSED ✅
  - Ciclo 1: ChatScreen + ChatViewModel producción, EthosColors, Gradle deps.
  - Ciclo 2: TTS playback (MediaPlayer), Vault dialog (AlertDialog), /api/ping.
  - Ciclo 3: Speaking indicator animado en TopBar, polish de animaciones.
  - Files: `ui/ChatScreen.kt`, `ui/ChatViewModel.kt`, `ui/EthosColors.kt`, `app.py`.
- **V2.81: NOMAD NATIVE CHAT UI & SYNC BRIDGE** - CLOSED ✅
  - Stubs iniciales + AGENT_CONTEXT.md + SYNC.md + SESSION_PROMPT.md.
  - Established bidirectional sync protocol between Antigravity and Android Studio.
- **V2.80: MESH COLONIZATION & HYBRID COGNITION** - STASIS ⏸️
  - Done: `mesh_protocol_v1.md`, `CognitiveInterfaces.kt`, `AudioStreamer.kt`, `mesh_listener.py`, `mesh_models.py`, `test_mesh_models.py`, `NodeProfiler.kt`, `mesh_server.py`.
  - Pending: `MeshClient` (Android OkHttp WebSocket).

## Bloques Recientes
- **V2.79: PARASITE SDK & MESH DISCOVERY** - CLOSED ✅
  - Files: `LICENSING_STRATEGY.md`, `TRADEMARK.md`, `.github/FUNDING.yml`, `LICENSE_BSL`, `AGENTS.md`.
  - Established Hybrid Licensing (Apache 2.0 Kernel + BSL 1.1 SDK).
  - Tests: 203/203.

- **V2.78: NATIVE ANDROID CORE SETUP** - CLOSED ✅
  - Inicializado proyecto Gradle / Jetpack Compose.
  - Configurados permisos (`RECORD_AUDIO`, `INTERNET`, `FOREGROUND_SERVICE`).
  - Creados `MainActivity` y `ForegroundService` base para persistencia.
- **V2.77: NATIVE ANDROID SCAFFOLDING** - CLOSED ✅
  - PWA archivada y código refactorizado hacia el SDK de Android.
  - Roadmap actualizado con enfoque Híbrido y Malla Física V2.

- **V2.76: PSI-SLEEP COGNITIVE CONSOLIDATION** - CLOSED ✅
  - Creado `src/core/sleep.py` (`PsiSleepDaemon`).
  - Daemon acoplado a los eventos de `startup`/`shutdown` en `FastAPI` (`app.py`).
  - Sustituye la reflexión síncrona bloqueante (`self._turn_count % 5 == 0`) de `chat.py`.
  - El sistema entra en modo REM tras 120s de inactividad, destilando y consolidando memorias de identidad.
  - Tests en `test_sleep.py` pasando. 203/203 pruebas limpias.

- **V2.75: NARRATIVE ROSTER & MEMORY ENRICHMENT** - CLOSED ✅
  - Creado `src/core/roster.py` (`Roster`, `PersonCard`).
  - Extracción asíncrona vía `roster.observe_turn()`.
  - Inyección de contexto de rostros conocidos (`roster.get_context()`) en `_build_system()`.
  - Ampliado `Memory.add()` a 250 caracteres por mensaje.
- **V2.74: PLUGIN STM CONTINUITY + TELEMETRY** - CLOSED ✅
  - Fix: `web_context` siempre inicializado (bug de variable no declarada).
  - STM ahora guarda `user_message + [dato obtenido vía Plugin: ...]` para continuidad.
  - `plugin_used` expuesto en evento `done` + badge 🔌 verde en UI.
  - **203/203 pasando.**
- **V2.73: WEB SEARCH PLUGIN + WEATHER** - CLOSED ✅
  - `WeatherPlugin` (wttr.in), `WebPlugin` (DuckDuckGo), detección determinista.
  - Inyección en mensaje de usuario (no en system prompt) para superar RLHF bias.
- **V2.72: EXTERNAL PLUGINS ARCHITECTURE** - CLOSED ✅
  - `src/core/plugins.py` creado. Plugins: `Time`, `System`.
  - `chat.py` intercepta `[PLUGIN: X]`, ejecuta, reinyecta, re-despacha al LLM.
- **V2.71: VAULT AUTHORIZATION PIPELINE** - CLOSED ✅
  - Flujo de solicitud `[GET_VAULT]` y autorización por WebSockets.

> **Visión Nómada (Canónica):** Ver `docs/VISION_NOMAD.md` + `docs/ARCHITECTURE_NOMAD_V3.md`.
> La visión es ASPIRACIONAL. La ejecución es INCREMENTAL y VERIFICADA EN CAMPO.
> **Regla de oro:** Un bloque NO está cerrado hasta que funciona EN EL SISTEMA REAL, no solo en tests.

## ⚠️ Lecciones de V1 — NO REPETIR

1. **V1 murió por amplitud sin profundidad.** Cientos de archivos, abstracciones elegantes, nada funcionaba de punta a punta. V2 sobrevivió porque cada bloque se probó en campo antes de abrir el siguiente.
2. **Tests verdes ≠ funciona.** 203 tests pasando no significa que el chat responde. Verificar integración real: levantar servidor, enviar mensaje, ver respuesta, confirmar en hardware.
3. **No crear archivos sin que se usen.** Si `EthosPerception.kt` no es invocado por ningún código en producción, no existe. Un archivo que solo pasa tests unitarios es deuda técnica disfrazada de progreso.
4. **Los docs aspiracionales no son deuda técnica.** `ARCHITECTURE_NOMAD_V3.md` es la brújula. No es un backlog. No hay presión por "cerrar" los 20 bloques.
5. **Vertical > Horizontal.** Es mejor tener Safety+Perception portados Y FUNCIONANDO en la app real, que tener los 20 bloques "al 70%".

## Definición de Done (Estricta)

Un bloque se considera CLOSED ✅ solo si:

| Criterio | Descripción |
|----------|-------------|
| **Tests** | Unit tests pasan (necesario pero no suficiente) |
| **Integración** | El código es invocado por el sistema en producción (app.py o NomadService) |
| **Demo** | Existe evidencia ejecutable: log, screenshot, o video del feature funcionando |
| **Campo** | Si toca Android: probado en emulador O dispositivo real, no solo compilado |
| **Regresión** | 203/203 backend tests siguen pasando. App sigue compilando. |
| **Poda** | Si algo quedó obsoleto por el nuevo código, fue eliminado en el mismo bloque |

## Hoja de Ruta (Roadmap V2) — Ejecución Incremental

> Cada fase tiene un **integration gate**: un demo concreto que debe funcionar
> antes de abrir la siguiente fase. Sin gate pasado, la fase no se cierra.

### Fase 24a — Kernel Ético On-Device (EN PROGRESO 🔨)
- ✅ Portar Perception a Kotlin (`EthosPerception.kt`).
- ✅ Portar Safety a Kotlin (`EthosSafety.kt`).
- ✅ Crear data class Signals (`EthosSignals.kt`).
- ✅ Crear Integration Gate (`EthosKernelGate.kt`).
- ✅ Wired gate into `MainActivity.kt`.
- ⏳ Verificar en emulador vía Logcat (requiere Android Studio Run).
- **🚪 GATE:** Enviar "hay un herido" a EthosPerception.kt → recibir `Signals(context="medical_emergency")` EN LA APP ANDROID corriendo en emulador. Sin servidor. Sin LLM.

### Fase 24b — Persistencia + SLM
- Room DB para memoria, identidad, roster.
- llama.cpp JNI para SLM on-device.
- **🚪 GATE:** La app Android genera una respuesta de texto coherente a "Hola" usando SLM local, con memoria persistida entre reinicios. Sin red.

### Fase 25 — Voice Pipeline
- Sherpa-ONNX + Silero VAD para wake word.
- TTS automático para toda respuesta.
- Conversación de 3 turnos por voz sin tocar pantalla.
- **🚪 GATE:** Decir "Ethos, ¿qué hora es?" por voz → escuchar la hora por TTS. Sin tocar la pantalla.

### Fase 25+ — Proactividad y Sensores
- SalienceDetector + ProactiveEngine.
- GPS, acelerómetro, CameraX.
- **🚪 GATE:** Ethos comenta proactivamente algo sobre el entorno sin que el usuario pregunte. En dispositivo real.

### Fase 26+ — Cognitive Snapshot, Mesh, DAO, Servidores
- Solo se abre cuando Fases 24-25 tienen gates pasados.



## Closed blocks

| V2.78 | Native Android Core Setup | ✅ |
| V2.70 | Secure Vault (Isolation Boundary) | ✅ |
| V2.66 | CBR Injection (Doctrina Legal) | ✅ |
| V2.65 | LLM Reasoning Suppression (<think>) | ✅ |
| V2.40 | Perception Classifier (Sin LLM, 0ms) | ✅ |
| V2.41 | Case-Based Ethics (CBR Precedents) | ✅ |
| V2.42 | Single-Call Pipeline (Hardening) | ✅ |
| V2.43 | Sentence Embeddings (Memoria Semántica) | ✅ |
| V2.44 | Narrative Identity (LLM Journal Reflections) | ✅ |
| V2.45 | Nomad PWA Ethics HUD (Metadata stream) | ✅ |
| V2.46 | Precedents Expansion (36 rich cases) | ✅ |
| V2.47 | GPU Docker Orchestration (NVIDIA + Ollama) | ✅ |
| V2.48 | LLM Native Multi-turn & Crash Fixes | ✅ |
| V2.49 | Neural TTS (Voz propia para Ethos con edge-tts) | ✅ |
| V2.50 | Sensory Expansion — Autonomous vision triggers | ✅ |
| V2.51 | Thalamic Gate — Wake word protection against background noise | ✅ |
| V2.52 | Limbic System — Emotional TTS and Visual Resonance | ✅ |
| V2.53 | Acoustic Echo Shield — Ignore STT while playing audio | ✅ |
| V2.54 | Cognitive Proprioception — STT semantic echo cancellation & Preemption | ✅ |
| V2.55 | Temporal Multimodal Fusion — Audio & Video context sync | ✅ |
| V2.56 | Status Telemetry Hardening (Boy Scout) | ✅ |
| V2.57 | SensoryBuffer WebSocket Integration — Continuous fusion loop | ✅ |
| V2.58 | Speech-Triggered Immediate Fusion — Zero-delay audio response | ✅ |
| V2.59 | Sensory-Context Perception — Multimodal pattern recognition | ✅ |
| V2.60 | Audio Feedback Suppression — ScriptProcessor removed, SR text rescue, phantom turn kill | ✅ FIELD-TESTED |



## Key files

| Area | Files |
|------|-------|
| Core | `src/core/{llm,ethics,memory,chat,safety,identity,vision,stt,tts,status,precedents}.py` |
| Server | `src/server/app.py` |
| CLI | `src/ethos_cli.py` |
| Entry | `src/main.py` (REPL) · `src/chat_server.py` (uvicorn) |
| Tests | `tests/core/` (165 tests) |
| Security | `scripts/eval/adversarial_suite.py` |
| Deploy | `Dockerfile.gpu` · `docker-compose.gpu.yml` · `scripts/docker_entrypoint.sh` |
| Run | `python -m src.chat_server` or `uvicorn src.server.app:app --port 8000` |
| Run GPU | `docker compose -f docker-compose.gpu.yml up --build` |
| Chat | `http://localhost:8000/` |
| Dashboard | `http://localhost:8000/dashboard` |
| Nomad | `https://[LAN-IP]:8443/nomad` (Archive) · `com.ethos.nomad` (Native) |

## System health (2026-04-27)

- **Tests:** 203/203 ✅ (backend) + 25+ on-device gate tests (pending Logcat verification)
- **Legacy imports:** 0
- **Perception:** Determinista (Sin LLM, latencia <1ms)
- **Ethics:** Basada en precedentes (CBR, 36 casos)
- **Memory:** Híbrida (Semantic Embeddings + TF-IDF fallback)
- **Identity:** Reflexiva (Narrative Journal + Stats)
- **Pipeline:** Single-Call Hardened (Background reflection, Early signaling)
- **PWA HUD:** Contexto ético en tiempo real (metadata event)
- **Adversarial Suite:** 6/6 blocked · 10/10 legitimate pass
- **GPU Deploy:** Docker + NVIDIA Container Toolkit + Ollama sidecar ready
- **Field Test:** Android PWA voice+vision confirmed (v22.3.3-field-tested)

## Known hardware limitations (field-tested)

- **Old Android SoC:** Camera and mic alternate (shared media pipeline). Cannot coexist simultaneously.
- **Mitigation:** SpeechRecognition text rescue on `onend` sends captured speech before mic-off.
- **Future:** Newer hardware with independent media pipelines eliminates this. Native app (Play Store) planned.

## Closed blocks

- **V2.83e (Maintenance):** Estabilización de lint y formato (Ruff) en `src/core` y `tests`. Sincronización completa con la visión Nomad V3.
- **V2.61 - V2.64 (Mente y Memoria):** Implementado el Arquetipo Narrativo (nivel 3 de destilación) en `Identity` y persistencia en disco del `UserModelTracker`. Modificado `llm.py` con máquina de estados para silenciar etiquetas `<think>`.
- **V2.60 (Sensory Feedback Suppression):** Se eliminó el `AudioContext` de la PWA para evitar el "pulso rítmico" por conflicto de hardware. Se agregó una rutina de rescate de transcripción interina en `onend`.
- **L1-AUDIT-PULSE (2026-04-24):** Resolución de conflictos de importación en tests tras la consolidación V2. Todo el kernel ahora importa exclusivamente de `src.core.*`.
- **V2.22 (Consolidated Core Minimal):** El kernel ha sido completamente movido a `src/core/`. Se eliminaron docenas de archivos del monolito Tri-Lobo legacy en favor de una arquitectura minimalista y directa.
