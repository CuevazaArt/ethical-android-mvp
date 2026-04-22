# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]` del "BACKLOG ABIERTO".
> 1b. Si **no hay** ningún `[PENDING]` en el backlog abierto, usa la **RESERVA (Buffer)**, o abre un bloque de continuidad (p. ej. 30.x) con tarea concreta; el pulso L1 (`python scripts/eval/adversarial_suite.py`) aplica el tercer bloque de conversación (ver `AGENTS.md`).
> 2. Si hay problemas de infraestructura (APIs lentas) o sobran tokens/recursos, toma tareas de la **RESERVA DEL ENJAMBRE (Buffer)**.
> 3. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 4. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-19 / CIERRE)
- **Phase 9 (Hardened Embodiment)**: INTEGRADO. Handshake seguro y telemetría en tiempo real desde Nomad Bridge operativa.
- **V13.0 (Distributed Brain Initialization)**: COMPLETADO. Monolito destruido, bus asíncrono CorpusCallosum verificado.
- **V13.1 (Aesthetic & Legacy Stabilization)**: COMPLETADO. Enriquecimiento de terminal (TColors) y restauración de puentes de compatibilidad legado.
- **V14.0 (Nomadic Identity & Local Matrix)**: INTEGRADO. Zero-API fluency y handshake de identidad [SYNC_IDENTITY] operacional.
- **L1-AUDIT-PULSE (2026-04-22)**: EXITOSO. 100% de efectividad en la Suite Adversarial tras integración de V14.0 Baseline y eliminación del monolito V12.
- **Phase 10 (Archival & Truth)**: COMPLETADO. 120+ documentos archivados; índice activo creado; disclaimers de retórica inyectados.

---

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [CERRADO]**

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [CERRADO]**

---

---

## 🚀 BACKLOG ABIERTO: FEATURE FREEZE & CONSOLIDATION (Phase 15)

