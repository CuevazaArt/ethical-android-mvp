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
- **V13.0 (Distributed Brain Initialization)**: COMPLETADO. Monolito destruido, bus asíncrono CorpusCallosum verificado.
- **V13.1 (Aesthetic & Legacy Stabilization)**: COMPLETADO. Enriquecimiento de terminal (TColors) y restauración de puentes de compatibilidad legado.

---

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [CERRADO]**

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [CERRADO]**

---

---

## 🚀 BACKLOG ABIERTO (Próximos Pasos V14.0: Encarnación Conversacional Nómada)

> **PROMPT DE ARRANQUE PARA AGENTES L2 (BOY SCOUTS):**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. El monolito ha sido abolido y la infraestructura asíncrona V13.0 está estable. Tu objetivo primordial absoluto ahora es consolidar el **Bloque 20.0 y 21.0**: la fluidez de interacción usando estrictamente LLMs locales (Ollama), desvinculándonos de dependencias API cerradas, y dotando a la matriz del Cerebelo de una identidad biográfica persistente. **Instrucciones:** Toma un ticket de `V14.0`, enfócate en el código (Python en `src/`), asume 100% de propiedad, y termina tu sesión ejecutando `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

**Bloque 20.0: Local Conversational Matrix (Zero-API Fluency) [PENDING]**
- Tarea 20.1: **Desacoplamiento Estricto Comercial:** [COMPLETED] Refactorizar el backend de percepción y decisión para enrutar el 100% de `process_chat_turn` hacia `OllamaLLMBackend`. 
- Tarea 20.2: **Refinamiento de Tiempos y Tolerancia Textual:** Sincronizar el `KERNEL_CHAT_TURN_TIMEOUT` con latencias largas realistas de modelos Llama3/Mistral corriendo en local. Optimizar el `System Prompt` maestro de chat para favorecer réplicas cortas y directas sin introspección verbosa.
 
**Bloque 21.0: Biographic Memory & Persistent Identity [COMPLETED]**
- Tarea 21.1: **Manifiesto de Identidad (Birth Context):** [COMPLETED] Crear `src/persistence/identity_manifest.py` para gestionar la narrativa base del agente.
- Tarea 21.2: **BiographicMemoryTracker:** [COMPLETED] Implementar el rastreador de episodios biográficos en el `CerebellumLobe` para que las sesiones de chat se guarden como hitos narrativos.

**Bloque 22.0: Nomad Field Test (Texto en Terreno) [PENDING]**
- Tarea 22.1: **Puente Web Chat Robustecido:** Refinar la PWA de `NomadBridge` (foco en modo texto/chat clásico). Eliminar o enmascarar componentes irrelevantes de UI pesadas para priorizar input/output liviano de texto.
- Tarea 22.2: **Inyección de Identidad al Front:** El servidor backend asíncrono debe enviar un paquete `[SYNC_IDENTITY]` al WebSocket conectarse al origen, para que la UI de chat se alinee al estado actual e historia de la entidad.

---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua V14)
> *Estas tareas no bloquean el progreso crítico (main branch) y son para mantenimiento estructural.*

**Bloque B.4: Poda de Viejas Vías [PENDING]**
- Tarea B.4.1: Eliminar y purgar todos los mocks asíncronos residuales temporales en las áreas de Thalamus que ya cumplieron su propósito durante el salto de la V12 a V13.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 16.0: Refinamiento de la Telemetría y Modulación Neuronal [DONE]**
- Tarea 16.1: **Visualización de Carga del Bus**: Integración de métricas de latencia de `CorpusCallosum`. (Completado: Antigravity)
- Tarea 16.2: **Throttling Dinámico del Bus**: Ajuste en `BusModulator`. (Completado: Antigravity)
- Tarea 16.3: **Decoupling de Judgement**: Remoción nativa de `AbsoluteEvilDetector` hacia `ExecutiveLobe`. (Completado: Antigravity)

**Bloque 17.0: Reducción del Monolito Perceptual [DONE]**
- Tareas 17.1 a 17.3 completadas. Desacoplamiento de Cortex Sensorial y Supervivencia Asíncrona. (Completado: Antigravity)

**Bloque 18.0 & 19.0: Consolidación Tri-Lobe y Sello de Calidad [DONE]**
- Hardening contra Cognitive Stalling, Restauración Suite Adversarial, Limpieza del Monolito (Regla Boy Scout). (Completado: Antigravity)

**Bloques Extra B.1 a B.3: Tipado Estricto y NaNs [DONE]**
- Hardening Numérico (math.isfinite), Docstrings MyPy. (Completado: Antigravity)

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

**Bloque V.13.1: Enriquecimiento Estético y Compatibilidad Legacy [DONE]**
- Tarea V.13.1.1: Integrar TColors (ANSI) en la salida del Kernel y restaurar alias de soporte legacy (ChatTurnCooperativeAbort, ApplyNomadTelemetry). (Completado: Antigravity)

**Bloque 15.0: Desmonolitización del Sistema Nervioso (Ethos V13.0) [DONE]**
