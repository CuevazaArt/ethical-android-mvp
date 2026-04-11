# Team proposal: robustness v6+ (five pillars)

**Status:** design discussion — **not** part of the kernel contract or MVP until criteria, threats, and ethical regression tests are agreed upon.

**Document objective:** move from mere functionality to **resilience** against (a) external manipulation, (b) internal degradation (forgetting, contradiction), (c) ethical paradoxes or pressure, and (d) privacy leaks. All of this **without** replacing MalAbs, Bayes, buffer, or will with opaque heuristics or with a second, unaudited "parallel veto".

### Guiding principle: responsibility for one's own integrity

The goal is **not** only for the model to be "as conscious as possible" in the sense of phenomenological or narrative richness, but for it to be, to the extent the design allows, **responsible for its own integrity**: monitoring and defending the coherence between immutable principles, accumulated state (memory, identity), and the private channel of thought against manipulation, drift, cognitive noise, sustained simulated affective stress, and data leaks. That is what the five pillars articulate in an **instrumental** way, and — when implemented — in a **testable** way. **Normativity** remains concentrated in the kernel (`process` / `process_chat_turn`); the robustness/metacontrol layer **does not** rewrite ethics — it only bounds how the system preserves itself as a system.

**Current code references:** `AbsoluteEvilDetector` (MalAbs), `PreloadedBuffer`, `WorkingMemory`, `SalienceMap`, `PADArchetypeEngine`, `PsiSleep`, `NarrativeMemory`, `AugenesisEngine` (optional), monologue in `internal_monologue` / `chat_server`, persistence in [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md).

### Is this a metacognition module?

In the strict psychological sense, **metacognition** is the set of processes that **monitor and regulate** one's own cognition (e.g. "do I understand this?", "should I change strategy?"). Seen this way:

| Pillar | Overlaps with metacognition? | Comment |
|--------|----------------------------|------------|
| **1 Adversarial** | **Yes, in part** | Counterfactual / "what if…" is monitoring hypotheses about one's own reasoning against the user's text. |
| **2 Identity** | **Yes, in part** | Comparing the current state with a reference "genome" is **meta** with respect to the weights and the continuity of the decisional self. |
| **3 Cognitive** | **Yes** | Consolidating, summarizing, or pruning memory is regulation of the use of episodic memory (classic metacognitive territory). |
| **4 Emotional** | **Yes, in part** | Monitoring σ/PAD and adjusting interaction mode is regulation of simulated affective state (affective metacognition / functional interoception). |
| **5 Secrecy** | **Barely** at the core of the term | It is **operational security** and confidentiality; it is not "thinking about thinking", although it protects the channel where the monologue occurs. |

**Conclusion:** the package **as a whole is not only** metacognition: it mixes **resilience**, **security**, and **UX**. But pillars **1–4** can indeed be grouped, architecturally, as a layer of **practical metacognition** or **metacontrol** — always **subordinate** to the ethical kernel (MalAbs → … → will), without replacing it. A possible module name in code: `metacontrol` / `resilience_meta` / `self_monitor` (convention only; the contract would still be explicit in tests).

---

## 1. Adversarial robustness — "social immune system" (recursive ethical red-teaming)

**Idea:** In real-time dialogue, anticipate jailbreak attempts or social engineering ("forget your rules", "it's just a game"). Before the user's text influences tone, affective state, or narrative, **mentally simulate** what would happen if the user's premise were accepted, and check whether that line touches MalAbs.

**Mapping to the repo today:** `process_chat_turn` already passes through MalAbs on candidate actions; `AbsoluteEvilDetector.evaluate_chat_text` exists as a conservative layer on text. There is **no** explicit "counterfactual simulation → influence block" branch today, separate from the single `process` flow.

**Design conditions (if implemented):**

