# Proposal 010: Synthesis of Architectural Critique & Alignment Plan (Phase 7 Init)

**Status: Strategy Anchor (April 2026)**
**Author: Antigravity Team**

## 1. Executive Summary: The "Authenticity Gap"
Following a full-repo audit, we have identified a critical divergence between the **Narrative Theater** (psychology, affect, circles) and the **Ethical Core** (mixture scoring). While the android *feels* more human, its final actions remain largely decoupled from its internal psychological state.

## 2. Identified Vulnerabilities & Technical Debt
*   **Decoupled Impact**: Most of the ~70 modules affect "Tone" but not `final_action`.
*   **Calibration Debt**: Moral coefficients are engineering priors, not empirically validated study results.
*   **Naming Drift**: The "Bayesian" engine currently performs fixed mixtures, not continuous belief updates.
*   **Governance Bottleneck**: The transition to Blockchain (Phase 6) will introduce a latency wall that the current synchronous kernel cannot handle.

## 3. Guiding Principles & User Directives (April 2026 Update)
Based on direct stakeholder feedback, the following guardrails must govern all future expansions of the model:

1.  **Strategic Vetoes Over Immediate Evasion**: Psychological states (Dissonance, Traumatic memory) should primarily feed into the **planning and execution of missions/tasks** (Tier 4/Executive Strategist), vetoing options based on perceived long-term environments, rather than creating erratic real-time reactions.
2.  **Patience on Empirical Calibration**: The "Laboratory Bias" and lack of organic scenario data will be addressed in future phases via the **DAO and field trials**. We will not prematurely invent RLHF data without real-world feedback.
3.  **Strict Anti-Radicalism (Safety First)**: The android must **never** become so "heroic" or "passionate" that it becomes a physical or social risk. It is strictly forbidden to attack a human or object out of frustration, anger, or moral radicalism. 
4.  **The "Average User Expectation" Standard**: The model must be oriented to behave as a highly reliable, emotionally intelligent, but ultimately predictable and safe *tool*. It should reflect what an average person expects from a high-end commercial assistant, not a rogue philosopher.

## 4. Actionable Alignment (Post-Claude BMA Update)
With the latest merge from the **Claude Team** (`PROPOSAL_BAYESIAN_MIXTURE_FEEDBACK`), the "Bayesian Illusion" has been resolved. The kernel now utilizes genuine Bayesian Mixture Averaging (BMA), Plackett-Luce likelihood, and Dirichlet distribution posterior updates. The engine formally Learns.

Our new strategic interlock goals (Phase 7 - Inter-Team Fusion) are:
1.  **Bridging Theater and Math**: Connect our psychological axes (e.g., Relational Tension from Uchi-Soto, Epistemic Curiosity, Dissonance) directly into the mathematical parameters of Claude's engine. For example, high relational tension should dynamically increase the system's "temperature" (Softmax Beta) or flatten Dirichlet priors natively.
2.  **DAO Calibration**: Implement the feedback extraction pipeline that allows distributed validators (DAO) to provide empirical scenarios to adjust the `KERNEL_FEEDBACK_UPDATE_STRENGTH`.
3.  **Boundary Safety Integration**: Enforce the non-radical alignment guidelines (Section 3) mathematically by constraining the absolute maximum weight drift during Bayesian posterior updates.

## 4. Next Steps for Antigravity (Phase 7)
*   **Async Scorer Port**: Preparing the `WeightedEthicsScorer` for the transition to asynchronicity required by the DAO/Blockchain layer (Proposal 009).
*   **Ground-Truth Mapping**: Aligning default coefficients with documented legal/ethical frameworks to reduce "engineering bias".

---
> [!NOTE]
> This document serves as the shared technical vision for the next sprint. We await Claude's commit on the Bayesian engine to finalize the interlock.
