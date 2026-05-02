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

### Execution pulse 105.4 (hardware unblock actions)

- Added concrete operator unblock checklist:
  - `docs/collaboration/evidence/PERCEPTION_HARDWARE_UNBLOCK_ACTIONS.md`.
- Checklist includes:
  - physical reconnect sequence for mic/camera/audio endpoint,
  - Windows privacy and driver recovery steps,
  - exact preflight and rerun-gate commands with pass criteria.
- This closes preparation loop before `105.5` rerun execution with real hardware path.

### Execution pulse 106.0 (software-lane pivot, blocked summary export)

- Hardware-dependent rerun (`105.5`) is postponed while perception devices are unavailable.
- Added software-only diagnostics feature in Flutter desktop shell:
  - `Copy blocked summary` action in diagnostics card.
  - action exports high-severity-only snapshot for fast incident triage notes.
- Widget coverage updated for the new diagnostics action and feedback line.
- Active execution lane is now Flutter diagnostics continuity until hardware availability changes.

### Execution pulse 106.1 (software-lane continuation checkpoint)

- Confirmed lane policy:
  - hardware-dependent pilot rerun remains postponed,
  - active delivery remains Flutter diagnostics UX only.
- Checkpoint keeps execution unblocked by preserving a strict dependency boundary:
  - no new perception-hardware requirements,
  - no backend contract changes needed for current UI increments.
- Next software slice queued: `106.2` quick incident-note export from diagnostics state.

### Execution pulse 106.2 (quick incident-note export)

- Added `Copy incident note` action in diagnostics card.
- Export payload includes compact triage fields:
  - status (`BLOCKED`/`MONITOR`),
  - connection state,
  - visible event count,
  - severity counters,
  - latest high-severity event message,
  - retry count and gate source.
- Widget coverage confirms action availability and diagnostics feedback update.

### Execution pulse 106.3 (software-lane stabilization checkpoint)

- Software-only diagnostics lane remains stable after consecutive UX slices (`106.0` to `106.2`).
- Validation posture remains green in local loop:
  - `flutter test` for desktop shell module,
  - collaboration invariants check for docs/plan sync.
- Next increment is intentionally low-risk and local-state only (`106.4`: event pinning helper).

### Execution pulse 106.4 (event pin action)

- Added `Pin latest high` action to diagnostics card.
- Added `Clear pin` action to reset pinned state.
- Pinned note now persists in-card as operator handoff anchor even as filters/depth change.

### Execution pulse 106.5 (pinned-note export)

- Added `Copy pinned note` action for one-click handoff export.
- Diagnostics feedback line now reflects pin/export lifecycle:
  - pinned latest event,
  - copied pinned note,
  - cleared pin.
- Next software mini-wave opened as chained prompts (`106.6+`).

### Execution pulse 106.6 (software prompt-sprint kickoff)

- Chained software-only sprint executed in-order under autopilot.
- Scope constrained to diagnostics UX polish with no backend or hardware dependencies.

### Execution pulse 106.7 (pinned note visibility polish)

- Pinned note now renders in a dedicated visual container with explicit title (`Pinned high event note`).
- Visual treatment distinguishes default/no-pin state from active pinned state.

### Execution pulse 106.8 (action bar grouping pass)

- Diagnostics action controls are now grouped for scanability:
  - `Export actions` (snapshot/blocked/incident/pinned copy),
  - `Pin actions` (pin latest, clear pin).
- Interaction ordering is deterministic and reflected in widget baseline assertions.

### Execution pulse 106.9 (software-lane handoff checkpoint)

- Closed `106.6`-`106.9` mini-wave with local validation still green (`flutter test` + invariants).
- Next queue opened as `107.x` software-only chain while hardware lane remains paused.

### Execution pulse 107.0 (mini-wave kickoff)

- Opened and executed bounded software-only mini-wave (`107.1` to `107.3`) under autopilot.
- Scope remained strictly UI/UX diagnostics polish with no hardware/backend dependency.

### Execution pulse 107.1 (empty-state guidance polish)

- Empty diagnostics state now includes explicit operator hint:
  - use `Check now` to seed a fresh diagnostics sample.
- Baseline widget assertions updated to lock this guidance text.

### Execution pulse 107.2 (feedback tone normalization)

- Diagnostics feedback messages normalized into one pattern:
  - `Diagnostics: ...`
- This reduces message-style drift across snapshot/blocked/incident/pin actions.

### Execution pulse 107.3 (software-lane checkpoint)

- Closed `107.x` chain with local validation still green (`flutter test` + invariants).
- Queued next software-only chain as `108.x`.

### Execution pulse 108.0 (microcopy/affordance kickoff)

