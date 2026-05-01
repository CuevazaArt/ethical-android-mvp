# Roadmap y Backlog de Enjambre (Swarm L2 Work Distribution)

Este documento estructura el volumen de trabajo arquitectónico para el Ethos Kernel bajo el modelo Swarm V4.0 (Pragmatismo Anónimo).

Aquí es donde los agentes de ejecución (LLMs en IDEs) reclaman sus tareas.

> **Track Cursor (L2):** directiva operativa y cierre de ola en [`docs/collaboration/CURSOR_TEAM_CHARTER.md`](../collaboration/CURSOR_TEAM_CHARTER.md); gate de integración en [`docs/collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md).

> [!IMPORTANT]
> **REGLA DE TOMA DE TAREAS (SWARM):**
> 1. Toma el primer bloque marcado como `[PENDING]` del "BACKLOG ABIERTO".
> 1b. Si **no hay** ningún `[PENDING]` en el backlog abierto, usa la **RESERVA (Buffer)**, o abre un bloque de continuidad (p. ej. 30.x) con tarea concreta; el pulso L1 (`python scripts/eval/adversarial_suite.py`) aplica el tercer bloque de conversación (ver `AGENTS.md`).
> 2. Si hay problemas de infraestructura (APIs lentas) o sobran tokens/recursos, toma tareas de la **RESERVA DEL ENJAMBRE (Buffer)**.
> 3. Ejecuta el código para resolverlo siguiendo las Reglas Boy Scout.
> 4. Usa `scripts/swarm_sync.py` al terminar para registrar el avance y hacer el commit.

---

## 📈 ESTADO DE INTEGRACIÓN (PULSE 2026-04-24 / AUDIT L1) [REVISADO] [ACTUALIZADO]
- **V2.22 (Consolidated Core Minimal)**: INTEGRADO. El sistema ha sido consolidado en `src/core/` (V2).
- **V1.0 Final Stabilization**: ARCHIVADO. La arquitectura Tri-Lobo asíncrona V13/V14 ha sido consolidada en un núcleo minimalista para mayor estabilidad en hardware limitado.
- **L1-AUDIT-PULSE (2026-04-24)**: COMPLETADO. Repara imports tras consolidación V2.
- **V2.60 (Feedback Suppression)**: INTEGRADO. Estabilización de audio en Nomad.

---

## ❄️ BLOQUES CONGELADOS (Hardware Constraints)
**Bloque SENSORY-HW: Integración Sensorial Continua de Alta Frecuencia**
- **Motivo:** Limitaciones de hardware en SoC Android antiguos (mic/cam no pueden coexistir).
- **Estado:** CONGELADO. No se dedicarán más recursos hasta disponer de hardware con pipelines de medios independientes.

---

---

## 🚀 BACKLOG ABIERTO: V2 STABILIZATION & CLEANUP (Phase 16)

> **[PROMPT GENERALISTA PARA EL ENJAMBRE (SWARM)]**
> *"Estás autorizado bajo la política de Pragmatismo Anónimo. Hemos completado la consolidación a V2 (src/core/). El objetivo actual es la **Fase 16: Estabilización de V2**. Tu prioridad máxima es reparar la infraestructura rota (imports, scripts, entry points) para que el nuevo núcleo sea funcional. **Instrucciones:** Escoge un bloque [PENDING], repara los imports apuntando a `src.core`, elimina el código legacy redundante, y finaliza siempre con `python scripts/swarm_sync.py --msg '...'`. ¡Ejecuta!"*

**Bloque 40.0: Reparación de Infraestructura V2 (Prioridad 1) [DONE ✅ V2.23]**
- Archivos eliminados: `kernel_lobes/`, `kernel_handlers/`, `modules/`, `kernel_decision.py`, `kernel_components.py`, `kernel_manifest.py`, `kernel_pipeline.py`, `kernel_utils.py`, `real_time_bridge.py`.
- Demo: `pytest tests/core/ -q` → 91 passed.

**Bloque 40.1: Purgado de Bridge y Código Legacy (Prioridad 2) [DONE ✅ V2.24]**
- `src/kernel.py` (bridge) eliminado. `adversarial_suite.py` migrado a `ChatEngine` directo. `main.py` limpio.
- Demo: `python -m src.ethos_cli diagnostics --json` ✅ | `pytest tests/core/ -q` → 91 passed.

**Bloque 40.2: Actualización de Documentación (Prioridad 3) [DONE ✅ V2.25]**
- `README.md` reescrito contra la arquitectura V2 real: tabla de comandos, pipeline de decisión, estructura de `src/core/`, responsabilidades por módulo.
- Sin referencias a `modules/`, `kernel.py`, `EthicalKernel`, ni `--sim 3`.

---

## 🏆 FASE 16: ESTABILIZACIÓN V2 [COMPLETA ✅]

**Todos los bloques cerrados. El repositorio es 100% V2 Core Minimal.**

---

## 🚀 FASE 18: V2 CORE REFINEMENT (Mente y Memoria)

**Bloque 18.1: Recursive Narrative Memory [INTEGRADO ✅]**
- **Tarea:** Implementar destilación multi-nivel de episodios en crónicas temáticas y un Arquetipo central (V2.61 & V2.63).
- **Meta:** Coherencia de identidad a largo plazo sin saturar el contexto del LLM, culminando en un arquetipo dinámico.
- **Archivos:** `src/core/memory.py`, `src/core/identity.py`.

**Bloque 18.2: User Model Enrichment (Cognitive Bias & Risk) [INTEGRADO ✅]**
- **Tarea:** Implementar detección heurística de sesgos del usuario, perfil de riesgo y persistencia a largo plazo (V2.62 & V2.64).
- **Meta:** Calibrar la apertura informativa y el tono del LLM según el estado del usuario, persistiendo entre sesiones.
- **Archivos:** `src/core/user_model.py` (nuevo), `src/core/chat.py`.

---

## 🚀 FASE 26: DESKTOP-FIRST FLUTTER CONVERGENCE (L1 STRATEGIC PIVOT)

**Strategic decision:** freeze active feature development on mobile Nomad and browser dashboards, then concentrate execution on a Flutter desktop interface with the most sellable capabilities (audio perception, video perception, and voice loop). Mobile and web return only after desktop maturity gates pass.

### Architectural guardrails (mandatory)
- **Core-first:** `src/core/` remains the single source of truth. No business logic in Flutter UI widgets.
- **Capability contracts:** Audio, video, and voice must expose stable contracts (`request`, `response`, `error`, `latency_ms`) before UI scaling.
- **Adapter isolation:** Platform specifics live in adapters; no direct platform calls from domain orchestration.
- **Demo-first integration:** Every block closes with executable evidence (test log, run log, or screenshot + trace).
- **Token economy:** default execution in low-cost mode; premium reasoning only for architecture conflicts.

### Freeze policy (to avoid repeated historical mistakes)
- Mobile and web are **frozen for new features**, but not abandoned:
  - Security patches allowed.
  - Smoke checks kept alive.
  - No schema drift from desktop contracts.

### Next-step format (L1 directive, mandatory)
Use this fixed structure in each planning handoff:

```text
[SIGUIENTE] Bloque X.Y — <title>
[POTENCIA SUGERIDA] A (Auto eficiencia) | B (Auto equilibrado) | C (Auto premium)
[MOTIVO] <one line>
[HECHO CUANDO] <verification command or measurable outcome>
```

---

## 🧩 BACKLOG ABIERTO: DESKTOP MIGRATION WAVE (Swarm-ready)

**Bloque 50.0: Contract spine for desktop migration [PENDING]**
- **Goal:** Define canonical contracts for `audio_perception`, `video_perception`, and `voice_turn` with error envelopes and latency telemetry.
- **Files:** `docs/architecture/`, `src/core/` interfaces only if required.
- **Demo:** contract validation test + example payload fixtures.
- **[POTENCIA SUGERIDA]:** C (Auto premium) — architecture contract quality determines all downstream work.

**Bloque 50.1: Flutter desktop shell + kernel transport [DONE ✅]**
- **Goal:** Bootstrap Flutter desktop app shell with resilient connection to existing kernel server.
- **Files:** desktop client module + minimal server handshake alignment.
- **Demo:** cold-start desktop client receives heartbeat and health payload.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (2026-04-30):** New module `src/clients/flutter_desktop_shell` starts on desktop, reaches `/api/ping` + `/api/status`, and recovers after server restart with bounded retry backoff.

**Bloque 50.2: Audio perception vertical slice [PENDING]**
- **Goal:** Desktop microphone capture -> kernel perception endpoint -> UI feedback with latency.
- **Files:** desktop audio adapter + integration boundary tests.
- **Demo:** reproducible log with bounded latency and graceful fallback on missing devices.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 50.3: Video perception vertical slice [PENDING]**
- **Goal:** Desktop camera frame pipeline -> kernel vision context -> UI state update.
- **Files:** desktop video adapter + core boundary validation.
- **Demo:** one deterministic scenario with motion/faces rendering and finite metric guards.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 50.4: Voice full-turn loop (STT -> core -> TTS) [PENDING]**
- **Goal:** End-to-end conversational loop with interruption safety and retry policy.
- **Files:** desktop voice orchestration layer + test harness.
- **Demo:** successful wake/utter/respond cycle and one controlled failure path.
- **[POTENCIA SUGERIDA]:** C (Auto premium) for first pass; B once contracts stabilize.

**Bloque 50.5: Commercial hardening for desktop [PENDING]**
- **Goal:** Packaging, auto-update strategy, telemetry minimum, and crash recovery.
- **Files:** release scripts + runtime health instrumentation.
- **Demo:** install -> run -> update smoke sequence on target desktop OS.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 50.6: Freeze-lane maintenance for web/mobile [PENDING]**
- **Goal:** Keep frozen platforms healthy without feature expansion.
- **Files:** smoke tests, dependency maintenance notes, CI health checks.
- **Demo:** monthly smoke matrix with pass/fail report.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 50.7: Re-entry plan to mobile/web [PENDING]**
- **Goal:** Define objective readiness gates for reopening mobile and web feature work.
- **Files:** `CONTEXT.md` + roadmap docs.
- **Demo:** signed gate checklist with metrics from desktop production-like usage.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

---

## 🚀 Continuidad (sin [PENDING] en Fase 16 — regla 1b)

**Bloque 30.0: Higiene numérica V2 (ChatEngine) [DONE]**
- **Tarea 30.1:** `_finite01` + ramas de `_generate_actions_from_signals` toleran NaN/Inf; tests en `tests/core/test_chat.py`.

**Bloque 30.2: Visión Nomad — telemetría finita en `_build_system` [DONE]**
- **Tarea 30.2:** `_finite01_or_none` / `_non_negative_int_or_none` para `brightness`, `motion`, `faces_detected`; evita comparaciones y f-strings con NaN/Inf.

---

## 🟢 CERRADOS (Histórico de Producción)

**Bloque 15.0: Desmonolitización y Consolidación V1 -> V2 [DONE]**
- [x] 15.1: Reparar Pytest Collection.
- [x] 15.2: Colapsar src/modules/.
- [x] 15.3: Acoplar LLM Real.
- [x] 15.4: Etiquetado de Estado.
- [x] 15.5: Archivar Teatro.
- [x] 15.6: Demo End-to-End Real.

...
