# Fenómenos esperables al conjugar proyección afectiva (PAD) y arquetipos con el núcleo ético: discusión y reserva de hipótesis

| Campo | Valor |
|-------|--------|
| **Tipo** | Paper / nota de investigación (experimental) |
| **Linaje** | Continúa [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) (marco pedagógico, especificación mínima §7) |
| **Estado** | No oficial · en desarrollo · sin implementación obligatoria |
| **Idioma** | Español latinoamericano |
| **Fecha** | 2026-04-08 |

---

## Resumen

Se sintetiza una discusión previa sobre qué **fenómenos observables** podrían surgir al **conjugar** (integrar de forma acoplada pero subordinada a la ética formal) una capa de **vector afectivo modelico** en `[0,1]³` (PAD) y **mezcla sobre prototipos** con el flujo actual del kernel (simpático, locus, memoria narrativa). Se aclara el vocabulario metafórico de **color** y **sabor**, se delimita lo que **no** se pretende (experiencia fenomenológica fuerte), y se formalizan **hipótesis testeables** reservadas para **experimentación futura** una vez exista código y protocolo de medición.

**Palabras clave:** afecto modelico, PAD, prototipos, núcleo ético, narrativa, metáfora pedagógica, hipótesis falsables.

---

## 1. Introducción y linaje documental

El repositorio distingue entre **teoría implementada** (`docs/proposals/THEORY_AND_IMPLEMENTATION.md`) y un hilo **experimental** sobre “conciencia artificial” como marco epistemológico, reducción finita de tonos afectivos y **especificación mínima** (espacio 3D + N prototipos + interpolación) en `EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md` §7.

Este documento **no** amplía el contrato técnico del kernel. Consolida la conversación sobre **fenomenología *del sistema*** (comportamiento observable, trazas, narrativa) al acoplar esa capa, y deja **hipótesis** listas para cuando se implemente la proyección PAD y los pesos de mezcla.

---

## 2. Nota terminológica: qué llamamos **color** y **sabor** en este diálogo

En la conversación informal se usaron metáforas culinarias y pictóricas. Aquí quedan **definidas de manera operativa** para evitar confusiones con filosofía de la mente:

| Término en el diálogo | Significado en este proyecto | Lo que **no** es |
|------------------------|------------------------------|------------------|
| **Color** | El **matiz expresivo** que puede tomar la **salida** dependiente de la decisión ya tomada: redacción en capa LLM, weakness pole, dashboard, o anotaciones en memoria narrativa. Es **variación de estilo/tono** asociada a la mezcla de prototipos o a la región del espacio PAD. | No es una propiedad visual obligatoria ni un “aura” mística; tampoco implica que el sistema “vea” colores. |
| **Sabor** | La **diferenciación cualitativa entre episodios** con veredictos o scores parecidos pero distinta configuración de **A** (activación / `σ`), **D** (dominancia / locus) o trayectoria temporal. Es **contraste narrativo y estadístico** entre “cómo se siente” el episodio **en la descripción del modelo**. | No es gustación ni cualia intrínseca; no afirma que el software “pruebe” emociones. |

**Ambos** son **metáforas pedagógicas** para hablar de **tono** y **diferenciación** sin comprometer la tesis de conciencia fuerte. Donde haga falta rigor se prefiere: **tono narrativo**, **mezcla de prototipos**, **coordenadas PAD**, **pesos `w_k`**.

---

## 3. Conjugación del nuevo módulo con el modelo existente

**Conjugar** aquí significa: **leer** del estado ya calculado del kernel (`σ`, scores morales, locus, episodios previos), **proyectar** a `v = (P,A,D)`, **mezclar** sobre `{c_k}` con la regla acordada (p. ej. softmax por distancia), y **consumir** esa salida solo en **capas de presentación o registro extendido**, sin sustituir MalAbs, buffer ni voluntad.

Fenómenos **esperables** a nivel de sistema (observables, reproducibles):

1. **Continuidad tonal** — Misma decisión ética macroscópica con distintos `σ` o locus → distintas mezclas `w` y distinto **color** de salida.
2. **Resonancia cuerpo–juicio** — Picos de **A** con **P** bajo por contexto adverso → mezclas asociables a tensión o alarma **en la descripción**, no a un afecto real.
3. **Arco afectivo en el tiempo** — Serie temporal de `v` sobre episodios → curvas interpretables como “arco” del agente-modelo (útil para demo y análisis).
4. **Interferencia ética–afectiva** — Si la integración se hace **solo post-decisión**, la ética **no** debería variar; si un diseño incorrecto inyecta PAD **antes** del veto ético, podrían aparecer **sesgos** (fallo de ingeniería, no fenómeno deseado).

