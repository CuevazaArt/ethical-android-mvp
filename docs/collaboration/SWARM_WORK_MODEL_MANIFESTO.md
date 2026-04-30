# Swarm Work Model Manifesto

**Subtitle:** A portable operating system for high-velocity, safety-aware software teams.

## 1) Why this manifesto exists

Most teams do not fail because they lack talent. They fail because they lack a shared execution model under pressure.  
This manifesto defines a complete, practical, and transferable method for:

- Distributed collaboration across humans and AI agents.
- Predictable integration in multi-branch environments.
- Quality and safety guardrails that scale with speed.
- Traceable delivery that survives tool changes and team turnover.

This is a method you can adopt in startups, enterprise teams, research groups, and mixed human-agent organizations.

---

## 2) Core doctrine (non-negotiable)

1. **Deliver outcomes, not activity.**  
   A unit of work is complete only when behavior is demonstrable.

2. **Single owner, full accountability.**  
   One work unit has one accountable owner from start to closure.

3. **Proof or it does not exist.**  
   Every completed unit includes execution evidence (tests, logs, or equivalent demo).

4. **Vertical integration by default.**  
   No isolated implementation-only work: code + tests + context update travel together.

5. **Minimal surface area.**  
   Prefer the smallest coherent change. New files require explicit justification.

6. **Prune continuously.**  
   Remove obsolete code and stale artifacts as part of delivery.

7. **Single source of truth.**  
   One concept, one canonical location. Duplicates are operational debt.

8. **Zero-trust engineering.**  
   Inputs are hostile by default; hardening is not optional.

9. **Repository is the memory, not chat.**  
   Decisions become durable only when encoded in code, tests, and docs.

10. **Governance over velocity, but never velocity without governance.**  
    Fast is good; reproducible and reviewable fast is the target.

---

## 3) Roles and authority model

Use role names that match your organization, but keep the structure:

- **L0 (Final authority):** owns production promotion decisions.
- **L1 (Watchtower / Integrator):** orchestrates work, validates closure, consolidates merges.
- **Scouts (Executors):** implement assigned vertical blocks end to end.

### Responsibility boundaries

- Only L0 (or designated release authority) promotes to production branch.
- L1 optimizes flow, quality, and coherence across contributors.
- Scouts own delivery quality of their assigned block; no incomplete handoffs.

---

## 4) Unit of execution: the vertical block

A block is the atomic work unit. It must include:

- Clear ID.
- Concrete deliverable.
- Allowed file scope.
- Required evidence.
- Expected tests.
- Closure checklist.

### Block assignment template

```text
## Block <ID> — <Name>
- Objective:
- Scope (files allowed):
- Out of scope:
- Definition of done:
- Required tests:
- Required demo evidence:
- Risks:
```

### Block closure template

```text
## Block <ID> — <Name>
- Status: CLOSED
- Files created/modified:
- Files deleted:
- Demo evidence:
- Tests executed:
- Result summary:
```

---

## 5) Collaboration protocol

### 5.1 Required reading order before coding

1. Contribution policy.
2. Collaboration workflow.
3. Agent/operator orientation.
4. Always-on rules and quality gates.
5. Active scope playbooks.

### 5.2 Redundancy-first behavior

Before implementation:

- Check open issues and active PRs.
- Search code and docs for recent equivalent work.
- Extend in-progress work when possible.

### 5.3 Language split for global teams

- **Collaboration language:** local team language allowed.
- **Repository language:** one canonical merge language (recommended: English).
- Explicit exceptions allowed only for intentional test/security payloads.

---

## 6) Workflow architecture (Git + integration funnel)

### 6.1 Branch topology

- `main`: protected production line.
- `master-<TeamSlug>`: team integration hub.
- `feature/<name>` (or topic branches): execution branches.

### 6.2 Promotion path

`feature/*` -> `master-<TeamSlug>` -> integration hub (`master-antigravity` or equivalent) -> `main`

### 6.3 Session start ritual

1. Fetch latest remote state.
2. Sync with production intent (`origin/main`).
3. Inspect peer team hubs for incremental updates.
4. Pull peer deltas only when conflict risk is acceptable.

### 6.4 Merge message semantics (recommended)

- `merge(sync): ...` for peer hub synchronization.
- `merge(integration): ...` for staged integration merges.
- `merge(main): ...` for production-line refresh merges.

---

## 7) Swarm method (multi-agent / multi-team execution)

### 7.1 Compute budget strategy

Adopt an explicit budget per cycle:

- Low-cost/high-throughput model tier for most implementation and tests.
- Higher-reasoning tier reserved for architecture and hard conflict resolution.

