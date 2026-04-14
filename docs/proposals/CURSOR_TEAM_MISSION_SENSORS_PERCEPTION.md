# Cursor Team Playbook — Sensors and Perception

**Status:** active collaborative charter for the Cursor line (`cursor-team` and `master-Cursor`) under the multi-office method in [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md).

This playbook defines **analysis, discussion, planning, implementation, integration, and release handoff** for how the kernel ingests and trusts **sensor-derived and LLM-mediated perception**.

## 1) Mission scope

1. **Structured perception:** JSON from `LLMModule.perceive`, schema validation (`perception_schema`), coherence checks (`perception_cross_check`), dual-vote (`perception_dual_vote`), and uncertainty-driven deliberation (`KERNEL_PERCEPTION_UNCERTAINTY_DELIB`).
2. **Input trust and safety gates:** normalization, MalAbs lexical + optional semantic layers, and safeguards for **valid-but-wrong** structured model outputs.
3. **Sensor-facing design track:** align kernel perception with situated-organism goals (sensor fusion, vitality, agency), without claiming hardware implementation until code + tests + docs are merged.

## 2) Out of scope for this team track

- On-chain governance and DAO testnet delivery (`mock_dao.py`, `MOCK_DAO_SIMULATION_LIMITS.md`).
- Direct promotion to `main` without maintainer/release flow.
- Claims of empirical calibration without in-repo evidence artifacts.

## 3) Multi-origin collaborative workflow (operational format)

### Intake sources

Work items may enter from:

- GitHub issues and PR comments.
- Chat directives from maintainers and operators.
- Backlog documents and weakness inventories in `docs/`.
- Local office findings (benchmarks, incident notes, test regressions).

### Intake gate (mandatory before implementation)

For each item, record:

1. **Redundancy check:** confirm not already solved/in progress (`docs/`, issues, open PRs).
2. **Novelty and coverage:** prioritize less-covered model areas unless critical regression.
3. **Track label:** `perception`, `malabs`, `sensor-fusion`, `runtime-policy`, or `docs`.
4. **Risk class:** `critical`, `high`, `normal` (operator-impact oriented).

### Branch and integration flow

1. **Daily collaborative work:** `cursor-team` (or short-lived topic branches from it).
2. **Team integration hub:** merge reviewed work into `master-Cursor`.
3. **Production promotion:** `master-Cursor` -> `main` is maintainer/release action only.

Use this convention for branch names from `cursor-team`:

- `cursor/perception-<topic>`
- `cursor/sensors-<topic>`
- `cursor/malabs-<topic>`
- `cursor/docs-<topic>`

### Meeting cadence (lightweight)

- **Async daily:** update item status (`todo`, `in_progress`, `blocked`, `ready_for_merge`).
- **Weekly integration check:** verify `master-Cursor` is refreshed against `main` policy.
- **Release prep checkpoint:** confirm docs/tests/changelog before promotion request.

## 4) Task board template (copy for each item)

Use this compact format in issue/PR descriptions:

```text
ID:
Source:
Track label:
Risk class:
Redundancy check:
Owner office:
Target branch:
Definition of done:
Evidence links:
```

## 5) Definition of done (sensors/perception)

An item is done only when all apply:

1. Code change merged in `cursor-team` (and integrated in `master-Cursor` when applicable).
2. Tests added/updated for behavior and env overrides.
3. Lint/type/test checks pass (`ruff`, `mypy`, `pytest`).
4. Minimal doc update in `docs/proposals/` (or ADR if decision-level).
5. `CHANGELOG.md` updated when operator behavior/expectations change.

## 6) Primary technical references

| Topic | Document / code |
|--------|-----------------|
| Perception pipeline | [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md), [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py) |
| Input trust + MalAbs | [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md), [`MALABS_SEMANTIC_LAYERS.md`](MALABS_SEMANTIC_LAYERS.md), [`PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md`](PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md) |
| Known perception gap | [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) (Section 3: unified degradation policy gap) |
| Situated model theory | [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md) |
| Contribution guardrails | [`CONTRIBUTING.md`](../../CONTRIBUTING.md), [`AGENTS.md`](../../AGENTS.md) |

## 7) Documentation and language policy reminders

- Day-to-day human collaboration can be in Spanish.
- Repository-facing artifacts merged to git must be English (except explicit fixture/security exceptions).
- Safety-critical defaults require the full pattern: named constants, tests, honest docs, and changelog traceability.
