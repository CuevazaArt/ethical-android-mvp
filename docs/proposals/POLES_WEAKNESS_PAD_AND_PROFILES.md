# Poles, weakness, PAD — heuristics and HCI profiles (Issue 5)

**Purpose:** State honestly what **EthicalPoles**, **WeaknessPole**, and **PAD / homeostasis** do in the Ethos Kernel, and give **operators** a clear **profile** when narrative “humanizing” layers may **hurt trust** in safety-critical settings (medicine, autonomy, crisis ops).

**Cross-refs:** [`THEORY_AND_IMPLEMENTATION.md`](THEORY_AND_IMPLEMENTATION.md) (pipeline order), [`src/runtime_profiles.py`](../../src/runtime_profiles.py), [`RUNTIME_CONTRACT.md`](RUNTIME_CONTRACT.md) (LLM does not set policy).

---

## 1. Ethical poles — heuristic multipolar scores

`EthicalPoles` (`src/modules/ethical_poles.py`) assigns **stylized** pole labels (`compassionate`, `conservative`, `optimistic`) with **dynamic weights** by context. Per-pole **linear** scores load from `pole_linear_default.json` (or **`KERNEL_POLE_LINEAR_CONFIG`**); see [ADR 0004](adr/0004-configurable-linear-pole-evaluator.md). The aggregate is still a **weighted sum** of per-pole valuations — **not** a calibrated moralometer and **not** peer-reviewed external validity.

**Claims to avoid in product copy:**

- “Objective ethics score” / “provably correct verdict”
- Precision beyond what `TripartiteMoral.total_score` and labels support

**Honest framing:** multipolar **heuristics** for narration, audit, and reflection; the **action id** still comes from MalAbs → `BayesianEngine` (see [`CORE_DECISION_CHAIN.md`](CORE_DECISION_CHAIN.md)).

---

## 2. Weakness pole — narrative color, not policy

`WeaknessPole` runs **after** `final_action` is fixed; it **does not** change the chosen action (see invariant tests in `tests/test_ethical_properties.py`). It influences **tone** and episodic memory (e.g. `weakness_line` hints into `LLMModule.communicate`).

**HCI risk:** simulated hesitation / “neurotic” color can read as **unreliable** or **distracting** when the user needs **predictable, stoic** machine behavior (clinical decision support, vehicle UX, emergency dispatch).

---

## 3. PAD and homeostasis telemetry

`PADArchetypeEngine` projects affective coordinates for narrative; **homeostasis** JSON (`affective_homeostasis` in WebSocket responses) exposes σ / strain / PAD-related **UX telemetry** — still **no feedback** into the ethical argmax.

**HCI risk:** rich inner-state fields can feel like **excessive anthropomorphism** or **opacity** (“why is the machine ‘stressed’?”) in high-stakes domains.

---

## 4. Mitigation: tone down narrative UX (env flags)

These flags **do not** change `final_action`; they **omit or redact** narrative layers in **chat JSON** / LLM embellishment:

| Goal | Variables (set to `0` / `false` / `off` as documented in README) |
|------|-------------------------------------------------------------------|
| Omit homeostasis / PAD-advisory block | `KERNEL_CHAT_INCLUDE_HOMEOSTASIS` |
| Redact internal monologue line | `KERNEL_CHAT_EXPOSE_MONOLOGUE` |
| Omit experience digest (inner summary) | `KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST` |

Further relational fields (`KERNEL_CHAT_INCLUDE_USER_MODEL`, `…_CHRONO`, `…_PREMISE`, `…_TELEOLOGY`) can be turned off for **privacy** or **minimal surface** — see README WebSocket section.

---

## 5. Runtime profile matrix (demo vs operational trust)

Named bundles live in **`src/runtime_profiles.py`**. Relevant rows:

| Profile | Poles / weakness / PAD in policy? | Narrative UX in WebSocket (default README) |
|---------|-------------------------------------|-------------------------------------------|
| `baseline` | Same core pipeline; poles always evaluate chosen action | Default: homeostasis + monologue + digest **on** (rich demo) |
| `operational_trust` | Unchanged **policy**; fewer **telemetry / tone** affordances | Homeostasis **off**, monologue **off**, experience digest **off** — **stoic** operator-facing JSON |

**Batch / simulations:** `EthicalKernel.process` still runs poles → weakness → PAD internally for episodes unless you change code; this profile targets **runtime chat** and **operator trust**, not rewriting the research harness.

---

## 6. Calibration roadmap (future work)

- **Linear pole weights and context multipliers** are heuristics, not empirically calibrated to human judgment today; scope, constraints, and a serious evidence program are in [POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md](POLE_WEIGHT_CALIBRATION_AND_EVIDENCE.md).
- Explicit **“clinical”** or **“autonomy”** product modes may add stricter defaults — should remain **documented** and **tested** (extend `RUNTIME_PROFILES` + smoke tests).
- Any **weight** changes to `EthicalPoles.BASE_WEIGHTS` belong in CHANGELOG + versioned experiments — not silent tweaks.

---

*MoSex Macchina Lab — critique roadmap Issue 5.*
