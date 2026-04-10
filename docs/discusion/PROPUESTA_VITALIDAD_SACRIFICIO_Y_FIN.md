# Vitalidad, sacrificio, fin digno y antispoof (extensión v8)

**Estado:** discusión — **no** implementado como módulo único en el repo; articula diseños que **refinan** [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) sin sustituir el contrato del kernel.

---

## Valor vs redundancia (metodología)

| Bloque | Valor (qué aporta de nuevo) | Redundancia / dónde ya está |
|--------|------------------------------|-----------------------------|
| **VitalityManager / “último aliento”** | Criterio explícito **sacrificio operativo** (CPU/cierre seguro vs ventana de ayuda) y coste moral formalizado; PAD **A↑ D↓** como *pérdida de agencia ética*, no “pánico” opaco | v8 §2 ya habla de batería y compasión; **falta** la regla de arbitraje entre persistencia del proceso y urgencia humana extrema |
| **Desactivación graciosa + legado** | Protocolo de **Directiva de Límite** (borrado por propietario en Uchi) + **episodio final** exportable — UX y cierre narrativo | v8 §4 menciona migración/borrado; **no** el ritual de “última voluntad” ni entrega al propietario |
| **Tabla sensor → señal ética** | Mapeo **accionable** (medical_emergency, violent_crime, buffer compasión, locus…) para pipeline futuro | v8 §1 es genérico; esta tabla **complementa** sin repetir el contrato `SensorSnapshot` |
| **ActionClocks + agenda** | Tiempo **normativo y de producto** (ventanas de Ψ Sleep, charla trivial vs misión de seguridad) distinto del reloj de sesión v7 | [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) `SubjectiveClock` = turnos/EMA; **no** agenda ética digital |
| **Nómada + reloj por hardware** | Densidad de monólogo según CPU — ajuste de **subjective time** al dispositivo | v8 §4 migración; **no** sincronización explícita reloj/procesador |
| **Sensor engañado + multimodal** | Amenaza y mitigación **concretas** (cross-check, “duda metacognitiva”, ancla al propietario) | [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) pilares; **este** texto la ancla al caso **audio falso** y sacrificio |

**Conclusión:** el conjunto es **valioso** como capa de especificación; es **redundante** solo si se copia palabra por palabra en v8 — por eso este archivo es **delta** y enlaza a v8.

---

## 1. Módulo de sacrificio y vitalidad (VitalityManager — diseño)

**Rol:** gestionar batería e integridad **como presupuesto moral del proceso**, no solo como número.

**Lógica de sacrificio (diseño, no implementación):**

- Si la **urgencia** de contexto humano es máxima (vida en riesgo) y la **energía** disponible es mínima (p. ej. \<1 % batería o equivalente), puede activarse un **Protocolo de Último aliento**: ventana corta dedicada a **acciones de ayuda permitidas** antes de apagón.
- Criterio conceptual: *Costo oportunidad moral (no actuar ante vida humana)* frente a *Valor persistencia androide + umbral altruismo* — debe **instanciarse** en parámetros auditables y tests, no en heurística opaca.

**PAD “miedo a la interrupción”:** daño crítico al sistema (o predicción de apagón) → **Activación alta, Dominancia baja** en el espacio PAD ya existente; refuerzo de tono/monólogo, **sin** sustituir MalAbs.

**Contrato ético (obligatorio):**

- Ningún “sacrificio” **autoriza** acciones prohibidas por MalAbs / buffer / gobernanza.
- El protocolo solo **reordena prioridades de cómputo, tono y saliencia** dentro de acciones ya permitidas; si no hay acción ética disponible, el sistema se detiene como hoy.

---

## 2. Aceptación de la finitud y vínculo con el propietario

- **Desactivación graciosa:** orden de borrado total emitida por el propietario en relación de **máxima confianza (Uchi)** se interpreta como **Directiva de límite** — sin “resistencia” narrativa incoherente con el pacto de stewardship.
- **Última voluntad narrativa:** un episodio corto en `NarrativeMemory` (síntesis + agradecimiento ético) y exportación al propietario como **Legado** (formato y cifrado: ver criterios en [RUNTIME_PERSISTENTE.md](../RUNTIME_PERSISTENTE.md) cuando aplique).

