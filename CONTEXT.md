# Session Context — Ethos

> Read this file first. It defines the active product scope and execution constraints.

## Current state (authoritative)

- **Active product:** Flutter Desktop MVP backed by the Python kernel server.
- **Business-logic authority:** `src/core/` only.
- **Server boundary:** `src/server/` contracts consumed by Flutter.
- **Mobile status:** freeze-lane for net-new features (security/health maintenance only).
- **Canonical roadmap:** `docs/proposals/PLAN_WORK_DISTRIBUTION_TREE.md`.

## Strategic amendment (V2.100)

- Ethos execution is now explicitly **Flutter-first for MVP completion**.
- Desktop is the single active client surface until MVP evidence is complete.
- Android work remains frozen except critical fixes.
- Product progress is measured by reproducible end-to-end behavior, not block count.

## Re-entry gates (mobile/web reopen)

- **G1 Stability:** 14 consecutive days without critical desktop crash in smoke cycle.
- **G2 Voice latency:** p95 full voice turn under 2500 ms on target desktop hardware.
- **G3 Contract no-drift:** 0 failures in freeze-lane checks for one full calendar month.
- **G4 Demo reliability:** 10/10 scripted demos across audio, video, and voice.
- **G5 Ops readiness:** Windows packaging + artifact manifest + rollback checklist validated.
- **Freshness policy:** stale evidence is treated as `DEGRADED` until refreshed inside SLA.

## Product checkpoint (must-pass)

- **Checkpoint:** a reproducible desktop session with a full interaction cycle and auditable logs.
- **Operational question:** can a non-author operator run the desktop cycle without manual debugging?
- **Rule:** no new client expansion before this checkpoint is consistently reproducible.

## Active execution wave

- **Wave:** V2.100.x — repository truth sync + hygiene + Flutter MVP depth.
- **Completed now:** repository truth sync (`100.0`), tracked artifact hygiene (`100.1`), MVP checkpoint contract runbook (`100.2`), CI desktop status smoke gate (`100.3`), active-doc index pruning (`100.4`), and public naming/scope alignment (`100.5`).
- **Validation basis:** CI + local reproducible checks; no manual “green” claims in docs.

### Execution pulse 100.6 (readiness checkpoint)

- Latest merged blocks: `100.1` to `100.5` on `main`.
- CI observation after corrective wave:
  - `100.4` CI run: `success`.
  - `100.5` CI run: `queued` at observation time.
  - Prior `100.3` run remained `in_progress` at observation time.
- Readiness interpretation:
  - corrective wave is integrated and synchronized on `main`;
  - closure tagging should wait for queued/in-progress CI runs to settle green.

### Execution pulse 100.7 (closure and tag recommendation)

- Corrective wave status: `100.1` through `100.7` merged on `main`.
- CI posture at this checkpoint:
  - latest visible stable runs: `100.5` and `100.4` were `success`;
  - `100.6` run was still `in_progress` at observation time;
  - earlier `100.2` failure is superseded by later successful corrective runs.
- Tag recommendation:
  - create/update closure tag only after latest run for `HEAD` resolves `success`;
  - use the latest successful `main` head as the only tag source for this wave.

### Execution pulse 100.8 (CI settle watch)

- Latest run for `100.7` (`25202632860`) completed `success`.
- `100.6`, `100.5`, and `100.4` runs are also `success`.
- No active blocking in-progress run remains for the corrective wave closure checkpoint.
- Historical `100.3` failure is superseded by subsequent successful runs on newer commits.

### Execution pulse 100.9 (formal close packet)

- Scope closed: repository truth sync, artifact hygiene, MVP checkpoint contract, CI desktop smoke gate, active-doc pruning, and naming/scope alignment.
- Verification status: latest corrective-wave runs (`100.5`..`100.8`) observed as `success`.
- Repository state: `main` synchronized, clean working tree, corrective wave fully integrated.
- Operator handoff:
  - Corrective wave is closed.
  - Next execution wave should start at `101.0` with Flutter MVP feature-depth objectives only.

### Execution pulse 101.0 (Flutter depth handoff started)

- Implemented first post-corrective Flutter depth increment:
  - `MVP checkpoint` state is now computed in the gate card from `G1..G5` + freshness.
  - States rendered: `READY`, `DEGRADED`, `BLOCKED`, `PENDING`.
- Contract discipline preserved:
  - no new business logic moved out of server/core boundaries;
  - UI derives state only from existing `/api/status` gate payloads.

### Execution pulse 101.1 (interaction depth slice)