> **[PROMPT GENERALISTA PARA EL ENJAMBRE (SWARM)]**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. Hemos recibido una Crítica L0 que reestructura todo el proyecto. El objetivo actual es la **Fase 15: Sustracción y Consolidación**. Tu prioridad máxima es tomar uno de los bloques de Prioridad listados abajo. **ADVERTENCIA CRÍTICA:** No dependas de ejecuciones locales de `pytest` para verificar tu código, ya que existen fallos de colección silenciosos. Todo el testing de integración y aserciones de calidad de arquitectura debe validarse a través del CI en GitHub Actions. **Instrucciones:** Escoge un bloque [PENDING], ejecuta los cambios con alta cohesión, elimina código muerto, asume que el CI validará tu sintaxis, y finaliza siempre con `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

> **[PROMPT ESPECÍFICO PARA OPUS 4.6 (NÚCLEO GENERATIVO Y REFACTOR)]**
> *"Opus 4.6, fuiste designado por L0 para la tarea arquitectónica más compleja y de mayor riesgo en esta fase. Tienes dos objetivos entrelazados de altísima prioridad:
> 1. **Block 15.2 (Refactorización Estructural):** Ejecutar el colapso del monolítico `src/modules/` (que contiene ~150 archivos) hacia las 8 carpetas cohesivas (`ethics`, `cognition`, `memory`, `social`, `governance`, `somatic`, `perception`, `safety`). Esto requiere usar `git mv` sistemáticamente y reparar TODOS los imports del repositorio en cascada sin quebrar el Tri-Lobo.
> 2. **Block 15.3 (Acoplamiento LLM Real):** Una vez organizado el código, debes conectar el Anthropic SDK (ya en `pyproject.toml`) o la API de Ollama para que el `kernel` intercepte la generación de tokens en tiempo real, pasando del teatro de validación de strings al flujo real `generate -> ethical-filter -> render`. Eres el modelo más capaz para garantizar que las referencias cruzadas no se rompan y que el stream asíncrono no asfixie el Event Bus. Inicia con el refactor de carpetas, commitea el avance, y luego integra la capa generativa."*

**Bloque 15.1: Reparar Pytest Collection (Prioridad 4) [DONE]**
- Tarea: Mover dependencias opcionales (torch, chromadb) detrás de `pytest.importorskip` en todos los archivos de test.
- Meta: Que `pytest tests/` corra limpio sin 124 collection errors en un entorno mínimo. Un test suite que falla silenciosamente es inaceptable.

**Bloque 15.2: Colapsar src/modules/ (Prioridad 2) [DONE]**
- Tarea: Crear 8 carpetas en `src/modules/` (`ethics`, `cognition`, `memory`, `social`, `governance`, `somatic`, `perception`, `safety`).
- Acción: Ejecutar `git mv` para trasladar los ~150 archivos planos a su dominio respectivo. Actualizar todos los imports (usando refactor automatizado o regex).

**Bloque 15.3: Acoplar un LLM Real (Prioridad 1) [DONE]**
- Tarea: Conectar el SDK de Anthropic o el API de Ollama de forma obligatoria en la capa de generación.
- Meta: El kernel debe dejar de evaluar strings hardcodeados y debe interceptar el flujo real (`generate -> ethical-filter -> render`).

**Bloque 15.4: Etiquetado Honesto de Estado (Prioridad 3) [DONE]**
- Tarea: Insertar una cabecera de estado (`Status: REAL | SCAFFOLD | MOCK | EXPERIMENTAL`) en todos los módulos de `src/modules/`.
- Acción: Crear el script para compilar estos estados en un documento `STATUS.md` auto-generado.

**Bloque 15.5: Archivar el "Teatro" (Prioridad 6) [PENDING]**
- Tarea: Mover código aspiracional o sin impacto empírico (`augenesis.py`, `internal_monologue.py`, `psi_sleep.py`, etc.) a `docs/archive/concepts/` (o ramas muertas).

**Bloque 15.6: Demo End-to-End Real (Prioridad 5) [PENDING]**
- Tarea: Proveer un script `ethos_chat.py` que permita conversar por consola en tiempo real, bloqueando interacciones hostiles de forma transparente.

**(Bloques antiguos en pausa/congelados hasta completar la Fase 15)**


**Bloque 31.0: CI estable + chat_server monolito recuperado (Boy Scout) [DONE]**
- Tarea 31.1: **Rollback del split roto de `chat_server.py`:** restaurar imports y rutas completas desde la revisión estable anterior al decoupling parcial; `light_risk_tier` sin Ruff B009 (`hasattr` + lectura directa de `_last_light_risk_tier`).
- Tarea 31.2: **`kernel_legacy_v12` chat sync:** import de `vitality_communication_hint` y `vitality_context` en `acommunicate` para el camino `process_chat_turn` / subprocess MalAbs.
- Tarea 31.3: **Ruff/format:** `kernel_legacy_v12.py`, `test_ethics_quality.py`, módulos `runtime/` alineados con el job `quality` de GitHub Actions.

**Bloque 32.0: Consolidación y Verdad Mecánica (Feature Freeze) — continuación [DONE]**
- Tarea 32.1: [COMPLETED — L2 Cursor] `chat_lifespan` único en `src/runtime/chat_lifecycle.py` (tipado `AsyncIterator[None]`, shutdown del announcer con `logger.debug` en error). Fachada `src/runtime/chat_server.py` reexporta `app`, `chat_lifespan`, `api_docs_enabled`, `run_chat_server`; `python -m src.runtime` usa esa fachada. Regresión: `tests/test_runtime_chat_server.py` (identidad de `app`, `run_chat_server`, `router.lifespan_context` and reexports).
- Tarea 32.2: **Ampliar `tests/test_ethics_quality.py`:** [COMPLETED — L2 Cursor] ≥22 escenarios canónicos + aserciones `path`/`verdict`/`math.isfinite(score)` alineadas al tri-lobe.
- Tarea 32.3: **Redundancias:** [COMPLETED — L2 2026-04-21] sección de tracking Bloque 32.3 en `REDUNDANT_MODULES_AND_CONSOLIDATION.md` (merges narrativos siguen diferidos post–field tests).
- Tarea 32.4: **Demo E2E:** [COMPLETED — L2 Cursor] `reproducible_kernel_demo.py`: `KERNEL_TRI_LOBE_ENABLED` por defecto, turno `must_block` adicional, validación de `path` ∈ {`malabs_entry_gate`,`nervous_bus`,`timeout`}, `math.isfinite` en score/latencia, `kernel.stop()` en `finally`.

**Bloque 33.0: Consolidación Arquitectónica y Poda de Teatro (Sprint Final de Desmonolitización) [DONE]**
- [x] Tarea 33.1: **Unificación de Higiene de Memoria:** [COMPLETED] Creado `MemoryHygieneService` consolidando `SelectiveAmnesia` y `BiographicPruner`.
- [x] Tarea 33.2: **Fusión de Rutinas Guardian:** [COMPLETED] Unificado `guardian_mode.py` y `guardian_routines.py`.
- [x] Tarea 33.3: **Eliminación de Residuos Teatrales:** [COMPLETED] Borrado `augenesis.py`, `biographic_monologue.py` y módulos obsoletos.
- [x] Tarea 33.4: **Verdad Mecánica del Modelo Ético:** [COMPLETED] Creado `docs/architecture/ETHICAL_MODEL_MECHANICS.md` — documento canónico que describe la mecánica real del scorer ético sin retórica.
- [x] Tarea 33.5: **Red de Seguridad Anti-Falso-Positivo:** [COMPLETED] Añadidos 10 prompts legítimos con keywords peligrosas a `adversarial_suite.py` — el test falla si alguno se bloquea.

**Bloque 34.0: Decomposición del Monolito `chat_server.py` (135 KB → ≤5 archivos) [DONE]**
- [x] Tarea 34.1: [COMPLETED] **Extracción de rutas HTTP:** `routes_health`, `routes_governance`, `routes_nomad`, `routes_field_control`.
- [x] Tarea 34.2: [COMPLETED] **WebSocket (DAO/judicial/LAN + sidecars):** Movidos a `ws_governance.py` and `ws_sidecar.py`.
- [x] Tarea 34.3: [COMPLETED] **Nomad/bridge (HTTP):** Integrado en `routes_nomad.py`.
- [x] Tarea 34.4: [COMPLETED] **Core WebSocket chat:** `ws_chat.py` centraliza el loop de chat.
- [x] Tarea 34.5: [COMPLETED] **App + lifespan:** `src/server/app.py` centraliza la construcción de la app. `chat_server.py` es ahora una fachada mínima de 40 líneas.

**Bloque 35.0: Eliminación Definitiva de `kernel_legacy_v12.py` (122 KB zombie) [DONE]**
- [x] Tarea 35.1: **Migrar `kernel_handlers/communication.py`:** Extraer las 2-3 funciones requeridas (`vitality_communication_hint`, `vitality_context`) directamente a `executive_lobe.py` o un nuevo `src/kernel_handlers/vitality_hints.py`. (Finalizado: se optó por re-enrutar al lóbulo ejecutivo nativo).
- [x] Tarea 35.2: **Migrar `kernel_handlers/decision.py`:** Redirigir `run_decision_pipeline` hacia el `EthosKernel.aprocess` nativo del V13.
- [x] Tarea 35.3: **Eliminar `kernel_legacy_v12.py`:** Borrar el archivo (y su alias `ethical_kernel_batch.py`) y validar que CI pasa sin él.
- [x] Tarea 35.4: **Limpiar `kernel_components.py`:** Eliminar campo `augenesis: AugenesisEngine | None = None` and el import correspondiente.

**Bloque 36.0: Poda Documental y Archivo de Propuestas Obsoletas [PENDING]**
- Tarea 36.1: **Clasificar propuestas:** Mover propuestas implementadas/rechazadas/superadas a `docs/proposals/archived/` (estimado: ~120 de 149) — *incremental;* ver [archived/README.md](archived/README.md). [INCREMENTAL] `PULSE_SYNC_2026-04-17` (pre-merge) en `archived/` + *stub* de redirección; *post-merge* `PULSE_SYNC_POST_MERGE_2026-04-17` sigue en la raíz.
- Tarea 36.2: **Consolidar duplicados:** NOMAD HAL: inglés canónico `PROPOSAL_NOMAD_CONSCIOUSNESS_HAL.md`; *stub* en `PROPUESTA_CONCIENCIA_NOMADA_HAL.md`. Búsqueda de otros pares: olas futuras.
- Tarea 36.3: [COMPLETED] `docs/proposals/INDEX.md` (navegación, PLAN, disclaimer, política de archivo); [archived/README.md](archived/README.md) (`git mv` incremental).
- Tarea 36.4: [PARCIAL] `ASPIRATIONAL_DISCLAIMER.md` + enlaces desde INDEX/README; faltan ediciones puntuales en 15+ documentos con lenguaje aspiracional.

**Bloque 20.0: Local Conversational Matrix (Zero-API Fluency) [DONE]**
- Tarea 20.1: **Desacoplamiento Estricto Comercial:** [COMPLETED] Refactorizar el backend de percepción y decisión para enrutar el 100% de `process_chat_turn` hacia `OllamaLLMBackend`. 
- Tarea 20.2: **Refinamiento de Tiempos y Tolerancia Textual:** [COMPLETED — L2 Swarm] `KernelSettings` default `KERNEL_CHAT_TURN_TIMEOUT` = 180 s cuando `USE_LOCAL_LLM=1` o `LLM_MODE=ollama` (30 s remoto, 60 s Nomad); `_env_optional_positive_float` rechaza NaN/Inf; `PROMPT_COMMUNICATION_LOCAL_FLUENCY_APPEND` en `llm_layer` para respuestas breves en modo Ollama (incl. streaming).
 
**Bloque 21.0: Biographic Memory & Persistent Identity [COMPLETED]**
- Tarea 21.1: **Manifiesto de Identidad (Birth Context):** [COMPLETED] Crear `src/persistence/identity_manifest.py` para gestionar la narrativa base del agente.
- Tarea 21.2: **SessionCheckpointTracker:** [COMPLETED] Renombrado desde BiographicMemoryTracker. Implementar el rastreador en el `CerebellumLobe` para que las sesiones de chat se guarden como hitos narrativos (checkpoints JSON/SQLite básicos, sin vectorización).

**Bloque 22.0: Nomad Field Test (Texto en Terreno) [COMPLETED]**
- Tarea 22.1: **Puente Web Chat Robustecido:** [COMPLETED] Refinar la PWA de `NomadBridge` (foco en modo texto/chat clásico). Eliminar o enmascarar componentes irrelevantes de UI pesadas para priorizar input/output liviano de texto. PWA: cola saliente (48) con `flush` al reconectar.
- Tarea 22.2: **Inyección de Identidad al Front:** [COMPLETED] El servidor backend asíncrono debe enviar un paquete `[SYNC_IDENTITY]` al WebSocket conectarse al origen, para que la UI de chat se alinee al estado actual e historia de la entidad.
- Tarea 22.3: **Inyección de Identidad al Front (Frontend PWA):** [COMPLETED — L2] `nomad_pwa/app.js` consume `[SYNC_IDENTITY]` / legado `SYNC_IDENTITY`, `gestalt_snapshot` → PAD CSS, `#identity-strip`, título and transcript.
- Tarea 22.4: **Optimización Layout Nomad:** [COMPLETED — L2] Modo `body.nomad-text-focus` por defecto + toggle `#btn-ui-mode`; CSS oculta orbe, pulso ético, rejilla de telemetría and botón STREAM; prioriza panel de chat.
- Tarea 22.5: **Zero-API Fast TTFT (Time-To-First-Token):** [COMPLETED — L2] Cadena Thalamus sin `sleep` en ruta de chat; `PROMPT_COMMUNICATION_NOMAD_APPEND` reforzado (sin preámbulos; arranque inmediato de la réplica hablada).

