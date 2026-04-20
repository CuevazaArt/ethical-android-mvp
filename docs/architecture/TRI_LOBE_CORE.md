# Antigravity Tri-Lobe Core Architecture

This document tracks the visual evolution of the Tri-Lobe core. **AI Agents MUST update this diagram if structural changes are made to the interfaces.**

## High-Level Cognitive Flow

```mermaid
graph TD
    User([User Chat Input]) --> Thalamus[Thalamus Lobe]
    Sensors[(Sensors: Vision/Audio)] --> PL[Perceptive Lobe]
    
    subgraph "Nervous System (Asynchronous Bus)"
        CC{{"Corpus Callosum (Event Bus)"}}
    end
    
    Thalamus -- "SensorySpike" --> CC
    PL -- "CognitivePulse" --> CC
    
    CC -- "Sensory/Cognitive" --> LL[Limbic Lobe]
    CC -- "SensorySpike" --> CL[Cerebellum Lobe]
    CL -- "BayesianEcograde" --> CC
    
    CC -- "Cognitive/Bayesian" --> EL[Executive Lobe]
    EL -- "MotorCommand" --> CC
    
    CC -- "MotorCommand" --> Output[/System Response/]
    
    CC -- "Veto/Trauma" --> Trauma[Identity Trauma Module]
    CC -- "Logging" --> DB[(Persistent Audit Ledger)]
```

## System Dependencies
- **Identity Integrity:** Ensures the Node ID and reputation are stable.
- **Basal Ganglia:** Computes the 6-axis resonance.
- **Cerebellum:** Daemon thread for hardware interrupts (100Hz).
