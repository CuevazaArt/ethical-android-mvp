# Antigravity Tri-Lobe Core Architecture

This document tracks the visual evolution of the Tri-Lobe core. **AI Agents MUST update this diagram if structural changes are made to the interfaces.**

## High-Level Cognitive Flow

```mermaid
graph TD
    User([User Input]) --> Thalamus[Thalamus Node]
    
    subgraph "Ethical Tri-Lobe Core"
        Thalamus --> PL[Perception Lobe]
        PL -- "Signals" --> LL[Limbic Lobe]
        LL -- "Tension" --> CL[Cerebellum Lobe]
        ML[(Memory Lobe)] -- "Temporal Priors" --> CL
        CL -- "Hypothesis weights" --> EL[Executive Lobe]
        EL -- "Action" --> ML
    end
    
    subgraph "Safety & Governance"
        EL --> DG[DAO Governance V11]
        DG --> Interlock{Safety Gate}
    end
    
    Interlock -- "Validated" --> Output[/System Response/]
    Interlock -- "Blocked" --> Trauma[Identity Trauma Module]
```

## System Dependencies
- **Identity Integrity:** Ensures the Node ID and reputation are stable.
- **Basal Ganglia:** Computes the 6-axis resonance.
- **Cerebellum:** Daemon thread for hardware interrupts (100Hz).