- Opened and executed bounded `108.x` software-only chain.
- Scope focused on low-friction diagnostics interactions and consistent microcopy.

### Execution pulse 108.1 (empty-state CTA polish)

- Added in-card diagnostics CTA button (`Run check now`) when no diagnostics events are visible.
- CTA mirrors operator intent directly from diagnostics surface (no panel switching required).

### Execution pulse 108.2 (feedback microcopy pass)

- Added `_setDiagnosticsMessage(...)` helper to centralize diagnostics feedback copy.
- Export/pin actions now use one feedback assignment path with consistent `Diagnostics: ...` prefix.

### Execution pulse 108.3 (software-lane checkpoint)

- Closed `108.x` chain with local validation still green:
  - `flutter test`,
  - collaboration invariants.
- Queued successor software-only chain as `109.x`.

### Execution pulse 109.0 (UX continuity kickoff)

- Opened and executed `109.x` software-only chain under autopilot.
- Scope remained limited to diagnostics microcopy and idle-state affordances.

### Execution pulse 109.1 (idle guidance refinement)

- Idle diagnostics copy tightened for faster operator scan:
  - retains explicit idle-state message,
  - keeps actionable `Run check now` CTA path.

### Execution pulse 109.2 (feedback compactness pass)

- Diagnostics feedback remains consistent through `_setDiagnosticsMessage(...)`.
- Copy is shorter and uniform, reducing repeated-line visual noise during rapid actions.

### Execution pulse 109.3 (software-lane checkpoint)

- Closed `109.x` with local validation still green (`flutter test` + invariants).
- Queued successor software-only chain as `110.x`.

### Execution pulse 110.0 (UX chain kickoff)

- Opened and executed bounded `110.x` software-only diagnostics chain.
- Scope stayed local to Flutter diagnostics UX and widget baseline coverage.

### Execution pulse 110.1 (feedback hierarchy pass)

- Diagnostics feedback now includes explicit state badges (`INFO`, `OK`, `ALERT`).
- Feedback wording remains concise while visual hierarchy is clearer for operator triage.

### Execution pulse 110.2 (empty-state affordance trim)

- Idle diagnostics guidance condensed into one actionable line:
  - `No events yet. Use Check now to seed diagnostics.`
- `Run check now` CTA remains in place for direct operator action.

### Execution pulse 110.3 (software-lane checkpoint)

- Closed `110.x` with local validation still green (`flutter test` + invariants).
- Queued successor software-only chain as `111.x`.

### Execution pulse 111.0 (continuity kickoff)

- Opened and executed bounded `111.x` diagnostics UX chain under autopilot.
- Scope remained local to Flutter diagnostics UX and widget baseline updates.

### Execution pulse 111.1 (timeline readability pass)

- Diagnostics timeline rows now separate timestamp and message text for faster scanning.
- Timestamp format is compact (`HH:MM:SS`) to reduce visual noise during repeated events.

### Execution pulse 111.2 (action copy consistency pass)

- Export action labels now follow one consistent style (`Export ...`).
- Diagnostics feedback copy now uses unified "exported/export failed" wording across snapshot/summary/note actions.

### Execution pulse 111.3 (software-lane checkpoint)

- Closed `111.x` with local validation still green (`flutter test` + invariants).
- Queued successor software-only chain as `112.x`.

### Execution pulse 112.0 (gate-driven pivot kickoff)

- Scope pivot is now explicit: diagnostics-card feature work is frozen unless a critical defect appears.
- Active lane shifts from UI micro-polish to MVP closure gates (`G4` first, `G2` provisional next).

### Execution pulse 112.1 (G4 executable desktop demo runner)

- Added reproducible local desktop E2E runner:
  - `scripts/eval/desktop_e2e_demo_runner.py`
  - flow: `/api/ping -> /api/status -> /api/perception/audio -> /api/status`
- Runner emits auditable evidence report:
  - `docs/collaboration/evidence/DESKTOP_E2E_DEMO_REPORT.json`
- Added dedicated tests for the runner:
  - `tests/eval/test_desktop_e2e_demo_runner.py`

### Execution pulse 112.2 (G2 provisional synthetic harness)

- Added synthetic latency harness for hardware-blocked periods:
  - `scripts/eval/g2_synthetic_latency_harness.py`
  - outputs:
    - `docs/collaboration/evidence/VOICE_TURN_LATENCY_SYNTHETIC_SAMPLES.jsonl`
    - `docs/collaboration/evidence/G2_PROVISIONAL_LATENCY_REPORT.json`
- Updated gate evaluators to consume provisional report explicitly:
  - `scripts/eval/desktop_gate_runner.py`
  - `src/server/app.py` (`/api/status` re-entry payload)
- G2 now remains `in_progress` with explicit `PROVISIONAL` summary (no false definitive PASS).

