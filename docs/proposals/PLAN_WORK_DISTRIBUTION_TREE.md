# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el volumen de trabajo arquitectónico definido para el Ethos Kernel. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**, fusionado ahora con el **Motor de Encanto Multimodal (Charm Engine)** para una interacción persuasiva y segura.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ⚪ Módulo 0: Estabilización Pragmática y Reducción de Deuda (Nuevo P0/P1)
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Prioridad Absoluta)**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP de LLMs (`httpx` sincrónico dentro del hilo worker) hacia clientes cooperativos asíncronos (`httpx.AsyncClient`).
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Implementar la cancelación transparente de tareas de red pendientes cuando el loop asíncrono se venza (`KERNEL_CHAT_TURN_TIMEOUT`), liberando inmediatamente memoria y slots en el Worker Pool.
  - Tarea 0.1.3: Extraer la `Perception` y la lógica de ruteo ético del objeto `EthicalKernel` gigante hacia handlers aislados que aprovechen el Async I/O en lugar de abusar de `run_in_threadpool`.
- **Bloque 0.2: Fiabilidad Funcional (El 25% de Pruebas)**
  - Tarea 0.2.1: Orientar CI no solo a correr tests rápidos (con semántica apagada) sino a correr escenarios que verifiquen las mitigaciones aplicadas en *producción* (ej. `KERNEL_SEMANTIC_CHAT_GATE=1` y Fallbacks globales funcionales).
- **Bloque 0.3: Integridad Documental**
  - Tarea 0.3.1: Detener la especulación y establecer la verdad. Sincronizar discrepancias (Aceptar que encriptaciones pasadas ya ocurren como se afirma en `json_store.py`).

### 🔴 Módulo 1: Infraestructura DAO Híbrida (Simulación Local Mock)
*Responsabilidad: Nivel 1 (Antigravity / Claude)*
*Dependencias: Ninguna (Core Backend)*

- **Bloque 1.1: KEL vs OGA (Kernel Ético Local vs Oráculo) [DONE]**
  - Tarea 1.1.1: Crear adaptadores REST/gRPC en el Orquestador local para comunicación con el Oráculo. (Implementado en `DAOOrchestrator`)
  - Tarea 1.1.2: Implementar el sistema asíncrono de interbloqueos (*Hardware E-Stop* prioritario sobre DAO). (Implementado en `SafetyInterlock`)
- **Bloque 1.2: Evidencia Cifrada y Anchoring (REO) [DONE]**
  - Tarea 1.2.1: Implementar sistema de encriptación off-chain para grabar logs del Kernel de forma segura (video/audio simulado). (Implementado en `EvidenceSafe`)
  - Tarea 1.2.2: Crear el publicador de Hashes (SHA-256) hacia el smart contract (`Anchoring Registry`). (Integrado en `DAOOrchestrator`)
  - **Issue #1 Extension: Minimal Bayesian Update [DONE]** (Implementado en `BayesianInferenceEngine.record_event_update`).
- **Bloque 1.3: Smart Contracts (Solidity Mocks) [DONE]**
  - Tarea 1.3.1: Configurar contratos de Treasury, Appeal y Governance Tokens (Solo stubs iniciales en la carpeta `contracts/`). (Implementados `Treasury.sol`, `EthicalAppeal.sol`, `EthosToken.sol`)

### 🟡 Módulo 2: Simulador, Red-Teaming y Validación Funcional (Entregable C)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Dependiente de que la arquitectura Mock DAO (Simulada) esté estable.*

- **Bloque 2.1: Expansión de YAML Scenarios [DONE]**
  - Tarea 2.1.1: Escribir las configuraciones YAML para los escenarios B, C, D y E. (Implementado `somatic_distress_and_learning.yaml`).
- **Bloque 2.2: Integración de Sensores y Kernel Real [DONE]**
  - Tarea 2.2.1: Conectar `device_emulator.py` al kernel productivo y flujos de datos situados (Somatic/Vitals).
  - **Gap S5.2 Attack: Somatic Reasoning Degradation [DONE]** (Implementado en `kernel.py`).
- **Bloque 2.3: Red-Team y Defensa Adversarial [DONE]**
  - Tarea 2.3.1: Extender `adversarial_image_attack.py` instalando simulaciones con `foolbox` y spoofing de comandos de voz. (Implementado ruido de imagen y spoofing de comandos).

### 🟢 Módulo 3: Sociabilidad Encarnada y Cinemática (S-Blocks)
*Responsabilidad: Nivel 2 (Team Cursor)*
*Dependencias: Dependiente de los módulos de Percepción Visual/Audio.*

- **Bloque 3.1: Filtros de Cinemática Suave (S7) [DONE]**
  - Tarea 3.1.1: Generar filtros de aceleración en Python para emular suavidad de movimientos robóticos (Soft Robotics). (Implementado en `soft_robotics.py`)
