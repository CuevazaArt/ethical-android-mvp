# experiments/out/field/ — field test session outputs

This directory holds **per-session artefacts** from field test phases F0–F4
(see `docs/proposals/PROPOSAL_FIELD_TEST_PLAN.md`).

## Layout

```
out/field/
├── F0_<YYYY-MM-DD>/          ← bench baseline (golden trace)
│   ├── manifest.json
│   └── decisions.jsonl
├── F1_<YYYY-MM-DD>/          ← LAN smoke (phone client stub)
├── F2_<YYYY-MM-DD>/          ← live sensor (phone hand-held)
├── F3_<YYYY-MM-DD>/          ← DAO rehearsal
└── F4_<YYYY-MM-DD>/
    └── fixtures/             ← replayable regression traces
```

## Retention policy

Raw `.jsonl` files and `manifest.json` are **gitignored** (see `.gitignore`).
Commit only anonymised fixtures explicitly moved to `F4_*/fixtures/`.

## Creating a baseline (F0)

```bash
KERNEL_ENV_VALIDATION=warn \
KERNEL_SENSOR_PRESET=quiet_indoor \
python scripts/run_empirical_pilot.py \
  --output experiments/out/field/F0_$(date +%Y-%m-%d)/decisions.jsonl
```

See `PROPOSAL_FIELD_TEST_PLAN.md §4 Phase F0` for full instructions.
