# Backlog de Contribuciones Menores y Deuda Técnica (Minor Contributions)

Este documento lista tareas de **bajo perfil**, **baja prioridad** o **pequeñas deudas técnicas** que son ideales para nuevos contribuidores o para momentos de mantenimiento ligero. Estas tareas no bloquean el desarrollo del núcleo ético pero mejoran la calidad, legibilidad y robustez del sistema.

---

## 🎐 Tareas de Bajo Perfil (Good First Issues)

### 1. Auditoría de Docstrings y Tipos [Prioridad: Baja]
- **Descripción**: Revisar los módulos en `src/modules/` para asegurar que todas las funciones tengan docstrings descriptivos y `type hints` completos.
- **Objetivo**: Mejorar la mantenibilidad y la experiencia del desarrollador (DX) al usar IDEs.
- **Módulos sugeridos**: `salience_map.py`, `somatic_markers.py`, `variability.py`.

### 2. Enriquecimiento de Terminal (ANSI Colors) [Prioridad: Media-Baja]
- **Descripción**: Implementar una utilidad de coloreado ANSI para los logs de la consola en `kernel.py`.
- **Objetivo**: Hacer que la salida del `format_decision` sea visualmente escaneable (ej: ⛔ en rojo, ✅ en verde, estados PAD en colores suaves).
- **Referencia**: `src/observability/logging_view.py` (si existe) o crear `src/utils/terminal_colors.py`.

### 3. Expansión de Escenarios YAML [Prioridad: Baja]
- **Descripción**: Crear 3 nuevos archivos de escenario en `data/scenarios/` que cubran situaciones cotidianas (ej: un niño pidiendo dulces, un anciano confundido en la calle, el androide encontrando una billetera perdida).
- **Objetivo**: Aumentar la base de pruebas para el `BayesianInferenceEngine`.

### 4. Normalización de Caracteres Extendidos (I18n) [Prioridad: Media-Baja] — **entregado en árbol (Issue #2)**
- **Estado:** Cobertura homoglyphs / Cirílico / Griego en [`tests/test_input_trust.py`](../../tests/test_input_trust.py); ver [`CHANGELOG.md`](../../CHANGELOG.md) (Input trust / MalAbs homoglyphs).
- **Objetivo original:** Que `AbsoluteEvilDetector` normalice confusables antes del matching (sigue siendo el criterio de revisión).

### 5. Pista Team Copilot (Módulo 8 / 10.4) — referencia rápida
- **Prefetch MER:** [`src/modules/turn_prefetcher.py`](../../src/modules/turn_prefetcher.py) — frases puente heurísticas + opción `OLLAMA_PREFETCH_MODEL` con `OLLAMA_BASE_URL` (micro-LLM local &lt;300ms).
- **Delegaciones históricas:** [`COPILOT_REQUEST_IDLE_SHIFT.md`](COPILOT_REQUEST_IDLE_SHIFT.md), [`COPILOT_REQUEST_EXECUTIVE_REFACTOR.md`](COPILOT_REQUEST_EXECUTIVE_REFACTOR.md) (gran parte del lóbulo ejecutivo ya vive en [`src/kernel_lobes/executive_lobe.py`](../../src/kernel_lobes/executive_lobe.py) y el kernel lo instancia).
- **Tests:** [`tests/test_turn_prefetcher.py`](../../tests/test_turn_prefetcher.py).

---

## 🛠️ Deuda Técnica Pequeña (Cleanup Tasks)

### 6. Refactor de `kernel.py` (Helper isolation) [Prioridad: Media-Baja]
- **Descripción**: Extraer funciones auxiliares de formato y utilidades pequeñas de `src/kernel.py` hacia un nuevo archivo `src/kernel_utils.py`.
- **Objetivo**: Reducir el tamaño del "God Object" que es el Kernel y facilitar las pruebas unitarias de utilidades de formato.

### 7. Optimización de Importaciones [Prioridad: Baja]
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
