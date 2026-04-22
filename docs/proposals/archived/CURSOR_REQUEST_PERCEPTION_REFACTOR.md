# REQUEST: Refactorización Lóbulo Perceptivo (Bloque 8.1)

**Para:** Team Cursor (Nivel 2)
**De:** Antigravity (Nivel 1 / General Planner)
**Contexto:** Desmonolitización P0 del kernel hacia la Arquitectura Tri-Lobulada (V1.5).

## Tareas Asignadas
1. **Migración de Componentes**: Mover la lógica de `src/kernel.py` relacionada con la percepción hacia `src/kernel_lobes/perception_lobe.py`.
   - Incluir: `LLMModule.perceive`, `VisionInferenceEngine` y `AudioInference`.
2. **Implementación de Clientes Async**:
   - Reemplazar cualquier llamada síncrona residual con `httpx.AsyncClient`.
   - Configurar timeouts agresivos (ej. 3.0s por defecto).
3. **Mantenimiento de `SemanticState`**:
   - Asegurar que el lóbulo devuelva un objeto `SemanticState` completo (definido en `models.py`).
   - Implementar la inyección de `TimeoutTrauma` si una petición asíncrona falla por latencia.

## Invariantes a Mantener
- El lóbulo perceptivo es el **único** lugar donde se permite I/O de red asíncrono.
- No debe contener lógica de decisión ética (vetos o pesos) fuera del parsing estructural.

---
> [!IMPORTANT]
> Seguir la Directiva 75/25: Menos tests, más código funcional y eficiente.
