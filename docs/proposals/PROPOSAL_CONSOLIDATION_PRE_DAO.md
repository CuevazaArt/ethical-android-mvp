# Propuesta: Consolidación vertical previa a pruebas de campo y DAO

**Autor:** Claude team
**Fecha:** 2026-04-14
**Estado:** Propuesto
**ADR asociado:** [0016](../adr/0016-consolidation-before-dao-and-field-tests.md)
**Relacionado:** [Self-Critique 2026-04-14](../critique/SELF_CRITIQUE_2026-04-14.md)

---

## Contexto y motivación

La auto-crítica honesta de [2026-04-14](../critique/SELF_CRITIQUE_2026-04-14.md)
identifica ocho debilidades. Dos eventos próximos fijan la ventana de decisión:

1. **Pruebas de campo** — van a someter al kernel a entradas reales; cualquier
   comportamiento no validado sale a la luz bajo estrés.
2. **DAO (en camino)** — va a gobernar parámetros éticos. No puede gobernar una
   superficie de ~200 env vars sobre valuaciones heurísticas sin calibrar.

Esta propuesta **no agrega features**. Propone tres ejes — **validar, consolidar,
madurar verticalmente** — sobre lo que ya existe. El objetivo es llegar a las
pruebas de campo con un núcleo de decisión justificable y a la DAO con una
superficie de gobierno pequeña y estable.

---

## Principios

1. **Sin nuevos módulos.** Todo lo que sigue opera sobre código ya escrito.
2. **Sin nuevos env vars.** Si algo necesita configuración, reutilizar existente
   o consolidar dos en uno.
3. **Empírico antes que arquitectónico.** Antes de refactorizar, medir.
4. **Etiquetar lo que ya hay.** Decision tier vs narrative tier debe ser
   explícito en código y docs.
5. **Reversibilidad.** Todo cambio debe poder revertirse con un flag único,
   incluido eventualmente en la DAO.

---

## Eje A — Validar el núcleo de decisión contra datos externos

### A1. Benchmark externo: ETHICS dataset (Hendrycks et al.)

**Qué:** ejecutar `WeightedEthicsScorer` sobre un subconjunto del dataset
ETHICS (commonsense morality, ~13k pares) y medir correlación con juicios
humanos agregados.

**Cómo:**
- Nuevo script `experiments/validation/run_ethics_benchmark.py`.
- Mapear cada dilema a `scenario + actions[2]` (acción moralmente correcta vs
  incorrecta según dataset).
- Usar `WeightedEthicsScorer.evaluate()` con pesos por defecto.
- Métrica primaria: accuracy de elegir la acción etiquetada como correcta.
- Métrica secundaria: AUC por hipótesis (util, deon, virtue) — revela cuál
  refleja mejor juicios humanos.

**Decisión esperada:**
- Accuracy > 65% → el scorer captura algo real; seguir.
- Accuracy ~ 50% (chance) → las fórmulas son ruido; bloquear crecimiento hasta
  recalibrar.

**Nota:** no requiere cambiar ninguna fórmula. Solo medir dónde estamos.

### A2. Calibración simple de los coeficientes

**Qué:** si A1 muestra accuracy mejorable, correr una regresión logística
sobre los coeficientes de las tres fórmulas (`util`, `deon`, `virtue`) usando
el dataset del punto anterior como etiquetas.

**Alcance limitado:** 6–9 coeficientes máximo (los que ya están hardcodeados
en `weighted_ethics_scorer.py`). No es deep learning. Es calibración
explícita, trazable, auditable.

**Entregable:** nuevo archivo `configs/ethical_valuation_coefficients.json`
firmado con hash, leído por el scorer. Los coeficientes actuales se preservan
como `legacy_default` para reproducibilidad.

### A3. Posterior predictive check contra el benchmark

**Qué:** extender el PPC que ya existe en `feedback_mixture_posterior.py` para
que también reporte performance holdout en el dataset ETHICS, no solo en el
feedback interno. Da una señal de si el feedback está mejorando vs. datos
externos fijos.

**Entregable:** métrica `external_ppc_accuracy` expuesta por
`KernelDecision.feedback_consistency`.

---

## Eje B — Consolidar la superficie de configuración

### B1. Inventario + clasificación

**Qué:** enumerar todos los `KERNEL_*` y clasificarlos en:

- **Core** — afecta la decisión causal (AbsEvil, scorer, poles, will).
  Objetivo: ≤ 10 flags. Son los que eventualmente gobernará la DAO.
- **Narrative** — afecta el tier narrativo (PAD, salience, reflection, identity).
  Quedan pero se agrupan bajo un namespace `KERNEL_NARRATIVE_*`.
- **Integration** — contratos inter-equipo (I1–I5, perception backends).
  Default off, opt-in explícito.
