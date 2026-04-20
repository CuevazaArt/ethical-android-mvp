# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]` del "BACKLOG ABIERTO".
> 2. Si hay problemas de infraestructura (APIs lentas) o sobran tokens/recursos, toma tareas de la **RESERVA DEL ENJAMBRE (Buffer)**.
> 3. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 4. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-19 / CIERRE)
- **Phase 9 (Hardened Embodiment)**: INTEGRADO. Handshake seguro y telemetría en tiempo real desde Nomad Bridge operativa.
- **S.13 (Field Test 1 - Límbico)**: Completado. Control de ganancia sensorial (`KERNEL_SENSORY_GAIN`) y amortiguación emocional estabilizados.
- **S.12 (Vertical Armor)**: Completado. Blindaje final de MalAbs y InputTrust.

---

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [CERRADO]**

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [CERRADO]**

---

## 🚀 BACKLOG ABIERTO (Próximos Pasos V13.0+)

**Bloque 16.0: Refinamiento de la Telemetría y Modulación Neuronal [PENDING]**
- Tarea 16.1: **Visualización de Carga del Bus**: Integración de métricas de latencia de `CorpusCallosum` en el Dashboard Clínico (WebSockets).
- Tarea 16.2: **Throttling Dinámico del Bus**: Implementar lógica en `BusModulator` para ajustar el `asyncio.sleep` de los lóbulos basado en el uso de CPU.
- Tarea 16.3: **Decoupling de Judgement**: Mover la lógica de `AbsoluteEvilDetector` de forma nativa al loop reactivo del `ExecutiveLobe` sin dependencias del kernel.

**Bloque 15.0: Desmonolitización del Sistema Nervioso (Ethos V13.0) [DONE]**
- Tarea 15.1: Guillotina del Kernel Monolítico y creación de la fachada `EthosKernel`. (Completado: Antigravity)
- Tarea 15.2: Implementación de `CorpusCallosum` (Pub/Sub Async) y modelos de pulsos `NervousPulse`. (Completado: Antigravity)
- Tarea 15.3: Migración de los 4 lóbulos al modelo "Bus-Aware" y resolución de importaciones circulares. (Completado: Antigravity)

---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua)
> *Estas tareas no bloquean el progreso crítico (`main` branch) y deben ser tomadas por los agentes L2 cuando hay cuellos de botella en la inferencia, sobran tokens horarios, o mientras el L1 está en procesos de consolidación.*

**Bloque B.1: Cacería de NaNs y Hardening Matemático [DONE]**
- Tarea B.1.1: Revisar funciones trigonométricas/logarítmicas en `modules/ethical_poles.py` y `modules/sigmoid_will.py` agregando `math.isfinite()`. (Completado: Antigravity)

**Bloque B.2: Tipado Estricto Paralelo [DONE]**
- Tarea B.2.1: Corregir advertencias de MyPy (o equivalentes) en los adaptadores de audio y test suites aisladas. (Completado: Antigravity)

**Bloque B.3: Documentación y Refactorización Pasiva [DONE]**
- Tarea B.3.1: Actualizar docstrings en `kernel_utils.py` y diagramas de Mermaid si las interfaces han cambiado sin documentarse. (Completado: Antigravity)

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [DONE]**
- Tarea 14.1: Auto-Descubrimiento (mDNS/Zeroconf) integrado en el servidor. (Completado: Antigravity)
- Tarea 14.2: Dashboard Clínico: Overhaul completo a interfaz diagnóstica. (Completado: Antigravity)

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [DONE]**
- Tarea 13.1: Reconexión del chat (Smartphone -> Kernel) con timeouts estrictos y encolamiento async en NomadBridge. (Completado: Antigravity)
- Tarea 13.2: VAD (Voice Activity Detection) Local en el cliente PWA. (Completado: Antigravity)

**Bloque 12.0: Autocalibración Física y Corrección Sensorial [DONE]**
- Tarea 12.1: Implementar corrección "Velo Azul" (BGR -> RGB) y streaming de webcam local al Dashboard. (Completado: Antigravity)
- Tarea 12.2: Implementado `SensorBaselineCalibrator` (Aclimatación de 60s) para umbrales dinámicos de temperatura y jerk. (Completado: Antigravity)

**Bloque S.13: Refinación de Tensión Límbica (Field Test 1) [DONE]**
- Tarea S.13.1: Introducción de ganancia global `KERNEL_SENSORY_GAIN` y suavizado de transiciones paramétricas (`KERNEL_SYMPATHETIC_ATTACK`). (Completado: Antigravity)

**Bloque S.12: Boy Scout Vertical Armor (Final Pass) [DONE]**
- Tarea S.12.1: Implementar blindaje de entradas en `AbsoluteEvilDetector` y normalización resiliente en `InputTrust`. (Completado: Antigravity)
- Tarea S.12.2: Consolidar redundancia en `SemanticChatGate` y asegurar cumplimiento de protocolos asíncronos. (Completado: Antigravity)

**Bloque S.14: Consolidación y Sincronización Final [DONE]**
- Tarea S.14.1: Unificar ramas de enjambre (Claude/Cursor/Copilot), resolver conflictos de inicialización Tri-Lobe y re-sellar manifiesto criptográfico. (Completado: Antigravity)

**Bloque Phase 9: Hardened Embodiment [DONE]**
- Tarea 9.1: Implementar HMAC-SHA256 en `SecureBoot` y handshake criptográfico en `NomadBridge`. (Completado: master-cursorultra / Antigravity)
- Tarea 9.2: Zero-Latency Vision queue y Vision Continuous Daemon. (Completado: master-cursorultra)

**Bloque S.11: Ajuste de Priors Experienciales (Learning Loop) [DONE]**
- Tarea S.11.1: Activar el lóbulo `temporal_horizon_prior` en el `CerebellumLobe`. (Completado: Antigravity)

**Bloque S.10: Persistencia de Estrategia Operativa (V10) [DONE]**
- Tarea S.10.1: Persistencia de `MetaplanRegistry`, `SkillLearningRegistry` y `SomaticMarkerStore`. (Completado: Antigravity)

... (rest of the history from main) ...
