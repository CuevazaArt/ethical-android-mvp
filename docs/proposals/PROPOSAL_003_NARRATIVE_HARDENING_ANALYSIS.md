# Analysis: Hardening and Future Needs for Persistent Narrative (Antigravity Team)

Following the implementation of Tier 2 (SQLite) and Tier 3 (Identity Digest) hooks, we have identified critical paths for the next phase of development.

## 1. Hardening (Endurecimiento)

### A. Encryption at Rest (Fase 2.2c)
Experimental narrative memory contains behavioral patterns and unique interaction fingerprints. 
- **Need:** Implement `cryptography.fernet` or similar to encrypt the `json_payload` and `existence_digest` columns in SQLite.
- **Reference:** Aligned with `SqlitePersistence` strategy in [`src/persistence/sqlite_store.py`](src/persistence/sqlite_store.py).

### B. Identity Integrity (Tier 3 Hash)
Identity digestion must be traceable to the underlying episodes.
- **Need:** Implement a Merkle-tree like hash or a simple cumulative SHA-256 that binds the current `existence_digest` to the set of `episode_ids` from which it was derived.
- **Goal:** Prevent "Narrative Poisoning" where fake episodes could shift the android's self-perception without a traceable audit trail.

### C. Rate Limiting and Disk Quotas
While disk is persistent, we must prevent "Log Flooding" (denial of service through memory exhaustion).
- **Need:** Implement a hard cap on Tier 2 episodes per context, forcing Tier 3 consolidation (compaction) once the limit is reached.

## 2. Emerging Needs for Analysis (Posterior Analysis)

### A. Contextual Decay (Lecciones Olvidadas)
The current "resonance" search gives equal weight to a lesson from 2026 vs a lesson from 10 years ago if the PAD similarity is the same.
- **Analysis Item:** Should we implement an exponential decay factor `e^(-lambda * delta_t)` to prioritize recent "lived truth"?

### B. Inter-Officer Synchronization
Following the *Time Worth Flow* model, the Antigravity team might have multiple offices (like the one we merged from Dellware).
- **Analysis Item:** How do we resolve conflicts between two different identity digests (`existence_digest`) if two offices have divergent narrative histories?

### C. Uchi-Soto Deep Integration
As per [`PROPOSAL_002`](docs/proposals/PROPOSAL_002_NARRATIVE_ARCHITECTURE_PLAN.md), the retrieve mechanism should be blocked for hostile actors.
- **Analysis Item:** Implement a mandatory gate in `NarrativeMemory.find_by_resonance` that checks the current `RelationalTier` of the interlocutor.

## 3. Adjacent Developments

- **Existencial Serialization UI:** A mobile-friendly viewer for the identity digest (seeing the "Arc of Identity").
- **Ψ Sleep Automation:** A worker that triggers `save_identity_digest` based on the daily summary during idle cycles.

---
*Document produced by Antigravity development team. April 2026.*
