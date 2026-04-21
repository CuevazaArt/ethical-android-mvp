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
- **V14.0 (Nomadic Identity & Local Matrix)**: INTEGRADO. Zero-API fluency y handshake de identidad [SYNC_IDENTITY] operacional.

---

**Bloque 13.0: Desbloqueo Conversacional y Voz (Zero-Friction Audio) [CERRADO]**

**Bloque 14.0: Cero Fricción y Recuperación Autónoma [CERRADO]**

---

---

## 🚀 BACKLOG ABIERTO (Próximos Pasos V14.0: Encarnación Conversacional Nómada)

> **PROMPT DE ARRANQUE PARA AGENTES L2 (BOY SCOUTS):**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. El monolito ha sido abolido y la infraestructura asíncrona V13.0 está estable. Tu objetivo primordial absoluto ahora es consolidar el **Bloque 20.0 y 21.0**: la fluidez de interacción usando estrictamente LLMs locales (Ollama), desvinculándonos de dependencias API cerradas, y dotando a la matriz del Cerebelo de una identidad biográfica persistente. **Instrucciones:** Toma un ticket de `V14.0`, enfócate en el código (Python en `src/`), asume 100% de propiedad, y termina tu sesión ejecutando `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

**Bloque 20.0: Local Conversational Matrix (Zero-API Fluency) [COMPLETED]**
- Tarea 20.1: **Desacoplamiento Estricto Comercial:** [COMPLETED] Refactorizar el backend de percepción y decisión para enrutar el 100% de `process_chat_turn` hacia `OllamaLLMBackend`. 
- Tarea 20.2: **Refinamiento de Tiempos y Tolerancia Textual:** [COMPLETED] Sincronizar el `KERNEL_CHAT_TURN_TIMEOUT` con latencias largas realistas de modelos Llama3/Mistral corriendo en local. Optimizar el `System Prompt` maestro de chat para favorecer réplicas cortas y directas sin introspección verbosa.
 
**Bloque 21.0: Biographic Memory & Persistent Identity [COMPLETED]**
- Tarea 21.1: **Manifiesto de Identidad (Birth Context):** [COMPLETED] Crear `src/persistence/identity_manifest.py` para gestionar la narrativa base del agente.
- Tarea 21.2: **BiographicMemoryTracker:** [COMPLETED] Implementar el rastreador de episodios biográficos en el `CerebellumLobe` para que las sesiones de chat se guarden como hitos narrativos.

**Bloque 22.0: Nomad Field Test (Texto en Terreno) [COMPLETED]**
- Tarea 22.1: **Puente Web Chat Robustecido:** [COMPLETED] Refinar la PWA de `NomadBridge` (foco en modo texto/chat clásico). Eliminar o enmascarar componentes irrelevantes de UI pesadas para priorizar input/output liviano de texto.
- Tarea 22.2: **Inyección de Identidad al Front:** [COMPLETED] El servidor backend asíncrono debe enviar un paquete `[SYNC_IDENTITY]` al WebSocket conectarse al origen, para que la UI de chat se alinee al estado actual e historia de la entidad.


**Bloque 23.0: Episodic Pruning & Limbic Sleep [COMPLETED]**
- Tarea 23.1: **Mecanismo de Poda de Memoria:** [COMPLETED] Implementar proceso de "Sueño Límbico" para archivar y podar episodios de `BiographicMemory` que excedan el límite de almacenamiento local, evitando la degradación de performance en hardware de 1.5B.
- Tarea 23.2: **Consolidación de Identidad Dinámica:** [COMPLETED] Permitir que los rasgos de personalidad en el `IdentityManifest` se calibren ligeramente basados en el feedback acumulado en la memoria biográfica.


**Bloque 24.0: Local Semantic Calibration (Ollama Alignment) [COMPLETED]**
- Tarea 24.1: **Ajuste de Temperatura Dinámica:** [COMPLETED] Implementar en `src/modules/llm_layer.py` un mecanismo para variar la temperatura del modelo local (Ollama) basado en la `social_tension` lóbulo Límbico (mayor tensión = menor temperatura/más determinismo).
- Tarea 24.2: **Refuerzo de Stop Sequences:** [COMPLETED] Asegurar que los modelos locales no generen diálogos imaginarios del usuario mediante la inyección agresiva de stop sequences en el `SystemPrompt` del `OllamaLLMBackend`.

**Bloque 25.0: Cognitive Resilience & Signal Smoothing [COMPLETED]**
- Tarea 25.1: **Filtro de Butterword en Percepción:** [COMPLETED] Implementar un suavizado de señales de baja frecuencia en `src/kernel_lobes/perception_lobe.py` para evitar oscilaciones rápidas en la clasificación de riesgo ante ruidos momentáneos de Ollama.

- Tarea 26.2: **Corazón Motivacional (Idle Pulses):** [COMPLETED] Recuperar el `MotivationEngine` (Bloque C1) e instanciarlo dentro de `ExecutiveLobe` o kernel. Diseñar un mecanismo (o daemon de fondo) que emita de forma periódica un `ProactivePulse` cuando no haya interacción del usuario, logrando que el androide tenga propósito autónomo.

**Bloque 27.0: Narrative Integrity & Coherence (The "Self-Audit" Cycle) [COMPLETED]**
- Tarea 27.1: **Validación de Coherencia de Identidad:** [COMPLETED] Implementar un servicio en `src/modules/identity_integrity.py` que realice una validación cruzada entre el `IdentityManifest` (valores estáticos) y los últimos episodios de `NarrativeMemory` (valores empíricos), detectando derivas éticas o "traumas" no procesados.
- Tarea 27.2: **Dashboard de Motivación:** [COMPLETED] Crear una extensión en el Visual Dashboard (`scripts/eval/visual_dashboard.py`) para monitorear en tiempo real los drives del `MotivationEngine` (Curiosidad, Integridad, Reparación Social).

**Bloque 28.0: Somatic Refinement (Nervous System Jitter Management) [COMPLETED]**
- Tarea 28.1: **Agility EMA (Dynamic Smoothing):** [COMPLETED] Refactorizar `ThalamusNode` para que el factor de suavizado `_alpha` no sea estático, sino que se ajuste dinámicamente según la varianza de la señal entrante (mayor ruido = mayor inercia sensorial).


---

## 🗄️ RESERVA DEL ENJAMBRE (Buffer de Optimización Continua V14)
> *Estas tareas no bloquean el progreso crítico (main branch) y son para mantenimiento estructural.*

**Bloque B.4: Poda de Viejas Vías [COMPLETED]**
- Tarea B.4.1: Eliminar y purgar todos los mocks asíncronos residuales temporales en las áreas de Thalamus que ya cumplieron su propósito durante el salto de la V12 a V13. [DONE]

**Bloque B.5: Hardening de ThalamusNode [COMPLETED]**
- Tarea B.5.1: Añadir validaciones `math.isfinite()` en todos los cálculos de EMA y Fusión Sensorial en `src/kernel_lobes/thalamus_node.py` para prevenir envenenamiento de confianza por NaNs. [DONE]

**Bloque B.6: L1-AUDIT-PULSE (Security Enforcement) [COMPLETED]**
- Tarea B.6.1: [DONE] Ejecutar obligatoriamente `python scripts/eval/adversarial_suite.py` tras completar 3 bloques (24, 25, 26). Resultados: 6/6 PASS. Ref: cfedbd7a.


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
