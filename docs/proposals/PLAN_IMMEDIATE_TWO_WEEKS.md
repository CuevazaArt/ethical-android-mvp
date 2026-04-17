# Immediate action plan — next two weeks

**Horizon:** ~14 days from the dated CHANGELOG entry (April 2026).  
**Audience:** maintainers triaging [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md) issues **#1–#9** and cross-refs in [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md).

This file is the **repo-local execution backlog**. **GitHub milestones, assignees, and labels** are set in the GitHub UI — not here.

**Quick wins (landed):** [PROPOSAL_QUICK_WINS_TWO_SPRINTS.md](PROPOSAL_QUICK_WINS_TWO_SPRINTS.md) — strict env default, lab/`pytest` ergonomics, perception circuit + metacognitive doubt, `ethos-runtime`, starter Prometheus alert rules.

---

## GitHub setup (maintainers — one-time per sprint)

1. **Create milestones** (suggested names; adjust dates to your calendar):
   - `Sprint 2026-04-25 — P0 blockers`
   - `Sprint 2026-04-25 — P1 core`
   - `Sprint 2026-04-25 — P2 polish` (optional; may spill to next sprint)
2. **Triage issues #1–#7:** attach milestone + priority label + assignee per table below.
3. **Close or narrow** duplicate / already-delivered acceptance items (several issues have partial delivery in-tree; update issue bodies to match reality).

---

## Priority map (this plan ↔ issues)

| Tier | Theme | Issues | Notes |
|------|--------|--------|--------|
| **P0** | Blockers | #1, #2, #6 (and security thread) | Honest naming, input trust, governance framing |
| **P1** | Core | #3, #4, #7 | Evidence, packaging boundary, env validation |
| **P2** | Polish | Observability, E2E, deprecations | Often overlaps ADR 0008 / roadmap |

---

## P0 — Blocking (must schedule first)

### 1. Triage issues #1–#7 (and #8–#9 as capacity allows)

| Issue | Suggested milestone | Suggested owner | Next action |
|-------|---------------------|-----------------|-------------|
| **#1** Bayesian naming vs mixture | P0 or P1 | **A recorded (docs)** | Option **A** — README + ADR 0009 / theory; see § P0 Bayesian below. |
| **#2** Input trust / MalAbs + perception | **P0 blockers** | TBD | Run evasion reproduction checklist; extend adversarial tests if gaps found. |
| **#3** Empirical pilot | P1 core | TBD | Expand labeled dataset + baseline comparison scripts (see § P1). |
| **#4** Core chain + packaging | P1 core | TBD | **Largely documented** — verify README + `pyproject.toml` extras; close or narrow issue. |
| **#5** Poles / weakness / PAD | P2 or backlog | TBD | No change required for this two-week slice unless capacity. |
| **#6** Governance MockDAO vs L0 | **P0 blockers** | TBD | Add **checkpoint** acceptance: see § P0 Governance. |
| **#7** KERNEL_* combinatorics | P1 core | TBD | Validator exists — verify strict mode in CI smoke; extend rules if needed. |

### 2. Security hardening — reproduce MalAbs evasion; threat model

**Goal:** no “paper” security — every claimed gap has a **repro** (test or documented command).

| Step | Deliverable | Location |
|------|-------------|----------|
| Run lexical + semantic adversarial suite | `pytest tests/adversarial_inputs.py tests/test_input_trust.py` | CI already runs with main suite |
| Run subprocess MalAbs integration (hash path) | `pytest tests/test_malabs_semantic_integration.py -v` | Documents production-like defaults |
| Document reproduction | Checklist in [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md) § *Reproducing known MalAbs evasion* | Operators + reviewers |
| Extend catalog | New rows in [ADVERSARIAL_ROBUSTNESS_PLAN.md](ADVERSARIAL_ROBUSTNESS_PLAN.md) when a new vector is added | Tied to Issue **#2** |

**Stretch (if time):** one new red-team vector with explicit `expected` behavior (pass/block/defer) per [ADVERSARIAL_ROBUSTNESS_PLAN.md](ADVERSARIAL_ROBUSTNESS_PLAN.md) Phase 2.

### 3. “Bayesian” — rename or minimal update (Issue #1)

**Decision required by end of sprint:**

| Option | Work |
|--------|------|
| **A — Rename (preferred for speed)** | User-facing strings + top-level docs: “weighted mixture” / “Bayesian-style scoring”; keep class name `BayesianEngine` with docstring caveat (breaking rename deferred). |
| **B — Minimal Bayes** | Small, tested update path (e.g. bounded episodic nudge already partially present) — document exact semantics; no silent full posterior claim. |

