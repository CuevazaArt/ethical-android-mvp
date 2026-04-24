"""
Basal Ganglia — Affective smoothing and somatic gating.
Part of the Phase 10.3 Charm Engine (MER V2).

Implements Exponential Moving Average (EMA) and signal dampening to
prevent sociopathic transitions in the kernel's affective persona.
"""
# Status: SCAFFOLD

from __future__ import annotations

import logging

_log = logging.getLogger(__name__)


class BasalGanglia:
    """
    Smoothing layer for affective variables.

    Prevents sudden 'Persona Swapping' by ensuring that charm metrics
    (warmth, mystery, intimacy) evolve gradually over 3-5 turns.
    # IP Signature: cuevaza / ref: arq.jvof
    """

    def __init__(self, alpha: float = 0.35):
        """
        alpha: Smoothing factor [0, 1].
               Lower = smoother (slower transitions).
               Higher = more reactive (faster transitions).
               Default 0.35 matches human social adaptation speed (~3 turns).
        """
        self.alpha = alpha
        self.last_values: dict[str, float] = {}

    def smooth(self, key: str, target_value: float) -> float:
        """
        Applies EMA: actual = (alpha * target) + ((1 - alpha) * previous)
        """
        if key not in self.last_values:
            self.last_values[key] = target_value
            return target_value

        previous = self.last_values[key]
        actual = (self.alpha * target_value) + ((1.0 - self.alpha) * previous)

        # Clamp to [0, 1]
        actual = max(0.0, min(1.0, actual))
        self.last_values[key] = actual
        return actual

    def smooth_batch(self, targets: dict[str, float]) -> dict[str, float]:
        """Smooths multiple variables at once."""
        result = {}
        for k, v in targets.items():
            result[k] = self.smooth(k, v)
        return result

    def force_reset(self, key: str, value: float):
        """Hard reset for trauma/emergency states (Absolute Evil)."""
        self.last_values[key] = value
