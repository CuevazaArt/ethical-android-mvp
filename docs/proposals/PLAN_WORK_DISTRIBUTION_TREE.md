# Árbol de Distribución de Trabajo: Escalado a Infraestructura Pública (Fase 9+)

Este documento estructura el volumen de trabajo arquitectónico definido para el Ethos Kernel. El trabajo se asigna a los diferentes equipos (Tiers) según las reglas de gobernanza del repositorio (`AGENTS.md`).

> [!IMPORTANT]
> **Nueva Directiva Estratégica (Update L1 - Fase 9)**:
> La transición asíncrona y la integración inicial del hardware (Módulo S) y el Motor de Encanto (Módulo E) se han estabilizado. El objetivo primario de la **Fase 9: Encarnación Endurecida y Multi-Agente** es asegurar los túneles de comunicación del Hardware Bridge (Criptografía HMAC), activar la Inteligencia Acústica real (Whisper/Pyaudio), y blindar el pipeline de CI/CD contra condiciones de carrera.

---

## 🌳 Árbol de Distribución de Módulos (Blocks Tree)

### ✅ Módulos Consolidados / Completados
*Se han colapsado los módulos tras su finalización exitosa. Referirse al `CHANGELOG.md` para trazabilidad.*
- **Módulo 0**: Estabilización Pragmática y Desmonolitización [DONE]
- **Módulo 1-7**: DAO, Red-Teaming, Swarm Ethics, Runtime Governance [DONE]
- **Módulo S (Fase 1)**: Nomad SmartPhone LAN Bridge (Video/Audio/Telemetría Asíncrona) [DONE]
- **Módulo E (Fase 1)**: Integración base del Motor de Encanto y Renderizado Somático [DONE]
- **Módulo 8**: Bloqueos SQLite Concurrentes (sqlite_safe_write) [DONE]

---

### 🔴 Módulo S: Seguridad Criptográfica y Autenticación LAN [PRIORIDAD 0]
*Responsabilidad: Nivel 1 (Team Antigravity)*
*Objetivo: Evitar vectores de ataque de "Spoofing Sensorial" sobre el puerto WebSocket del dispositivo móvil.*

- **Bloque S.4: Handshake Criptográfico (HMAC)**
  - Tarea S.4.1: Implementar sistema de validación de tokens o firmas HMAC en `/ws/nomad` para rechazar fotogramas o telemetría falsificada en redes LAN.

### 🔵 Módulo CI: Estabilización de Integración Continua [PRIORIDAD 1]
*Responsabilidad: Nivel 1 (Team Antigravity) & Nivel 2 (Copilot)*
*Objetivo: Prevenir la inyección de fallos concurrentes (Flaky Tests) y subir los estándares de código.*

- **Bloque CI.1: Concurrency Workflows**
  - Tarea CI.1.1: Expandir `.github/workflows/ci.yml` para ejecutar pruebas agresivas de stress de Base de Datos y WebSockets. 
  - Tarea CI.1.2: Aumentar el piso de cobertura de código (Coverage) del 65% al 75%.

### 🟢 Módulo A: Inteligencia Acústica Autónoma [PRIORIDAD 2]
*Responsabilidad: Nivel 2 (Team Cursor / Alternate: Copilot)*
*Objetivo: Conectar los streams de sonido real a un modelo de reconocimiento acústico.*

- **Bloque A.1: Procesamiento Acústico Base**
  - Tarea A.1.1: Reemplazar los stubs vacíos en el `AudioAIProcessor`. Implementar detección de eventos sonoros (gritos, cristales rotos) y Voice Activity Detection (VAD) acoplado a Whisper local, procesando buffers que fluyen desde el NomadBridge.

### 🟣 Módulo B & E: Offloading de Visión y RLHF Judicial [PRIORIDAD 3]
*Responsabilidad: Nivel 2 (Team Claude para E.3, Copilot para B.4)*

- **Bloque E.3: Validación Automatizada (Claude)**
  - Tarea E.3.1: Configurar "LLM-as-a-Judge" actions que validen si los textos generados usando `prosody_guidance` violan la directiva anti-adulación de bajo nivel.
- **Bloque B.4: Optimización de Frame-Rate (Copilot)**
  - Tarea B.4.1: Sustituir `asyncio.to_thread` del adaptador MobileNetV2 por un proceso dedicado u ONNX Runtime para garantizar que el loop concurrente nunca caiga bajo los 30Hz de evaluación.

---

## 🚀 Flujo de Sincronización Estratégica (Fase 9)

1. **Jornada Actual:** 
   - **Antigravity (L1)**: Adopta las defensas perimetrales (Security S.4) y el marco de CI para bloquear regresiones.
   - **Cursor (N2)**: Asume la responsabilidad acústica (Módulo A) ahora que la UI/Física está completa.
   - **Claude (N2)**: Finaliza las métricas evaluativas del comportamiento somático.
2. **Siguiente Fase Inter-Equipos:**
   - Convergencia de los canales en un entorno 100% blindado contra manipulación sensorial local.
3. **Validación L0:**
   - Cuando el testeo concurrente se bloquee verde y no existan riesgos de suplantación de sensaciones, se validará el androide situacional de cara al público.
