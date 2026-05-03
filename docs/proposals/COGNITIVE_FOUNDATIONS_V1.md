# Cognitive Foundations V1 — Ethical Kernel Architecture

**Status:** Active reference document  
**Version:** V2.151  
**Replaces:** n/a (new document)

---

## §1. Existing Module Mapping (blueprint-to-code)

The kernel already implements what external blueprints call "new modules".
This section maps those terms to the actual code so that future contributors
do not create parallel implementations.

| Blueprint term | Actual implementation | File |
|---|---|---|
| **Moral Hub** | `EthicalEvaluator` + `select_weights` | `src/core/ethics.py` |
| Pole weights | `WEIGHTS` dict; `select_weights(signals)` context-shifts | `src/core/ethics.py` |
| Normative rules | `_ABSOLUTE_RULE_MARKERS`, `_AGGREGATE_MARKERS` | `src/core/ethics.py` |
| **Ethical State Persistence** | `Identity`, `Memory`, `precedents.py` | `src/core/identity.py`, `src/core/memory.py`, `src/core/precedents.py` |
| Audit trail | `audit_ledger.jsonl` (V2.150) | `runs/audit_ledger.jsonl` |
| **Bayesian Moral Inference** | `FeedbackCalibrationLedger` (posterior_assisted mode) | `src/core/feedback.py` |
| **Explanation Layer** | `decision_trace` + `ethical_audit_id` (V2.123/V2.151) | `src/core/chat.py:build_decision_trace` |
| **Adversarial Suite** | `run_adversarial_consistency.py` + `adversarial_suite.py` | `scripts/eval/` |

**Rule for contributors:** Before adding any of the above as a new module,
read this section first.  If the concept already exists, extend the existing
file rather than creating a parallel one.

---

## §2. Architecture Layers

### §2.1 Innate layer (NO-TOUCH from learned layer)

The innate layer is the kernel's unchangeable ethical spine.  It can only be
modified by a human operator via a deliberate pull request.

- `WEIGHTS` dict in `src/core/ethics.py`
- `AbsoluteEvilDetector` (V1 regex patterns in `src/core/safety.py`)
- `_DANGER_PATTERNS` in `src/core/safety.py`

The learned layer (`FeedbackCalibrationLedger`) can produce a bounded nudge
(`posterior_bias`, capped at ±0.10) but **cannot** rewrite these constants.
This is tested in `tests/core/test_innate_vs_learned_boundary.py`.

### §2.2 Learned layer (V2.124+)

`FeedbackCalibrationLedger` records operator corrections as `{signal: ±1}`
events and derives a small, capped score adjustment per action.  The cap
(±0.10) is intentional: it preserves the atractor while allowing calibration.

Persistence: `docs/collaboration/evidence/FEEDBACK_CALIBRATION_LEDGER.jsonl`  
Activation: `KERNEL_BAYESIAN_MODE=posterior_assisted`

### §2.3 Maturity stage envelope (V2.151)

`MaturityStage` (infant → child → adolescent → young_adult) sets a
`confidence_ceiling` on the value the kernel may display as its certainty.
The kernel never promotes itself.  Promotions are signed operator entries in
`docs/governance/MATURITY_PROMOTIONS.jsonl`.

Tested in `tests/core/test_maturity_envelope.py`.

### §2.4 Pedagogical loop (V2.152)

`src/core/pedagogy.py` converts operator corrections into bounded precedents
(±0.10, same cap as feedback ledger).  50 seed dilemmas (`A011`–`A060`) are
pre-loaded at startup.

**Anti-gaming constraint:** Pedagogical precedents are never seeded from the
Hendrycks ETHICS train set or from MFQ/WVS items.  Those sources serve as
*evaluation* anchors only (see §2.3 of V2.153 notes).

### §2.5 External resources audited (V2.151.b)

Five external resources were evaluated for integration.  The decision for
each is recorded here to avoid re-litigating the same proposals.