This preserves quality while protecting token/time budgets.

### 7.2 Watchtower model

L1 continuously:

- Ingests completed blocks.
- Performs micro-merges to reduce drift.
- Resolves integration friction early.
- Keeps context synchronized across environments.

### 7.3 Interruption recovery protocol

If a contributor/agent is interrupted:

1. Capture ground truth (`git status`, `git diff`, test state).
2. Separate done work vs remaining work.
3. Issue a continuation brief with only pending deliverables.
4. Re-run tests before closure.

### 7.4 Context transfer protocol

When switching tools/IDEs/offices:

- Generate a compact handoff block (current branch, active block, latest changes, pending steps).
- Paste handoff as first message in the new environment.
- Re-anchor on persistent context docs before writing code.

---

## 8) Quality, safety, and security gates

### 8.1 Baseline quality gate (pre-push)

- Lint
- Format check
- Static typing
- Test suite (targeted during development, full before integration)

### 8.2 Security cadence

- Run adversarial/security evaluation on a fixed cadence (for example every 3 blocks).
- Any safety-critical threshold or gating change requires immediate adversarial audit.
- No feature expansion when critical safety checks are failing.

### 8.3 Safety-critical full pattern

For threshold/gate/circuit-limit changes, ship all of:

1. Named defaults in code.
2. Tests locking defaults and override behavior.
3. Documentation stating evidence and limits honestly.
4. Changelog entry when behavior or operator expectations change.

---

## 9) Documentation and traceability doctrine

Documentation is an operational artifact, not decoration.

Minimum expectation for meaningful changes:

- Update the smallest relevant technical doc (proposal, ADR, or runbook).
- Add changelog entry for operator/reviewer-visible effects.
- Keep claims aligned with transparency and limitations policy.
- Prefer durable repository references over chat-only explanations.

---

## 10) CI economy policy

Use CI as a quality instrument, not as background noise.

- Run full CI for executable-code changes.
- Skip heavy jobs automatically for docs-only changes.
- Keep lightweight structural checks always-on.
- Batch local micro-commits and push once per swarm cycle when possible.

Goal: maximize confidence per CI minute.

---

## 11) Command interface for operational clarity

A small command vocabulary reduces coordination latency.  
Define short, unambiguous operator commands such as:

- next task generation
- state report
- review request
- merge request
- interruption recovery
- conflict resolution request

This allows high-throughput orchestration with low cognitive overhead.

---

## 12) Anti-patterns this manifesto prohibits

- Shipping code without evidence.
- Starting dependent work before upstream closure.
- Editing outside declared scope.
- Treating docs as optional after implementation.
- Creating parallel versions of the same concept.
- Direct production pushes without release authority.
- Repeating work already implemented elsewhere.

---

## 13) Portable adoption plan (for new organizations)

### Phase A — Bootstrap (Week 1)

- Define L0/L1/executor roles.
- Create branch model and merge authority policy.
- Publish quality gate command set.
- Standardize block templates.

### Phase B — Stabilize (Weeks 2–4)

- Run work by vertical blocks only.
- Enforce closure evidence on every block.
- Add integration pulse rituals and merge message prefixes.
- Introduce interruption and handoff protocols.

### Phase C — Scale (Month 2+)

- Add explicit swarm compute budgets.
- Instrument lead time, reopen rate, CI waste, and merge conflict rates.
- Tune cadence without relaxing governance rules.

---

## 14) Suggested metrics (executive dashboard)

- **Lead time per block** (start -> closed with evidence).
- **Reopen rate** (closed blocks reopened due to regressions).
- **Merge conflict density** (conflicts per 100 commits).
- **CI efficiency ratio** (useful validation minutes / total CI minutes).
- **Documentation latency** (time from behavior change to docs/changelog update).
- **Safety gate pass rate** (critical checks first-pass success rate).

---

## 15) One-page executive summary

This manifesto operationalizes a simple idea: **scale requires a shared method, not heroic individuals**.  
Its differentiators are:

- vertical blocks with hard closure evidence,
- explicit authority and integration layers,
- swarm-aware budget and orchestration discipline,
- quality/security gates tied to delivery,
- and durable traceability in repository artifacts.

Teams that adopt this model gain speed with lower coordination entropy, lower merge risk, and higher auditability.

---

## 16) How to adapt without breaking the method

You may adapt:

- branch names,
- model roster,
- command vocabulary,
- and cadence windows.

You should not relax:

- evidence-based closure,
- scoped accountability,
- protected production promotion,
- safety-critical full-pattern requirements,
- and repository-first traceability.

If those invariants hold, the method remains valid across domains and industries.
