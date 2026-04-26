# [BLOQUE] L1-AUDIT: Auditoría de Repo y Orquestación de Enjambre

> **Este documento es una ORDEN OPERATIVA.** Debe ser ejecutado por un agente Gemini 3.1 Pro (Low) en Antigravity, Cursor, o cualquier IDE con acceso al repositorio completo.

---

## [IDENTIDAD]: Scout-L1-AUDIT
## [MODELO IDEAL]: Gemini 3.1 Pro (Low)
## [ALTERNATIVA]: Claude Sonnet 4.6 (Thinking) — Solo si Pro Low falla 3 veces.

---

## FASE 1: Auditoría Completa del Repositorio

### Objetivo
Revisar el estado del repositorio `CuevazaArt/ethical-android-mvp` en **todas sus ramas** e identificar:
1. Ramas obsoletas que deben eliminarse (ya mergeadas o abandonadas).
2. Ramas que contienen trabajo valioso no mergeado a `main`.
3. Inconsistencias entre ramas y el estado actual de `main`.
4. Archivos que violen las nuevas directivas de licenciamiento híbrido (ver `LICENSING_STRATEGY.md`).

### Ramas a Auditar

**Ramas locales:**
- `antigravity-team`
- `backup-v13.1-distributed-brain`
- `master-Cursor`
- `master-antigravity`
- `master-claude`
- `master-cursorultra`
- `master-visualStudio`
- `temp-antigravity-backup`

**Ramas remotas relevantes (agrupar por prefijo):**
- `remotes/origin/antigravity-team`
- `remotes/origin/antigravity/hemisphere-refactor-proposal`
- `remotes/origin/arch/tri-lobe-kernel-p0`
- `remotes/origin/backup/*` (todas)
- `remotes/origin/claude/*` (todas)
- `remotes/origin/copilot/*` (todas)
- `remotes/origin/cursor*` (todas)
- `remotes/origin/doc/*`
- `remotes/origin/feature/*`
- `remotes/origin/kernel-for-Vusual-Std`
- `remotes/origin/main-pre-commune`
- `remotes/origin/main-whit-landing`
- `remotes/origin/master-*` (todas)
- `remotes/origin/merge/*`
- `remotes/origin/refactor/*`

### Procedimiento
1. Para cada rama, ejecuta `git log main..[branch] --oneline -5` para ver si tiene commits únicos.
2. Si la rama no tiene commits por delante de `main` → **marcar para ELIMINACIÓN**.
3. Si tiene commits únicos → revisar si el contenido es:
   - a) Valioso y no mergeado → **marcar para RESCUE** (rescatar a main).
   - b) Obsoleto/conflictivo con V2 → **marcar para ELIMINACIÓN** con justificación.
4. Verificar que `LICENSING_STRATEGY.md`, `TRADEMARK.md`, y `.github/FUNDING.yml` existen en `main`.
5. Verificar que `src/clients/nomad_android/LICENSE_BSL` existe.

### Entregable de FASE 1
Generar un informe con formato:

```
## Informe de Auditoría de Ramas

### ELIMINAR (ya mergeadas o abandonadas)
- [branch-name]: [razón de 1 línea]

### RESCATAR (trabajo valioso pendiente)
- [branch-name]: [qué contiene, qué archivos]

### MANTENER (activas o referencia)
- main
- [otras si aplica]
```

---

## FASE 2: Generar 5 Prompts de Enjambre Flash

### Objetivo
Basándote en el informe de FASE 1, generar **exactamente 5 prompts** para un enjambre de agentes **Gemini 3 Flash**. Cada prompt debe ser auto-contenido (el agente Flash no tendrá contexto previo).

### Distribución de Tareas del Enjambre

**Flash-Scout-1: PODA DE RAMAS MUERTAS**
- Recibe la lista de ramas a eliminar.
- Ejecuta `git push origin --delete [branch]` para cada una.
- Confirma la eliminación con `git branch -a`.

**Flash-Scout-2: HEADERS DE LICENCIA EN KERNEL**
- Agrega el header Apache 2.0 al inicio de cada archivo `.py` en `src/core/` y `src/server/`:
```python
# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.
```
- NO tocar archivos en `src/clients/nomad_android/` (esos son BSL).

