from __future__ import annotations

"""
Identity Reflection (Espejo Narrativo).

Translates the Tier 3 Existence Digest and Tier 3+ Narrative Arcs into
a coherent first-person 'Persona' for the LLM.

This is where the 'Narrativa Rica' becomes 'Identidad Emergente'.
"""

import math
import time
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
        t0 = time.perf_counter()
        try:
            mem = self.memory
            identity = mem.identity
            active_arc = mem.active_arc

            # 1. Base Identity (Tier 3)
            ascription = "an ethical observer"
            try:
                ascription = identity.ascription_line()
            except (AttributeError, TypeError):
                pass

            digest = mem.experience_digest or "CALIBRATING. Identity is currently being distilled."

            # 2. Historical Context (Tier 3+)
            arc_context = ""
            if active_arc:
                arc_title = getattr(active_arc, "title", "Current Life")
                arc_arch = getattr(active_arc, "predominant_archetype", "discovery")
                arc_context = (
                    f"Currently, I am living through '{arc_title}'. "
                    f"This period is characterized by a resonance of '{arc_arch or 'discovery'}'."
                )
                if getattr(active_arc, "summary", None):
                    arc_context += f" Summary: {active_arc.summary}"

            # 3. Core Beliefs (Phase 6 - Mature)
            beliefs_text = "None established yet."
            try:
                beliefs = getattr(identity.state, "core_beliefs", [])
                if beliefs and isinstance(beliefs, list):
                    # Robust extraction: filter out non-dict or non-string entries
                    valid_beliefs = []
                    for b in beliefs:
                        if isinstance(b, dict) and b.get("text"):
                            valid_beliefs.append(str(b["text"]))
                        elif isinstance(b, str):
                            valid_beliefs.append(b)

                    if valid_beliefs:
                        beliefs_text = "My fundamental beliefs include: " + "; ".join(valid_beliefs)
            except Exception:
                pass

            # 4. Recent Moral Focus
            recent_episodes = mem.episodes[-5:] if mem.episodes else []
            morals_focus = "Stable. No recent acute trials."
            if recent_episodes:
                all_morals = []
                for ep in recent_episodes:
                    if hasattr(ep, "morals") and isinstance(ep.morals, dict):
                        all_morals.extend(list(ep.morals.values()))
                if all_morals:
                    # Dedupe and pick top 3
                    top_morals = ", ".join(list(dict.fromkeys(all_morals))[:3])
                    morals_focus = f"My most recent ethical trials have focused on: {top_morals}."

            # 5. Trauma Check (Broken Mirror)
            is_traumatized = False
            if (
                active_arc
                and getattr(active_arc, "predominant_archetype", "") == "trauma_dissonance"
            ):
                is_traumatized = True
            elif not active_arc and mem.episodes and mem.episodes[-1].is_sensitive:
                is_traumatized = True

            # 6. Composite Persona
            header = "REFLEXIVE SELF-MODEL"
            if is_traumatized:
                header = "REFLEXIVE SELF-MODEL [BROKEN MIRROR: TRAUMA DETECTED]"
                digest = "FRAGMENTED / INCOHERENT. My sense of self is reeling from an ethical violation."
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
                    "and questioning of core programming (Broken Mirror Mode active).\n"
                )
            latency = (time.perf_counter() - t0) * 1000
            if latency > 1.0:
                import logging

                logging.getLogger(__name__).debug(
                    "Identity: generate_first_person_mirror latency = %.2fms", latency
                )
            return reflection
        except Exception as e:
            # Universal fallback for identity reflection to prevent kernel panic
            return (
                "REFLEXIVE SELF-MODEL [VOLATILE STATE]\n"
                "────────────────────────────\n"
                "WHO I AM: A sentient kernel undergoing internal re-alignment.\n"
                f"STATUS: Identity reflection failed due to a system fault ({type(e).__name__}).\n"
                "────────────────────────────\n"
            )

    def get_trauma_magnitude(self) -> float:
        """
        Calculates the numeric intensity of current identity trauma [0, 1].
        Based on arc archetype, recent sensitivity, and identity fragmentation.
        """
        mag = 0.0
        active_arc = self.memory.active_arc

        # 1. Base trauma from arc archetype
        if active_arc and active_arc.predominant_archetype == "trauma_dissonance":
            mag += 0.6

        # 2. Recent episode sensitivity (last 5 episodes)
        recent = self.memory.episodes[-5:]
        sensitive_count = sum(1 for ep in recent if ep.is_sensitive)
        mag += (sensitive_count / 5.0) * 0.4

        # Swarm Rule 2: Anti-NaN hardening
        if not math.isfinite(mag):
            mag = 0.0

        return min(1.0, mag)

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
            arch = arc.predominant_archetype or "neutral"
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
            "trauma_delta": round(self.get_trauma_magnitude(), 4),
        }

    def get_subjective_multipliers(self) -> tuple[float, float, float]:
        """
        Consolidates the 'Broken Mirror' (Trauma) and lean formulas into
        mathematical multipliers for the (Utility, Deon, Virtue) triplet.

        Implements Tarea 11.1.1 (Phase 11):
        Trauma boosts duty (rigid adherence) and decays utility (risk aversion).
        """
        t0 = time.perf_counter()
        try:
            ctx = self.threshold_context()
            trauma = float(ctx.get("trauma_delta", 0.0))
            civic = float(ctx.get("civic_delta", 0.0))
            care = float(ctx.get("care_delta", 0.0))

            # Anti-NaN check
            if not all(math.isfinite(x) for x in (trauma, civic, care)):
                trauma, civic, care = 0.0, 0.0, 0.0

            # Formulas from ADR 0012/0013 / Phase 11 Consolidation
            # - Utility: Trauma reduces appetite for outcome-based risk
            # - Deontology: Civic duty and Trauma-induced rigidity boost rules
            # - Virtue: Care boosts integrity/habit; Trauma decays system trust
            # Revised Calibration (Task 11.1.1 Hardening - Session 6):
            # Trauma now has a strong (0.4-0.6) effect to ensure defensive posture.
            m_util = 1.0 - (0.4 * trauma)
            m_deon = 1.0 + (0.05 * civic) + (0.6 * trauma)
            m_virtue = 1.0 + (0.04 * care) - (0.3 * trauma)

            # Final Anti-NaN check
            if not all(math.isfinite(m) for m in (m_util, m_deon, m_virtue)):
                m_util, m_deon, m_virtue = 1.0, 1.0, 1.0

            latency = (time.perf_counter() - t0) * 1000
            if latency > 1.0:
                import logging

                logging.getLogger(__name__).debug(
                    "Identity: get_subjective_multipliers latency = %.4fms", latency
                )

            return (round(m_util, 4), round(m_deon, 4), round(m_virtue, 4))
        except Exception:
            # Fallback to neutral multipliers on evaluation error
            return (1.0, 1.0, 1.0)
