# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el inmenso volumen de trabajo arquitectónico definido para el Ethos Kernel tras la exitosa integración del modelo Tri-lobulado y la evaluación visual-somática en `main`. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**, fusionado ahora con el **Motor de Encanto Multimodal (Charm Engine)** para una interacción persuasiva y segura.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ⚙️ Módulo 0: Estabilización Pragmática y Reducción de Deuda (Nuevo P0/P1)
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Prioridad Absoluta)**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP de LLMs (`httpx` sincrónico dentro del hilo worker) hacia clientes cooperativos asíncronos (`httpx.AsyncClient`).
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Implementar la cancelación transparente de tareas de red pendientes cuando el loop asíncrono se venza (`KERNEL_CHAT_TURN_TIMEOUT`), liberando inmediatamente memoria y slots en el Worker Pool.
  - Tarea 0.1.3: Extraer la `Perception` y la lógica de ruteo ético del objeto `EthicalKernel` gigante hacia handlers aislados que aprovechen el Async I/O en lugar de abusar de `run_in_threadpool`.
- **Bloque 0.2: Escalabilidad del Chat Server**
  - Tarea 0.2.1: Rediseñar la capa WebSocket del servidor (`chat_server.py`) para manejar concurrencia pura sin bloquear el event loop principal, permitiendo streaming asíncrono.
- **Bloque 0.3: Mantenimiento Histórico (Legacy Modules) [DONE]**
  - Tarea 0.3.1: Los módulos de la integración fundacional 1 al 6 (Mock DAO, Safety Interlock, UchiSoto, Swarm Logic) han sido consolidados y se consideran estables en producción local.

### 🧠 Módulo C: Profundidad Cognitiva y Recompensas RLHF
*Responsabilidad: Nivel 2 (Team Claude)*
*Dependencias: Modelo RLHF existente y Motor Bayesiano.*

- **Bloque C.1: Fusión BMA (Bayesian Mixture Averaging) y Recompensas RLHF**
  - Tarea C.1.1: Conectar los *outputs* asíncronos del `rlhf_reward_model.py` directamente como *Priors* moduladores dentro de `bayesian_engine.py` en tiempo real.
  - Tarea C.1.2: Validar el arrastre de métricas RLHF sobre las decisiones de los polos multipolares en el estadio 3 del Kernel.
- **Bloque C.2: Gobernanza Real en Runtime**
  - Tarea C.2.1: Implementar handlers para que cualquier voto exitoso en el `MultiRealmGovernor` altere en vivo (hot-reload) los umbrales de Absoluto Mal (`semantic_chat_gate.py`) sin necesidad de reiniciar el proceso del kernel.

### 🦾 Módulo S: Encarnación Activa y Hardware Bridge (Nomad PC/Mobile)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Arquitectura Somática e Inferencia de Visión estabilizada.*

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video and audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona.
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
  - Tarea: Construir `src/modules/basal_ganglia.py` aplicando Filtros EMA (Exponential Moving Average) sobre las variables `charm_warmth` y `charm_mystery` del `UserModelTracker`. Las transiciones deben durar 3-5 turnos.
- **Bloque 10.4: Predicción Local y Prefetching**
  - *Responsabilidad:* **Team Copilot**
  - Tarea: Inyectar micro-LLM (ej. Llama-3-2B) o precompilador probabilístico para inferir turnos y lanzar asentimientos rápidos en <300ms antes que el API principal complete.

---

### ♾️ Módulo 11: El Bucle Ouroboros (Chat AGI y Radares)
*Responsabilidad: Nivel 1 (Antigravity) & Nivel 2 (Team Claude)*
*Objetivo: Cerrar el bucle aferente-eferente. El Kernel no solo debe percibir el mundo (Fase 10), sino hablarle de vuelta al smartphone y proyectar sus inferencias morales en un Dashboard local (L0) real.*

- **Bloque 11.1: Tránsito Audio-to-Audio (STT + TTS)**
  - *Responsabilidad:* **Team Claude**
  - Tarea: Consumir la `audio_queue` asíncrona del puente, pasar a Whisper y detonar el Lóbulo Ejecutivo. Devolver voz síncroizada a la PWA.
- **Bloque 11.2: Ampliación del Dashboard de Operador (L0)**
  - *Responsabilidad:* **Antigravity**
  - Tarea: Acoplar Radar de Encanto (Charm Engine Vector) y Terminal de Texto interactiva al Dashboard.

## 🚀 Flujo de Sincronización Recomendado

1. **Semana Actual:** Antigravity (N1) se encarga de cimentar el Ouroboros (Módulo 11). Claude aborda 11.1 en su rama para STT/Voice.
2. **Semana Siguiente:** Sincronización de progresos a `master-antigravity`.
3. **Validación N0:** Integración unificada a `main` tras validaciones somáticas. 
