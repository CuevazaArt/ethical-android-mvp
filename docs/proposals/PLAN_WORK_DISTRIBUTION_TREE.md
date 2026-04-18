# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el inmenso volumen de trabajo arquitectónico definido para el Ethos Kernel tras la exitosa integración del modelo Tri-lobulado y la evaluación visual-somática en `main`. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**, fusionado ahora con el **Motor de Encanto Multimodal (Charm Engine)** para una interacción persuasiva y segura.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ⚙️ Módulo 0: Estabilización Pragmática y Reducción de Deuda (Nuevo P0/P1)
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Prioridad Absoluta)**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP de LLMs (`httpx` sincrónico dentro del hilo worker) hacia clientes cooperativos asíncronos (`httpx.AsyncClient`). *Estado hub:* verbal Ollama/HTTP JSON ya exponen `acompletion` / `aembedding` asíncronos; transporte MalAbs-embebido en [`semantic_embedding_client.py`](../../src/modules/semantic_embedding_client.py) tiene `ahttp_fetch_ollama_embedding_with_policy` + cancel cooperativo entre reintentos; rutas **sync** (`completion`, `http_fetch_*`) se conservan para hilos y llamadas legacy.
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Implementar la cancelación transparente de tareas de red pendientes cuando el loop asíncrono se venza (`KERNEL_CHAT_TURN_TIMEOUT`), liberando inmediatamente memoria y slots en el Worker Pool. *Estado hub:* [`process_chat_turn_async`](../../src/kernel.py) / [`process_chat_turn_stream`](../../src/kernel.py) enlazan TLS cooperative + [`set_llm_cancel_scope`](../../src/modules/llm_http_cancel.py) en el hilo asyncio; en [`chat_server.py`](../../src/chat_server.py) el WebSocket marca el event de cancelación, luego `aclose` del async generator (`TimeoutError` y `finally`) y después `abandon_chat_turn` (ADR 0002).
  - Tarea 0.1.3: Extraer la `Perception` y la lógica de ruteo ético del objeto `EthicalKernel` gigante hacia handlers aislados que aprovechen el Async I/O en lugar de abusar de `run_in_threadpool`. *Estado hub:* [`chat_turn_policy.py`](../../src/kernel_lobes/chat_turn_policy.py) — (1) `chat_turn_is_heavy` + `prioritized_principles_for_context` + buffer; (2) `default_chat_light_actions` + `generic_chat_actions_for_suggested_context` (catálogo `CandidateAction`); (3) [`kernel_utils.py`](../../src/kernel_utils.py) `kernel_decision_event_payload` (bus eventos); (4) `candidate_actions_for_chat_turn` (ruteo heavy → genérico / light); (5) `ethical_context_for_chat_turn` (``everyday`` vs `suggested_context` para el pipeline); (6) [`kernel_utils.py`](../../src/kernel_utils.py) `enrich_chat_turn_signals_for_bayesian` (I3/I5), `coercion_uncertainty_from_perception`, plus merge/apply helpers. [`kernel.py`](../../src/kernel.py) delega; [`tests/test_chat_turn_policy.py`](../../tests/test_chat_turn_policy.py) + [`tests/test_kernel_utils.py`](../../tests/test_kernel_utils.py).
- **Bloque 0.2: Escalabilidad del Chat Server**
  - Tarea 0.2.1: Rediseñar la capa WebSocket del servidor (`chat_server.py`) para manejar concurrencia pura sin bloquear el event loop principal, permitiendo streaming asíncrono. *Estado parcial (abril 2026):* [`RealTimeBridge`](../../src/real_time_bridge.py) aplica tope a ``KERNEL_CHAT_THREADPOOL_WORKERS`` (``CHAT_THREADPOOL_MAX_WORKERS``) para desalentar pools anómalos; I5 en [`kernel_utils.py`](../../src/kernel_utils.py) restringe ``KERNEL_TEMPORAL_REFERENCE_ETA_S`` y tolera señales no numéricas/ETA no finitos; límite de mensaje entrante WebSocket ``KERNEL_CHAT_WS_MAX_MESSAGE_BYTES`` en [`chat_server.py`](../../src/chat_server.py). **Solicitud L1 (Antigravity):** decisión de alcance/ADR — [`PROPOSAL_L1_REQUEST_CHAT_SERVER_0.2.1_FOLLOWUP.md`](./PROPOSAL_L1_REQUEST_CHAT_SERVER_0.2.1_FOLLOWUP.md).
- **Bloque 0.3: Mantenimiento Histórico (Legacy Modules) [DONE]**
  - Tarea 0.3.1: Los módulos de la integración fundacional 1 al 6 (Mock DAO, Safety Interlock, UchiSoto, Swarm Logic) han sido consolidados y se consideran estables en producción local.