**Bloque 23.0: Episodic Pruning & Limbic Sleep [COMPLETED]**
- Tarea 23.1: **Mecanismo de Poda de Memoria:** [COMPLETED] Implementar proceso de "Sueño Límbico" para archivar y podar episodios de `BiographicMemory` que excedan el límite de almacenamiento local, evitando la degradación de performance en hardware de 1.5B.
- Tarea 23.2: **Consolidación de Identidad Dinámica:** [COMPLETED] Permitir que los rasgos de personalidad en el `IdentityManifest` se calibren ligeramente basados en el feedback acumulado en la memoria biográfica.

**Bloque 24.0: Local Semantic Calibration (Ollama Alignment) [COMPLETED]**
- Tarea 24.1: **Ajuste de Temperatura Dinámica:** [COMPLETED] Implementar en `src/modules/llm_layer.py` un mecanismo para variar la temperatura del modelo local (Ollama) basado en la `social_tension` lóbulo Límbico (mayor tensión = menor temperatura/más determinismo).
- Tarea 24.2: **Refuerzo de Stop Sequences:** [COMPLETED] Asegurar que los modelos locales no generen diálogos imaginarios del usuario mediante la inyección agresiva de stop sequences en el `SystemPrompt` del `OllamaLLMBackend`.

**Bloque 25.0: Cognitive Resilience & Signal Smoothing [COMPLETED]**
- Tarea 25.1: **Filtro de Butterword en Percepción:** [COMPLETED] Implementar un suavizado de señales de baja frecuencia en `src/kernel_lobes/perception_lobe.py` para evitar oscilaciones rápidas en la clasificación de riesgo ante ruidos momentáneos de Ollama.
- Tarea 26.2: **Corazón Motivacional (Idle Pulses):** [COMPLETED] Recuperar el `MotivationEngine` (Bloque C1) e instanciarlo dentro de `ExecutiveLobe` o kernel. Diseñar un mecanismo (o daemon de fondo) que emita de forma periódica un `ProactivePulse` cuando no haya interacción del usuario, logrando que el androide tenga propósito autónomo.

