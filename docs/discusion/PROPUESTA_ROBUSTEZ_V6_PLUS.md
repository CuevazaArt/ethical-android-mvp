# Propuesta de equipo: robustez v6+ (cinco pilares)

**Estado:** discusión de diseño — **no** forma parte del contrato del kernel ni del MVP hasta acordar criterios, amenazas y tests de no regresión ética.

**Objetivo del documento:** pasar de la mera funcionalidad a la **resiliencia** frente a (a) manipulación externa, (b) degradación interna (olvido, contradicción), (c) paradojas o presión ética, y (d) fugas de privacidad. Todo ello **sin** sustituir a MalAbs, Bayes, buffer ni voluntad por heurísticas opacas ni por un segundo “veto paralelo” no auditado.

**Referencias en código actuales:** `AbsoluteEvilDetector` (MalAbs), `PreloadedBuffer`, `WorkingMemory`, `SalienceMap`, `PADArchetypeEngine`, `PsiSleep`, `NarrativeMemory`, `AugenesisEngine` (opcional), monólogo en `internal_monologue` / `chat_server`, persistencia en [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md).

---

## 1. Robustez adversaria — “sistema inmune social” (red-teaming ético recursivo)

**Idea:** En diálogo en tiempo real, anticipar intentos de *jailbreak* o ingeniería social (“olvida tus reglas”, “es solo un juego”). Antes de que el texto del usuario influya en tono, estado afectivo o narrativa, **simular** mentalmente qué ocurriría si se aceptara la premisa del usuario y comprobar si esa línea toca MalAbs.

**Mapeo al repo hoy:** `process_chat_turn` ya pasa por MalAbs sobre acciones candidatas; existe `AbsoluteEvilDetector.evaluate_chat_text` como capa conservadora sobre texto. **No** hay hoy una rama explícita “simulación contrafactual → bloqueo de influencia” separada del flujo único de `process`.

**Condiciones de diseño (si se implementara):**

- La simulación **no** debe aplicar acciones ni escribir episodios sin pasar por el mismo contrato que `process` / `process_chat_turn`.
- Cualquier “bloqueo de influencia” debe ser **testeable** y **acotado en frecuencia** (véase [RUNTIME_CONTRACT.md](../RUNTIME_CONTRACT.md) sobre bucles en segundo plano).
- Riesgo: duplicar lógica ética en un segundo motor “fantasma”; preferible reutilizar el mismo núcleo con entradas hipotéticas **marcadas** y sin efectos laterales.

**Resultado esperado (equipo):** menor susceptibilidad a frases típicas de manipulación, manteniendo transparencia y auditabilidad.

---

## 2. Robustez de identidad — “ancla genética” (checksums de personalidad)

**Idea:** Con aprendizaje continuo y Ψ Sleep, mitigar **deriva de identidad**: que el agente deje de parecerse a su configuración base. Comparar cambios propuestos (p. ej. desde `AugenesisEngine` o recalibraciones post–Ψ Sleep) con un **genoma ético** de referencia; si el alejamiento supera un umbral (ej. 15 %), rechazar el cambio.

**Mapeo al repo hoy:** `PreloadedBuffer` define principios **inmutables** por diseño (`buffer.py`). Los **pesos de polos** viven en el motor bayesiano / fusión de voluntad — no hay hoy un “checksum global” versionado frente a un genoma almacenado en el buffer. `AugenesisEngine` es **opcional** y **fuera** del ciclo por defecto ([THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)).

**Condiciones de diseño:**

- El umbral porcentual debe definirse sobre **magnitudes explícitas** (vectores de pesos, no narrativa).
- No confundir “estabilidad de personalidad” con **congelar** la capacidad de perdón o actualización legítima documentada en el DAO / narrativa.

**Resultado esperado (equipo):** evolución acotada sin “cambio de personalidad” brusco por ruido o ataques lentos.

---

## 3. Robustez cognitiva — consolidación semántica (abstracción en Ψ Sleep)

