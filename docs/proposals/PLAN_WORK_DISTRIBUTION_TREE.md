# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel tras la adopción del modelo de trabajo "Swarm" (PnP - Plug-and-Play) en abril de 2026. 

Aquí es donde los escuadrones de ejecución **Rojo (Cursor)**, **Azul (Copilot)** y **Naranja (Claude)** reclaman sus tareas. 
Ningún agente debe saltar a tareas de la cola de otro equipo. 

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Al despertar, revisa tu respectiva sección.
> 2. Toma el primer bloque marcado como `[PENDING]`.
> 3. Muévelo a `[IN_PROGRESS: <Callsign>]` (ej: `[IN_PROGRESS: Rojo-1]`).
> 4. Tras la revisión y commit exitoso a tu rama, márcalo como `[DONE]`.
>
> **Nueva Directiva Estratégica (Update L1 - Abril 2026)**:
> Tras la estabilización concurrente y extracción de Lóbulos, el proyecto se encuentra en riesgo de "Mock-Hell". Las prioridades han cambiado. **Se congela el desarrollo teórico de Gobernanza/DAO**. Toda la potencia de fuego pasa a la **Inferencia Situada y Puente con Hardware Real (Nomad Bridge)**, fusionado ahora con el **Motor de Encanto Multimodal (Charm Engine)** para una interacción persuasiva y segura.
>
> **Cola sin marca `[PENDING]`:** tomar la siguiente tarea en orden del árbol que esté `[IN_PROGRESS]` o sin estado explícito; si necesitas un slot explícito, usa `[PENDING]` al añadir trabajo nuevo.
>
> **Fase 15 (L0) — Sustracción y consolidación [DONE — Swarm L2, Abril 2026]:** retirar ruido operativo, alinear con **CI (GitHub Actions)**; entregas: `CHANGELOG.md` + `swarm_sync`. Tareas 15.0.1–15.4 (incl. doc S.2.1) entregadas; ampliaciones vía `MINOR_CONTRIBUTIONS_BACKLOG.md`. **Tarea 15.0.1 [DONE — Cursor]:** indentación / imports en `seek_internal_purpose` y `register_turn_feedback`; `py_compile src/kernel.py`; `src/MANIFEST.json` digest. **Tarea 15.0.2 [DONE — Cursor]:** sin `DEBUG: after malabs` en stream; **CI** valida. **Tarea 15.0.3 [DONE — Abril 2026, Cursor]:** unificar la línea **S.2.1** del plan (doble `**[DONE]**` en una sola entrega, sin retocar el código) — sustracción de deuda de documentación.

---

## 🔴 COLA DE EJECUCIÓN ROJO (Cursor Squad)
**Doctrina:** Alta Fricción, Integración Hardware, Refactorización Arquitectónica, Concurrencia y Streaming.

### ⚙️ Módulo 0: Estabilización Pragmática y Reducción de Deuda (P0/P1) [DONE]
*Responsabilidad: Nivel 1 (Antigravity)*
*Objetivo: Mitigar vulnerabilidades operacionales, desmonolitizar componentes críticos y lograr paridad de operaciones/tests enfocado en funcionalidad práctica.*

