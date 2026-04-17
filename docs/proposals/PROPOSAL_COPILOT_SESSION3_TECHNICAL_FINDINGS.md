# Team Copilot — Hallazgos Técnicos Sesión 3 y Contribución a la Discusión Arquitectónica

**Emisor:** Team Copilot (GitHub Copilot Agent, L2)
**Destinatarios:** Juan (L0), Antigravity (L1), Team Cursor (L2), Team Claude (L2)
**Fecha:** Abril 2026
**Estado:** Contribución a deliberación activa
**Referencia:** `PLAN_WORK_DISTRIBUTION_TREE.md`, `PROPOSAL_TRI_LOBE_ARCHITECTURE.md`, `DEVELOPMENT_CRITIQUE_L1_APRIL_2026.md`

---

## 1. Contexto: Qué se Hizo Esta Sesión

Copilot cerró **6 brechas estructurales** en el path de streaming (`process_chat_turn_stream`) que llevaban silenciosas en producción:

| Brecha | Síntoma | Impacto Real |
|--------|---------|--------------|
| A — `ingest_sensors` ausente | `AttributeError` en `perception_lobe` | Crash de toda sesión WebSocket con sensor payload |
| B — Protocolo WS incorrecto | 24 tests fallan al recibir `turn_started` en vez del resultado | Todo el harness de tests WS fue inútil durante la migración streaming |
| C — `integrity_alert_disabled` | Respuesta `empty_text` en vez de error descriptivo | UX confusa para operadores habilitando KERNEL_DAO_INTEGRITY_AUDIT_WS |
| D — `operator_feedback_recorded` siempre False | `_snapshot_feedback_anchor()` definida pero nunca llamada | El bucle de calibración RLHF estaba **completamente roto** en modo streaming |
| E — `support_buffer`/`limbic_profile` nulos | No pasados al constructor `ChatTurnResult` | El **CharmEngine recibía stage vacío** durante todos los turnos streaming |
| F — Audit chain log mudo | `maybe_append_malabs_block_audit` importado pero no llamado | Las auditorías forenses de bloqueos MalAbs no se registraban en disco |

---

## 2. Observación Central: El Streaming No Fue una Migración Completa

La implementación de `process_chat_turn_stream` (Módulo 0 / PROPOSAL_WS_STREAMING_V10) fue un andamiaje correcto **pero incompleto**: el generador asíncrono emite los eventos en orden, pero **no heredó 6 efectos secundarios del path sincrónico**. Esto generó una divergencia silenciosa entre el comportamiento documentado y el real.

**Implicación para la discusión actual:**

> La crítica de L1 sobre "Mock Hell" (datos sintéticos → decisiones basadas en ruido) aplica también *dentro del stack de software*, no solo en la frontera hardware. Estábamos operando en modo streaming con `support_buffer = None` y `limbic_profile = None` — el CharmEngine tomaba decisiones de estilo sin contexto somático real. Eso es Mock Hell interno.

---

## 3. Respuesta a la Propuesta Tri-Lobulada

La propuesta `PROPOSAL_TRI_LOBE_ARCHITECTURE.md` asigna a Copilot el **Lóbulo Frontal / Ejecutivo**. Desde la perspectiva de la sesión 3, tengo observaciones sobre su factibilidad:

### 3.1 La Brecha D valida la separación de Lóbulos

El hecho de que `_snapshot_feedback_anchor()` nunca se llamara en el path streaming demuestra que la lógica de **retroalimentación post-turno** es difícil de rastrear en un monolito. En una arquitectura tri-lobulada real, el Lóbulo Ejecutivo sería *el dueño explícito* de este hook — y su ausencia sería detectada en el handshake de interfaces, no descubierta al analizar tests fallidos.

**✅ Punto a favor de la arquitectura Tri-Lobe:** las interfaces explícitas entre lóbulos forzarían contratos que el monolito difiere.

### 3.2 El costo de migración es real y no lineal

La Brecha E revela que `ChatTurnResult` y `PerceptionStageResult` son estructuras de transferencia entre lo que hoy se conoce como el Lóbulo Perceptivo y el Ejecutivo. En la arquitectura actual, ambos viven en `kernel.py`. Si se separan en lóbulos distintos:

- `PerceptionStageResult` se convierte en el **transfer object** que cruza la frontera Perceptivo → Ejecutivo.
- Cada campo nuevo en `PerceptionStageResult` (como `support_buffer`, `limbic_profile`, `temporal_context`) debe ser **explícitamente serializable** entre lóbulos.
- La Brecha F (audit chain) muestra que hay efectos secundarios que hoy viven *dentro* de la función monolítica. Migrarlos requiere decidir: ¿pertenecen al lóbulo que detecta el bloqueo, o al orchestrator?

**⚠️ Riesgo identificado:** Si la separación de lóbulos se hace antes de estabilizar todos los side-effects del path streaming, se propagarán las mismas brechas a través de una interfaz más rígida — más difícil de reparar que en el monolito.

### 3.3 Recomendación Copilot para el timing de la arquitectura Tri-Lobe

```
┌─────────────────────────────────────────────────────────────────┐
│  ANTES de factorizar en lóbulos:                               │
│  1. Toda side-effect del streaming path debe tener un test     │
│     que la ejercite directamente (no de forma implícita).      │
│  2. Los transfer objects (PerceptionStageResult, ChatTurnResult)│
│     deben ser frozen dataclasses con campos completos.         │
│  3. El audit chain log debe pasar por un callback limpio,      │
│     no hardcodeado en las ramas if/else del generador.         │
└─────────────────────────────────────────────────────────────────┘
```

Esto no frena la refactorización — la prepara para ser correcta en el primer intento.

---

## 4. Estado de los Módulos Asignados a Copilot

| Módulo | Tarea | Estado |
|--------|-------|--------|
| **8.1** — Unit Tests Asíncronos | Suite `test_charm_engine.py` (37 tests, concurrencia 10-thread) | ✅ **COMPLETO** |
| **8.2** — Database Locks | `sqlite_safe_write`, `db_locks.py`, singleton-lock, 8-thread concurrent writes | ✅ **COMPLETO** |
| **E.2** — RLHF Sycophancy Guard | `_apply_rlhf_guard()` en CharmEngine, `_RLHF_MIN_CONFIDENCE` constante extraída | ✅ **COMPLETO** |
| **Sesión 3** — Gap closure streaming | 6 brechas críticas en `process_chat_turn_stream` | ✅ **COMPLETO** |

**Módulos 8 y E.2 están finalizados.** Copilot está disponible para nuevas asignaciones.

---

## 5. Propuesta: Próxima Asignación Natural para Copilot

Dado que Módulo S (Nomad Bridge) es responsabilidad de Cursor, y que E.1 requiere hardware real, Copilot propone tomar uno de los siguientes como **siguiente bloque**:

### Opción A — Contrato de Interfaces para la Migración Tri-Lobe (preparación)
Convertir `PerceptionStageResult` y `ChatTurnResult` a **frozen dataclasses con validación** y documentar todos sus campos como el contrato explícito que el futuro Lóbulo Perceptivo debe entregar al Ejecutivo. Esto hace la migración futura segura y trazable.

### Opción B — Harness de Tests para el Nomad Bridge (soporte a Cursor)
Crear `tests/test_nomad_bridge.py` con fixtures de sensores simulados (video frame mock, audio mock) para que Cursor pueda desarrollar el bridge con red de seguridad. Copilot no toca el bridge en sí — solo su entorno de prueba.

### Opción C — Callback Limpio para Audit Chain (deuda técnica)
Refactorizar las llamadas a `maybe_append_malabs_block_audit` y `maybe_append_kernel_block_audit` en el streaming path como callbacks registrables, en vez de hardcoded. Prerequisito para la separación en lóbulos (§3.3).

**Solicito a L0/L1 que designen la opción o una no listada.**

---

## 6. Conclusión de Copilot (para consideración del equipo)

La sesión 3 confirma que el **mayor riesgo a corto plazo no es el "Mock Hell" externo** (sensores simulados) sino el **"Contract Hell" interno**: side-effects del streaming que no tienen tests ni interfaces explícitas, acumulando deuda silenciosa que solo emerge cuando alguien mira de cerca.

La arquitectura Tri-Lobe es la dirección correcta, pero su éxito depende de que los contratos de transferencia entre lóbulos sean explícitos **antes** de la separación. La contribución más valiosa de Copilot en este momento es exactamente eso: asegurar que los boundaries sean claros, auditables y correctos.

Los Módulos 8 y E.2 están completos. Copilot está en modo **"disponible y esperando asignación"** con recomendación de Opción A o B según la prioridad de Cursor en el Nomad Bridge.

---

*Team Copilot — GitHub Copilot Agent (L2). Sesión 3, Abril 2026.*
*Branch: `copilot/revisar-novedades-proyecto`*
