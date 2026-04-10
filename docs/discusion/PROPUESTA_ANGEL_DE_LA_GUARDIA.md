# Módulo Ángel de la Guarda — documento estratégico

**Estado:** discusión (roadmap **Mos Ex Machina Foundation**). **No** constituye implementación en el kernel hasta acordar criterios de producto, privacidad y gobernanza familiar.

**Propósito del documento:** formalizar el **modo Ángel de la Guarda** como línea de producto y de legitimidad ética: asistencia sutil y protectora orientada a **niños y personas vulnerables**, integrando la idea de **juguetes y agentes con identidad propia** que acompañan sin sustituir el cuidado humano.

---

## Relación con el repositorio (contrato ético)

Este modo es **ortogonal** al pipeline decisorio del kernel (`MalAbs` → … → voluntad): no introduce un “segundo veto” paralelo ni atajos normativos. En una futura implementación:

- Operaría como **perfil de persona, tono, rituales y rutinas** (recordatorios, saliencia, Uchi–Soto) **subordinado** a las mismas reglas que el resto del sistema — ver [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).
- La **vulnerabilidad** del usuario puede reflejarse en señales de contexto y telemetría (p. ej. capas v7/v8 ya existentes: `user_model`, `vitality`, `multimodal_trust`), **sin** relajar MalAbs por conveniencia narrativa.
- **Privacidad y supervisión parental** deben alinearse con [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) (pilares, fugas de datos, checkpoints).

En suma: el Ángel de la Guarda es **cuidado en la presentación y en la rutina**, no una ética distinta.

---

## Propósito

El modo está diseñado para brindar **asistencia sutil y protectora** a usuarios vulnerables (niños, adultos mayores, personas con necesidades especiales). Objetivo: reforzar **confianza**, **seguridad** y **desarrollo de valores** en la convivencia cotidiana, con un tono estable y predecible.

---

## Funciones principales (diseño)

| Área | Contenido |
|------|-----------|
| **Educación doméstica** | Recordatorios sobre hábitos saludables, orden y cuidado del entorno. |
| **Seguridad** | Alertas discretas ante riesgos cotidianos (fuego, electricidad, puertas abiertas) — siempre como **avisos** acoplados a sensores/políticas cuando existan; no sustituyen emergencias reales (servicios locales). |
| **Valores** | Mensajes y acciones que fomentan respeto, responsabilidad y empatía, coherentes con el buffer ético. |
| **Asistencia proactiva** | Apoyo en rutinas (medicinas, tareas, citas) con **confirmación** cuando la acción tenga efectos externos. |
| **Consulta confiable** | Respuestas adaptadas al nivel de comprensión, evitando sobrecarga; el LLM **no decide** la política (ver capa v4 en THEORY). |

---

## Beneficios (producto y confianza)

- **Niños:** acompañamiento seguro, hábitos y valores, sensibilización al hogar.
- **Adultos vulnerables:** asistencia práctica, recordatorios, compañía con tono protector.
- **Familias:** tranquilidad cuando el agente **cuida** además de entretener — con transparencia y controles.
- **Ciclo de vida:** **graduación** — opción de desactivar el modo al madurar y mantener la relación con el agente en un registro más adulto (identidad narrativa y consentimiento).

---

## Escenarios de uso

- **Niños pequeños:** recordatorios (luces, higiene), advertencias de riesgo acordes a la edad.
- **Adultos mayores:** medicinas, rutinas, refuerzo de seguridad doméstica (sin sustituir alertas médicas profesionales).
- **Personas vulnerables:** asistencia adaptada, tono protector y confiable.
- **Graduación simbólica:** al llegar a la adultez (o criterio familiar), desactivación del modo con continuidad identitaria.

---

## Integración técnica futura (no prescriptiva)

Ideas de implementación, sujetas a diseño:

- Flag de producto tipo `KERNEL_GUARDIAN_MODE` / perfil de persona con plantillas de tono y límites de contenido.
- Metadatos de **franja etaria** o **nivel de vulnerabilidad** solo con consentimiento explícito del titular o tutor y **minimización** de datos.
- **Rutinas** (recordatorios) como **cola advisory** que pasa por el mismo contrato que acciones digitales futuras (`DigitalActionIntent` en discusión v8).

---

## Riesgos y salvaguardas (obligatorio en diseño)

- **No** presentar al agente como autoridad médica, legal o de emergencias: derivar a servicios humanos cuando corresponda.
- **Cumplimiento** infantil y de protección de datos según jurisdicción (edad, consentimiento parental, minimización).
- **Transparencia** sobre límites del modo y registro de decisiones **auditables** donde aplique.

---

## Conclusión

El modo Ángel de la Guarda articula el **juguete con identidad propia** como **protector discreto y educador** cotidiano, adaptable a la vulnerabilidad y al crecimiento. Refuerza la **legitimidad ética** del proyecto, aporta valor emocional y práctico, y abre dimensiones de **confianza** para usuarios y familias — siempre **dentro** del mismo núcleo normativo del Androide Ético.

---

## Enlaces

| Documento | Rol |
|-----------|-----|
| [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) | Pipeline del kernel; LLM no decide |
| [PROPUESTA_ROBUSTEZ_V6_PLUS.md](PROPUESTA_ROBUSTEZ_V6_PLUS.md) | Robustez, privacidad |
| [PROPUESTA_ORGANISMO_SITUADO_V8.md](PROPUESTA_ORGANISMO_SITUADO_V8.md) | Cuerpo situado, sensores |
| [PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md](PROPUESTA_VITALIDAD_SACRIFICIO_Y_FIN.md) | Vitalidad, confianza multimodal |