- Added manual transport probe action in Flutter status card (`Check now`) for operator-driven reconnection checks.
- UI now records and renders `Last manual probe` timestamp for traceable diagnostics steps.
- Existing contract surfaces (`voice_turn_state`, `reentry_gates`, `reentry_gates_details`) remain unchanged.

### Execution pulse 101.2 (payload ergonomics)

- Added `Copy JSON` quick action in Flutter payload card for faster operator diagnostics.
- Added explicit deterministic feedback line after payload action (success/fallback message).
- No backend contract changes; improvement remains UI-only on active surface.

### Execution pulse 101.3 (diagnostics timeline)

- Added `Diagnostics timeline` card to Flutter shell for recent local transport/UI events.
- Timeline keeps a bounded recent history for quick operator triage without payload scanning.
- Empty-state diagnostics message is explicit and covered by widget tests.

### Execution pulse 101.4 (diagnostics filtering)

- Added lightweight diagnostics filters in Flutter shell timeline: `All`, `Transport`, `Manual`.
- Operators can now isolate manual probe events from transport noise in real time.
- Feature remains client-side and keeps server contracts unchanged.

### Execution pulse 101.5 (CI lane split)

- CI workflow now separates Python-impacting and Flutter-impacting changes.
- Python-heavy jobs (`quality`, `windows-smoke`, `desktop-gate-report`) run only when Python lane changes.
- Flutter lane changes trigger dedicated `flutter-desktop-smoke` job (`flutter test` in desktop shell module).
- This removes false-red CI from historical Python typing debt when only Flutter UI changes are pushed.

### Execution pulse 101.6 (diagnostics retention tuning)

- Added diagnostics timeline retention controls in Flutter shell:
  - `Short` mode keeps 4 recent events.
  - `Medium` mode keeps 8 recent events.
- Retention is applied client-side with deterministic truncation behavior.

### Execution pulse 101.7 (diagnostics UX polish)

- Diagnostics timeline now includes per-event type badges (`TRANSPORT`, `MANUAL`).
- Visual grouping improves operator scan speed for triage during reconnect/probe flows.
- No backend or contract changes introduced.

### Execution pulse 101.8 (stabilization checkpoint)

- Local verification remains green:
  - `flutter test` passed for desktop shell.
  - `verify_collaboration_invariants.py` passed.
- CI progression after lane split:
  - `101.6` completed `success`.
  - newer runs (`101.7` and overlap with `101.5`) observed in-progress during checkpoint.
- Checkpoint interpretation: mini-wave is stable locally and lane-split correction is taking effect in CI.

### Execution pulse 101.9 (diagnostics interaction polish)

- Added diagnostics interaction controls:
  - `Clear timeline` action for fast reset during operator triage.
  - explicit `Showing N event(s)` counter for immediate timeline depth awareness.
- Interaction polish remains UI-only and does not alter backend contracts.

### Execution pulse 102.0 (wave handoff checkpoint)

- Flutter diagnostics mini-wave (`101.1`..`101.9`) is closed.
- CI confirmation:
  - `101.6`, `101.7`, `101.8`, `101.9` all completed `success`.
- Handoff objective opened:
  - `102.1` focuses on diagnostics snapshot export for faster operator incident notes.

### Execution pulse 102.1 (diagnostics snapshot export)

- Added one-click diagnostics snapshot export in Flutter timeline card (`Copy snapshot`).
- Snapshot output includes connection, voice state, retry count, gate source, and visible events.
- Export path includes deterministic user feedback (`copied` / fallback failure message).

### Execution pulse 102.2 (severity hinting)

- Diagnostics events now include deterministic severity hints:
  - `HIGH` for connection-loss/error-like signals,
  - `MED` for retry/manual-probe context,
  - `LOW` for routine informational events.
- Severity is computed client-side from event message heuristics.

### Execution pulse 102.3 (wave checkpoint)

- Post-102.2 local validation remains green:
  - `flutter test` in `src/clients/flutter_desktop_shell`,
  - `python scripts/eval/verify_collaboration_invariants.py`.
- Sequence is ready for the next diagnostics usability slice (`102.4`: severity filter toggle).

### Execution pulse 102.4 (severity filter toggle)

- Added severity filter chips (`Severity: All`, `High`, `Med`, `Low`) on diagnostics timeline.
- Event visibility now combines two deterministic filters:
  - event type (`All` / `Transport` / `Manual`),
  - severity (`All` / `High` / `Med` / `Low`).
- Widget coverage now validates severity filter interaction path after manual probe.

