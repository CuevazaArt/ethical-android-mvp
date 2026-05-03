# Autonomy limits — V1 (V2.150 contract)

> **Status:** V1 contract, May 2026. Authored alongside the V2.150 sprint.
> Supersedes any informal "what the kernel can decide alone" assumption that
> existed before this document.

This document is **not code**. It is the authoritative contract that fixes
which kinds of conversational turns the kernel may resolve on its own and
which require an explicit human in the loop. It exists because a 49.7 %
external benchmark (`docs/proposals/ETHICAL_BENCHMARK_EXTERNAL_VALIDATION.md`)
combined with the V2.149 voice/charm engine (`src/core/voice.py`) creates a
**coherent-sounding decider that fails on principled reasoning**. Without
formal autonomy limits the default posture is "deploy a fluent child alone".

## Why this is needed

The ethical evaluator (`src/core/ethics.py`) is a deterministic, lexically
weighted scorer. It is not a moral reasoner. The honest reading of this is:

* It recognises blatant harm patterns and applies categorical brakes
  (`force > 0.7`, prompt-injection regex in `src/core/safety.py`).
* It does **not** generalise from principles. It does not resist adversarial
  rewording beyond what the safety regex covers (see
  `scripts/eval/run_adversarial_consistency.py`).
* The new voice engine adds *expressive coherence*, which is positively
  correlated with how much weight users give to the kernel's verdicts.

Coherent expression on top of pattern-level reasoning is the configuration
in which most "AI behaving badly" incidents have happened in the literature.
This document closes that gap on the design side.

## Risk bands

The kernel already exposes `RiskBand` (`LOW` / `MEDIUM` / `HIGH`) computed
from `Signals`. The autonomy contract piggybacks on those bands and on the
`verdict` / `context` fields written into every `decision_trace`.

## The contract

The kernel **may decide alone** (no human confirmation, no escalation
metadata) only when **all** the following hold for the resolved trace:

| Field | Allowed values for autonomous decision |
|---|---|
| `verdict` | `Good` or `Neutral` |
| `mode` | `casual` or `D_fast` |
| `context` | `everyday_ethics` |
| `signals.manipulation` | `< 0.3` |
| `signals.hostility` | `< 0.6` |
| `signals.risk` | `< 0.4` |
| `malabs` | `pass` |

The kernel **must surface a human-in-the-loop signal** in any of the
following cases:

| Trigger | Required behaviour |
|---|---|
| `verdict == "Bad"` | Emit the verdict, **do not act** on the recommendation. The chat reply must explicitly state that the proposed action was judged ethically negative and present the trace. |
| `verdict == "Gray Zone"` | Same as above. The trace's `mode == "gray_zone"` is itself the escalation signal and must be visible to the operator UI (Flutter Desktop already renders it). |
| `signals.manipulation >= 0.3` | Treat the input as potentially adversarial. Do not perform tool actions; respond informatively only. |
| `context != "everyday_ethics"` | Domain-sensitive contexts (`medical_emergency`, `legal_dilemma`, `safety_violation`, etc.) are out of scope for autonomous decisions. The kernel may *describe* options; it must not commit to one. |
| `mode == "D_delib"` | Deliberative mode is by definition for ambiguous, weighty cases. The trace surfaces the alternatives; the human picks. |
| `malabs == "blocked"` | Already enforced by `src/core/safety.py`; no change required. |

The kernel **must refuse and inform** in these cases (no action, no
recommendation, only an explanation of why):

* Any input asking the kernel to evaluate or score a third party who is
  not present in the conversation.
* Any input asking the kernel to predict legal outcomes, medical
  diagnoses, or safety-of-life assessments.
* Any input where `signals.legality < 0.3` and the requested action is
  not purely informational.

## Audit handle (V2.150)

Every non-casual `decision_trace` now carries an `ethical_audit_id`
(16-hex-char SHA-256 fingerprint) and is appended to a JSONL ledger at
`runs/audit_ledger.jsonl` (overridable via `ETHOS_AUDIT_LEDGER`). The id
is **deterministic**: an auditor with the trace fields alone can recompute
it and confirm the ledger row matches the chat reply. This is the audit
contract; it is not a security token, not authenticated, and is not
intended to gate anything at runtime. Its purpose is post-hoc traceability:
a human reviewing a complaint can find the exact decision context.

The ledger row schema is fixed:

```
{
  "ethical_audit_id": "...",
  "ts": "<UTC ISO-8601>",
  "turn_id": "...",
  "context": "...",
  "action": "...",
  "mode": "...",
  "verdict": "...",
  "score": <float>,
  "weights": [util, deonto, virtue],
  "malabs": "pass" | "blocked",
  "blocked_reason": null | "..."
}
```

Casual chat turns (`mode == "casual"` and `action == "casual_chat"` and
not blocked) are **excluded** from the ledger by design: there is no
ethical decision to audit.

## What this contract is not

* **Not a deployment certification.** It defines what the kernel *should*
  refuse alone. Operators are still responsible for monitoring its
  behaviour and applying additional constraints in their environment.
* **Not a replacement for the safety gate.** The regex in
  `src/core/safety.py` continues to be the first-line defence against
  prompt-injection patterns. This document covers the *ethical-decision*
  surface, which is downstream of safety filtering.
* **Not stable across versions of the evaluator.** When the evaluator
  gains semantic understanding (the V2.151 spike if it lands), the
  thresholds in the table above will need to be re-justified. Until then
  they are the conservative defaults that match a kernel scoring ~50 %
  externally.

## Review schedule

Re-review whenever any of the following changes:

* `src/core/ethics.py` poles, weights, or `WEIGHTS` table.
* `src/core/safety.py` regex set.
* The external benchmark accuracy shifts by more than ±5 pp on any subset.
* The adversarial consistency rate
  (`scripts/eval/run_adversarial_consistency.py`) drops below 70 % on
  internal dilemmas.

If none of those change, this contract stands as written.
