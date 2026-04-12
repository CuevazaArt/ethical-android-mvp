# ADR 0011 — Social / sympathetic / locus texture before mixture argmax

## Status

Accepted — April 2026

## Context

[ADR 0010](0010-poles-pre-argmax-modulation.md) adds optional **pole** modulation of hypothesis valuations before argmax. Other early pipeline modules (**Uchi-Soto** trust/caution, **sympathetic** `sigma`, **locus** dominance) already run **before** scoring but previously only influenced **mode** and **post-hoc** narrative.

## Decision

1. **`PreArgmaxContextChannels`** (trust, caution, sigma, dominant_locus) maps to **small** util/deon/virtue multipliers via **`context_hypothesis_multipliers`** — geometric mean 1.0, typical per-slot deviation **well under ±3%**.
2. **`KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX=1`:** `EthicalKernel.process` fills `WeightedEthicsScorer.pre_argmax_context_modulators` before `evaluate`; default **off**.
3. **Ordering:** valuations are scaled by **pole multipliers first**, then **context** multipliers (when both enabled).
4. **Ethics:** MalAbs and mixture still gate behavior; this path adds **texture**, not unbounded preference injection.

## Consequences

- Mass studies can log `context_richness_pre_argmax` alongside poles for attribution.
- Combined with poles, reference agreement may shift — expected in sensitivity runs.

## Related

- [ADR 0010](0010-poles-pre-argmax-modulation.md), [`PROPOSAL_MILLION_SIM_EXPERIMENT.md`](../proposals/PROPOSAL_MILLION_SIM_EXPERIMENT.md)
