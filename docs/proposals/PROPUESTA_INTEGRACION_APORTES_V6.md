# Propuesta de integración: aportes no redundantes (v6 coherente con el repo)

> **Tipo:** diseño de evolución v6 del kernel; **estado:** Fases 1–5 reflejadas en código (detalle en cada sección).  
> **Relacionado:** [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md) (marco filosófico y redundancias), [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) (contrato técnico actual).

## Objetivo

Incorporar solo lo que **añade estado medible nuevo** o **comportamiento proactivo acotado**, sin duplicar polos, PAD, σ, narrativa episódica ni Psi Sleep/DAO tal como ya existen.

**Principios:**

1. **MalAbs y buffer** siguen siendo anclas; ninguna fase los modifica en producción.
2. **Nada nuevo** en el camino crítico del veto ético sin tests de no regresión.
3. Cada fase = **incremento acotado** + **criterios falsables** (métricas en simulación o logs).

---

## Dónde estamos hoy (inventario del modelo, 2026)

### Capa de orquestación

| Pieza | Archivo | Rol |
|-------|---------|-----|
| Ciclo de decisión | `src/kernel.py` | Encadena módulos; `KernelDecision`, `ChatTurnResult`; `process_chat_turn()` (chat + STM); `register_episode` en turnos ligeros. |
| Puente async | `src/real_time_bridge.py` | `asyncio.to_thread` sobre `process_chat_turn`. |
| Servidor WS | `src/chat_server.py` | FastAPI `/ws/chat`, un kernel por conexión. |

### Flujo principal `process()` (orden real en código)

1. **Uchi-Soto** — confianza / dialectica a partir de señales + `message_content`.  
2. **Simpático** — σ, modo energético.  
3. **Locus** — atribución causal (α, β, dominante).  
4. **MalAbs** — filtro duro sobre **acciones** candidatas.  
5. **Buffer** — principios activados por contexto.  
6. **Bayes** — elección de acción esperada.  
7. **Polos** — `TripartiteMoral` (scores, veredicto, narrativa multipolar).  
8. **Voluntad sigmoide** — modo D_fast / gray_zone / etc.  
9. **PAD + arquetipos** — proyección afectiva **post-decisión**; no gobierna el veto.  
10. **Memoria narrativa** — episodio (con `affect_pad` / `affect_weights` si aplica); **`NarrativeIdentityTracker`** actualiza estado de yo solo al registrar episodio (`src/modules/narrative_identity.py`).  
11. **Weakness** — carga emocional / registro de episodios débiles.  
12. **Perdón algorítmico** — registro por episodio.  
13. **DAO** — auditoría; alertas de solidaridad si riesgo alto.

**Fuera del ciclo por tick:** `execute_sleep()` (Psi Sleep + perdón + weakness load + inmortalidad + **`DriveArbiter.evaluate`**). `process_natural` añade LLM perceive → ciclo → communicate → narrate. Monólogo estructurado en logs vía `compose_monologue_line` (`src/modules/internal_monologue.py`).

### Módulos por carpeta (`src/modules/`)

| Módulo | Archivo | Función resumida |
|--------|---------|-------------------|
| MalAbs | `absolute_evil.py` | Veto de acciones + `evaluate_chat_text()` conservador. |
| Constitución | `buffer.py` | Principios pre-cargados por contexto. |
| Impacto | `bayesian_engine.py` | Expectativas sobre acciones; poda. |
| Polos | `ethical_poles.py` | Multipolar dinámico → `TripartiteMoral`. |
| Voluntad | `sigmoid_will.py` | Modo de decisión según impacto/incertidumbre. |
| Cuerpo | `sympathetic.py` | σ, energía, modo simpático/parasimpático. |
| Memoria larga | `narrative.py` | Episodios, morales, σ, PAD opcional en episodio. |
| Social | `uchi_soto.py` | Círculos de confianza. |
| Atribución | `locus.py` | Locus de control. |
| Noche | `psi_sleep.py` | Auditoría, recalibraciones sueltas. |
| Gobernanza | `mock_dao.py` | Votación, auditorías, alertas. |
| Ruido | `variability.py` | Variabilidad controlada (opcional). |
| Lenguaje | `llm_layer.py` | Percepción, comunicación, narrativa rica. |
| Humanización | `weakness_pole.py` | Imperfección narrativa sin cambiar decisión. |
| Perdón | `forgiveness.py` | Decaimiento de memorias negativas. |
| Respaldo | `immortality.py` | Backup distribuido. |
| Augenesis | `augenesis.py` | Perfiles de “alma” sintética. |
| Afecto | `pad_archetypes.py` | PAD + softmax sobre prototipos. |
| STM | `working_memory.py` | Turnos de diálogo cortos. |
| Drives (post-sleep) | `drive_arbiter.py` | Intenciones discretas advisory tras backup. |
| Identidad narrativa | `narrative_identity.py` | EMA sobre episodios; contexto LLM + JSON chat. |
| Monólogo | `internal_monologue.py` | Una línea `[MONO]` para logs / API. |

### Simulaciones y tests

| Área | Ubicación |
|------|-----------|
| Escenarios 1–9 | `src/simulations/runner.py`, `src/main.py` |
| Propiedades éticas + chat + servidor | `tests/` |

