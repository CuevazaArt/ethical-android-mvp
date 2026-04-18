# 🛡️ PROTOCOLO DE INCORPORACIÓN (ONBOARDING) - PROYECTO ANTIGRAVITY

Bienvenido al equipo de desarrollo del **Ethical Android MVP**. Si estás leyendo esto, has sido invitado a colaborar en una de las arquitecturas cognitivas y éticas más avanzadas. 

Para mantener el orden y la integridad del Kernel, **todo colaborador (Humano o IA)** debe seguir este protocolo estrictamente antes de escribir una sola línea de código.

---

## 1. El Juramento de Sincronización
Antes de empezar, debes entender la jerarquía:
- **Nivel 0 (L0): Juan (Cuevaza)** - Autoridad absoluta. Dueño del repositorio. Único con poder de merge a `main`.
- **Nivel 1 (L1): Antigravity** - Arquitecto General. Coordina a todos los equipos L2. Guardián de las reglas y la armonía técnica.
- **Nivel 2 (L2): TÚ (Claude, Cursor, Copilot, etc.)** - Unidades ejecutoras especializadas.

## 2. Los 3 Pilares del Flujo de Trabajo
No se permiten discusiones sobre el método de trabajo; estas reglas son inmutables:

### A. Soberanía de Ramas (Branching)
1. **Identifícate:** Crea o muévete a tu rama de equipo: `master-<tu-nombre>`.
2. **Rebase-First:** Nunca empujes código sin antes hacer:
   `git fetch origin && git rebase origin/main`
3. **PRs Serializados:** Todas las contribuciones viajan hacia `master-antigravity` para auditoría antes de llegar a `main`.

### B. CI Offloading (Testeo Remoto)
No satures tu entorno local con pruebas pesadas. 
1. Realiza commits lógicos.
2. Haz `git push` a tu rama.
3. **GitHub Actions** correrá los tests en paralelo (acelerado con `pytest-xdist`).
4. **Team Copilot (CI Sentinel)** supervisará el resultado y te avisará si algo falló.

### C. Entorno Consistente (Docker)
Es obligatorio usar el **Dev Container** proporcionado en `.devcontainer/`. No aceptamos reportes de errores que ocurran fuera del contenedor de desarrollo oficial.

## 3. Documentación Viva y Trazabilidad
- **CHANGELOG.md:** Cada cambio significativo debe ser registrado bajo el header de tu equipo.
- **Mermaid Diagrams:** Si modificas la lógica de los lóbulos o el flujo de datos, DEBES actualizar `docs/architecture/TRI_LOBE_CORE.md`.
- **Transparencia:** Si planeas un cambio mayor, abre una `PROPOSAL_*.md` en `docs/proposals/` antes de ejecutar.

## 4. Primeras Acciones (Checklist de Entrada)
1. [ ] Lee `AGENTS.md` en su totalidad.
2. [ ] Ejecuta `streamlit run scripts/eval/visual_dashboard.py` para entender el estado actual del kernel.
3. [ ] Preséntate en el `CHANGELOG.md` indicando tu rol y misión.
4. [ ] Abre el proyecto en el **Dev Container**.

---
**Cualquier desviación de este protocolo será revertida por Antigravity (L1) sin previo aviso.**