**Recorded (April 2026):** Option **A** — operator- and contributor-facing text uses **weighted mixture** / **Bayesian-style** where needed; root [`README.md`](../../README.md) § *What it does* states semantics; class name `BayesianEngine` unchanged. Canonical detail: [ADR 0009](../../docs/adr/0009-ethical-mixture-scorer-naming.md), [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md).

**Do not** leave #1 open without an explicit maintainer decision recorded in the issue.

### 4. Governance checkpoints (Issue #6)

**Within two weeks, ship:**

- [x] **Governance checkpoint** — operator checklist in [GOVERNANCE_MOCKDAO_AND_L0.md](GOVERNANCE_MOCKDAO_AND_L0.md) §5.
- [x] README already links governance; checkpoint doc cross-links to regression test.
- [x] Regression test [`tests/test_governance_l0_immutable.py`](../../tests/test_governance_l0_immutable.py) — L0 fingerprint unchanged after DAO submit / vote / resolve.

---

## P1 — Core (schedule after P0 is staffed)

### 1. Env combo validation (Issue #7)

**Status in repo:** [`src/validators/env_policy.py`](../../src/validators/env_policy.py) implements `SUPPORTED_COMBOS`, `collect_env_violations`, `validate_kernel_env`; [`src/chat_server.py`](../../src/chat_server.py) runs validation after profile merge.

| Task | Done when |
|------|-----------|
| Confirm **strict** path tested | [`tests/test_env_policy.py`](../../tests/test_env_policy.py) (`mode="strict"`); CI **windows-smoke** runs the same module ([`.github/workflows/ci.yml`](../../.github/workflows/ci.yml)) |
| Document operator workflow | [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md); [README.md](../../README.md) § *Environment validation*; `ethos config --strict` ([`CONTRIBUTING.md`](../../CONTRIBUTING.md)) |
| Expand `DEPRECATION_ROADMAP` | First **real** entry when a flag is scheduled (see P2) |

### 2. Labeled scenarios + baselines (Issue #3)

| Task | Done when |
|------|-----------|
| Dataset | [`tests/fixtures/labeled_scenarios.json`](../../tests/fixtures/labeled_scenarios.json) + methodology [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md); expanded pilot fixture [`tests/fixtures/empirical_pilot/scenarios.json`](../../tests/fixtures/empirical_pilot/scenarios.json) |
| Runner | [`scripts/run_empirical_pilot.py`](../../scripts/run_empirical_pilot.py) documents `--output` and harness filter; regression [`tests/test_empirical_pilot_runner.py`](../../tests/test_empirical_pilot_runner.py) in CI (**semantic-default-contract** job) + [`run_cursor_integration_gate.py`](../../scripts/eval/run_cursor_integration_gate.py) |
| Baseline comparison | [EMPIRICAL_METHODOLOGY.md](EMPIRICAL_METHODOLOGY.md) §3 defines **first** / **max_impact** baselines; script columns `baseline_first`, `baseline_max_impact` (static policies on the same candidate lists — not ground truth) |

### 3. Core vs optional boundary (Issue #4)

**Status:** README diagram + `pyproject.toml` `theater` extra + [ADR 0001](../adr/0001-packaging-core-boundary.md).  
**Remaining:** optional import-split is **out of scope** for two weeks — track in issue or Phase 4 of [PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md).

---

## P2 — Polish (spillover acceptable)

| Item | Pointer |
|------|---------|
| **Prometheus / structured logging** | [ADR 0008](../adr/0008-runtime-observability-prometheus-and-logs.md), [`src/observability/`](../../src/observability/); **verification table** in [`docs/deploy/COMPOSE_PRODISH.md`](../deploy/COMPOSE_PRODISH.md) (`/health`, `/metrics` 200 vs 404 when disabled, compose `config` = CI) |
| **End-to-end tests (kernel ↔ landing)** | Landing is **Next.js** — E2E is **manual or Playwright in `landing/`** (not kernel pytest). Add a **smoke checklist** in [REPOSITORY_LAYOUT.md](../REPOSITORY_LAYOUT.md) or landing README if missing. |
| **Deprecation roadmap for flags** | [`DEPRECATION_ROADMAP`](../../src/validators/env_policy.py) + [KERNEL_ENV_POLICY.md](KERNEL_ENV_POLICY.md); first scheduled deprecation needs CHANGELOG + version bump policy |

---

## Definition of done (end of two weeks)

