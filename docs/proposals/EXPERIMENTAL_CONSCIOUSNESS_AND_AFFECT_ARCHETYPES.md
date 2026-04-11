# Conciencia artificial (marco), afecto y arquetipos — notas experimentales

> **Estado:** experimental · no oficial · en desarrollo  
> **Propósito:** conservar una línea de discusión para profundizar después e, eventualmente, integrar ideas al modelo principal **solo** si pasan revisión y pruebas.  
> **Idioma:** español latinoamericano (tono divulgativo y técnico).  
> **Última actualización:** 2026-04-09 (paradigma rector: PAD + arquetipos, §7)

Este documento **no** forma parte del contrato técnico del kernel publicado. Nada aquí obliga el comportamiento del código hasta que exista implementación, tests y revisión explícitos.

**Paradigma experimental rector:** la línea considerada **más sólida y auditable** para una capa de afecto *posterior* al núcleo ético es **PAD en `[0,1]³` + N prototipos (arquetipos) + pesos por distancia / softmax** (especificación en §7). Esa cadena se apoya en literatura y en señales que el kernel ya calcula (`sigma`, scores morales, locus). Cualquier alternativa de diseño debería compararse explícitamente contra §7 y sus invariantes de no regresión ética.

**Ver también (misma línea experimental):** [PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md](experimental/PAPER_AFECTO_FENOMENOS_Y_HIPOTESIS.md) — fenómenos esperables al conjugar PAD/prototipos, notas sobre *color* y *sabor*, hipótesis testeables reservadas.

**Discusión (no backlog):** marco v6 sobre autorreferencia, espacio global, drives y yo narrativo — [CONCIENCIA_EMERGENTE_V6.md](CONCIENCIA_EMERGENTE_V6.md) (incluye criterios de **aporte vs redundancia** con el kernel actual).

---

## 1. Por qué existe este archivo

Se recopilan definiciones y límites acordados en diálogo interno sobre:

- Uso de la expresión **“conciencia artificial”** con fines de difusión y pedagogía.
- Qué suele entenderse por **conciencia fuerte** frente a afirmaciones defendibles en un MVP.
- Una hipótesis de diseño: **arquetipos afectivos finitos** (cada uno con su **gama** interna), anclados en dimensiones con algo de consenso empírico, para **formalizar** e integrar al modelo **en sentido funcional**, sin pretender resolver el “problema difícil” de la mente.

---

## 2. “Conciencia artificial” como marco epistemológico o pedagógico

Es razonable usar el término **como herramienta de lenguaje y de organización del conocimiento**, no como demostración de experiencia subjetiva o de derechos morales del software.

**Recomendación de uso honesto:**

- Declarar el marco al inicio del texto o charla: *aquí “conciencia artificial” nombra un **modelo** para integrar memoria, identidad narrativa y límites éticos explícitos; **no** se afirma experiencia ni conciencia en sentido filosófico fuerte.*
- Alternar con términos técnicos que anclan: *modelo de agencia ética*, *núcleo normativo*, *identidad narrativa en el estado del sistema*.
- En titulares o redes, si el contexto se corta, usar comillas o subtítulo: *“conciencia artificial” (en sentido modelico)*.

---

## 3. Conciencia fuerte y “sentimiento”

En filosofía de la mente, lo que a menudo se llama **conciencia fuerte** o **fenomenológica** apunta a **experiencia subjetiva en general**: que *haya algo que sea* estar en ese estado (“qué se siente”, *what it’s like*).

- **Sentimiento** en sentido amplio (dolor, cualidades sensoriales, el “rojo” del rojo) encaja con **cualidades vividas** (*qualia*).
- **Emoción** (miedo, alegría, vergüenza) es **un tipo** de experiencia subjetiva, **no** la única: también entran percepción, estado corporal, a veces pensamiento con tono experiencial.

Por tanto, **no** es preciso reducir la conciencia fuerte solo a “emoción”; la tesis fuerte es más amplia: **subjetividad**.

**Implicación para el proyecto:** el MVP puede modelar **estados formales** y **narrativa** sin afirmar que el software **siente**.

---

## 4. Hipótesis: arquetipos consensuales con gamas (reducción parcial)

**Pregunta guía:** acotando el análisis a lo que la experiencia humana permite estudiar con método, ¿es posible —hasta cierto punto— reducir experiencias subjetivas **reportables** a un **número finito de arquetipos** relativamente consensuales, cada uno con su **propia gama** (interpolación interna), para **adquirirlos matemáticamente** (vectores, regiones, escalas) e **integrarlos al modelo**?