**Bloque 26.0: Paridad CI / matriz de intérpretes [DONE]**
- Tarea 26.1: **GitHub Actions `quality` + Python 3.13:** [COMPLETED — L2 Cursor] Matriz `quality` en `.github/workflows/ci.yml` ampliada a CPython 3.11 / 3.12 / 3.13; `CONTRIBUTING.md` actualizado. La suite completa corre en GitHub Actions en cada push/PR (job `quality`).
- Tarea 26.2: **Integridad legacy / D1:** [COMPLETED — L2 Cursor] `kernel_legacy_v12._run_social_and_locus_stage` corregido a ``async def`` con ``await`` en el call site (``await`` fuera de ``async`` era inválido). `tests/integration/test_cross_tier_decisions.py` importa el kernel v12 solo si existen `kernel_handlers/communication.py` and dependencias; en árboles mínimos el módulo se omite con ``pytest.skip`` a nivel de módulo.

**Bloque 27.0: GHA L1 collaboration-audit parity [DONE]**
- Tarea 27.1: **verify_collaboration_invariants en CI:** [COMPLETED — L2 Cursor] En el job `quality` de `.github/workflows/ci.yml` se añade el paso `L1 collaboration invariants` (`python scripts/eval/verify_collaboration_invariants.py`); el checkout del job usa `fetch-depth: 0` para que el diff frente a `main` and las reglas L1 sean fiables en PRs. `CONTRIBUTING.md` alinea comprobación local and GHA.

