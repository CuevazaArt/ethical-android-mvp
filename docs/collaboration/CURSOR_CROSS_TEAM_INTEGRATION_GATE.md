# Cursor cross-team integration gate

This checklist defines when `master-Cursor` is ready to be interlaced with other team branches (`master-*`) before a maintainer decides promotion to `main`.

## Goal

- Keep cross-team merges predictable.
- Catch contract drift early (especially chat JSON fields used by operators and other teams).
- Ensure perception/limbic increments remain traceable and test-backed.

## Required gate (must pass)

1. **Branch hygiene**
   - `master-Cursor` is pushed and clean (`git status` has no pending changes).
   - Integration commits are traceable in `CHANGELOG.md`.

2. **Contract stability**
   - WebSocket payload still includes:
     - `support_buffer`
     - `limbic_perception`
     - `perception_confidence`
     - `temporal_context`
     - `temporal_sync`
   - `temporal_sync.sync_schema` is stable (`temporal_sync_v1`) unless migration is explicitly announced.

3. **Perception/limbic confidence posture**
   - `perception_confidence.band` and `score` remain present in JSON.
   - `perception_observability` mirrors confidence (`confidence_band`, `confidence_score`).

4. **Temporal sync readiness**
   - `turn_index`, `processor_elapsed_ms`, and `turn_delta_ms` are present.
   - Those three integer fields are **coerced** to non-negative ints in the WebSocket builder when values are missing or non-numeric (JSON stability only; not a policy change).
   - DAO/LAN toggles (`KERNEL_TEMPORAL_DAO_SYNC`, `KERNEL_TEMPORAL_LAN_SYNC`) behave as documented.

5. **Regression suite**
   - Targeted tests pass (see `scripts/eval/run_cursor_integration_gate.py`):
     - `tests/test_chat_server.py`
     - `tests/test_chat_turn.py`
     - `tests/test_temporal_planning.py`
     - `tests/test_perception_confidence.py`
     - `tests/test_process_natural_verbal_observability.py`
     - `tests/test_perception_dual_vote_failure.py`
     - `tests/test_semantic_chat_gate.py`

6. **Operator docs**
   - `KERNEL_ENV_POLICY.md` and `OPERATOR_QUICK_REF.md` include any new `KERNEL_*` knobs and payload contract changes.

## Reproducible gate command

From repository root:

```bash
python scripts/eval/run_cursor_integration_gate.py
```

Optional — focused LLM vertical regressions ([`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](../proposals/PROPOSAL_LLM_VERTICAL_ROADMAP.md)):

```bash
python scripts/eval/run_llm_vertical_tests.py -q
```

Optional flags:

- `--strict` (fails if git tree is dirty)
- `--json` (machine-readable summary)

## Interlace recommendation

If all gate checks pass:

1. Open cross-team integration PR from `master-Cursor` into the selected team integration branch.
2. Require at least one reviewer from another team (`master-*` owner).
3. Keep rebase-to-`main` as maintainer-only action after cross-team signoff.
