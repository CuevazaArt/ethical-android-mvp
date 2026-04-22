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
- **L1-AUDIT-PULSE (2026-04-22)**: EXITOSO. 100% de efectividad en la Suite Adversarial tras integración de V14.0 Baseline.

---

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [CERRADO]**

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [CERRADO]**

---

---

## 🚀 BACKLOG ABIERTO (Próximos Pasos V14.0: Encarnación Conversacional Nómada)


> **PROMPT DE ARRANQUE PARA AGENTES L2 (BOY SCOUTS):**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. El monolito ha sido abolido y la infraestructura asíncrona V13.0 está estable. Tu objetivo primordial absoluto ahora es consolidar el **Bloque 20.0 y 21.0**: la fluidez de interacción usando estrictamente LLMs locales (Ollama), desvinculándonos de dependencias API cerradas, y dotando a la matriz del Cerebelo de una identidad biográfica persistente. **Instrucciones:** Toma un ticket de `V14.0`, enfócate en el código (Python en `src/`), asume 100% de propiedad, y termina tu sesión ejecutando `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

**Bloque 20.0: Local Conversational Matrix (Zero-API Fluency) [DONE]**
- Tarea 20.1: **Desacoplamiento Estricto Comercial:** [COMPLETED] Refactorizar el backend de percepción y decisión para enrutar el 100% de `process_chat_turn` hacia `OllamaLLMBackend`. 
- Tarea 20.2: **Refinamiento de Tiempos y Tolerancia Textual:** [COMPLETED — L2 Swarm] `KernelSettings` default `KERNEL_CHAT_TURN_TIMEOUT` = 180 s cuando `USE_LOCAL_LLM=1` o `LLM_MODE=ollama` (30 s remoto, 60 s Nomad); `_env_optional_positive_float` rechaza NaN/Inf; `PROMPT_COMMUNICATION_LOCAL_FLUENCY_APPEND` en `llm_layer` para respuestas breves en modo Ollama (incl. streaming).
 
**Bloque 21.0: Biographic Memory & Persistent Identity [COMPLETED]**
- Tarea 21.1: **Manifiesto de Identidad (Birth Context):** [COMPLETED] Crear `src/persistence/identity_manifest.py` para gestionar la narrativa base del agente.
- Tarea 21.2: **BiographicMemoryTracker:** [COMPLETED] Implementar el rastreador de episodios biográficos en el `CerebellumLobe` para que las sesiones de chat se guarden como hitos narrativos.

**Bloque 22.0: Nomad Field Test (Texto en Terreno) [DONE]**
- Tarea 22.1: **Puente Web Chat Robustecido:** [COMPLETED — L2 Cursor] PWA: cola saliente (48) con `flush` al reconectar, envío dual `/ws/chat` + relay `chat_text` por `/ws/nomad` si el chat no está `OPEN`, `onclose` simétrico y un solo temporizador de backoff. Servidor: `NomadBridge.chat_text_queue` default 48 (`KERNEL_NOMAD_CHAT_TEXT_QUEUE_MAX`), `_charm_feedback_replay` + `_flush_charm_feedback_replay` tras `accept`, `public_queue_stats` con `chat_text_queue_*` y `charm_feedback_replay_pending`, `last_rms` finito, `vessel_online`, `last_sensor_update_delta`, `_chat_text_consumer` tipado a `str`.
- Tarea 22.2: **Inyección de Identidad al Front (Backend):** [COMPLETED — L2] `chat_server.py` emite `build_sync_identity_ws_message` tras `try_load_checkpoint` (tipo `[SYNC_IDENTITY]`, `payload` con `gestalt_snapshot`, `base_history`, `identity_manifest`, `narrative_recent`, `existence_digest`, `identity_ascription`, etc.).
- Tarea 22.3: **Inyección de Identidad al Front (Frontend PWA):** [COMPLETED — L2] `nomad_pwa/app.js` consume `[SYNC_IDENTITY]` / legado `SYNC_IDENTITY`, `gestalt_snapshot` → PAD CSS, `#identity-strip`, título y transcript.
- Tarea 22.4: **Optimización Layout Nomad:** [COMPLETED — L2] Modo `body.nomad-text-focus` por defecto + toggle `#btn-ui-mode`; CSS oculta orbe, pulso ético, rejilla de telemetría y botón STREAM; prioriza panel de chat.
- Tarea 22.5: **Zero-API Fast TTFT (Time-To-First-Token):** [COMPLETED — L2] Cadena Thalamus sin `sleep` en ruta de chat; `PROMPT_COMMUNICATION_NOMAD_APPEND` reforzado (sin preámbulos; arranque inmediato de la réplica hablada).