### Execution pulse 112.3 (gate scoreboard checkpoint)

- Gate posture after 112.x execution:
  - `G1`: in_progress (coverage gap remaining)
  - `G2`: in_progress (PROVISIONAL synthetic evidence active)
  - `G3`: in_progress (month-window still accumulating)
  - `G4`: pass (executable local demo runner evidence)
  - `G5`: pass (packaging + rollback validated)
- Successor chain opened as `113.x`, focused on moving `G1` and `G3` toward closure.

### Execution pulse 113.0 (gate stability sprint kickoff)

- Executed full `113.x` gate sprint in-order under autopilot.
- Scope remained gate-first (`G1` and `G3` evidence progression), with no diagnostics-card expansion.

### Execution pulse 113.1 (G1 stability ledger acceleration)

- Added reproducible G1 smoke recorder:
  - `scripts/eval/record_desktop_stability_smoke.py`
- Added test coverage:
  - `tests/eval/test_record_desktop_stability_smoke.py`
- Appended new stability ledger row for current day:
  - `docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl`
- Gate snapshot now reports:
  - `G1 = pass` (`14/14 day(s) covered, failures=0`).

### Execution pulse 113.2 (G3 no-drift execution cadence)

- Executed one additional G3 no-drift run via:
  - `scripts/eval/freeze_lane_monthly_report.py --record-run --allow-in-progress`
- G3 history now includes a new zero-failure run-day:
  - `docs/collaboration/evidence/G3_CONTRACT_NO_DRIFT_HISTORY.jsonl`
- Snapshot reflects deterministic progress:
  - `G3 = in_progress` (`2/28 day(s), failed=0`).

### Execution pulse 113.3 (gate scoreboard checkpoint)

- Exported explicit gate scoreboard artifact:
  - `docs/collaboration/evidence/GATE_SCOREBOARD_SNAPSHOT.json`
- Current posture after `113.x`:
  - `G1`: pass
  - `G2`: in_progress (PROVISIONAL synthetic evidence)
  - `G3`: in_progress
  - `G4`: pass
  - `G5`: pass
- Successor chain opened as `114.x` for remaining in-progress gates.

### Execution pulse 114.0 (gate closure sprint kickoff)

- Executed full `114.x` sprint in-order under autopilot.
- Scope stayed gate-first and avoided diagnostics-card scope expansion.

### Execution pulse 114.1 (G2 provisional-to-live transition prep)

- Added executable transition guard:
  - `scripts/eval/g2_transition_guard.py`
- Added dedicated coverage:
  - `tests/eval/test_g2_transition_guard.py`
- Generated explicit transition artifact:
  - `docs/collaboration/evidence/G2_TRANSITION_READINESS.json`
- Current transition posture:
  - `status=BLOCKED_HARDWARE` with valid provisional report and explicit unblock checklist.

### Execution pulse 114.2 (G3 cadence reinforcement)

- Extended monthly runner with cadence planning output:
  - `scripts/eval/freeze_lane_monthly_report.py --cadence-output ...`
- Added cadence-plan tests in:
  - `tests/eval/test_freeze_lane_monthly_report.py`
- Generated deterministic cadence artifact:
  - `docs/collaboration/evidence/G3_CADENCE_PLAN.json`
- Current cadence posture:
  - `covered_days=2/28`, `next_run_due_at=2026-05-03T09:00:00Z`, failures remain `0`.

### Execution pulse 114.3 (gate scoreboard checkpoint)

- Refreshed gate scoreboard artifact:
  - `docs/collaboration/evidence/GATE_SCOREBOARD_SNAPSHOT.json`
- Posture remains explicit and auditable:
  - `G1`: pass
  - `G2`: in_progress (PROVISIONAL + transition report `BLOCKED_HARDWARE`)
  - `G3`: in_progress (cadence plan active)
  - `G4`: pass
  - `G5`: pass
- Successor chain opened as `115.x` for daily cadence closure loops.

### Execution pulse 115.0 (daily gate cadence execution loop)

- Executed full `115.x` loop in-order under autopilot.
- Scope stayed gate-first with emphasis on cadence determinism and truthful evidence freshness.

### Execution pulse 115.1 (G3 daily no-drift run append)

- Added idempotent daily runner:
  - `scripts/eval/record_g3_daily_contract_run.py`
- Added dedicated tests:
  - `tests/eval/test_record_g3_daily_contract_run.py`
- Runner behavior now avoids duplicate-day inflation:
  - appends only when current UTC day is missing,
  - returns `skipped_duplicate_day` when an entry already exists.
- Current day posture:
  - today's G3 day was already present, so coverage remained `2/28` (truthful no-overclaim).

