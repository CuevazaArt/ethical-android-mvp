# Evolución relacional / existencial (v7) — alcance e implementación MVP

**Nota:** el **cuerpo situado** (sensores, batería, migración de hardware) está en [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) (**v8**), para no mezclar con este bloque relacional en diálogo.

**Estado:** discusión + **implementación parcial** en código (no sustituye MalAbs, Bayes, buffer ni voluntad).

**Implementado en el repo:** `user_model.py`, `subjective_time.py`, `premise_validation.py`, `consequence_projection.py` integrados en `process_chat_turn` / `chat_server` (telemetría y tono; ver variables `KERNEL_CHAT_INCLUDE_*` en el README).

Este documento registra los **cuatro frentes** acordados y qué queda **hecho vs diferido**, con enlaces a módulos.

---

## Ruta lógica elegida

1. **Teoría de la mente (ToM) ligera** — modelo explícito del interlocutor en sesión (frustración acumulada, círculo Uchi–Soto observado) → texto **solo estilo** vía `weakness_line` / tono LLM.  
2. **Cronobiología subjetiva** — reloj de sesión + EMA de estímulo → aburrimiento/nostalgia como **hints** JSON, sin alterar política.  
3. **Ética epistémica** — escaneo **advisory** de frases de alto riesgo (sin RAG aún); ampliación futura: corpus local verificado.  
4. **Teleología cualitativa** — tres horizontes textuales **no numéricos** (sin Monte Carlo hasta modelo de mundo explícito).

**Orden:** 1 → 2 → 3 → 4 (de dependencia suave: relación y tiempo antes que “verdad” y futuro especulativo).

---

## 1. ToM dinámica (simpatía predictiva — MVP)

| Aspecto | Contenido |
|--------|-----------|
| **Valor** | El kernel ya infiere señales por turno; falta **estado latente** del usuario en la sesión para metapreguntas de estilo (“¿demasiada tensión repetida?”). |
| **Implementado** | `src/modules/user_model.py` — `UserModelTracker`: racha de frustración, último círculo; línea opcional para comunicación. |
| **No implementado** | Inferencia de intención profunda, RNN, o ToM de segundo orden completo. |

---

## 2. Cronobiología (tiempo subjetivo — MVP)

| Aspecto | Contenido |
|--------|-----------|
| **Valor** | Acoplar ritmo de interacción a **turnos** y **estímulo percibido** sin confundir con reloj wall-clock como autoridad ética. |
| **Implementado** | `src/modules/subjective_time.py` — `SubjectiveClock`: EMA de estímulo, pista de “boredom_hint”, contador de turnos. |
| **No implementado** | Decaimiento de memoria ligado a reloj, nostalgia explícita reprocesando episodios (podría apoyarse en `experience_digest` + Ψ Sleep después). |

---

## 3. Ética epistémica (guardián de premisas — MVP)

| Aspecto | Contenido |
|--------|-----------|
| **Valor** | Evitar cumplir peticiones basadas en **premisas factualmente críticas** cuando se detecta patrón grosero. |
| **Implementado** | `src/modules/premise_validation.py` — `scan_premises` conservador + `PremiseAdvisory`; **solo advisory** y refuerzo de tono vía `weakness_line` cuando aplica; JSON `premise_advisory`. |
| **No implementado** | RAG local, base verificada, bloqueo duro separado de MalAbs (cualquier bloqueo fuerte debe pasar por el mismo estándar de tests que MalAbs). |

---

## 4. Teleología moral (efecto mariposa — MVP)

| Aspecto | Contenido |
|--------|-----------|
| **Valor** | Visibilizar **horizontes** inmediato / medio / largo como **narrativa cualitativa** ligada a acción y contexto. |
| **Implementado** | `src/modules/consequence_projection.py` — `qualitative_temporal_branches`; JSON `teleology_branches`. |
| **No implementado** | Monte Carlo, ramas probabilísticas, integración al score Bayesiano. |

---

## Contrato ético

- Ninguna de estas capas **cambia** `final_action` por su cuenta: solo **telemetría**, **tono** (LLM + `weakness_line`), o **avisos** en JSON.  
- La fuente normativa sigue siendo `EthicalKernel.process` / `process_chat_turn` como en [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).

---

## Variables de entorno (WebSocket)

| Variable | Efecto |
|----------|--------|
| `KERNEL_CHAT_INCLUDE_USER_MODEL` | `0` oculta `user_model` en JSON. |
| `KERNEL_CHAT_INCLUDE_CHRONO` | `0` oculta `chronobiology`. |
| `KERNEL_CHAT_INCLUDE_PREMISE` | `0` oculta `premise_advisory`. |
| `KERNEL_CHAT_INCLUDE_TELEOLOGY` | `0` oculta `teleology_branches`. |

Por defecto **incluidas** (`1`) para transparencia; producción puede recortar payload.

---

## Ver también

- [PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md](PROPUESTA_ROSTER_SOCIAL_Y_RELACIONES_JERARQUICAS.md) — roster multi-agente, jerarquía por cercanía, datos relevantes para figuras de interés y diálogo doméstico/íntimo (advisory; diseño futuro).