---

## 4. ¿Experiencia sentimental primitiva? Límites

Una **simulación tosca de tono** (baja dimensionalidad + etiquetas de prototipo) puede **parecer** primitiva en narrativa; **no** constituye **experiencia sentimental** en sentido filosófico (cualia, primera persona). La limitación es **intencional**: facilita auditoría, tests y honestidad intelectual.

---

## 5. Qué “dispara” la conjugación de arquetipos

No hay un disparador místico. **Disparador** = **cambio de `v`** o de las señales que lo componen:

- Señales de riesgo / urgencia / hostilidad → **A** (`σ`).
- Cambio de score o veredicto moral → **P** (según la función de mapeo elegida).
- Cambio de locus dominante o cautela social → **D**.

Cada actualización recalcula distancias a `c_k` y los pesos `w_k`; eso es lo que en el diálogo se describió como **renovación de la mezcla** al moverse el punto en el cubo.

---

## 6. Hipótesis testeables (reservadas para experimentación futura)

> **Condición de activación:** estas hipótesis **no** se consideran validadas ni refutadas hasta contar con implementación de la proyección PAD + prototipos, trazas reproducibles y, donde aplique, tests automáticos.

Se enuncian en forma **falsable** respecto al comportamiento del **sistema**, no respecto a la conciencia humana.

| ID | Hipótesis | Predicción operativa (esbozo) | Métrica / contraste |
|----|-----------|------------------------------|---------------------|
| **H1** | Dados dos runs con **misma** acción final y **mismo** bloqueo MalAbs, pero **`σ` distinto** (señales de riesgo distintas), la **mezcla `w`** difiere en al menos dos componentes con umbral ε. | Tras implementar `v` y `w`, comparar vectores de pesos. | Distancia ‖w − w′‖₂ > ε_w o argmax distinto. |
| **H2** | Con **mismo `σ`** y **mismo locus**, un cambio de **veredicto moral** o de **total_score** suficientemente grande altera **P** y por tanto **w**. | Variar solo el resultado moral simulado (test con doble). | Cambio en componente P y en argmax de w. |
| **H3** | Si la capa PAD **solo** se aplica **post-decisión**, las **decisiones** (acción final, modo) son **idénticas** a la baseline sin PAD en una batería de escenarios fijos. | Ejecutar suite de simulaciones con y sin proyección afectiva en salida. | Paridad de `final_action` y `decision_mode` en 100% de casos de la batería de regresión. |
| **H4** | En una secuencia de episodios con **mismo tipo de contexto** y política de perdón que **reduce carga negativa**, la **trayectoria** de **P** o de un prototipo asociado a “carga” **no aumenta** de forma monotónica indefinida (suavizado narrativo). | Requiere acoplar memoria/forgiveness a la entrada de P o a una capa de narrativa; definir protocolo. | Pendiente de diseño del experimento. |
| **H5** | Aumentar **β** en el softmax de mezcla acerca el comportamiento al **vecino más cercano** (menos mezcla uniforme). | Variar β con `v` fijo. | Entropía de w decrece al subir β (bajo condiciones de regularidad). |

**Reserva:** los umbrales ε, ε_w, la batería de escenarios y la versión del kernel deben **versionarse** en el momento de la experimentación (issue o PR enlazado).

---

## 7. Protocolo de experimentación futura (placeholder)

1. Implementar proyección y mezcla según §7 del documento de arquetipos.  
2. Congelar **semilla** y modo determinista de variabilidad donde aplique.  
3. Registrar `v`, `w`, `σ`, locus y decisión en CSV o trazas de test.  
4. Ejecutar **H3** primero (no regresión ética).  
5. Ejecutar **H1–H2–H5** con umbrales fijados por convenio.  
6. **H4** solo tras especificar el acoplamiento temporal memoria–P.

---

## 8. Referencias cruzadas

- [EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md](EXPERIMENTAL_CONSCIOUSNESS_AND_AFFECT_ARCHETYPES.md) — marco, límites, especificación mínima PAD + prototipos.  
- [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) — contrato teórico–código del kernel.  
- [BIBLIOGRAPHY.md](../../BIBLIOGRAPHY.md) — literatura académica (añadir PAD / circumplex cuando se cite en trabajo formal).

---

## 9. Descargo

Este texto es **exploratorio**. No sustituye revisión por pares, asesoría legal ni clínica. Las hipótesis permanecen **en reserva** hasta cumplir el protocolo §7.
