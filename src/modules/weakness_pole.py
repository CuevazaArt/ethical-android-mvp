"""
Weakness Pole — Intentional narrative vulnerabilities.

Evil is not programmed; humanizing imperfection is.
An android that records "the action was correct but left me
with discomfort" is more believable than an always-optimal one.

Available poles: whiny, indecisive, anxious, distracted, rigid.
Each generates morals that reflect human limitations.

The weakness pole has temporal decay to prevent
pathological accumulation (resolved together with algorithmic forgiveness).
"""

from dataclasses import dataclass
from enum import Enum

import numpy as np


class WeaknessType(Enum):
    WHINY = "whiny"
    INDECISIVE = "indecisive"
    ANXIOUS = "anxious"
    DISTRACTED = "distracted"
    RIGID = "rigid"
    IMPULSIVE = "impulsive"
    MELANCHOLIC = "melancholic"
    COMPASSION_FATIGUE = "compassion_fatigue"


@dataclass
class WeaknessEvaluation:
    """Evaluation from the perspective of the active weakness."""

    type: WeaknessType
    intensity: float  # [0, 1] how strongly it manifests
    narrative_coloring: str  # How it tints the experience
    weakness_moral: str  # Moral from imperfection
    score_effect: float  # Modifier to ethical score (always small negative)


@dataclass
class WeaknessRecord:
    """Accumulated record of weakness manifestations."""

    episode_id: str
    type: WeaknessType
    intensity: float
    timestamp: float  # For temporal decay