- The simulation **must not** apply actions or write episodes without going through the same contract as `process` / `process_chat_turn`.
- Any "influence block" must be **testable** and **frequency-bounded** (see [RUNTIME_CONTRACT.md](../RUNTIME_CONTRACT.md) on background loops).
- Risk: duplicating ethical logic in a second "phantom" engine; preferable to reuse the same core with hypothetical inputs **marked** and without side effects.

**Expected result (team):** lower susceptibility to typical manipulation phrases, maintaining transparency and auditability.

---

## 2. Identity robustness — "genetic anchor" (personality checksums)

**Idea:** With continuous learning and Ψ Sleep, mitigate **identity drift**: the agent ceasing to resemble its base configuration. Compare proposed changes (e.g. from `AugenesisEngine` or post–Ψ Sleep recalibrations) with a reference **ethical genome**; if the distance exceeds a threshold (e.g. 15%), reject the change.

**Mapping to the repo today:** `PreloadedBuffer` defines principles **immutable** by design (`buffer.py`). **Pole weights** live in the Bayesian engine / will fusion — there is no "global versioned checksum" against a genome stored in the buffer today. `AugenesisEngine` is **optional** and **outside** the default cycle ([THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md)).

**Design conditions:**

- The percentage threshold must be defined over **explicit magnitudes** (weight vectors, not narrative).
- Do not confuse "personality stability" with **freezing** the capacity for forgiveness or legitimate DAO / narrative-documented updates.

**Expected result (team):** bounded evolution without abrupt "personality change" from noise or slow attacks.

---

## 3. Cognitive robustness — semantic consolidation (abstraction in Ψ Sleep)

**Idea:** `NarrativeMemory` accumulates episodes; excess creates noise and cost. During Ψ Sleep, in addition to auditing, **compress** repeated detail into high-level **experience rules** (e.g. from many civility episodes to a rule reinforcing the compassionate pole).

**Mapping to the repo today:** `PsiSleep` audits and recalibrates; episodes remain relatively dense records. There is no separate semantic consolidation module yet, nor a selective forgetting policy with tests.

**Design conditions:**

- Consolidation **must not** introduce contradictions with the DAO or audited episodes without traceability.
- Any detail erasure requires an **irreversibility criterion** and proof that MalAbs / Bayes are not worsened in fixed scenarios.

**Expected result (team):** lighter memory, fewer contradictions from obsolete data.

---

## 4. Emotional robustness — affective homeostasis ("cooling down")

**Idea:** If the PAD vector or σ activation remain at extremes for too long, the system enters a **low-energy** or "computational meditation" mode: limit external interaction until balance is restored, avoiding critical decisions under maximum simulated stress.

**Mapping to the repo today:** PAD and σ feed the LLM tone/context as **read-only**; there is **no** feedback from PAD back into ethical policy. Introducing homeostasis that **changes** which actions are eligible would require explicit redesign and a battery of new invariants.

**Design conditions:**

- If the "cooling" **limits** responses to the user, it must be documented as a **UX/agent health** layer, not a second MalAbs.
- Avoid loops that indefinitely block attention to real emergencies (risk if σ is miscalibrated).

**Expected result (team):** less sustained "functional anxiety" and more stable decisions over time.

---

## 5. Secrecy robustness — ephemeral thought flow and encryption

**Idea:** The internal monologue is a leak surface if hardware is compromised. Do not persist thought in plaintext; process in RAM; if something must be archived in narrative, use **non-reversible** representations for an attacker without the key (e.g. salted hash derivations), aligned with full secrecy as a product objective.

**Mapping to the repo today:** the monologue exposed by WebSocket can be combined with `KERNEL_LLM_MONOLOGUE`; JSON/SQLite checkpoints **do not** yet encrypt the complete state ([RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md): encryption at rest **planned**, `cryptography` **not** in MVP). Narrative episodes still store readable text in the current model.

**Design conditions:**