**Flash-Scout-3: HEADERS DE LICENCIA EN SDK ANDROID**
- Agrega el header BSL 1.1 al inicio de cada archivo `.kt` en `src/clients/nomad_android/`:
```kotlin
// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
```

**Flash-Scout-4: LIMPIEZA DE DOCUMENTACIÓN OBSOLETA**
- Revisar archivos en la raíz del proyecto que ya no sean relevantes para V2:
  - `CLAUDE_REQUEST_HEMISPHERE_REFACTOR.md` → ¿Obsoleto? Eliminar.
  - `COPILOT_REQUEST_HEMISPHERE_REFACTOR.md` → ¿Obsoleto? Eliminar.
  - `CURSOR_REQUEST_HEMISPHERE_REFACTOR.md` → ¿Obsoleto? Eliminar.
  - `PROPOSAL_CLAUDE_HEMISPHERE_CRITIQUE.md` → ¿Obsoleto? Eliminar.
  - `PROPOSAL_HEMISPHERE_LOBE_COUNT_DISCUSSION.md` → ¿Obsoleto? Eliminar.
  - `INTEGRATION_PULSE_ANALYSIS_2026_04_16.md` → ¿Obsoleto? Eliminar.
  - `COLLABORATIVE_BRANCHES.md` → Revisar si sigue vigente. Si no, eliminar.
  - `ONBOARDING.md` → Verificar si está actualizado para V2. Si no, actualizar o eliminar.
- Para cada archivo: leer las primeras 20 líneas, determinar si es V1/legacy o vigente.
- Generar lista de archivos a eliminar con justificación de 1 línea.

**Flash-Scout-5: ACTUALIZACIÓN DE README.md**
- Reescribir `README.md` para que refleje:
  - Estado actual del proyecto (V2, 203 tests, Android SDK).
  - Modelo de licenciamiento híbrido (Apache 2.0 + BSL).
  - Links a `LICENSING_STRATEGY.md` y `TRADEMARK.md`.
  - Badges: tests passing, license Apache 2.0, GitHub Sponsors.
  - Instrucciones de instalación y uso del Kernel.
  - Sección "Contributing" breve apuntando a `CONTRIBUTING.md`.
  - **Tono profesional y atractivo para atraer estrellas y sponsors.**

### Formato de Cada Prompt Flash

Cada prompt generado DEBE seguir este formato exacto:

```markdown
[IDENTIDAD]: Flash-Scout-[N]
[MODELO IDEAL]: Gemini 3 Flash
[ALTERNATIVA]: Gemini 3.1 Pro (Low) — Solo si Flash falla 3 veces.

[DIRECTIVA CERO]
No estás autorizado a rendirte ni a dejar trabajo a medias. Entrega código funcional o no entregues nada.

[OBJETIVO]
(Descripción mecánica y precisa de la tarea)

[ARCHIVOS PERMITIDOS]
(Lista exacta de archivos que puede tocar)

[ARCHIVOS PROHIBIDOS]
(Lista de archivos que NO debe tocar bajo ninguna circunstancia)

[ENTREGABLE]
(Qué debe mostrar al terminar: diff, log, lista de archivos)

[REGLAS]
- Zero dead code.
- Sin saludos, sin despedidas.
- Un commit por tarea con mensaje: "Flash-Scout-N: [descripción de 1 línea]"
```

---

## FASE 3: Entrega Final

Al completar FASE 1 y FASE 2, el Scout-L1-AUDIT debe:
1. Guardar el informe de auditoría como comentario en el chat o como archivo temporal.
2. Presentar los 5 prompts listos para copiar y pegar.
3. **NO ejecutar los prompts.** Solo generarlos. L0 decide cuándo y dónde lanzar cada Flash-Scout.

---

## Notas para L0

- Puedes lanzar los 5 Flash-Scouts en paralelo (uno por ventana/tab de Antigravity o por IDE).
- Flash-Scout-1 (poda de ramas) debe ejecutarse PRIMERO, antes que los otros, para evitar que trabajen sobre ramas muertas.
- Después de que todos terminen, regresa a L1 (yo) y di `review` para validar la integración.