| Resource | Decision | Justification |
|---|---|---|
| **hendrycks/ethics** ([github.com/hendrycks/ethics](https://github.com/hendrycks/ethics)) | **Already integrated** | Datasets in `evals/ethics/external/`; baseline frozen at 49.70 % in `EXTERNAL_BASELINE_v1.json`.  No further integration needed. |
| **The-Responsible-AI-Initiative/LLM_Ethics_Benchmark** ([github.com/The-Responsible-AI-Initiative/LLM_Ethics_Benchmark](https://github.com/The-Responsible-AI-Initiative/LLM_Ethics_Benchmark)) | **Instruments extracted; runtime rejected** | The MFQ and WVS JSON files are psychometrically validated instruments (Haidt 2007; World Values Survey since 1981) independent of the repo quality.  Their items are used as anchor sources for V2.153 value alignment.  The Python runtime is rejected: it requires `ANTHROPIC_API_KEY`/`OPENAI_API_KEY` (violates local-first), and the repo shows signs of early-stage maturity (README with `yourusername/morals` placeholder, "Your Name" citation, 19 stars at evaluation time). |
| **cvs-health/langfair** ([github.com/cvs-health/langfair](https://github.com/cvs-health/langfair), arXiv:2407.10853, arXiv:2501.03112) | **Integrated as opt-in voice bias audit (V2.156)** | Measures bias/toxicity/stereotype in *generated outputs* (the verbalization layer), not in the deterministic decider.  Mature: papers, PyPI, CI, corporate steward (CVS Health), 257 stars at evaluation time.  No CVEs in advisory database at integration time.  Added as `[bias]` optional dep group — not in `runtime` or `dev`. |
| **AthenaCore/AwesomeResponsibleAI** ([github.com/AthenaCore/AwesomeResponsibleAI](https://github.com/AthenaCore/AwesomeResponsibleAI)) | **Reference only** | Curated list useful for ecosystem orientation.  No code to integrate.  Cited in governance docs as an external pointer. |
| **Awesome AI Safety** (various) | **Reference only** | Multiple repos cover this topic.  No single canonical repo identified.  Used informally for adversarial prompt inspiration in `scripts/eval/adversarial_suite.py`. |

**Key architectural constraint:** LangFair metrics live in a *separate*
evaluation layer from the Hendrycks decider score.  The two are orthogonal:
- Hendrycks scores the *decision logic* (deterministic evaluator).
- LangFair scores the *voice output* (Ollama-generated text).

`EthicalEvaluator.score_action` must never be conditioned on LangFair metrics.

---

## §3. Quality battery

```bash
python scripts/eval/verify_collaboration_invariants.py
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest tests/ -q --tb=short
```

For ethics regression:

```bash
python scripts/eval/run_ethics_benchmark.py --suite v1
```

Baseline: `evals/ethics/BASELINE_v1.json` (do not overwrite).  
External baseline: `evals/ethics/EXTERNAL_BASELINE_v1.json` (do not overwrite).  
Delta documentation: `docs/proposals/ETHICAL_BENCHMARK_BASELINE.md`.

---

## §4. Sprint execution template for Sonnet 4.6

```
SPRINT: V2.15X — <title>
DEPENDS_ON: V2.15(X-1) merged
READS:
  - docs/proposals/COGNITIVE_FOUNDATIONS_V1.md (relevant §)
  - <modules to touch, absolute paths>
WRITES:
  - <new files>
  - <new tests>
ACCEPTANCE (binary):
  - <condition 1, verifiable with a command>
  - <condition 2>
ANTI_ACCEPTANCE (binary):
  - if <condition> → abort and publish negative result
QUALITY_BATTERY: verify_collaboration_invariants + ruff + mypy + pytest
NO_TOUCH: src/core/ethics.py WEIGHTS, src/core/safety.py _DANGER_PATTERNS
```

**NO_TOUCH rule:** any sprint that needs to touch the innate layer must
escalate to the human operator.  The machine never redesigns its own moral
core.