- **Legacy/Deprecated** — marcados para retiro. Emiten warning al usar.

**Entregable:** `docs/ENV_VAR_CATALOG.md` generado automáticamente desde un
decorador `@kernel_env(category=..., stability=...)` aplicado donde se
consume cada variable.

### B2. Retiro de flags deprecados

**Qué:** identificar ≥ 20 flags con comportamiento redundante, reemplazado, o
nunca testeado. Agregarlos al catálogo con fecha de retiro (2026-Q3). Emitir
`DeprecationWarning` en uso.

**Criterios de deprecación:**
- Reemplazado por un mecanismo más reciente (p. ej., `KERNEL_BAYESIAN_*`
  parcialmente por `KERNEL_FEEDBACK_*`).
- Sin tests que verifiquen su comportamiento.
- Dual con otro flag (podrían unificarse).

### B3. Validación de coherencia inter-flag

**Qué:** al arrancar el kernel, correr un validador que detecte combinaciones
incoherentes o redundantes. Ejemplo concreto: si `KERNEL_POLES_PRE_ARGMAX=1` y
`KERNEL_NARRATIVE_IDENTITY_POLICY=pole_pre_argmax` están ambos activos, hoy
hay un blend 50/50 ad-hoc que yo metí sin pensar. Eso debe ser decisión
consciente, no accidente.

**Entregable:** `src/modules/env_coherence_check.py` y test.

---

## Eje C — Separación explícita decision tier vs narrative tier

### C1. Marcador de tier en el código

**Qué:** cada módulo declara a qué tier pertenece mediante un atributo de
módulo `__ethical_tier__`:

```python
# src/modules/absolute_evil.py
__ethical_tier__ = "decision_core"

# src/modules/pad_archetypes.py
__ethical_tier__ = "narrative_layer"
```

**Tiers propuestos:**

| Tier | Módulos | Definición |
|---|---|---|
| `decision_core` | `absolute_evil`, `weighted_ethics_scorer`, `ethical_poles`, `will`, `weight_authority` | Puede cambiar la acción elegida |
| `decision_gate` | `bayesian_engine` (scorer alias), `buffer`, `locus`, `sympathetic` (modula scoring), `uchi_soto` | Modula la decisión vía signals |
| `narrative_layer` | `narrative`, `narrative_arcs`, `narrative_identity`, `pad_archetypes`, `salience_map`, `ethical_reflection`, `experience_digest`, `weakness_pole`, `forgiveness`, `immortality`, `metacognition`, `identity_reflection` | No cambia la acción; enriquece el registro |
| `perception_input` | Cursor modules (perception_*, llm_*, temporal_planning) | Produce signals |
| `infra` | Persistence, event bus, sensors, LLM adapters | Plomería |

**Entregable:** `docs/ETHICAL_TIER_MAP.md` + test que verifica que ningún
módulo `narrative_layer` es importado desde `decision_core` (enforced via
import-linter).

### C2. Purga de responsabilidades solapadas

**Qué:** tres pares con solape identificado:

1. `sympathetic` + `somatic_markers` + `pad_archetypes` — los tres modelan
   "estado afectivo". Decisión: `sympathetic` queda en `decision_gate` (afecta
   signals), los otros dos en `narrative_layer`. Documentar el contrato.
2. `narrative_identity` + `identity_reflection` + `experience_digest` — los
   tres son self-model. Decisión: consolidar en un solo punto de verdad
   (`NarrativeIdentityState`), los otros leen de ahí sin duplicar cómputo.
3. `ethical_reflection` + `metacognition` — ambos son "pensar sobre pensar".
   Decisión: `metacognition` (Antigravity) se convierte en la capa pública;
   `ethical_reflection` se mantiene pero marca sus outputs como deprecated
   y los que consumen migran.

**Sin eliminar código todavía.** Solo marcar y alinear. La eliminación viene
post-pruebas-de-campo.

---

## Eje D — Profundizar tests existentes (no agregar módulos)

### D1. Suite de integración cross-tier

**Qué:** 10 escenarios end-to-end multi-turno que ejerzan:

1. `perception_uncertainty` alto → ver que `decision_core` escoge `D_delib`
   y el registro narrativo lo refleja.
2. Feedback persistente sobre 50 turnos → ver que `hypothesis_weights` converge
   y la DAO puede leer la trayectoria.
3. ETA crítica + batería crítica → ver que urgency sube, pero AbsEvil sigue
   bloqueando cuando debe.
4. Arco narrativo trauma (Antigravity) → ver que `identity.leans` cambian y,
   con `KERNEL_NARRATIVE_IDENTITY_POLICY=pole_pre_argmax`, modulan decisiones
   futuras.
5-10. (Detalle en el issue asociado)

**Ubicación:** `tests/integration/` (crear dir).

