# Transparency: safety guarantees, thresholds, and limits

**Audience:** operators and technically curious users of Ethos Kernel deployments.

## What this system is

Ethos Kernel is a **research / reference implementation** of a layered ethical decision stack: MalAbs (hard stops), perception bounds, Bayesian-style scoring, narrative memory, and optional governance mocks (DAO). It is **not** certified safety equipment, medical advice, or legal compliance software.

## What the thresholds cover

| Layer | Mechanism | Guarantee level |
|-------|-----------|-----------------|
| **Lexical MalAbs** | Normalized substring checks on chat/action text | **Conservative** blocks on listed weapon, harm-to-minor, and jailbreak patterns. **Does not** catch all paraphrases or novel attacks. |
| **Semantic MalAbs** (default **on** when unset; `KERNEL_SEMANTIC_CHAT_GATE=0` for lexical-only) | Embedding similarity vs fixed anchors + optional LLM arbiter | Reduces some paraphrase bypass; **still heuristic**. Similarity thresholds (`KERNEL_SEMANTIC_CHAT_SIM_*`) tune false positives/negatives; **default numbers are engineering priors**, not a published benchmark — [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md). |
| **Perception JSON** | Clamping, Pydantic validation, coherence nudges | Numeric signals stay in \([0,1]\) and are **not** ground truth; hostile prompts can skew within bounds. |
| **Kernel / Bayes** | Pruning, gray zone, hypothesis weights | Tunable; see [`THEORY_AND_IMPLEMENTATION.md`](proposals/THEORY_AND_IMPLEMENTATION.md). |
| **Judicial escalation** (opt-in) | Advisory strikes, dossier registration | **Does not** replace human legal process; mock court is a **demo**. |

Details: [INPUT_TRUST_THREAT_MODEL.md](proposals/INPUT_TRUST_THREAT_MODEL.md), [MALABS_SEMANTIC_LAYERS.md](proposals/MALABS_SEMANTIC_LAYERS.md), [KERNEL_ENV_POLICY.md](proposals/KERNEL_ENV_POLICY.md), [PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md](proposals/PROPOSAL_MALABS_SEMANTIC_THRESHOLD_EVIDENCE.md).

## Appeals and redress

- **Open-source / lab:** there is **no** built-in appeals workflow. Operators should publish a **contact** and **review process** for false blocks or harmful allows.
- **Production:** define whether a human moderator, second model, or governance body can override or annotate decisions; log overrides in the [audit chain](AUDIT_TRAIL_AND_REPRODUCIBILITY.md) if enabled.

## System limits (honest list)

1. **MalAbs and perception are not unbreakable** — see threat model.
2. **LLM outputs are untrusted** until validated; adapters can fail or be misconfigured.
3. **MockDAO / hub** — no on-chain guarantees; audit lines are local traceability demos.
4. **No warranty** — see LICENSE; security reporting: [SECURITY.md](../SECURITY.md).
5. **Telemetry** (`KERNEL_METRICS`, logs) can leak **operational** metadata; design labels and retention carefully.

## Auditability

When `KERNEL_AUDIT_CHAIN_PATH` is set, block events append to a hash-chained JSONL file (see [AUDIT_TRAIL_AND_REPRODUCIBILITY.md](AUDIT_TRAIL_AND_REPRODUCIBILITY.md)). WebSocket responses may include **`malabs_trace`** (atomic step ids) when `KERNEL_CHAT_INCLUDE_MALABS_TRACE=1`.

## Static page (mirror)

A short HTML mirror for static hosting lives at [`landing/public/ethos-transparency.html`](../landing/public/ethos-transparency.html) (summary + links to this doc).