### Execution pulse 115.2 (G2 transition freshness refresh)

- Refreshed transition readiness artifact:
  - `docs/collaboration/evidence/G2_TRANSITION_READINESS.json`
- Refreshed cadence artifact:
  - `docs/collaboration/evidence/G3_CADENCE_PLAN.json`
- Current transition posture remains explicit:
  - `G2 status=BLOCKED_HARDWARE`,
  - provisional evidence valid/fresh, live promotion blocked by missing mic/camera path.

### Execution pulse 115.3 (gate scoreboard checkpoint)

- Refreshed scoreboard artifact:
  - `docs/collaboration/evidence/GATE_SCOREBOARD_SNAPSHOT.json`
- Current posture remains:
  - `G1`: pass
  - `G2`: in_progress (blocked by hardware; transition report fresh)
  - `G3`: in_progress (`2/28`, cadence loop active)
  - `G4`: pass
  - `G5`: pass
- Successor chain opened as `116.x` for first next-day coverage gain.

### Execution pulse 116.0 (next-day closure prep loop — tooling)

- Shipped deterministic gate evaluation and hygiene tooling:
  - `evaluate_stability_gate` / `build_gate_snapshot` accept fixed `now` for tests; desktop gate tests use pinned April 2026 UTC for the 14-day G1 window.
  - `record_g3_daily_contract_run.run_g3_daily_contract()` is injectable for skip vs append coverage.
  - `tests/eval/test_g2_transition_guard.py` extended for stale provisional, invalid samples, and `provisional=false`.
  - Contract shape tests lock `G2_TRANSITION_READINESS.json` and `G3_CADENCE_PLAN.json`.
  - `scripts/eval/run_gate_maintenance_checklist.py` documents the operator command chain (`--execute` runs it).
  - `scripts/eval/audit_kernel_ruff_scope.py` matches CI Ruff scope; `pyproject.toml` excludes vendored `llama_cpp` for Ruff/Mypy.
  - CI `quality` job runs `pytest tests/eval/` before the full matrix.
- Operational G3 day-coverage increment (`116.1`) still waits on the next UTC calendar day without a recorded run.

### Execution pulse 117.0 (premium autopilot chain — 20 prompts)

- Added executable premium chain:
  - `scripts/eval/premium_autopilot_20.py`
  - `docs/collaboration/PREMIUM_AUTOPILOT_PROMPTS_20.md`
  - `tests/eval/test_premium_autopilot_20.py`
- Premium chain validates 20 hardening checkpoints (code, tests, CI wiring, docs continuity).
- Evidence artifact emitted by autopilot run:
  - `docs/collaboration/evidence/PREMIUM_AUTOPILOT_20_REPORT.json`
- CI desktop gate report now includes premium autopilot artifact generation:
  - `gate-reports/premium-autopilot-20.json`

### Execution pulse 119.0 (A1 — chat panel in Flutter desktop shell)

- Flutter shell now exposes a real chat surface bound to `/ws/chat`:
  - new `src/clients/flutter_desktop_shell/lib/chat_panel.dart` (WS client, streaming bubbles, bounded retry).
  - `Chat | Diagnostics` segmented selector in `main.dart`, defaulting to Chat.
- Dedicated widget tests added in `test/chat_panel_test.dart`; existing diagnostics tests switch tabs explicitly so legacy coverage is preserved.
- Local validation: `flutter test` → 8 passed; collaboration invariants pass.

### Execution pulse 118.0 (core model audit autopilot — 20 prompts)

- Audited and hardened core model runtime paths in:
  - `src/core/safety.py`
  - `src/core/identity.py`
  - `src/core/status.py`
  - `src/core/sleep.py`
- Main hardening outcomes:
  - bounded exception handling and payload-size guard for encoded safety checks;
  - resilient identity state loading with type coercion and warning logs;
  - status timeout/encoding safeguards for degraded environments;
  - psi-sleep latency telemetry (`last_reflection_ms`) and stats exposure.
- Added regression coverage:
  - `tests/core/test_safety.py`
  - `tests/core/test_identity.py`
  - `tests/core/test_status.py`
  - `tests/core/test_sleep.py`
- Added 20-prompt model audit board + checker:
  - `docs/collaboration/MODEL_AUDIT_PROMPTS_20.md`
  - `scripts/eval/model_audit_runner_20.py`
  - `tests/eval/test_model_audit_runner_20.py`
- Evidence artifact:
  - `docs/collaboration/evidence/MODEL_AUDIT_AUTOPILOT_20_REPORT.json`

## System references

- **Freeze policy and evidence matrix:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`
- **CI gate runner:** `scripts/eval/desktop_gate_runner.py`
- **Primary quality command set:** see `README.md` and `CONTRIBUTING.md`
