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
- **Fase:** 22 (Identity Roster & Narrative Enrichment) - EN PROGRESO
- **Logro:** Ethos ahora extrae "Fichas de Identidad" (Roster) asíncronamente y guarda episodios narrativos ricos (250 chars) en STM/Memory.
- **Siguiente Paso:** Validar llenado de Fichas de Identidad mediante chat continuo.

## Bloques Activos
- **V2.75: NARRATIVE ROSTER & MEMORY ENRICHMENT**
  - Creado `src/core/roster.py` (`Roster`, `PersonCard`).
  - Extracción asíncrona vía `roster.observe_turn()` al procesar el mensaje del usuario.
  - Inyección de contexto de rostros conocidos (`roster.get_context()`) en `_build_system()`.
  - Ampliado `Memory.add()` a 250 caracteres por mensaje para preservar detalle episódico.
  - Tests en `test_roster.py` pasando. 202/202 pasando globalmente.

## Bloques Recientes
- **V2.74: PLUGIN STM CONTINUITY + TELEMETRY** - CLOSED ✅
  - Fix: `web_context` siempre inicializado (bug de variable no declarada).
  - STM ahora guarda `user_message + [dato obtenido vía Plugin: ...]` para continuidad.
  - `plugin_used` expuesto en evento `done` + badge 🔌 verde en UI.
  - **199/199 pasando.**
- **V2.73: WEB SEARCH PLUGIN + WEATHER** - CLOSED ✅
  - `WeatherPlugin` (wttr.in), `WebPlugin` (DuckDuckGo), detección determinista.
  - Inyección en mensaje de usuario (no en system prompt) para superar RLHF bias.
- **V2.72: EXTERNAL PLUGINS ARCHITECTURE** - CLOSED ✅
  - `src/core/plugins.py` creado. Plugins: `Time`, `System`.
  - `chat.py` intercepta `[PLUGIN: X]`, ejecuta, reinyecta, re-despacha al LLM.
- **V2.71: VAULT AUTHORIZATION PIPELINE** - CLOSED ✅
  - Flujo de solicitud `[GET_VAULT]` y autorización por WebSockets.

## Roadmap Aspiracional (L0 Vision — 2026-04-25)

> **Plugin Tool-Use con LoRA / DAO refinement:**  
> La arquitectura de plugins (V2.72) está funcional y probada. La rugosidad actual en la invocación de herramientas (el LLM a veces responde desde memoria en lugar del plugin) es inherente al modelo base (Llama 3.1 8B) y no del Kernel.  
>  
> **Plan a largo plazo:**
> - **DAO de refinamiento colectivo:** Datasets de conversaciones curadas por la comunidad donde el uso correcto de herramientas sea la respuesta esperada. Estos ejemplos enriquecen el fine-tuning base.
> - **LoRAs como máscaras de interfaz:** Adapters ligeros (<100MB) entrenados específicamente sobre el protocolo `[PLUGIN: X]`, el formato de la Bóveda, y la identidad de Ethos. Se intercambian por contexto (ciudadano, médico, legal) sin reentrenar el modelo base.
> - **Beneficio neto:** El Kernel V2 se vuelve el *runtime* estable; las LoRAs son la *personalidad / competencia específica*. El contrato entre ambos es el system prompt actual.

Sensory expansion via hardware (Nomad camera/mic integration) is **FROZEN** until better resources/hardware are available. Development will now focus on higher-level conversational features and kernel logic via traditional chat interfaces.

## Closed blocks

| Block | Name | Status |
|-------|------|--------|
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

## Frozen blocks ❄️

| Block | Name | Reason |
|-------|------|--------|
| SENSORY-HW | High-frequency continuous sensory hardware integration | SoC hardware limitations (Android media pipeline constraints) |

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

- **Tests:** 188/188 ✅
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
