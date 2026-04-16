# Roadmap: Arquitectura Somática y Fusión Sensorial (Largo Plazo)

**Estado:** Planificación  
**Prioridad:** Diferida (Posterior a Visión Estructural y Audición Autónoma)  

Este documento mapea la evolución sensorial del androide. Con un núcleo humanoide, **carecer del sentido del cuerpo y el tacto equivale a la parálisis funcional**. La integración de estos módulos en el `EthicalKernel` requerirá abstracciones robustas para evitar saturar el razonamiento ético con ruido mecánico.

## 🚥 Señales de Orquestación

Se aplican las mismas reglas de adopción asíncrona establecidas en `team-task-synchronization.mdc`.
- `[🟩 PENDIENTE]` / `[🟧 DESARROLLANDO POR: <Equipo>]` / `[🟨 ESPERANDO MODULO]` / `[✅ COMPLETADO]`

---

## 🏔️ Arquitectura de Percepción Extendida (Bloques Brutos)

Plataforma modular escalable a conducción autónoma (compartiendo el 70% de los subsistemas sensoriales).

### Bloque S1: Comunicaciones y Telemetría Crítica
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S1.1** | Antenas y Comunicación Multibanda | `[🟩 PENDIENTE]` | WiFi 6/6E, BT LE, 5G, UWB, LoRa para OTA y multi-robot. |
| **S1.2** | GNSS de alta precisión (RTK) | `[🟩 PENDIENTE]` | Navegación exterior, sincronización temporal (GPS/Galileo). |
| **S1.3** | Módulos Computación Distribuida | `[🟩 PENDIENTE]` | Edge + Cloud sync para IA pesada vs Latencia baja. |

### Bloque S2: Percepción Espacial Activa y Conducción
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S2.1** | LIDAR / Radar / ToF | `[🟩 PENDIENTE]` | SLAM y detección en oscuridad/niebla (automotriz). |
| **S2.2** | Sensores Proximidad y Colisión | `[🟩 PENDIENTE]` | IR, Ultrasonido, Bumpers. Primera línea de defensa. |
| **S2.3** | Interfaces de Control Vehicular | `[🟩 PENDIENTE]` | CAN bus, LIN bus, OBD-II para conducción autónoma. |

### Bloque S3: Propiocepción y Equilibrio Automotriz
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S3.1** | Sensores Inerciales Avanzados | `[🟧 DESARROLLO]` | IMUs para balance, detección de caídas y estabilidad. |
| **S3.2** | Modulos de Seguridad y Redundancia | `[🟩 PENDIENTE]` | Watchdogs, baterías auxiliares. |

### Bloque S4: Haptics y Manejo Seguro
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S4.1** | Fuerza, Torque y Presión | `[🟩 PENDIENTE]` | Piel artificial, feedback háptico para volante/objetos. |
| **S4.2** | Interfaces Hombre-Máquina (HMI) | `[🟩 PENDIENTE]` | Pantallas, proyector, LEDs de estado y voz sintetizada. |

### Bloque S5: Extensiones Auxiliares y Contexto Avanzado
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S5.1** | Smartphone como Módulo Auxiliar | `[🟩 PENDIENTE]` | Uso de array de procesador/cámaras portable para telemetría. |
| **S5.2** | Dron como Extensión Aérea | `[🟩 PENDIENTE]` | Visión aérea (Mos Ex Machina ext), inspección y mapeo rápido. |
| **S5.3** | Sensores Medioambientales | `[🟩 PENDIENTE]` | Temperatura, CO2, luz y ruido ambiental. |

### Bloque S6: Percepción Social y Ética
| ID | Tarea | Estado | Notas |
|:---|:---|:---|:---|
| **S6.1** | Sensores Biométricos | `[🟩 PENDIENTE]` | Leer ritmo cardíaco/temperatura del humano cercano para Ethos. |
| **S6.2** | IA de Percepción Semántica | `[🟩 PENDIENTE]` | Intenciones, lenguaje corporal, e inferencia compleja. |

---

## 🔄 Registro de Progreso

- **2026-04-15:** Creación inicial del Roadmap Jerárquico Somático como meta a largo plazo. Los esfuerzos actuales del equipo se concentran puramente en **Visión (PLAN_VISION)** y **Audición (PLAN_AUDIO)**.
- **2026-04-15:** Inicio de **Bloque S3 (Propiocepción)**. Antigravity expande el contrato `SensorSnapshot` para incluir `is_falling`, `is_obstructed`, `motor_effort_avg` y `stability_score`, e integra los nudges somáticos en la percepción del kernel.
- **2026-04-15:** Incorporación de la arquitectura de **Sociabilidad Encarnada** (Bloques S7-S10) descritos en [`PROPOSAL_EMBODIED_SOCIABILITY.md`](PROPOSAL_EMBODIED_SOCIABILITY.md) para garantizar la aceptación social e interacciones no amenazantes.
