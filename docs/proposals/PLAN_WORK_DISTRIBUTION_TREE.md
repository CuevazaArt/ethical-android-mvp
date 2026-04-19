# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel tras la adopción del modelo de trabajo "Swarm" (PnP - Plug-and-Play) en abril de 2026. 

Aquí es donde los escuadrones de ejecución **Rojo (Cursor)**, **Azul (Copilot)** y **Naranja (Claude)** reclaman sus tareas. 
Ningún agente debe saltar a tareas de la cola de otro equipo. 

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Al despertar, revisa tu respectiva sección.
> 2. Toma el primer bloque marcado como `[PENDING]`.
> 3. Muévelo a `[IN_PROGRESS: <Callsign>]` (ej: `[IN_PROGRESS: Rojo-1]`).
> 4. Tras la revisión y commit exitoso a tu rama, márcalo como `[DONE]`.

---

## 🔴 COLA DE EJECUCIÓN ROJO (Cursor Squad)
**Doctrina:** Alta Fricción, Integración Hardware, Refactorización Arquitectónica, Concurrencia y Streaming.

### ⚙️ Módulo 0: Estabilización Pragmática y Reducción de Deuda (P0/P1) [DONE]
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` [DONE]**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP hacia clientes asíncronos (`httpx.AsyncClient`). [DONE]
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Implementar la cancelación transparente de tareas de red. [DONE]
  - Tarea 0.1.3: Extraer la `Perception` hacia handlers aislados (`PerceptiveLobe`). [DONE]
- **Bloque 0.2: Escalabilidad del Chat Server [DONE]**
  - Tarea 0.2.1: Rediseñar la capa WebSocket del servidor para manejar concurrencia pura. [DONE]
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

### ⚪ Módulo 9: Nomadismo Perceptivo (streaming) — visión continua [PENDING]
*Responsabilidad prioritaria Team Cursor en el árbol histórico; coordinar con L1 antes de duplicar pipelines.*

- **Bloque 9.1: Daemon de Visión Continua (CNN/Webcam) [PENDING]**
  - Tarea 9.1.1: Modificar `VisionInferenceEngine` para crear un stream en background que clasifique entidades a ~5Hz con pre-procesamiento asíncrono (ver también cola Rojo / hardware bridge arriba).

---

## 🔵 COLA DE EJECUCIÓN AZUL (Team Copilot)
**Doctrina:** CI/CD Sentinel, Repo Higiene, Pruebas y Deuda Técnica Menor, Boy Scout Paranoico.

- **Bloque 8.1: Linter Continuo y Hardening Vertical [PENDING]**
  - Tarea 8.1.1: Auditar `docstrings` y `type hints` en las divisiones de `src/kernel.py` y `src/kernel_lobes/`. Introducir `try/except` donde fallen por variables nulas. 
- **Bloque 9.3: Refactorización Asíncrona Total de Eferencia [PENDING]**
  - Tarea 9.3.1: Eliminar cuellos de botella síncronos en las llamadas a utilidades de API. Migrar `http_fetch_ollama_embedding` a dependencias puramente `async` con `httpx.AsyncClient`.
- **Bloque 8.2: Hardening de Tests Mocks (Input Trust) [PENDING]**
  - Tarea 8.2.1: Extender mocks para *input_trust* (ej. inyectar simulaciones de ataques homoglyphs cirílicos para evadir la puerta de Absoluto Mal y validar la defensa).

---

## 🟠 COLA DE EJECUCIÓN NARANJA (Team Claude)
**Doctrina:** Matemática Bayesiana Avanzada, Modelado Cognitivo, Identidad Persistente y RLHF.

- **Bloque C.1: Fusión BMA y Recompensas RLHF [PENDING]**
  - Tarea C.1.1: Conectar matemáticamente los *outputs* asíncronos del `rlhf_reward_model.py` como *Priors* moduladores fuertes dentro de `src/modules/bayesian_engine.py`.
- **Bloque 9.2: Acumulación de Tensión Límbica Estática [PENDING]**
  - Tarea 9.2.1: Evolucionar el `BayesianEngine` para que pueda integrar un peso negativo de tiempo (decay) si el Lóbulo Perceptivo dicta que un estímulo peligroso (ej. arma) se mantiene visible en el stream visual +5 segundos sin voz humana.
- **Bloque 11.1: Tránsito Subjetivo del Afecto [PENDING]**
  - Tarea 11.1.1: Consolidar las fórmulas del "Espejo Roto" (Trauma) en la identidad central (`identity_reflection.py`), para asegurar que cambie los *multipliers* de utilitarismo en etapas posteriores del modelo moral.

## 🚀 Flujo de Sincronización Recomendado

1. **Semana Actual:** Antigravity (N1) se encarga transversalmente de desmonolitizar `kernel.py` y actualizar las dependencias de concurrencia. Claude y Cursor toman sus ramas (`master-claude`, `master-Cursor`) and abordan C.1 y S.1 respectivamente.
2. **Semana Siguiente:** Sincronización de progresos a `master-antigravity`. Antigravity evalúa el impacto del async I/O en la latencia global del kernel.
3. **Validación N0:** Integración unificada a `main` tras validaciones somáticas.

---

## 🟢 CERRADOS (Histórico de Producción)
*Misiones completadas por el Swarm L2 bajo supervisión L1 (referencia rápida; el detalle sigue en secciones `[DONE]` arriba).*

- Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Antigravity/Swarm) `[DONE]`
- Bloque 0.2: Escalabilidad del Chat Server HTTP/ASGI `[DONE]`
- Bloque 10.2: Tribunal Ético Edge & MalAbs local `[DONE]`
- Bloque 10.3: Amortiguación Afectiva (Ganglios Basales EMA) `[DONE]`
- Bloque 12.1: Recursive Narrative Memory (Consolidación) `[DONE]`
