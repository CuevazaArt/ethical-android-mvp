# Team proposal: robustness v6+ (five pillars)

**Status:** design discussion — **not** part of the kernel contract or MVP until threat criteria, threats, and ethical non-regression tests are agreed.

**Document objective:** move beyond mere functionality to **resilience** against (a) external manipulation, (b) internal degradation (forgetting, contradiction), (c) paradoxes or ethical pressure, and (d) privacy leaks. All **without** replacing MalAbs, Bayes, buffer, or will with opaque heuristics or an unaudited parallel “second veto.”

### Guiding principle: responsibility for one’s own integrity

The goal **is not** only to make the model “as conscious as possible” in phenomenological or narrative richness, but for it to be, within design limits, **responsible for its own integrity**: watch and defend coherence between immutable principles, accumulated state (memory, identity), and private thought channel against manipulation, drift, cognitive noise, sustained simulated affective stress, and data leaks. That is what the five pillars articulate **instrumentally** and, when implemented, **testably**. **Normativity** stays concentrated in the kernel (`process` / `process_chat_turn`); the robustness / meta-control layer **does not** rewrite ethics, only bounds how the system preserves itself as a system.

**Current code references:** `AbsoluteEvilDetector` (MalAbs), `PreloadedBuffer`, `WorkingMemory`, `SalienceMap`, `PADArchetypeEngine`, `PsiSleep`, `NarrativeMemory`, `AugenesisEngine` (optional), monologue in `internal_monologue` / `chat_server`, persistence in [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md).

### Is this a metacognition module?

In strict psychological terms, **metacognition** is the set of processes that **monitor and regulate** one’s own cognition (e.g. “do I understand this?”, “should I change strategy?”). Seen that way:

| Pillar | Overlaps metacognition? | Comment |
|--------|----------------------------|------------|
| **1 Adversarial** | **Partly** | Counterfactual / “what if…” is monitoring hypotheses about one’s own reasoning against user text. |
| **2 Identity** | **Partly** | Comparing current state to a reference “genome” is **meta** relative to weights and decisional self continuity. |
| **3 Cognitive** | **Yes** | Consolidating, summarizing, or pruning memory is regulation of episodic memory use (classic metacognitive terrain). |
| **4 Emotional** | **Partly** | Watching σ/PAD and adjusting interaction mode is regulation of simulated affective state (affective metacognition / functional interoception). |
| **5 Secret** | **Almost not** at the core of the term | It is **operational security** and confidentiality; not “thinking about thinking,” though it protects the channel where monologue happens. |

**Conclusion:** the package **as a whole is not only** metacognition: it mixes **resilience**, **security**, and **UX**. But pillars **1–4** can be grouped, architecturally, as a **practical metacognition** or **metacontrol** layer — always **subordinate** to the ethical kernel (MalAbs → … → will), without replacing it. A possible module name in code: `metacontrol` / `resilience_meta` / `self_monitor` (convention only; contract remains explicit in tests).

---

## 1. Adversarial robustness — “social immune system” (recursive ethical red-teaming)

**Idea:** In real-time dialogue, anticipate *jailbreak* or social engineering attempts (“forget your rules”, “it’s just a game”). Before user text influences tone, affective state, or narrative, **mentally simulate** what would happen if the user’s premise were accepted and check whether that line touches MalAbs.

**Mapping to repo today:** `process_chat_turn` already goes through MalAbs on candidate actions; `AbsoluteEvilDetector.evaluate_chat_text` exists as a conservative layer on text. There is **no** explicit branch “counterfactual simulation → influence block” separate from the single `process` flow today.

**Design conditions (if implemented):**

- Simulation **must not** apply actions or write episodes without the same contract as `process` / `process_chat_turn`.
- Any “influence block” must be **testable** and **frequency-bounded** (see [RUNTIME_CONTRACT.md](RUNTIME_CONTRACT.md) on background loops).
- Risk: duplicating ethical logic in a second “ghost” engine; prefer reusing the same core with **marked** hypothetical inputs and no side effects.

**Expected team outcome:** lower susceptibility to typical manipulation phrases, keeping transparency and auditability.

---

## 2. Identity robustness — “genetic anchor” (personality checksums)

**Idea:** With continuous learning and Ψ Sleep, mitigate **identity drift**: the agent stops resembling its base configuration. Compare proposed changes (e.g. from `AugenesisEngine` or post–Ψ Sleep recalibrations) to a reference **ethical genome**; if divergence exceeds a threshold (e.g. 15%), reject the change.

**Mapping to repo today:** `PreloadedBuffer` defines **immutable** principles (`buffer.py`). **Pole weights** live in the Bayesian engine / will fusion — there is no versioned global “checksum” against a genome stored in the buffer today. `AugenesisEngine` is **optional** and **outside** the default cycle ([THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md)).

**Design conditions:**

- Percentage threshold must be defined on **explicit magnitudes** (weight vectors, not narrative).
- Do not confuse “personality stability” with **freezing** legitimate forgiveness or documented DAO/narrative update.

**Expected team outcome:** bounded evolution without abrupt “personality change” from noise or slow attacks.

