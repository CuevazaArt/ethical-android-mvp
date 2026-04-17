# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 8+)

Este documento estructura el volumen de trabajo arquitectónico definido para el Ethos Kernel. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**. 

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

---

### 🟢 Módulo S: Encarnación Activa y Hardware Bridge (Nomad PC/Mobile) [PRIORIDAD 0]
*Responsabilidad: Nivel 2 (Team Cursor)*
*Objetivo: Integrar sensores reales (visión/audio) provenientes de un dispositivo móvil LAN como inputs de inferencia física, abandonando las señales de prueba simuladas.*

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video y audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona.
- **Bloque S.2: Calibración Termo-Visual Continua**
  - Tarea S.2.1: Refinar las interrupciones del `VitalityAssessment` utilizando la telemetría real transmitida por el *Nomad Bridge*.

### 🔵 Módulo 8: Higiene, Pruebas Unitarias y Concurrencia [PRIORIDAD 1]
*Responsabilidad: Nivel 2 (Team Copilot)*
*Objetivo: Asegurar que el servidor concurrente recién creado no colapse por Data Races en las bases SQLite compartidas.*

- **Bloque 8.1: Unit Tests Asíncronos**
  - Tarea 8.1.1: Crear suite de testeo masivo asíncrono para verificar cancelaciones limpias en el `chat_server` cuando se invocan múltiples abortos.
- **Bloque 8.2: Database Locks**
  - Tarea 8.2.1: Implementar sistema de colas / bloqueo seguro para que los turnos concurrentes no corrompan los archivos `kernel_episodes.jsonl` o `DAO` ledgers.

### 🔴 L1 Oversight: Arquitectura y Governance Gate [PRIORIDAD ABSOLUTA]
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Liderar y coordinar todas las transiciones arquitectónicas pesadas y serializar las fusiones hacia Main.*

- Control de Calidad arquitectónica de los PRs de Cursor sobre el *Nomad Bridge*.
- Mantenimiento estricto del *Threat Model* contra ataques de red LAN e inyección sensorial.
- **Claude (L2):** Marcado temporalmente como Offline / Fuera de servicio.

---

## 🚀 Flujo de Sincronización (Abril 2026)

1. **Jornada Actual:** 
   - **Antigravity (N1)**: Audita commits, asume control del `master-antigravity` y valida mitigaciones de concurrencia.
   - **Cursor (N2)**: Frontline único. Salto inmediato a Módulo S.1.
   - **Copilot (N2)**: Escudero de tests y saneamiento Concurrente (Módulo 8.2).
2. **Próxima Ventana de Sincronización:**
   - Cursor y Copilot envían sus PRs de Hardware Mock y Locks a Antigravity.
3. **Validación N0:**
   - La Demostración en vivo ("Hardware in the loop") es el gatillo de Release L0.
