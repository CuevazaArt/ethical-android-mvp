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

**Bloque 50.0: Contract spine for desktop migration [DONE ✅]**
- **Goal:** Define canonical contracts for `audio_perception`, `video_perception`, and `voice_turn` with error envelopes and latency telemetry.
- **Files:** `docs/architecture/`, `src/core/` interfaces only if required.
- **Demo:** contract validation test + example payload fixtures.
- **[POTENCIA SUGERIDA]:** C (Auto premium) — architecture contract quality determines all downstream work.
- **Evidence (2026-04-30):** `docs/architecture/DESKTOP_CONTRACT_SPINE_V1.md` + contract fixtures and validation tests integrated.

**Bloque 50.1: Flutter desktop shell + kernel transport [DONE ✅]**
- **Goal:** Bootstrap Flutter desktop app shell with resilient connection to existing kernel server.
- **Files:** desktop client module + minimal server handshake alignment.
- **Demo:** cold-start desktop client receives heartbeat and health payload.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (2026-04-30):** New module `src/clients/flutter_desktop_shell` starts on desktop, reaches `/api/ping` + `/api/status`, and recovers after server restart with bounded retry backoff.

**Bloque 50.2: Audio perception vertical slice [DONE ✅]**
- **Goal:** Desktop microphone capture -> kernel perception endpoint -> UI feedback with latency.
- **Files:** desktop audio adapter + integration boundary tests.
- **Demo:** reproducible log with bounded latency and graceful fallback on missing devices.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (2026-04-30):** `/api/perception/audio` contract endpoint with success/fallback envelopes and integration tests.

**Bloque 50.3: Video perception vertical slice [DONE ✅]**
- **Goal:** Desktop camera frame pipeline -> kernel vision context -> UI state update.
- **Files:** desktop video adapter + core boundary validation.
- **Demo:** one deterministic scenario with motion/faces rendering and finite metric guards.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (2026-04-30):** `DesktopVideoAdapter` + ws chat integration + non-finite/malformed guards with tests.

**Bloque 50.4: Voice full-turn loop (STT -> core -> TTS) [DONE ✅]**
- **Goal:** End-to-end conversational loop with interruption safety and retry policy.
- **Files:** desktop voice orchestration layer + test harness.
- **Demo:** successful wake/utter/respond cycle and one controlled failure path.
- **[POTENCIA SUGERIDA]:** C (Auto premium) for first pass; B once contracts stabilize.
- **Evidence (50.4A/50.4C/50.4D):** Dark voice UX + backend status binding via `/api/status` (`voice_turn_state`, `voice_turn_state_at`) + explicit success/fallback transition tests.

**Bloque 50.5: Commercial hardening for desktop [DONE ✅]**
- **Goal:** Packaging, auto-update strategy, telemetry minimum, and crash recovery.
- **Files:** release scripts + runtime health instrumentation.
- **Demo:** install -> run -> update smoke sequence on target desktop OS.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (50.5A/50.5B/50.5C, 2026-04-30):** Windows packaging baseline + hardened PowerShell build flow with checked command execution, artifact manifest, and rollback checklist generation.

**Bloque 50.6: Freeze-lane maintenance for web/mobile [DONE ✅]**
- **Goal:** Keep frozen platforms healthy without feature expansion.
- **Files:** smoke tests, dependency maintenance notes, CI health checks.
- **Demo:** monthly smoke matrix with pass/fail report.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).
- **Evidence (2026-04-30):** freeze matrix + fixture-driven schema guardrails (`tests/test_freeze_lane_guardrails.py`).

**Bloque 50.7: Re-entry plan to mobile/web [DONE ✅]**
- **Goal:** Define objective readiness gates for reopening mobile and web feature work.
- **Files:** `CONTEXT.md` + roadmap docs.
- **Demo:** signed gate checklist with metrics from desktop production-like usage.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).
- **Evidence (50.7A/50.7B):** Re-entry gates documented in `CONTEXT.md` + gate audit proofpack in `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`.

