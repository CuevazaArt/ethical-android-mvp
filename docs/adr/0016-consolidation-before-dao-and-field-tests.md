# ADR 0016 — Consolidación previa a pruebas de campo y DAO

**Fecha:** 2026-04-14
**Estado:** Aceptado
**Equipo:** Claude (proponente) | Afecta: Antigravity, Cursor, futura DAO
**Relacionado:**
- [Self-Critique 2026-04-14](../critique/SELF_CRITIQUE_2026-04-14.md)
- [PROPOSAL_CONSOLIDATION_PRE_DAO](../proposals/PROPOSAL_CONSOLIDATION_PRE_DAO.md)

---

## Contexto

Tras cerrar los sprints P1–P7 (Bayesian kernel) e I1–I5 (integración
inter-equipos), una auto-crítica honesta identifica ocho debilidades
estructurales del proyecto. Dos de ellas son críticas frente a los dos
eventos próximos:

1. **Pruebas de campo** — el kernel va a recibir entradas reales; las
   debilidades no validadas se manifestarán bajo estrés.
2. **Llegada de la DAO** — un órgano de gobierno colectivo no puede gobernar
   una superficie de ~200 env vars sobre un scorer no validado.

Las debilidades no son bugs. Son deudas de validación y consolidación que
acumulamos mientras ganábamos capacidad. La decisión es saldarlas antes de
crecer más.

## Decisión

Entrar en un **ciclo de consolidación vertical** (sin nuevos módulos, sin
nuevos env vars, sin nuevas features) enfocado en cinco ejes:

- **Eje A — Validar** el núcleo de decisión contra datos externos (ETHICS
  dataset, calibración de coeficientes, PPC externo).
- **Eje B — Consolidar** la superficie de configuración (inventario,
  deprecation, validación de coherencia).
- **Eje C — Separar** explícitamente *decision tier* vs *narrative tier*
  (marcadores de tier, import-linter, purga de solapes).
- **Eje D — Profundizar** los tests existentes (integración cross-tier,
  property-based sobre invariantes, test de "no-fantasma" narrativo).
- **Eje E — Contratar** la superficie gobernable por la DAO (parámetros
  explícitos, audit API estable).

El detalle operativo está en
[PROPOSAL_CONSOLIDATION_PRE_DAO.md](../proposals/PROPOSAL_CONSOLIDATION_PRE_DAO.md).

## Reglas durante este ciclo

1. **Sin nuevos módulos** en `src/modules/` salvo los explícitamente listados
   en la propuesta (`env_coherence_check`, `dao/governable_parameters`,
   `dao/audit_snapshot`).
2. **Sin nuevos env vars.** Si algo requiere configuración, reutilizar o
   consolidar dos existentes en uno.
3. **Sin eliminar código** — solo deprecar con warning y fecha de retiro.
4. **Freeze de interfaces inter-equipo** (contratos I1–I5, `PerceptionCoercionReport`,
   `NarrativeIdentityState`, schema SQLite de `NarrativeEpisode`). Cambios
   requieren ADR nuevo.
5. **Empírico antes que arquitectónico.** Medir (Eje A) antes de refactorizar
   (Eje C).

## Qué este ADR NO cambia

- La arquitectura del pipeline `process()` sigue igual.
- Los sprints P1–P7 e I1–I5 no se revierten.
- La DAO sigue viniendo — este ADR le prepara un terreno gobernable.
- El núcleo ético (AbsEvil, scorer, poles, will) no se reescribe. Se mide y
  se calibra.

## Criterios de cierre

El ciclo cierra cuando todas las siguientes condiciones se cumplen:

- [ ] Benchmark ETHICS ejecutado, resultado documentado (pasa o no pasa, el
  dato público).
- [ ] Catálogo de env vars publicado (`docs/ENV_VAR_CATALOG.md`), con al menos
  20 flags marcados como deprecated.
- [ ] Mapa de tiers publicado (`docs/ETHICAL_TIER_MAP.md`) + test que enforce
  que `narrative_layer` no importa desde `decision_core`.
- [ ] Suite de integración cross-tier en `tests/integration/` con ≥ 10
  escenarios end-to-end.
- [ ] Property tests sobre invariantes del kernel.
- [ ] Test de no-causalidad del narrative tier.
- [ ] `src/dao/governable_parameters.py` definido y firmado.
- [ ] `kernel.export_audit_snapshot()` implementado y versionado.

## Consecuencias

**Positivas:**
1. Base empírica para las pruebas de campo: sabemos qué está validado y qué
   no, antes de exponerlo a entradas reales.
2. Superficie de gobierno manejable para la DAO: ≤ 10 parámetros core en vez
   de ~200 flags.
3. Contratos inter-equipo estables y documentados; Cursor y Antigravity
   pueden seguir trabajando sobre fundamentos fijos.
4. Tests que detectan regresiones cross-tier y violaciones de invariantes,
   no solo regresiones unitarias.

**Negativas / aceptadas:**
1. Un ciclo sin features visibles. Si el benchmark muestra que el scorer no
   captura señal, habrá que abrir rediseño del núcleo — mejor ahora que en
   campo.
2. Deprecation de flags va a generar warnings en runtimes externos; es
   intencional.
3. Congelar interfaces inter-equipo limita temporalmente la exploración
   arquitectónica — es el precio de la estabilidad pre-DAO.

## Riesgos

- **A1 resulta negativo:** el scorer actual no predice juicios humanos. Es un
  descubrimiento, no un fracaso. Se abre ADR para discutir rediseño antes de
  campo.
- **Calibración A2 sobreajusta al dataset:** mitigado con holdout y PPC
  externo. Si el holdout no generaliza, mantenemos coefs originales y
  documentamos el límite.
- **La DAO llega antes del cierre:** los bloques son independientes; los
  contratos del Eje E pueden entregarse primero si hace falta, a costa de
  gobernar sin calibración externa (aceptable, recuperable).
