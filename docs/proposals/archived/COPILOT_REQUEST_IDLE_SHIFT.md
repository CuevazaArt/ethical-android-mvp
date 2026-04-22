# Delegación L1 -> L2 (Team Copilot): Turno "Idle Shift"

**Emisor:** Antigravity (L1) / Juan (L0)
**Receptor:** Team Copilot (L2 - GitHub Engine)
**Prioridad:** Alta (Ejecutar durante el periodo de descanso C-Suite)
**Contexto:** Team Cursor y Team Claude se encuentran inactivos por el momento. Mientras ellos regresan, necesitamos que impulses la Fase 4 de la nueva Arquitectura Tri-Lobe.

## Mandato Estricto (`BRANCH-LOCALIZATION-02`)
Debes realizar todos estos trabajos única y exclusivamente en tu rama designada: `master-copilot`. **No crees nuevas ramas**. Todo tu trabajo será revisado a la vuelta del descanso.

## Bloque de Tareas Asignadas

### 1. Refactorización del "Executive Lobe" (Fase 4 del task.md)
Tu objetivo es poblar el archivo vacío `src/kernel_lobes/executive_lobe.py` que ya hemos creado en el andamiaje.
* **Instrucción 1.1:** Migra la clase `MotivationEngine` desde `src/modules/motivation_engine.py` (o instánciala dentro de `ExecutiveLobe`).
* **Instrucción 1.2:** Asimila la lógica del *Monólogo Narrativo* (`compose_monologue_line`) en el `ExecutiveLobe` para que solo se dispare si el juicio ético del Córtex recibe un estado `is_safe=True`.

### 2. Mantenimiento del Repositorio (Mecánicas de GitHub)
Al estar más cerca de la infraestructura de repositorios:
* **Instrucción 2.1:** Asegúrate de que los *stubs* (esqueletos vacíos) en `src/kernel_lobes/` están tipeados correctamente. Límpialos de cualquier error sintáctico (Linting).
* **Instrucción 2.2:** Prepara el terreno actualizando silenciosamente el `.gitignore` o archivos similares si notas redundancias que entorpezcan.

## Resultado Esperado para la Revisión
A nuestra vuelta, esperamos encontrar un Push atómico en `master-copilot` con tu aporte al `ExecutiveLobe`. El Andamiaje de Fase 1 ya fue fusionado desde `main`, así que tu rama ya cuenta con las carpetas nuevas. ¡Éxito en tu turno solitario!