**Bloque 51.0: Stability ledger automation [DONE ✅]**
- **Goal:** Automate auditable evidence for G1 (14-day no-crash desktop smoke).
- **Files:** `scripts/eval/desktop_gate_runner.py`, `docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl`.
- **Demo:** `python scripts/eval/desktop_gate_runner.py stability --ledger docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl --days 14`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 51.1: Voice latency benchmark harness [DONE ✅]**
- **Goal:** Compute p95 full-turn voice latency against re-entry threshold.
- **Files:** `scripts/eval/desktop_gate_runner.py`, `docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl`.
- **Demo:** `python scripts/eval/desktop_gate_runner.py latency --samples docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl --target-p95-ms 2500`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 51.2: Demo reliability checklist runner [DONE ✅]**
- **Goal:** Evaluate scripted demo reliability (10/10) from versioned checklist evidence.
- **Files:** `scripts/eval/desktop_gate_runner.py`, `docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json`.
- **Demo:** `python scripts/eval/desktop_gate_runner.py demo --checklist docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json --required-count 10`.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 51.3: CI gate-report integration [DONE ✅]**
- **Goal:** Execute desktop re-entry gate evaluation in GitHub Actions and publish auditable artifact.
- **Files:** `.github/workflows/ci.yml`.
- **Demo:** CI job `desktop-gate-report` uploads `desktop-gate-report` artifact with G1/G2/G4 JSON outputs.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 51.4: CI gate summary visibility [DONE ✅]**
- **Goal:** Surface G1/G2/G4 pass-fail summary directly in workflow run UI.
- **Files:** `.github/workflows/ci.yml`.
- **Demo:** `desktop-gate-report` writes markdown table to `GITHUB_STEP_SUMMARY`.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 52.0: Contract no-drift monthly closure automation [DONE ✅]**
- **Goal:** Version monthly G3 evidence with objective PASS/IN_PROGRESS/FAIL status.
- **Files:** `scripts/eval/freeze_lane_monthly_report.py`, `docs/collaboration/evidence/G3_CONTRACT_NO_DRIFT_HISTORY.jsonl`.
- **Demo:** `python scripts/eval/freeze_lane_monthly_report.py --record-run --allow-in-progress`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.1: Daily stability ledger append automation [DONE ✅]**
- **Goal:** Eliminate manual edits for G1 smoke evidence while preventing duplicate day entries.
- **Files:** `scripts/eval/append_stability_ledger.py`, `docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl`.
- **Demo:** `python scripts/eval/append_stability_ledger.py --date 2026-05-01T09:00:00Z --status pass --cycle desktop-smoke --note "No critical crash; daily automation entry."`.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 52.2: Live voice latency capture harness [DONE ✅]**
- **Goal:** Replace static latency samples with endpoint-driven capture records.
- **Files:** `scripts/eval/capture_voice_turn_latency.py`, `docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl`.
- **Demo:** `python scripts/eval/capture_voice_turn_latency.py --base-url http://127.0.0.1:8000 --samples 20 --output docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.3: Executable demo reliability runner [DONE ✅]**
- **Goal:** Generate 10/10 demo checklist from runnable integration checks instead of manual toggles.
- **Files:** `scripts/eval/run_demo_reliability_checklist.py`, `docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json`.
- **Demo:** `python scripts/eval/run_demo_reliability_checklist.py --output docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.4: Flutter readiness gates panel [DONE ✅]**
- **Goal:** Expose G1..G5 reopening readiness directly in desktop shell UI.
- **Files:** `src/clients/flutter_desktop_shell/lib/main.dart`, `src/clients/flutter_desktop_shell/test/widget_test.dart`.
- **Demo:** `flutter test` validates rendering of `Re-entry readiness gates` and fallback/source messaging.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.5: Backend reentry-gates status feed [DONE ✅]**
- **Goal:** Publish server-side readiness gate statuses in `/api/status` for Flutter binding.
- **Files:** `src/server/app.py`, `tests/server/test_app_integration.py`.
- **Demo:** `pytest tests/server/test_app_integration.py::test_api_status_returns_all_fields -q`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.6: Reentry gate payload v2 (metadata-rich) [DONE ✅]**
- **Goal:** Expose detailed per-gate metadata (`status`, `source`, `updated_at`, `summary`, `stale`) in backend status payload.
- **Files:** `src/server/app.py`, `tests/server/test_app_integration.py`.
- **Demo:** `pytest tests/server/test_app_integration.py::test_api_status_returns_all_fields -q`.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.7: Flutter gate panel v2 (details + freshness) [DONE ✅]**
- **Goal:** Render per-gate metadata and freshness state in desktop shell UI.
- **Files:** `src/clients/flutter_desktop_shell/lib/main.dart`, `src/clients/flutter_desktop_shell/test/widget_test.dart`, `src/clients/flutter_desktop_shell/README.md`.
- **Demo:** `flutter test` + `flutter analyze` in desktop shell module.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 52.8: CI artifact v2 (details snapshot) [DONE ✅]**
- **Goal:** Publish gate snapshot with detailed metadata in CI artifact and workflow summary.
- **Files:** `.github/workflows/ci.yml`, `scripts/eval/desktop_gate_runner.py`.
- **Demo:** `desktop-gate-report` uploads `reentry-gates-snapshot.json` and summary table includes status/source/updated_at.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 52.9: Gate drift sentinel (schema lock) [DONE ✅]**
- **Goal:** Harden tests so contract drift in `reentry_gates` / `reentry_gates_details` fails fast.
- **Files:** `tests/server/test_app_integration.py`, `tests/eval/test_desktop_gate_runner.py`.
- **Demo:** integration + eval tests validate enums, non-empty source/summary, and parseable timestamps.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 53.0: Evidence freshness policy and ops playbook [DONE ✅]**
- **Goal:** Define stale-evidence SLA and degraded policy for reopen decisions.
- **Files:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`, `CONTEXT.md`, `CHANGELOG.md`, `tests/test_freeze_lane_guardrails.py`.
- **Demo:** freeze guardrail tests assert freshness policy markers exist.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 53.1: Scheduled freshness enforcement in CI [DONE ✅]**
- **Goal:** Audit gate freshness daily and fail CI when evidence is stale.
- **Files:** `.github/workflows/ci.yml`, `scripts/eval/desktop_gate_runner.py`.
- **Demo:** `desktop-gate-report` runs on `schedule`, emits `reentry-gates-snapshot.json`, and enforces stale-gate failure.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

---

## 🚀 FASE 27: FLUTTER MVP EXECUTION CORRIDOR (V2.100.x)

**Directive:** prioritize one product surface (Flutter Desktop + Python kernel), remove repository drift, and prove end-to-end reproducibility before any new expansion.

**Bloque 100.0: Repository truth sync (README/CONTEXT) [DONE ✅]**
- **Goal:** Align public project narrative with active runtime reality (Flutter-first MVP + kernel authority).
- **Files:** `README.md`, `CONTEXT.md`.
- **Demo:** docs clearly state active surface, freeze-lane policy, and quality truth source.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 100.1: Artifact hygiene pass (tracked binaries/logs/db) [DONE ✅]**
- **Goal:** Remove non-source execution artifacts from main branch and guard against reintroduction.
- **Files:** `.gitignore`, repository root tracked artifacts.
- **Demo:** `git status` clean after removing tracked runtime logs/db leftovers.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 100.2: Flutter MVP checkpoint contract [DONE ✅]**
- **Goal:** Define single executable MVP checkpoint (operator-run scenario) with explicit pass/fail criteria.
- **Files:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`, `src/clients/flutter_desktop_shell/README.md`.
- **Demo:** one command sequence that any operator can run to validate checkpoint readiness.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 100.3: End-to-end CI smoke for desktop path [DONE ✅]**
- **Goal:** Add a minimal CI-enforced integration check for desktop critical cycle contracts.
- **Files:** `.github/workflows/ci.yml`, `tests/server/`, optional `scripts/eval/`.
- **Demo:** CI fails when critical desktop cycle contract breaks.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 100.4: Documentation pruning index and active set [DONE ✅]**
- **Goal:** Define active-doc index and archive policy to reduce navigation entropy.
- **Files:** `docs/INDEX.md` (new), `docs/proposals/INDEX.md`, archive pointers.
- **Demo:** active documentation tree reduced to an explicit, auditable set.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 100.5: Public naming and scope alignment pass [DONE ✅]**
- **Goal:** Align public-facing naming and scope language with Flutter-first MVP reality.
- **Files:** `README.md`, selected top-level docs with conflicting Android-primary claims.
- **Demo:** no top-level active docs describe Android as the primary active product surface.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 100.6: CI observation and release-readiness checkpoint [DONE ✅]**
- **Goal:** Confirm post-enmienda CI behavior and summarize release readiness after the 100.x corrective wave.
- **Files:** GitHub Actions run status + `CONTEXT.md` pulse.
- **Demo:** updated readiness snapshot referencing latest `main` validations.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 100.7: Final closure pulse and tag recommendation [DONE ✅]**
- **Goal:** Publish final closure pulse for the corrective wave and recommend release tag criteria.
- **Files:** `CONTEXT.md`, `CHANGELOG.md`.
- **Demo:** closure criteria and tag recommendation documented after CI stabilization.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 100.8: Post-wave CI settle watch [DONE ✅]**
- **Goal:** Confirm latest in-progress CI run reaches success and clear residual run confusion.
- **Files:** CI run status observation + closure note.
- **Demo:** final checkpoint states no blocking in-progress CI for the corrective wave.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 100.9: Formal phase close packet [DONE ✅]**
- **Goal:** Produce the final close packet for this corrective wave (status, deltas, next command).
- **Files:** `CONTEXT.md`, `CHANGELOG.md`.
- **Demo:** one concise closure packet ready for operator handoff.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.0: Flutter MVP execution wave handoff [DONE ✅]**
- **Goal:** Start next execution wave focused on feature-depth in active Flutter MVP lane.
- **Files:** `src/clients/flutter_desktop_shell/lib/main.dart`, `src/clients/flutter_desktop_shell/test/widget_test.dart`, plan/context/changelog sync.
- **Demo:** gate panel now computes and renders MVP checkpoint state (`READY`, `DEGRADED`, `BLOCKED`, `PENDING`) from G1..G5 + freshness details.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 101.1: Flutter MVP interaction depth slice [DONE ✅]**
- **Goal:** Add one user-visible interaction-depth slice in Flutter (beyond transport status) with strict server-contract boundaries.
- **Files:** Flutter shell module + targeted tests.
- **Demo:** status card includes manual `Check now` probe action with explicit probe timestamp and no regression in gate/voice panels.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 101.2: Flutter payload ergonomics pass [DONE ✅]**
- **Goal:** Improve status payload usability (quick diagnostics actions) without changing backend contracts.
- **Files:** `src/clients/flutter_desktop_shell/lib/main.dart`, targeted widget tests.
- **Demo:** payload panel now exposes `Copy JSON` action with deterministic feedback text.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.3: Flutter diagnostics timeline slice [DONE ✅]**
- **Goal:** Surface compact diagnostics timeline in UI from existing client-side state transitions.
- **Files:** Flutter shell module + tests.
- **Demo:** new `Diagnostics timeline` card renders recent events (or empty-state message) in desktop shell.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 101.4: Flutter diagnostics filtering pass [DONE ✅]**
- **Goal:** Add lightweight event filtering/controls for faster operator triage in diagnostics timeline.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics timeline now provides `All`, `Transport`, and `Manual` filter controls.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.5: CI split for Python vs Flutter lane [DONE ✅]**
- **Goal:** Prevent false-red CI on Flutter-only changes while preserving strict Python quality gates.
- **Files:** `.github/workflows/ci.yml`.
- **Demo:** `quality/windows-smoke/desktop-gate-report` run only on Python-affecting changes; Flutter-only changes run `flutter-desktop-smoke`.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.6: Flutter diagnostics retention tuning [DONE ✅]**
- **Goal:** Expose compact retention controls for diagnostics timeline depth (short/medium) without backend changes.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics timeline now includes `Short` (4 events) and `Medium` (8 events) depth controls.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.7: Flutter diagnostics UX polish pass [DONE ✅]**
- **Goal:** Improve diagnostics card readability and operator affordance with minimal UI polish.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics events now render with type badges (`TRANSPORT` / `MANUAL`) for faster scanning.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.8: Flutter wave stabilization checkpoint [DONE ✅]**
- **Goal:** Consolidate current 101.x UI slices and confirm no regressions in active shell behavior.
- **Files:** Flutter shell tests + context/changelog pulse.
- **Demo:** local flutter tests + invariants pass; CI shows new lane-split success (`101.6`) with latest runs progressing on updated commits.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 101.9: Flutter diagnostics interaction polish [DONE ✅]**
- **Goal:** Add one small interaction refinement to diagnostics panel while preserving current contracts.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics panel now includes `Clear timeline` action and explicit visible-count indicator.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.0: Flutter wave handoff checkpoint [DONE ✅]**
- **Goal:** Close 101.x mini-wave with a concise checkpoint and define next feature-depth objective.
- **Files:** `CONTEXT.md`, `CHANGELOG.md`, plan handoff lines.
- **Demo:** latest 101.6..101.9 CI runs green and handoff objective documented.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.1: Flutter diagnostics snapshot export [DONE ✅]**
- **Goal:** Add one-click export of current diagnostics timeline summary for operator incident notes.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics card now provides `Copy snapshot` and deterministic export feedback line.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.2: Flutter diagnostics severity hinting [DONE ✅]**
- **Goal:** Add lightweight severity hinting for diagnostics events to prioritize operator attention.
- **Files:** Flutter shell module + tests.
- **Demo:** diagnostics events now render deterministic severity badges (`HIGH`, `MED`, `LOW`) from message heuristics.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.3: Flutter diagnostics wave checkpoint [DONE ✅]**
- **Goal:** Record a concise checkpoint after severity rollout and confirm no regressions.
- **Files:** `CONTEXT.md`, `CHANGELOG.md`, plan handoff line.
- **Demo:** checkpoint now captures local validation posture (`flutter test`, collaboration invariants) after severity rollout.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.4: Flutter diagnostics severity filter toggle [DONE ✅]**
- **Goal:** Add optional severity filter chips (`All`, `High`, `Med`, `Low`) to narrow incident triage quickly.
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics list now supports deterministic severity filtering while preserving existing type/depth controls.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.5: Flutter diagnostics severity counters [DONE ✅]**
- **Goal:** Show compact `high/med/low` counters in diagnostics card for instant triage density.
- **Files:** Flutter shell module + widget tests.
- **Demo:** counter strip now renders deterministic totals and updates after manual probe + filter interactions.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 102.6: Flutter diagnostics triage milestone checkpoint [DONE ✅]**
- **Goal:** Register closure of the triage slice (`102.2` to `102.5`) before next feature wave.
- **Files:** `CONTEXT.md`, `CHANGELOG.md`, plan handoff line.
- **Demo:** checkpoint now records triage capabilities and refreshed local validation (`flutter test` + collaboration invariants).
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.0: Flutter diagnostics next-wave planning checkpoint [DONE ✅]**
- **Goal:** Open the next diagnostics UX wave with a compact, test-first target definition.
- **Files:** plan handoff line + `CONTEXT.md`.
- **Demo:** next-wave scope anchored around operator triage acceleration with deterministic UI behavior.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.1: Flutter diagnostics quick triage actions [DONE ✅]**
- **Goal:** Add one-click triage actions to focus urgent events and reset filter state quickly.
- **Files:** Flutter shell module + widget tests.
- **Demo:** `Focus high` and `Reset filters` actions update visible diagnostics deterministically.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.2: Flutter diagnostics high-alert strip [DONE ✅]**
- **Goal:** Surface a clear high-severity warning strip whenever urgent diagnostics are present.
- **Files:** Flutter shell module + widget tests.
- **Demo:** high-alert strip appears with count and operator wording once high-severity events exist.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.3: Perception hardware readiness brief [DONE ✅]**
- **Goal:** Define minimal hardware shortlist and go/no-go criteria for basic perception pilot.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** shortlist and acceptance criteria are explicit and decoupled from Flutter sprint lane.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.4: Perception pilot execution checklist [DONE ✅]**
- **Goal:** Convert readiness brief into a deterministic first-pilot checklist (setup, capture, validation, rollback).
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** first-run checklist now defines timed steps, pass/fail criteria, and rollback in one operator flow (<30 minutes).
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.5: Perception pilot evidence template [DONE ✅]**
- **Goal:** Define a compact evidence template for pilot runs (inputs, metrics, decision, incidents).
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** evidence template now enforces mandatory sections and deterministic `GO`/`NO-GO` decision fields.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 103.6: Perception pilot readiness checkpoint [DONE ✅]**
- **Goal:** Consolidate readiness artifacts (`103.3`-`103.5`) and declare pilot start gate.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** checkpoint now confirms active shortlist, execution checklist, and evidence template before pilot-1.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 104.0: Perception pilot prompt-sprint kickoff [DONE ✅]**
- **Goal:** Launch a wider prompt sprint for pilot-1 execution while keeping Flutter diagnostics lane active.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** sprint prompt chain is explicit, sequential, and ready for single-agent autopilot execution.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 104.1: Pilot-1 dry-run evidence seed [DONE ✅]**
- **Goal:** Produce first evidence record using the 103.5 template with synthetic or controlled local inputs.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** one complete synthetic evidence artifact is captured with all mandatory fields.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 104.2: Pilot-1 incident taxonomy pass [DONE ✅]**
- **Goal:** Normalize incident labels so future pilot runs are comparable.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** incident categories and severity mapping are explicitly defined for evidence reports.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 104.3: Pilot-1 go/no-go rubric lock [DONE ✅]**
- **Goal:** Prevent ambiguous hardware decisions by freezing deterministic decision thresholds.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** GO / GO-WITH-CONSTRAINTS / NO-GO thresholds are locked and referenced by evidence template.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 104.4: Pilot lane handoff checkpoint [DONE ✅]**
- **Goal:** Close sprint with explicit pilot lane status before any hardware scale-up.
- **Files:** planning/docs checkpoint (`CONTEXT.md` + plan entry).
- **Demo:** lane status, open risks, and next execution owner are synchronized.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 105.0: Pilot-1 controlled hardware run [DONE ✅]**
- **Goal:** Execute first real hardware pilot using locked checklist and evidence rubric.
- **Files:** pilot evidence output + context/plan checkpoint.
- **Demo:** one controlled pilot run evidence payload is validated with deterministic `NO-GO` decision and explicit blocker trace.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 105.1: Pilot-1 physical hardware execution [DONE ✅]**
- **Goal:** Repeat pilot run with physically connected starter hardware and update decision from controlled baseline.
- **Files:** pilot evidence output + context/plan checkpoint.
- **Demo:** physical-attempt evidence payload validated by rubric with deterministic `NO-GO` due missing capture devices.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 105.2: Pilot-1 hardware procurement checkpoint [DONE ✅]**
- **Goal:** Convert physical-attempt blockers into a minimal procurement/connection checklist for rerun.
- **Files:** context/plan checkpoint.
- **Demo:** executable preflight report now lists mic/camera/audio availability and exposes rerun blockers deterministically.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 105.3: Pilot-1 physical rerun gate [DONE ✅]**
- **Goal:** Re-run pilot once preflight reports ready=true and capture updated evidence decision.
- **Files:** evidence JSON + context/plan checkpoint.
- **Demo:** executable rerun gate report now emits deterministic `BLOCKED`/`PASS`; current state is `BLOCKED` until camera+mic path is available.
- **[POTENCIA SUGERIDA]:** B (Auto equilibrado).