### 🧠 Módulo C: Profundidad Cognitiva y Recompensas RLHF
*Responsabilidad: Nivel 2 (Team Claude)*
*Dependencias: Modelo RLHF existente y Motor Bayesiano.*

> Cola operativa y huecos de cableado (abril 2026): [`PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md`](PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md).

- **Bloque C.1: Fusión BMA (Bayesian Mixture Averaging) y Recompensas RLHF**
  - Tarea C.1.1: Conectar los *outputs* asíncronos del `rlhf_reward_model.py` directamente como *Priors* moduladores dentro de `bayesian_engine.py` en tiempo real. *Estado hub:* con ``KERNEL_RLHF_MODULATE_BAYESIAN=1``, MalAbs ``rlhf_features`` → ``maybe_modulate_bayesian_from_malabs`` → ``apply_rlhf_modulation`` tras la evaluación MalAbs en chat y `aprocess_natural`; modelo opcional en ``artifacts/rlhf/reward_model.json``; ver [`PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md`](PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md).
  - Tarea C.1.2: Validar el arrastre de métricas RLHF sobre las decisiones de los polos multipolares en el estadio 3 del Kernel.
- **Bloque C.2: Gobernanza Real en Runtime**
  - Tarea C.2.1: Implementar handlers para que cualquier voto exitoso en el `MultiRealmGovernor` altere en vivo (hot-reload) los umbrales de Absoluto Mal (`semantic_chat_gate.py`) sin necesidad de reiniciar el proceso del kernel.

### 🦾 Módulo S: Encarnación Activa y Hardware Bridge (Nomad PC/Mobile)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Arquitectura Somática e Inferencia de Visión estabilizada.*

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video and audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona. *Estado parcial (abril 2026):* [`nomad_bridge.py`](../../src/modules/nomad_bridge.py) — colas acotadas, límites decoded base64 + telemetría; ``KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES``; contadores ``rejections`` / ``queue_evictions`` en ``nomad_bridge_queue_stats_v3``; con ``KERNEL_METRICS=1``, mismos eventos en Prometheus (`ethos_kernel_nomad_bridge_*`). [`tests/test_nomad_bridge_stream.py`](../../tests/test_nomad_bridge_stream.py), [`test_observability_metrics.py`](../../tests/test_observability_metrics.py).
- **Bloque S.2: Calibración Termo-Visual Continua**
  - Tarea S.2.1: Refinar las interrupciones del `VitalityAssessment` (ej. alertas de calor del dispositivo) utilizando la telemetría real transmitida por el *Nomad Bridge*.

### 🧹 Módulo 8: Higiene, Mantenimiento y Deuda Menor
*Responsabilidad: Nivel 2 (Team Copilot / Contribuidores Libres)*
*Nota:* El registro exhaustivo de estas tareas debe consolidarse permanentemente en el `MINOR_CONTRIBUTIONS_BACKLOG.md`.

- **Bloque 8.1: Calidad y DX (Developer Experience)**
  - Tarea 8.1.1: Linter continuo y auditoría de `docstrings` / `type hints` a lo largo de las divisiones de `kernel.py`.
  - Tarea 8.1.2: Refactorización y embellecimiento de las salidas ANSI de terminal para facilitar el modo de depuración de operadores locales.
  - Tarea 8.1.3: Extender mocks para *input_trust* (ej. Caracteres homoglyphs cirílicos para evadir la puerta de Absoluto Mal).

---

### ⚪ Módulo 9: Nomadismo Perceptivo (Streaming Aferente Continuo)
*Responsabilidad: Nivel 1 (Antigravity - Planificación) / Nivel 2 (Ejecución)*
*Objetivo: Migrar desde un modelo puramente conversacional ("Chat-Turn") hacia un stream sensorial continuo en background, permitiendo al androide percibir el entorno de forma pasiva y detonar la proactividad del MotivationEngine.*

- **Bloque 9.1: Daemon de Visión Continua (CNN/Webcam)**
  - *Responsabilidad:* **Team Cursor**
  - Tarea: Modificar `VisionInferenceEngine` para crear un stream en background que clasifique "entidades" (humanos, armas, obstáculos) a 5Hz utilizando OpenCV/Ollama Vision ligero.
  - Vínculo: Alimentará asíncronamente el nuevo `SensoryBuffer` del `PerceptiveLobe`.