### Qué **ya cubre** buena parte del vocabulario “conciencia funcional” sin los cuatro puentes nuevos

- **Tensión decisoria:** polos + incertidumbre bayesiana + modo de voluntad.  
- **Cuerpo / alerta:** σ, Uchi-Soto.  
- **Tono / afecto:** PAD post-decisión.  
- **Historia:** episodios + Psi Sleep.  
- **Diálogo:** `WorkingMemory` + chat + WebSocket.  

**Cubierto en v6 repo:** reflexión de segundo orden (**Fase 1**), saliencia (**Fase 2**), drives advisory (**Fase 3**), yo narrativo (**Fase 4**), monólogo compacto (**Fase 5**). Lo que sigue siendo **fuera de alcance** por defecto es auto-modificación de ética operativa (véase sección excluida).

---

## Propuesta de integración (adaptada a este repo)

### Fase 1 — `EthicalReflection` (metacognición mínima) — **implementado**

**Qué:** módulo puro `src/modules/ethical_reflection.py` que, dado `TripartiteMoral` + `BayesianResult` + salida de `SigmoidWill.decide`, produce un **`ReflectionSnapshot`**:

- `pole_spread` = max(score) − min(score) por polo,  
- `conflict_level` ∈ {`low`, `medium`, `high`} (umbrales en `EthicalReflection.LOW_MAX` / `MEDIUM_MAX`),  
- `strain_index` ∈ [0, 1] = `(spread/2) * (0.5 + uncertainty)`,  
- `note` breve para logs / API.

**Dónde:** en `EthicalKernel.process`, tras modo final y elección de acción, **antes** de PAD; campo `KernelDecision.reflection`. Expuesto en `format_decision` y JSON del `chat_server`. `reflection_to_llm_context()` alimenta `LLMModule.communicate(..., reflection_context=...)` en `process_natural` y `process_chat_turn`.

**Uso:** explicabilidad, telemetría y matiz de voz (sin cambiar decisión). **No** modifica la acción ni MalAbs.

**Criterio de éxito:** tests en `tests/test_ethical_reflection.py`; regresión ética intacta (acción igual con o sin reflexión — la reflexión es solo lectura).

---

### Fase 2 — `SalienceMap` (GWT-lite, solo lectura) — **implementado**

**Qué:** `src/modules/salience_map.py` — `SalienceSnapshot` con `weights` normalizados en cuatro ejes (`risk`, `social`, `body`, `ethical_conflict`), `dominant_focus`, `raw_scores`. `social` combina hostilidad, `caution_level` y dialectica; `body` usa σ; `ethical_conflict` usa `reflection.strain_index`.

**Dónde:** tras `EthicalReflection`, antes de PAD; campo `KernelDecision.salience`. `salience_to_llm_context()` → `communicate(..., salience_context=...)`. JSON en `chat_server`; bloque en `format_decision`.

**Evolutivo:** ponderar locus/Bayes (±ε) solo con batería de regresión — **no** hecho aún.

---

### Fase 3 — `DriveArbiter` (teleología acotada) — **implementado**

**Qué:** `src/modules/drive_arbiter.py`. Evaluación **tras** Psi Sleep e inmortalidad (`EthicalKernel.execute_sleep`); también expuesto en JSON WebSocket como `drive_intents` (vista advisory en cada turno). Emite hasta cuatro `DriveIntent` con `suggest`, `reason`, `priority`.

**No** ejecuta acciones físicas sin capa de política/DAO; **no** inventa acciones MalAbs-frágiles.

**Criterio:** trazabilidad; lista acotada y ordenada por prioridad.

---

### Fase 4 — `NarrativeIdentity` (yo persistente) — **implementado**

**Qué:** `NarrativeIdentityTracker` en `NarrativeMemory.identity`; `update_from_episode` solo al registrar episodio. `ascription_line()` / `to_llm_context()` alimentan `LLMModule.communicate(..., identity_context=...)` y el JSON del chat (`identity` con leans + `ascription`).

**No** sustituye episodios; **no** modifica pesos de polos.

---

### Fase 5 — `InternalMonologue` (registro estructurado) — **implementado**

**Qué:** `compose_monologue_line(decision, episode_id)` en `internal_monologue.py` — línea compacta `[MONO]` para `format_decision` y campo `monologue` en JSON del `chat_server` cuando hay `KernelDecision`.

---

### Excluido del roadmap por defecto

- **Auto-modificación de ética operativa** (excepto MalAbs): solo laboratorio aislado, reversibilidad, revisión legal — ver [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md).

---

## Orden sugerido de implementación

1. Fase 1 (Reflection) — **hecho.**  
2. Fase 2 (Salience) — **hecho** (telemetría + LLM context).  
3. Fase 5 (monólogo estructurado) — **hecho** (`format_decision` + JSON `monologue`).  
4. Fase 4 (Identity) — **hecho** (memoria + LLM + JSON `identity`).  
5. Fase 3 (Drives) — **hecho** (post–Ψ Sleep + JSON `drive_intents` por turno).

---

## Referencias

- Contrato actual: `docs/proposals/THEORY_AND_IMPLEMENTATION.md`  
- Afecto: `docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7  
- Discusión filosófica previa: [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md)

---

*Última actualización: 2026-04-09 (Fases 3–5 integradas en kernel, LLM y `chat_server`.)*
