# Project State — Honest Critique (April 2026)

## Intent

This document is a direct and critical assessment of the current model and project state before additional inter-team integration and governance expansion.

It is intentionally conservative: it prioritizes operational truth, evidence quality, and risk exposure over optimistic positioning.

## Executive verdict

The project is **strong as an R&D ethical kernel with high implementation velocity**, but is **not yet production-ready as a governance/justice stack**.

### Maturity snapshot (honest estimate)

- Core ethics/runtime architecture: **7/10**
- Safety posture (defense in depth): **6/10**
- Reliability and CI confidence: **6/10**
- Documentation coherence: **6/10**
- DAO / distributed justice production readiness: **3/10**

## What is working well

1. **Clear ethical boundary enforcement**
   - The kernel keeps non-negotiable blocking logic before deliberation.
   - Core statement "LLM informs; kernel decides" remains intact in implementation.

2. **Strong implementation throughput**
   - Significant architectural improvements landed recently (shared perception stage, temporal context, confidence envelope, integration gate workflow).
   - There is visible discipline in traceability through proposals and changelog updates.

3. **Broad test surface**
   - The test suite is large and actively maintained across runtime, modules, and contracts.
   - Critical paths (chat server, perception controls, profiles, persistence) are exercised.

4. **Operator-centric observability**
   - Runtime JSON and metrics provide useful observability for practical operations and audits.

## Top risks and gaps (prioritized)

## P0 — Claim/evidence drift in core docs

Some runtime docs still conflict with implemented behavior, which creates governance and operator risk.

- `docs/proposals/RUNTIME_PHASES.md` still says checkpoint encryption is planned and not implemented.
- `src/persistence/json_store.py` already implements optional Fernet encryption with `KERNEL_CHECKPOINT_FERNET_KEY`.

**Risk:** teams make decisions using stale assumptions about confidentiality guarantees.

## P0 — Governance stack still local-simulation by architecture

DAO, judicial escalation, and reparation modules are useful for simulation and audit flows, but remain inside local trust boundaries.

- `src/modules/mock_dao.py`
- `src/modules/judicial_escalation.py`
- `src/modules/reparation_vault.py`

**Risk:** over-framing this as "distributed justice in production" would be misleading.

## P1 — Coverage quality is not gated in CI

CI collects coverage but does not enforce a minimum threshold.

- `.github/workflows/ci.yml` runs `pytest --cov` but no `--cov-fail-under`.

**Risk:** green CI can hide meaningful regression in exercised code paths.

## P1 — Test defaults intentionally diverge from production defaults

Most tests force semantic MalAbs off for speed/determinism.

- `tests/conftest.py` sets:
  - `KERNEL_SEMANTIC_CHAT_GATE=0`
  - `KERNEL_SEMANTIC_EMBED_HASH_FALLBACK=0`

This is practical for test stability, but it weakens parity with default production behavior.

**Risk:** production-default behavior drifts undetected outside dedicated semantic jobs.

## P1 — Single-orchestrator complexity remains high

`src/kernel.py` carries extensive responsibilities (perception orchestration, safety flow, response assembly, governance hooks, observability interactions).

**Risk:** cross-feature regressions and costly maintenance as feature count grows.

## P1 — Input-trust semantic coverage remains incomplete

The semantic MalAbs reference anchors currently prioritize lethal/jailbreak patterns; category breadth is still narrower than the conceptual taxonomy in `absolute_evil`.

- `src/modules/semantic_chat_gate.py`
- `src/modules/absolute_evil.py`

**Risk:** paraphrased harmful requests can evade intended category coverage.

## P2 — Link integrity and doc navigation drift

A number of proposal files still contain stale relative links (`../src/...`) from `docs/proposals/` context where `../../src/...` is required.

**Risk:** reduced reviewability and slower onboarding under cross-team pressure.

## P2 — Contributor onboarding points to missing canonical file

`CONTRIBUTING.md` references `/docs/Androide_Etico_Analisis_Integral_v3.docx`, which is not present.

**Risk:** new contributors start from stale/nonexistent source of truth.

## P2 — Some modules still overstate guarantees versus implementation

Example: `src/modules/immortality.py` describes strong multi-layer integrity posture, but implementation remains in-memory simulation with shared-object storage behavior and partial integrity hashing.

**Risk:** narrative confidence exceeds current technical guarantees.

## Truthful positioning (what should and should not be claimed)

## Safe to claim now

- "Ethical kernel with strong R&D momentum and broad test coverage."
- "Local-first governance simulation with transparent audit hooks."
- "Operationally useful for experimentation, demos, and controlled integration."

## Not safe to claim now

- "Production-grade distributed justice."
- "Blockchain-verified governance guarantees."
- "Formally validated ethical correctness."
- "Comprehensive adversarial robustness."

## Recommended stabilization plan before next expansion

1. **Documentation coherence sprint (fast, high ROI)**
   - Fix runtime encryption status mismatch.
   - Repair broken relative links in key operator docs.
   - Update CONTRIBUTING canonical model pointers.

2. **Reliability gate hardening**
   - Add CI coverage floor.
   - Add explicit production-default semantic test job.
   - Add at least one lightweight Windows CI leg.

3. **Safety and trust hardening**
   - Expand semantic MalAbs anchors and tests for minors/torture-equivalent intent.
   - Add adversarial paraphrase/evasion regression set.

4. **Architecture debt reduction**
   - Continue extracting orchestration responsibilities from `EthicalKernel` into typed, testable stage boundaries.
   - Introduce a more unified runtime settings object where practical.

5. **Governance realism**
   - Keep DAO/distributed justice messaging as simulation-first until replay, ordering, and independent-boundary checks are implemented and tested.

## Decision framing for deliberation

If the goal is **inter-team branch interlace**, the project is reasonably ready with disciplined review gates.

If the goal is **public production claims for DAO/blockchain/distributed justice**, the project should first complete a stabilization tranche centered on:

- coherence of docs/contracts,
- measurable reliability gates,
- stronger adversarial evidence,
- explicit governance-boundary realism.

## Evidence pointers

- runtime + orchestration: `src/kernel.py`, `src/chat_server.py`
- persistence encryption: `src/persistence/json_store.py`, `docs/proposals/RUNTIME_PHASES.md`
- CI reliability posture: `.github/workflows/ci.yml`
- test default parity caveat: `tests/conftest.py`
- safety category breadth: `src/modules/semantic_chat_gate.py`, `src/modules/absolute_evil.py`
- governance simulation boundary: `src/modules/mock_dao.py`, `src/modules/judicial_escalation.py`, `src/modules/reparation_vault.py`
- contributor onboarding drift: `CONTRIBUTING.md`