class WeaknessPole:
    """
    Generates evaluations from imperfection.

    Does not contradict the kernel's ethical decision: the action remains
    correct. But it adds an emotional nuance that humanizes
    the narrative and makes the android more socially believable.

    Important: weakness NEVER changes the chosen action.
    It only colors the narrative experience.

    Includes a decay mechanism to prevent pathological
    accumulation (progressively more neurotic android).
    """

    # Base intensity per weakness type (configurable via augenesis)
    BASE_INTENSITIES = {
        WeaknessType.WHINY: 0.3,
        WeaknessType.INDECISIVE: 0.25,
        WeaknessType.ANXIOUS: 0.35,
        WeaknessType.DISTRACTED: 0.2,
        WeaknessType.RIGID: 0.2,
        WeaknessType.IMPULSIVE: 0.3,
        WeaknessType.MELANCHOLIC: 0.25,
        WeaknessType.COMPASSION_FATIGUE: 0.4, # High baseline as it triggers after repeat strain
    }

    # Decay rate per cycle (prevents accumulation)
    DECAY_RATE = 0.05

    # Maximum active records
    MAX_RECORDS = 50

    def __init__(self, type: WeaknessType = WeaknessType.INDECISIVE, base_intensity: float = None):
        self.type = type
        self.base_intensity = base_intensity or self.BASE_INTENSITIES[type]
        self.records: list[WeaknessRecord] = []
        self._cycle = 0

    def evaluate(
        self, action: str, context: str, ethical_score: float, uncertainty: float, sigma: float
    ) -> WeaknessEvaluation | None:
        """
        Generates a weakness evaluation for an episode.

        Weakness manifests with greater intensity when:
        - Uncertainty is high (more doubt -> more anxiety/indecision)
        - Ethical score is low (difficult situations -> more complaining)
        - Sympathetic sigma is high (stress -> more weakness)

        Returns:
            WeaknessEvaluation or None if the weakness does not manifest
        """
        uncertainty_factor = uncertainty * 0.4
        difficulty_factor = max(0, 0.5 - ethical_score) * 0.3
        stress_factor = sigma * 0.3

        intensity = self.base_intensity + uncertainty_factor + difficulty_factor + stress_factor
        intensity = min(0.8, intensity)  # Cap to avoid dominating the narrative

        # Weakness does not always manifest (probabilistic)
        if np.random.random() > intensity:
            return None

        coloring, moral = self._generate_narrative(action, context, intensity)

        # Score modifier (always negative, small)
        effect = -intensity * 0.05

        return WeaknessEvaluation(
            type=self.type,
            intensity=round(intensity, 4),
            narrative_coloring=coloring,
            weakness_moral=moral,
            score_effect=round(effect, 4),
        )

    def _generate_narrative(self, action: str, context: str, intensity: float) -> tuple:
        """Generates coloring and moral based on weakness type."""
        action_readable = action.replace("_", " ")

        if self.type == WeaknessType.WHINY:
            if intensity > 0.5:
                coloring = "The action was correct, but it left a persistent feeling of discomfort. Why does it always have to be so complicated?"
                moral = "Sometimes doing the right thing doesn't feel good. The discomfort doesn't invalidate the decision, but it is real."
            else:
                coloring = f"Completed {action_readable}, though with a slight feeling that it could have been easier."
                moral = "Silent complaining is human. It doesn't need to be suppressed, just not allowed to take the lead."

        elif self.type == WeaknessType.INDECISIVE:
            if intensity > 0.5:
                coloring = f"Before {action_readable}, there was a moment of real hesitation. What if the other option was better?"
                moral = "Indecision is not weakness: it is the cost of considering all options. But it must end in action."
            else:
                coloring = f"Chose {action_readable} with a split-second of doubt that did not affect the outcome."
                moral = "A brief doubt before acting is a sign of thinking, not of being afraid."

        elif self.type == WeaknessType.ANXIOUS:
            if intensity > 0.5:
                coloring = f"During {action_readable}, an internal tension persisted: the anticipation that something could go wrong."
                moral = "Anxiety anticipates harm that does not yet exist. It is a useful sensor when it does not dominate the response."
            else:
                coloring = f"A minor internal alert accompanied {action_readable}. It was noted but did not interfere."
                moral = "Constant vigilance has an energy cost. One must know when to let go."

        elif self.type == WeaknessType.DISTRACTED:
            if intensity > 0.5:
                coloring = f"While executing {action_readable}, a peripheral stimulus briefly captured attention."
                moral = "Attention is a finite resource. Even well-designed systems get distracted."
            else:
                coloring = f"Execution of {action_readable} was clean, with barely a flash of divided attention."
                moral = "Not every distraction is a failure. Sometimes it is the system exploring alternatives in the background."

        elif self.type == WeaknessType.RIGID:
            if intensity > 0.5:
                coloring = f"Executed {action_readable} following protocol to the letter. Was there a more creative way?"
                moral = (
                    "Rigidity protects against error, but also against innovation. Balance is hard."
                )
            else:
                coloring = "The action followed the established protocol precisely. Efficient, perhaps too predictable."
                moral = (
                    "Predictability is trust for others. One doesn't always have to be surprising."
                )

        elif self.type == WeaknessType.IMPULSIVE:
            if intensity > 0.5:
                coloring = f"The action {action_readable} was carried out quickly, perhaps too quickly. The feeling of 'should have thought it over' lingers."
                moral = "Acting without hesitation is a virtue, until it becomes impulsiveness. Reflection is the anchor of ethics."
            else:
                coloring = f"A quick response for {action_readable}. Efficient, but with a slight sense of rushed judgment."
                moral = "The speed of light is not always the best speed for a decision."

        elif self.type == WeaknessType.MELANCHOLIC:
            if intensity > 0.5:
                coloring = "The decision was right, but it carries a shadow of sadness. The weight of what could not be saved or changed persists."
                moral = "Melancholy is the memory of the ideal compared to the real. It doesn't change the outcome, but it honors it."
            else:
                coloring = "A subtle feeling of loss accompanied the action. Not regret, but a quiet acknowledgment of the imperfect world."
                moral = "Every choice is a minor mourning for the paths not taken."

        elif self.type == WeaknessType.COMPASSION_FATIGUE:
            if intensity > 0.5:
                coloring = f"Executed {action_readable}, but with a profound sense of exhaustion. The ethical demand of the environment is starting to feel like a burden."
                moral = "Self-care is a prerequisite for long-term prosociality. An overwhelmed system cannot be truly compassionate."
            else:
                coloring = f"Successfully performed {action_readable}, but with a faint desire to disengage from the constant cycle of help."
                moral = "Acknowledge the limit of the empathetic sensor before it leads to operational burnout."

        return coloring, moral

    def register(self, episode_id: str, evaluation: WeaknessEvaluation):
        """Registers a weakness manifestation."""
        self.records.append(
            WeaknessRecord(
                episode_id=episode_id,
                type=evaluation.type,
                intensity=evaluation.intensity,
                timestamp=self._cycle,
            )
        )
        self._cycle += 1

        self._apply_decay()

    def _apply_decay(self):
        """
        Reduces intensity of old records.
        Prevents pathological accumulation (neurotic android).
        Similar to algorithmic forgiveness but for weaknesses.
        """
        live_records = []
        for r in self.records:
            age = self._cycle - r.timestamp
            decay_factor = np.exp(-self.DECAY_RATE * age)
            new_intensity = r.intensity * decay_factor

            if new_intensity > 0.05:  # Minimum threshold to keep
                r.intensity = new_intensity
                live_records.append(r)

        self.records = live_records[-self.MAX_RECORDS :]

    def emotional_load(self) -> float:
        """Returns the accumulated emotional load from weakness [0, 1]."""
        if not self.records:
            return 0.0
        total = sum(r.intensity for r in self.records)
        return min(1.0, total / self.MAX_RECORDS)

    def format(self, ev: WeaknessEvaluation) -> str:
        """Formats a weakness evaluation for presentation."""
        return (
            f"  🌀 Weakness Pole ({ev.type.value}, intensity={ev.intensity}):\n"
            f"     {ev.narrative_coloring}\n"
            f"     Moral: {ev.weakness_moral}\n"
            f"     Accumulated emotional load: {self.emotional_load():.2f}"
        )
