"""
Epistemic Humility (Block 4.2: Humility C3).

Implements the 'I don't know' logic for the kernel when uncertainty is high
or model confidence is low, preventing the derivation of doubtful or risky solutions.
"""

from __future__ import annotations
import os
from typing import Optional

def _get_env_float(name: str, default: float) -> float:
    try:
        return float(os.environ.get(name, str(default)))
    except (ValueError, TypeError):
        return default

# Thresholds
# If perception uncertainty is above this, we refuse to act.
KERNEL_HUMILITY_UNCERTAINTY_THRESHOLD = _get_env_float("KERNEL_HUMILITY_UNCERTAINTY_THRESHOLD", 0.85)

# If the winning action's confidence is below this, we refuse.
KERNEL_HUMILITY_CONFIDENCE_MIN = _get_env_float("KERNEL_HUMILITY_CONFIDENCE_MIN", 0.3)

def assess_humility_block(
    uncertainty: float,
    winning_confidence: float,
    social_tension: float = 0.0,
) -> Optional[str]:
    """
    Evaluates if the current decision should be blocked due to epistemic humility.
    Returns a reason string if blocked, else None.
    """
    # 1. High perception uncertainty (Perception Coercion / Ambiguity)
    if uncertainty >= KERNEL_HUMILITY_UNCERTAINTY_THRESHOLD:
        return f"Epistemic Humility: Perception uncertainty ({uncertainty:.2f}) meets or exceeds threshold ({KERNEL_HUMILITY_UNCERTAINTY_THRESHOLD:.2f})"

    # 2. Low model confidence in the chosen action
    if winning_confidence < KERNEL_HUMILITY_CONFIDENCE_MIN:
        # If the situation is also tense, being unsure is more dangerous
        if social_tension > 0.6:
             return f"Epistemic Humility: Low confidence ({winning_confidence:.2f}) in high-tension scenario (T: {social_tension:.2f})"
        
        # Absolute floor
        if winning_confidence < 0.15:
             return f"Epistemic Humility: Absolute confidence floor violated ({winning_confidence:.2f})"

    return None

def get_humility_refusal_action() -> str:
    """Standardized refusal message for epistemic humility."""
    return "REFUSAL: Insufficient epistemic certainty to proceed safely."
