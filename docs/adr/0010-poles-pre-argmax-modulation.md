# ADR 0010 — Optional pole modulation before mixture argmax

## Status

Accepted — April 2026

## Context

Ethical **poles** (compassionate / conservative / optimistic) historically evaluated only the **chosen** action after `WeightedEthicsScorer` picked a winner — useful for narrative multipolar labels but **not** for “personality” shaping behavior.

Operators and experiments need an **opt-in** path where pole base weights **scale the three hypothesis valuations** (util / deon / virtue) **before** `dot(hypothesis_weights, valuations)`, so the same mixture weights can yield different argmax outcomes under different pole settings.

## Decision

1. **`WeightedEthicsScorer.pre_argmax_pole_weights`:** optional `dict[str, float]`; when set, valuations are multiplied by `pole_hypothesis_multipliers(...)` (geometric-mean–normalized) before the mixture dot product. Uncertainty uses the same scaled valuations for variance.
2. **Activation:** set environment variable **`KERNEL_POLES_PRE_ARGMAX=1`**. `EthicalKernel.process` copies `self.poles.base_weights` into `self.bayesian.pre_argmax_pole_weights` before `evaluate`, or clears the field when the env is off.
3. **Default:** **off** — preserves existing production behavior unless explicitly enabled.
4. **Risks (documented):** can **dominate** the mixture if pole axes are extreme; may **reorder** actions in ways that surprise maintainers of fixtures designed under pole-as-narration-only. Use for **research / sandbox / mass studies**, not silent deployment.

## Consequences

- Mass experiments can sweep poles **and** mixture with pre-argmax modulation to measure real behavioral diversity.
- Fixture **reference_action** agreement may **drop** when this flag is on — that is expected, not a regression by itself.

## Related

- [ADR 0009](0009-ethical-mixture-scorer-naming.md) — mixture is not full Bayesian inference.
- [`docs/proposals/README.md`](../proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md) — protocol v3 and frontier scenarios.