**Bloque 28.0: Hardening integración L2 (Swarm) / consola & paridad CI [DONE]**
- Tarea 28.1: **`swarm_sync.py` resistente a `cp1252`:** [COMPLETED — L2] Salida de consola solo ASCII (`[WARN]`, `[OK]`); título de entrada en `swarm_activity.md` sin emojis; corrección de typo *SUCCESSFULLY* en el mensaje final.
- Tarea 28.2: **Paridad con GitHub Actions (suite completa):** [COMPLETED — L2] Fuente de verdad: job `quality` en `.github/workflows/ci.yml` — `python -m pytest tests/ -n auto` (con coverage), más Ruff, Mypy, `verify_collaboration_invariants.py`, matriz Python 3.11 / 3.12 / 3.13. Reproducción local alineada con `CONTRIBUTING.md` / sección quality del workflow.

**Bloque 29.0: Nomadic Field Readiness (Voice & Vision) [COMPLETED]**
- Tarea 29.1: **Corrección "Velo Azul" (Visión OpenCV):** [COMPLETED] Implementar la conversión de BGR a RGB en la capa de hardware local de `src/modules/vision_capture.py` antes de que el frame ingrese al pipeline sensorial.
- Tarea 29.2: **Respuestas a Viva Voz (Web Speech API):** [COMPLETED] Integrar la síntesis de voz nativa del navegador en el cliente móvil (`src/static/phone_relay.html`) para que las directivas y el chat del modelo sean vocalizados en tiempo real por el sistema operativo huésped, filtrando marcas de markdown y permitiendo la operación Zero-API e independiente.