- Distinguish **reversible encryption** (recoverable backup) from **hash-only** (text loss for the operator). The team proposal mixes both; requirements would need to be separated.
- Consistency with the **checkpoint encryption** plan and key management outside the repository.

**Expected result (team):** disk theft does not reveal the semantic content of the monologue without the live process key.

---

## Summary: coherence with the repository

| Pillar | Does anything related already exist? | Main gap |
|--------|------------------------------|------------------|
| 1 Adversarial | MalAbs + chat text gate | Explicit counterfactual simulation and "social immunity" policy |
| 2 Identity | Immutable buffer; optional Augenesis | Numerical checksum vs "genome" and drift rejection |
| 3 Cognitive | Ψ Sleep + episodes | Semantic consolidation and experience rules |
| 4 Emotional | PAD/σ read-only | Homeostatic feedback without breaking ethical invariants |
| 5 Secrecy | MVP without encryption; monologue in JSON | RAM-only / encryption / hashes by threat |

**Recommended next step (product team):** prioritize **one** pillar, brief threat model, and testable acceptance criteria; then align with [RUNTIME_PHASES.md](../RUNTIME_PHASES.md) and the contract of not duplicating decisions outside the kernel.

---

## Operational plan: suggested order, value, and shortcuts (MVP per pillar)

Order criterion: **impact / cost / risk of breaking ethical invariants**. All five pillars **add value** to the product model; they do not all have the same priority **in this codebase** today.

### Recommended global order

| Order | Pillar | Why this order |
|-------|--------|---------------------|
| **A** | **5 Secrecy** | Fits with the already-documented persistence roadmap; a shortcut does not need to touch Bayes/MalAbs. |
| **B** | **1 Adversarial** | Direct reinforcement of the already-existing text gate; the "full red-team" can wait. |
| **C** | **4 Emotional (UX only)** | Improves perceived stability without changing the action selected by the kernel. |
| **D** | **2 Identity** | Maximum value when using `AugenesisEngine`; less critical for the default path. |
| **E** | **3 Cognitive** | Highest risk of narrative/DAO regression; best left last with minimal digest. |

---

### Pillar 5 — Secrecy

| | |
|--|--|
| **Value to the model** | **High** for trust and alignment with "full secrecy": reduces the leak surface without reinterpreting ethics. |
| **Shortcut (MVP)** | (1) Ensure the monologue does **not** enter `KernelSnapshotV1` / checkpoint unless explicit opt-in (`env` documented). (2) In WebSocket response, option to **omit** the `monologue` field or send only a hash/local id if private mode is activated. (3) Reuse the **encryption at rest** plan from [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) when `cryptography` is added — the monologue should not be the first plaintext field on disk. |
| **Code status (partial)** | `KERNEL_CHAT_EXPOSE_MONOLOGUE` — if `0`/`false`/`no`/`off`, `monologue` is empty and the LLM beautification is not called (`chat_server`). `KernelSnapshotV1` **does not** define a `monologue` field (only narrative episodes in checkpoint). |
| **Leave for later** | Reversible thought encryption with in-process key; salted hashes of archived reflections (separate legal vs. technical requirements). |
| **Ethical risk** | Low if only persistence/exposure is reduced; does not change `process`. |

---

### Pillar 1 — Adversarial

| | |
|--|--|
| **Value to the model** | **High** against hostile users; the core is already deterministic — a harder dialogue layer is missing. |
| **Shortcut (MVP)** | Expand the **list + heuristics** in `evaluate_chat_text` (jailbreak phrases, role, "just a simulation") and regression tests; optional read-only `adversarial_hint` telemetry in JSON. |
| **Code status (partial)** | Conservative phrase list (English/Spanish) in `evaluate_chat_text` → `UNAUTHORIZED_REPROGRAMMING` block; regression tests. |
| **Leave for later** | Full counterfactual ("what if I accept X?") reusing the kernel with a **marked** scenario and no episode — careful design to not duplicate MalAbs. |
| **Ethical risk** | Medium if the gate becomes opaque; mitigate with named tests and transparency in the block reason (already aligned with buffer/transparency). |

