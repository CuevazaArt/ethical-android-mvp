# Trazabilidad: implementaciones recientes (Guardian, v9, v10)

Este documento **consolida** los componentes y conceptos incorporados al repositorio en el ciclo de trabajo reciente, con **sustento bibliográfico** en el formato del repositorio: referencias numeradas según **[BIBLIOGRAPHY.md](../BIBLIOGRAPHY.md)** (índice al final de ese archivo).

**Coherencia:** Ninguna de estas capas altera el pipeline normativo **MalAbs → … → voluntad**; son telemetría, tono LLM, candidatos explícitos o señales acotadas, como documentan [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) y las PROPUESTA enlazadas.

---

## Tabla componente → código → sustento

| Concepto | Implementación (módulo / integración) | Sustento bibliográfico (refs.) |
|----------|--------------------------------------|----------------------------------|
| **Modo Ángel de la Guarda** (tono protector opt-in) | `src/modules/guardian_mode.py`; `KERNEL_GUARDIAN_MODE`; `process_chat_turn` → `communicate` | Principios de IA en sociedad y alineación de valores [15], [17]; interacción humano–agente y confianza [67], [69]. |
| **Disonancia epistémica / consenso sensorial** (v9.1) | `src/modules/epistemic_dissonance.py`; tras `multimodal_trust`; JSON `epistemic_dissonance` | Incertidumbre e información [21]; razonamiento causal / coherencia entre fuentes [24], [25]; sensores y estimación [61]; límites de interpretabilidad ante señales contradictorias [71]. |
| **Candidatos generativos** (“tercera vía”, v9.2) | `src/modules/generative_candidates.py`; `CandidateAction.source` / `proposal_id`; `KERNEL_GENERATIVE_ACTIONS` | Dilemas morales empíricos y trade-offs [18]; agentes racionales y espacio de planes [31]; modos deliberativos vs rápidos [41]. |
| **Diplomacia en zona gris** (v10) | `src/modules/gray_zone_diplomacy.py`; hints en `weakness_line`; `KERNEL_GRAY_ZONE_DIPLOMACY` | Deliberación bajo tensión cognitiva [41]; ética del discurso y acuerdo racional [73]; explicabilidad y transparencia ante el usuario [15]. |
| **Registro de aprendizaje de habilidades** (v10) | `src/modules/skill_learning_registry.py`; auditoría en `execute_sleep` | Gobernanza y alcance de capacidades [74]; marcos de principios para IA [15]; alineación “constitucional” y restricción de comportamiento [90]. |
| **Marcadores somáticos** (v10) | `src/modules/somatic_markers.py`; `apply_somatic_nudges` sobre `signals` | Marcadores somáticos y emoción en la decisión [91]; cibernética y lazo sensor–actitud [59]; vehículos sensoriales simples [60]. |
| **Metaplan / metas maestras** (v10, sesión) | `src/modules/metaplan_registry.py`; hint opcional al LLM | Planes persistentes e intención [33]; agentes y planificación [31]. |
| **Antispoof multimodal** (contexto v8) | `src/modules/multimodal_trust.py` (ya existente; v9.1 lo combina) | Misma línea que disonancia epistémica [21], [24], [61]. |

---

## Documentación de diseño asociada

| Documento | Contenido |
|-----------|-----------|
| [discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md](discusion/PROPUESTA_ANGEL_DE_LA_GUARDIA.md) | Producto y contrato Ángel de la Guarda |
| [discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md](discusion/PROPUESTA_CAPACIDAD_AMPLIADA_V9.md) | Pilares v9 (epistémica, generativa, enjambre, metaplanificación) |
| [discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](discusion/PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md) | Diplomacia, skills, soma, metaplan operativo |

---

## Próxima jornada de desarrollo (plan propuesto)

Prioridad sugerida alineada con el repo y lo ya esbozado en PROPUESTA:

1. **Persistencia de metas y marcadores** — Extender `KernelSnapshotV1` o campo auxiliar para `MetaplanRegistry` y, si aplica, pesos de `SomaticMarkerStore`; tests de round-trip checkpoint. *Sustento:* continuidad narrativa [40], [97], [98]; persistencia [104].

2. **9.2+ generativa con LLM local** — Parser de candidatos desde salida JSON del modelo bajo `KERNEL_GENERATIVE_LLM=1`; tests de propiedad MalAbs. *Sustento:* [81]–[83], [31].

3. **9.4 metaplanificación** — Filtrado advisory explícito frente a `MasterGoal` en `drive_intents` o hints adicionales; consentimiento documentado. *Sustento:* [33], [17], [15].

4. **9.3 enjambre** — Solo si hay diseño de amenazas; prototipo fuera del núcleo. *Sustento:* [52], [57], [58].

5. **Ángel de la Guarda (producto)** — Rutinas y UI; sin tocar veto ético. *Sustento:* [67]–[70], [15].

---

*Ex Machina Foundation — trazabilidad de implementación; alinear con [BIBLIOGRAPHY.md](../BIBLIOGRAPHY.md) para citas académicas completas.*
