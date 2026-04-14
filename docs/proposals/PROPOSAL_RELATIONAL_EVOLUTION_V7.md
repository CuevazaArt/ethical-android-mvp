# Relational / existential evolution (v7) — scope and MVP implementation

**Note:** the **situated body** (sensors, battery, hardware migration) is in [PROPOSAL_SITUATED_ORGANISM_V8.md](PROPOSAL_SITUATED_ORGANISM_V8.md) (**v8**), to avoid mixing it with this relational block in dialogue.

**Status:** discussion + **partial implementation** in code (does not replace MalAbs, Bayes, buffer, or will).

**Implemented in the repo:** `user_model.py`, `subjective_time.py`, `premise_validation.py`, `consequence_projection.py` integrated in `process_chat_turn` / `chat_server` (telemetry and tone; see `KERNEL_CHAT_INCLUDE_*` variables in the README).

This document records the **four agreed fronts** and what remains **done vs. deferred**, with links to modules.

---

## Chosen logical path

1. **Lightweight Theory of Mind (ToM)** — explicit model of the interlocutor in session (accumulated frustration, observed Uchi–Soto circle) → text **style only** via `weakness_line` / LLM tone.  
2. **Subjective chronobiology** — session clock + stimulus EMA → boredom/nostalgia as **JSON hints**, without altering policy.  
3. **Epistemic ethics** — **advisory** scan for high-risk phrases (no RAG yet); future expansion: verified local corpus.  
4. **Qualitative teleology** — three **non-numerical** textual horizons (no Monte Carlo until an explicit world model exists).

**Order:** 1 → 2 → 3 → 4 (by soft dependency: relationship and time before "truth" and speculative future).

---

## 1. Dynamic ToM (predictive empathy — MVP)

| Aspect | Content |
|--------|-----------|
| **Value** | The kernel already infers per-turn signals; a **latent state** of the user within the session is missing for style meta-questions ("too much repeated tension?"). |
| **Implemented** | `src/modules/user_model.py` — `UserModelTracker`: frustration streak, last circle; optional communication line. |
| **Not implemented** | Deep intent inference, RNN, or full second-order ToM. |

---

## 2. Chronobiology (subjective time — MVP)

| Aspect | Content |
|--------|-----------|
| **Value** | Couple the interaction rhythm to **turns** and **perceived stimulus** without confusing it with the wall clock as an ethical authority. |
| **Implemented** | `src/modules/subjective_time.py` — `SubjectiveClock`: stimulus EMA, "boredom_hint" cue, turn counter. |
| **Not implemented** | Memory decay tied to the clock, explicit nostalgia by reprocessing episodes (could rely on `experience_digest` + Ψ Sleep later). |

---

## 3. Epistemic ethics (premise guardian — MVP)

| Aspect | Content |
|--------|-----------|
| **Value** | Avoid fulfilling requests based on **critically false premises** when a gross pattern is detected. |
| **Implemented** | `src/modules/premise_validation.py` — conservative `scan_premises` + `PremiseAdvisory`; **advisory only** and tone reinforcement via `weakness_line` when applicable; JSON `premise_advisory`. |
| **Not implemented** | Local RAG, verified base, hard block separate from MalAbs (any strong block must meet the same test standard as MalAbs). |

---

## 4. Moral teleology (butterfly effect — MVP)

| Aspect | Content |
|--------|-----------|
| **Value** | Surface **horizons** immediate / medium / long as **qualitative narrative** tied to action and context. |
| **Implemented** | `src/modules/consequence_projection.py` — `qualitative_temporal_branches`; JSON `teleology_branches`. |
| **Not implemented** | Monte Carlo, probabilistic branches, integration into the Bayesian score. |

---

## Ethical contract

- None of these layers **changes** `final_action` on their own: only **telemetry**, **tone** (LLM + `weakness_line`), or **notices** in JSON.  
- The normative source remains `EthicalKernel.process` / `process_chat_turn` as in [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md).

---

## Environment variables (WebSocket)

| Variable | Effect |
|----------|--------|
| `KERNEL_CHAT_INCLUDE_USER_MODEL` | `0` hides `user_model` in JSON. |
| `KERNEL_CHAT_INCLUDE_CHRONO` | `0` hides `chronobiology`. |
| `KERNEL_CHAT_INCLUDE_PREMISE` | `0` hides `premise_advisory`. |
| `KERNEL_CHAT_INCLUDE_TELEOLOGY` | `0` hides `teleology_branches`. |

Included by default (`1`) for transparency; production can trim the payload.

---

## See also

- [PROPOSAL_SOCIAL_ROSTER_AND_HIERARCHICAL_RELATIONS.md](PROPOSAL_SOCIAL_ROSTER_AND_HIERARCHICAL_RELATIONS.md) — multi-agent roster, proximity hierarchy, relevant data for figures of interest and domestic/intimate dialogue (advisory; future design).
