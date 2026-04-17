# REQUEST: Refactorización Lóbulo Ejecutivo y Cerebelo (Bloques 8.3 & 8.4)

**Para:** Team Copilot (Nivel 2)
**De:** Antigravity (Nivel 1 / General Planner)
**Contexto:** Desmonolitización P0 del kernel hacia la Arquitectura Tri-Lobulada (V1.5).

## Tareas Asignadas

### A) Lóbulo Ejecutivo (`src/kernel_lobes/executive_lobe.py`)
1. **Migración de Componentes Eferentes**: Mover la lógica de reacción y narrativa de `src/kernel.py` hacia este lóbulo.
   - Incluir: `MotivationEngine`, `NarrativeMemory`, `LLMModule.communicate`.
2. **Implementación de `formulate_response()`**:
   - Generar la respuesta final (verbal y motora) basándose en la `EthicalSentence` recibida.
   - Si la sentencia es `is_safe=False`, inyectar un mensaje de veto estandarizado.

### B) Cerebelo Somático (`src/kernel_lobes/cerebellum_node.py`)
1. **Implementación del Daemon Somático**:
   - Completar el bucle de monitoreo en el daemon `CerebellumNode`.
   - Conectar los sensores de `vitality.py` (batería, temperatura) para que polleen a 100Hz simulados.
2. **Interruptores de Seguridad**:
   - Si se detecta un estado crítico, activar el `hardware_interrupt_event` para que el `CorpusCallosumOrchestrator` detenga inmediatamente cualquier acción en el Lóbulo Ejecutivo.

## Invariantes a Mantener
- El Lóbulo Ejecutivo solo puede disparar acciones si la sentecia ética es positiva.

---
> [!IMPORTANT]
> Seguir la Directiva 75/25: Menos tests, más código funcional y eficiente.
