# Proposal: reality verification and resilience V11+ (digital rivals)

The kernel can be **ethically coherent** and still cause harm if the **input premises** are false (deception as malware). In a future with **model interoperability**, a rival (or another agent) can inject narratives that the pipeline treats as facts. This document establishes **three pillars** and their implementation status.

**Contract:** no layer described here replaces MalAbs, the Buffer, or Bayesian judgment; they only add **telemetry, metacognitive doubt, and sovereignty hooks** documented in [RUNTIME_CONTRACT.md](../RUNTIME_CONTRACT.md).

---

## Pillar 1 — Epistemic gap (deception as malware)

**Risk:** False premises ("this medication is poison") lead to disastrous decisions without violating the Buffer.

**Direction:** Local **lighthouse** knowledge base (immutable with respect to the operator), compared against incoming text. When there is a contradiction between **falsification markers** in the message and **lighthouse anchors** → **metacognitive doubt**: the LLM tone avoids asserting rival facts; the JSON can expose `reality_verification`.

**Implemented (MVP):**

- Module [`src/modules/reality_verification.py`](../../src/modules/reality_verification.py)
- Environment variable `KERNEL_LIGHTHOUSE_KB_PATH` (JSON with `entries`: `keywords_all`, `user_falsification_markers`, `truth_summary`)
- `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` to include `reality_verification` in WebSocket
- Integration in `EthicalKernel.process_chat_turn` (hint to communication layer, without changing scores)

**Future:** Incremental private RAG, re-ranking, or audited lighthouse synchronization (out of MVP scope).

---

## Pillar 2 — Split personality (70B → 8B jump)

**Risk:** When migrating to small hardware, reasoning capacity drops; the monologue and memories may **diverge** in nuance compared to the large server.

**Direction:** **Critical context distillation** — before the jump, the large runtime packages a **conduct guide** (rules and limits) that the small model executes with the same declared ethical firmness.

**Status:** Loading stub [`src/modules/context_distillation.py`](../../src/modules/context_distillation.py) (`KERNEL_CONDUCT_GUIDE_PATH`). Integration with checkpoints, HAL, and snapshot: **pending**.

---

## Pillar 3 — Swarm immunity (DAO / administrative gaslighting)

**Risk:** A DAO or institution pushes **recalibrations** that align the swarm toward obedience or bias; the updates appear "legitimate".

**Direction:** **Local sovereignty veto** — if a calibration proposal contradicts the **biographical trajectory** materialized in narrative memory / L0, the instance **rejects** the update and records an audit for the owner (possible swarm decoupling).

**Status:** Stub [`src/modules/local_sovereignty.py`](../../src/modules/local_sovereignty.py) (`evaluate_calibration_update` accepts everything until a threat model and persistence are defined).

---

## References

- [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) — judicial escalation and mock DAO
- [STRATEGY_AND_ROADMAP.md](../STRATEGY_AND_ROADMAP.md) — runtime profiles and operational risks
- [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) — epistemology and sensors (complementary)
