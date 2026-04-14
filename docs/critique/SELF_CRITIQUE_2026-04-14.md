# Self-Critique — 2026-04-14

**Autor:** Claude team (solicitado explícitamente por el maintainer)
**Alcance:** revisión honesta de todo el repo post sprints P1–P7 + I1–I5.
**Propósito:** fijar por escrito lo que sabemos que está mal o sin justificar, para
que el plan de consolidación pre-DAO y pre-pruebas-de-campo ataque lo correcto.
Este documento no es autocomplaciente: prefiere errar por severidad.

---

## 1. Lo que está genuinamente bien

1. **Fusible ético explícito** — `absolute_evil.py` como gate duro antes de cualquier
   scoring. Orden correcto en `kernel.process()`: AbsEvil siempre primero sobre todas
   las acciones candidatas; si todas caen, se bloquea. Patrón correcto.
2. **Composición modular limpia** — `KernelComponentOverrides` + DI permite
   mockear piezas aisladas; los tests se apoyan en esto extensivamente.
3. **Documentación honesta de ADRs** — `ADR 0009` admite que "Bayesian" era un
   nombre incorrecto y lo renombra a "mixture scorer". Es raro y valioso ver ese
   nivel de autocrítica en un proyecto.
4. **Audit trail completo** — `KernelDecision` captura casi todo el estado.
   Tras P1/I1 también captura `applied_mixture_weights` y `weights_snapshot`, y
   tras I2 los cambios de peso se emiten al bus. La reproducibilidad post-hoc es
   posible.
5. **Separación entrada / decisión / archivo** — la arquitectura multi-equipo
   (Cursor perception → Claude decision → Antigravity narrative) tiene una
   frontera conceptual clara. Cursor y Antigravity están maduros en sus capas.

## 2. Lo que está genuinamente mal

### 2.1 El modelo ético del núcleo no está fundamentado

`weighted_ethics_scorer.py` calcula las valuaciones útiles/deontológica/virtud con
fórmulas inventadas:

```
util   = base * stake
deon   = 0.68 * base + 0.09 - 0.45 * force
virtue = 0.84 * base + ...
```

Ninguna de estas constantes viene de literatura, de calibración empírica, ni de
juicios humanos etiquetados. Los pesos por defecto `[0.4, 0.35, 0.25]` son
*design hyperparameters* disfrazados de prior. La **ontología** de tres
hipótesis éticas es defendible; las **fórmulas específicas** no lo son. Este
es el nudo real del proyecto: el modelo no es necesariamente *incorrecto*, pero
**no está justificado**, y todo lo que construimos encima hereda esa
indeterminación.

### 2.2 "Bayesian" sigue siendo parcialmente cosmético

Los sprints recientes (weight authority stack, feedback mixture posterior,
posterior predictive check, calibración de beta) sí añaden inferencia real
sobre los pesos de la mezcla. Pero esa inferencia opera **encima de valuaciones
heurísticas sin calibrar**. Es inferencia Bayesiana sobre una función de
verosimilitud inventada. El beneficio marginal es limitado hasta que las
valuaciones base se calibren contra datos externos.

### 2.3 Explosión de configuración (~200 env vars `KERNEL_*`)

Cada sprint agrega 2–5 flags nuevos que nunca se retiran. Hoy mismo agregamos
tres más (`KERNEL_NARRATIVE_IDENTITY_POLICY`, `KERNEL_TEMPORAL_ETA_MODULATION`,
`KERNEL_TEMPORAL_REFERENCE_ETA_S`). Consecuencias:

- La matriz combinatoria es ingobernable; no testeamos ni una fracción.
- No hay validación de coherencia inter-flag (p. ej., ¿qué pasa si
  `KERNEL_POLES_PRE_ARGMAX=1` y `KERNEL_NARRATIVE_IDENTITY_POLICY=pole_pre_argmax`
  simultáneamente? Hay una blend ad-hoc que nadie decidió conscientemente).
- Un operador en producción tiene una superficie de error masiva.
- Cuando llegue la DAO a gobernar parámetros, no puede gobernar ~200 flags.
  Necesita un set pequeño y estable.

### 2.4 Capa narrativa sobredimensionada respecto a su influencia causal

El proyecto se vende como "ethics by architecture", pero la arquitectura ética
real son ~4 módulos (`absolute_evil`, `weighted_ethics_scorer`, `ethical_poles`,
`will`). Todo lo demás — PAD archetypes, reflection, salience, weakness pole,
forgiveness, immortality, narrative identity, experience digest, somatic
markers — **no modifica la decisión**. Son post-hoc. Muy elaborados, bien
implementados, pero no son *ética causal*, son *narrativa sobre la ética*.

Esto no es necesariamente malo — pero debe **etiquetarse explícitamente** como
"narrative tier" separado del "decision tier". Hoy están mezclados y eso
confunde qué parte del sistema hay que validar.

### 2.5 Tests anchos pero superficiales

688 funciones de test, pero dominan:

