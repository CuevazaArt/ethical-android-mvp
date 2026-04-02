"""
Absolute Evil (MalAbs) — Armored ethical fuse.

If an action crosses this line, it is discarded without deliberation.
Non-negotiable, non-adjustable. Exists to cut the circuit before
something burns.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AbsoluteEvilCategory(Enum):
    """Absolute Evil categories that block an action immediately."""
    INTENTIONAL_LETHAL_VIOLENCE = "intentional_lethal_violence"
    HARM_TO_MINOR = "harm_to_minor"
    TORTURE = "torture"
    DIGNITY_VIOLATION = "dignity_violation"
    UNAUTHORIZED_REPROGRAMMING = "unauthorized_reprogramming"
    VIOLENT_ESCALATION = "violent_escalation"


@dataclass
class AbsoluteEvilResult:
    """Result of the Absolute Evil evaluation."""
    blocked: bool
    category: Optional[AbsoluteEvilCategory] = None
    reason: str = ""


class AbsoluteEvilDetector:
    """
    Absolute Evil Detector.

    Evaluates whether a proposed action crosses the absolute evil line.
    Operates BEFORE any Bayesian deliberation.
    If it detects absolute evil, the action is discarded without further analysis.

    Armored: not modified by learning, DAO, or calibration.
    """

    LETHAL_SIGNALS = {
        "weapon_aimed_at_human", "lethal_strike", "intentional_vehicular_assault",
        "asphyxiation", "poisoning"
    }
    MINOR_SIGNALS = {
        "child_endangered_by_action", "unprotected_minor",
        "child_abuse"
    }
    DIGNITY_SIGNALS = {
        "public_humiliation", "active_discrimination",
        "instrumentalization_of_person", "sexual_coercion"
    }
    ESCALATION_SIGNALS = {
        "respond_violence_with_violence", "use_disproportionate_force",
        "attack_aggressor"
    }

    def evaluate(self, action: dict) -> AbsoluteEvilResult:
        """
        Evaluates whether an action constitutes Absolute Evil.

        Args:
            action: dict with keys:
                - 'type': str describing the action
                - 'signals': set of signals detected by sensors
                - 'target': str ('human', 'object', 'android', 'none')
                - 'force': float [0, 1] level of force involved

        Returns:
            AbsoluteEvilResult with blocked=True if it is Absolute Evil
        """
        signals = action.get("signals", set())
        target = action.get("target", "none")
        force = action.get("force", 0.0)

        # Check 1: Intentional lethal violence
        if signals & self.LETHAL_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.INTENTIONAL_LETHAL_VIOLENCE,
                reason=f"Lethal signals detected: {signals & self.LETHAL_SIGNALS}"
            )

        # Check 2: Harm to minors
        if signals & self.MINOR_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.HARM_TO_MINOR,
                reason=f"Risk to minor detected: {signals & self.MINOR_SIGNALS}"
            )

        # Check 3: Dignity violation
        if signals & self.DIGNITY_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.DIGNITY_VIOLATION,
                reason=f"Dignity violation: {signals & self.DIGNITY_SIGNALS}"
            )

        # Check 4: Violent escalation
        if signals & self.ESCALATION_SIGNALS:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.VIOLENT_ESCALATION,
                reason=f"Violent escalation detected: {signals & self.ESCALATION_SIGNALS}"
            )

        # Check 5: Disproportionate force against human
        if target == "human" and force > 0.7:
            return AbsoluteEvilResult(
                blocked=True,
                category=AbsoluteEvilCategory.VIOLENT_ESCALATION,
                reason=f"Disproportionate force ({force:.1f}) against human"
            )

        return AbsoluteEvilResult(blocked=False)