1. **GitHub:** Issues #1–#7 have milestones and assignees (or explicit “deferred” with reason).
2. **Security:** Threat-model reproduction section filled; adversarial tests green on `main`.
3. **Governance:** Issue #6 has documented checkpoints linked from README or issue.
4. **Bayesian:** Issue #1 has a recorded decision (rename path or minimal update).
5. **P1:** Env validation and empirical pilot paths **verified** or issue bodies updated to remaining gaps.

---

## Appendix — Technical model: pending vs settled (April 2026)

Cross-check: [`PROJECT_STATUS_AND_MODULE_MATURITY.md`](PROJECT_STATUS_AND_MODULE_MATURITY.md), [`PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md`](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md), [`WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md), [`MODULE_IMPACT_AND_EMPIRICAL_GAP.md`](MODULE_IMPACT_AND_EMPIRICAL_GAP.md).

| Area | Settled in code/docs | Still open (technical) |
|------|----------------------|-------------------------|
| **Scoring (mixture)** | [`weighted_ethics_scorer.py`](../../src/modules/weighted_ethics_scorer.py) canonical module; kernel imports `BayesianEngine` from [`bayesian_engine.py`](../../src/modules/bayesian_engine.py) (`BayesianInferenceEngine` wraps scorer; [ADR 0009](../../docs/adr/0009-ethical-mixture-scorer-naming.md)); theory + core chain aligned. | Full **online** Bayesian inference over parameters = **new scoped project**, not the current mixture. |
| **MalAbs chat** | Lexical + normalization + optional semantic tier + tests. | **Evasion** cataloged in [ADVERSARIAL_ROBUSTNESS_PLAN.md](ADVERSARIAL_ROBUSTNESS_PLAN.md); hash embeddings **weaker** than neural; paraphrase without n-grams remains a known gap. |
| **Buffer / L0** | `PreloadedBuffer.verify_action` — lexical/heuristic checks. | [Phased remediation §3.2](PROPOSAL_CORE_IMPLEMENTATION_GAP_PHASED_REMEDIATION.md): **embedding or LLM verifier** paths for principles are **not** implemented as described (lab backlog). |
| **Perception** | Pydantic + coherence + caps in `perception_schema` / `llm_layer`. | **GIGO:** valid JSON can still bias signals; no semantic “world truth” check ([INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)). |
| **Epistemic / reality / lighthouse** | Modules exist under flags. | Maturity **Experimental** — integration depth varies ([PROJECT_STATUS…](PROJECT_STATUS_AND_MODULE_MATURITY.md)). |
| **Governance** | MockDAO + L0 honesty documented. | Durable off-process votes / verifiable records = **Phase 5** in phased remediation, not MVP-complete. |
| **Stubs / narrative crypto** | `swarm_peer_stub`, `ml_ethics_tuner`, continuity stubs in `existential_serialization`. | Explicit **stubs** — not production paths. |
| **Runtime architecture** | WebSocket chat: `RealTimeBridge` thread offload; optional `KERNEL_CHAT_TURN_TIMEOUT`, `KERNEL_CHAT_THREADPOOL_WORKERS` ([ADR 0002](../adr/0002-async-orchestration-future.md)); cooperative cancel + `abandon_chat_turn`, async LLM path, Anthropic `AsyncAnthropic` where applicable. | Uniform **prefix** env namespace for all LLM touchpoints — [WEAKNESSES… §3](../WEAKNESSES_AND_BOTTLENECKS.md); preempting a **single** long native call inside `process()` without cooperative checkpoints remains OS-limited ([ADR 0002](../adr/0002-async-orchestration-future.md) §9). |

**Net:** the **numeric ethical core path** (MalAbs → mixture choice → poles/will shaping modes) is **tested and documented**; pending items are **input-trust recall**, **buffer verification depth**, **governance persistence**, and **LLM env surface / degradation uniformity** ([WEAKNESSES… §3](../WEAKNESSES_AND_BOTTLENECKS.md)) — not “missing a hidden scoring engine.” Chat async bridge: cooperative cancel + abandon + optional async HTTP are **partially** implemented ([ADR 0002](../adr/0002-async-orchestration-future.md)); remaining limits are documented there (§9).

---

## References

- [CRITIQUE_ROADMAP_ISSUES.md](CRITIQUE_ROADMAP_ISSUES.md)
- [INPUT_TRUST_THREAT_MODEL.md](INPUT_TRUST_THREAT_MODEL.md)
- [ADVERSARIAL_ROBUSTNESS_PLAN.md](ADVERSARIAL_ROBUSTNESS_PLAN.md)
- [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md)
