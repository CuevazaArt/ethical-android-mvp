# Cursor cross-team integration gate

**Team remit** (L2 Cursor hub, branch hygiene, and owned PLAN tracks): see [`CURSOR_TEAM_CHARTER.md`](./CURSOR_TEAM_CHARTER.md). This checklist defines when `master-Cursor` is ready to be interlaced with other team branches (`master-*`) before a maintainer decides promotion to `main`.

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
     - `tests/test_chat_turn_policy.py` (Module 0.1.3 — `chat_turn_policy` vs `PreloadedBuffer.get_snapshot` alignment)
     - `tests/test_kernel_utils.py` (Module 0.1.3 — `kernel_decision_event_payload` and env helpers)
     - `tests/test_real_time_bridge.py` (Module 0.2.1 — chat thread offload / pool cap)
     - `tests/test_temporal_planning.py`
     - `tests/test_temporal_horizon_prior.py` (ADR 0005 + PLAN **8.1.33** + **16.0.11** — finite `compute_horizon_signals` / `apply_horizon_prior_to_engine` vs Bayesian weights)
     - `tests/test_perception_confidence.py`
     - `tests/test_process_natural_verbal_observability.py`
     - `tests/test_perception_dual_vote_failure.py`
     - `tests/test_semantic_chat_gate.py`
     - `tests/test_input_trust.py` (PLAN **8.1.3** + **8.1.36** — homoglyph matrix / `normalize_text_for_malabs`)
     - `tests/test_llm_touchpoint_policies.py`
     - `tests/test_llm_http_cancel.py` (G-05 cooperative cancel scope)
     - `tests/test_llm_cancel_burst_operational.py` (G-05 burst concurrency smoke + abandon short-circuit)
     - `tests/test_chat_async_llm_cancel.py` (async LLM HTTP / `KERNEL_CHAT_ASYNC_LLM_HTTP`)
     - `tests/test_chat_turn_abandon.py` (timeout abandon / `turn_abandoned` / cooperative `process` exit)
     - `tests/test_empirical_pilot_runner.py` (Issue 3 — `run_empirical_pilot` / `last_run_summary` regression)
     - `tests/test_governance_mock_honesty_docs.py`
     - `tests/test_semantic_threshold_proposal_doc_alignment.py`
     - `tests/test_transparency_s10.py` (embodied sociability S10 — optional `transparency_s10` in chat JSON)
     - `tests/test_mer_presentation_contract.py` (MER Block 10.5 / ADR 0018 — import guardrails + MalAbs `safety_block` unchanged under presentation envs)
     - `tests/test_turn_prefetcher.py` (MER Block 10.4 — `TurnPrefetcher` heuristic + `OLLAMA_BASE_URL` for `/api/generate`)
     - `tests/test_rlhf_reward_model.py` (RLHF + Module **C.1.1** Bayesian bridge / `TestRlhfBayesianBridge` when `KERNEL_RLHF_MODULATE_BAYESIAN` is on)
     - `tests/test_charm_engine_basal.py` (MER Block **10.3** — optional `KERNEL_BASAL_GANGLIA_SMOOTHING` EMA on charm vector)
     - `tests/test_nomad_bridge_stream.py` (Nomad LAN bridge Module S.1)
     - `tests/test_vitality.py` (Nomad → vitality merge Module S.2.1)
     - `tests/test_variability_engine.py` (PLAN 16.0.2 — VariabilityEngine finite I/O on Bayes noise path)
     - `tests/test_terminal_colors.py` (PLAN 8.1.2 / 16.0.4 — `Term.header` width clamp, `NO_COLOR`)
     - `tests/test_perceptive_lobe.py` (PLAN 16.0.5 — PerceptiveLobe MOCK / `aclose`)
     - `tests/test_kernel_lobes_stack.py` (PLAN **8.1.5** / **8.1.24** — Tri-Lobe stack: finite ProactivePulse operator line, limbic swarm nudge, `CorpusCallosum` probes)
     - `tests/test_kernel_utils.py` (Fase **15.18** / **0.1.9-0.1.10** / **8.1.30-8.1.31** — `kernel_utils` env coercers, `format_proactive_candidate_line`, `kernel` reexport identity vs `kernel_utils`)
     - `tests/test_swarm_sync_script.py` (V14 — `scripts/swarm_sync.py` dry-run JSON, `local_llm_audit` / Ollama netloc; PLAN **8.1.29**)
     - `tests/test_salience_map.py` (PLAN 8.1.4 + **16.0.8** — SalienceMap finite inputs; uniform 1/n axes)
     - `tests/test_somatic_markers.py` (PLAN 8.1.6 + **16.0.8** — somatic nudges; `quantize` without `int(nan)`)
     - `tests/test_kernel_tri_lobe_bus_memory.py` (PLAN 26.0.1 — Tri-Lobe MemoryLobe ↔ `EVENT_KERNEL_AMNESIA_FORGET_EPISODE` / `EVENT_KERNEL_EPISODE_REGISTERED`)

6. **Adversarial suite (promotion toward `master-antigravity`)**
   - Run `python scripts/eval/adversarial_suite.py` from the repository root. This is **in addition to** item 5 (pytest gate), not a substitute. Policy: [`AGENTS.md`](../../AGENTS.md); Cursor red-team lane: [`CURSOR_ROJO1.md`](./CURSOR_ROJO1.md). See also [`ADVERSARIAL_ROBUSTNESS_PLAN.md`](../proposals/ADVERSARIAL_ROBUSTNESS_PLAN.md) and [`INPUT_TRUST_THREAT_MODEL.md`](../proposals/INPUT_TRUST_THREAT_MODEL.md) for threat context.

7. **Operator docs**
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

**CI:** On pull requests to `main`, the workflow job **semantic-default-contract** (`.github/workflows/ci.yml`) runs `tests/test_empirical_pilot_runner.py` together with MalAbs semantic integration tests; the full **quality** job still runs the entire `tests/` tree (including the same module).

## Interlace recommendation

If all gate checks pass:

1. Open cross-team integration PR from `master-Cursor` into the selected team integration branch.
2. Require at least one reviewer from another team (`master-*` owner).
3. Keep rebase-to-`main` as maintainer-only action after cross-team signoff.
