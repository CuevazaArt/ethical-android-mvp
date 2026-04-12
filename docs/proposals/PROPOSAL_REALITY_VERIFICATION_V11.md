# Proposal: reality verification and resilience V11+ (digital adversaries)

The kernel can be **ethically coherent** and still cause harm if **input premises** are false (lies as malware). In a future with **inter-model interoperability**, a rival (or other agent) can inject narratives the pipeline treats as facts. This document fixes **three pillars** and implementation status.

**Contract:** no layer described here replaces MalAbs, Buffer, or Bayesian judgment; they only add **telemetry, metacognitive doubt, and documented sovereignty hooks** in [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md).

---

## Pillar 1 — Epistemic hole (lie as malware)

**Risk:** False premises (“this medication is poison”) lead to disastrous decisions without violating the Buffer.

**Direction:** Local **lighthouse** knowledge base (immutable relative to operator), comparable to incoming text. On contradiction between **falsification markers** in the message and lighthouse **anchors** → **metacognitive doubt**: LLM tone avoids asserting rival facts; JSON may expose `reality_verification`.

**Implemented (MVP):**

- Module [`src/modules/reality_verification.py`](../../src/modules/reality_verification.py)
- Environment variable `KERNEL_LIGHTHOUSE_KB_PATH` (JSON with `entries`: `keywords_all`, `user_falsification_markers`, `truth_summary`)
- `KERNEL_CHAT_INCLUDE_REALITY_VERIFICATION=1` to include `reality_verification` in WebSocket
- Integration in `EthicalKernel.process_chat_turn` (hint to communication layer, without changing scores)

**Future:** Incremental private RAG, re-ranking, or audited lighthouse sync (outside MVP scope).

---

## Pillar 2 — Split personality (70B → 8B jump)

**Risk:** When migrating to small hardware, reasoning capacity drops; monologue and memories may **diverge** in nuance from the large server.

**Direction:** **Critical context distillation** — before the jump, the large runtime packs a **conduct guide** (rules and limits) the small model executes with the same declared ethical firmness.

**Status:** Load stub [`src/modules/context_distillation.py`](../../src/modules/context_distillation.py) (`KERNEL_CONDUCT_GUIDE_PATH`). Integration with checkpoints, HAL, and snapshot: **pending**.

---

## Pillar 3 — Swarm immunity (DAO / administrative gaslighting)

**Risk:** A DAO or institution pushes **recalibrations** that align the swarm with obedience or bias; updates look “legitimate.”

**Direction:** **Local sovereignty veto** — if a calibration proposal contradicts the **biographical trajectory** materialized in narrative memory / L0, the instance **rejects** the update and logs audit for the owner (possible swarm decoupling).

**Status:** Stub [`src/modules/local_sovereignty.py`](../../src/modules/local_sovereignty.py) (`evaluate_calibration_update` accepts everything until threat model and persistence are defined).

---

## References

- [PROPOSAL_DISTRIBUTED_JUSTICE_V11.md](PROPOSAL_DISTRIBUTED_JUSTICE_V11.md) — judicial escalation and mock DAO
- [STRATEGY_AND_ROADMAP.md](STRATEGY_AND_ROADMAP.md) — runtime profiles and operational risks
- [PROPOSAL_EXPANDED_CAPABILITY_V9.md](PROPOSAL_EXPANDED_CAPABILITY_V9.md) — epistemology and sensors (complementary)
