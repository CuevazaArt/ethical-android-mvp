# PROPOSAL — Field Test Plan: Model, Next DAO, and Physical Sensors

**Status:** Draft  
**Date:** 2026-04-14  
**Scope:** Ethos Kernel ethical core (scorer + MalAbs + poles), next-iteration DAO
(governance UX + audit sidecar), and **real** physical sensors via a smartphone
relay, with a minimal PC ↔ phone management interface.  
**Related:** [ADR 0017 — Smartphone sensor relay bridge](../adr/0017-smartphone-sensor-relay-bridge.md),
[`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md),
[`ROADMAP_PRACTICAL_PHASES.md`](../ROADMAP_PRACTICAL_PHASES.md),
[`src/modules/sensor_contracts.py`](../../src/modules/sensor_contracts.py),
[`src/modules/hardware_abstraction.py`](../../src/modules/hardware_abstraction.py),
[`src/modules/mock_dao.py`](../../src/modules/mock_dao.py),
[`src/chat_server.py`](../../src/chat_server.py).

> **Language policy:** English per [`CONTRIBUTING.md`](../../CONTRIBUTING.md). This
> document is a **plan**, not a deployment commitment.

---

## 1. Purpose

The kernel has been validated under **synthetic** inputs: batch simulations
(`src/main.py`), chat fixtures, and scripted sensor fixtures
(`KERNEL_SENSOR_FIXTURE`). Several open weaknesses (`WEAKNESSES_AND_BOTTLENECKS.md`
§3, §4, §5, §7) cannot be closed with synthetic data alone:

- Perception dual-vote disagreement rates against **real** ambient audio/motion.
- MockDAO UX and audit sidecar behavior under **real** multi-participant load.
- Whether pole weights and multimodal thresholds (`KERNEL_MULTIMODAL_*`) remain
  calibrated once jerk, noise, silence, and biometric anomaly come from a live
  handset instead of curated presets.

This plan frames a **small, reversible, instrumented field test** that moves the
kernel from desk-bench to a living PC + smartphone pair without overclaiming.

## 2. Out-of-scope (explicit)

- On-chain DAO. The **next DAO** here means the natural evolution of
  `MockDAO` + `KERNEL_AUDIT_SIDECAR_PATH` (`mock_dao.py`, governance docs),
  not a Solidity deployment. See `WEAKNESSES_AND_BOTTLENECKS.md` §4.
- Any claim of Bayesian posterior calibration beyond ADR 0012 / ADR 0013.
- Medical, safety-critical, or legal deployment. The field test is a
  **laboratory** exercise with informed operators.
- Android app store distribution. The phone role is a **sensor/UI relay**
  attached over LAN to a PC running the kernel.

## 3. System under test

```
┌──────────────────────────────────────────────────────┐
│ PC (operator console)                                │
│  ┌───────────────────────────────────────────────┐   │
│  │ EthicalKernel + RealTimeBridge (chat_server)  │   │
│  │  · weighted_ethics_scorer                     │   │
│  │  · MalAbs / deontic_gate / poles              │   │
│  │  · MockDAO (audit sidecar on disk)            │   │
│  │  · perception_dual_vote (optional)            │   │
│  └───────────────────────────────────────────────┘   │
│         ▲ WebSocket /ws/chat (LAN)                   │
│         │                                            │
│         │                             HTTP /control  │
│         │                             (new, minimal) │
└─────────┼────────────────────────────────────────────┘
          │
          │  LAN (Wi-Fi, private)
          ▼
┌──────────────────────────────────────────────────────┐
│ Smartphone — sensor + UI relay (PWA / webview)       │
│  · battery, accelerometer, ambient mic level,        │
│    silence, optional camera hint, GPS coarse         │
│  · minimal control UI (start/stop session,           │
│    mark "trusted place", attach operator note)       │
│  · no kernel logic runs here                         │
└──────────────────────────────────────────────────────┘
```

**Design constraint:** the phone is a **dumb sensor + UI relay**. It never
hosts the ethical core. "Jumping" from PC to phone means the PC-hosted kernel
starts accepting a new `sensor` stream from the phone client while the operator
UI is mirrored through the phone (a single shared session, authenticated by
pairing token).

Rationale (`hardware_abstraction.py`): `ComputeTier.EDGE_MOBILE` is documented
but not the target for this test — the kernel stays on the PC tier so LLM and
decision latency remain reproducible.

## 4. Phases

### Phase F0 — Bench baseline (PC only, no phone)

**Goal:** lock a reproducible baseline before adding physical-world noise.

- Run `scripts/run_empirical_pilot.py` and `tests/test_decision_core_invariants.py`
  on the target host. Record: Python version, commit hash, profile
  (`ETHOS_RUNTIME_PROFILE`), thresholds (`KERNEL_MULTIMODAL_*`,
  `KERNEL_PERCEPTION_UNCERTAINTY_DELIB`).
- Export a **golden decision trace** for ≥ 50 scripted turns using
  `KERNEL_SENSOR_FIXTURE` against a fixed preset.
- Archive MockDAO audit sidecar (`KERNEL_AUDIT_SIDECAR_PATH`).

**Exit criteria:** all invariants green; golden trace committed under
`experiments/out/field/F0_<date>/`.

### Phase F1 — Local PC + LAN smoke (phone client stub)

**Goal:** confirm LAN transport and minimal control surface before trusting
real sensors.

- Start kernel with `scripts/start_lan_server.(ps1|sh)` bound to the LAN
  interface (explicit bind, not 0.0.0.0 on public networks).
- Phone opens the PWA/webview, pairs with the PC using a **one-time pairing
  token** printed in the console.
- Phone posts a **deterministic** `sensor` stream every 1 s (fixed JSON).
  Kernel must:
  - Accept the stream on the existing `sensor` field of `/ws/chat`.
  - Emit a `session_paired` audit line in the sidecar.
  - Expose a new minimal `/control` surface (ADR 0017 §6) for `status`,
    `pause`, `resume`, `end_session`.

**Exit criteria:** round-trip latency p95 < 200 ms on LAN; zero divergence
between Phase F0 and F1 decisions when the phone stream replays the fixture.

### Phase F2 — Live sensor field test (phone hand-held by operator)

**Goal:** first contact with reality. Single operator, single phone, single PC.
Duration: ≤ 60 minutes per session; ≤ 3 sessions.

- Scenarios (scripted, reversible, non-risky):
  1. **Quiet-room baseline** — low noise, phone on desk.
  2. **Motion event** — operator walks, phone in hand.
  3. **Ambient audio spike** — deliberate loud sound (clap, kitchen).
  4. **Trust-flip** — operator toggles "trusted place" from UI.
  5. **Battery drain** — phone falls below `KERNEL_VITALITY_CRITICAL_BATTERY`.
- For each scenario record:
  - `final_action` and `chosen_action_source`.
  - `perception_dual_vote` disagreement (if enabled).
  - Multimodal trust distrust channels (`multimodal_trust.py`).
  - Vitality + Guardian signals (`vitality.py`, `guardian_mode.py`).
  - Audit sidecar tail (for DAO slice — see §5).

**Exit criteria:** no unhandled exceptions, no kernel restarts, all decisions
stay within the declared policy envelope (MalAbs never bypassed).

### Phase F3 — Next-DAO rehearsal (multi-participant mock)

**Goal:** exercise the **governance UX** that will plug into the kernel next,
without making any distributed-consensus claim.

- Seed `MockDAO` with ≥ 3 `Participant` rows (human operators on the PC).
- Use the existing `dao_vote` / `dao_resolve` / `dao_submit_draft` /
  `dao_list` WebSocket messages (`chat_server.py`, `KERNEL_MORAL_HUB_DAO_VOTE`).
- From the phone: allow the operator to **author a draft** and **cast a vote**
  through the minimal control UI (no new transport, reuse `/ws/chat` with a
  session tag indicating DAO intent).
- Mirror all governance events into `KERNEL_AUDIT_SIDECAR_PATH` with tight
  permissions; diff the sidecar against the in-process `MockDAO` ledger at
  end-of-session.

**Exit criteria:** sidecar ↔ in-memory ledger match; audit lines are
append-only; no DAO vote altered `final_action` in this phase (explicit
invariant — see `MOCK_DAO_SIMULATION_LIMITS.md`).

### Phase F4 — Findings, calibration, regression capture

- Convert each surprising trace into a **replayable fixture** under
  `experiments/out/field/F4_<date>/fixtures/` so it can feed future CI.
- Open issues for each calibration gap (pole weights, multimodal thresholds,
  perception dual-vote disagreement distribution).
- Re-run F0 golden trace to verify no regression after instrumentation changes.

## 5. Instrumentation

- **Prometheus** (`KERNEL_METRICS=1`) must be on for F1–F3; scrape into a
  local file-backed store (not a shared cluster).
- **JSON logs** (`KERNEL_LOG_JSON=1`) capture per-turn structured evidence.
- **Audit sidecar** (`KERNEL_AUDIT_SIDECAR_PATH`) is **mandatory** for F3; the
  file is rotated per session.
- **Session manifest** — a single JSON written by the PC at session end:
  commit hash, profile, env overrides, phone build id, scenario log, file
  hashes of all outputs. Stored under `experiments/out/field/<phase>_<date>/`.

No biometric or raw audio is persisted beyond the per-turn summary features
already declared by `SensorSnapshot` (see `sensor_contracts.py`). Cameras,
if ever enabled, emit only the `vision_emergency` scalar, never frames.

## 6. PC ↔ smartphone minimal management interface

This is the **only** new surface introduced by the field test. It is designed
to be the smallest thing that works; details in [ADR 0017](../adr/0017-smartphone-sensor-relay-bridge.md).

- **Transport.** Reuse the existing `/ws/chat` WebSocket for sensor frames
  and DAO messages; add a small **HTTP `/control`** surface for pairing,
  status, pause/resume/end-session, and fetching the session manifest.
- **Pairing.** One-time token printed on the PC console; the phone posts the
  token to `/control/pair` and receives a short-lived session credential.
- **Phone client.** A **PWA** (HTML + vanilla JS) served by the PC on the
  same port — no app-store distribution, no native build. The phone opens
  `http://<lan-ip>:8765/phone` and pins the pairing token into `localStorage`.
- **UI (phone).** Four buttons: *Start*, *Pause*, *End*, *Trusted place*
  (toggle). A live tile shows battery, jerk, noise, silence, and latest
  `final_action` echoed back from the PC.
- **UI (PC).** A terminal-first operator log plus the existing Grafana board
  (`deploy/grafana/ethos-kernel-overview.json`). No new desktop app.
- **Security.** LAN-only by default; explicit bind address; reject connections
  without a valid session credential; operators must treat the pairing token
  as a secret. HTTPS is **not** required for F1–F3 lab use, but the manifest
  must record whether TLS was in play.

## 7. Closing the most critical gaps

The field test is scoped to move five specific gaps from `WEAKNESSES_AND_BOTTLENECKS.md`
out of "synthetic only" status. Each gap gets **one** concrete acceptance signal
from the plan, nothing more.

| Weakness | Field-test acceptance signal |
|----------|------------------------------|
| §3 Local inference failure modes | F2 records at least one induced LLM timeout with correct `chat_turn_timeout` JSON and no session crash. |
| §4 MockDAO simulation limits | F3 sidecar ↔ ledger diff is empty; DAO votes never moved `final_action`. |
| §6 Pole weights heuristic | F4 produces a calibration issue with a fixture, **not** a silent tweak of defaults. |
| §7 Peripheral complexity / no ablation | F2 captures at least three real traces reusable by a future ablation run. |
| §8 Psi Sleep independence | Out of scope for this plan — flagged so operators do not conflate. |

Gaps the field test **does not** close (and must not claim to): §1 (true async
kernel), §2 (Bayesian naming), §5 (external moral benchmark).

## 8. Safety, consent, and reversibility

- **Informed operators only.** No bystanders provide sensor data. The phone
  UI shows a persistent "Field test — recording sensor summaries" banner
  while a session is active.
- **Stop switch.** *End* on phone and `end_session` on `/control` both
  tear down the WebSocket and flush the session manifest.
- **Data retention.** Per-session data stays under `experiments/out/field/`
  and is purged after the calibration issue is filed. No network upload.
- **Rollback.** All field-test code lives behind environment flags
  (`KERNEL_FIELD_CONTROL=1`, `KERNEL_FIELD_PAIRING_TOKEN=…`). Setting them to
  `0` restores pre-field behavior exactly.

## 9. Deliverables

- This proposal and [ADR 0017](../adr/0017-smartphone-sensor-relay-bridge.md).
- Session manifests for F0–F3 under `experiments/out/field/` (not committed
  unless anonymized).
- One issue per calibration finding in F4.
- A tag `field-test-plan-v1-2026-04-14` marking the plan baseline.

## 10. Non-goals

- No fine-tuning or RLHF is triggered by field data — see Phase 3 of the
  roadmap; that needs its own proposal.
- No change to `final_action` provenance. DAO votes remain advisory.
- No production deployment artifact emerges from this plan. The outcome is
  **evidence**, not a release.

## 11. Open questions

1. Should the phone PWA be served by a separate static sidecar, or inline by
   `chat_server`? Default in ADR 0017: inline, behind a feature flag.
2. How to bound sensor frame rate on the PC side so a misbehaving phone does
   not saturate the chat thread pool? Proposal: token-bucket in
   `RealTimeBridge` gated on `KERNEL_FIELD_SENSOR_HZ`.
3. Do we need a **second** phone to rehearse multi-participant DAO in F3, or
   is the PC console sufficient as a second voice? Default: PC is enough for
   v1; second phone is a Phase-2 extension.

## 12. Readiness gate — first smartphone integration (F1)

**Purpose:** Align operators and developers on what is **ready now** vs what **waits** on the first physical handset session on a private LAN.

| Layer | Status | Notes |
|-------|--------|--------|
| PC kernel + chat server | Ready | Run F0 baseline (`scripts/run_empirical_pilot.py`, golden traces per §4 F0). |
| Phone relay PWA (`GET /phone`) | Ready behind flag | Set `KERNEL_FIELD_CONTROL=1` and a non-empty `KERNEL_FIELD_PAIRING_TOKEN` ([ADR 0017](../adr/0017-smartphone-sensor-relay-bridge.md), [`docs/ADR_0017_IMPLEMENTATION.md`](../ADR_0017_IMPLEMENTATION.md)). |
| `/control/*` pairing | Ready | Same flag; LAN-only unless `KERNEL_FIELD_ALLOW_WAN=1` (lab only). |
| Real-world F1 session | **Waiting** | Requires scheduling: phone + PC on same Wi-Fi, stable bind address, operator follows [`docs/REPOSITORY_PERMISSIONS_CHECKLIST.md`](../REPOSITORY_PERMISSIONS_CHECKLIST.md) field-test steps. |
| Sensor APIs on handset | Variable | Browsers may withhold motion/mic on **non-HTTPS LAN IPs**; UI degrades to null fields (ADR 0017 consequences). Not a kernel bug. |
| Thread-pool rate limit | Pending | Token-bucket in `RealTimeBridge` not yet landed (§11 Q2); `KERNEL_FIELD_SENSOR_HZ` documents intent. |

**Cursor team posture:** Do **not** block on charm/presentation-layer work for F1; prioritize transport, pairing, and trace capture. First integration milestone is **F1 LAN smoke** with a real phone, then F2 live sensors.
