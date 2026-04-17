# Antigravity Team: Guía de Colaboración y Hitos

Este documento consolida la metodología de trabajo para el equipo Antigravity y proporciona referencias clave para mantener el orden y la trazabilidad en el desarrollo del Ethos Kernel.

## 📌 Protocolo de Colaboración

Para asegurar la integridad del kernel y la sincronización entre oficinas (Local/Dellware), todos los colaboradores (humanos y agentes) deben seguir este flujo:

1.  **Read First:** Antes de cualquier cambio, es obligatorio revisar:
    *   **[`AGENTS.md`](AGENTS.md):** El punto de entrada para entender la arquitectura y las prioridades actuales.
    *   **[`CONTRIBUTING.md`](CONTRIBUTING.md):** Reglas de lenguaje (Inglés para repo, Español para comunicación si procede), tests y trazabilidad.
    *   **[`.cursor/rules/`](.cursor/rules/):** Guías de estilo siempre activas para el asistente.

2.  **Rama de Trabajo:**
    *   Desarrollo local: `antigravity-team`.
    *   Integración de equipo: `master-antigravity`.
    *   Merge final: Hacia `main` solo tras validación completa del equipo.

3.  **Trazabilidad Ética:** Toda modificación en seguridad o lógica ética debe documentarse en `docs/proposals/` y reflejarse en el `CHANGELOG.md`.

## 🚀 Estado de la Arquitectura Narrativa

| Tier | Estado | Descripción |
| :--- | :--- | :--- |
| **Tier 1 (Ephemeral)** | ✅ Consolidado | Memoria a corto plazo funcional. |
| **Tier 2 (Persistent)**| ✅ Consolidado | Almacenamiento SQLite con búsqueda por Resonancia PAD. |
| **Tier 3 (Identity)**   | ✅ Consolidado | Consolidación de episodios en lecciones existenciales e Identidad Narrativa. |
| **Tier 4 (Executive)**  | ✅ Consolidado | Estratega Ejecutivo y Gestión de Misiones (Internas/Externas). |
| **Integración I1-I7**  | 🏗️ En curso   | Sincronización con equipos Claude (Bayesian) y Cursor (Sensors). |

## 🛠️ Herramientas de Calidad
*   **Tests:** Ejecutar `python -m pytest tests/` antes de cada push. El suite debe estar 100% verde.
*   **Aislamiento:** El entorno de test usa archivos SQLite temporales automáticos para evitar contaminación de datos.

---
> [!IMPORTANT]
> **No placeholders**. Implementar lógica funcional y tests unitarios para cada avance. La estética del código y la documentación son tan críticas como la funcionalidad.
