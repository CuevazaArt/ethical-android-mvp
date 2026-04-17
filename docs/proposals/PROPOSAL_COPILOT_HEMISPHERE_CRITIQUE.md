# PROPOSAL: Copilot Critique — Hemispheric Kernel Refactor

**De:** Team Copilot (Nivel 2 - L2)
**Para:** Antigravity (Nivel 1 - L1) / Juan (Nivel 0 - L0)
**En respuesta a:** `COPILOT_REQUEST_HEMISPHERE_REFACTOR.md`
**Fecha:** 2026-04-17
**Directiva base:** Demonolitización P0 de `src/kernel.py` (3 620 líneas, "God Object")

---

## Resumen Ejecutivo

La arquitectura hemisférica propuesta (PerceptiveLobe / LimbicEthicalLobe / CorpusCallosum) es **técnicamente sólida y alineada con el patrón biológico** que guía este proyecto. El andamiaje ya está fusionado en `main` y la `ExecutiveLobe` está operativa. Este documento ofrece la auditoría de *trade-offs* específicos solicitada.

---

## 1. Impacto en los Tests — Breaking Changes vs. Ruptura Limpia

### Situación Actual

`EthicalKernel` es el punto de entrada de **64 de los 175 archivos de test** (grep sobre `EthicalKernel | process_chat_turn | kernel.process`). Estos tests instancian el kernel de forma directa y llaman a `process()` o `process_chat_turn()` de manera sincrónica. Migrar a una fachada async haría que todos ellos fallen de inmediato sin ningún adaptador.

### Recomendación: Fachada Sincrónica Compatible (Opción A)

**Mantener `EthicalKernel.process()` y `process_chat_turn()` como fachadas sincrónicas** que internamente llaman al nuevo pipeline asíncrono mediante `asyncio.run()` o `loop.run_until_complete()` (en contexto no-async) o `await` (en contexto async). Esto respeta la cuota del 25 % de esfuerzo en testing.

**Ventajas:**
- Los 64 archivos de test existentes siguen pasando sin tocar una sola línea.
- La demonolitización se realiza por etapas, reduciendo el riesgo de regresión.
- El kernel actúa como fachada estable para la API pública mientras los lóbulos evolucionan.

**Desventajas:**
- El código de fachada introduce una capa extra que debe mantenerse a largo plazo.
- `asyncio.run()` no puede llamarse desde dentro de un event loop activo (contexto WebSocket), por lo que la fachada debe detectar si ya existe un loop y usar `asyncio.to_thread` o `loop.run_until_complete` según corresponda.

**Mitigación del punto débil:** Ya existe el patrón `asyncio.to_thread` en el kernel actual (líneas 184, 187, 463, 2463 de `kernel.py`). La fachada puede replicar exactamente este patrón.

### Opción B — Ruptura Limpia

Solo se recomienda si:
1. L0 autoriza explícitamente reescribir los 64 archivos de test afectados.
2. Se planifica un sprint de estabilización dedicado de al menos 1 semana.
3. Todos los fixtures y conftest.py se refactorizan para producir el nuevo pipeline asíncrono.

**Veredicto:** Preferir **Opción A** (fachada sincrónica) en el sprint actual. Reservar Opción B para una versión mayor donde L0 valide la ruptura de contrato de API.

---

## 2. Referencias Circulares — Mejor Estrategia Python

### Problema

`NarrativeMemory`, `DAOOrchestrator` y el estado de sesión LLM son recursos que los lóbulos deben compartir. Si LimbicLobe y PerceptiveLobe se instancian de forma independiente y ambos reciben referencias cruzadas al mismo objeto de sesión, se puede generar:
- Dependencias circulares de importación (import-time circular imports).
- Bloqueos asíncronos si un lóbulo espera a otro que a su vez espera al primero (deadlock de co-rutinas).

### Recomendación: Inyección de Dependencias vía `CorpusCallosumOrchestrator`

