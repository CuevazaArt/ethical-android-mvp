# Session Context — Ethos 2.0

> Read THIS file first. Only read AGENTS.md if you need clarification on rules.

## Current state

- **Version:** Ethos V2 Core Minimal (Fase 17 COMPLETA)
- **Architecture:** `src/core/` → `src/server/` (zero legacy)
- **LLM:** Ollama local (llama3.2:1b default; gemma3, devstral available)
- **V1 archive tag:** `v15-archive-full-vision` (frozen reference, do not modify)
- **Last merge to main:** 2026-04-25 (V2.70 — `v2.70-secure-vault`)

## Fase α ✅ · Fase β ✅ · Fase γ ✅ · Fase δ ✅ · Fase 16 ✅ · Fase 17 ✅ · Fase 18 ✅

## Estado Actual (Abril 2026)
- **Fase:** 23 (Nomad Native Android SDK Transition) - COMPLETA ✅
- **Logro:** Setup de Core Android (Gradle/Compose) y Servicios en primer plano funcionales.
- **Siguiente Paso:** Implementación del SDK de Colonización (App-Parásito) y Protocolo de Malla (Mesh).

## Bloques Activos
- **V2.80: MESH COLONIZATION & HYBRID COGNITION** - IN PROGRESS
  - Done: `mesh_protocol_v1.md`, `CognitiveInterfaces.kt`, `AudioStreamer.kt`, `mesh_listener.py`, `mesh_models.py`, `test_mesh_models.py`.
  - Pending: `NodeProfiler.kt` (Android hardware telemetry), integration testing.

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

> **Vision: Colonización Distribuida (Android Parasitization):**
> No se trata de reemplazar Android (drivers propietarios), sino de parasitarlo como un "hipervisor social".
> - **Capa Física:** Smartphones relegados (Android 8+) actuando como "sustrato biológico".
> - **SDK Colonizador:** App-agente que expone capacidades (CPU/GPU/NPU) a una malla distribuida.
> - **Protocolo de Malla:** P2P (libp2p/WebRTC) para descubrimiento y asignación de tareas.
> - **Kernel de Modelo:** Inferencia fragmentada (modelos 1B-8B según RAM del nodo).
> - **Multiplexor Físico:** Rack de laboratorio para clusters locales de alta densidad (ADB over USB).


## Hoja de Ruta (Roadmap V2)

### Corto Plazo (Fase 23: Mono-Smartphone Híbrido)
- Inicializar proyecto en Android Studio con Jetpack Compose.
- Implementar **Foreground Service** para persistencia en background (evitando muerte de proceso).
- Reemplazar capturas WebRTC por acceso nativo `CameraX` y `AudioRecord` (PCM crudo 16kHz).
- Crear el *Router Cognitivo* que delegue tareas de alta complejidad al Ethos Kernel (Python Backend) y tareas básicas a SLMs locales.
- Integrar Wake Words on-device (e.g. Porcupine) para escucha pasiva de bajo consumo.

### Medio Plazo (Delegación Sensorial y DAO)
- Integración de biometría extendida desde Android (Acelerómetro, GPS, Batería, Luz ambiental) fluyendo hacia el `SensoryBuffer` del Kernel.
- Acoplamiento con el sistema DAO para gobernanza de memoria.
- Estabilidad de red offline y sincronización retardada de memorias (Psi-Sleep nativo).

### Largo Plazo (Nomad Physical Mesh / Solarpunk Robotics)
- Transición a hardware físico dedicado.
- Conexión física USB-C/Thunderbolt de múltiples Android obsoletos en un chasis robótico para sumar potencia de cálculo en clúster local (Edge Mesh Swarm).
- Autosuficiencia energética mediante puente a baterías motrices de alta capacidad.
- Independencia total del Cloud (100% inferencia multi-nodo en el dispositivo robótico).



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
| Nomad | `https://[LAN-IP]:8443/nomad` |

## System health (2026-04-25)

- **Tests:** 203/203 ✅
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

- **V2.61 - V2.64 (Mente y Memoria):** Implementado el Arquetipo Narrativo (nivel 3 de destilación) en `Identity` y persistencia en disco del `UserModelTracker`. Modificado `llm.py` con máquina de estados para silenciar etiquetas `<think>`.
- **V2.60 (Sensory Feedback Suppression):** Se eliminó el `AudioContext` de la PWA para evitar el "pulso rítmico" por conflicto de hardware. Se agregó una rutina de rescate de transcripción interina en `onend`.
- **L1-AUDIT-PULSE (2026-04-24):** Resolución de conflictos de importación en tests tras la consolidación V2. Todo el kernel ahora importa exclusivamente de `src.core.*`.
- **V2.22 (Consolidated Core Minimal):** El kernel ha sido completamente movido a `src/core/`. Se eliminaron docenas de archivos del monolito Tri-Lobo legacy en favor de una arquitectura minimalista y directa.
