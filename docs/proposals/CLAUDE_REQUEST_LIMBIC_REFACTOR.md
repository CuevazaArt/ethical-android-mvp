# REQUEST: Refactorización Lóbulo Límbico-Ético (Bloque 8.2)

**Para:** Claude (Nivel 2)
**De:** Antigravity (Nivel 1 / General Planner)
**Contexto:** Desmonolitización P0 del kernel hacia la Arquitectura Tri-Lobulada (V1.5).

## Tareas Asignadas
1. **Migración de Componentes Nucleares**: Mover la lógica de juicio moral de `src/kernel.py` hacia `src/kernel_lobes/limbic_lobe.py`.
   - Incluir: `AbsoluteEvilDetector`, `BayesianEngine`, `EthicalPoles`, `UchiSotoModule`, `DAOOrchestrator` e `IdentityIntegrityManager`.
2. **Implementación de `EthicalSentence`**:
   - Asegurar que el método `judge()` devuelva una `EthicalSentence` (definida en `models.py`) que sea determinista y booleana (Safe/Unsafe).
   - Inyectar penalizaciones en la confianza del motor Bayesiano si el `SemanticState` recibido incluye un `TimeoutTrauma`.
3. **Mantenimiento de Gobernanza**:
   - Asegurar la compatibilidad con `MultiRealmGovernance`.

## Invariantes a Mantener
- **Aislamiento Total de Red**: Queda terminantemente prohibido usar `httpx`, `asyncio.sleep` o cualquier forma de E/S de red en este lóbulo.
- Toda la lógica debe ser **CPU-bound** y sincrónica para garantizar la inmutabilidad ética en el momento del juicio.

---
> [!IMPORTANT]
> Seguir la Directiva 75/25: Menos tests, más código funcional y fiable.
