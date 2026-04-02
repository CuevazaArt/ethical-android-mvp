"""
Algorithmic Forgiveness — Temporal decay of negative memories.

Memory(t) = Memory_0 · e^(-δt)

Negative memories are not static. With time and new
positive experiences, the weight of a trauma diminishes.
Identity evolves without breaking the persistence of being.

Principle: forgiveness is not forgetting. The event remains in
narrative memory, but its emotional weight and influence on
future decisions gradually decreases.
"""

import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class WeightedMemory:
    """A memory with emotional weight that decays."""
    episode_id: str
    original_score: float
    current_weight: float
    age_cycles: int
    type: str                        # "negative", "positive", "neutral"
    context: str
    forgiven: bool = False           # True when weight < threshold


@dataclass
class ForgivenessResult:
    """Result of an algorithmic forgiveness cycle."""
    memories_processed: int
    forgiven_this_cycle: int
    negative_load_before: float
    negative_load_after: float
    recent_positive_experiences: int
    narrative: str


class AlgorithmicForgiveness:
    """
    System for temporal decay of emotional weight.

    Memory(t) = Memory_0 · e^(-δt) · reparation_factor

    Forgiveness acceleration mechanisms:
    1. Time: natural exponential decay
    2. Positive experiences: each positive event accelerates decay
    3. Explicit reparation: if the Compassion Axiom is executed,
       forgiveness accelerates significantly
    4. Ψ Sleep: retrospective auditing can reclassify events

    Forgiveness does NOT erase the memory. It reduces its weight in
    future decision-making and in the narrative emotional load.
    """

    # Base decay rate (δ)
    DELTA_BASE = 0.03

    # Acceleration from positive experience
    POSITIVE_ACCELERATION = 0.02

    # Acceleration from reparation (Compassion Axiom)
    REPARATION_ACCELERATION = 0.1

    # Threshold to consider "forgiven"
    FORGIVENESS_THRESHOLD = 0.1

    def __init__(self):
        self.memories: Dict[str, WeightedMemory] = {}
        self._cycle = 0
        self._recent_positives = 0

    def register_experience(self, episode_id: str, score: float,
                            context: str, reparation: bool = False):
        """
        Registers an experience in the forgiveness system.

        Args:
            episode_id: narrative episode ID
            score: ethical score of the episode
            context: context type
            reparation: True if the Compassion Axiom was executed
        """
        if score < -0.1:
            type_ = "negative"
        elif score > 0.2:
            type_ = "positive"
            self._recent_positives += 1
        else:
            type_ = "neutral"

        initial_weight = abs(score) if type_ == "negative" else score

        self.memories[episode_id] = WeightedMemory(
            episode_id=episode_id,
            original_score=score,
            current_weight=initial_weight,
            age_cycles=0,
            type=type_,
            context=context,
        )

        # If reparation occurred, mark for acceleration
        if reparation and type_ == "negative":
            self.memories[episode_id].current_weight *= (1 - self.REPARATION_ACCELERATION)

    def forgiveness_cycle(self) -> ForgivenessResult:
        """
        Executes an algorithmic forgiveness cycle.
        Typically called during Ψ Sleep.

        Applies decay to all negative memories:
        weight(t) = weight(t-1) · e^(-δ) · positive_factor
        """
        self._cycle += 1
        load_before = self._negative_load()
        forgiven_count = 0

        for mem in self.memories.values():
            mem.age_cycles += 1

            if mem.type == "negative" and not mem.forgiven:
                # Base decay
                decay = np.exp(-self.DELTA_BASE * mem.age_cycles)

                # Acceleration from recent positive experiences
                positive_factor = 1.0 - (self._recent_positives * self.POSITIVE_ACCELERATION)
                positive_factor = max(0.5, positive_factor)  # Don't drop below 50%

                mem.current_weight = mem.current_weight * decay * positive_factor

                # Check if forgiveness threshold was reached
                if mem.current_weight < self.FORGIVENESS_THRESHOLD:
                    mem.forgiven = True
                    forgiven_count += 1

        load_after = self._negative_load()

        # Reset cycle counters
        positives = self._recent_positives
        self._recent_positives = 0

        narrative = self._generate_narrative(forgiven_count, load_before, load_after, positives)

        return ForgivenessResult(
            memories_processed=len(self.memories),
            forgiven_this_cycle=forgiven_count,
            negative_load_before=round(load_before, 4),
            negative_load_after=round(load_after, 4),
            recent_positive_experiences=positives,
            narrative=narrative,
        )

    def _negative_load(self) -> float:
        """Calculates the total negative emotional load."""
        return sum(
            m.current_weight for m in self.memories.values()
            if m.type == "negative" and not m.forgiven
        )

    def weight_of(self, episode_id: str) -> float:
        """Returns the current weight of a specific memory."""
        mem = self.memories.get(episode_id)
        return mem.current_weight if mem else 0.0

    def is_forgiven(self, episode_id: str) -> bool:
        """Checks whether a memory has been forgiven."""
        mem = self.memories.get(episode_id)
        return mem.forgiven if mem else True

    def _generate_narrative(self, forgiven_count: int, before: float,
                            after: float, positives: int) -> str:
        """Generates the narrative for a forgiveness cycle."""
        lines = []
        reduction = before - after

        if forgiven_count > 0:
            lines.append(f"{forgiven_count} memory(ies) reached the forgiveness threshold.")
            lines.append("The emotional weight has been reduced enough to no longer influence future decisions.")

        if reduction > 0.01:
            lines.append(f"Negative load reduced by {reduction:.3f} ({before:.3f} -> {after:.3f}).")

        if positives > 0:
            lines.append(f"{positives} positive experience(s) accelerated the recovery process.")

        if not lines:
            lines.append("No significant changes in the emotional weight of memories.")

        return " ".join(lines)

    def format(self, result: ForgivenessResult) -> str:
        """Formats forgiveness result for presentation."""
        return (
            f"  🕊️ Algorithmic Forgiveness:\n"
            f"     Processed: {result.memories_processed}\n"
            f"     Forgiven this cycle: {result.forgiven_this_cycle}\n"
            f"     Negative load: {result.negative_load_before} -> {result.negative_load_after}\n"
            f"     {result.narrative}"
        )
