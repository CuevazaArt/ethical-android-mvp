# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]`.
> 2. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 3. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-20)
- **Phase 9 (Hardened Embodiment)**: INTEGRADO. HMAC-SHA256 Secure Boot y Zero-Latency Vision Bridge operativos.
- **S.12 (Vertical Armor)**: Completado. Blindaje final de MalAbs y InputTrust.
- **S.11 (Learning Loop)**: Completado. Ajuste de priors temporales episódicos en el Cerebelo.
- **S.10 (V10 Persistence)**: Completado. Persistencia de registros de metaplan, habilidades y marcadores somáticos.
- **S.4 (Persistence)**: Completado. Gap de amnesía bayesiana cerrado.
- **11.2 (Crisis)**: Completado. Protocolo "Final Breath" operativo.

---

## 📥 BACKLOG ABIERTO (Open Tasks)

**Bloque 10.1: Integración de Inteligencia Acústica Real [PENDING]**
- Tarea 10.1.1: Conectar el `AudioInference` con el stream multi-agente de Nomad Bridge para clasificación de prosodia en tiempo real.
- Tarea 10.1.2: Implementar VAD (Voice Activity Detection) local para reducir el tráfico de red en el Bridge.

**Bloque 10.2: Refactorización de Pydantic Settings (Phase 4) [PENDING]**
- Tarea 10.2.1: Migrar las constantes de entorno restantes de `modules/llm_layer.py` al objeto `KernelSettings`.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque S.12: Boy Scout Vertical Armor (Final Pass) [DONE]**
- Tarea S.12.1: Implementar blindaje de entradas en `AbsoluteEvilDetector` y normalización resiliente en `InputTrust`. (Completado: Antigravity)
- Tarea S.12.2: Consolidar redundancia en `SemanticChatGate` y asegurar cumplimiento de protocolos asíncronos. (Completado: Antigravity)

**Bloque Phase 9: Hardened Embodiment [DONE]**
- Tarea 9.1: Implementar HMAC-SHA256 en `SecureBoot` y handshake criptográfico en `NomadBridge`. (Completado: master-cursorultra / Antigravity)
- Tarea 9.2: Zero-Latency Vision queue y Vision Continuous Daemon. (Completado: master-cursorultra)

**Bloque S.11: Ajuste de Priors Experienciales (Learning Loop) [DONE]**
- Tarea S.11.1: Activar el lóbulo `temporal_horizon_prior` en el `CerebellumLobe`. (Completado: Antigravity)

**Bloque S.10: Persistencia de Estrategia Operativa (V10) [DONE]**
- Tarea S.10.1: Persistencia de `MetaplanRegistry`, `SkillLearningRegistry` y `SomaticMarkerStore`. (Completado: Antigravity)

... (rest of the history from main) ...