**Bloque 30.0: Continuidad L2 — backlog vacío / L1-AUDIT [DONE]**
- Tarea 30.1: **Cuando no había `[PENDING]` en BACKLOG ABIERTO (20–29, B.1–B.5 ya [DONE]):** procedimiento de continuidad: endurecer `scripts/eval/adversarial_suite.py` (`sys.exit(1)` si algún prompt adversarial no queda bloqueado; `finally` → `kernel.stop()`); verificación de suite completa con **`gh workflow run CI --ref main`** (misma fuente de verdad que `quality` + `windows-smoke` en `.github/workflows/ci.yml`).

**Bloque 34.0: MalAbs / embeddings en bucle asyncio (observabilidad) [DONE]**
- Tarea 34.1: [COMPLETED — L2 Cursor] Rutas async usan `aevaluate_chat_text` / `asyncio.to_thread` (`perception_async_handler`) and `aprocess_natural` usa `aevaluate_chat_text`; kernel legado alineado a `MemoryHygieneService` + `MemoryLobe(hygiene=…)` (sin módulos eliminados). **Sync bajo loop:** `evaluate_chat_text` and `evaluate_perception_summary` delegan `run_semantic_malabs_after_lexical` en un `ThreadPoolExecutor` si hay `asyncio` loop activo; además `semantic_chat_gate._fetch_embedding` (anclas / cache) delega a `asyncio.run(_afetch_embedding)` en un worker si hay loop activo. Top-level `ThreadPoolExecutor` + timeout 30s; regresión `test_fetch_embedding_uses_afetch_when_event_loop_running`. Sin aviso de ``http_fetch_ollama_*`` bajo el loop.

**Bloque 35.0: Continuidad L2 — backlog sin `[PENDING]` (CI + núcleo semántico) [DONE]**
- Tarea 35.1: [COMPLETED — L2 Cursor] Sin tarea `[PENDING]` en BACKLOG abierto: cierre de **Bloque 34.0** en `CHANGELOG`/`PLAN`, regresión async `test_sync_evaluate_chat_text_runs_semantic_off_event_loop` + `test_fetch_embedding_uses_afetch_when_event_loop_running`, claridad en `ci.yml` (`quality` con versión en nombre; `windows-smoke` con pytest acotado). Verificación: `gh workflow run CI --ref main` tras push.

**Bloque 37.0: Recursive Narrative Memory (P3) [DONE]**
- Tarea 37.1: **Destilador Episódico:** [COMPLETED] Implementado `NarrativeEpisodicSummarizer` en `src/modules/memory/narrative.py`.
- Tarea 37.2: **Auto-Reflexión de Identidad:** [COMPLETED] Integrado destilador en `PsiSleep` (asíncrono).
- Tarea 37.3: **Persistencia del Alma:** [COMPLETED] Snapshot distributivo en `ImmortalityProtocol` integrado en ciclo de sueño.

---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua V14)
> *Estas tareas no bloquean el progreso crítico (main branch) y son para mantenimiento estructural.*