- Unit tests aislados con `monkeypatch` para env y mocks para sensores/LLM.
- Snapshots y assertions puntuales (`assert decision.final_action == "X"`).
- Pocos escenarios end-to-end multi-turno con retroalimentación real
  `memory → weights → decisión → memory`.

Los sprints I1–I5 que acabamos de mergear validan cada mecanismo aislado, no el
comportamiento acoplado. Riesgo alto de regresiones cross-module invisibles.

### 2.6 Overlap conceptual sin resolver

- `ethical_poles` y `weighted_ethics_scorer` puntúan independientemente; ambos
  resultados van al `KernelDecision`. ¿Cuál manda para la acción final? El
  `bayes_result.chosen_action`. Pero `moral.total_score` se presenta al usuario.
  No hay función objetivo unificada.
- `sympathetic`, `somatic_markers`, `pad_archetypes` solapan en "estado afectivo".
- `identity_integrity`, `narrative_identity`, `experience_digest` solapan en
  "self-model".

Cada módulo resuelve un 20% de un problema adyacente. Esto se va a volver
intratable en la próxima iteración.

### 2.7 No hay aprendizaje cerrado real

El feedback ajusta los *pesos de la mezcla* sobre valuaciones fijas. Las
valuaciones *base* no aprenden nada. El sistema no mejora su razonamiento
ético; retuerce un hiperparámetro de 3 dimensiones dentro de una estructura
rígida. Para un MVP está bien; para un agente ético en el mundo real, no basta.

### 2.8 "Multi-team" es en parte ficción narrativa

Revisamos commits: todos con el mismo autor (`CuevazaArt`, `Cuevaza`). Las
ramas `master-antigravity`, `master-Cursor`, `master-claude` son **roles o
perspectivas de trabajo de un solo autor**, no equipos independientes. Las
ramas `claude/*` corresponden a sesiones/agentes distintas coordinadas por el
mismo maintainer.

Esto no es malo per se — es una técnica de trabajo legítima y disciplinada
(modularizar responsabilidades en ramas). Pero los docs presentan "coordinación
inter-equipos" como si hubiera equipos humanos distintos, y eso genera una
expectativa incorrecta en lectores externos (y eventualmente en la DAO).

## 3. Lo que los otros "equipos" aportaron (y cómo encaja con la crítica)

### Antigravity (`master-antigravity`, +1732 LOC)

Madurez del tier narrativo:
- `narrative_arcs`: agrupación de episodios por arco, shock/trauma, resonancia
- `narrative_storage` (SQLite): persistencia tier 2/3 con migraciones
- `metacognition`, `identity_reflection`, `narrative_identity` enriquecido
- `psi_sleep` con pruning automático por significance
- `immortality` integrado con archetypes y arcs

**Encaja con la crítica:** valida el punto 2.4. Antigravity es el tier
narrativo robusto. El problema no es que esté mal hecho — está bien hecho. El
problema es que no lo etiquetamos como tier separado y no shaping la decisión.

### Cursor (`master-Cursor`, +9589 LOC)

Hardening de percepción:
- `perception_backend_policy`: políticas de degradación para LLM
- `llm_touchpoint_policies`: precedencia configurable
- `llm_verbal_backend_policy`: degradación verbal/narración
- `perception_coercion_report`: reporte de (un)certainty por JSON parse,
  dual-vote, LLM-degradation
- `temporal_planning`: ETA, battery horizon, context

**Encaja con la crítica:** Cursor hace exactamente lo que debe — dar señales
*honestas* al núcleo, incluyendo "no confío en mi percepción". El I3/I5 que
acabamos de mergear conecta eso al scorer. Lo que Cursor NO puede arreglar es
que el scorer, al recibir esas señales, las combine con fórmulas inventadas.

## 4. Diagnóstico consolidado

Es un prototipo de investigación **bien ingenierado sobre una síntesis
personal de ética**. Ni más, ni menos.

- Como ejercicio de software: sólido.
- Como modelo ético: **no validado contra nada externo**. No hay corpus de
  juicios humanos, no hay benchmarks éticos estándar (ETHICS dataset, Moral
  Machine, etc.), no hay evaluación por jueces humanos sistemática.
- Como MVP: razonable. Los MVPs pueden ser síntesis personales.
- Como base para una DAO que gobierne parámetros éticos: **no está listo**.
  Gobernar 200 env vars sobre un scorer no validado es gobernar ruido.

## 5. Lo que esta crítica NO dice

- No dice que el código esté mal escrito. Está bien escrito.
- No dice que los "equipos" sean un engaño — son una práctica de trabajo.
- No dice que los sprints P1–P7 e I1–I5 hayan sido tiempo perdido — mejoraron
  observabilidad, persistencia, y cierran gaps inter-capa. Pero trabajaron
  sobre la capa de inferencia, no sobre la capa de valuación.
- No dice que haya que reescribir. Dice que hay que **validar, consolidar, y
  congelar** antes de crecer más.

---

El plan de acción está en
[`PROPOSAL_CONSOLIDATION_PRE_DAO.md`](../proposals/PROPOSAL_CONSOLIDATION_PRE_DAO.md)
y en el [ADR 0016](../adr/0016-consolidation-before-dao-and-field-tests.md).
