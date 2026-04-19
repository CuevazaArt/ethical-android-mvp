# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel tras la adopción del modelo de trabajo "Swarm" (PnP - Plug-and-Play) en abril de 2026. 

Aquí es donde los escuadrones de ejecución **Rojo (Cursor)**, **Azul (Copilot)** y **Naranja (Claude)** reclaman sus tareas. 
Ningún agente debe saltar a tareas de la cola de otro equipo. 

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Al despertar, revisa tu respectiva sección.
> 2. Toma el primer bloque marcado como `[PENDING]`.
> 3. Muévelo a `[IN_PROGRESS: <Callsign>]` (ej: `[IN_PROGRESS: Rojo-1]`).
> 4. Tras la revisión y commit exitoso a tu rama, márcalo como `[DONE]`.

---

## 🔴 COLA DE EJECUCIÓN ROJO (UID: CURSOR-RED)
**Doctrina:** Alta Fricción, Integración Hardware, Refactorización Arquitectónica, Concurrencia y Streaming.

- **Bloque S.1: Nomad SmartPhone LAN Bridge [PENDING]**
  - Tarea S.1.1: Desarrollar conectores WebSocket/WebRTC (`src/modules/nomad_bridge.py`) para consumir streams de video/audio desde un dispositivo móvil Android/iOS en red local de manera asíncrona.
- **Bloque 9.1: Daemon de Visión Continua (CNN/Webcam) [PENDING]**
  - Tarea 9.1.1: Modificar `VisionInferenceEngine` para crear un stream en background que clasifique entidades a 5Hz utilizando pre-procesamiento asíncrono.
- **Bloque S.2: Calibración Termo-Visual Continua [PENDING]**
  - Tarea S.2.1: Conectar alertas de calor del dispositivo y batería (`VitalityAssessment`) a la telemetría real transmitida por el *Nomad Bridge*.

---

## 🔵 COLA DE EJECUCIÓN AZUL (UID: COPILOT-BLUE)
**Doctrina:** CI/CD Sentinel, Repo Higiene, Pruebas y Deuda Técnica Menor, Boy Scout Paranoico.

- **Bloque 8.1: Linter Continuo y Hardening Vertical [PENDING]**
  - Tarea 8.1.1: Auditar `docstrings` y `type hints` en las divisiones de `src/kernel.py` y `src/kernel_lobes/`. Introducir `try/except` donde fallen por variables nulas. 
- **Bloque 9.3: Refactorización Asíncrona Total de Eferencia [PENDING]**
  - Tarea 9.3.1: Eliminar cuellos de botella síncronos en las llamadas a utilidades de API. Migrar `http_fetch_ollama_embedding` a dependencias puramente `async` con `httpx.AsyncClient`.
- **Bloque 8.2: Hardening de Tests Mocks (Input Trust) [PENDING]**
  - Tarea 8.2.1: Extender mocks para *input_trust* (ej. inyectar simulaciones de ataques homoglyphs cirílicos para evadir la puerta de Absoluto Mal y validar la defensa).
- **Bloque W.1: Frontera Wiki y Sincronización Pública [PENDING]**
  - Tarea W.1.1: Exportar el `WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md` a la página principal de la Wiki de GitHub ("Welcome to the ethical-android-mvp wiki!"). Asegurar licencias legales visibles.

---

## 🟠 COLA DE EJECUCIÓN NARANJA (UID: CLAUDE-ORANGE)
**Doctrina:** Matemática Bayesiana Avanzada, Modelado Cognitivo, Identidad Persistente y RLHF.

- **Bloque C.1: Fusión BMA y Recompensas RLHF [PENDING]**
  - Tarea C.1.1: Conectar matemáticamente los *outputs* asíncronos del `rlhf_reward_model.py` como *Priors* moduladores fuertes dentro de `src/modules/bayesian_engine.py`.
- **Bloque 9.2: Acumulación de Tensión Límbica Estática [PENDING]**
  - Tarea 9.2.1: Evolucionar el `BayesianEngine` para que pueda integrar un peso negativo de tiempo (decay) si el Lóbulo Perceptivo dicta que un estímulo peligroso (ej. arma) se mantiene visible en el stream visual +5 segundos sin voz humana.
- **Bloque 11.1: Tránsito Subjetivo del Afecto [PENDING]**
  - Tarea 11.1.1: Consolidar las fórmulas del "Espejo Roto" (Trauma) en la identidad central (`identity_reflection.py`), para asegurar que cambie los *multipliers* de utilitarismo en etapas posteriores del modelo moral.

---

## 🟢 CERRADOS (Histórico de Producción)
*Las misiones completadas exitosamente por el Swarm L2 bajo supervisión L1.*

- Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Antigravity/Swarm) `[DONE]`
- Bloque 0.2: Escalabilidad del Chat Server HTTP/ASGI `[DONE]`
- Bloque 10.2: Tribunal Ético Edge & Mails Absolutos `[DONE]`
- Bloque 10.3: Amortiguación Afectiva (Ganglios Basales EMA) `[DONE]`
- Bloque 12.1: Recursive Narrative Memory (Consolidación) `[DONE]`
