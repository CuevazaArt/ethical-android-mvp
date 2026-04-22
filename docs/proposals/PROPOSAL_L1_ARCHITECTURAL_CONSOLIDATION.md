# PROPOSAL: L1 Architectural Consolidation (Subtraction & Truth)

## 1. Context and Honest Appraisal
Following a deep and critical review of the Ethos Kernel's current state, we acknowledge the project's genuine philosophical ambition and substantial foundational work (Bayesian engine, Audit framework, Multi-Realm Governance, Event Bus). However, we also recognize severe structural and aspirational gaps:
- **Catastrophic Fragmentation:** `src/modules/` is a flat pile of ~150 files, destroying navigability.
- **Incomplete Decoupling:** The kernel remains largely monolithic, orchestrating 14+ stages.
- **Silent Failures:** Pytest collection errors mask broken tests for optional dependencies.
- **Aspirational Gap:** The `CHANGELOG.md` promises capabilities (e.g., RLHF PPO, Nomad physical sensors) that are currently mocks or shims.
- **The Missing Core:** The system evaluates ethical responses, but lacks a real, tightly-coupled LLM generation loop (Anthropic/Ollama).

## 2. Objective (L1 Directive)
Transition the project from an "academic ethical library" to a "conscious assistant" by executing a rigorous phase of **Subtraction and Consolidation**. We will build the capabilities the user actually expects, and archive or mock anything that distracts from a demonstrable end-to-end flow.

## 3. Execution Priorities (Phase 15 Roadmap)

### Priority 1: Couple a Real LLM (The Missing Core)
- **Action:** Integrate a genuine generator (Anthropic SDK or Ollama). The kernel must intercept and filter real-time generation (`generate -> ethical-filter -> render`).
- **Goal:** Shift from evaluating imaginary responses to an actual, interactive ethical consciousness.

### Priority 2: Collapse `src/modules/`
- **Action:** Reorganize the ~150 files into 6-8 cohesive domains using `git mv` and import updates.
  - `ethics/`: `absolute_evil`, `buffer`, `poles`, `deontic_gate`
  - `cognition/`: `bayesian`, `mixture_averaging`, `reflection`
  - `memory/`: `narrative`, `forgiveness`, `immortality`, `biographic`
  - `social/`: `uchi_soto`, `gray_zone`, `swarm`
  - `governance/`: `dao`, `multi_realm`, `audit`, `mock_dao`
  - `somatic/`: `hardware`, `sympathetic`, `affective_homeostasis`
  - `perception/`: `input_trust`, `vision`, `audio`, `nomad`
  - `safety/`: `guardian`, `judicial`, `malabs`

### Priority 3: Honest Module Status Labels
- **Action:** Add a standardized docstring header to every module indicating its real state:
  ```python
  """
  Status: REAL | SCAFFOLD | MOCK | EXPERIMENTAL
  Coverage: X%
  """
  ```
- **Goal:** Auto-generate a `STATUS.md` so external users know exactly what works.

### Priority 4: Repair the Pytest Collection
- **Action:** Wrap optional dependencies (Torch, ChromaDB) with `pytest.importorskip`.
- **Goal:** Ensure `pytest tests/` runs cleanly in a minimal environment without silent collection errors.

### Priority 5: Real End-to-End Demo
- **Action:** Build a demonstrable flow (e.g., `ethos chat`) showing a user request intercepted, ethically evaluated, and either rejected with a deontic trace or fulfilled.

### Priority 6: Prune the Theater
- **Action:** Archive purely theoretical modules (`augenesis`, `internal_monologue`, `psi_sleep`) to `docs/archive/concepts/` if they do not provide empirically verifiable output.

### Priority 7: Physical Nomad Hardware
- **Action:** Replace WebSocket empty stubs with actual pipelines (e.g., physical phone accelerometer -> `jerk_detector` -> `VitalityAssessment`, Camera -> `MobileNetV2` threat perception).

## 4. Work Distribution Impact
The `PLAN_WORK_DISTRIBUTION_TREE.md` has been refocused. All legacy "aspirational" blocks are suspended. Swarm execution will now exclusively target the 7 Priorities outlined above.
