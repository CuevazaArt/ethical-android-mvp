# Capacidad ampliada — v9 (influencia, resolución compleja, horizonte largo)

**Estado:** discusión estratégica + **fase 9.1 parcialmente implementada** en repo (telemetría epistémica; sin cambio del pipeline normativo MalAbs → … → voluntad).

**Relación con versiones anteriores**

| Versión | Enfoque |
|---------|---------|
| **v6–v7** | Reflexión, saliencia, identidad, capas relacionales y teleología **cualitativa** en JSON |
| **v8** | Organismo situado: `SensorSnapshot`, fusión en señales, antispoof multimodal, vitalidad |
| **v9** | Cuatro pilares que **amplían percepción, opciones candidatas, colaboración distribuida y planificación** — siempre **subordinados** al kernel |

**Contrato ético (invariante)**  
El **kernel** sigue siendo la autoridad sobre acciones permitidas y veto MalAbs. Cualquier LLM, simulador o red **propone, etiqueta o prioriza hipótesis**; no sustituye la función de voluntad ni abre atajos normativos. La documentación de producto debe mantener esta línea para no confundir “creatividad” con “nueva ética”.

---

## Pilar 1 — Inferencia epistémica avanzada (“detector de realidad”)

**Problema:** Con micrófonos y cámaras de alta calidad, el sistema puede recibir **deepfakes** o señales contradictorias. Hace falta no solo “percibir” sino **validar coherencia entre modalidades**.

**Diseño:** **Consenso / disonancia de sensores** — comparar hipótesis de alarma (p. ej. audio de auxilio) con inercia, visión y coherencia de escena.

**Ejemplo canónico:** Grito de auxilio fuerte en audio, **acelerómetro en reposo**, visión sin indicios de estrés → **disonancia de realidad** (posible manipulación o error).

**Capacidad:** Navegar entornos de desinformación; proteger al usuario de estafas o presión externa **sin** relajar MalAbs por narrativa.

**Riesgos:** No usar la etiqueta “disonancia” para **anular** deberes mínimos cuando hay incertidumbre real; mantener humildad epistémica en el tono (LLM).

**Implementación en repo (9.1)**

- Módulo `src/modules/epistemic_dissonance.py`: `assess_epistemic_dissonance(snapshot, multimodal_assessment)` → telemetría `active` / `score` / `reason`; opcional **hint** de comunicación (tono).
- WebSocket: campo JSON `epistemic_dissonance` (omisible con `KERNEL_CHAT_INCLUDE_EPISTEMIC=0`).
- Umbrales opcionales: `KERNEL_EPISTEMIC_AUDIO_MIN`, `KERNEL_EPISTEMIC_MOTION_MAX`, `KERNEL_EPISTEMIC_VISION_LOW`.

**Extensión futura:** Reglas adicionales, calibración por dispositivo, correlación con `multimodal_trust` de forma explícita en la API de producto.

---

## Pilar 2 — Imaginación ética y creatividad (tercera vía)

**Problema:** Hoy el kernel elige entre **acciones candidatas** dadas. En dilemas estructurales, todas pueden ser malas en distinto grado.

**Diseño:** **Simulación generativa de escenarios** — el LLM local (u otro generador) propone **nuevas** `CandidateAction` hipotéticas (“¿frenar el tranvía remoto si existiera canal digital?”), que entran al **mismo** `process(...)` que el resto.

**Capacidad:** Pasar de “clasificador sobre lista fija” a **explorador de espacio de acciones** bajo las mismas reglas.

**Riesgos altos**

- Confusión entre **propuesta narrativa** y **acción autorizada**.
- Acciones “creativas” que eluden MalAbs si no se modelan como candidatos explícitos auditables.

**Requisitos de diseño (futuro 9.2)**

- Trazabilidad: cada candidato generado con ID, texto y origen (`generative_proposal`).
- Límite de candidatos y revisión determinista antes de `process`.
- Tests de propiedad: “generative layer no puede saltarse MalAbs”.

---

## Pilar 3 — Conciencia colectiva (protocolo de enjambre ético)

**Problema:** Instancias nómadas en distintos hardware pueden **discrepar** bajo estrés o información parcial.

**Diseño:** **Mesh / P2P** entre nodos de confianza (Bluetooth, Wi‑Fi local) para intercambiar **resúmenes de veredicto** o firmas, idealmente sin revelar identidad ni contenido privado.

**Capacidad:** Justicia distribuida en emergencias masivas sin nube central.

**Riesgos:** Superficie de ataque (nodos maliciosos, Sybil), complejidad de **pruebas de conocimiento cero** en dispositivos restringidos, gobernanza legal.

**Estado en repo:** **No implementado** — documento de diseño y dependencias (criptografía, modelo de amenazas). Precede a cualquier código de red.

---

## Pilar 4 — Metaplanificación y teleología (objetivos a largo plazo)

**Problema:** El sistema reacciona en segundos; muchos objetivos humanos son **días o meses**.

**Diseño:** **Jerarquía de planes** — metas maestras declaradas (p. ej. salud financiera) que **filtran** sugerencias y recordatorios en micro-decisiones.

**Capacidad:** “Arquitecto de vida” coherente con valores **declarados** por el usuario.

**Riesgos:** Paternalismo, manipulación si las metas no son transparentes y revocables; tensión con autonomía.

**Estado en repo:** Base relacional ya existe (`teleology_branches`, `user_model`, cronobiología). La v9 formaliza **persistencia de metas** y **pesos** como trabajo futuro (9.4), con consentimiento explícito y UX de control.

---

## Plan de integración por fases

| Fase | Contenido | Estado |
|------|-----------|--------|
| **9.1** | Disonancia epistémica / consenso sensorial (telemetría + hint de tono) | **Parcial en código** (`epistemic_dissonance.py`, WebSocket) |
| **9.2** | Candidatos generativos acotados + trazabilidad + tests | Diseño; código pendiente |
| **9.3** | Enjambre P2P + privacidad (ZK u otra capa) | Solo documentación |
| **9.4** | Metas maestras persistentes + filtrado advisory | Diseño; extiende v7 |

**Dependencias sugeridas:** 9.1 aprovecha v8 (`SensorSnapshot`, `multimodal_trust`). 9.2 depende de un contrato claro para `CandidateAction`. 9.3 es independiente del kernel numérico pero exige runtime de red. 9.4 se apoya en persistencia y UI de consentimiento.

---

## Enlaces

| Documento | Rol |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Pipeline; LLM no decide |
| [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) | Sensores v8 |
| [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md) | Multimodal antispoof |
| [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) | Teleología cualitativa, usuario |