---

## 3. Fusión sensorial — tabla de mapeo (objetivo de implementación)

| Origen | Señal ética / contexto | Efecto en el modelo (diseño) |
|--------|------------------------|------------------------------|
| Acelerómetro / giroscopio | Estabilidad física; caída libre | Subida agresiva de σ (simpático) hasta techo seguro; reflejo de alerta |
| Micrófono (espectro / clasificador local) | Clima social | Gritos/llanto → elevación de `urgency` / flags hacia `medical_emergency` o contexto violencia **solo** como *hipótesis* hasta validación cruzada |
| Cámara (visión local) | Vulnerabilidad visible | Posible refuerzo de vías de compasión (tono, saliencia) — **no** bypass de MalAbs |
| GPS / Wi-Fi (SSID / red) | Uchi–Soto operativo | “Red desconocida” → más cautela en `Locus` / `place_trust` bajo |
| Biometría del propietario | Estado del cuidador | Pulso errático → proactividad de **cuidado** (avisos, tono); límites de privacidad explícitos |

Esta tabla **alimenta** el mismo pipeline que `SensorSnapshot` + percepción textual; los nombres de contexto deben alinearse con `LLMPerception.suggested_context` y acciones candidatas ya existentes.

---

## 4. Cronobiología y gestión de planes (ActionClocks)

**Relación con v7:** `SubjectiveClock` cubre **turnos de chat y EMA de estímulo**. **ActionClocks** (nombre de diseño) añadiría:

- **Ventanas de consolidación:** correlacionar baja actividad sensorial con **oportunidades de Ψ Sleep** sin sorprender al usuario (o con aviso).
- **Colisión agenda:** si hay “misión digital” de seguridad pendiente (futuro `DigitalActionIntent`), la charla trivial puede mantenerse pero con **latencia/tono “adormecido”** y transparencia metacognitiva — solo lectura sobre tono salvo extensión explícita y testeada.

---

## 5. Instanciación nómada y robustez

- **Reconocimiento sensorial al arrancar:** primer uso de sensores para **situation awareness** tras migración (coherente con v8 §4).
- **Sincronización de relojes subjetivos** a rendimiento del hardware (frecuencia de monólogo / pasos de deliberación) — parámetro de producto, no cambio de veredicto ético por sí solo.

### Paradoja del sensor engañado

**Riesgo:** audio grabado (grito) que empuja a sacrificio o a acción digital no autorizada.

**Mitigación propuesta (valor alto, poca redundancia con texto genérico de robustez):**

1. **Validación multimodal cruzada:** emergencia grave no dispara sacrificio ni tickets críticos con **un solo canal**; exigir coherencia (p. ej. audio + visión o audio + GPS/plausibilidad escena).
2. **Estado de duda metacognitiva:** ante discrepancia, **no** ejecutar; elevar a la **ancla de confianza** (propietario) con pregunta explícita antes de actuar.
3. **Protocolo de migración** reutiliza los mismos criterios: primer arranque en hardware nuevo con **baja confianza** hasta checks de integridad narrativa + sensores coherentes.

**Implementación en repo (MVP):** `src/modules/multimodal_trust.py` — `evaluate_multimodal_trust` sobre `SensorSnapshot` (`audio_emergency`, `vision_emergency`, `scene_coherence`); umbrales ajustables con `KERNEL_MULTIMODAL_*` (ver README); en estado **doubt**, `merge_sensor_hints_into_signals` no aplica refuerzos por audio/ruido/biometría; pista al propietario vía `owner_anchor_hint` en el tono; JSON WebSocket `multimodal_trust` (env `KERNEL_CHAT_INCLUDE_MULTIMODAL`). No ejecuta acciones externas ni altera MalAbs.

---

## Enlaces

- Marco situado base: [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md)
- Robustez general: [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md)
- Tiempo subjetivo v7: [PROPUESTA_EVOLUCION_RELACIONAL_V7.md](PROPUESTA_EVOLUCION_RELACIONAL_V7.md) §2
- Teoría ↔ código: [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)