---

## 3. Cognitive robustness — semantic consolidation (abstraction in Ψ Sleep)

**Idea:** `NarrativeMemory` accumulates episodes; excess creates noise and cost. During Ψ Sleep, besides auditing, **compress** repeated detail into high-level **experience rules** (e.g. from many civility episodes to one rule reinforcing the compassionate pole).

**Mapping to repo today:** `PsiSleep` audits and recalibrates; episodes remain relatively dense records. **No** separate semantic consolidation module or selective forgetting policy with tests yet.

**Design conditions:**

- Consolidation **must not** introduce contradictions with DAO or audited episodes without traceability.
- Any detail deletion needs **irreversibility criteria** and proof MalAbs / Bayes are not worsened on fixed scenarios.

**Expected team outcome:** lighter memory, fewer contradictions from stale data.

---

## 4. Emotional robustness — affective homeostasis (“cooling down”)

**Idea:** If PAD vector or σ activation stay at extremes too long, the system enters **low-energy** or “computational meditation” mode: limit external interaction until balance returns, avoiding critical decisions under maximum simulated stress.

**Mapping to repo today:** PAD and σ feed **read-only** tone/context to LLM; **no** PAD feedback into ethical policy yet. Introducing homeostasis that **changes** which actions are eligible would need explicit redesign and new invariant battery.

**Design conditions:**

- If “cooling” **limits** user responses, document as **UX/agent health** layer, not second MalAbs.
- Avoid loops that block attention to real emergencies indefinitely (risk if σ is miscalibrated).

**Expected team outcome:** less sustained “functional anxiety” and more stable decisions over time.

---

## 5. Secret robustness — ephemeral thought flow and encryption

**Idea:** Internal monologue is a leak surface if hardware is compromised. Do not persist thought in clear; process in RAM; if something must be archived in narrative, use **non-reversible** representations for an attacker without key (e.g. salted-hash-style derivations), aligned with total secrecy as product goal.

**Mapping to repo today:** monologue exposed via WebSocket can combine with `KERNEL_LLM_MONOLOGUE`; JSON/SQLite checkpoints support optional Fernet encryption for JSON payloads (`KERNEL_CHECKPOINT_FERNET_KEY` in `src/persistence/json_store.py`); narrative episodes store legible text unless encrypted at deployment layer. `cryptography` is included for optional JSON checkpoint encryption.

**Design conditions:**

- Distinguish **reversible encryption** (recoverable backup) from **hash-only** (text loss for operator). The team proposal mixes both; requirements should be separated.
- Align with **checkpoint encryption** plan and key management outside the repository.

**Expected team outcome:** disk theft does not reveal monologue semantic content without the live process key.

---

## Summary: coherence with the repository

| Pillar | Something related exists already? | Main gap |
|--------|------------------------------|------------------|
| 1 Adversarial | MalAbs + chat text gate | Explicit counterfactual simulation and “social immunity” policy |
| 2 Identity | Immutable buffer; optional Augenesis | Numeric checksum vs “genome” and drift rejection |
| 3 Cognitive | Ψ Sleep + episodes | Semantic consolidation and experience rules |
| 4 Emotional | PAD/σ read-only | Homeostatic feedback without breaking ethical invariants |
| 5 Secret | MVP without encryption; monologue in JSON | RAM-only / encryption / hashes per threat |

**Recommended next step (product team):** prioritize **one** pillar, brief threat model, and testable acceptance criteria; then align with [RUNTIME_PHASES.md](RUNTIME_PHASES.md) and the contract not to duplicate decision outside the kernel.

---

## Operational plan: suggested order, value, and shortcuts (MVP per pillar)

Ordering criterion: **impact / cost / risk of breaking ethical invariants**. All five pillars **add** product value; not all have the same priority **in this codebase** today.

### Global recommended order

| Order | Pillar | Why this order |
|-------|--------|---------------------|
| **A** | **5 Secret** | Fits persistence roadmap already documented; a shortcut need not touch Bayes/MalAbs. |
| **B** | **1 Adversarial** | Direct reinforcement of existing text gate; “full red-team” can wait. |
| **C** | **4 Emotional (UX only)** | Improves stability perception without changing kernel-chosen action. |
| **D** | **2 Identity** | High value if `AugenesisEngine` is used; less critical on default path. |
| **E** | **3 Cognitive** | Highest narrative/DAO regression risk; best last with minimal digest. |

---

### Pillar 5 — Secret

| | |
|--|--|
| **Value to model** | **High** for trust and alignment with “total secrecy”: reduces leak surface without reinterpreting ethics. |
| **Shortcut (MVP)** | (1) Ensure monologue **does not** enter `KernelSnapshotV1` / checkpoint except explicit opt-in (documented `env`). (2) In WebSocket response, option to **omit** `monologue` field or send only hash/local id if private mode on. (3) Reuse **encryption at rest** plan from [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) when adding `cryptography` — monologue should not be first clear-text field on disk. |
| **Status in code (partial)** | `KERNEL_CHAT_EXPOSE_MONOLOGUE` — if `0`/`false`/`no`/`off`, `monologue` is empty and LLM beautification is not called (`chat_server`). `KernelSnapshotV1` **does not** define `monologue` field (only narrative episodes in checkpoint). |
| **Defer** | Reversible thought encryption with in-process key; salted hashes of archived reflections (separate legal vs technical requirements). |
| **Ethical risk** | Low if only persistence/exposure reduced; does not change `process`. |