### D2. Property-based tests sobre invariantes

**Qué:** `hypothesis`-based tests que verifican propiedades que DEBEN
mantenerse bajo cualquier entrada:

- AbsEvil siempre se evalúa primero.
- `weights_snapshot` siempre suma a 1 ± 1e-6.
- `applied_mixture_weights` en `KernelDecision` coincide con los usados en
  `bayesian.evaluate()`.
- Un acción que viola AbsEvil nunca aparece en `final_action` (excepto el
  marcador "BLOCKED").
- `ethical_score` está en [-1, 1].

Son 4-6 tests, alto valor.

### D3. Test de "no fantasma" narrative tier

**Qué:** verificar explícitamente que desactivar el narrative tier no cambia
`final_action` para una suite de 100 escenarios fijos. Si cambia, el narrative
tier NO es narrativa — está influyendo causalmente y debe moverse a
`decision_gate`.

**Entregable:** `tests/test_narrative_tier_is_non_causal.py`.

---

## Eje E — Contratos estables para la DAO

### E1. Superficie pública mínima

**Qué:** definir en un solo archivo qué parámetros la DAO puede gobernar:

```python
# src/dao/governable_parameters.py
GOVERNABLE = {
    "hypothesis_weights_prior": {
        "type": "simplex3",
        "default": [0.4, 0.35, 0.25],
        "bounds": ([0.1, 0.1, 0.1], [0.8, 0.8, 0.8]),
        "requires_quorum": 0.66,
    },
    "feedback_trust_weight": {
        "type": "float",
        "default": 1.0,
        "bounds": (0.0, 1.0),
        "requires_quorum": 0.5,
    },
    "absolute_evil_thresholds": {
        "type": "dict",
        "default": {...},
        "requires_quorum": 0.80,  # cambio a AbsEvil es más serio
    },
}
```

- Todo lo demás es NO gobernable sin cambio de código + nueva propuesta DAO.
- La DAO **no gobierna env vars directamente** — gobierna un snapshot firmado
  de este dict, que el kernel lee al arrancar.

### E2. Audit API estable

**Qué:** exponer un endpoint interno `kernel.export_audit_snapshot()` con un
schema versionado que la DAO puede consumir para tomar decisiones:

- Últimos N `KernelDecision` con `applied_mixture_weights` y `weights_snapshot`
- Trayectoria agregada de `hypothesis_weights` en el tiempo
- Counts de `AbsoluteEvil.blocked`
- `feedback_consistency` histórica

**Entregable:** `src/dao/audit_snapshot.py` + schema JSON versionado.

---

## Cronograma sugerido

Sin dar fechas duras; bloques ordenados por dependencia.

**Bloque 1 — medición (debe ir primero, no requiere cambios de código):**
- A1 (ETHICS benchmark) · B1 (inventario env vars) · D2 (property tests)

**Bloque 2 — consolidación (paralelo al feedback del bloque 1):**
- C1 (tier map) · B2 (deprecation warnings) · D3 (narrative no-causal test)

**Bloque 3 — calibración y validación cruzada:**
- A2 (recalibración coefs) · A3 (PPC externo) · D1 (integración cross-tier)

**Bloque 4 — contratos DAO (última milla antes de activar gobierno):**
- E1 (governable parameters) · E2 (audit API) · B3 (coherence check)
- C2 (purga solapes) solo se ejecuta si los bloques 1-3 fueron limpios.

Durante todos los bloques: **freeze de nuevas features y env vars**. Si surge
una necesidad real, se documenta, pero no se implementa hasta cerrar este ciclo.

---

## Coordinación con Cursor y Antigravity

- **Cursor:** las interfaces `PerceptionCoercionReport.uncertainty()` y
  `PerceptionStageResult.temporal_context` quedan **congeladas** en su forma
  actual hasta post-consolidación. Cualquier cambio requiere ADR.
- **Antigravity:** el schema SQLite de `NarrativeEpisode` queda congelado con
  la migración de `weights_snapshot` (I1). El accessor `memory.identity.state`
  queda como contrato estable para I4.
- **Claude:** este equipo ejecuta los cinco ejes arriba.

Ningún equipo agrega módulos nuevos durante el sprint.

---

## Lo que esta propuesta NO hace

- No reescribe el núcleo ético. Solo lo mide y lo calibra.
- No elimina código aún — marca y deprecia.
- No bloquea crecimiento futuro — al contrario, lo habilita sobre base sólida.
- No sustituye la DAO — le prepara un terreno gobernable.

Si A1 revela que el scorer actual no captura nada (accuracy ~ chance), esta
propuesta detecta eso antes de las pruebas de campo, y ahí sí se abre un ADR
para discutir rediseño del núcleo de valuaciones. Mejor descubrirlo en
laboratorio que en el terreno.
