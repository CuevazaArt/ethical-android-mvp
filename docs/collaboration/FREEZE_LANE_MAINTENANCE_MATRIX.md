# Freeze-Lane Maintenance Matrix (Web/Mobile)

Purpose: keep frozen platforms healthy (smoke + security) without opening new feature work.

## Scope

- Platforms: `web` (dashboard/browser lane), `mobile` (Nomad lane).
- Cadence: monthly.
- Allowed work: security patches, dependency hygiene, smoke checks, contract no-drift checks.
- Forbidden work: net-new features, UX expansion, business-logic divergence from desktop contracts.

## Monthly Matrix

| Month | Web smoke | Mobile smoke | Security patch review | Desktop contract no-drift | Freeze status |
|---|---|---|---|---|---|
| 2026-05 | TODO | TODO | TODO | TODO | PENDING |
| 2026-06 | TODO | TODO | TODO | TODO | PENDING |
| 2026-07 | TODO | TODO | TODO | TODO | PENDING |

## Smoke Definition (Minimal)

### Web lane
- `GET /api/ping` returns `{"pong": true}`.
- `GET /api/status` returns `status=online` and finite uptime.
- No browser runtime crash on dashboard initial load.

### Mobile lane
- Nomad websocket opens and replies to ping/pong.
- One typed `chat_text` frame returns a terminal `done` event.
- No fatal bridge error in the first interaction cycle.

## No-Drift Rule (Contract Spine)

Frozen lanes must keep the desktop envelope unchanged:
- required keys: `version`, `contract`, `request`, `response`, `error`, `latency_ms`
- `version` must remain `1.0` until a versioned migration is formally approved
- `contract` must remain one of: `audio_perception`, `video_perception`, `voice_turn`

## Freeze Healthy Criterion

A freeze lane is **HEALTHY** for a month only if all are true:
- Web smoke: PASS
- Mobile smoke: PASS
- Security patch review: PASS
- Desktop contract no-drift check: PASS
- No net-new feature merged in frozen lane paths

If any check fails, status is **DEGRADED** and only remediation work is allowed.

## Gate Audit Proofpack (50.7B)

| Gate | What is required | Source of truth | Current status |
|---|---|---|---|
| G1 Stability | 14 consecutive days without critical desktop crash in smoke cycle | `docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl` + `python scripts/eval/desktop_gate_runner.py stability --ledger docs/collaboration/evidence/DESKTOP_STABILITY_LEDGER.jsonl --days 14` | PASS (51.0 automation) |
| G2 Voice latency | p95 full voice turn < 2500 ms on target desktop profile | `docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl` + `python scripts/eval/desktop_gate_runner.py latency --samples docs/collaboration/evidence/VOICE_TURN_LATENCY_SAMPLES.jsonl --target-p95-ms 2500` | PASS (51.1 benchmark harness) |
| G3 Contract discipline | 0 schema drift findings for one full month | `pytest tests/test_freeze_lane_guardrails.py -q` + monthly matrix | IN PROGRESS (checks green) |
| G4 Demo reliability | 10/10 scripted demos passing (audio/video/voice) | `docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json` + `python scripts/eval/desktop_gate_runner.py demo --checklist docs/collaboration/evidence/DEMO_RELIABILITY_CHECKLIST.json --required-count 10` | PASS (51.2 checklist runner) |
| G5 Ops readiness | Reproducible packaging + rollback checklist validated | `scripts/build_windows_desktop_release.ps1`, `ARTIFACTS.txt`, `ROLLBACK_CHECKLIST.txt` | PASS (2026-04-30 local build) |

### Decision policy

Reopen mobile/web feature work only when **all gates are PASS** in the same review cycle.
