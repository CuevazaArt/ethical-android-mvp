# Antigravity Tri-Lobe Core Architecture

This document tracks the visual evolution of the Tri-Lobe core. **AI Agents MUST update this diagram if structural changes are made to the interfaces.**

## High-Level Cognitive Flow

```mermaid
graph TD
    User([User Input]) --> Thalamus[Thalamus Node]
    
    subgraph "Ethical Tri-Lobe Core"
        Thalamus --> PL[Perception Lobe]
        Thalamus --> LL[Limbic Lobe]
        Thalamus --> EL[Executive Lobe]
        
        PL -- "Environment State" --> LL
        LL -- "Cognitive Tension" --> EL
        EL -- "Action Candidates" --> Thalamus
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
