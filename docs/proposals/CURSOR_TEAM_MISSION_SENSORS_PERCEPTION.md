# Cursor Team Playbook — Sensors and Perception

**Status:** active collaborative charter for the Cursor line (**`master-Cursor`** is the integration hub; the branch name `cursor-team` is **deprecated**) under the multi-office method in [`MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md).

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

1. **Daily collaborative work:** short-lived **topic branches from `master-Cursor`** (the historical `cursor-team` line is deprecated).
2. **Team integration hub:** merge reviewed work into `master-Cursor`.
3. **Production promotion:** `master-Cursor` -> `main` is maintainer/release action only.

Use this convention for branch names from `master-Cursor`:

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

1. Code change merged in `master-Cursor` (via PR or direct merge per team policy).
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
| LLM touchpoint env precedence | [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md), [`src/modules/llm_touchpoint_policies.py`](../../src/modules/llm_touchpoint_policies.py) |
| Situated model theory | [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md) |
| Contribution guardrails | [`CONTRIBUTING.md`](../../CONTRIBUTING.md), [`AGENTS.md`](../../AGENTS.md) |

## 7) Documentation and language policy reminders

- Day-to-day human collaboration can be in Spanish.
- Repository-facing artifacts merged to git must be English (except explicit fixture/security exceptions).
- Safety-critical defaults require the full pattern: named constants, tests, honest docs, and changelog traceability.

### Mandatory resource check (all offices)

Before starting any new item, review and circulate:

- [`docs/collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md`](../collaboration/COLLABORATIVE_METHOD_GENERALIZATION_GUIDE.md)
- [`docs/collaboration/MULTI_OFFICE_GIT_WORKFLOW.md`](../collaboration/MULTI_OFFICE_GIT_WORKFLOW.md)
- [`CONTRIBUTING.md`](../../CONTRIBUTING.md)
- [`AGENTS.md`](../../AGENTS.md)

## 8) Initial execution backlog (P0/P1)

The table below is the active starter queue for **`master-Cursor`** work.

### P0 (immediate, operator-facing risk)

#### SP-P0-01 — Unified degradation policy for perception health *(landed — extend to all LLM touchpoints)*

- **Source:** `WEAKNESSES_AND_BOTTLENECKS.md` Section 3 (explicit gap).
- **Delivered (perception path):** [`PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md`](PROPOSAL_PERCEPTION_BACKEND_DEGRADATION_POLICY.md), ``KERNEL_PERCEPTION_BACKEND_POLICY``, [`tests/test_perception_backend_policy.py`](../../tests/test_perception_backend_policy.py). **Remaining:** same operator-visible pattern for communicate / narrative / optional monologue when maintainers scope it.
- **Track label:** `runtime-policy`
- **Risk class:** `critical`
- **Owner office:** Cursor (shared)
- **Target branch:** `cursor/perception-backend-degradation-policy`
- **Implementation target:**
  - Define a single operator-visible policy for perception backend failures (slow host, repeated LLM errors, semantically invalid but schema-valid outputs).
  - Include explicit modes: `fast_fail`, `template_mode`, and `session_banner` semantics.
  - Wire policy docs to runtime behavior references.
- **Evidence links (start):**
  - [`perception_circuit.py`](../../src/modules/perception_circuit.py)
  - [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md)
  - [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md)

#### SP-P0-02 — Perception coercion and uncertainty observability contract *(landed baseline)*

- **Source:** chat/operator visibility requirement.
- **Delivered (baseline):** stable chat JSON contract for `perception.coercion_report` + `perception_observability` in [`src/chat_server.py`](../../src/chat_server.py), with tests in [`tests/test_perception_observability_contract.py`](../../tests/test_perception_observability_contract.py). Extend as needed for future dashboard schemas.
- **Track label:** `perception`
- **Risk class:** `high`
- **Owner office:** Cursor (shared)
- **Target branch:** `cursor/perception-observability-contract`
- **Implementation target:**
  - Standardize what operators can reliably inspect per turn (`coercion_report`, uncertainty, dual-vote disagreement markers, circuit state).
  - Ensure docs and tests define the contract as stable (or explicitly experimental).
- **Evidence links (start):**
  - [`test_perception_coercion_report.py`](../../tests/test_perception_coercion_report.py)
  - [`test_perception_uncertainty_delib.py`](../../tests/test_perception_uncertainty_delib.py)
  - [`OPERATOR_QUICK_REF.md`](OPERATOR_QUICK_REF.md)

#### SP-P0-03 — Regression suite for valid-but-wrong perception payloads *(landed baseline)*

- **Source:** input trust threat model.
- **Delivered (baseline):** [`tests/test_perception_valid_wrong_payloads.py`](../../tests/test_perception_valid_wrong_payloads.py) locks coherence nudges, context fallback uncertainty, and fail-safe triggers for type-garbage payloads (alongside existing fuzz and cross-check tests).
- **Track label:** `perception`
- **Risk class:** `high`
- **Owner office:** Cursor (shared)
- **Target branch:** `cursor/perception-valid-wrong-regressions`
- **Implementation target:**
  - Expand fixtures as new coherence or distrust rules land; keep parity with `validate_perception_dict` / `perception_from_llm_json`.
- **Evidence links (start):**
  - [`test_perception_schema_fuzz.py`](../../tests/test_perception_schema_fuzz.py)
  - [`test_perception_cross_check.py`](../../tests/test_perception_cross_check.py)
  - [`INPUT_TRUST_THREAT_MODEL.md`](INPUT_TRUST_THREAT_MODEL.md)

### P1 (next increment, architecture readiness)

#### SP-P1-01 — Sensor adapter contract (pre-hardware integration seam)

- **Source:** pending module “Hardware integration” in `CONTRIBUTING.md`.
- **Track label:** `sensor-fusion`
- **Risk class:** `normal`
- **Owner office:** Cursor (design + implementation)
- **Target branch:** `cursor/sensors-adapter-contract`
- **Implementation target:**
  - Define the minimal sensor adapter interface needed by perception without coupling to one transport/vendor.
  - Add deterministic test doubles for local CI usage.
- **Evidence links (start):**
  - [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md)
  - [`src/modules/llm_layer.py`](../../src/modules/llm_layer.py)
  - [`tests/`](../../tests/)

#### SP-P1-02 — Sensor fusion input normalization profile

- **Source:** situated model + perception consistency requirements.
- **Track label:** `sensor-fusion`
- **Risk class:** `normal`
- **Owner office:** Cursor (design first)
- **Target branch:** `cursor/sensors-fusion-normalization`
- **Implementation target:**
  - Specify canonical normalization for incoming sensor signals before they influence perception/risk signals.
  - Document failure handling and fallback posture for missing/noisy sensors.
- **Evidence links (start):**
  - [`PROPOSAL_SITUATED_ORGANISM_V8.md`](PROPOSAL_SITUATED_ORGANISM_V8.md)
  - [`PERCEPTION_VALIDATION.md`](PERCEPTION_VALIDATION.md)
  - [`KERNEL_ENV_POLICY.md`](KERNEL_ENV_POLICY.md)

#### SP-P1-03 — Perception-stage responsibility split + optional multicore parallelism *(landed baseline)*

- **Source:** Cursor architecture review (latency/coupling in `process_chat_turn`).
- **Delivered (baseline):** `EthicalKernel` now isolates independent text pre-enrichment and sensor-side assessments into dedicated helpers shared across text entrypoints (`process_chat_turn`, `process_natural`), with opt-in parallel execution via `KERNEL_PERCEPTION_PARALLEL` and `KERNEL_PERCEPTION_PARALLEL_WORKERS`.
- **Support buffer extension:** shared perception stage emits a local `support_buffer` snapshot (PreloadedBuffer principles + metaplan strategy hint, `offline_ready=true`) so perception/planning grounding is available even without network access.
- **Limbic-perception extension:** shared stage now derives a compact limbic profile (`arousal_band`, threat/regulation loads, planning bias, multimodal mismatch, vitality critical) and uses it to prioritize support-buffer principles (`safety_first` / `balanced` / `planning_first`).
- **Temporal directive extension:** shared perception stage now derives a local `TemporalContext` (processor-time ascent, human wall-clock, battery horizon, delta-time turn budget, known-task ETA heuristics such as transport) and emits `temporal_sync` readiness flags for DAO/local-network synchronization.
- **Confidence envelope extension:** shared stage emits `perception_confidence` (score/band/reasons) so planning bias and operator dashboards can reason over one unified trust signal instead of scattered diagnostics.
- **Track label:** `perception`
- **Risk class:** `normal`
- **Owner office:** Cursor (implementation)
- **Target branch:** `master-Cursor`
- **Implementation target:**
  - Keep default behavior inline/sequential unless the env flag is explicitly enabled.
  - Use bounded worker pools and preserve deterministic outputs.
  - Keep tests that assert parallel path is active only when configured.
- **Evidence links (start):**
  - [`src/kernel.py`](../../src/kernel.py)
  - [`tests/test_chat_turn.py`](../../tests/test_chat_turn.py)
  - [`.env.example`](../../.env.example)

## 9) Model-critical backlog (beyond sensors/perception)

When perception P0 items are stable, **prioritize cross-cutting kernel/model risk** in this order (rationale and pointers): [`MODEL_CRITICAL_BACKLOG.md`](MODEL_CRITICAL_BACKLOG.md). It aligns [`CRITIQUE_ROADMAP_ISSUES.md`](CRITIQUE_ROADMAP_ISSUES.md) P0 rows with [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) §3 (unified LLM degradation) and packaging/governance blockers.

**LLM incorporation / adjacent layers / integration** (embedding vs completion, MalAbs semantic, `process_natural` observability, generative candidates): assigned gap register [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) (Cursor shared line).

## 10) Ready-to-use task card examples

Use this exact shape in issues/PR descriptions:

```text
ID: SP-P0-01
Source: docs/WEAKNESSES_AND_BOTTLENECKS.md §3
Track label: runtime-policy
Risk class: critical
Redundancy check: open issue/PR scan + docs/proposals scan
Owner office: cursor-team (shared)
Target branch: cursor/perception-backend-degradation-policy
Definition of done:
- Named defaults documented
- Tests lock behavior and env overrides
- Proposal/ops docs updated
- CHANGELOG updated if operator behavior changed
Evidence links:
- src/modules/perception_circuit.py
- tests/test_perception_circuit.py
- docs/proposals/PERCEPTION_VALIDATION.md
```
