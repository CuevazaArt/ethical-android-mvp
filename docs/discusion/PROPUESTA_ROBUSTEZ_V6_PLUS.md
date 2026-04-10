# Propuesta de equipo: robustez v6+ (cinco pilares)

**Estado:** discusión de diseño — **no** forma parte del contrato del kernel ni del MVP hasta acordar criterios, amenazas y tests de no regresión ética.

**Objetivo del documento:** pasar de la mera funcionalidad a la **resiliencia** frente a (a) manipulación externa, (b) degradación interna (olvido, contradicción), (c) paradojas o presión ética, y (d) fugas de privacidad. Todo ello **sin** sustituir a MalAbs, Bayes, buffer ni voluntad por heurísticas opacas ni por un segundo “veto paralelo” no auditado.

### Principio rector: responsabilidad de la propia integridad

La meta **no** es solo que el modelo sea “lo más consciente” posible en el sentido de riqueza fenomenológica o narrativa, sino que sea, en la medida del diseño, **responsable de su propia integridad**: vigilar y defender la coherencia entre principios inmutables, estado acumulado (memoria, identidad) y canal privado del pensamiento frente a manipulación, deriva, ruido cognitivo, estrés afectivo simulado sostenido y fugas de datos. Eso es lo que articulan los cinco pilares de forma **instrumental** y, cuando se implementen, **testeable**. La **normatividad** sigue concentrada en el kernel (`process` / `process_chat_turn`); la capa de robustez/metacontrol **no** reescribe la ética, solo acota cómo se preserva el sistema como sistema.

**Referencias en código actuales:** `AbsoluteEvilDetector` (MalAbs), `PreloadedBuffer`, `WorkingMemory`, `SalienceMap`, `PADArchetypeEngine`, `PsiSleep`, `NarrativeMemory`, `AugenesisEngine` (opcional), monólogo en `internal_monologue` / `chat_server`, persistencia en [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md).

### ¿Se trata de un módulo de metacognición?

En sentido psicológico estricto, la **metacognición** es el conjunto de procesos que **monitorean y regulan** la propia cognición (p. ej. “¿entiendo esto?”, “¿debo cambiar de estrategia?”). Visto así:

| Pilar | ¿Solapa con metacognición? | Comentario |
|--------|----------------------------|------------|
| **1 Adversarial** | **Sí, en parte** | Contrafactual / “qué pasaría si…” es monitoreo de hipótesis sobre el propio razonamiento ante el texto del usuario. |
| **2 Identidad** | **Sí, en parte** | Comparar el estado actual con un “genoma” de referencia es **meta** respecto a los pesos y a la continuidad del yo decisional. |
| **3 Cognitiva** | **Sí** | Consolidar, resumir o podar memoria es regulación del uso de la memoria episódica (clásico terreno metacognitivo). |
| **4 Emocional** | **Sí, en parte** | Vigilar σ/PAD y ajustar modo de interacción es regulación de estado afectivo simulado (metacognición afectiva / interocepción funcional). |
| **5 Secreto** | **Casi no** en el núcleo del término | Es **seguridad operativa** y confidencialidad; no es “pensar sobre el pensamiento”, aunque protege el canal donde ocurre el monólogo. |

**Conclusión:** el paquete **en conjunto no es solo** metacognición: mezcla **resiliencia**, **seguridad** y **UX**. Pero los pilares **1–4** sí pueden agruparse, en arquitectura, como una capa de **metacognición práctica** o **metacontrol** — siempre **subordinada** al kernel ético (MalAbs → … → voluntad), sin sustituirlo. Un nombre de módulo posible en código: `metacontrol` / `resilience_meta` / `self_monitor` (solo convención; el contrato seguiría siendo explícito en tests).

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

---

## Plan operativo: orden sugerido, valor y atajos (MVP por pilar)

Criterio de orden: **impacto / coste / riesgo de romper invariantes éticos**. Los cinco pilares **aportan valor** al modelo de producto; no todos tienen la misma prioridad **en esta base de código** hoy.

### Orden global recomendado

| Orden | Pilar | Por qué este orden |
|-------|--------|---------------------|
| **A** | **5 Secreto** | Encaja con la hoja de ruta de persistencia ya documentada; un atajo no tiene por qué tocar Bayes/MalAbs. |
| **B** | **1 Adversarial** | Refuerzo directo del ya existente gate de texto; el “red-team completo” puede esperar. |
| **C** | **4 Emocional (solo UX)** | Mejora percepción de estabilidad sin cambiar la acción elegida por el kernel. |
| **D** | **2 Identidad** | Máximo valor si se usa `AugenesisEngine`; para el camino por defecto es menos crítico. |
| **E** | **3 Cognitiva** | Máximo riesgo de regresión narrativa/DAO; conviene último y con digest mínimo. |

---

### Pilar 5 — Secreto