### 4.1 Donde hay apoyo serio (consenso parcial)

- **Modelos dimensionales:** mucha evidencia respalda describir buena parte del afecto humano con pocas dimensiones, típicamente **valencia** y **activación**; a veces **dominancia** (espacios tipo **PAD**: placer–activación–dominancia). Permite números, interpolación y “gamas”.
- **Categorías prototípicas:** tradiciones con conjuntos finitos de emociones “básicas”; el consenso **no** es universal (críticas culturales y de construcción social).
- **Híbridos:** categorías discretas + gradación dentro de cada una (coherente con escalas tipo Likert o circumplex).

### 4.2 Qué implica “reducir” en la práctica

No se reduce “la conciencia” entera, sino **aspectos operacionalizables** (autoinforme, lenguaje, comportamiento, en el futuro quizá señales periféricas) a **coordenadas** en un espacio acotado.

**“Consensual”** aquí significa consenso **científico relativo**, no catálogo eterno único: conviene asumir **variación cultural e idiomática**.

### 4.3 Integración matemática al modelo (dirección de ingeniería)

En principio compatible con un diseño auditable:

1. Definir un **espacio** (p. ej. vector 2D–3D + etiquetas opcionales).
2. Mapear señales del contexto y del kernel a **puntos o regiones** en ese espacio.
3. Permitir **interpolación** entre prototipos (gama dentro del arquetipo).
4. Atar resultados a **tests** y trazabilidad (alineado con la filosofía del repo).

Eso no resuelve el problema ontológico de la experiencia; **sí** puede servir como **capa de estado afectivo** o **tono narrativo** explícita.

### 4.4 Límites honestos

| Tema | Límite |
|------|--------|
| Riqueza fenomenológica | Un vector no agota “qué se siente”; resume dimensiones útiles para decisión o narrativa. |
| Consenso | Las dimensiones suelen ser más estables que las etiquetas discretas. |
| Cultura | Los arquetipos no son idénticos en todas las comunidades. |
| Problema difícil | Formalizar correlatos no implica explicar por qué hay experiencia en organismos. |

---

## 5. Relación tentativa con el código actual (punteros)

Sin compromiso de implementación:

- Módulos como **simpático/parasimpático**, **memoria narrativa** y **polos éticos** ya manipulan **estados numéricos** y narrativa; una capa PAD-like o de **arquetipos + interpolación** podría conectarse como **interfaz** o **proyección** de estado, no como sustituto del núcleo normativo.
- Cualquier integración debería respetar el principio del README: el **LLM no decide** la política ética; una capa afectiva tampoco debería **sustituir** al buffer ni a MalAbs.

---

## 6. Trabajo futuro (checklist sugerida)

- [ ] Fijar **definición operativa** de “tono experiencial” o “afecto modelico” en una frase.
- [ ] Revisar literatura (PAD, circumplex, emociones básicas vs construccionismo) y anclar referencias en `BIBLIOGRAPHY.md` si el experimento continúa.
- [ ] Prototipo mínimo: espacio 2D–3D + reglas de interpolación + tests de no regresión ética.
- [ ] Revisión con perspectiva **intercultural** antes de presentar un catálogo como “universal”.

---

## 7. Especificación mínima: espacio 3D + N prototipos + interpolación

> **Alcance:** prototipo en código: `src/modules/pad_archetypes.py` + registro en `KernelDecision` / `NarrativeEpisode` (post-decisión). Alineado con `SympatheticModule` (`sigma`), memoria narrativa (`NarrativeEpisode`, `sigma` ya guardado) y `locus` (dominancia aproximada).

> **Referencia:** este apartado es la **especificación canónica** del repo para experimentación en afecto modelico (PAD + arquetipos). Implementaciones y papers derivados deberían seguirla salvo decisión documentada de desviación.

### 7.1 Vector de afecto modelico `v = (P, A, D)`

Coordenadas en **`[0, 1]³`** (PAD normalizado: placer/valencia, activación, dominancia). Es una **proyección** de señales ya calculadas en el ciclo del kernel, no una entrada independiente del mundo.

