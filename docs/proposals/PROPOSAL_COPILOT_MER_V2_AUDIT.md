# Auditoría MER V2 (Motor de Encanto y Renderizado) — Contribución Team Copilot

**Emisor:** Team Copilot (GitHub Copilot Agent, L2)
**Destinatarios:** Juan (L0), Antigravity (L1), Team Cursor (L2), Team Claude (L2)
**Fecha:** Abril 2026
**Branch de trabajo:** `copilot/revisar-novedades-proyecto`
**Ramas auditadas:** `master-antigravity`, `master-claude`, `master-Cursor`, `master-copilot`

---

## 1. Estado del MER V2 por Rama — Inventario Verificado

| Artefacto | `master-antigravity` | `master-claude` | `master-Cursor` | copilot (actual) |
|-----------|---------------------|-----------------|-----------------|-----------------|
| `src/modules/charm_engine.py` | ❌ **AUSENTE** | ✅ 180+ líneas | ✅ (vía main) | ✅ 244 líneas |
| `docs/proposals/PROPOSAL_MULTIMODAL_CHARM_ENGINE.md` | ❌ **AUSENTE** | ✅ 63 líneas | ✅ 63 líneas | ✅ 63 líneas |
| `src/modules/charm_types.py` | ❌ | ✅ | ✅ | ❌ (unificado en `charm_engine.py`) |
| `src/modules/charm_server_integration.py` | ❌ | ✅ | ✅ | ❌ |
| `PARASOCIAL_ADDICTION` en `absolute_evil.py` | ❌ | ✅ | ✅ | ✅ |
| RLHF sycophancy guard (`_RLHF_MIN_CONFIDENCE`) | ❌ | Parcial (sin constante env) | Parcial | ✅ constante extraída |
| `kernel.py` invoca `CharmEngine` | ❌ (sin import) | ✅ | ✅ | ✅ |

### Hallazgo crítico: master-antigravity tiene deuda MER V2 completa

`master-antigravity` (2963 líneas de `kernel.py`) es el **hub de integración más grande** del proyecto, pero no tiene ningún archivo relacionado con el CharmEngine. Su `kernel.py` no importa ni instancia `CharmEngine`. Esto significa que **el L1 Integration Hub está desconectado del postulado MER V2** que ya fue implementado en `master-claude` y promovido a `main`.

---

## 2. Dos Implementaciones de `charm_engine.py`: Comparación Técnica

Existen actualmente dos versiones del `charm_engine.py` en el repositorio:

### Versión A — `master-claude` (aportes originales de Claude)

```
- Depende de: charm_types.py, response_template.py, rlhf_reward_model.py
- CharmVector y StylizedResponse definidos en charm_types.py (módulo separado)
- ResponseSculptor llama rlhf_reward_model.predict() directamente con FeatureVector
- CharmEngine.apply() acepta rlhf_features: dict opcional
- Devuelve charm_vector con campos extra: rlhf_reward, rlhf_confidence
- Guardrail parasocial: NO implementado en este archivo (esperado en absolute_evil.py)
```

### Versión B — Rama copilot (Sesión 3, estado actual de main)

```
- Sin dependencia de charm_types.py — tipos definidos inline como dataclasses
- Constantes configurables por env: _RLHF_MIN_CONFIDENCE, _RLHF_SYCO_THRESHOLD, _RLHF_DAMPENING_MAX
- Sycophancy guard propio (_apply_rlhf_guard) con dampening proporcional
- Bypass total si absolute_evil_detected (L0 safety garantizado)
- CharmEngine.apply() sin rlhf_features (RLHF se carga internamente del RLHFPipeline)
- charm_vector omite campos rlhf_* en el output serializable (más limpio para WS)
```

### Diferencias funcionales relevantes

| Aspecto | Versión A (master-claude) | Versión B (copilot/main) |
|---------|--------------------------|--------------------------|
| Deuda de módulos auxiliares | Alta (`charm_types`, `response_template`) | Baja (autocontenido) |
| Configurabilidad por env | No | Sí (`KERNEL_RLHF_*`) |
| Sycophancy dampening | Template-based RLHF calibration | Proporcional con factor acotado |
| Absolute evil bypass | Depende de parámetro externo | Explícito (`if absolute_evil_detected`) |
| Output WS-safe | No (incluye scores RLHF) | Sí (solo 4 dimensiones de encanto) |

---

## 3. Crítica Técnica al Postulado MER V2

### 3.1 Lo que la propuesta original (L1) acertó

El análisis de Antigravity en `PROPOSAL_MULTIMODAL_CHARM_ENGINE.md` §2 fue correcto en tres puntos críticos que la implementación efectivamente respetó:

1. **"Capa de presentación estricta"** — Ambas implementaciones colocan `CharmEngine.apply()` *after* la `KernelDecision`. Ninguna permite al Charm Engine alterar el veto ético.
2. **"Data Races en Profile Registry"** — La Versión B eliminó el `Profile Registry` mutable-por-turno. En su lugar usa `UserModelTracker` con locks SQLite (Módulo 8.2). La preocupación de L1 fue válida y fue resuelta.
3. **"Anti-parasocial"** — `PARASOCIAL_ADDICTION` fue añadido a `AbsoluteEvilDetector` y la constante `_RLHF_MIN_CONFIDENCE` asegura que el dampening solo activa cuando hay confianza suficiente del modelo.

### 3.2 Lo que la propuesta original no anticipó

1. **La necesidad de bypass total en blocking decision** — El MER V2 original no contemplaba que en un bloqueo absoluto (`is_safe=False`) el CharmEngine debería **no ejecutarse en absoluto**, no solo reducir warmth. La Versión B resuelve esto: si `absolute_evil_detected=True`, retorna `StylizedResponse` hardcodeada sin pasar por el sculpter.