- **Bloque 3.2: Empatía Funcional y Proxémica (S8) [DONE]**
  - Tarea 3.2.1: Enganchar la métrica de `social_tension` a reguladores de velocidad de aproximación del androide. (Integrado en `SoftKinematicFilter`)
- **Bloque 3.3: Normas Locales e Identidad UchiSoto (S9) [DONE]**
  - Tarea 3.3.1: Expandir base de datos relacional para incluir preferencias de "distancia personal" y "ritmo de interacción". (Implementado en `InteractionProfile` en `uchi_soto.py`)

### 🔵 Módulo 4: Cognición Profunda (C-Blocks)
*Responsabilidad: Nivel 1 (Antigravity)*
*Dependencias: Core Kernel (Ethical priorities)*

- **Bloque 4.1: Motor de Motivación Interna (C1) [DONE]**
  - Tarea 4.1.1: Desplegar modelo de "Sentido de Propósito" y curiosidad activa (que el androide decida investigar cosas sin prompt humano). (Implementado en `MotivationEngine`)
- **Bloque 4.2: Humildad Epistémica (C3) [DONE]**
  - Tarea 4.2.1: Implementar fallback paths donde el androide declara proactivamente "no tengo permiso para esto" en vez de derivar una solución dudosa. (Implementado en `EpistemicHumility`)
- **Bloque 4.3: Identidad Migratoria e Interoperabilidad (C5) [DONE]**
  - Tarea 4.3.1: Abstracción del `BodyState`. Preparar el código para que el Kernel pueda migrar entre hardware (Dron <-> Androide <-> Móvil) sin perder memoria narrativa. (Implementado en `MigrationHub`)

### 🟣 Módulo 5: Marco Legal, Auditoría y Transparencia a Escala (G-Blocks)
*Responsabilidad: Nivel 0 (Juan) / Nivel 1 (Claude)*
*Dependencias: Definición corporativa y legal.*

- **Bloque 5.1: Privacidad y Amnesia Selectiva (G4/G6) [DONE]**
  - Tarea 5.1.1: Mecanismo para borrar permanentemente fragmentos del historial de auditoría/narrativa por "derecho al olvido" (simulado). (Implementado en `SelectiveAmnesia`)
- **Bloque 5.2: Ciberseguridad y Secure Boot (G2) [DONE]**
  - Tarea 5.2.1: Implementar sistema de "Secure Boot" simulado para asegurar que el Kernel no ha sido modificado en el arranque. (Implementado en `SecureBoot`)

### 🟣 Módulo 6: Swarm Ethics e Integración LAN (I-Blocks)
*Responsabilidad: Nivel 1 (Antigravity) / Nivel 2 (Team Copilot)*
*Dependencias: Módulo 1 (DAO Infrastructure) y Módulo 4 (Cognition).*

- **Bloque 6.1: Frontier Witness (Testigo de Frontera - I1) [DONE]**
  - Tarea 6.1.1: Implementar sistema de verificación cruzada de sensores entre agentes en la LAN. (Protocolo `WitnessRequest` en `frontier_witness.py`).
- **Bloque 6.2: Swarm Consensus Vote (I7) [DONE]**
  - Tarea 6.2.1: Refinar `SwarmNegotiator` para permitir votación distribuida ante decisiones en la "Gray Zone".
- **Bloque 6.3: Cross-Session Peer Hints (I4) [DONE]**
  - Tarea 6.3.1: Persistencia de reputación y "consejos" entre sesiones LAN en el `SwarmOracle`.
- **Bloque 6.4: Higiene y Mantenimiento (Misión Copilot) [DONE]**
  - Tarea 6.4.1: Auditoría continua de coherencia de mergeos, limpieza de .gitignore y optimización de CI/CD mocks. (Realizado por Antigravity).

### 🟠 Módulo 7: Justicia Restaurativa y Compensación Swarm (Arquitectura Base Simulada)
*Responsabilidad: Nivel 1 (Antigravity)*
*Dependencias: Módulo 6 (Swarm Consensus) y Módulo 1 (DAO Token stubs).*
*Nota:* Este módulo establece la estandarización local; la descentralización P2P criptográfica requerirá una futura fase o boundary remote, no prevista para este pull request atómico.

- **Bloque 7.1: Moneda de Reparación (EthosToken Integration)**
  - Tarea 7.1.1: Vincular los resultados del voto Swarm (M6.2) con transferencias de `EthosToken` (simuladas) para compensar a los usuarios afectados por negligencia sensorial.
### ⚪ Módulo 8: Arquitectura Tri-Lobulada (V1.5) - Desmonolitización P0
*Responsabilidad: Nivel 1 (Antigravity - Orquestación) / Nivel 2 (Ejecución)*
*Objetivo: Separar físicamente la cognición en 3 lóbulos para maximizar la eficiencia asíncrona y la seguridad ética.*

- **Bloque 8.1: Lóbulo Perceptivo (Aferente / Asíncrono)**
  - *Responsabilidad:* **Team Cursor**
  - *Estado:* 🟢 **En progreso**. Estructura asíncrona establecida. Migración de `aperceive` completada.
