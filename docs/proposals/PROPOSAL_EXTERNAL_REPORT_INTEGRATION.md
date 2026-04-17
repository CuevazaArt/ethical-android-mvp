# External Team Research Reconciliation
**Date:** 2026-04-17
**Reviewer:** Antigravity (L1 Planner)
**Status:** Merged actionable insights into roadmap, redundant theory discarded.

## 1. Executive Summary
The external team submitted a comprehensive research report titled *"Reconstrucción Robusta del Modelo Conversacional Multimodal para Androides Sociales"*. Juan (L0) directed a strict filtering pass: extract actionable value, discard redundancies. 

This document summarizes the assimilation of their insights into our `Quad-Lobe MER V2` architecture.

## 2. Redundancies Discarded (Already Implemented)
The report proposed several architectural shifts that **we have already achieved** in the current Quad-Lobe sprint:
- **"Módulo Ético Distribuido y Enforcement en Tiempo Real":** Discarded. Our `EthicalLobe` already runs as a local edge gate (Level 2 Contextual Veto) in <20ms, preventing the centralization bottleneck they feared.
- **"Adaptación Cultural Tatemae/Honne":** Discarded/Aligned. We already have the robust `UchiSotoModule` mapping interaction profiles to social distances.
- **"Smoothing Afectivo":** They proposed Kalman Filters or LSTM for emotional stability. We have already deployed **Exponential Moving Average (EMA)** via the `BasalGanglia` module. EMA achieves the exact same goal (preventing sociopathic parameter jumps) with a fraction of the CPU cost of an LSTM. We will keep EMA for the edge, but log Kalman/LSTM as a future scaling option if running on the cloud.

## 3. High-Value Extractions (Actionable for L2 Squads)
The external report provided highly specific, state-of-the-art tooling recommendations that perfectly align with our upcoming blocks. I have authorized the L2 teams to adopt these specific tools under the *Autonomía Acotada* policy:

### A. Team Copilot: TurnGPT & VAP (For Módulo 10.4 / Eferencia)
- **Insight:** The external team recommends **TurnGPT** and **Voice Activity Projection (VAP)** for granular, speculative turn execution and backchanneling.
- **Action:** Copilot Squad is authorized to upgrade the `TurnPrefetcher` (currently using heuristic dictionaries) to utilize lightweight VAP models when hardware allows, drastically improving group-conversation flow.

### B. Team Cursor: OpenFace 3.0 (For Módulo 10.1 / Fusión Sensorial)
- **Insight:** For robust VAD under poor signal-to-noise ratios, cross-referencing with lightweight visual micro-expression models like **OpenFace 3.0** is highly recommended.
- **Action:** Team Cursor must evaluate `OpenFace 3.0` inside the `ThalamusNode` pipeline to extract "lip_movement" and "presence" variables without saturating the Raspberry Pi/Edge CPU.

### C. Large/Small Culture Dynamics (Robot-Ethnographer)
- **Insight:** Dynamically learning group "small-culture" rather than relying on monolithic national stereotypes.
- **Action:** This provides excellent theoretical backing for our `MultiRealmGovernor`. We will ensure that LAN-based nodes (interacting with the same household group) independently tune their `UchiSoto` baselines based on local group norms (Swarm LAN).

## 4. Conclusion
The external research validates our current trajectory (especially the Quadrilobular split and affective smoothing). The primary value extracted was the identification of specific edge-optimized AI models (OpenFace 3.0, TurnGPT) which have now been slotted into the L2 execution queues.

We now proceed to **Módulo 9: Nomadismo Perceptivo**.