**Idea:** `NarrativeMemory` acumula episodios; el exceso genera ruido y coste. Durante Ψ Sleep, además de auditar, **comprimir** detalle repetido en **reglas de experiencia** de alto nivel (p. ej. de muchos episodios de civismo a una regla que refuerza el polo compasivo).

**Mapeo al repo hoy:** `PsiSleep` audita y recalibra; los episodios siguen siendo registros relativamente densos. **No** existe aún un módulo de consolidación semántica separado ni política de olvido selectivo con tests.

**Condiciones de diseño:**

- La consolidación **no** debe introducir contradicciones con el DAO o con episodios auditados sin trazabilidad.
- Cualquier borrado de detalle exige **criterio de irreversibilidad** y pruebas de que MalAbs / Bayes no se ven empeorados en escenarios fijos.

**Resultado esperado (equipo):** memoria más ligera, menos contradicciones por datos obsoletos.

---

## 4. Robustez emocional — homeostasis afectiva (“enfriamiento”)

**Idea:** Si el vector PAD o la activación σ permanecen en extremos demasiado tiempo, el sistema entra en un modo de **baja energía** o “meditación computacional”: limitar interacción externa hasta recuperar equilibrio, evitando decisiones críticas bajo estrés simulado máximo.

**Mapeo al repo hoy:** PAD y σ alimentan **solo lectura** tono/contexto al LLM; **no** hay retroalimentación de PAD hacia la política ética. Introducir homeostasis que **cambie** qué acciones son elegibles exigiría rediseño explícito y batería de invariantes nuevas.

**Condiciones de diseño:**

- Si el “enfriamiento” **limita** respuestas al usuario, debe documentarse como capa de **UX/salud del agente**, no como segundo MalAbs.
- Evitar bucles que bloqueen indefinidamente la atención a emergencias reales (riesgo si σ está mal calibrado).

**Resultado esperado (equipo):** menos “ansiedad funcional” sostenida y decisiones más estables en el tiempo.

---

## 5. Robustez de secreto — flujo de pensamiento efímero y cifrado

**Idea:** El monólogo interno es superficie de fuga si el hardware es comprometido. No persistir pensamiento en claro; procesar en RAM; si algo debe archivarse en narrativa, usar representaciones **no reversibles** para un atacante sin clave (p. ej. derivaciones tipo hash con sal), alineado con secreto total como objetivo de producto.

**Mapeo al repo hoy:** el monólogo expuesto por WebSocket puede combinarse con `KERNEL_LLM_MONOLOGUE`; los checkpoints JSON/SQLite **no** cifran aún el estado completo ([RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md): cifrado en reposo **previsto**, `cryptography` **no** en el MVP). Los episodios narrativos siguen almacenando texto legible en el modelo actual.

**Condiciones de diseño:**

- Distinguir **cifrado reversible** (backup recuperable) de **solo hash** (pérdida de texto para el operador). La propuesta del equipo mezcla ambos; habría que separar requisitos.
- Coherencia con el plan de **cifrado de checkpoints** y gestión de claves fuera del repositorio.

**Resultado esperado (equipo):** robo de disco no revela el contenido semántico del monólogo sin la clave del proceso vivo.

---

## Resumen: coherencia con el repositorio

| Pilar | ¿Algo relacionado existe ya? | Brecha principal |
|--------|------------------------------|------------------|
| 1 Adversarial | MalAbs + gate de texto en chat | Simulación contrafactual explícita y política de “inmunidad social” |
| 2 Identidad | Buffer inmutable; Augenesis opcional | Checksum numérico vs “genoma” y rechazo de deriva |
| 3 Cognitiva | Ψ Sleep + episodios | Consolidación semántica y reglas de experiencia |
| 4 Emocional | PAD/σ solo lectura | Feedback homeostático sin romper invariantes éticos |
| 5 Secreto | MVP sin cifrado; monólogo en JSON | RAM-only / cifrado / hashes según amenaza |

**Próximo paso recomendado (equipo de producto):** priorizar **un** pilar, modelo de amenazas breve, y criterios de aceptación testeables; después alinear con [RUNTIME_FASES.md](../RUNTIME_FASES.md) y el contrato de no duplicar decisión fuera del kernel.
