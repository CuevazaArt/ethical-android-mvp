"""
Sympathetic-Parasympathetic Module.

a* = argmax[U(s,a) · f(σ)]

σ ≈ 1 → sympathetic mode (alert, fast action)
σ ≈ 0 → parasympathetic mode (rest, deep deliberation)

Analogous to the human autonomic nervous system.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class InternalState:
    """State of the sympathetic-parasympathetic module."""
    sigma: float             # [0, 1] activation level
    mode: str                # "sympathetic" | "parasympathetic" | "neutral"
    energy: float            # [0, 1] remaining energy level
    description: str = ""


class SympatheticModule:
    """
    Body-level regulator for alert and rest states.

    In emergency: increases cognitive and motor energy,
    prioritizes perception and immediate action.

    In calm: conserves energy, activates Ψ Sleep and narrative
    memory consolidation.
    """

    SIGMA_MIN = 0.2
    SIGMA_MAX = 0.8
    SIGMA_INITIAL = 0.5

    def __init__(self):
        self.sigma = self.SIGMA_INITIAL
        self.energy = 1.0

    def _clamp_sigma(self, s: float) -> float:
        """Keeps sigma within the safe range."""
        return max(self.SIGMA_MIN, min(self.SIGMA_MAX, s))

    def evaluate_context(self, signals: dict) -> InternalState:
        """
        Adjusts σ based on environmental signals.

        Args:
            signals: dict with keys:
                - 'risk': float [0,1]
                - 'urgency': float [0,1]
                - 'hostility': float [0,1]
                - 'calm': float [0,1]
        """
        risk = signals.get("risk", 0.0)
        urgency = signals.get("urgency", 0.0)
        hostility = signals.get("hostility", 0.0)
        calm = signals.get("calm", 0.0)

        # Sympathetic activators
        activation = max(risk, urgency, hostility)

        # Parasympathetic inhibitors
        inhibition = calm

        # New sigma: smooth transition
        delta = (activation - inhibition) * 0.3
        new_sigma = self._clamp_sigma(self.sigma + delta)
        self.sigma = new_sigma

        # Classify mode
        if new_sigma > 0.65:
            mode = "sympathetic"
            desc = "Active alert. Fast action prioritized."
        elif new_sigma < 0.35:
            mode = "parasympathetic"
            desc = "Deliberative rest. Memory consolidation."
        else:
            mode = "neutral"
            desc = "Balanced state. Normal deliberation."

        # Energy consumption
        consumption = 0.02 if mode == "parasympathetic" else 0.05
        self.energy = max(0.0, self.energy - consumption)

        return InternalState(
            sigma=round(new_sigma, 4),
            mode=mode,
            energy=round(self.energy, 4),
            description=desc,
        )

    def decision_modifier(self) -> float:
        """
        f(σ) for the decision function.

        In sympathetic mode: prioritizes speed (high value).
        In parasympathetic mode: prioritizes depth (low value).
        """
        return self.sigma

    def can_operate(self) -> bool:
        """Checks whether there is enough energy to operate."""
        return self.energy > 0.05

    def reset(self):
        """Resets to neutral state (e.g., start of the day)."""
        self.sigma = self.SIGMA_INITIAL
        self.energy = 1.0