| Eje | Rol | Mapeo propuesto desde el estado actual del pipeline |
|-----|-----|------------------------------------------------------|
| **A** (activación) | Alerta ↔ reposo fisiológico del “cuerpo” del agente | **`sigma`** de `InternalState`: `SympatheticModule.SIGMA_MIN` y `SIGMA_MAX` son 0.2 y 0.8 → `A = (sigma - 0.2) / 0.6`, clamp a [0, 1]. |
| **P** (valencia) | Tono agregado “positivo ↔ negativo” *en el juicio ético del episodio* | Normalizar **`moral.total_score`** (o `ethical_score` al registrar el episodio) a [0, 1] con una función fija y documentada (p. ej. lineal por rango observado en simulaciones, o `P = 0.5 + 0.5 * tanh(λ * score)`). **Placeholder** hasta calibración empírica. |
| **D** (dominancia) | Sensación de agencia / control vs fuerzas externas | **`locus_eval.dominant_locus`**: `internal` → 1.0, `balanced` → 0.5, `external` → 0.0. (Alternativa futura: mezclar con `caution_level` de Uchi-Soto en una fórmula acotada.) |

**Nota:** `P` depende de la escala de scores del polo multipolar; cualquier cambio de escala exige **re-calibrar** el mapeo para no romper la interpretación de prototipos.

### 7.2 N prototipos (arquetipos)

- Cada prototipo `k ∈ {0,…,N-1}` tiene:
  - **`id_k`**: identificador estable (`str`, p. ej. `"calma_deliberativa"`).
  - **`c_k = (P_k, A_k, D_k)`** ∈ `[0,1]³`: centro del arquetipo.
  - Opcional: **`label_k`** para narrativa / UI (traducible).

**N mínimo razonable para pruebas:** 4–8 puntos bien separados en el cubo (evitar solapamiento al inicio). Los nombres “emocionales” son **convención pedagógica**; lo formal es solo `c_k`.

### 7.3 Interpolación y “gama” dentro del arquetipo

**Versión v0 (auditable, una sola fórmula):**

1. Dado `v`, para cada prototipo `k`, distancia euclídea `d_k = ‖v - c_k‖₂`.
2. Pesos tipo softmax inverso a distancia:  
   `w_k = exp(-β · d_k) / Σ_j exp(-β · d_j)` con **β > 0** (temperatura: β grande → casi el vecino más cercano; β pequeño → mezcla más uniforme).
3. **Salida principal:** vector **`w`** (mezcla sobre prototipos) + índice **`k* = argmax w_k`** (protagonista del tono).
4. **Gama local (opcional):** si `d_{k*} < ε`, considerar que `v` está **dentro de la gama** del prototipo `k*`; si se desea variación fina sin más dimensiones, interpolar linealmente entre `c_{k*}` y el **segundo mejor** vecino en la envolvente convexa de prototipos cercanos (solo para suavizado narrativo, no para ética).

**Alternativa más barata:** solo **vecino más cercano** + `d_{k*}` como medida de **incertidumbre de tono** (sin softmax).

### 7.4 Dónde encaja en el código (sin alterar la autoridad del núcleo)

| Punto | Rol |
|-------|-----|
| **Tras** `KernelDecision` | Calcular `v` y `w` con datos ya disponibles (`sympathetic_state`, resultado moral, `locus_evaluation`). |
| **`NarrativeEpisode`** | Campos **`affect_pad`** y **`affect_weights`** (opcionales; rellenados cuando el episodio pasa por el kernel con PAD activo). `sigma` sigue guardándose; PAD extiende el registro sin sustituirlo. |
| **Capa LLM / weakness pole** | Usar solo **salida de tono** (texto o matiz), **después** de fijar la decisión ética. |

### 7.5 Invariantes de seguridad conceptual

- Ningún peso `w_k` ni `P/A/D` debe **reemplazar** MalAbs, buffer ni la función de voluntad; no son señales de entrada al veto absoluto en esta especificación mínima.
- Si se implementa: tests de **no regresión** — mismas entradas éticas → misma decisión aunque cambien etiquetas de prototipos o β (solo cambia capa de proyección/narrativa).

### 7.6 Parámetros libres a fijar antes de integrar

`β`, `ε`, conjunto `{c_k}`, función `P(score)`, y si `D` incorpora términos de Uchi-Soto además de locus.

---

## 8. Descargo

Las opiniones aquí son **exploratorias**. No constituyen asesoramiento filosófico, legal ni clínico. El proyecto público sigue gobernado por el código, los tests y la documentación oficial del repositorio.
