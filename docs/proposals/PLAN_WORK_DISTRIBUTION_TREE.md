# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el inmenso volumen de trabajo arquitectónico definido para el Ethos Kernel tras la exitosa integración del modelo Tri-lobulado y la evaluación visual-somática en `main`. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Abril 2026 - Aprobación L0)**:
> 1. **Balance de Esfuerzo:** Reducir la creación y mantenimiento exhaustivo de tests al **25%** del esfuerzo total. Concentrar el **75%** del tiempo en la **resolución práctica de problemas, eliminación de vulnerabilidades y funcionalidades concretas**.
> 2. **Erradicación de Deuda Técnica Monolítica:** Prioridad absoluta a la desmonolitización de `kernel.py` para resolver cuellos de botella asíncronos y agotamiento de worker pools, migrando las tareas de red a flujos cooperativos nativos.

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
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video y audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona.
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

## 🚀 Flujo de Sincronización Recomendado

1. **Semana Actual:** Antigravity (N1) se encarga transversalmente de desmonolitizar `kernel.py` y actualizar las dependencias de concurrencia. Claude y Cursor toman sus ramas (`master-claude`, `master-Cursor`) y abordan C.1 y S.1 respectivamente.
2. **Semana Siguiente:** Sincronización de progresos a `master-antigravity`. Antigravity evalúa el impacto del async I/O en la latencia global del kernel.
3. **Validación N0:** Integración unificada a `main` tras validaciones somáticas. 
