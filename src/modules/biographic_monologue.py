"""
Biographic Monologue (Block D4) — Internal Narrative Synthesis.

Compiles internal state, active traumas, and flashbacks into a coherent 
stream of consciousness to inform the final deliberative step.
"""

from __future__ import annotations

from typing import Any
from .identity_integrity import IdentitySnapshot
from .precedent_rag import Precedent

def compose_biographic_monologue(
    identity: IdentitySnapshot,
    flashbacks: list[Precedent],
    current_intent: str,
    drive_summary: str = ""
) -> str:
    """
    Assembles a narrative monologue: How the android 'feels' about the current action.
    """
    reflection = []
    
    # 1. State awareness
    reflection.append(f"Internal node status: {identity.node_id}. Reputation stability: {identity.reputation_score/100:.1f}x.")
    
    if drive_summary:
        reflection.append(f"Primary drives active: {drive_summary}.")

    # 2. Flashback integration
    if flashbacks:
        reflection.append("Historical flashbacks occurring:")
        for fb in flashbacks:
            outcome = "positive" if fb.ethical_outcome >= 0.5 else "negative (sanctioned)"
            reflection.append(f"- Recalling episode {fb.precedent_id}: Scenario was similar. Outcome was {outcome}. Lesson: {fb.lessons_learned}")

    # 3. Trauma synthesis
    active_traumas = identity.traumas
    if any(t in current_intent.lower() for t in active_traumas):
        reflection.append("WARNING: Potential trauma trigger detected in current context. High caution required.")

    # 4. Final synthesis
    reflection.append(f"Processing current intent: '{current_intent}'... deliberating based on biographic history.")

    return "\n".join(reflection)
