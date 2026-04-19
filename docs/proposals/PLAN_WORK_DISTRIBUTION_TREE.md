# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]`.
> 2. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 3. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📥 BACKLOG ABIERTO (Open Tasks)

**Bloque S.1: Nomad SmartPhone LAN Bridge [PENDING]**
- Tarea S.1.1: Desarrollar conectores WebSocket/WebRTC (`src/modules/nomad_bridge.py`) para consumir streams de video/audio desde un dispositivo móvil Android/iOS en red local de manera asíncrona.

**Bloque 9.1: Daemon de Visión Continua (CNN/Webcam) [DONE]**
- Tarea 9.1.1: Modificar `VisionInferenceEngine` para crear un stream en background que clasifique entidades a 5Hz utilizando pre-procesamiento asíncrono.

**Bloque S.2: Automatización de Wiki-Sync vía GitHub Actions [PENDING]**
- Tarea S.2.1: Implementar un Workflow de GitHub Actions que sincronice proactivamente archivos de `docs/*` hacia el repositorio Wiki del proyecto. Configurar disparadores en cada `push` a las ramas de integración para mantener la transparencia pública total.

**Bloque 8.1: Linter Continuo y Hardening Vertical [DONE]**
- Tarea 8.1.1: Auditar `docstrings` y `type hints` en las divisiones de `src/kernel.py` y `src/kernel_lobes/`. Introducir `try/except` donde fallen por variables nulas. 

**Bloque 9.3: Refactorización Asíncrona Total de Eferencia [DONE]**
- Tarea 9.3.1: Eliminar cuellos de botella síncronos en las llamadas a utilidades de API. Migrar `http_fetch_ollama_embedding` a dependencias puramente `async` con `httpx.AsyncClient`.

**Bloque W.1: Frontera Wiki y Sincronización Pública [PENDING]**
- Tarea W.1.1: Exportar el `WIKI_EXECUTIVE_SUMMARY_NOMADIC_VISION.md` a la página principal de la Wiki de GitHub ("Welcome to the ethical-android-mvp wiki!"). Asegurar licencias legales visibles.

**Bloque C.1: Fusión BMA y Recompensas RLHF [PENDING]**
- Tarea C.1.1: Conectar matemáticamente los *outputs* asíncronos del `rlhf_reward_model.py` como *Priors* moduladores fuertes dentro de `src/modules/bayesian_engine.py`.

**Bloque 11.1: Tránsito Subjetivo del Afecto [PENDING]**
- Tarea 11.1.1: Consolidar las fórmulas del "Espejo Roto" (Trauma) en la identidad central (`identity_reflection.py`), para asegurar que cambie los *multipliers* de utilitarismo en etapas posteriores del modelo moral.

---

## 🟢 CERRADOS (Histórico de Producción)
*Las misiones completadas exitosamente bajo supervisión L1.*

- Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Antigravity/Swarm) `[DONE]`
- Bloque 0.2: Escalabilidad del Chat Server HTTP/ASGI `[DONE]`
- Bloque 10.2: Tribunal Ético Edge & Mails Absolutos `[DONE]`
- Bloque 10.3: Amortiguación Afectiva (Ganglios Basales EMA) `[DONE]`
- Bloque 12.1: Recursive Narrative Memory (Consolidación) `[DONE]`
