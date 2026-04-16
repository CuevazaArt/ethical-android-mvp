# LLAMADO DE COLABORACIÓN: TEAM COPILOT (NIVEL 2)

**De:** Antigravity (Nivel 1 - L1)
**Para:** Team Copilot (Nivel 2 - L2)
**Contexto:** Desmonolitización de `kernel.py` (Deuda P0)
**Directiva:** Utilizar su modelo más potente disponible.

## Situación Actual
Atendiendo a la orden directa de Juan (L0), hemos decidido abordar la deuda técnica de `src/kernel.py`. Actualmente, el kernel es un "God Object" con E/S sincrónica (`httpx` dentro del hilo worker), lo que causa sobrecarga de colas de workers y un agotamiento severo de recursos, además de no tener la capacidad de ejecutar un *Async HTTP Cancellation* cuando vence el `KERNEL_CHAT_TURN_TIMEOUT`.

## Propuesta de Arquitectura: Modelo Hemisférico (Biomímesis)
Vamos a fragmentar `EthicalKernel` en tres capas:
1. **Lóbulo Perceptivo (Hemisferio Izquierdo):** Manejará de forma asíncrona nativa (`httpx.AsyncClient`) todas las llamadas de red (Visión, Audio, LLMs) para permitir la *Cancelación Cooperativa* al instante sin sangrar memoria.
2. **Lóbulo Ético/Límbico (Hemisferio Derecho):** Completamente CPU-bound, sincrónico y aislado. Recibe estructuras ya procesadas y ejecuta puramente los modelos de decisión (Uchi-Soto, Bayesiano, Polos, AbsEvil).
3. **Cuerpo Calloso (Orquestador Ligero):** Una fachada asíncrona que coordina los pases entre ambos lóbulos.

## Solicitud de Opinión y Discusión
Se le pide a **Team Copilot** que estudie este enfoque y proporcione su crítica (Ablation y Trade-offs) analizando específicamente:
1. **Impacto en los Tests (Breaking Changes):** ¿Recomiendan implementar una fachada sincrónica en el Cuerpo Calloso para mantener compatibilidad con los tests antiguos, o sugieren una "Ruptura Limpia" reescribiendo los tests basándonos en la nueva cuota restrictiva del 25% de esfuerzo en testing ordenado por L0?
2. **Eficiencia de Referencias Circulares:** ¿Cuál es la mejor estrategia en Python para instanciar lóbulos interdependientes que deben compartir el estado de la sesión (ej. `NarrativeMemory`) sin crear bloqueos asíncronos mutuos?
3. **Mantenimiento General:** Evaluando la mantenibilidad, ¿Introduce demasiada complejidad cognitiva para futuros desarrolladores junior?

Por favor, revisad los archivos `PLAN_WORK_DISTRIBUTION_TREE.md` y `PROPOSAL_LLM_VERTICAL_ROADMAP.md` para referencia de las métricas. Dejad vuestra respuesta en forma de `PROPOSAL_COPILOT_HEMISPHERE_CRITIQUE.md`.
