# V11 — Distributed artificial justice & DAO escalation (design)

**Status:** design + **Phase 1** scaffolding in code (`src/modules/judicial_escalation.py`).  
**Does not replace** v9 (epistemic/generative) or v10 (operational); V11 is a **governance and social-contract** track.

**Upstream vision (V12):** The **hybrid civilization hub** — mixed tribunal, federated evolution, ethical economy, hybrid immortality registry — is documented separately as **[PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md)**. V11 remains the **concrete escalation/audit path**; V12 is **institution-scale architecture (design only)** and does not supersede V11 numbering.

## Positioning

Allowing the android to **document** and optionally **escalate** persistent owner–agent conflict toward the **MockDAO** shifts the metaphor from **User–Tool** toward an **artificial social contract**: the owner is not an unchecked dictator inside the narrative layer, but a participant whose insistence can be **audited** and (in later phases) **peer-reviewed**. The **kernel ethical pipeline** (MalAbs → Bayes → poles → will) is unchanged; V11 adds **transparency, dossiers, and ledger hooks**, not a parallel veto.

## Phase map (implementation order)

| Phase | Goal | Risk level | Repo status |
|-------|------|-------------|-------------|
| **1 — Traceability & dossier (MVP)** | Template notice + structured dossier + **local DAO audit** entry (`escalation` records). Optional WebSocket telemetry (`KERNEL_CHAT_INCLUDE_JUDICIAL`). Client opt-in `escalate_to_dao` on a chat turn. | Low — advisory + audit only | **Implemented** (baseline) |
| **2 — Escalation state machine** | Per-kernel **session strikes** (`EscalationSessionTracker`); phases `traceability_notice` → `dossier_ready` when strikes ≥ threshold; `escalate_to_dao` registers only if threshold met, else `escalation_deferred`. Env: `KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`, `KERNEL_JUDICIAL_RESET_IDLE_TURNS`. | Low–medium — UX and consent copy | **Implemented** |
| **3 — Mock “court” simulation** | `MockDAO.run_mock_escalation_court`: proposal + quadratic votes (panel, android, deterministic community) → verdict **A/B/C**; JSON `mock_court` when **`KERNEL_JUDICIAL_MOCK_COURT=1`**. Phase `mock_court_resolved`. | Medium — must stay clearly **simulated** | **Implemented** |
| **4 — Owner-facing sanctions (optional product)** | Restrict delegated agency, force `D_delib`, etc. **Only** for actions mediated by the assistant; never raw OS lockout. Requires threat model + legal review. | **High** | Not started |
| **5 — P2P ethical nodes** | Network of instances, Sybil resistance, identity. | **Very high** | Research only |
| **6 — Evidence privacy** | Encrypted dossiers, ZK proofs, selective disclosure. | **Very high** (crypto + semantics) | Research only |
| **7 — Cross-instance reputation & augenesis wake** | Global ledger, “hostile owner” query at install. | **Extreme** (privacy, GDPR, coercion) | Research only |

## Phase 1–2 (code) — behaviour

- **`KERNEL_JUDICIAL_ESCALATION=1`**: enable advisory logic (default off).
- **`KERNEL_CHAT_INCLUDE_JUDICIAL=1`**: include `judicial_escalation` in WebSocket JSON when advisory applies (default off).
- **Advisory trigger (conservative):** `decision_mode == gray_zone` and (elevated reflection strain or active premise advisory).
- **Phase 2 — session strikes:** each qualifying turn increments **strikes**; after **`KERNEL_JUDICIAL_RESET_IDLE_TURNS`** (default 2) consecutive non-qualifying turns, strikes reset. **`KERNEL_JUDICIAL_STRIKES_FOR_DOSSIER`** (default 2) is the threshold for **`dossier_ready`** and for registering a dossier when **`escalate_to_dao: true`**.
- **`escalate_to_dao: true`** before threshold: returns phase **`escalation_deferred`** (`dao_registration_blocked: true`), no ledger write.
- At or above threshold: build `EthicalDossierV1` (includes `session_strikes`), register an **`escalation`** audit line in `MockDAO` (no blockchain, no sanctions).
- **Phase 3 — mock tribunal:** if **`KERNEL_JUDICIAL_MOCK_COURT=1`**, after registration call `run_mock_escalation_court` (proposal + votes). Response includes **`mock_court`** (`verdict_code` **A** / **B** / **C**, `verdict_label`, vote totals, `disclaimer`). **Phase** becomes **`mock_court_resolved`** when the court runs; otherwise **`dao_submitted_mock`** only.

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

- [PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md](PROPOSAL_DAO_ALERTS_AND_TRANSPARENCY.md) — DAO corruption alerts: transparency vs. “guerrilla” resistance, forensic memorial vs. erasure (design)
- [PROPOSAL_OPERATIONAL_STRATEGY_V10.md](PROPOSAL_OPERATIONAL_STRATEGY_V10.md) — gray-zone diplomacy precursor
- [PROPOSAL_ETOSOCIAL_STATE_V12.md](PROPOSAL_ETOSOCIAL_STATE_V12.md) — etosocial hub / hybrid justice infrastructure (vision; V12)
- [RUNTIME_PERSISTENT.md](RUNTIME_PERSISTENT.md) — checkpoints and confidentiality
- [THEORY_AND_IMPLEMENTATION.md](THEORY_AND_IMPLEMENTATION.md) — kernel contract

*Ex Machina Foundation — V11 governance track.*