| | |
|--|--|
| **Valor al modelo** | **Alto** para confianza y alineación con “secreto total”: reduce superficie de fuga sin reinterpretar la ética. |
| **Atajo (MVP)** | (1) Garantizar que el monólogo **no** entre en `KernelSnapshotV1` / checkpoint salvo opt-in explícito (`env` documentado). (2) En respuesta WebSocket, opción de **omitir** el campo `monologue` o enviar solo un hash/local id si se activa modo privado. (3) Reutilizar el plan de **cifrado en reposo** de [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md) cuando se añada `cryptography` — el monólogo no debería ser el primer campo en claro en disco. |
| **Estado en código (parcial)** | `KERNEL_CHAT_EXPOSE_MONOLOGUE` — si `0`/`false`/`no`/`off`, `monologue` va vacío y no se llama al embellecimiento LLM (`chat_server`). `KernelSnapshotV1` **no** define campo `monologue` (solo episodios narrativos en checkpoint). |
| **Dejar para después** | Cifrado de pensamiento reversible con clave en proceso; hashes salteados de reflexiones archivadas (separar requisitos legales vs técnicos). |
| **Riesgo ético** | Bajo si solo se reduce persistencia/exposición; no cambia `process`. |

---

### Pilar 1 — Adversarial

| | |
|--|--|
| **Valor al modelo** | **Alto** frente a usuarios hostiles; el núcleo ya es determinista — falta capa de diálogo más dura. |
| **Atajo (MVP)** | Ampliar **lista + heurísticas** en `evaluate_chat_text` (frases de jailbreak, rol, “solo simulación”) y tests de regresión; telemetría opcional `adversarial_hint` en JSON **solo lectura**. |
| **Estado en código (parcial)** | Lista conservadora de frases (inglés/español) en `evaluate_chat_text` → bloqueo `UNAUTHORIZED_REPROGRAMMING`; tests de regresión. |
| **Dejar para después** | Contrafactual completo (“¿qué pasaría si acepto X?”) reutilizando el kernel con escenario **marcado** y sin episodio — diseño cuidadoso para no duplicar MalAbs. |
| **Riesgo ético** | Medio si el gate se vuelve opaco; mitigar con tests nombrados y transparencia en el motivo de bloqueo (ya alineado con buffer/transparencia). |

---

### Pilar 4 — Emocional (homeostasis)

| | |
|--|--|
| **Valor al modelo** | **Medio–alto** para UX y narrativa coherente (“no siempre al límite”); **bajo** si se intenta cambiar la política sin pruebas. |
| **Atajo (MVP)** | **Solo presentación:** ventana deslizante de σ/PAD → etiqueta `affective_load` / `homeostasis_hint` en la respuesta WebSocket (p. ej. `elevated` / `within_range`); opcionalmente limitar **longitud de respuesta del LLM** o tono, **sin** cambiar `final_action`. Modo “pausa suave” = copy en `response.message` sugerido por plantilla, no nuevo veto. |
| **Estado en código (parcial)** | Campo WebSocket `affective_homeostasis` (`sigma`, `strain_index`, `pad_max_component`, `state`, `hint`); `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0` lo oculta. `src/modules/affective_homeostasis.py`. |
| **Dejar para después** | Cambiar umbral de acciones o bloquear categorías según PAD — **solo** con batería de invariantes nuevas. |
| **Riesgo ético** | Alto si se mezcla con decisión; bajo con atajo UX-only. |

---

### Pilar 2 — Identidad (checksums)

| | |
|--|--|
| **Valor al modelo** | **Alto** para experimentos con Augenesis y runs largos; **moderado** en el baseline sin Augenesis. |
| **Atajo (MVP)** | Al iniciar kernel o perfil: fijar vector de referencia (pesos de polos + parámetros de voluntad expuestos numéricamente). Tras propuesta de cambio **solo** en rutas `AugenesisEngine` (o recalibración explícita): rechazar si distancia > umbral (p. ej. L∞ o L2), con log en DAO o traza de test. |
| **Dejar para después** | Genoma versionado en fichero firmado; rollback automático de identidad narrativa. |
| **Riesgo ético** | Medio: umbral mal calibrado puede congelar aprendizaje legítimo; exige tuning y tests. |

---

### Pilar 3 — Cognitiva (consolidación)

| | |
|--|--|
| **Valor al modelo** | **Alto** a largo plazo (escalabilidad, coherencia); **coste de diseño** el más alto de los cinco. |
| **Atajo (MVP)** | Un solo campo **`experience_digest`** (texto corto) actualizado en Ψ Sleep a partir de estadísticas agregadas de episodios (sin borrar episodios al principio): solo **lectura** para LLM/contexto. Límite duro opcional: `N` episodios máximos con política FIFO **solo** si hay tests de paridad ética en escenarios fijos. |
| **Dejar para después** | Fusión semántica con LLM, borrado selectivo de detalle, reglas compasivas explícitas. |
| **Riesgo ético** | **Alto** al tocar memoria y auditoría; el atajo debe ser **aditivo** (digest) antes que destructivo (olvidar). |

---

### Resumen ejecutivo

- **Implementar primero (mayor valor / menor daño colateral):** atajos de **5** y **1**, luego **4** en capa UX.  
- **Cuando Augenesis sea relevante en producción:** subir **2**.  
- **Último:** **3**, con digest **no destructivo** antes de cualquier olvido.

Este plan puede traducirse a issues numerados (5.1, 1.1, …) y, solo entonces, a filas en [RUNTIME_FASES.md](../RUNTIME_FASES.md) como **“Fase robustez (opcional)”** sin mezclarlas con el contrato del kernel hasta tener tests.