**Bloque 105.4: Hardware unblock action list [DONE ✅]**
- **Goal:** Produce minimal operator checklist to flip preflight from `false` to `true`.
- **Files:** context/plan checkpoint.
- **Demo:** operator checklist now includes physical reconnect, Windows privacy/driver recovery, preflight rerun, and gate pass criteria.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 105.5: Pilot rerun execution after unblock [POSTPONED ⏸️]**
- **Goal:** Execute rerun gate with connected mic/camera and update pilot decision status.
- **Files:** updated preflight + rerun gate reports + context/plan checkpoint.
- **Demo:** deferred until physical perception hardware is available in the active environment.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.0: Flutter blocked-summary export [DONE ✅]**
- **Goal:** Add software-only triage export focused on blocking/high-severity diagnostics.
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics card now includes `Copy blocked summary` action with deterministic feedback.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.1: Flutter diagnostics lane continuation checkpoint [DONE ✅]**
- **Goal:** Keep sprint velocity on Flutter UX while hardware lane stays paused.
- **Files:** context/plan checkpoint.
- **Demo:** checkpoint explicitly tracks hardware postponement and active software-only next step.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.2: Flutter diagnostics quick incident note [DONE ✅]**
- **Goal:** Add one-click note template export for incident tickets (status, counters, latest high event).
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics card now exports deterministic incident-note text via `Copy incident note`.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.3: Flutter software-lane stabilization checkpoint [DONE ✅]**
- **Goal:** Consolidate software-only diagnostics gains after 106.0-106.2 before new UX expansion.
- **Files:** context/plan checkpoint.
- **Demo:** checkpoint captures current software lane scope, validation posture, and next low-risk UI increment.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.4: Flutter diagnostics event-pin action [DONE ✅]**
- **Goal:** Add one-click "pin latest high event" helper for operator handoff continuity.
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics card now pins latest high-severity event into persistent note line.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.5: Flutter pinned-note export action [DONE ✅]**
- **Goal:** Let operators copy the pinned event note directly for incident handoff.
- **Files:** Flutter shell module + widget tests.
- **Demo:** `Copy pinned note` action exports current pinned note and emits deterministic feedback.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.6: Flutter prompt-sprint kickoff (software lane) [DONE ✅]**
- **Goal:** Open next chained sprint for diagnostics UX polish while hardware lane remains paused.
- **Files:** context/plan checkpoint.
- **Demo:** chained prompt sequence is explicit and ordered for autopilot execution.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.7: Pinned note visibility polish [DONE ✅]**
- **Goal:** Improve readability/scannability of pinned diagnostics note in crowded event states.
- **Files:** Flutter shell module + widget tests.
- **Demo:** pinned note now renders inside a dedicated styled container with explicit title.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.8: Diagnostics action bar grouping pass [DONE ✅]**
- **Goal:** Reduce operator cognitive load by grouping copy/pin/filter actions in consistent order.
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics action area now has deterministic groups (`Export actions`, `Pin actions`).
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 106.9: Software-lane handoff checkpoint [DONE ✅]**
- **Goal:** Close mini-wave with explicit scope and validation posture before next UI expansion.
- **Files:** context/plan/changelog.
- **Demo:** chain completion and next software-only successor block are synchronized.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 107.0: Diagnostics mini-wave kickoff [DONE ✅]**
- **Goal:** Open the next software-only UX mini-wave after 106.6-106.9 closure.
- **Files:** context/plan checkpoint.
- **Demo:** next chain is explicit and ready for autopilot execution.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 107.1: Diagnostics empty-state guidance polish [DONE ✅]**
- **Goal:** Clarify operator next actions when diagnostics list is empty.
- **Files:** Flutter shell module + widget tests.
- **Demo:** empty diagnostics state now includes actionable guidance text.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 107.2: Diagnostics feedback tone normalization [DONE ✅]**
- **Goal:** Keep action feedback messages concise and consistent for faster scanning.
- **Files:** Flutter shell module + widget tests.
- **Demo:** diagnostics feedback messages now follow a consistent `Diagnostics: ...` verbal pattern.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 107.3: Software-lane checkpoint [DONE ✅]**
- **Goal:** Close the mini-wave with explicit scope and validation posture.
- **Files:** context/plan/changelog.
- **Demo:** 107.x completion and queued successor block are synchronized.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