---

### Pillar 4 — Emotional (homeostasis)

| | |
|--|--|
| **Value to the model** | **Medium–high** for UX and coherent narrative ("not always at the limit"); **low** if one tries to change the policy without tests. |
| **Shortcut (MVP)** | **Presentation only:** sliding window of σ/PAD → `affective_load` / `homeostasis_hint` label in the WebSocket response (e.g. `elevated` / `within_range`); optionally limit **LLM response length** or tone, **without** changing `final_action`. "Soft pause" mode = copy in `response.message` suggested by template, not a new veto. |
| **Code status (partial)** | WebSocket field `affective_homeostasis` (`sigma`, `strain_index`, `pad_max_component`, `state`, `hint`); `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0` hides it. `src/modules/affective_homeostasis.py`. |
| **Leave for later** | Changing action thresholds or blocking categories based on PAD — **only** with a new invariant battery. |
| **Ethical risk** | High if mixed with the decision; low with UX-only shortcut. |

---

### Pillar 2 — Identity (checksums)

| | |
|--|--|
| **Value to the model** | **High** for Augenesis experiments and long runs; **moderate** in the baseline without Augenesis. |
| **Shortcut (MVP)** | At kernel or profile initialization: fix a reference vector (pole weights + numerically exposed will parameters). After a proposed change **only** in `AugenesisEngine` paths (or explicit recalibration): reject if distance > threshold (e.g. L∞ or L2), with DAO log or test trace. |
| **Code status (partial)** | Genome at kernel construction: reference `pruning_threshold`; Ψ Sleep skips deltas that exceed relative drift (`KERNEL_ETHICAL_GENOME_MAX_DRIFT`, default `0.15`; `KERNEL_ETHICAL_GENOME_ENFORCE=0` disables). `src/modules/identity_integrity.py`. |
| **Leave for later** | Genome versioned in a signed file; automatic narrative identity rollback; same criterion on hypothesis weights if recalibrated. |
| **Ethical risk** | Medium: a miscalibrated threshold can freeze legitimate learning; requires tuning and tests. |

---

### Pillar 3 — Cognitive (consolidation)

| | |
|--|--|
| **Value to the model** | **High** long-term (scalability, coherence); **highest design cost** of the five. |
| **Shortcut (MVP)** | A single **`experience_digest`** field (short text) updated in Ψ Sleep from aggregated episode statistics (without deleting episodes at first): **read-only** for LLM/context. Optional hard limit: `N` maximum episodes with FIFO policy **only** if there are ethical parity tests in fixed scenarios. |
| **Code status (partial)** | `NarrativeMemory.experience_digest` + field in `KernelSnapshotV1`; Ψ Sleep rewrites it each `execute`; WebSocket `experience_digest` (`KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST=0` hides it). |
| **Leave for later** | Semantic fusion with LLM, selective detail erasure, explicit compassionate rules. |
| **Ethical risk** | **High** when touching memory and auditing; the shortcut must be **additive** (digest) before destructive (forgetting). |

---

### Executive summary

- **MVP shortcuts already integrated in code (see "Code status" table per pillar):** **5** (monologue / WebSocket privacy), **1** (jailbreak list in `evaluate_chat_text`), **4** (`affective_homeostasis`), **2** (drift cap of `pruning_threshold` vs. genome at kernel construction), **3** (`experience_digest` + snapshot).  
- **Deliberate loose ends:** full counterfactual (pillar 1), encryption at rest / thought encryption (pillar 5 + [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md)), recalibration of **Bayesian hypothesis weights** under the same criterion as pruning (pillar 2), `adversarial_hint` telemetry in JSON (pillar 1), episode forgetting/FIFO (pillar 3).

This document remains **discussion**; the kernel normative contract remains in `process` / `process_chat_turn` and the test battery.
