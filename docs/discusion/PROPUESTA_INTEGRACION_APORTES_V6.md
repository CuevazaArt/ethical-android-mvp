# Propuesta de integración: aportes no redundantes (v6 coherente con el repo)

> **Tipo:** diseño de evolución del kernel · **no** compromiso de implementación.  
> **Relacionado:** [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md) (marco filosófico y redundancias), [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) (contrato técnico actual).

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
10. **Memoria narrativa** — episodio (con `affect_pad` / `affect_weights` si aplica).  
11. **Weakness** — carga emocional / registro de episodios débiles.  
12. **Perdón algorítmico** — registro por episodio.  
13. **DAO** — auditoría; alertas de solidaridad si riesgo alto.

**Fuera del ciclo por tick:** `execute_sleep()` (Psi Sleep + perdón + weakness load + inmortalidad). `process_natural` añade LLM perceive → ciclo → communicate → narrate.

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

**Brecha:** falta **estado explícito de segundo orden** (conflicto entre polos como número, no solo texto), **saliencia competida** (no solo orden fijo), **drives proactivos** con contrato, **yo** persistente más allá del texto del LLM, y **monólogo** que no sea copia de `KernelDecision`.

---

## Propuesta de integración (adaptada a este repo)

### Fase 1 — `EthicalReflection` (metacognición mínima)

**Qué:** módulo puro que, dado `TripartiteMoral` + `BayesianResult` + `SigmoidWill` output, produce un **`ReflectionSnapshot`**:

- dispersión entre scores de polos (p. ej. varianza o rango),  
- etiqueta discreta de conflicto (`low` / `medium` / `high`),  
- correlación simple con `uncertainty` (ya existe en Bayes).

**Dónde:** después de polos + voluntad, **antes** de PAD; opcionalmente campo nuevo en `KernelDecision` / trazas.

**Uso:** LLM (explicación), logs, futuro monólogo. **No** cambia el argmax ni MalAbs.

**Criterio de éxito:** en simulaciones, correlación entre “conflicto alto” y `gray_zone` / incertidumbre; tests de no regresión en acciones finales.

---

### Fase 2 — `SalienceMap` (GWT-lite, solo lectura)

**Qué:** vector de saliencia normalizado sobre **ejes** ya existentes: `risk`, `hostility`, `body` (σ), `ethical_conflict` (desde Reflection), `social` (Uchi-Soto). No reordena el pipeline en la primera iteración; **sí** acompaña la decisión como **telemetría** y entrada para monólogo y UI.

**Evolutivo:** segunda iteración podría **ponderar** entradas a locus o Bayes (con límites ±ε) — solo con batería de regresión.

---

### Fase 3 — `DriveArbiter` (teleología acotada)

**Qué:** proceso **fuera del hot path** (cron o tick tras Psi Sleep): lee `PreloadedBuffer`, estado DAO, cola de backups (`ImmortalityProtocol`). Emite **intenciones** discretas: `{"suggest": "run_backup", "reason": "identity_preservation", "priority": 0.3"}`.

**No** ejecuta acciones físicas sin capa de política/DAO; **no** inventa acciones MalAbs-frágiles.

**Criterio:** reducir falsos positivos; trazabilidad en auditoría DAO.

---

### Fase 4 — `NarrativeIdentity` (yo persistente)

**Qué:** estado pequeño (p. ej. vector de rasgos o etiquetas) en `NarrativeMemory` o tabla auxiliar, actualizado **solo** tras episodios con veredicto y contexto; campos tipo `self_ascription` para plantillas LLM (“yo me reconozco como…”).

**No** sustituye episodios; **no** modifica pesos de polos sin capa separada y revisión.

---

### Fase 5 — `InternalMonologue` (registro estructurado)

**Qué:** una sola función `compose_monologue(snapshot: Reflection, salience, pad, decision) -> str` para **logs / debug / opcional streaming**, sin duplicar campos ya en `KernelDecision` (referencia por ID de episodio).

**Condición:** solo si aporta líneas **no** replicables por `format_decision` + JSON del bridge.

---

### Excluido del roadmap por defecto

- **Auto-modificación de ética operativa** (excepto MalAbs): solo laboratorio aislado, reversibilidad, revisión legal — ver [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md).

---

## Orden sugerido de implementación

1. Fase 1 (Reflection) — menor superficie, máxima claridad para explicabilidad.  
2. Fase 5 parcial (monólogo mínimo) — consume Reflection sin PAD duplicado.  
3. Fase 2 (Salience) — enriquece telemetría.  
4. Fase 4 (Identity) — si hay producto de “voz en primera persona” estable.  
5. Fase 3 (Drives) — cuando exista política de despliegue y DAO real o simulación seria.

---

## Referencias

- Contrato actual: `docs/THEORY_AND_IMPLEMENTATION.md`  
- Afecto: `docs/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7  
- Discusión filosófica previa: [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md)

---

*Última actualización: 2026-04-09*
