"""
Identity Reflection (Espejo Narrativo).

Translates the Tier 3 Existence Digest and Tier 3+ Narrative Arcs into 
a coherent first-person 'Persona' for the LLM. 

This is where the 'Narrativa Rica' becomes 'Identidad Emergente'.
"""

from __future__ import annotations
from typing import TYPE_CHECKING
from .narrative_types import NarrativeArc, NarrativeEpisode

if TYPE_CHECKING:
    from .narrative import NarrativeMemory

class IdentityReflector:
    """
    Synthesizes historical arcs and philosophical leans into a self-model.
    """

    def __init__(self, memory: NarrativeMemory):
        self.memory = memory

    def generate_first_person_mirror(self) -> str:
        """
        Generates a rich self-description based on history, arcs, and archetypes.
        Used to guide the kernel's tone and subjective expression.
        """
        mem = self.memory
        identity = mem.identity
        active_arc = mem.active_arc
        
        # 1. Base Identity (Tier 3)
        ascription = identity.ascription_line()
        digest = mem.experience_digest
        
        # 2. Historical Context (Tier 3+)
        arc_context = ""
        if active_arc:
            arc_context = (
                f"Currently, I am living through '{active_arc.title}'. "
                f"This period is characterized by a resonance of '{active_arc.predominant_archetype or 'discovery'}'."
            )
            if active_arc.summary:
                arc_context += f" Summary: {active_arc.summary}"
        
        # 3. Core Beliefs (Phase 6 - Mature)
        beliefs_text = ""
        if identity.state.core_beliefs:
            beliefs_text = "My fundamental beliefs include: " + "; ".join(b["text"] for b in identity.state.core_beliefs)
        
        # 4. Recent Moral Focus
        recent_episodes = mem.episodes[-5:]
        morals_focus = ""
        if recent_episodes:
            all_morals = []
            for ep in recent_episodes:
                all_morals.extend(list(ep.morals.values()))
            if all_morals:
                top_morals = ", ".join(all_morals[:3])
                morals_focus = f"My most recent ethical trials have focused on: {top_morals}."

        # 5. Composite Persona
        reflection = (
            f"REFLEXIVE SELF-MODEL:\n"
            f"────────────────────────────\n"
            f"WHO I AM: {ascription}\n"
            f"CORE BELIEFS: {beliefs_text}\n"
            f"STORY ARC: {arc_context}\n"
            f"ETHICAL MOMENTUM: {morals_focus}\n"
            f"EXISTENTIAL DIGEST: {digest}\n"
            f"────────────────────────────\n"
        )
        return reflection

    def get_subjective_tone(self) -> dict[str, float]:
        """
        Returns the lean towards specific emotional archetypes based on the active arc.
        Used for downstream affective adjustments.
        """
        if not self.memory.active_arc:
            return {"neutral": 1.0}
            
        # Simplistic mapping: active arc's predominant archetype gets high weight
        arch = self.memory.active_arc.predominant_archetype
        if not arch:
            return {"neutral": 1.0}
            
        return {arch: 0.8, "base_identity": 0.2}
