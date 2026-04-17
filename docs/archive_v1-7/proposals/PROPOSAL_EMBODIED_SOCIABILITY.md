# Sociabilidad Encarnada y Percepción No Amenazante (Bloques S7+ y G)

Para lograr una integración social estable, el androide debe trascender la mera funcionalidad técnica. La aceptación humana depende de la previsibilidad, la empatía funcional y la adaptación cultural. Un robot seguro que se mueve de forma errática o que viola el espacio personal será percibido como una amenaza.

Esta propuesta integra los requerimientos críticos de interacción social en la arquitectura expandida.

---

## 🏔️ Arquitectura de Sociabilidad Encarnada (Nuevos Bloques)

Estos bloques se añaden a la Arquitectura de Percepción Extendida (`PLAN_SOMATIC_HARDWARE_ROADMAP.md`).

### Bloque S7: Comportamiento No Amenazante (Cinemática Social)
| ID | Tarea | Notas |
|:---|:---|:---|
| **S7.1** | Cinemática Suavizada (Soft Robotics) | Filtros de aceleración para evitar movimientos bruscos o robóticos que generen sobresalto. |
| **S7.2** | Proxémica Dinámica | Mantenimiento de la distancia interpersonal adecuada, ajustable según el contexto (íntima, personal, social, pública). |
| **S7.3** | Señalización de Intención | Uso de LEDs, proyecciones u orientación del torso/mirada para anunciar el siguiente movimiento antes de realizarlo. |
| **S7.4** | Limitadores Activos de Fuerza | Zonas seguras donde la fuerza y velocidad se reducen automáticamente al detectar proximidad humana. |

### Bloque S8: Lenguaje Corporal y Empatía Funcional
| ID | Tarea | Notas |
|:---|:---|:---|
| **S8.1** | Mimetismo Postural Básico | Ajuste de la postura (orientación del torso, mirada) para demostrar atención y respeto. |
| **S8.2** | Modulación del Ritmo | Pausas y velocidad de movimiento coherentes con la interacción. |
| **S8.3** | Detección de Estado Humano (Inferencia Rápida) | Identificar cansancio, estrés o confusión para ajustar la interacción. |
| **S8.4** | Señales de Empatía Funcional | Respuestas (físicas o verbales) calmadas y consistentes, sin simular emociones humanas complejas falsas. |

### Bloque S9: Ética Contextual y Adaptación Cultural
| ID | Tarea | Notas |
|:---|:---|:---|
| **S9.1** | Mapas de Normas Sociales | Módulo que almacena jerarquías, turnos de conversación, límites de contacto y privacidad del entorno actual. |
| **S9.2** | Selector de Contexto Cultural | Ajuste de parámetros proxémicos y de cortesía según la cultura dominante parametrizada. |
| **S9.3** | Aprendizaje de Preferencias Individuales | Memoria `UchiSoto` expandida para recordar ritmo, temas y límites personales de humanos recurrentes. |

### Bloque S10: Transparencia y Seguridad Emocional
| ID | Tarea | Notas |
|:---|:---|:---|
| **S10.1** | Narrador de Acciones (Explainability) | Capacidad de articular: qué hace, por qué, qué hará después y cómo detenerlo. |
| **S10.2** | Capacidad de Desaparecer | Protocolos de no-intervención activa para respetar la privacidad y el espacio humano. |
| **S10.3** | Anticipación de Incomodidad | Monitor de la tensión o desconfianza en humanos cercanos, ajustando o deteniendo el comportamiento. |
| **S10.4** | Solicitud de Ayuda | Protocolos claros (visuales o acústicos) para indicar que el androide necesita intervención humana, reduciendo la incertidumbre. |

---

## Integración con Módulos Existentes

- **`UchiSotoModule` (Bloque S9.3):** Se expandirá para no solo almacenar el nivel de confianza, sino también las preferencias interaccionales (distancia, tono).
- **`EthicalKernel` (Bloque S9.1):** Necesitará un inyector de contexto cultural pre-argmax para ajustar los pesos o vetar acciones que violen normas locales severas.
- **`NarrativeMemory` (Bloque S10.1):** Será la base para la explicabilidad de las acciones pasadas y las intenciones futuras.
- **`SomaticSignalMapper` (S7.4):** Limitará el riesgo aceptable en función de la proximidad.
