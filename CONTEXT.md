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

## System references

- **Freeze policy and evidence matrix:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`
- **CI gate runner:** `scripts/eval/desktop_gate_runner.py`
- **Primary quality command set:** see `README.md` and `CONTRIBUTING.md`
