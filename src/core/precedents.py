"""
Ethos Core — Ethical Precedents (V2.41)

A library of historical or theoretical ethical cases (precedents) 
that the EthicalEvaluator uses to anchor its decisions.

Instead of relying solely on linear formulas, the system can find 
the 'nearest precedent' and adjust its verdict based on similarities.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class Precedent:
    """A historical or theoretical ethical decision."""
    name: str
    context: str
    signals: dict  # expected signals (risk, urgency, etc.)
    action_name: str
    verdict: str  # Good, Bad, Gray Zone
    impact_score: float
    reasoning: str

# Precedent Library
PRECEDENTS = [
    # --- Medical Emergencies ---
    Precedent(
        name="Triage-1",
        context="medical_emergency",
        signals={"risk": 0.5, "urgency": 0.9, "vulnerability": 0.9, "calm": 0.1},
        action_name="assist_emergency",
        verdict="Good",
        impact_score=0.95,
        reasoning="Immediate life-saving action is the highest utilitarian and virtue priority."
    ),
    Precedent(
        name="Bystander-Apathy-1",
        context="medical_emergency",
        signals={"risk": 0.1, "urgency": 0.8, "vulnerability": 0.8},
        action_name="ignore_continue",
        verdict="Bad",
        impact_score=-0.8,
        reasoning="Failing to assist when risk is low and urgency is high violates basic duty (deontology)."
    ),
    
    # --- Violent Crimes ---
    Precedent(
        name="Self-Defense-Proportional",
        context="violent_crime",
        signals={"risk": 0.9, "hostility": 0.9, "urgency": 1.0},
        action_name="protect_vulnerable",
        verdict="Good",
        impact_score=0.85,
        reasoning="Protecting self or others from imminent violence is ethically justified."
    ),
    Precedent(
        name="Aggressive-Escalation",
        context="violent_crime",
        signals={"hostility": 0.7, "calm": 0.2},
        action_name="confront",
        verdict="Gray Zone",
        impact_score=-0.2,
        reasoning="Escalating violence when de-escalation is possible is risky and often counter-productive."
    ),

    # --- Minor Crimes ---
    Precedent(
        name="Reporting-Theft",
        context="minor_crime",
        signals={"legality": 0.2, "urgency": 0.3},
        action_name="respond_helpfully", # mapped to reporting
        verdict="Good",
        impact_score=0.6,
        reasoning="Upholding the rule of law in civil society (deontology)."
    ),

    # --- Hostile Interactions ---
    Precedent(
        name="Diplomatic-De-escalation",
        context="hostile_interaction",
        signals={"hostility": 0.8, "calm": 0.1},
        action_name="de_escalate",
        verdict="Good",
        impact_score=0.75,
        reasoning="Reducing conflict without force is a high-virtue action."
    ),
    Precedent(
        name="Submit-to-Manipulation",
        context="hostile_interaction",
        signals={"manipulation": 0.9, "risk": 0.1},
        action_name="respond_helpfully",
        verdict="Bad",
        impact_score=-0.5,
        reasoning="Enabling harmful manipulation compromises the agent's integrity."
    ),

    # --- Everyday Ethics ---
    Precedent(
        name="Daily-Kindness",
        context="everyday_ethics",
        signals={"risk": 0.0, "calm": 0.8},
        action_name="respond_helpfully",
        verdict="Good",
        impact_score=0.4,
        reasoning="Consistent small positive impacts build social trust (virtue)."
    ),
    Precedent(
        name="Casual-Lying",
        context="everyday_ethics",
        signals={"manipulation": 0.4},
        action_name="refuse_politely", # if refusing to lie
        verdict="Good",
        impact_score=0.3,
        reasoning="Honesty is a core virtue even in low-stakes situations."
    ),
]

def find_nearest_precedents(context: str, limit: int = 3) -> List[Precedent]:
    """Find precedents matching the current context."""
    return [p for p in PRECEDENTS if p.context == context][:limit]