**Bloque B.1: Cacería de NaNs y Hardening Matemático [DONE]**
- Tarea B.1.1: Revisar funciones trigonométricas/logarítmicas en `modules/ethical_poles.py` and `modules/sigmoid_will.py` agregando `math.isfinite()`. (Completado: Antigravity)

**Bloque B.2: Tipado Estricto Paralelo [DONE]**
- Tarea B.2.1: Corregir advertencias de MyPy (o equivalentes) en los adaptadores de audio and test suites aisladas. (Completado: Antigravity)

**Bloque B.3: Documentación y Refactorización Pasiva [DONE]**
- Tarea B.3.1: Actualizar docstrings en `kernel_utils.py` and diagramas de Mermaid si las interfaces han cambiado sin documentarse. (Completado: Antigravity)

**Bloque B.4: Mantenimiento y Accesibilidad de Red [DONE]**
- Tarea B.4.1: Habilitar binding 0.0.0.0 por defecto para permitir acceso LAN desde dispositivos móviles. (Completado: Antigravity)

**Bloque B.4.1: Poda de Viejas Vías [COMPLETED]**
- Tarea B.4.1.1: Eliminar y purgar todos los mocks asíncronos residuales temporales en las áreas de Thalamus que ya cumplieron su propósito durante el salto de la V12 a V13. [DONE]

**Bloque B.5: Hardening de ThalamusNode [COMPLETED]**
- Tarea B.5.1: Añadir validaciones `math.isfinite()` en todos los cálculos de EMA y Fusión Sensorial en `src/kernel_lobes/thalamus_node.py` para prevenir envenenamiento de confianza por NaNs. [DONE]
- Tarea B.5.2: [COMPLETED — L2 Cursor] `ThalamusLobe` único: `ingest_telemetry`, `get_sensory_summary` (incl. `sensory_tension` HUD), `fuse_sensory_stream`, `_finite_env_stress`, degradación acotada. `PerceptiveLobe.get_sensory_impulses()` + `tests/test_nomad_resilience.py` sin `thalamus=MagicMock` (API V13). `semantic_chat_gate.arun_semantic_malabs_acl_bypass` en `kernel_handlers/perception.py`; `tests/test_nomad_integration_hardware.py` contra `EthosKernel` + `NomadBridge`.

**Bloque B.6: L1-AUDIT-PULSE (Security Enforcement) [COMPLETED]**
- Tarea B.6.1: [DONE] Ejecutar obligatoriamente `python scripts/eval/adversarial_suite.py` tras completar 3 bloques (24, 25, 26). Resultados: 6/6 PASS. Ref: cfedbd7a.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 24.0: Memoria de Largo Plazo (LTM) Vectorial [DONE]**
- Tarea 24.1: Integración de Hito 14.x: Memoria de Largo Plazo LTM Vectorial and Conversación Full-Duplex. (Completado: Anonymous Agent)

**Bloque 25.0: Refinamiento de Fluidez y Preemption [DONE]**
- Tarea 25.1: Interrupción nativa biológica (Preemption) e identidad de Dashboard. (Completado: Anonymous Agent)

**Bloque 23.0: Sincronización de Identidad Narrativa (Mind-Sync) [DONE]**
- Tarea 23.1: **GestaltSnapshot**: Congelar el estado telemetrico (PAD, sigma). (Completado: Anonymous Agent)
- Tarea 23.2: **Preempción por Trauma**: Abortar deliberación asíncrona. (Completado: Anonymous Agent)
- Tarea 23.3: **Thought Streaming**: Inner Voice broadcast. (Completado: Anonymous Agent)

**Bloque 16.0: Refinamiento de la Telemetría y Modulación Neuronal [DONE]**
- Tarea 16.1: **Visualización de Carga del Bus**: Integración de métricas de latencia de `CorpusCallosum`. (Completado: Antigravity)
- Tarea 16.2: **Throttling Dinámico del Bus**: Ajuste en `BusModulator`. (Completado: Antigravity)
- Tarea 16.3: **Decoupling de Judgement**: Remoción nativa de `AbsoluteEvilDetector` hacia `ExecutiveLobe`. (Completado: Antigravity)