**Bloque 26.0: Paridad CI / matriz de intérpretes [DONE]**
- Tarea 26.1: **GitHub Actions `quality` + Python 3.13:** [COMPLETED — L2 Cursor] Matriz `quality` en `.github/workflows/ci.yml` ampliada a CPython 3.11 / 3.12 / 3.13; `CONTRIBUTING.md` actualizado. La suite completa corre en GitHub Actions en cada push/PR (job `quality`).
- Tarea 26.2: **Integridad legacy / D1:** [COMPLETED — L2 Cursor] `kernel_legacy_v12._run_social_and_locus_stage` corregido a ``async def`` con ``await`` en el call site (``await`` fuera de ``async`` era inválido). `tests/integration/test_cross_tier_decisions.py` importa el kernel v12 solo si existen `kernel_handlers/communication.py` y dependencias; en árboles mínimos el módulo se omite con ``pytest.skip`` a nivel de módulo.

---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua V14)
> *Estas tareas no bloquean el progreso crítico (main branch) y son para mantenimiento estructural.*

**Bloque B.1: Cacería de NaNs y Hardening Matemático [DONE]**
- Tarea B.1.1: Revisar funciones trigonométricas/logarítmicas en `modules/ethical_poles.py` y `modules/sigmoid_will.py` agregando `math.isfinite()`. (Completado: Antigravity)

**Bloque B.2: Tipado Estricto Paralelo [DONE]**
- Tarea B.2.1: Corregir advertencias de MyPy (o equivalentes) en los adaptadores de audio y test suites aisladas. (Completado: Antigravity)

**Bloque B.3: Documentación y Refactorización Pasiva [DONE]**
- Tarea B.3.1: Actualizar docstrings en `kernel_utils.py` y diagramas de Mermaid si las interfaces han cambiado sin documentarse. (Completado: Antigravity)

**Bloque B.4: Mantenimiento y Accesibilidad de Red [DONE]**
- Tarea B.4.1: Habilitar binding 0.0.0.0 por defecto para permitir acceso LAN desde dispositivos móviles. (Completado: Antigravity)

**Bloque B.5: Poda de Viejas Vías [DONE]**
- Tarea B.5.1: [COMPLETED — L2 Cursor] `ThalamusLobe` único: `ingest_telemetry`, `get_sensory_summary` (incl. `sensory_tension` HUD), `fuse_sensory_stream`, `_finite_env_stress`, degradación acotada. `PerceptiveLobe.get_sensory_impulses()` + `tests/test_nomad_resilience.py` sin `thalamus=MagicMock` (API V13). `semantic_chat_gate.arun_semantic_malabs_acl_bypass` en `kernel_handlers/perception.py`; `tests/test_nomad_integration_hardware.py` contra `EthosKernel` + `NomadBridge`.


---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 24.0: Memoria de Largo Plazo (LTM) Vectorial [DONE]**
- Tarea 24.1: Integración de Hito 14.x: Memoria de Largo Plazo LTM Vectorial y Conversación Full-Duplex. (Completado: Anonymous Agent)

**Bloque 25.0: Refinamiento de Fluidez y Preemption [DONE]**
- Tarea 25.1: Interrupción nativa biológica (Preemption) e identidad de Dashboard. (Completado: Anonymous Agent)

**Bloque 23.0: Sincronización de Identidad Narrativa (Mind-Sync) [DONE]**
- Tarea 23.1: **GestaltSnapshot**: Congelar el estado telemetrico (PAD, sigma). (Completado: Anonymous Agent)
- Tarea 23.2: **Preempción por Trauma**: Abortar deliberación asíncrona. (Completado: Anonymous Agent)
- Tarea 23.3: **Thought Streaming**: Inner Voice broadcast. (Completado: Anonymous Agent)

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