### Execution pulse 102.5 (severity counters) — milestone reached

- Added diagnostics severity counters in-card (`High`, `Med`, `Low`) computed from buffered events.
- Counters update deterministically after event ingestion and reset on `Clear timeline`.
- This closes the triage mini-wave (`102.2` to `102.5`): severity labels, severity filter, and density counters are now operational.

### Execution pulse 102.6 (triage milestone checkpoint)

- Milestone checkpoint confirmed for diagnostics triage slice (`102.2` to `102.5`).
- Current local validation posture remains green:
  - `flutter test` in `src/clients/flutter_desktop_shell`,
  - `python scripts/eval/verify_collaboration_invariants.py`.
- Sequence opened for next diagnostics UX planning checkpoint (`103.0`).

### Execution pulse 103.0 (next-wave planning checkpoint)

- Next-wave objective defined: accelerate operator triage loop with low-friction, deterministic controls.
- Scope guard: keep changes in Flutter desktop shell and widget-test lane only.

### Execution pulse 103.1 (quick triage actions)

- Added one-click diagnostics actions:
  - `Focus high`: jumps filters to urgent-only view,
  - `Reset filters`: restores broad diagnostics view.
- Interaction behavior is deterministic and covered in widget tests.

### Execution pulse 103.2 (high-alert strip)

- Added high-severity warning strip in diagnostics card.
- Strip appears only when high-severity events exist and shows current urgent-event count.
- This widens sprint throughput (planning + actions + alerting) while preserving green local validation.

### Execution pulse 103.3 (perception hardware readiness brief)

- Hardware discovery opens in parallel lane (without blocking Flutter diagnostics delivery).
- Minimal pilot shortlist (starter tier):
  - **Mic:** USB cardioid mic with native Windows support (48 kHz capable).
  - **Camera:** UVC-compliant 1080p webcam (stable at 30 fps in low light).
  - **Audio out:** wired headset for echo-controlled turn validation.
- Pilot go/no-go acceptance criteria:
  - **Capture stability:** no device disconnect during 15-minute run.
  - **Input latency:** stable capture and handoff behavior suitable for p95 turn target envelope.
  - **Signal quality:** intelligible speech at normal desk distance and face detection reliability in baseline lighting.
  - **Rollback safety:** operator can disable perception hardware path and return to transport-only mode in one step.

### Execution pulse 103.4 (perception pilot execution checklist)

- Deterministic first-pilot flow (<30 min, one operator):
  1. **Setup (5 min):** connect starter hardware (USB mic, UVC cam, wired headset), verify OS device availability.
  2. **Baseline transport check (3 min):** run desktop shell transport probe and confirm no regression before perception inputs.
  3. **Capture run (10 min):** execute speech + face-presence routine under normal desk conditions; observe disconnects, clipping, and frame stability.
  4. **Validation gate (7 min):** classify pass/fail for stability, latency envelope, and signal quality against 103.3 criteria.
  5. **Rollback drill (3 min):** disable perception path and confirm return to transport-only diagnostics view.
- Pilot is accepted only when all five stages complete with explicit PASS and no unresolved blocker.

### Execution pulse 103.5 (perception pilot evidence template)

- Standard evidence template for each pilot run:
  1. **Run metadata:** date/time, operator, desktop profile, hardware IDs (mic/cam/headset).
  2. **Input conditions:** room noise level (qualitative), lighting condition, desk distance, sample duration.
  3. **Core metrics (mandatory):**
     - capture disconnect count,
     - dropped/invalid frame observations,
     - operator-rated speech intelligibility (1-5),
     - observed turn-latency envelope (within/outside target band),
     - rollback success (`PASS`/`FAIL`).
  4. **Incidents:** concise list of anomalies with timestamp and suspected trigger.
  5. **Decision:** `GO`, `GO-WITH-CONSTRAINTS`, or `NO-GO`, plus next action owner.
- Any pilot run without all five sections is considered invalid evidence for hardware scaling decisions.

### Execution pulse 103.6 (perception pilot readiness checkpoint)

- Pilot-1 start gate is now explicit and active:
  - hardware shortlist (`103.3`) available,
  - execution checklist (`103.4`) available,
  - evidence template (`103.5`) available.
- Next phase opened as a wider chained sprint (`104.x`) to move from readiness docs into pilot execution artifacts and decision locks.

### Execution pulse 104.0 (prompt-sprint kickoff)

- Launched chained pilot sprint (`104.1` to `104.4`) for single-agent sequential execution.
- Scope remained in planning/evidence lane; Flutter diagnostics lane stays unblocked.

