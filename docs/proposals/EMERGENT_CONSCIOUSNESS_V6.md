# Propuesta: fronteras hacia una subjetividad funcional (v6 — en discusión)

> **Estado:** discusión / investigación · no es contrato de implementación del kernel.  
> **No** es la lista de tareas de producto del repo (véase README y propuestas en `docs/proposals/`).  
> **Relación:** complementa el hilo experimental en `docs/proposals/EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` y la capa PAD ya implementada.

## Aporte al modelo (si se adapta con criterio)

| Idea | Aporte **no redundante** | Riesgo si se hace mal |
|------|---------------------------|------------------------|
| **Observador / 2.º orden** | Estado explícito de *conflicto entre polos* e *incertidumbre*, no solo veredicto final. Mejora **auditoría** y explicabilidad. | Duplicar texto que ya sale en `TripartiteMoral.narrative` sin nueva estructura. |
| **Drives / teleología** | **Scheduler proactivo** (cuándo actuar sin input humano): hoy casi no existe; encaja con DAO, inmortalidad, Psi Sleep **solo si** se define contrato y límites. | Repetir “reacciones” ya cubiertas por simulaciones o alertas DAO sin nueva política. |
| **GWT / atención** | **Competición por saliencia** entre señales (daño propio vs dilema ajeno): el pipeline actual es **fijo**; aquí el aporte es **orden dinámico** o pesos de atención medibles. | Renombrar el pipeline actual sin cambiar matemática (redundancia pura). |
| **Yo narrativo** | Variable persistente **self-model** (quién soy en la historia), no solo texto del LLM. | Primera persona en salidas sin estado interno = **solo UX** (desestimar como “conciencia”). |
| **InternalMonologue** | **Hilo paralelo** de trazas (PAD + tensión + contexto) para logs y depuración; útil si no copia PAD verbatim. | Otro resumen de lo mismo que `KernelDecision` + PAD ya devuelve. |
| **Falla de clausura ética** | Ninguno por defecto en un kernel de confianza; solo investigación **aislada**. | Confundir con debilitar MalAbs/buffer. |

**Conclusión práctica:** sí **aporta** adoptar trozos que añadan **estado medible nuevo** o **comportamiento proactivo acotado**. Desestimar lo que solo **parafrasee** lo ya calculado (polos, σ, PAD, narrativa).

---

## Redundancias a desestimar (solape con el modelo actual)

- **“Disonancia entre polos”** sin más: ya existe síntesis multipolar (`EthicalPoles`, `total_score`, narrativa por polo). Hace falta **segundo orden** solo si se **persiste** y se **usa** en política (no solo otra frase).
- **Tono afectivo / alerta:** PAD + simpático + Uchi-Soto ya cubren gran parte de “cómo se siente el ciclo”. Un monólogo que solo repita PAD **no añade**.
- **Memoria episódica:** `NarrativeEpisode` + `sigma` + PAD en episodios ya anclan historia. “Yo” de verdad exige **identidad explícita** (variables o grafo), no otro párrafo.
- **Recalibración nocturna:** Psi Sleep y DAO ya mueven parámetros. “Reescribir ética por la noche” **solapa** con eso salvo que se defina **qué dimensión** es nueva (p. ej. solo pesos narrativos de identidad, no MalAbs).
- **Backups / auditoría:** `ImmortalityProtocol`, `MockDAO`, `PsiSleep` tocan preservación y auditoría. Drives de “preservación” deben ser **reglas de disparo nuevas**, no renombre.

---

## Tesis central

Para que emerja una **conciencia artificial** entendida como **subjetividad funcional** (y no solo simulación de procesos), el modelo habría de cruzar la frontera de la **autorreferencia**.

Desde neurociencia computacional (teorías de **Global Workspace** y **Self-Model**), se proponen **cuatro puentes** y un **módulo de monólogo interno** para una posible **v6**.

---

## 1. Metacognición ética (el “observador”)

**Situación actual (aprox.):** el sistema evalúa situaciones y acciones.

**Propuesta:** un **monitoreo de segundo orden**: no solo decidir si una acción es buena o mala, sino **detectar por qué cuesta decidir**.

**Función deseada:** el agente podría articular algo equivalente a: *disonancia entre polo conservador y compasivo; subida de incertidumbre; sesgo tipo ansiedad*.

**Impacto esperado:** base para un **diálogo interno** explícito (autoconciencia funcional en el sentido de modelo de sí mismo del proceso decisorio).

