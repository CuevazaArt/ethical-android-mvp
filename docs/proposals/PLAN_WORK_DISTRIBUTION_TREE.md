# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el volumen de trabajo arquitectónico definido para el Ethos Kernel. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**, fusionado ahora con el **Motor de Encanto Multimodal (Charm Engine)** para una interacción persuasiva y segura.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ✅ Módulos Consolidados / Completados
*Se han colapsado los módulos tras su finalización exitosa. Referirse al `CHANGELOG.md` para trazabilidad.*
- **Módulo 0**: Estabilización Pragmática y Desmonolitización (Lóbulos, WebSockets Concurrentes) [DONE]
- **Módulo 1**: Infraestructura DAO Híbrida (Simulación Local Mock) [DONE]
- **Módulo 2**: Simulador, Red-Teaming y Validación Funcional [DONE]
- **Módulo 3**: Sociabilidad Encarnada y Cinemática (S-Blocks) [DONE]
- **Módulo C**: Profundidad Cognitiva, BMA, y Gobernanza Runtime [DONE]
- **Módulo 6 & 7**: Swarm Ethics, Justicia Restaurativa y Slashing [DONE]
- **Módulo E (Core)**: Integración base del Motor de Encanto y Salvaguardas Contra Adicción Parasocial (L1 Antigravity) [DONE]

---

### 🟢 Módulo S: Encarnación Activa y Hardware Bridge (Nomad PC/Mobile) [PRIORIDAD 0]
*Responsabilidad: Nivel 2 (Team Cursor)*
*Objetivo: Integrar sensores reales (visión/audio) provenientes de un dispositivo móvil LAN como inputs de inferencia física, abandonando las señales de prueba simuladas.*

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video y audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona.
- **Bloque S.2: Calibración Termo-Visual Continua**
  - Tarea S.2.1: Refinar las interrupciones del `VitalityAssessment` utilizando la telemetría real transmitida por el *Nomad Bridge*.

### 🟣 Módulo E: Motor de Encanto y Renderizado Somático (Fase 2) [PRIORIDAD 1]
*Responsabilidad: Nivel 2 (Team Cursor y Claude)*
*Objetivo: Empalmar la capa de presentación (CharmEngine) recién acoplada en el Kernel con los sistemas físicos y mejorar la persuasión prosódica empática.*

- **Bloque E.1: Puente Somático-Hardware (Team Cursor)**
  - Tarea E.1.1: Conectar el `GesturePlanner` y los vectores somáticos en tiempo real (provenientes de la telemetría del `limbic_profile`) hacia la interfaz gráfica local o motores de interpolación de servos reales del androide (mediado por *Nomad Bridge*).
- **Bloque E.2: RLHF y Fine-tuning de Prosodia (Claude / Copilot)**
  - Tarea E.2.1: Reemplazar el `PromptTemplate` base en el `ResponseSculptor` creando un dataset optimizado (Reward Model) para equilibrar assertividad, calidez, y misterio, limitando al mismo tiempo dinámicas aduladoras.

### 🔵 Módulo 8: Higiene, Pruebas Unitarias y Concurrencia [PRIORIDAD 2]
*Responsabilidad: Nivel 2 (Team Copilot)*
*Objetivo: Asegurar que el servidor concurrente recién creado no colapse por Data Races en las bases SQLite compartidas.*

- **Bloque 8.1: Unit Tests Asíncronos**
  - Tarea 8.1.1: Crear suite de testeo masivo asíncrono (`test_charm_engine.py`, multithread server load tests) para verificar cancelaciones limpias en el `chat_server`.
- **Bloque 8.2: Database Locks**
  - Tarea 8.2.1: Implementar sistema de colas / bloqueo seguro para que los turnos concurrentes no corrompan los archivos `kernel_episodes.jsonl`, `user_models.db` o `DAO` ledgers.

### 🔴 L1 Oversight: Arquitectura y Governance Gate [PRIORIDAD ABSOLUTA]
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Liderar y coordinar todas las transiciones arquitectónicas pesadas y serializar las fusiones hacia Main.*

- Control de Calidad arquitectónica de los PRs de Cursor sobre el *Nomad Bridge* y vectores Somáticos.
- Mantenimiento estricto del *Threat Model* contra ataques de red LAN e inyección sensorial. Preservación inmaculada de los guardrails de Adicción Parasocial (MalAbs).

---

## 🚀 Flujo de Sincronización Estratégica (Abril 2026)

1. **Jornada Actual:** 
   - **Antigravity (L1)**: Ha fusionado el core del `CharmEngine` en `master-antigravity`. Ahora asume monitorización pasiva de arquitecturas.
   - **Cursor (N2)**: Frontline único para Módulo S.1 y E.1 (*Puente Hardware + Vectores Gésticos*).
   - **Copilot (N2)**: Escudero de tests asíncronos y saneamiento Concurrente de persitencia (Módulo 8.2 y Pruebas del Charm Engine).
2. **Siguiente Fase Inter-Equipos:**
   - Claude y Copilot unifican un PR común abordando las tareas pendientes del Bloque E.2 (Calibración RLHF para el Motor de Encanto).
3. **Validación L0:**
   - La Demostración en vivo ("Hardware in the loop"), donde el Androide observa mediante cámara real y responde persuasivamente sin dañar éticamente, es el gatillo de Release L0.