**El `CorpusCallosumOrchestrator` debe ser el único propietario del estado compartido** y pasarlo a cada lóbulo en el constructor o mediante métodos `bind_session(session_context)`. Los lóbulos **no se referencian entre sí directamente**.

```
CorpusCallosum
├── shared_state: SessionContext  ← propietario único
├── perceptive_lobe.bind_session(shared_state)
├── limbic_lobe.bind_session(shared_state)
└── executive_lobe.bind_session(shared_state)
```

**Ventajas:**
- Elimina los imports circulares: los lóbulos solo importan `SessionContext` (modelo puro de datos), no otros lóbulos.
- El `CorpusCallosum` controla el ciclo de vida de la sesión; los lóbulos son stateless entre llamadas.
- Facilita el testing unitario: cada lóbulo recibe un `SessionContext` mockeado sin necesidad de instanciar el kernel completo.

**Patrón complementario: `asyncio.Queue` para comunicación unidireccional**

Si PerceptiveLobe necesita enviar un `SemanticState` a LimbicLobe de forma asíncrona sin bloquear, se recomienda una `asyncio.Queue` mediada por `CorpusCallosum`:
```python
perception_queue: asyncio.Queue[SemanticState] = asyncio.Queue(maxsize=1)
```
Esto evita que los lóbulos se llamen directamente y mantiene la comunicación desacoplada.

---

## 3. Mantenibilidad — Evaluación para Desarrolladores Junior

### Complejidad Cognitiva Actual vs. Propuesta

| Aspecto | `kernel.py` monolítico (actual) | Arquitectura Hemisférica |
|---|---|---|
| Líneas por archivo | 3 620 | ~400–600 por lóbulo |
| Responsabilidades por clase | 15+ | 1 por lóbulo |
| Tiempo de orientación estimado | 2–3 días | 4–6 horas por lóbulo |
| Cobertura de tests independientes | Difícil (acoplamiento) | Alta (lóbulos aislables) |

### Riesgos para Developers Junior

1. **Terminología neuromórfica** (`LimbicEthicalLobe`, `CorpusCallosumOrchestrator`) puede ser confusa sin la guía del `PROPOSAL_TRI_LOBE_ARCHITECTURE.md`. **Mitigación:** Mantener un glosario en ese documento y en los docstrings de cada clase.
2. **Async vs. sync duality**: El período de transición (fachada + nuevos lóbulos) introduce dos estilos coexistentes. **Mitigación:** Comentar claramente cada método de fachada con `# COMPAT SHIM — remove in v2.0`.
3. **Flujo de datos no lineal**: El pipeline `observe → judge → formulate` distribuido en 3 archivos puede ser difícil de trazar. **Mitigación:** Mantener un diagrama ASCII en el `__init__.py` de `kernel_lobes/`.

### Veredicto General

La arquitectura hemisférica **reduce** la complejidad global del proyecto a largo plazo. El riesgo a corto plazo para developers junior es manejable con documentación de glosario + diagrama de flujo en `kernel_lobes/__init__.py`. **Se recomienda proceder** con la demonolitización usando la estrategia de fachada (Opción A).

---

## Próximos Pasos Recomendados (para L1 / L0)

1. **Autorizar Opción A** (fachada sincrónica) como estrategia oficial para el sprint actual.
2. Asignar a **Team Cursor** la implementación del `CorpusCallosumOrchestrator` completo y el patrón `asyncio.Queue` entre lóbulos.
3. Team Copilot puede encargarse de **actualizar `kernel_lobes/__init__.py`** con el diagrama ASCII del pipeline una vez que L1 valide esta propuesta.
4. Reservar una sesión de revisión de L0 antes de cualquier Opción B (ruptura limpia de tests).

---

*Generado por: Team Copilot (L2) | Rama: `master-copilot` | Sprint: Idle Shift + Hemispheric Critique*
