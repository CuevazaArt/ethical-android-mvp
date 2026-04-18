# ADR 0018 — Presentation tier vs ethical core (MER / conversational UX)

**Date:** 2026-04-17  
**Status:** Proposed  
**Owners:** Cursor line (`master-Cursor`) — normative for *new* presentation-layer features; L1 may accept or amend.  
**Related:**

- [`PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md`](../proposals/PROPOSAL_MULTIMODAL_CHARM_ENGINE_DIGEST.md)
- [`PLAN_WORK_DISTRIBUTION_TREE.md`](../proposals/PLAN_WORK_DISTRIBUTION_TREE.md) (Módulo 10)
- Modules: [`prefetch_ack.py`](../../src/modules/prefetch_ack.py), [`transparency_s10.py`](../../src/modules/transparency_s10.py), [`basal_ganglia.py`](../../src/modules/basal_ganglia.py), [`llm_layer.py`](../../src/modules/llm_layer.py)

---

## Context

MER V2 (Motor de Encanto Resiliente) added **latency UX** and **affective smoothing** adjacent to the main verbal path: thalamus fusion, MalAbs edge metadata, basal-ganglia EMA on user-model charm fields, prefetch acknowledgments, transparency S10 envelopes, etc. Product language sometimes calls this “charm” or “presentation”; the kernel must not blur that into **ethical certification** or **decision authority**.

---

## Decision

1. **Ethical core (non-negotiable without explicit ADR + tests):** `KernelDecision`, MalAbs (`AbsoluteEvilDetector` + semantic gate where enabled), input trust normalization, DAO / L0 policy hooks that veto or gate *actions*, and any field that directly changes `final_action` selection for non-UX reasons.

2. **Presentation tier (conversational / operator UX):** May **condition** prompts (e.g. `weakness_line`, tone hints), emit **non-authoritative** WebSocket envelopes (`prefetch_ack`, `transparency_s10`, optional JSON mirrors), smooth **style** signals in `UserModelTracker` (`basal_ganglia`), and schedule **delays or micro-copy** that do not change the ethics outcome of a turn without a documented, tested contract.

3. **Forbidden default:** Presentation tier code **must not** override MalAbs block/allow results, silently strip semantic-gate outcomes, or bind “charm intensity” to releasing hazardous `CandidateAction`s or DAO votes unless a future ADR and tests explicitly define a **bounded** interface (see multimodal charm digest guardrail sections on operator-only surfaces and tier boundaries).

4. **Observability:** Reuse existing hooks (`verbal_llm_observability`, stream events, `GET /health` degradation fields). New presentation-only events should be **schema-versioned** and **opt-in** via `KERNEL_CHAT_INCLUDE_*` or equivalent.

---

## Consequences

- New MER-adjacent features are reviewed against this split: **UX-only** changes belong in presentation modules and chat bridge; **ethics** changes require MalAbs / decision-core review.
- Naming in code and ADRs should prefer **presentation / conversational UX** over “charm” when referring to implementation seams (digest §4).

---

## Compliance (existing MER blocks)

| MER block | Role vs this ADR |
|-----------|------------------|
| 10.1 Thalamus fusion | Sensor fusion **hints** to perception; no MalAbs bypass. |
| 10.2 MalAbs edge | **Core** — strengthens observability of the fuse, not presentation. |
| 10.3 Basal ganglia | **Presentation** — EMA on charm fields; advisory to LLM prompts. |
| 10.4 Prefetch ack | **Presentation** — fast envelope before primary completion; optional Ollama micro-phrase; fallback template. |

**Regression:** [`tests/test_mer_presentation_contract.py`](../../tests/test_mer_presentation_contract.py) — AST import boundaries for presentation modules; behavioral checks that `safety_block` + no `KernelDecision` persist when S10 / basal env flags are on; JSON omits `transparency_s10` when there is no decision object.

---

## Status transitions

Move to **Accepted** when L1 confirms alignment with consolidation / DAO-readiness docs, or when presentation-tier modules include regression tests that assert **no** mutation of blocked MalAbs results from presentation paths.
