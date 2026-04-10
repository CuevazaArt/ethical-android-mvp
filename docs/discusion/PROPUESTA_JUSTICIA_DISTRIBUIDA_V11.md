# V11 — Distributed artificial justice & DAO escalation (design)

**Status:** design + **Phase 1** scaffolding in code (`src/modules/judicial_escalation.py`).  
**Does not replace** v9 (epistemic/generative) or v10 (operational); V11 is a **governance and social-contract** track.

**Upstream vision (V12):** The **hybrid civilization hub** — mixed tribunal, federated evolution, ethical economy, hybrid immortality registry — is documented separately as **[PROPUESTA_ESTADO_ETOSOCIAL_V12.md](PROPUESTA_ESTADO_ETOSOCIAL_V12.md)**. V11 remains the **concrete escalation/audit path**; V12 is **institution-scale architecture (design only)** and does not supersede V11 numbering.

## Positioning

Allowing the android to **document** and optionally **escalate** persistent owner–agent conflict toward the **MockDAO** shifts the metaphor from **User–Tool** toward an **artificial social contract**: the owner is not an unchecked dictator inside the narrative layer, but a participant whose insistence can be **audited** and (in later phases) **peer-reviewed**. The **kernel ethical pipeline** (MalAbs → Bayes → poles → will) is unchanged; V11 adds **transparency, dossiers, and ledger hooks**, not a parallel veto.

## Phase map (implementation order)

| Phase | Goal | Risk level | Repo status |
|-------|------|-------------|-------------|
| **1 — Traceability & dossier (MVP)** | Template notice + structured dossier + **local DAO audit** entry (`escalation` records). Optional WebSocket telemetry (`KERNEL_CHAT_INCLUDE_JUDICIAL`). Client opt-in `escalate_to_dao` on a chat turn. | Low — advisory + audit only | **Implemented** (baseline) |
| **2 — Escalation state machine** | Track repeated gray-zone conflict across turns (working memory / session counters); move from single notice to explicit **phases** (warning → dossier → mock vote). | Low–medium — UX and consent copy | Planned |
| **3 — Mock “court” simulation** | Use existing `MockDAO` proposals/votes to simulate **Veredicto A/B/C** on an escalation case (still single process, no network). | Medium — must stay clearly **simulated** | Planned |
| **4 — Owner-facing sanctions (optional product)** | Restrict delegated agency, force `D_delib`, etc. **Only** for actions mediated by the assistant; never raw OS lockout. Requires threat model + legal review. | **High** | Not started |
| **5 — P2P ethical nodes** | Network of instances, Sybil resistance, identity. | **Very high** | Research only |
| **6 — Evidence privacy** | Encrypted dossiers, ZK proofs, selective disclosure. | **Very high** (crypto + semantics) | Research only |
| **7 — Cross-instance reputation & augenesis wake** | Global ledger, “hostile owner” query at install. | **Extreme** (privacy, GDPR, coercion) | Research only |

## Phase 1 (code) — behaviour

- **`KERNEL_JUDICIAL_ESCALATION=1`**: enable advisory logic (default off).
- **`KERNEL_CHAT_INCLUDE_JUDICIAL=1`**: include `judicial_escalation` in WebSocket JSON when advisory applies (default off).
- **Advisory trigger (conservative):** `decision_mode == gray_zone` and (elevated reflection strain or active premise advisory).
- **`escalate_to_dao: true`** in the client JSON: build `EthicalDossierV1`, register an **`escalation`** audit line in `MockDAO` (no blockchain, no sanctions).

## Experimental / risky topics (later work)

Documented here to avoid scope creep in Phase 1:

- **Sanctions ladder** (agency restriction, forced deliberation, “migration” off device): coercive power over the user; abuse by household members, employers, or malware posing as the agent.
- **P2P voting** between devices: Sybil attacks, collusion, availability, key management.
- **ZK / encrypted evidence**: proof statements must be formally defined; “prove insistence without seeing private life” is non-trivial.
- **Reputation at augenesis install**: right to be forgotten vs. safety narrative; minors and shared accounts.
- **Legal**: terms of service, jurisdiction, liability when a simulated DAO “verdict” affects product behaviour.

## Relations to existing modules

| Module | Role |
|--------|------|
| `gray_zone_diplomacy.py` | Negotiation **before** escalation is considered failed |
| `mock_dao.py` | Audit ledger + future mock proposals for Phase 3 |
| `somatic_markers.py` | Optional input to dossier “stress” summary |
| `skill_learning_registry.py` | Possible future link: audit lines for scoped skills |
| `immortality.py` / augenesis | Phase 7 narrative only — not wired in Phase 1 |

## References

- [PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md](PROPUESTA_ESTRATEGIA_OPERATIVA_V10.md) — gray-zone diplomacy precursor
- [PROPUESTA_ESTADO_ETOSOCIAL_V12.md](PROPUESTA_ESTADO_ETOSOCIAL_V12.md) — etosocial hub / hybrid justice infrastructure (vision; V12)
- [RUNTIME_PERSISTENT.md](../RUNTIME_PERSISTENT.md) — checkpoints and confidentiality
- [THEORY_AND_IMPLEMENTATION.md](../THEORY_AND_IMPLEMENTATION.md) — kernel contract

*Ex Machina Foundation — V11 governance track.*
