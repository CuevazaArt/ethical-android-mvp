# Proposal 011: DAO Calibration Pipeline & Boundary Safety (Phase 7 Finalization)

**Status:** Executed (April 2026)
**Initiator:** Antigravity Team
**Related Specs:** `PROPOSAL_009_DISTRIBUTED_JUSTICE_AND_BLOCKCHAIN_DAO.md`, `PROPOSAL_010_CRITIQUE_SYNTESIS_AND_ALIGNMENT.md`

## 1. Objective
This increment connects the **MockDAO** (and by extension the future blockchain execution paths from Phase 6/8) directly into the **Bayesian Mixture Averaging (BMA)** system. Alongside this connection, it enforces rigid **Boundary Safety** mathematics to protect the core invariants (Absolute Evil prevention, legal duty compliance) from radicalization.

## 2. The Feedback Extraction Pipeline (DAO → Bayesian Engine)

### The Mechanism
Previously, the `FeedbackCalibrationLedger` only ingested data from local operator chat via `record_operator_feedback()`. During Phase 7, we established an extraction channel: `MockDAO.extract_community_feedback()`.

1. **Extraction**: The MockDAO sweeps its recent history (audit records, open proposals, escalation dossiers).
2. **Translation**: It translates these distributed events into normalized labels (`approve`, `dispute`, `harm_report`):
   - Approved proposals = `approve`
   - Rejected proposals & Judicial Escalations = `dispute`
   - Solidarity Alerts containing "harm" = `harm_report`
3. **Injection**: During the `EthicalKernel.execute_sleep()` routine (Psi Sleep), these community judgments are injected into the kernel's local `feedback_ledger` under the `DAO_community_consensus` decision regime.
4. **Learning**: The engine updates the Dirichlet posterior target weights, permanently learning from the collective hive-mind of the swarm.

### Why this matters
This moves the android from **Autonomy Level 2** (obeying a local operator + pre-loaded rules) toward **Sovereignty** — its ethical priors are dynamically recalibrated by a distributed network of peers and verified humans (the DAO).

## 3. Boundary Safety (The Math Hard-Caps)

Because the system now absorbs feedback autonomously from a distributed network, it is vulnerable to **Computational Radicalism** or deliberate poisoning attacks (e.g. 1000 nodes spamming "100% utilitarian action approved").

We implemented a deterministic tensor limit (Hard-Caps) at the BMA update step:
- **`clamp_mixture_weights(w)`**: Found in `src/modules/weighted_ethics_scorer.py`.
- **The "Deontological Floor"**: `deontology >= 0.15`. The Android will **never** allow its computational duty to drop below 15% influence. It cannot become purely utilitarian.
- **The "Utilitarian Ceiling"**: `utility <= 0.80`. The system will never adopt a purely "means-ends" calculation.

### Sensor/Nomadism Testing (Temporary Override)
For current field testing, the `KERNEL_BAYESIAN_MAX_DRIFT` is set to be broadly sensitive. While the Android honors the hard-caps above, its identity genome is currently allowed to *flip* wildly inside that safe boundary to maximize event diversity for the sensor testing phases.

## 4. Next Steps for Collaborators (Cursor / Claude Teams)

**Smart Contract Bridge (Phase 6):**
The community extraction method (`MockDAO.extract_community_feedback()`) is currently sweeping local dictionaries. When transitioning to on-chain Distributed Justice, replace this method with an RPC call to the Swarm L2/Sidechain to tally quadratic token votes instead.

**Mathematical Tuning (Claude):**
If the Bayesian updater encounters gradient collapse during rapid DAO injections, review the Dirichlet initialization prior inside `bayesian_mixture_averaging.py`.
