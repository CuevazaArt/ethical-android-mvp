# Architecture Decision Records (ADRs)

| ADR | Title |
|-----|--------|
| [0001 — packaging core boundary](0001-packaging-core-boundary.md) | Pip-installable core vs monolith repo (**Accepted**) |
| [0002 — async orchestration (future)](0002-async-orchestration-future.md) | Thread offload + optional turn timeout / dedicated pool (partial; async HTTP TBD) |
| [0003 — optional semantic chat gate](0003-optional-semantic-chat-gate.md) | HF-style embeddings vs Ollama language layer; future MalAbs complement |
| [0004 — configurable linear pole evaluator](0004-configurable-linear-pole-evaluator.md) | JSON weights for `EthicalPoles`; path to nonlinear / ML later |
| [0005 — temporal prior from consequence horizons](0005-temporal-prior-from-consequence-horizons.md) | `horizon_weeks` / long arc as numeric nudge to ethical mixture weights |
| [0006 — Phase 2 core boundary + event bus](0006-phase2-core-boundary-and-event-bus.md) | Incremental `KernelEventBus`; package split deferred |
| [0007 — snapshot schema migration policy](0007-snapshot-schema-migration-policy.md) | `SCHEMA_VERSION` bumps: migrations module + golden fixtures + tests |
| [0008 — runtime observability (Prometheus + logs)](0008-runtime-observability-prometheus-and-logs.md) | Opt-in `/metrics`, JSON logs, `X-Request-ID`; no policy change |
| [0009 — ethical mixture scorer naming](0009-ethical-mixture-scorer-naming.md) | `weighted_ethics_scorer` canonical; `bayesian_engine` shim; not full Bayes |
| [0010 — poles pre-argmax modulation](0010-poles-pre-argmax-modulation.md) | Pole weights scale hypothesis valuations before mixture dot |
| [0011 — context richness pre-argmax](0011-context-richness-pre-argmax.md) | Social/locus/sigma channels modulate valuations pre-argmax |
| [0012 — Bayesian weight inference (mixture)](0012-bayesian-weight-inference-ethical-mixture-scorer.md) | Optional BMA win probabilities + feedback Dirichlet updates (ADR 0012) |
| [0013 — Hierarchical context-dependent weight inference (Level 3)](0013-hierarchical-context-weight-inference.md) | Per-context Dirichlet posteriors (Level 3) — 67 % preference satisfaction vs 33 % for global Level 2 (**Proposed**) |
| [0017 — Smartphone sensor relay bridge](0017-smartphone-sensor-relay-bridge.md) | Inline PWA + `/control/*` surface for PC ↔ phone field tests; token-bucket rate limiter; session manifest; LAN-only security (**Proposed**) |

See also [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md), [`LLM_STACK_OLLAMA_VS_HF.md`](../proposals/LLM_STACK_OLLAMA_VS_HF.md), [`PERCEPTION_VALIDATION.md`](../proposals/PERCEPTION_VALIDATION.md), [`TEMPORAL_PRIOR_HORIZONS.md`](../proposals/TEMPORAL_PRIOR_HORIZONS.md), [`USER_MODEL_ENRICHMENT.md`](../proposals/USER_MODEL_ENRICHMENT.md) (design proposal), and [`CHANGELOG.md`](../../CHANGELOG.md).
