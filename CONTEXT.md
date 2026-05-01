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
- **Immediate objective:** align public docs with runtime reality and remove non-source artifacts from `main`.
- **Validation basis:** CI + local reproducible checks; no manual “green” claims in docs.

## System references

- **Freeze policy and evidence matrix:** `docs/collaboration/FREEZE_LANE_MAINTENANCE_MATRIX.md`
- **CI gate runner:** `scripts/eval/desktop_gate_runner.py`
- **Primary quality command set:** see `README.md` and `CONTRIBUTING.md`
