# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

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

## 📥 BACKLOG ABIERTO (Open Tasks)

**Bloque 12.0: Autocalibración Física y Corrección Sensorial [PENDING]**
- Tarea 12.2: **Calibración Dinámica de Entorno (Aclimatación):** Crear una rutina `SensorBaselineCalibrator` durante los primeros 60 segundos de boot. En lugar de usar valores fijos (ej. 75ºC o 0.6 de Jerk), calcular medias y varianzas relativas al entorno actual para definir el "Punto Dulce" de forma autónoma.

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [PENDING]**
- Tarea 13.1: **Reconexión del chat:** Asegurar que los mensajes de texto del Nomad (Smartphone) fluyan hacia `process_chat_turn` sin ser bloqueados por la latencia límbica. Implementar timeouts estrictos.
- Tarea 13.2: **VAD (Voice Activity Detection) Local:** Integrar detección de voz robusta en el cliente PWA antes de consumir tokens o saturar el Bridge. Requisito para el futuro Text-to-Speech (TTS).

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [PENDING]**
- Tarea 14.1: **Auto-Descubrimiento (mDNS/Zeroconf):** Implementar un broadcast local en el servidor para que el PWA encuentre la IP automáticamente, minimizando la interacción humana (Server Self-Healing).
- Tarea 14.2: **Dashboard Clínico:** Eliminar elementos UI decorativos y reemplazarlos por feeds de datos expuestos y tabulados (Float/Boolean) de latencia, sigma, y telemetría pura.

---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua)
> *Estas tareas no bloquean el progreso crítico (`main` branch) y deben ser tomadas por los agentes L2 cuando hay cuellos de botella en la inferencia, sobran tokens horarios, o mientras el L1 está en procesos de consolidación.*

**Bloque B.1: Cacería de NaNs y Hardening Matemático [BUFFER]**
- Tarea B.1.1: Revisar funciones trigonométricas/logarítmicas en `modules/ethical_poles.py` y `modules/sigmoid_will.py` agregando `math.isfinite()`.

**Bloque B.2: Tipado Estricto Paralelo [BUFFER]**
- Tarea B.2.1: Corregir advertencias de MyPy (o equivalentes) en los adaptadores de audio y test suites aisladas.

**Bloque B.3: Documentación y Refactorización Pasiva [BUFFER]**
- Tarea B.3.1: Actualizar docstrings en `kernel_utils.py` y diagramas de Mermaid si las interfaces han cambiado sin documentarse.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 12.0: Autocalibración Física y Corrección Sensorial [DONE]**
- Tarea 12.1: Implementar corrección "Velo Azul" (BGR -> RGB) y streaming de webcam local al Dashboard. (Completado: Antigravity)

**Bloque S.13: Refinación de Tensión Límbica (Field Test 1) [DONE]**
- Tarea S.13.1: Introducción de ganancia global `KERNEL_SENSORY_GAIN` y suavizado de transiciones paramétricas (`KERNEL_SYMPATHETIC_ATTACK`). (Completado: Antigravity)

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