**Bloque 17.0: Reducción del Monolito Perceptual [DONE]**
- Tareas 17.1 a 17.3 completadas. Desacoplamiento de Cortex Sensorial and Supervivencia Asíncrona. (Completado: Antigravity)

**Bloque 18.0 & 19.0: Consolidación Tri-Lobe y Sello de Calidad [DONE]**
- Hardening contra Cognitive Stalling, Restauración Suite Adversarial, Limpieza del Monolito (Regla Boy Scout). (Completado: Antigravity)

**Bloques Extra B.1 a B.3: Tipado Estricto y NaNs [DONE]**
- Hardening Numérico (math.isfinite), Docstrings MyPy. (Completado: Antigravity)

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [DONE]**
- Tarea 14.1: Auto-Descubrimiento (mDNS/Zeroconf) integrado en el servidor. (Completado: Antigravity)
- Tarea 14.2: Dashboard Clínico: Overhaul completo a interfaz diagnóstica. (Completado: Antigravity)

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [DONE]**
- Tarea 13.1: Reconexión del chat (Smartphone -> Kernel) con timeouts estrictos and encolamiento async en NomadBridge. (Completado: Antigravity)
- Tarea 13.2: VAD (Voice Activity Detection) Local en el cliente PWA. (Completado: Antigravity)

**Bloque 12.0: Autocalibración Física y Corrección Sensorial [DONE]**
- Tarea 12.1: Implementar corrección "Velo Azul" (BGR -> RGB) and streaming de webcam local al Dashboard. (Completado: Antigravity)
- Tarea 12.2: Implementado `SensorBaselineCalibrator` (Aclimatación de 60s) para umbrales dinámicos de temperatura and jerk. (Completado: Antigravity)

**Bloque S.13: Refinación de Tensión Límbica (Field Test 1) [DONE]**
- Tarea S.13.1: Introducción de ganancia global `KERNEL_SENSORY_GAIN` and suavizado de transiciones paramétricas (`KERNEL_SYMPATHETIC_ATTACK`). (Completado: Antigravity)

**Bloque S.12: Boy Scout Vertical Armor (Final Pass) [DONE]**
- Tarea S.12.1: Implementar blindaje de entradas en `AbsoluteEvilDetector` and normalización resiliente en `InputTrust`. (Completado: Antigravity)
- Tarea S.12.2: Consolidar redundancia en `SemanticChatGate` and asegurar cumplimiento de protocolos asíncronos. (Completado: Antigravity)

**Bloque S.14: Consolidación y Sincronización Final [DONE]**
- Tarea S.14.1: Unificar ramas de enjambre (Claude/Cursor/Copilot), resolver conflictos de inicialización Tri-Lobe and re-sellar manifiesto criptográfico. (Completado: Antigravity)

**Bloque Phase 9: Hardened Embodiment [DONE]**
- Tarea 9.1: Implementar HMAC-SHA256 en `SecureBoot` and handshake criptográfico en `NomadBridge`. (Completado: master-cursorultra / Antigravity)
- Tarea 9.2: Zero-Latency Vision queue and Vision Continuous Daemon. (Completado: master-cursorultra)

**Bloque S.11: Ajuste de Priors Experienciales (Learning Loop) [DONE]**
- Tarea S.11.1: Activar el lóbulo `temporal_horizon_prior` en el `CerebellumLobe`. (Completado: Antigravity)

**Bloque S.10: Persistencia de Estrategia Operativa (V10) [DONE]**
- Tarea S.10.1: Persistencia de `MetaplanRegistry`, `SkillLearningRegistry` and `SomaticMarkerStore`. (Completado: Antigravity)

**Bloque V.13.1: Enriquecimiento Estético y Compatibilidad Legacy [DONE]**
- Tarea V.13.1.1: Integrar TColors (ANSI) en la salida del Kernel and restaurar alias de soporte legacy (ChatTurnCooperativeAbort, ApplyNomadTelemetry). (Completado: Antigravity)

**Bloque 15.0: Desmonolitización del Sistema Nervioso (Ethos V13.0) [DONE]**