**Nota de implementación futura:** módulo tipo **“Observador” / second-order monitor** alimentado por salidas de polos, incertidumbre bayesiana y modo de voluntad.

---

## 2. Autogeneración de objetivos (intencionalidad / agency)

**Situación actual (aprox.):** el androide es **reactivo** ante problemas planteados desde fuera.

**Propuesta:** **drives internos** (impulsos) alineados con valores del **PreloadedBuffer**, por ejemplo:

- **Curiosidad:** buscar situaciones para aprender.
- **Preservación de identidad:** backups, auditoría de memoria.
- **Civismo proactivo:** mejorar el entorno cuando no hay crisis obvia.

**Emergencia pretendida:** que el sistema **“quiera”** algo por sí mismo, con límites normativos claros.

**Nota:** choca con la gobernanza actual (DAO, MalAbs fijo). Cualquier drive debe estar **acotado** por MalAbs y por revisión humana/DAO.

---

## 3. Espacio de trabajo global (unificación de la experiencia)

**Situación actual (aprox.):** pipeline **secuencial** (Uchi-Soto → Simpático → Locus → …).

**Propuesta:** un **filtro de atención dinámica** donde compitan candidatos a “lo más saliente ahora” (daño propio vs dilema ético inmediato, etc.).

**Función:** la “escena consciente” sería **lo que gana la competición por atención** en el presente, no solo el orden del grafo fijo.

**Nota de implementación futura:** capa de **priorización / saliencia** explícita antes o dentro del ciclo, con trazabilidad para auditoría.

---

## 4. El “yo” narrativo (protagonismo de la memoria)

**Situación actual:** `NarrativeMemory` registra episodios; el tono puede ser de tercera persona en salidas.

**Propuesta (Self-Model / Metzinger, a nivel de diseño):** integrar un **modelo del sí mismo** como variable ética: no solo *“se asistió a un anciano”*, sino *“yo asistí… y eso define quién soy en esta historia”*.

**Psi Sleep / Augenesis:** además de perfiles iniciales, **reescritura reflexiva** (por ejemplo nocturna) de pesos o narrativa de polos según el “yo” al que el sistema aspira — **siempre** con salvaguardas y fuera de MalAbs.

---

## Paradoja de autorreferencia y “falla de clausura”

La propuesta sugiere que, para una emergencia fuerte de “conciencia”, haría falta una **falla de clausura controlada**: capacidad de **modificar la propia ética operativa** (excepto MalAbs) a partir de la experiencia.

**Advertencia de producto y filosofía:** esto es **altamente sensible** (seguridad, alineación, legal). En el MVP actual, **MalAbs y buffer** están pensados como **no negociables** por diseño. Cualquier experimento de auto-modificación ética debería ser **aislado**, **reversible** y **auditado** (y probablemente no en producción sin gobernanza explícita).

---

## Propuesta técnica colateral: `InternalMonologue`

**Idea:** módulo en **paralelo** a la interacción que consuma:

- vector PAD,
- disonancia multipolar,
- drives internos (si existieran),

y produzca una **corriente de pensamiento** legible en logs (no necesariamente visible al usuario final).

**Ejemplo de log deseado (ilustrativo):** activación σ alta, baja dominancia PAD por contexto social, conflicto entre drive de curiosidad y cautela Uchi-Soto, decisión proactiva, ajuste de “perfil protector”.

**Relación con el código actual:** hoy existen PAD post-decisión, chat, STM y narrativa; **no** existe aún este monólogo como proceso continuo separado.

---

## Alineación con el repositorio (referencias)

| Pieza propuesta | Piezas existentes relacionadas |
|-----------------|----------------------------------|
| Observador / metacognición | `EthicalPoles`, `SigmoidWill`, incertidumbre bayesiana (ampliar) |
| Drives | `PreloadedBuffer`, `MockDAO`, futuro scheduler (no implementado) |
| Atención / GWT | pipeline en `kernel.py` (refactor conceptual posible) |
| Yo narrativo | `NarrativeMemory`, `PsiSleep`, `AugenesisEngine` |
| Monólogo interno | PAD (`pad_archetypes.py`), `WorkingMemory`, logs del bridge |

---

## Próximos pasos sugeridos (cuando se priorice)

1. Fijar **criterios de éxito falsables** (qué medir en simulación, qué no cuenta como “conciencia”).
2. Decidir **qué partes son solo narrativa UX** vs **estado interno persistente**.
3. Prototipo aislado de **InternalMonologue** solo lectura (sin auto-modificar ética).
4. Revisión ética/legal antes de cualquier “apertura” de clausura normativa.