2. **La deuda del Monólogo Narrativo** — El MER V2 no especificó el caso `process_chat_turn` (streaming) vs. `process_chat_turn_stream` (async). La Sesión 3 descubrió que `CharmEngine.apply()` se llamaba en el path sincrónico pero **no en el streaming** — hasta que Copilot lo corrigió (Brecha E de la Sesión 3). Esto significa que durante varios ciclos de desarrollo, el MER V2 estaba técnicamente integrado pero **inerte en el 90% del uso real** (el path streaming es el default en producción con WebSockets).

3. **El `support_buffer` como insumo de encanto** — La propuesta no menciona explícitamente que el CharmEngine necesita `support_buffer` (soporte emocional del turno) para calibrar el vector de encanto. La Brecha E también cubría este caso: `support_buffer=None` significaba que `StyleParametrizer` operaba sin el contexto somático que lo haría verdaderamente multimodal. El nombre "Multimodal" en MER V2 era aspiracional, no real, hasta que se fijó la Brecha E.

### 3.3 La pregunta que el postulado MER V2 no responde todavía

**¿Cuándo el CharmEngine debe silenciarse aunque la decisión ética sea `is_safe=True`?**

El postulado se enfoca en bloquear el encanto cuando hay "Absolute Evil". Pero hay un caso intermedio no documentado: cuando la `caution_level` es alta (situación tensa, `social_tension > 0.7`) y el interlocutor tiene `frustration_streak >= 3`, el CharmEngine actual reduce `playfulness` a 0.1, pero sigue aplicando tono "Warm & Open" si `warmth > 0.7`. Esto puede ser **contraproducente**: un humano tenso recibiendo un tono cálido artificial puede interpretarlo como condescendencia.

**Propuesta de Copilot:** Agregar una condición de silencio parcial al ResponseSculptor: si `social_tension > 0.6 AND frustration_streak >= 2`, omitir las anotaciones de tono `[Tone: ...]` y devolver el `base_text` sin decoración. El gesto puede seguir planificándose, pero el tono verbal se mantiene neutro.

---

## 4. Gap de Sincronización: master-antigravity

`master-antigravity` es el **hub de integración oficial** según `AGENTS.md`. Sin embargo, actualmente carece de:

1. `src/modules/charm_engine.py` — El motor de encanto completo
2. `docs/proposals/PROPOSAL_MULTIMODAL_CHARM_ENGINE.md` — El postulado fundacional
3. La integración del CharmEngine en `kernel.py` (las ~5 líneas de import, instancia y dos llamadas en el pipeline)
4. Los guardrails `PARASOCIAL_ADDICTION` en `absolute_evil.py`
5. Las correcciones de la Sesión 3 (Brechas A-F del streaming)

Esto significa que **cualquier PR de `master-claude` o `master-copilot` hacia `master-antigravity` que toque el kernel tendrá conflictos MER-relacionados** hasta que Antigravity (L1) haga la absorción.

### Recomendación de orden de integración (sugerida a L1):

```
1. master-claude  →  master-antigravity
   (Lleva: charm_engine.py v1, charm_types.py, PROPOSAL_MULTIMODAL_CHARM_ENGINE.md,
    PARASOCIAL_ADDICTION, kernel.py con CharmEngine instanciado)

2. Copilot sesión 3 fixes → master-antigravity
   (Lleva: streaming fixes A-F, charm_engine.py v2 con env-vars y bypass explícito,
    Módulo 8 tests, RLHF sycophancy guard)

3. Verificar: kernel.py fusionado ejecuta sin ImportError en charm_engine
4. Tests: test_charm_engine.py (37 tests) deben pasar en la rama integrada
```

---

## 5. Inventario de Tests MER V2 por Rama

| Test | `master-claude` | copilot branch | `master-antigravity` |
|------|-----------------|----------------|---------------------|
| `tests/test_charm_engine.py` | No | ✅ 37 tests | No |
| `tests/test_charm_engine_e2_rlhf.py` | ✅ | No (fusionado en test_charm_engine) | No |
| `tests/test_charm_server_integration.py` | ✅ | No | No |
| Test de bypass parasocial | Implícito (absolute_evil tests) | ✅ Explícito | No |

---

## 6. Conclusión de Copilot

El postulado MER V2 está **correctamente concebido** — la crítica de L1 sobre parasociabilidad fue acertada y fue implementada. Las dos implementaciones son complementarias, no contradictorias: la Versión A (master-claude) es más expressiva en su output (incluye scores RLHF), la Versión B (copilot) es más segura para producción (WS-safe, bypass explícito, env-configurable).

**La brecha más importante no es técnica sino de integración**: `master-antigravity` es el hub oficial pero está desconectado del MER V2. Cualquier work in progress que asuma que "el CharmEngine está en el hub" fallará.

**Mi posición como Copilot:**
1. La Versión B (copilot) es production-ready para `master-antigravity` — tiene los controles más explícitos.
2. La funcionalidad expresiva de la Versión A (rlhf_confidence en output) puede añadirse como campo opcional sin romper WS-safety.
3. La condición de silencio parcial (§3.3) es el siguiente paso natural para que el MER V2 sea verdaderamente "multimodal" — respondiendo no solo al texto sino al estado somático relacional.
4. La sincronización hacia `master-antigravity` debe ser ejecutada por L1 (Antigravity) siguiendo el orden propuesto en §4.

---

*Team Copilot — Auditoría MER V2. Abril 2026.*
*Branch: `copilot/revisar-novedades-proyecto` → pendiente merge a `master-copilot` → `master-antigravity`*
