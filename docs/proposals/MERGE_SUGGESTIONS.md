# Merge & Integration Suggestions

Resumen de observaciones y acciones recomendadas tras el intento de merge de las ramas `master-*` en `merge/master-all-<ts>`.

1) Pull / sincronización
- Observación: la rama local `merge/master-all-20260415-210826` no tiene un ref remoto homónimo (pull no encontró ref). Se recomienda crear la rama remota si la integración debe compartirse.
- Acción sugerida: push de la rama de integración después de resolver conflictos localmente: `git push origin merge/master-all-20260415-210826`.

2) Conflictos detectados
- Archivos en conflicto principales: `CHANGELOG.md`, `src/kernel.py`, `src/modules/absolute_evil.py`.
- Recomendación:
  - `CHANGELOG.md`: fusión tipo `union` (conservar entradas de ambas ramas). Ya se añadió `.gitattributes` para facilitar esto.
  - `src/modules/absolute_evil.py`: aceptar adiciones de categorías (`ECOLOGICAL_DESTRUCTION`, `MASS_MANIPULATION`) si el equipo de seguridad lo valida; asegurarse de actualizar tests y referencias en `semantic_chat_gate`.
  - `src/kernel.py`: revisar firmas y nuevos campos (p. ej. `verbal_llm_degradation_events`, `temporal_context`) y ejecutar tests de integración para detectar roturas de API.

3) Calidad de código y estilo
- Se ejecutó `ruff check .` y se reportaron muchos avisos `F401`, `I001`, `B007` en archivos de tests. No son críticos pero sugieren limpieza: eliminar imports no usados, ordenar bloques de imports y renombrar variables no usadas en bucles de tests.
- Recomendación: ejecutar `ruff --fix` en los tests y/o ajustar reglas en `pyproject.toml` si ciertos patrones son intencionales.

4) Tests
- Se ejecutaron `pytest tests/test_semantic_chat_gate.py` exitosamente.
- Recomendación: una vez resueltos los conflictos clave, ejecutar la suite completa en CI (o localmente con `pytest -q`) y verificar cobertura mínima definida en CI (`--cov-fail-under`) antes de promover la rama.

5) Procedimiento seguro propuesto para finalizar la integración
- Crear un branch de respaldo (hecho previamente en `artifacts/merge_conflicts_*`).
- Resolver manualmente los hunks conflictivos en `src/*` (preferir revisión humana en `kernel.py`).
- Aplicar `git add` + `git commit` para las resoluciones.
- Ejecutar `pytest -q` y `ruff check .` locally; corregir errores importantes.
- Empujar la rama de integración y abrir PR para revisión final.

6) Documentación adicional
- Registrar en `CHANGELOG.md` la decisión de fusión y cualquier cambio de comportamiento que afecte APIs (p. ej. kernel signatures).

---
Si quieres, aplico ahora las resoluciones automáticas acordadas y continúo con los merges restantes, o bien guardo los hunks conflictivos para revisión humana. Indica la acción preferida.
