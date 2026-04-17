# Multimodal charm engine - integration digest (Ethos Kernel)

**Status:** Design digest (P0) - not an implementation spec.

**Purpose:** Map a conversational **multimodal "charm" / UX stack** (interaction orchestration, profile registry, cultural adaptation, intent and style vectors, conditioned LLM prompts, response sculpting, gesture and expression planning, micro-behavior timing, feedback) onto **this repository's seams** so teams can extend presentation without bypassing MalAbs, input trust, DAO/L0, tests, or traceability.

**Language:** Repository integration text is English per `CONTRIBUTING.md`.

**Scope:** This digest synthesizes an informal product brief into **architecture-aligned** language. It is **not** a verbatim transcript of source material.

---

## 1. Executive summary

The source concept describes a **hybrid modular stack**: interaction orchestration, profile registry, cultural adaptation, intent and style vectors, conditioned LLM prompts, response sculpting, gesture and expression planning, micro-behavior timing, and feedback. Targets include **continuity, trust, and culturally adaptive tone** with optional **multimodal delivery**.

**Ethos Kernel fit:** Implement charm as a **presentation and planning layer** that **conditions** verbal/monologue paths and **sensor fusion** inputs, but **does not** replace `EthicalKernel.process` or silently change `KernelDecision` / `final_action` without explicit DAO/L0 policy and tests. Verbal output still passes through existing gates (MalAbs, semantic chat gate where applicable, LLM touchpoint policies).

---

## 2. Component mapping

| Concept (brief) | Repo seam | Default posture |
|-----------------|-----------|-----------------|
| Orchestration above chat | `process_chat_turn` / WebSocket bridge | Does **not** set `final_action` by default; may schedule **delays** and **UX** only |
| Profile registry | `NarrativeMemory` / session store / user model docs | Minimize PII; align with retention and `uchi_soto` |
| Cultural adaptation | Verbal templates + `KERNEL_LLM_*` policies | No stereotype ground truth; use **coarse** buckets + opt-out |
| Intent + style vectors | Prompt conditioning + lobe stubs | Vectors are **hints**, not ethics overrides |
| Conditioned LLM | `llm_layer`, `KERNEL_LLM_TP_*` | See [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) |
| Response sculpting | Verbal path variants; **not** DAO truth | Observability via `verbal_llm_observability` |
| Style vector (UX) | Prompt + optional monologue | Must not bypass MalAbs or input trust |
| Gesture / expression planner | `kernel_lobes` / narrative tier | **Presentation** only unless ADR extends motor/actuation |
| Micro-revelations / timing | Delays in bridge; **no** covert manipulation | Honor opt-out and discomfort signals |
| Feedback loop | Hierarchical updater / mixture weights | **Cannot** weaken L0 immutability or DAO quorum rules |

---

## 3. Turn flow (conceptual)

```
inputs -> profile update -> cultural blend -> intent + style vector
    -> prompt composer -> LLM variants -> sculpted script
    -> optional gesture/expression plan -> delivery + feedback
```

**Kernel alignment:** Map **inputs** to existing `sensor` / text paths; **cultural blend** and **style** feed **prompt text** and **perception hints**, not the ethics scorer directly unless a future ADR defines a bounded, tested interface. **Charm logic** may read `KernelDecision` and **perception** for context but must not **overwrite** decision outputs without governance.

---

## 4. Critiques (honest)

- **Manipulability KPIs** risk optimizing for engagement over stated operator ethics; tie metrics to **consent**, **opt-out latency**, and **harm proxies** already in repo tests/docs.
- **Naming:** "Charm" is **not** a kernel primitive; use **presentation tier** or **conversational UX** in code and ADRs to avoid implying ethics certification.
- **Demographic inference** is biased and privacy-sensitive; prefer **user-declared** coarse preferences and **explicit** cultural packs.
- **Micro-revelations** can shade into dark patterns; require **visibility** in operator logs and **user-visible** pacing controls where product allows.
- **Full multimodal stack** is parallel to perception stubs; ship **interfaces** before **depth** to avoid forked behavior between chat and sensors.

---

## 5. Guardrails

- **MalAbs + semantic gates** apply to **all** user-visible text paths that mirror chat semantics.
- **Input trust** and jailbreak fixtures remain authoritative; charm must not add unreviewed bypass strings.
- **DAO / L0:** No default coupling of "charm intensity" to **release of action** or DAO votes without explicit proposal + tests.
- **Observability:** Reuse `verbal_llm_observability` and perception coercion reports; add **narrow** events if needed (proposal-first).
- **Offline / airgap:** Respect [`PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md`](PROPOSAL_OFFLINE_MODE_TAXONOMY_AND_KNOWLEDGE_CORPUS.md) and LLM degradation matrix for safe fallbacks.

---

## 6. Phased roadmap (suggested)

| Phase | Content |
|-------|---------|
| **P0** | This digest + optional ADR stub: **presentation vs ethics core** boundary |
| **P1** | Text-only MVP on verbal path; tests; **no** `final_action` changes |
| **P2** | Metrics (continuity, discomfort, opt-out); simulation hooks |
| **P3** | Multimodal planner contract + simulation alignment |

---

## 7. Related documents

- [`PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md`](PROPOSAL_LLM_TOUCHPOINT_DEGRADATION_MATRIX.md) - precedence and safe modes
- [`PROPOSAL_LLM_INTEGRATION_TRACK.md`](PROPOSAL_LLM_INTEGRATION_TRACK.md) - integration gap register
- [`PROPOSAL_LLM_VERTICAL_ROADMAP.md`](PROPOSAL_LLM_VERTICAL_ROADMAP.md) - phased operator recipes
- [`docs/WEAKNESSES_AND_BOTTLENECKS.md`](../WEAKNESSES_AND_BOTTLENECKS.md) - honest limits
- [`PROPOSAL_SENSOR_FUSION_NORMALIZATION.md`](PROPOSAL_SENSOR_FUSION_NORMALIZATION.md) - multimodal doubt / sensor merge

---

## 8. Open questions

- **Charm intensity vs `KERNEL_LLM_*`:** single knob or per-touchpoint caps?
- **Offline harness:** mirror chat-server flag behavior vs fully local templates?
- **Minimum anonymization** for cross-session "continuity" features?
- **Simulation:** which scenarios in `tests/fixtures/` anchor charm-specific regressions?

---

## 9. Document control

- **Owner:** Cursor team (digest); L1 Antigravity for ADR if promoted.
- **Updates:** Register substantive changes in `CHANGELOG.md` under `### Cursor Team Updates`.
