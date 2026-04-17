# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el inmenso volumen de trabajo arquitectónico definido para el Ethos Kernel tras la exitosa integración del modelo Tri-lobulado y la evaluación visual-somática en `main`. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Abril 2026 - Aprobación L0)**:
> 1. **Balance de Esfuerzo:** Reducir la creación y mantenimiento exhaustivo de tests al **25%** del esfuerzo total. Concentrar el **75%** del tiempo en la **resolución práctica de problemas, eliminación de vulnerabilidades y funcionalidades concretas**.
> 2. **Erradicación de Deuda Técnica Monolítica:** Prioridad absoluta a la desmonolitización de `kernel.py` para resolver cuellos de botella asíncronos y agotamiento de worker pools, migrando las tareas de red a flujos cooperativos nativos.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ⚪ Módulo 0: Estabilización Pragmática y Reducción de Deuda (Nuevo P0/P1)
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` [DONE]**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP de LLMs (`httpx` sincrónico dentro del hilo worker) hacia clientes cooperativos asíncronos (`httpx.AsyncClient`). [DONE]
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Cancelación transparente de tareas de red pendientes cuando el loop asíncrono se venza (`KERNEL_CHAT_TURN_TIMEOUT`). [DONE]
  - Tarea 0.1.3: **Desmonolitización Total (Lóbulos):** Extraer Stages 0-5 (Percepción, Ética, Ejecutivo, Cerebelo, Memoria) del objeto gigante `EthicalKernel` hacia handlers aislados. [DONE]
- **Bloque 0.2: Fiabilidad Funcional y Escalabilidad**
  - Tarea 0.2.1: Rediseñar la capa WebSocket del servidor (`chat_server.py`) para manejar concurrencia pura sin bloquear el event loop principal, permitiendo streaming asíncrono.
  - Tarea 0.2.2: Orientar CI no solo a correr tests rápidos (con semántica apagada) sino a correr escenarios que verifiquen las mitigaciones aplicadas en *producción* (ej. `KERNEL_SEMANTIC_CHAT_GATE=1` y Fallbacks globales funcionales).
- **Bloque 0.3: Mantenimiento Histórico y Documental [DONE]**
  - Tarea 0.3.1: Detener la especulación y establecer la verdad. Sincronizar discrepancias (Aceptar que encriptaciones pasadas ya ocurren como se afirma en `json_store.py`). [DONE]
  - Tarea 0.3.2: Consolidación de módulos de integración fundacional 1 al 6. [DONE]

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

### 🔵 Módulo 4: [REASIGNADO Y CONSOLIDADO EN MODULO 0 Y C]

### 🧠 Módulo C: Profundidad Cognitiva y Recompensas RLHF
*Responsabilidad Actual: Nivel 1 (Antigravity) & Nivel 2 (Team Cursor)*
*Status:* Claude está en reposo hasta recuperación. Transferencia de misiones a Antigravity y Cursor.

- **Bloque C.1: Fusión BMA (Bayesian Mixture Averaging) y Recompensas RLHF**
  - Tarea C.1.1: Conectar los *outputs* asíncronos del `rlhf_reward_model.py` directamente como *Priors* moduladores dentro de `bayesian_engine.py` en tiempo real. **[DONE por Antigravity]**
  - Tarea C.1.2: Validar el arrastre de métricas RLHF sobre las decisiones de los polos multipolares en el estadio 3 del Kernel. *(Asignado a: Cursor)*
- **Bloque C.2: Gobernanza Real en Runtime**
  - Tarea C.2.1: Implementar handlers para que cualquier voto exitoso en el `MultiRealmGovernor` altere en vivo (hot-reload) los umbrales de Absoluto Mal (`semantic_chat_gate.py`) sin necesidad de reiniciar el proceso del kernel. *(Asignado a: Antigravity)*

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
- **Bloque 7.2: Difusión de Reputación Negativa (Slashing)**
  - Tarea 7.2.1: Implementar lógica para degradar la reputación de un nodo en el `SwarmOracle` central si sus testigos son desmentidos por la mayoría de la red.

---

## 🚀 Flujo de Sincronización Recomendado (Actualizado con Disponibilidad)

1. **Jornada Actual:** 
   - **Antigravity (N1)**: Mergear trabajo asíncrono y RLHF a `main`. Empezar Módulo C.2 (Gobernanza Runtime) y Módulo 7 (Justicia Restaurativa).
   - **Cursor (N2)**: Tomar y continuar pruebas sobre C.1.2 BMA arrastres, y arrancar Módulo S (Nomad SmartPhone LAN Bridge).
   - **Copilot (N2)**: Mantener prioridades de DX y deuda en Módulo 8 (Linters en Lóbulos, Observabilidad ANSI y Defensas Homoglyphs).
2. **Próxima Ventana de Sincronización:**
   - Todos los N2 inyectan PRs a los master-branches. Antigravity fusiona usando `Squash & Merge` a `main` resolviendo conflictos de API.
3. **Validación N0:**
   - Lanzamiento de *Release Tag Oficial* con el Chat Server Asíncrono escalable antes de expandir redes de swarm WAN.