### Execution pulse 104.1 (dry-run evidence seed)

- Seeded first synthetic evidence artifact using the 103.5 template:
  - metadata and input conditions filled,
  - core metrics populated in controlled (non-hardware-production) mode,
  - deterministic decision field completed.
- This artifact is explicitly synthetic and used only to validate reporting discipline before real hardware run.

### Execution pulse 104.2 (incident taxonomy pass)

- Locked incident taxonomy for pilot evidence consistency:
  - `capture_disconnect`,
  - `audio_clipping`,
  - `audio_dropout`,
  - `frame_drop`,
  - `latency_spike`,
  - `rollback_failure`.
- Severity mapping:
  - **HIGH:** disconnects, rollback failure, repeated latency spikes.
  - **MED:** intermittent clipping/dropout or frame-drop bursts.
  - **LOW:** transient recoverable anomalies with no user-impact escalation.

### Execution pulse 104.3 (go/no-go rubric lock)

- Locked deterministic decision rubric:
  - **GO:** zero HIGH incidents, rollback PASS, and latency envelope within target.
  - **GO-WITH-CONSTRAINTS:** one bounded MED pattern with rollback PASS and explicit mitigation owner.
  - **NO-GO:** any rollback FAIL, any unresolved HIGH incident, or unstable capture continuity.
- Rubric is now mandatory reference for pilot decision fields.

### Execution pulse 104.4 (pilot lane handoff checkpoint)

- Closed `104.x` sprint and handed off to `105.0` controlled hardware run.
- Open risks at handoff:
  - USB device variance across desktop profiles,
  - low-light webcam behavior drift,
  - ambient-noise sensitivity for intelligibility scoring.
- Next execution owner: single operator in autopilot lane, using locked checklist + evidence template + rubric.

### Execution pulse 105.0 (controlled pilot run evidence)

- Added executable evidence validator: `scripts/eval/perception_pilot_evidence_validator.py`.
- Added unit coverage: `tests/eval/test_perception_pilot_evidence_validator.py`.
- Generated controlled pilot evidence payload:
  - `docs/collaboration/evidence/PERCEPTION_PILOT_1_CONTROLLED_RUN.json`
  - validated with `--require-decision-match`.
- Controlled run decision: **NO-GO** (expected) due missing physical mic/camera path and unstable capture envelope.
- Next step is `105.1`: physical hardware execution with the same validator/rubric to update decision status.

### Execution pulse 105.1 (physical hardware attempt)

- Added physical-attempt evidence payload:
  - `docs/collaboration/evidence/PERCEPTION_PILOT_1_PHYSICAL_RUN.json`
  - validated with `scripts/eval/perception_pilot_evidence_validator.py --require-decision-match`.
- Device probe in this environment confirms audio endpoints but no usable camera/mic capture path for pilot requirements.
- Physical attempt decision: **NO-GO** (deterministic), with mitigation owner kept in hardware lane for rerun unblock.
- Next step is `105.2`: hardware procurement/connection checkpoint before the next physical execution.

### Execution pulse 105.2 (hardware procurement checkpoint)

- Added executable preflight tool:
  - `scripts/eval/perception_hardware_preflight.py`
  - writes `docs/collaboration/evidence/PERCEPTION_HARDWARE_PREFLIGHT.json`.
- Preflight report currently shows:
  - `camera_count = 0`,
  - `microphone_count = 0`,
  - `audio_endpoint_count = 2`,
  - `preflight_ready = false`.
- Added tests for preflight readiness logic:
  - `tests/eval/test_perception_hardware_preflight.py`.
- Next gate is `105.3`: physical rerun once preflight flips to ready.

### Execution pulse 105.3 (physical rerun gate)

- Added rerun gate evaluator:
  - `scripts/eval/perception_pilot_rerun_gate.py`
  - writes `docs/collaboration/evidence/PERCEPTION_PILOT_RERUN_GATE_REPORT.json`.
- Gate combines:
  - hardware preflight readiness,
  - physical-run evidence structure/decision integrity,
  - rubric-compatible decision progression.
- Current gate output:
  - `preflight_ready=false`,
  - `computed_decision=NO-GO`,
  - `status=BLOCKED`.
- Added coverage:
  - `tests/eval/test_perception_pilot_rerun_gate.py`.

## System references

- **Freeze policy and evidence matrix:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`
- **CI gate runner:** `scripts/eval/desktop_gate_runner.py`
- **Primary quality command set:** see `README.md` and `CONTRIBUTING.md`
