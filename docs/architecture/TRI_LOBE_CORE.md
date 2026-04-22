# Antigravity Tri-Lobe Core Architecture

This document tracks the visual evolution of the Tri-Lobe core. **AI Agents MUST update this diagram if structural changes are made to the interfaces.**

## High-Level Cognitive Flow

```mermaid
graph TD
    User([User Chat Input]) --> Thalamus[Thalamus Lobe - L0]
    Sensors[(Sensors: Vision/Audio)] --> PL[Perceptive Lobe - L1]
    
    subgraph "Kernel Central"
        K[EthosKernel]
        K -- "ProactivePulse (45s)" --> CC
    end

    subgraph "Nervous System (Asynchronous Bus)"
        CC{{"Corpus Callosum (Event Bus)"}}
    end
    
    Thalamus -- "SensorySpike" --> CC
    PL -- "CognitivePulse" --> CC
    
    CC -- "Sensory/Cognitive" --> LL[Limbic Lobe - L2]
    CC -- "SensorySpike" --> CL[Cerebellum Lobe - L4]
    CL -- "BayesianEcograde" --> CC
    
    CC -- "Cognitive/Bayesian" --> EL[Executive Lobe - L3]
    EL -- "MotorCommand" --> CC
    EL -- "Drives/Curiosity" --> ME[Motivation Engine]
    ME -- "ProactiveIntent" --> EL
    
    CC -- "Sensory/Motor" --> ML[Memory Lobe - L5]
    ML -- "Biographic/DAO/Identity" --> CC

    CC -- "MotorCommand" --> Output[/System Response/]
    
    CC -- "Veto/Trauma" --> Trauma[Identity Integrity Manager]
    CC -- "Audit" --> DB[(Distributed Justice Ledger)]
```

## System Dependencies
- **Identity Integrity:** Ensures the Node ID and reputation are stable.
- **Basal Ganglia:** Computes the 6-axis resonance.
- **Cerebellum:** Daemon thread for hardware interrupts (100Hz).
