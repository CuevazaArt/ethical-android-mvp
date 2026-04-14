# PROPOSAL — DAO / blockchain / distributed justice staged execution

## Status

Draft execution proposal for cross-team evaluation while `master-claude` finalizes its current delivery.

## Why this proposal now

The repository already contains governance and distributed-justice building blocks:

- `MockDAO` voting/audit paths (`src/modules/mock_dao.py`)
- judicial escalation and dossier flow (`src/modules/judicial_escalation.py`)
- local sovereignty and deontic checks (`src/modules/local_sovereignty.py`, `src/modules/deontic_gate.py`)
- transparency and integrity audit events (`src/modules/hub_audit.py`, `src/modules/moral_hub.py`)

What remains is **execution ordering**: how to move from mock governance to distributed coordination without over-claiming chain guarantees.

## Scope and non-goals

### In scope

- execution plan (phased)
- operator-visible contracts and acceptance criteria
- evidence posture and rollback boundaries

### Out of scope

- claiming production on-chain consensus in the current branch
- replacing L0 (`PreloadedBuffer`) with DAO votes
- introducing irreversible blockchain dependencies without staged tests and fallback

## Core principles

1. **L0 remains non-negotiable** — distributed justice augments process and audit, not core ethical invariants.
2. **Off-chain first, explicit honesty** — use deterministic off-chain coordination before any chain bridge.
3. **Replayable evidence** — every phase must produce machine-checkable artifacts.
4. **Operator fallback path** — each new distributed step needs a local safe mode.

## Staged plan

## Phase 0 — Cross-team contract freeze (immediate)

Objective: lock interoperable payload contracts while teams finish parallel work.

Deliverables:

- freeze JSON keys for:
  - `judicial_escalation`
  - `integrity` / DAO audit actions
  - `temporal_sync` (`temporal_sync_v1`)
- cross-team integration gate run on `master-*` branches before interlacing

Acceptance:

- targeted tests pass on each team branch
- no unannounced contract key removals

## Phase 1 — Deterministic off-chain justice ledger

Objective: harden distributed justice without chain dependency.

Deliverables:

- append-only off-chain event stream for escalation and DAO actions
- deterministic event ordering using `temporal_sync` fields (`turn_index`, deltas)
- replay checker proving identical state reconstruction from logs

Acceptance:

- replay test reproduces final governance state
- mismatch detection emits explicit operator diagnostics

## Phase 2 — Local-network distributed coordination

Objective: synchronize multiple local nodes safely (LAN first).

Deliverables:

- local coordinator protocol (schema-versioned envelopes)
- idempotent event handling (duplicate-safe)
- conflict resolution policy (`same_turn`, `different_clock`, `stale_event`)

Acceptance:

- stress test with reordered/duplicated events
- no divergence in reconstructed DAO/judicial state

## Phase 3 — Optional blockchain anchoring (checkpoint, not authority)

Objective: anchor audit checkpoints on chain without moving ethical authority on-chain.

Deliverables:

- periodic hash commitments of off-chain justice ledger
- verification utility: local ledger -> hash -> on-chain anchor comparison
- explicit docs: chain anchor is integrity witness, not policy executor

Acceptance:

- successful anchor verification on test network
- clear operator runbook for anchor failures and offline fallback

## Phase 4 — Governance hardening and review board

Objective: formal cross-team operating model for distributed justice releases.

Deliverables:

- release checklist requiring:
  - contract compatibility report
  - replay verification report
  - security/threat review summary
- minimum reviewer policy: at least one reviewer from another `master-*` team line

Acceptance:

- release candidate passes full integration gate and review checklist

## Concrete examples

## Example A — Escalation dossier across nodes

Scenario:

- node A creates judicial dossier event at `turn_index=42`
- node B receives it late but with same event id and higher wall-clock delta

Expected behavior:

- idempotent merge keeps one dossier record
- audit stream retains both receive timestamps
- reconciliation report marks "late arrival, no state divergence"

## Example B — DAO integrity alert in degraded network

Scenario:

- LAN sync disabled by operator (`KERNEL_TEMPORAL_LAN_SYNC=0`)
- DAO sync remains enabled (`KERNEL_TEMPORAL_DAO_SYNC=1`)

Expected behavior:

- chat JSON shows `temporal_sync.local_network_sync_ready=false`
- DAO-side audit events continue locally
- no hidden retry loops pretending LAN dissemination happened

## Example C — Optional blockchain anchor mismatch

Scenario:

- off-chain replay hash differs from expected on-chain anchor

Expected behavior:

- system marks anchor mismatch as integrity warning
- no automatic policy mutation
- operators receive deterministic replay diff artifact for investigation

## Pending gaps to close while waiting for other teams

1. Add replay-state checker script for governance events.
2. Add LAN duplicate/reorder simulation tests for DAO+judicial payloads.
3. Add one operator runbook page for "sync degraded but safe-local mode."
4. Add contract compatibility matrix between `master-Cursor`, `master-claude`, and `master-antigravity`.

## Traceability

- governance baseline: [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md)
- distributed justice baseline: [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md)
- DAO limits: [MOCK_DAO_SIMULATION_LIMITS.md](MOCK_DAO_SIMULATION_LIMITS.md)
- integration gate: [`../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md`](../collaboration/CURSOR_CROSS_TEAM_INTEGRATION_GATE.md)
