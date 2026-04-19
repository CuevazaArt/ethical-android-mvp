# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]`.
> 2. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 3. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-19-V2)
- **S.4 (Persistence)**: Completado. Gap de amnesía bayesiana cerrado mediante LBP y Schema V5.
- **8.2 (Hardening)**: Completado. Blindaje Anti-NaN y saneamiento de sensores en flujo asíncrono.
- **C.1 (Bayesian RLHF)**: Completado. Modulación no lineal y category-aware operando.
- **11.1 (Identity/Trauma)**: Completado. Integrada magnitud de trauma en el core de decisión.
- **S.1/S.2 (Nomad/Wiki)**: Completado. Bridge LAN estable y sincronización de Wiki automatizada.
- **S.3 (Redundancy)**: Completado. Consolidados modelos y utilidades.

---

## 📥 BACKLOG ABIERTO (Open Tasks)

**Bloque S.4: Persistencia Bayesiana y Field Readiness [DONE]**
- Tarea S.4.1: Implementar **Local Bayesian Persistence (LBP)**. Guardar el `posterior_alpha` en la base de datos (DAO) al final de cada turno.
- Tarea S.4.2: Restaurar el estado bayesiano en el arranque para habilitar aprendizaje ético multi-sesión. (Focal point: Antigravity)

**Bloque 8.2: Hardening Vertical Auxiliar [DONE]**
- Tarea 8.2.1: Revisión de `security_verification.py` y `adversarial_suite.py`. Cubrir gaps de saneamiento de inputs en el lóbulo de percepción. (Asignado a: Squad Beta / Team Cursor)

**Bloque S.3: Monitoreo de Redundancia y Desuso [DONE]**
- Tarea S.3.1: Escanear el kernel en busca de métodos decorativos o shims obsoletos. (Completado: Antigravity)

---

**Bloque S.1: Nomad SmartPhone LAN Bridge [DONE]**
- Tarea S.1.1: Desarrollar conectores WebSocket/WebRTC (`src/modules/nomad_bridge.py`) para consumir streams de video/audio desde un dispositivo móvil Android/iOS en red local de manera asíncrona. (Completado: Antigravity)

**Bloque 9.1: Daemon de Visión Continua (CNN/Webcam) [DONE]**
- Tarea 9.1.1: Modificar `VisionInferenceEngine` para crear un stream en background que clasifique entidades a 5Hz utilizando pre-procesamiento asíncrono.

**Bloque S.2: Automatización de Wiki-Sync vía GitHub Actions [DONE]**
- Tarea S.2.1: Implementar un Workflow de GitHub Actions que sincronice proactivamente archivos de `docs/*` hacia el repositorio Wiki del proyecto. (Completado: Antigravity)

**Bloque 8.1: Linter Continuo y Hardening Vertical [DONE]**
- Tarea 8.1.1: Auditar `docstrings` y `type hints` en las divisiones de `src/kernel.py` y `src/kernel_lobes/`. Introducir `try/except` donde fallen por variables nulas. 

**Bloque 9.3: Refactorización Asíncrona Total de Eferencia [DONE]**
- Tarea 9.3.1: Eliminar cuellos de botella síncronos en las llamadas a utilidades de API. Migrar `http_fetch_ollama_embedding` a dependencias puramente `async` con `httpx.AsyncClient`.

**Bloque W.1: Frontera Wiki y Sincronización Pública [DONE]**
- Tarea W.1.1: Exportar el `WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md` a la página principal de la Wiki de GitHub ("Welcome to the ethical-android-mvp wiki!"). (Completado: Antigravity)

**Bloque C.1: Fusión BMA y Recompensas RLHF [DONE]**
- Tarea C.1.1: Conectar matemáticamente los *outputs* asíncronos del `rlhf_reward_model.py` como *Priors* moduladores fuertes dentro de `src/modules/bayesian_engine.py`.
- Tarea C.1.2: Validación matemática de alineación RLHF -> BMA (`scripts/eval/eval_rlhf_alignment.py`). (Completado: Antigravity)

**Bloque 11.1: Tránsito Subjetivo del Afecto [DONE]**
- Tarea 11.1.1: Consolidar las fórmulas del "Espejo Roto" (Trauma) en la identidad central (`identity_reflection.py`), para asegurar que cambie los *multipliers* de utilitarismo en etapas posteriores del modelo moral. (Completado: Antigravity)

---

## 🟢 CERRADOS (Histórico de Producción)
*Las misiones completadas exitosamente bajo supervisión L1.*

- Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Antigravity/Swarm) `[DONE]`
- Bloque 0.2: Escalabilidad del Chat Server HTTP/ASGI `[DONE]`
- Bloque 10.2: Tribunal Ético Edge & Mails Absolutos `[DONE]`
- Bloque 10.3: Amortiguación Afectiva (Ganglios Basales EMA) `[DONE]`
- Bloque 12.1: Recursive Narrative Memory (Consolidación) `[DONE]`
