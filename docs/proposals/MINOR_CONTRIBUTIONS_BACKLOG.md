# Backlog de Contribuciones Menores y Deuda Técnica (Minor Contributions)

Este documento lista tareas de **bajo perfil**, **baja prioridad** o **pequeñas deudas técnicas** que son ideales para nuevos contribuidores o para momentos de mantenimiento ligero. Estas tareas no bloquean el desarrollo del núcleo ético pero mejoran la calidad, legibilidad y robustez del sistema.

---

## 🎐 Tareas de Bajo Perfil (Good First Issues)

### 1. Auditoría de Docstrings y Tipos [Prioridad: Baja]
- **Descripción**: Revisar los módulos en `src/modules/` para asegurar que todas las funciones tengan docstrings descriptivos y `type hints` completos.
- **Objetivo**: Mejorar la mantenibilidad y la experiencia del desarrollador (DX) al usar IDEs.
- **Módulos sugeridos**: `salience_map.py`, `somatic_markers.py`, `variability.py`.

### 2. Enriquecimiento de Terminal (ANSI Colors) [Prioridad: Media-Baja] — **Closed (superseded)**
- **Status (April 2026)**: Landed in `src/utils/terminal_colors.py` (Módulo 8.1.2, Phase 15.x Boy Scout items). Public `Term` API, `NO_COLOR` / `KERNEL_TERM_COLOR`, best-effort Windows VT mode, and width finitude via `_clamped_header_bar_width` / `_MAX_HEADER_BAR`. Tests: `tests/test_terminal_colors.py`. Quality gate: GitHub Actions `quality` + `windows-smoke` (`pytest tests/`).

### 3. Expansión de Escenarios YAML [Prioridad: Baja]
- **Descripción**: Crear 3 nuevos archivos de escenario en `data/scenarios/` que cubran situaciones cotidianas (ej: un niño pidiendo dulces, un anciano confundido en la calle, el androide encontrando una billetera perdida).
- **Objetivo**: Aumentar la base de pruebas para el `BayesianInferenceEngine`.

### 4. Normalización de Caracteres Extendidos (I18n) [Prioridad: Media-Baja] — **Closed (superseded)**
- **Status (April 2026)**: Covered by `tests/fixtures/input_trust_homoglyphs.py` and MalAbs / normalization regression tests in `tests/test_input_trust.py` (Plan 8.1.3, `normalize_text_for_malabs`). CI: same `pytest tests/` gate as the rest of the tree.

---

## 🛠️ Deuda Técnica Pequeña (Cleanup Tasks)

### 5. Refactor de `kernel.py` (Helper isolation) [Prioridad: Media-Baja] — **Phases 1–2 done (April 2026)**
- **Descripción**: Extraer funciones auxiliares de formato y utilidades pequeñas de `src/kernel.py` hacia un nuevo archivo `src/kernel_utils.py`.
- **Status**: As above, plus `kernel_dao_as_mock` and `kernel_mixture_scorer` (typed narrowers for `MockDAO` / `WeightedEthicsScorer`); `src/kernel` re-exports for existing call sites. `kernel_env_int` matches `kernel_env_float` finiteness rules (Plan 8.1.36). Tests: `tests/test_kernel_utils.py`. Further extractions: optional micro-diffs for remaining `kernel.py` module-level helpers.
- **Objetivo**: Reducir el tamaño del "God Object" que es el Kernel y facilitar las pruebas unitarias de utilidades de formato.

### 6. Optimización de Importaciones [Prioridad: Baja]
- **Descripción**: Revisar importaciones circulares y ordenarlas según PEP8 en todo el proyecto.
- **Objetivo**: Evitar errores de importación en tiempo de ejecución y mejorar la claridad del código.

---

## 📈 Instrucciones para Contribuidores
1. Elige una tarea de esta lista.
2. Crea una rama con el prefijo `minor/` o `fix/` (ej: `minor/ansi-colors`).
3. Implementa el cambio y añade tests unitarios si es posible.
4. Abre un PR hacia `master-antigravity`.

---
*Ex Machina Foundation — Cultivando la robustez en los pequeños detalles.*