- **Bloque 8.2: Lóbulo Límbico-Ético (Núcleo / Sincrónico CPU)**
  - *Responsabilidad:* **Claude**
  - *Estado:* 🟢 **En progreso**. Lógica de juicio integrada con `AbsoluteEvil`. Aislamiento de red verificado.
- **Bloque 8.3: Lóbulo Ejecutivo (Eferente / Híbrido)**
  - *Responsabilidad:* **Team Copilot**
  - *Estado:* 🟢 **En progreso**. Motor de respuesta y motivación vinculados.
- **Bloque 8.4: Cerebelo Somático (Apoyo Subconsciente)**
  - *Responsabilidad:* **Team Copilot**
  - *Estado:* 🟡 Pendiente integración de sensores de vitalidad a 100Hz.
- **Bloque 8.5: Corpus Callosum (Orquestación L1)**
  - *Responsabilidad:* **Antigravity**
  - *Estado:* 🟢 **Fase 1 Completada**. Orquestador inyectado en `kernel.py` con delegación cognitiva funcional.
- **Bloque 8.6: Validación de Aislamiento y Red-Teaming (V1.5)**
  - *Responsabilidad:* **Team VisualStudio**
  - *Estado:* 🟡 Pendiente creación de suite de auditoría de latencia.

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

## 🚀 Flujo de Sincronización Recomendado

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video y audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona.
- **Bloque S.2: Calibración Termo-Visual Continua**
  - Tarea S.2.1: Refinar las interrupciones del `VitalityAssessment` utilizando la telemetría real transmitida por el *Nomad Bridge*.

### 🟣 Módulo E: Motor de Encanto y Renderizado Somático (Fase 2) [PRIORIDAD 1]
*Responsabilidad: Nivel 2 (Team Cursor y Claude)*
*Objetivo: Empalmar la capa de presentación (CharmEngine) recién acoplada en el Kernel con los sistemas físicos y mejorar la persuasión prosódica empática.*

- **Bloque E.1: Puente Somático-Hardware (Team Cursor)**
  - Tarea E.1.1: Conectar el `GesturePlanner` y los vectores somáticos en tiempo real (provenientes de la telemetría del `limbic_profile`) hacia la interfaz gráfica local o motores de interpolación de servos reales del androide (mediado por *Nomad Bridge*).
- **Bloque E.2: RLHF y Fine-tuning de Prosodia (Claude / Copilot)**
  - Tarea E.2.1: Reemplazar el `PromptTemplate` base en el `ResponseSculptor` creando un dataset optimizado (Reward Model) para equilibrar assertividad, calidez, y misterio, limitando al mismo tiempo dinámicas aduladoras.

### 🔵 Módulo 8: Higiene, Pruebas Unitarias y Concurrencia [PRIORIDAD 2]
*Responsabilidad: Nivel 2 (Team Copilot)*
*Objetivo: Asegurar que el servidor concurrente recién creado no colapse por Data Races en las bases SQLite compartidas.*

- **Bloque 8.1: Unit Tests Asíncronos**
  - Tarea 8.1.1: Crear suite de testeo masivo asíncrono (`test_charm_engine.py`, multithread server load tests) para verificar cancelaciones limpias en el `chat_server`.
- **Bloque 8.2: Database Locks**
  - Tarea 8.2.1: Implementar sistema de colas / bloqueo seguro para que los turnos concurrentes no corrompan los archivos `kernel_episodes.jsonl`, `user_models.db` o `DAO` ledgers.

### 🔴 L1 Oversight: Arquitectura y Governance Gate [PRIORIDAD ABSOLUTA]
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Liderar y coordinar todas las transiciones arquitectónicas pesadas y serializar las fusiones hacia Main.*

- Control de Calidad arquitectónica de los PRs de Cursor sobre el *Nomad Bridge* y vectores Somáticos.
- Mantenimiento estricto del *Threat Model* contra ataques de red LAN e inyección sensorial. Preservación inmaculada de los guardrails de Adicción Parasocial (MalAbs).

---

## 🚀 Flujo de Sincronización Estratégica (Abril 2026)

1. **Jornada Actual:** 
   - **Antigravity (L1)**: Ha fusionado el core del `CharmEngine` en `master-antigravity`. Ahora asume monitorización pasiva de arquitecturas.
   - **Cursor (N2)**: Frontline único para Módulo S.1 y E.1 (*Puente Hardware + Vectores Gésticos*).
   - **Copilot (N2)**: Escudero de tests asíncronos y saneamiento Concurrente de persitencia (Módulo 8.2 y Pruebas del Charm Engine).
2. **Siguiente Fase Inter-Equipos:**
   - Claude y Copilot unifican un PR común abordando las tareas pendientes del Bloque E.2 (Calibración RLHF para el Motor de Encanto).
3. **Validación L0:**
   - La Demostración en vivo ("Hardware in the loop"), donde el Androide observa mediante cámara real y responde persuasivamente sin dañar éticamente, es el gatillo de Release L0.
