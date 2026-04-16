# Distribución de Trabajo de Equipos (Sprint Abril 2026)

**Propósito:** Organizar y distribuir el backlog crítico (P0 y P1) definido en `CRITIQUE_ROADMAP_ISSUES.md` y `PLAN_IMMEDIATE_TWO_WEEKS.md` entre los equipos activos (Antigravity, Claude, Cursor). Esto permite paralelizar el desarrollo manteniendo la integridad estructural del código a través de las ramas de integración (`master-antigravity`, `master-claude`, `master-cursor`).

---

## 1. Equipo Antigravity (En ejecución actual)
**Foco:** Ciberseguridad, validación rigurosa de entradas y robustez adversarial.
**Rama de Integración:** `master-antigravity`

- **Issue #2 (P0) - Confianza de entrada LLM (Defensa en profundidad):**
  - Ejecutar endurecimiento de validación semántica y barreras léxicas (`src/modules/absolute_evil.py` y `src/modules/input_trust.py`).
  - Expandir pruebas en `tests/adversarial_inputs.py` contra técnicas de evasión (homoglifos, leetspeak, inyección rápida).
  - Implementación de la matriz de degradación de inputs.
- **Issue #7 (P1) - Validaciones de entorno (`KERNEL_*` Combinatorics):**
  - Mantenimiento estricto del pipeline CI y consolidación de banderas en entornos compartidos.

---

## 2. Equipo Claude (Bloque Propuesto)
**Foco:** Inferencia Bayesiana, alineación teórica y gobernanza.
**Rama de Integración:** `master-claude`

- **Issue #1 (P0) - Honestidad de Nomenclatura Bayesiana vs Actualización Mínima:**
  - Ejecutar los lineamientos de `CLAUDE_TEAM_PLAYBOOK_REAL_BAYESIAN_INFERENCE.md`.
  - Definir e implementar el renombrado de `BayesianEngine` o implementar una capa matemática real testeada de Bayes.
- **Issue #6 (P0) - MockDAO y Honestidad del Nivel 0 (L0):**
  - Finalizar checklists de operadores para el checkpoint definido en `GOVERNANCE_MOCKDAO_AND_L0.md`.
  - Implementar mecanismos transparentes para evidenciar que `PreloadedBuffer` (L0) es inmutable en runtime frente a falsas promesas DAO.

---

## 3. Equipo Cursor (Bloque Propuesto)
**Foco:** Arquitectura de sensores, empaquetado del núcleo y escenarios empíricos.
**Rama de Integración:** `master-cursor`

- **Issue #3 (P1) - Piloto Empírico y Escenarios Métrica:**
  - Ejecutar según `CURSOR_TEAM_MISSION_SENSORS_PERCEPTION.md`.
  - Extensión de la base de escenarios etiquetados en `tests/fixtures/labeled_scenarios.json`.
  - Ejecución de las comparativas de líneas base a través de `scripts/run_empirical_pilot.py`.
- **Issue #4 (P1) - Empaquetado del Cadena Transparente (Core Decision Chain):**
  - Segmentar explícitamente `ethos-core` de las extensiones secundarias.
  - Actualizaciones en documentación técnica sobre las fronteras de importación.
- **Issue #5 (P2) - Heurísticas PAD / Debilidad y Confianza Operativa (HCI):**
  - Calibración de perfiles operativos cuando la "debilidad humana simulada" reduzca la confiabilidad en modos críticos.

---

## Mecanismo de Sincronización
Todos los equipos deberán operar sus desarrollos en sus ramas `master-<equipo>`. Cada avance debe ser validado con `pytest tests/ -v`, formatiado por ruff (`python -m ruff check src tests`) y evidenciado con sus respectivos `PROPOSAL_*.md` antes del pull request a `main`.
