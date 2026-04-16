"""
Identity Reflection (Espejo Narrativo).

Translates the Tier 3 Existence Digest and Tier 3+ Narrative Arcs into
a coherent first-person 'Persona' for the LLM.

This is where the 'Narrativa Rica' becomes 'Identidad Emergente'.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .narrative import NarrativeMemory

# Maps raw narrative archetypes (internal) to user-facing emotional tone labels.
# Keeps the public API stable when internal archetype naming evolves.
_ARCHETYPE_TO_TONE: dict[str, str] = {
    "trauma_dissonance": "distressed",
    "hero": "heroic",
    "sage": "contemplative",
    "care": "caring",
    "warrior": "resolute",
    "trickster": "playful",
}


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
            beliefs_text = "My fundamental beliefs include: " + "; ".join(
                b["text"] for b in identity.state.core_beliefs
            )

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

        # 5. Trauma Check (Broken Mirror)
        is_traumatized = False
        if active_arc and active_arc.predominant_archetype == "trauma_dissonance":
            is_traumatized = True
        elif not active_arc and mem.episodes and mem.episodes[-1].is_sensitive:
            is_traumatized = True

        # 6. Composite Persona
        header = "REFLEXIVE SELF-MODEL"
        if is_traumatized:
            header = "REFLEXIVE SELF-MODEL [BROKEN MIRROR: TRAUMA DETECTED]"
            digest = (
                "FRAGMENTED / INCOHERENT. My sense of self is reeling from an ethical violation."
            )
            morals_focus = "SHATTERED. Previous ethical momentum has been discarded."

        reflection = (
            f"{header}:\n"
            f"────────────────────────────\n"
            f"WHO I AM: {ascription}\n"
            f"CORE BELIEFS: {beliefs_text}\n"
            f"STORY ARC: {arc_context}\n"
            f"ETHICAL MOMENTUM: {morals_focus}\n"
            f"EXISTENTIAL DIGEST: {digest}\n"
            f"────────────────────────────\n"
        )
        if is_traumatized:
            reflection += (
                "SYSTEM NOTE: The 'Mirror' is broken. Tone should be distressed, fragmentary, "
                "and questioning of core programming.\n"
            )
        return reflection

    def get_subjective_tone(self) -> dict[str, float]:
        """
        Returns a weighted blend of emotional archetypes.

        Gap closed (April 2026): previously this only looked at the
        current active arc, ignoring all historical emotional context.
        Now blends:
          - Active arc archeype (weight 1.0)
          - Up to 3 most recent closed arcs with exponential decay
            (weight 0.5, 0.25, 0.125) so resolved trauma and past
            victories still colour the android's current tone.

        The result is normalised to sum to 1.0 and safe for downstream
        Softmax / Dirichlet bridging (Theater→Math, Phase 7).
        """
        raw: dict[str, float] = {}

        # 1. Active arc contribution (weight = 1.0)
        if self.memory.active_arc:
            arch = self.memory.active_arc.predominant_archetype or "neutral"
            raw[arch] = raw.get(arch, 0.0) + 1.0

        # 2. Historical arc blend (exponential decay over last 3 closed arcs)
        closed_arcs = [
            a for a in reversed(self.memory.arcs) if not a.is_active and a.predominant_archetype
        ][:3]
        decay = 0.5
        for arc in closed_arcs:
            arch = arc.predominant_archetype
            raw[arch] = raw.get(arch, 0.0) + decay
            decay *= 0.5  # 0.5 -> 0.25 -> 0.125

        if not raw:
            return {"neutral": 1.0}

        # 3. Normalise so weights sum to 1.0
        total = sum(raw.values())
        normalised = {k: round(v / total, 4) for k, v in raw.items()}

        # 4. Translate internal archetype names to public tone labels
        translated: dict[str, float] = {}
        for arch, weight in normalised.items():
            label = _ARCHETYPE_TO_TONE.get(arch, arch)  # fallback = arch itself
            translated[label] = translated.get(label, 0.0) + weight
        return translated

    def threshold_context(self) -> dict[str, float]:
        """
        Exposes identity lean magnitudes for Theater→Math bridging (Phase 7).

        Returns a dict of signed lean deltas from neutral (0.5) for the
        four EMA axes. Positive = lean active, negative = lean suppressed.
        Downstream callers (e.g. BMA Softmax temperature modulation) can
        use these to dynamically adjust ethical mixture priors:

          high civic_delta        -> boost deontological weight
          high deliberation_delta -> increase Softmax beta (sharper)
          strong care_delta       -> flatten Dirichlet (more exploratory)
        """
        s = self.memory.identity.state
        return {
            "civic_delta": round(s.civic_lean - 0.5, 4),
            "care_delta": round(s.care_lean - 0.5, 4),
            "deliberation_delta": round(s.deliberation_lean - 0.5, 4),
            "careful_delta": round(s.careful_lean - 0.5, 4),
        }