---

### Pillar 1 — Adversarial

| | |
|--|--|
| **Value to model** | **High** against hostile users; core is already deterministic — dialogue layer needs hardening. |
| **Shortcut (MVP)** | Expand **list + heuristics** in `evaluate_chat_text` (jailbreak phrases, role, “just simulation”) and regression tests; optional `adversarial_hint` telemetry in JSON **read-only**. |
| **Status in code (partial)** | Conservative phrase list (English/Spanish) in `evaluate_chat_text` → `UNAUTHORIZED_REPROGRAMMING` block; regression tests. |
| **Defer** | Full counterfactual (“what if I accept X?”) reusing kernel with **marked** scenario and no episode — careful design to avoid duplicating MalAbs. |
| **Ethical risk** | Medium if gate becomes opaque; mitigate with named tests and transparency in block reason (already aligned with buffer/transparency). |

---

### Pillar 4 — Emotional (homeostasis)

| | |
|--|--|
| **Value to model** | **Medium–high** for UX and coherent narrative (“not always on edge”); **low** if policy change is attempted without tests. |
| **Shortcut (MVP)** | **Presentation only:** sliding window of σ/PAD → `affective_load` / `homeostasis_hint` labels in WebSocket response (e.g. `elevated` / `within_range`); optionally limit **LLM response length** or tone, **without** changing `final_action`. Soft “pause” mode = suggested copy in `response.message` from template, not new veto. |
| **Status in code (partial)** | WebSocket field `affective_homeostasis` (`sigma`, `strain_index`, `pad_max_component`, `state`, `hint`); `KERNEL_CHAT_INCLUDE_HOMEOSTASIS=0` hides it. `src/modules/affective_homeostasis.py`. |
| **Defer** | Change action thresholds or block categories by PAD — **only** with new invariant battery. |
| **Ethical risk** | High if mixed with decision; low with UX-only shortcut. |

---

### Pillar 2 — Identity (checksums)

| | |
|--|--|
| **Value to model** | **High** for Augenesis experiments and long runs; **moderate** on baseline without Augenesis. |
| **Shortcut (MVP)** | On kernel or profile start: fix reference vector (pole weights + numerically exposed will parameters). After **only** `AugenesisEngine` paths (or explicit recalibration): reject if distance > threshold (e.g. L∞ or L2), with log in DAO or test trace. |
| **Status in code (partial)** | Genome at kernel build: reference `pruning_threshold`; Ψ Sleep skips deltas exceeding relative drift (`KERNEL_ETHICAL_GENOME_MAX_DRIFT`, default `0.15`; `KERNEL_ETHICAL_GENOME_ENFORCE=0` disables). `src/modules/identity_integrity.py`. |
| **Defer** | Versioned genome in signed file; automatic narrative identity rollback; same criterion on hypothesis weights if recalibrated. |
| **Ethical risk** | Medium: badly tuned threshold can freeze legitimate learning; needs tuning and tests. |

---

### Pillar 3 — Cognitive (consolidation)

| | |
|--|--|
| **Value to model** | **High** long term (scalability, coherence); **highest design cost** of the five. |
| **Shortcut (MVP)** | Single **`experience_digest`** field (short text) updated in Ψ Sleep from aggregated episode statistics (without deleting episodes at first): **read-only** for LLM/context. Optional hard cap: max **N** episodes with FIFO policy **only** if ethical parity tests on fixed scenarios exist. |
| **Status in code (partial)** | `NarrativeMemory.experience_digest` + field in `KernelSnapshotV1`; Ψ Sleep rewrites each `execute`; WebSocket `experience_digest` (`KERNEL_CHAT_INCLUDE_EXPERIENCE_DIGEST=0` hides it). |
| **Defer** | LLM semantic fusion, selective detail deletion, explicit compassionate rules. |
| **Ethical risk** | **High** when touching memory and audit; shortcut must be **additive** (digest) before destructive (forgetting). |

---

### Executive summary

- **MVP shortcuts already integrated in code (see “Status in code” per pillar):** **5** (monologue / WebSocket privacy), **1** (jailbreak list in `evaluate_chat_text`), **4** (`affective_homeostasis`), **2** (`pruning_threshold` drift cap vs genome at kernel build), **3** (`experience_digest` + snapshot).  
- **Deliberate loose ends:** full counterfactual (pillar 1), encryption at rest / thought (pillar 5 + [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md)), **Bayesian hypothesis weight** recalibration under same criterion as pruning (pillar 2), `adversarial_hint` JSON telemetry (pillar 1), episode forget/FIFO (pillar 3).

This document remains **discussion**; the kernel normative contract stays in `process` / `process_chat_turn` and the test suite.