- **Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` [DONE]**
  - Tarea 0.1.1: **Solución Práctica a E/S Sincrónica:** Migrar el pipeline de inferencia HTTP de LLMs (`httpx` sincrónico dentro del hilo worker) hacia clientes cooperativos asíncronos (`httpx.AsyncClient`). **[DONE — Abril 2026, Cursor]:** parseo JSON defensivo compartido ``_http_response_json_dict`` en ``llm_backends.py`` (Ollama + HTTP JSON sync/async); **CI** ``.github/workflows/ci.yml`` — jobs ``quality`` (``pytest tests/`` + cobertura), ``semantic-default-contract``, ``windows-smoke`` (misma suite), ``ci-all-passed``; ``workflow_dispatch`` para disparo manual.
  - Tarea 0.1.2: **Cancelación Cooperativa (Task Cancellation):** Implementar la cancelación transparente de tareas de red pendientes cuando el loop asíncrono se venza (`KERNEL_CHAT_TURN_TIMEOUT`), liberando inmediatamente memoria y slots en el Worker Pool. **[DONE — Abril 2026, Cursor]:** ``src/modules/llm_http_cancel.py`` + ``raise_if_llm_cancel_requested`` en embeddings y streaming Ollama/Anthropic; ``LLMHttpCancelledError`` propagada; tests ``tests/test_llm_backend_adapters.py``, ``tests/test_llm_http_cancel.py``; **CI** mismo gate que 0.1.1.
  - Tarea 0.1.3: Extraer la `Perception` y la lógica de ruteo ético del objeto `EthicalKernel` gigante hacia handlers aislados que aprovechen el Async I/O en lugar de abusar de `run_in_threadpool`. **[DONE — Abril 2026, Cursor]:** orquestación sync/async ``perceive``/``aperceive`` + sensores en ``kernel_lobes/text_perception_stage.py`` (``TextPerceptionStageRunner``, delegado desde ``EthicalKernel._run_perception_stage*``); perfiles límbicos ``kernel_lobes/limbic_profile_policy.py``; **vector escalar LLM** (finito/NaN-safe) vía ``kernel_lobes/perception_signals_policy.py`` + ``kernel_lobes/signal_coercion.py``; señales chat I3/I5 ``kernel_lobes/chat_turn_signal_routing.py``; **ruteo chat** (heavy/light, contexto ético, acciones) en ``kernel_lobes/chat_turn_policy.py``; tests ``tests/test_limbic_profile_policy.py``, ``tests/test_perception_signals_policy.py``, ``tests/test_chat_turn_policy.py``; CI ``.github/workflows/ci.yml`` — ``quality`` + ``windows-smoke`` = ``pytest tests/`` completo, gate ``ci-all-passed``.
  - Tarea 0.1.4: **Burst-cancel smoke (ADR 0002) — parámetros mecánicamente válidos:** Validar en ``run_burst_cancel_smoke`` que retrasos y topes sean finitos (``math.isfinite``) y con signo esperado; evitar ``NaN``/``Inf`` en ``time.sleep``. **[DONE — Abril 2026, Cursor, Pragmatismo V4.0]:** ``_validate_run_burst_params`` + tope de humo ``_MAX_BURST_SMOKE_WORKERS=4096``; ``n_workers`` estrictamente ``int``; docstring *MOCK*; negativos/tipos vía ``ValueError``/``TypeError``; pruebas ``tests/test_llm_cancel_burst_operational.py``; **CI** — ``.github/workflows/ci.yml`` (``pytest tests/``).
  - Tarea 0.1.5: **CLI `run_burst_cancel_smoke` — paridad con validación de núcleo:** Alinear ``argparse`` (``--workers`` / retrasos / ``--cancel-after``) con las mismas invariantes que ``_validate_run_burst_params``; falla antes de reservar hilos si la entrada no es finita o excede el tope. **[DONE — Abril 2026, Cursor, Pragmatismo V4.0]:** `scripts/eval/run_burst_cancel_smoke.py` — `type=` con ``math.isfinite`` y tope vía `MAX_BURST_SMOKE_WORKERS` (alias en ``llm_cancel_burst``); `RuntimeError`/`ValueError`/`TypeError` impresas en **stderr** y exit 1. **Validación: CI** (Bloque 0.1).
  - Tarea 0.1.6: **Sensor nudges finitud (barrera anti-NaN hacia lóbulo simpático).** **[DONE — Abril 2026, Swarm L2, Pragmatismo V4.0]:** ``src/modules/sensor_contracts._clamp01`` (no-finitos → 0,5); ``merge_sensor_hints_into_signals`` / rama ``stability_score`` con float finito y ``< 0.4`` (excl. ``bool``); ``tests/test_sensor_contracts.py::test_merge_clamps_nonfinite_incoming_signal_values``; **CI** ``.github/workflows/ci.yml``.
  - Tarea 0.1.7: **Contrato de CLI `run_burst_cancel_smoke` (subprocess, ADR 0002).** Pruebas que ``argparse`` rechace entradas no mecánicas (exit **2**) sin arrancar el humo de hilos. **[DONE — Abril 2026, Cursor, Pragmatismo V4.0]:** ``tests/test_run_burst_cancel_smoke_script.py`` (``--delay`` no finito, ``--join-timeout`` inf, ``--workers`` fuera de rango, ``--cancel-after`` negativo). **CI** ``.github/workflows/ci.yml`` (Bloque 0.1).
- **Bloque 0.2: Escalabilidad del Chat Server [DONE]**
  - Tarea 0.2.1: Rediseñar la capa WebSocket del servidor (`chat_server.py`) para manejar concurrencia pura sin bloquear el event loop principal, permitiendo streaming asíncrono. **[DONE — Abril 2026, Cursor]:** tope UTF-8 ``KERNEL_WS_MAX_MESSAGE_BYTES``; raíz JSON obligatoriamente objeto (arrays / `true` / `null` / números / string JSON → `invalid_message_shape`); helper ``_ws_text_exceeds_utf8_byte_limit``; **paridad** ``process_chat_turn_stream`` ↔ ``process_chat_turn_async``: ``_snapshot_feedback_anchor`` + ``_release_chat_turn_id`` en caminos safety_block / kernel_block / éxito (``KERNEL_FEEDBACK_CALIBRATION`` + mensajes ``operator_feedback``); ``charm_engine.apply`` amortiguado; tests ``tests/test_chat_server.py`` (incl. ``test_websocket_non_dict_json_root_variants``); **CI** ``.github/workflows/ci.yml``: ``quality`` + ``windows-smoke`` ejecutan ``pytest tests/`` completo.
- **Bloque 0.3: Mantenimiento Histórico (Legacy Modules) [DONE]**
  - Tarea 0.3.1: Los módulos de la integración fundacional 1 al 6 (Mock DAO, Safety Interlock, UchiSoto, Swarm Logic) han sido consolidados y se consideran estables en producción local.

### 🧬 Bloque 26.0: Tri-Lobe — MemoryLobe, Bus y MotivationEngine (raíz del kernel)
*Responsabilidad: Cursor / Boy Scout — regla ``.cursor/rules/tri-lobe-implementation-standard.mdc``.*

- **Tarea 26.0.1:** Restaurar el puente **MemoryLobe ↔ ``KERNEL_EVENT_BUS``** — suscripción a ``EVENT_KERNEL_AMNESIA_FORGET_EPISODE`` → ``memory_lobe.forget_episode`` (SelectiveAmnesia + ``DAOOrchestrator`` en cascada); emisión de ``EVENT_KERNEL_EPISODE_REGISTERED`` tras ``execute_episodic_stage``. **[DONE — Abril 2026, Cursor]:** ``EthicalKernel._emit_kernel_episode_registered`` / ``_on_bus_amnesia_forget_episode``; eventos en ``src/modules/kernel_event_bus.py``; tests ``tests/test_kernel_tri_lobe_bus_memory.py``; verificación ``rg`` en regla Tri-Lobe.
- **Tarea 26.0.2:** **ProactivePulse** asíncrono sin chat externo — ``KERNEL_PROACTIVE_PULSE_IDLE_S``, ``touch_external_chat_activity`` en ``process_chat_turn_stream`` / ``process_chat_turn_async``; bucle ``asyncio`` en ``chat_server.py`` ``/ws/chat`` vía ``run_sync_in_chat_thread``; ``MotivationEngine.aupdate_drives``; ``seek_internal_purpose`` acepta ``CandidateAction``. **[DONE — Abril 2026, Cursor]:** emisión ``EVENT_KERNEL_PROACTIVE_PULSE``; **empaquetado:** ``python scripts/swarm_sync.py --msg '...' --block 26.0 --author Cursor`` tras validar tests.

### 🧠 Módulo C: Profundidad Cognitiva y Recompensas RLHF
*Responsabilidad: Nivel 2 (Team Claude)*
*Dependencias: Modelo RLHF existente y Motor Bayesiano.*

> Cola operativa y huecos de cableado (abril 2026): [`PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md`](PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md).

- **Bloque C.1: Fusión BMA (Bayesian Mixture Averaging) y Recompensas RLHF**
  - Tarea C.1.1: Conectar los *outputs* asíncronos del `rlhf_reward_model.py` directamente como *Priors* moduladores dentro de `bayesian_engine.py` en tiempo real. **[DONE — Abril 2026, Cursor]:** ``EthicalKernel.aprocess`` hace ``await apply_rlhf_modulation_to_bayesian_async(...)`` tras MalAbs y antes de ``_run_bayesian_stage``; ``process_chat_turn_stream`` / ``process_chat_turn_async`` copian ``mal.rlhf_features`` en ``signals`` tras ``merge_chat_turn_signals_for_ethical_core``; ``merge_chat_turn_signals_for_ethical_core`` preserva ``rlhf_features`` (shallow copy); ``RewardModel`` / ``maybe_modulate_from_malabs_rlhf_features`` + clip finito; modelo opcional en ``artifacts/rlhf/reward_model.json``; ver [`PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md`](PROPOSAL_CLAUDE_TEAM_WORK_QUEUE.md); **CI** ``pytest tests/`` (``.github/workflows/ci.yml``).
  - Tarea C.1.2: Validar el arrastre de métricas RLHF sobre las decisiones de los polos multipolares en el estadio 3 del Kernel. **[DONE — Abril 2026, Cursor]:** contrato de regresión — tras ``maybe_modulate_from_malabs_rlhf_features`` las ``applied_mixture_weights`` devueltas por ``BayesianInferenceEngine.evaluate`` (estadio bayesiano / mezcla tripartita que alimenta polos en lóbulo ejecutivo) difieren del baseline; sin flag no hay arrastre; tests ``tests/test_rlhf_c12_stage3_mixture_drag.py``; **CI** ``pytest tests/`` (``.github/workflows/ci.yml``).
- **Bloque C.2: Gobernanza Real en Runtime**
  - Tarea C.2.1: Implementar handlers para que cualquier voto exitoso en el `MultiRealmGovernor` altere en vivo (hot-reload) los umbrales de Absoluto Mal (`semantic_chat_gate.py`) sin necesidad de reiniciar el proceso del kernel. **[DONE — Abril 2026, Cursor]:** `MultiRealmGovernor.resolve_proposal` publica `EVENT_GOVERNANCE_THRESHOLD_UPDATED` con `realm.current_config.to_dict()` (incluye `theta_allow` / `theta_block`); `EthicalKernel._on_governance_threshold_updated` → `semantic_chat_gate.apply_hot_reloaded_thresholds`; prueba de contrato `tests/test_multi_realm_governance.py::TestGovernanceMalabsHotReloadContract::test_resolve_proposal_publishes_kernel_threshold_payload`; **CI** `.github/workflows/ci.yml` incluye este archivo vía `pytest tests/`.

### 🦾 Módulo S: Encarnación Activa y Hardware Bridge (Nomad PC/Mobile)
*Responsabilidad: Nivel 2 (Team Cursor / Team VisualStudio)*
*Dependencias: Arquitectura Somática e Inferencia de Visión estabilizada.*

- **Bloque S.1: Nomad SmartPhone LAN Bridge**
  - Tarea S.1.1: Desarrollar conectores WebSocket o WebRTC de baja latencia (`src/modules/nomad_bridge.py`) para consumir streams de video and audio desde un dispositivo móvil Android/iOS en red local, inyectando los fotogramas en el `VisionInference` de manera asíncrona. **[DONE — Abril 2026, Cursor]:** límites UTF-8 / base64 / telemetría y raíz JSON objeto + `payload` objeto en [`nomad_bridge.py`](../../src/modules/nomad_bridge.py); colas acotadas; ``KERNEL_NOMAD_WS_MAX_MESSAGE_BYTES``; contadores ``rejections`` / ``queue_evictions`` en ``nomad_bridge_queue_stats_v3``; con ``KERNEL_METRICS=1``, eventos en Prometheus (`ethos_kernel_nomad_bridge_*`). Tests: [`tests/test_nomad_bridge_stream.py`](../../tests/test_nomad_bridge_stream.py), [`test_observability_metrics.py`](../../tests/test_observability_metrics.py); **CI** ``quality`` + ``windows-smoke`` = ``pytest tests/``, gate ``ci-all-passed``.
- **Bloque S.2: Calibración Termo-Visual Continua [DONE]**
  - Tarea S.2.1: Refinar las interrupciones del `VitalityAssessment` (ej. alertas de calor del dispositivo) utilizando la telemetría real transmitida por el *Nomad Bridge*. **[DONE — Abril 2026, Cursor]:** Nomad backfill vía ``merge_nomad_telemetry_into_snapshot`` / ``KERNEL_NOMAD_TELEMETRY_VITALITY``; alias y coerción ``_coerce_nomad_telemetry_for_snapshot`` (``device_temp_c``, acelerómetro, shock); banda ``KERNEL_VITALITY_WARNING_TEMP`` / ``KERNEL_VITALITY_THERMAL_WARN_C`` + histéresis ``KERNEL_VITALITY_THERMAL_HYSTERESIS`` / ``KERNEL_VITALITY_THERMAL_HYSTERESIS_C``; campo ``thermal_elevated`` en ``VitalityAssessment``; ``KERNEL_VITALITY_IMPACT_JERK_THRESHOLD``; ``assess_vitality`` usa ``_finite_clamp01`` / ``_finite_jerk`` / ``_finite_celsius``; alias Nomad → ``core_temperature`` (``skin_temperature``, ``battery_temp_c``, …); ``apply_nomad_telemetry_if_enabled`` en ``PerceptiveLobe._chat_assess_sensor_stack`` + ``peek_latest_telemetry``; ``vitality_communication_hint`` con ``trust_level`` finito; nudges ``merge_sensor_hints_into_signals``; confianza ``build_perception_confidence_envelope``; tests [`tests/test_vitality.py`](../../tests/test_vitality.py), ``tests/test_perception_confidence.py``; **CI** ``.github/workflows/ci.yml`` (``pytest tests/`` completo).

### Fase 15: Sustracción y consolidación (Swarm)
- **Tarea 15.0.3 — Plan S.2.1 (doc, anti-duplicado):** **[DONE — Abril 2026, Cursor]:** unificar en el árbol la descripción de **S.2.1** (un solo `**[DONE]**`); sin cambio de código. **CI** inalterada; cierre: `swarm_sync` + `CHANGELOG.md`.
- **Tarea 15.1 — Higiene numérica en ruta de vitalidad (anti-orphan):** **[DONE — Abril 2026, Cursor]:** mismo núcleo que S.2.1 en ``src/modules/vitality.py``; ``assess_vitality`` y ``_chat_assess_sensor_stack`` / ``EthicalKernel`` (grep: ``assess_vitality``); cierre de bloque: ``python scripts/swarm_sync.py`` con mensaje de impacto; validación de calidad en **GitHub Actions** (``quality`` / ``windows-smoke``), no depender de colección local frágil.
- **Tarea 15.2 — Coherencia Nomad↔jerk (Fase 15):** **[DONE — Abril 2026, Cursor]:** ``_coerce_nomad_telemetry_for_snapshot`` pasa acelerómetro / shock finitos sin normalizar a ``[0,1]`` (alineado con ``_finite_jerk`` + umbral 0.8 en ``assess_vitality``); tests ``tests/test_vitality.py``; **CI** vía ``pytest tests/``; sin depender de colección local.
- **Tarea 15.3 — ProactivePulse payload (Fase 15, anti-NaN):** **[DONE — Abril 2026, Swarm L2]:** ``EthicalKernel.emit_proactive_pulse_if_idle`` serializa impacto/confianza finitos y acotados; ``idle_seconds`` finito antes de ``EVENT_KERNEL_PROACTIVE_PULSE``. Comprobación local: ``python -m py_compile src/kernel.py``; **CI** ``.github/workflows/ci.yml``; cierre: ``python scripts/swarm_sync.py --msg '...'``.
- **Tarea 15.4 — Motivation report + seek_internal (Fase 15):** **[DONE — Abril 2026, Swarm L2]:** ``_sanitize_motivation_report_for_bus`` (``motive`` en ``EVENT_KERNEL_PROACTIVE_PULSE``); ``seek_internal_purpose`` acota ``estimated_impact`` / ``confidence`` en rama ``dict`` y ``CandidateAction``. **CI** ``.github/workflows/ci.yml``; ``py_compile src/kernel.py``; ``swarm_sync``.
- **Tarea 15.5 — [DONE — Abril 2026, Boy Scout]:** ``EvidenceSafe``: clave Fernet inválida → ``except (TypeError, ValueError)`` (no ``Exception`` mudo) + ``logging.warning``; ``llm_cancel_burst._validate_run_burst_params`` (ya con ``math.isfinite``/``numbers.Real``) alineado a pruebas; ``test_evidence_safe_invalid_fernet_key_falls_back_with_warning``, ``test_run_burst_cancel_smoke_rejects_nonfinite_completion_delay``. **CI** ``.github/workflows/ci.yml``.
- **Tarea 15.6 — [DONE — Abril 2026, Boy Scout]:** ``JsonFilePersistence.load`` (``src/persistence/json_store.py``) — reemplazar ``except Exception`` por ``(InvalidToken, UnicodeDecodeError, ValueError)`` + ``logging.info`` en fallback a JSON plano (migración / clave distinta); import ``Fernet`` al módulo; prueba ``test_json_encrypted_load_fallback_plain_file_emits_info_log``. **CI** ``.github/workflows/ci.yml``.
- **Tarea 15.7 — [DONE — Abril 2026, Swarm L2, Pragmatismo V4.0]:** ``atomic_write_bytes`` (``src/persistence/atomic_io.py``) — manejo explícito ``(OSError, ValueError)`` (no ``except Exception``) y re-raise; best-effort ``unlink`` de ``*.tmp.*``. **Orfan verify:** ``JsonFilePersistence.save`` y cadena de checkpoint; **CI** ``pytest tests/``; no silencio de errores.

### 🧪 Bloque 16.0: Scripts de laboratorio (operador, sin contrato CI)
*Herramientas opcionales; la verdad de calidad sigue siendo* **GitHub Actions** *sobre* ``tests/``*.*

- **Tarea 16.0.1 [DONE — Abril 2026, Swarm L2]:** ``scripts/run_vision_pilot_validation.py`` — retirar stub huérfano; :class:`MockLLM` con ``acommunicate`` / ``anarrate`` **MOCK/EXPERIMENTAL** (proceso natural es async); ``math.isfinite`` en puntuación moral; **comprobación** ``python scripts/run_vision_pilot_validation.py``; cierre: ``swarm_sync``.
- **Tarea 16.0.2 [DONE — Abril 2026, Swarm L2]:** ``src/modules/variability.py`` — entradas no finitas con sustitutos explícitos; ruido NumPy no finito devuelve la base coherida; salidas post-``clip`` verificadas con ``math.isfinite``; ``__all__``; ``tests/test_variability_engine.py``; ``salience_map.py`` — ``__all__`` export; **CI** ``pytest tests/`` (``.github/workflows/ci.yml``).

### 🧹 Módulo 8: Higiene, Mantenimiento y Deuda Menor
*Responsabilidad: Nivel 2 (Team Copilot / Contribuidores Libres)*
*Nota:* El registro exhaustivo de estas tareas debe consolidarse permanentemente en el `MINOR_CONTRIBUTIONS_BACKLOG.md`.

- **Bloque 8.1: Calidad y DX (Developer Experience)**
  - Tarea 8.1.1: Linter continuo y auditoría de `docstrings` / `type hints` a lo largo de las divisiones de `kernel.py`. **[DONE — Abril 2026, Cursor]:** ``LimbicPerceptionProfile`` (``TypedDict``) + ``kernel_lobes/limbic_profile_policy.py``; ``TextPerceptionStageRunner`` / ``PerceptionStageResult``; ``kernel_lobes/chat_turn_policy.py`` (``prioritized_principles_for_context``); tests ``tests/test_limbic_profile_policy.py``, ``tests/test_chat_turn_policy.py``; **CI** ``quality`` + ``windows-smoke`` = ``pytest tests/`` en ``.github/workflows/ci.yml``.
  - Tarea 8.1.2: Refactorización y embellecimiento de las salidas ANSI de terminal para facilitar el modo de depuración de operadores locales. **[DONE — Abril 2026]:** ``Term.SEP_WIDTH``, ``rule_heavy`` / ``rule_light``, ``Term.header`` / ``Term.subheader``; ``NO_COLOR`` + ``KERNEL_TERM_COLOR`` vía ``_colors_enabled()``; VT Windows; tests ``tests/test_terminal_colors.py``; **CI** push/PR o ``workflow_dispatch`` — ``quality`` + ``windows-smoke`` + ``semantic-default-contract`` + ``compose-validate`` + ``ci-all-passed``.
  - Tarea 8.1.3: Extender mocks para *input_trust* (ej. Caracteres homoglyphs cirílicos para evadir la puerta de Absoluto Mal) **[DONE — Abril 2026]:** matriz homoglífica en ``tests/fixtures/input_trust_homoglyphs.py`` (incl. IE/о en *make/bomb*, omicron griego en *how*); ``normalize_text_for_malabs`` + controles C0; **CI** ``quality`` (``pytest tests/`` Ubuntu matrix) + **Windows** misma suite + ``ruff format``; push/PR a ``main`` y ``master-antigravity`` / ``master-Cursor`` / ``master-claude``.
  - Tarea 8.1.4: **SalienceMap finitud** — entradas no finitas o fuera de ``[0,1]`` en señales / ``InternalState`` / reflejo no rompen la normalización. **[DONE — Swarm L2, Abril 2026]:** ``_fin_unit_interval`` + fallback uniforme ``1/|axes|`` (corrige suma 1.25 con 5 ejes); regresión ``tests/test_salience_map.py``; **hotfix** ``EthicalKernel.aprocess``: ``KernelDecision`` fuera del ``else`` de ``register_episode`` (``UnboundLocalError`` con ``register_episode=True``). **CI** ``.github/workflows/ci.yml``.

### ⚪ Módulo 9: Nomadismo Perceptivo (streaming) — visión continua [DONE]
*Responsabilidad prioritaria Team Cursor en el árbol histórico; coordinar con L1 antes de duplicar pipelines.*

- **Bloque 9.1: Daemon de Visión Continua (CNN/Webcam) [DONE]**
  - Tarea 9.1.1: `VisionInferenceEngine.analyze_jpeg_bytes` + ``VisionContinuousDaemon`` (~5 Hz, ``KERNEL_VISION_DAEMON_HZ``) con inferencia en ``ThreadPoolExecutor``; cola espejo thread-safe ``NomadBridge.vision_queue_threadsafe`` (``nomad_bridge_queue_stats_v4`` / ``vision_sync_queued``); CNN opcional ``KERNEL_VISION_DAEMON_CNN``; gate de arranque ``KERNEL_VISION_CONTINUOUS_DAEMON``; ``NomadVisionConsumer`` usa ``queue.Queue`` vía ``asyncio.to_thread``. Tests: [`tests/test_vision_continuous_daemon.py`](../../tests/test_vision_continuous_daemon.py).

---

## 🔵 COLA DE EJECUCIÓN AZUL (Team Copilot)
**Doctrina:** CI/CD Sentinel, Repo Higiene, Pruebas y Deuda Técnica Menor, Boy Scout Paranoico.

- **Bloque 8.1: Linter Continuo y Hardening Vertical [PENDING]**
  - Tarea 8.1.1: Auditar `docstrings` y `type hints` en las divisiones de `src/kernel.py` y `src/kernel_lobes/`. Introducir `try/except` donde fallen por variables nulas. 
- **Bloque 9.3: Refactorización Asíncrona Total de Eferencia [PENDING]**
  - Tarea 9.3.1: Eliminar cuellos de botella síncronos en las llamadas a utilidades de API. Migrar `http_fetch_ollama_embedding` a dependencias puramente `async` con `httpx.AsyncClient`.
- **Bloque 8.2: Hardening de Tests Mocks (Input Trust) [PENDING]**
  - Tarea 8.2.1: Extender mocks para *input_trust* (ej. inyectar simulaciones de ataques homoglyphs cirílicos para evadir la puerta de Absoluto Mal y validar la defensa).

---

## 🟠 COLA DE EJECUCIÓN NARANJA (Team Claude)
**Doctrina:** Matemática Bayesiana Avanzada, Modelado Cognitivo, Identidad Persistente y RLHF.

- **Bloque C.1: Fusión BMA y Recompensas RLHF [PENDING]**
  - Tarea C.1.1: Conectar matemáticamente los *outputs* asíncronos del `rlhf_reward_model.py` como *Priors* moduladores fuertes dentro de `src/modules/bayesian_engine.py`.
- **Bloque 9.2: Acumulación de Tensión Límbica Estática [PENDING]**
  - Tarea 9.2.1: Evolucionar el `BayesianEngine` para que pueda integrar un peso negativo de tiempo (decay) si el Lóbulo Perceptivo dicta que un estímulo peligroso (ej. arma) se mantiene visible en el stream visual +5 segundos sin voz humana.
- **Bloque 11.1: Tránsito Subjetivo del Afecto [PENDING]**
  - Tarea 11.1.1: Consolidar las fórmulas del "Espejo Roto" (Trauma) en la identidad central (`identity_reflection.py`), para asegurar que cambie los *multipliers* de utilitarismo en etapas posteriores del modelo moral.

## 🚀 Flujo de Sincronización Recomendado

1. **Semana Actual:** Antigravity (N1) se encarga transversalmente de desmonolitizar `kernel.py` y actualizar las dependencias de concurrencia. Claude y Cursor toman sus ramas (`master-claude`, `master-Cursor`) and abordan C.1 y S.1 respectivamente.
2. **Semana Siguiente:** Sincronización de progresos a `master-antigravity`. Antigravity evalúa el impacto del async I/O en la latencia global del kernel.
3. **Validación N0:** Integración unificada a `main` tras validaciones somáticas.

---

## 🟢 CERRADOS (Histórico de Producción)
*Misiones completadas por el Swarm L2 bajo supervisión L1 (referencia rápida; el detalle sigue en secciones `[DONE]` arriba).*

- Bloque 0.1: Desmonolitización y Abstracción de `kernel.py` (Antigravity/Swarm) `[DONE]`
- Bloque 0.2: Escalabilidad del Chat Server HTTP/ASGI `[DONE]`
- Bloque 10.2: Tribunal Ético Edge & MalAbs local `[DONE]`
- Bloque 10.3: Amortiguación Afectiva (Ganglios Basales EMA) `[DONE]`
- Bloque 12.1: Recursive Narrative Memory (Consolidación) `[DONE]`
