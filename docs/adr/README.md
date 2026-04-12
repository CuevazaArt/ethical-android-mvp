# Architecture Decision Records (ADRs)

| ADR | Title |
|-----|--------|
| [0001 — packaging core boundary](0001-packaging-core-boundary.md) | Pip-installable core vs monolith repo |
| [0002 — async orchestration (future)](0002-async-orchestration-future.md) | Async orchestration for chat / kernel (stub) |
| [0003 — optional semantic chat gate](0003-optional-semantic-chat-gate.md) | HF-style embeddings vs Ollama language layer; future MalAbs complement |
| [0004 — configurable linear pole evaluator](0004-configurable-linear-pole-evaluator.md) | JSON weights for `EthicalPoles`; path to nonlinear / ML later |
| [0005 — temporal prior from consequence horizons](0005-temporal-prior-from-consequence-horizons.md) | `horizon_weeks` / long arc as numeric nudge to Bayes mixture |
| [0006 — Phase 2 core boundary + event bus](0006-phase2-core-boundary-and-event-bus.md) | Incremental `KernelEventBus`; package split deferred |
| [0007 — snapshot schema migration policy](0007-snapshot-schema-migration-policy.md) | `SCHEMA_VERSION` bumps: migrations module + golden fixtures + tests |
| [0008 — runtime observability (Prometheus + logs)](0008-runtime-observability-prometheus-and-logs.md) | Opt-in `/metrics`, JSON logs, `X-Request-ID`; no policy change |

See also [`CORE_DECISION_CHAIN.md`](../proposals/CORE_DECISION_CHAIN.md), [`LLM_STACK_OLLAMA_VS_HF.md`](../proposals/LLM_STACK_OLLAMA_VS_HF.md), [`PERCEPTION_VALIDATION.md`](../proposals/PERCEPTION_VALIDATION.md), [`TEMPORAL_PRIOR_HORIZONS.md`](../proposals/TEMPORAL_PRIOR_HORIZONS.md), [`USER_MODEL_ENRICHMENT.md`](../proposals/USER_MODEL_ENRICHMENT.md) (design proposal), and [`CHANGELOG.md`](../../CHANGELOG.md).