- **Bloque 9.2: Acumulación de Tensión Límbica Estática**
  - *Responsabilidad:* **Claude**
  - Tarea: Evolucionar el `BayesianEngine`. Si el Lóbulo Perceptivo dicta que un estímulo peligroso permanece en la vista durante +5 segundos, el Lóbulo Límbico debe escalar automáticamente la *Tensión Social* sin esperar una interacción de texto.
- **Bloque 9.3: Refactorización Asíncrona Total de Eferencia**
  - *Responsabilidad:* **Team Copilot**
  - Tarea: Eliminar los cuellos de botella síncronos en `ExecutiveLobe` (`llm.communicate`) y `NarrativeMemory` (`requests` a Ollama). Migrar `http_fetch_ollama_embedding` a `httpx.AsyncClient`.
- **Bloque 9.4: Monitor de Stream Inter-Lóbulos**
  - *Responsabilidad:* **Team VisualStudio**
  - Tarea: Desarrollar pruebas que inyecten un mock contínuo en el Lóbulo Perceptivo simulando estrés de entorno, midiendo si el Lóbulo Ejecutivo logra interrumpir el stream para alertar (E-Stop).

---

### 🟢 Módulo 10: Motor de Encanto Resiliente (MER V2)
*Responsabilidad: Nivel 1 (Antigravity - Planificación y Orquestación) / Nivel 2 (Ejecución Escuadrones)*
*Objetivo: Construir la infraestructura que evite transiciones sociopáticas y asegure latencia instintiva frente al ruido (Lectura labial VVAD + Smoothing Emocional).*

- **Bloque 10.1: Fusión Sensorial (VVAD + VAD) y Tálamo**
  - *Responsabilidad:* **Team Cursor + Team Copilot**
  - Tarea: Crear `src/kernel_lobes/thalamus_node.py`. Acoplar OpenCV/LipReading de bajo costo computacional con el VAD existente.
  - Prioridad: **Alta**. Proveer estabilidad al stream perceptivo.
- **Bloque 10.2: Tribunal Ético Edge (Doble Capa Local)**
  - *Responsabilidad:* **Antigravity (L1)**
  - Tarea: Mover `AbsoluteEvilDetector` directamente al Edge (Nivel 1 <50ms) e instanciar el Lóbulo Límbico Contextual como Nivel 2 (Asíncrono, también local por carencia 6G).
  - Prioridad: **Máxima**. Asegurar que la censura estricta no estrangule la conversacion fluida.
- **Bloque 10.3: Amortiguación Afectiva (Ganglios Basales)**
  - *Responsabilidad:* **Claude**
  - Tarea: Construir `src/modules/basal_ganglia.py` aplicando Filtros EMA (Exponential Moving Average) sobre las variables `charm_warmth` y `charm_mystery` del `UserModelTracker`. Las transiciones deben durar 3-5 turnos. *Estado hub:* módulo existe; **Cursor** integró EMA en [`charm_engine.py`](../../src/modules/charm_engine.py) bajo `KERNEL_BASAL_GANGLIA_SMOOTHING`; persistencia en `UserModelTracker` y tunear τ en backlog.
- **Bloque 10.4: Predicción Local y Prefetching**
  - *Responsabilidad:* **Team Copilot**
  - Tarea: Inyectar micro-LLM (ej. Llama-3-2B) o precompilador probabilístico para inferir turnos y lanzar asentimientos rápidos en <300ms antes que el API principal complete.
  - *Estado hub:* [`turn_prefetcher.py`](../../src/modules/turn_prefetcher.py) (heurísticas + `OLLAMA_PREFETCH_MODEL` / `OLLAMA_BASE_URL`); [`tests/test_turn_prefetcher.py`](../../tests/test_turn_prefetcher.py).
- **Bloque 10.5: Contrato capa presentación vs núcleo ético (MER ADR)**
  - *Responsabilidad:* **Team Cursor** (normativo + trazabilidad)
  - Estado hub: ADR [`0018`](../adr/0018-presentation-tier-vs-ethical-core.md); tests `tests/test_mer_presentation_contract.py`; `PreloadedBuffer.get_snapshot` alimenta el soporte local sin tocar MalAbs.

## 🚀 Flujo de Sincronización Recomendado

1. **Semana Actual:** Antigravity (N1) se encarga transversalmente de desmonolitizar `kernel.py` y actualizar las dependencias de concurrencia. Claude y Cursor toman sus ramas (`master-claude`, `master-Cursor`) and abordan C.1 y S.1 respectivamente.
2. **Semana Siguiente:** Sincronización de progresos a `master-antigravity`. Antigravity evalúa el impacto del async I/O en la latencia global del kernel.
3. **Validación N0:** Integración unificada a `main` tras validaciones somáticas. 