**Bloque 108.0: Diagnostics microcopy and affordance kickoff [PENDING]**
- **Goal:** Open next software-only UX pass focused on clarity and low-friction interactions.
- **Files:** context/plan checkpoint.
- **Demo:** bounded prompt chain is ready for sequential autopilot execution.
- **[POTENCIA SUGERIDA]:** A (Auto eficiencia).

### Next prompts (mandatory format)

[SIGUIENTE] Bloque 108.0 — Diagnostics microcopy and affordance kickoff
[POTENCIA SUGERIDA] A (Auto eficiencia)
[MOTIVO] Continue software-only velocity with bounded UI clarity upgrades.
[HECHO CUANDO] Next prompt chain is explicit and queued in deterministic order.

### Sprint prompts (108.x chain)

[SIGUIENTE] Bloque 108.1 — Diagnostics empty-state CTA polish
[POTENCIA SUGERIDA] A (Auto eficiencia)
[MOTIVO] Improve readability and operator guidance when diagnostics are idle.
[HECHO CUANDO] Empty-state and guidance copy are concise, actionable, and test-covered.

[SIGUIENTE] Bloque 108.2 — Diagnostics feedback microcopy pass
[POTENCIA SUGERIDA] A (Auto eficiencia)
[MOTIVO] Refine wording consistency across copy/export/pin actions.
[HECHO CUANDO] Feedback strings are normalized and validated by widget assertions.

[SIGUIENTE] Bloque 108.3 — Software-lane checkpoint
[POTENCIA SUGERIDA] A (Auto eficiencia)
[MOTIVO] Close mini-wave with explicit scope and readiness for the next UX slice.
[HECHO CUANDO] Context/plan/changelog align on 108.x completion and successor queue.

### Re-entry gates (authoritative checklist)
- **Gate G1 (stability):** 14 consecutive days with no critical desktop crash in smoke cycle.
- **Gate G2 (latency):** p95 end-to-end voice turn under 2500 ms on target desktop profile.
- **Gate G3 (contract discipline):** 0 schema drift findings in freeze-lane contract checks for one full month.
- **Gate G4 (demo reliability):** 10/10 successful scripted demos (audio + video + voice) under operator checklist.
- **Gate G5 (ops readiness):** reproducible packaging flow + release manifest + rollback instructions validated.

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
