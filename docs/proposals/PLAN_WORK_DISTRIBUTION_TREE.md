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

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-24 / AUDIT L1) [REVISADO] [ACTUALIZADO]
- **V2.22 (Consolidated Core Minimal)**: INTEGRADO. El sistema ha sido consolidado en `src/core/` (V2).
- **V1.0 Final Stabilization**: ARCHIVADO. La arquitectura Tri-Lobo asíncrona V13/V14 ha sido consolidada en un núcleo minimalista para mayor estabilidad en hardware limitado.
- **L1-AUDIT-PULSE (2026-04-24)**: PENDIENTE. Iniciando ciclo de estabilización para corregir imports rotos tras la consolidación V2.

---

## 🚀 BACKLOG ABIERTO: V2 STABILIZATION & CLEANUP (Phase 16)

> **[PROMPT GENERALISTA PARA EL ENJAMBRE (SWARM)]**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. Hemos completado la consolidación a V2 (src/core/). El objetivo actual es la **Fase 16: Estabilización de V2**. Tu prioridad máxima es reparar la infraestructura rota (imports, scripts, entry points) para que el nuevo núcleo sea funcional. **Instrucciones:** Escoge un bloque [PENDING], repara los imports apuntando a `src.core`, elimina el código legacy redundante, y finaliza siempre con `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

**Bloque 40.0: Reparación de Infraestructura V2 (Prioridad 1) [PENDING]**
- Tarea: Corregir TODOS los imports en `src/*.py` y `tests/**/*.py` que apunten a `src.modules` o `src.kernel_lobes`.
- Meta: Que `python -m src.main` y `python -m src.ethos_cli` funcionen usando `src.core.chat.ChatEngine`.

**Bloque 40.1: Purgado de Código Legacy (Prioridad 2) [PENDING]**
- Tarea: Eliminar archivos obsoletos en la raíz de `src/` (`kernel.py`, `kernel_components.py`, etc.) una vez que `ChatEngine` cubra sus funciones.
- Meta: Repositorio limpio y 100% V2.

**Bloque 40.2: Actualización de Documentación (Prioridad 3) [PENDING]**
- Tarea: Actualizar `README.md` y `docs/` para reflejar la estructura V2.
- Meta: Verdad documental alineada con el código.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 15.0: Desmonolitización y Consolidación V1 -> V2 [DONE]**
- [x] 15.1: Reparar Pytest Collection.
- [x] 15.2: Colapsar src/modules/.
- [x] 15.3: Acoplar LLM Real.
- [x] 15.4: Etiquetado de Estado.
- [x] 15.5: Archivar Teatro.
- [x] 15.6: Demo End-to-End Real.

...
