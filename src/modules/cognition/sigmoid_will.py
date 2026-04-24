"""
Sigmoid Will — Dynamic decision core.

W(x) = 1/(1 + e^(-k*(x - x0))) + λ * I(x)

Will is a smooth curve, not a switch.
Avoids numerical explosions and allows gradual transitions.
"""
# Status: SCAFFOLD

from dataclasses import dataclass

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"


@dataclass
class SigmoidParameters:
    """Parameters of the will function."""

    k: float = 5.0  # Slope (sensitivity)
    x0: float = 0.5  # Equilibrium point
    lambda_i: float = 0.1  # Sensitivity to creative imagination


class SigmoidWill:
    """
    Calculates the android's will to act.

    The sigmoid guarantees:
    - Numerical stability (no explosions)
    - Smooth transitions between deciding and not deciding
    - Connection with creative imagination via lambda
    """

    def __init__(self, params: SigmoidParameters = None):
        self.params = params or SigmoidParameters()

    def calculate(self, x: float, uncertainty: float = 0.0) -> float:
        """
        Calculates the will to act.
        Numerical Stability: Uses defensive clipping and math.isfinite checks to prevent NaN.
        """
        import math

        # Swarm Rule: Anti-NaN Hardening
        if not math.isfinite(x):
            x = 0.0
        if not math.isfinite(uncertainty):
            uncertainty = 0.0

        k = float(self.params.k)
        x0 = float(self.params.x0)
        lam = float(self.params.lambda_i)

        if not all(math.isfinite(v) for v in (k, x0, lam)):
            return 0.5  # Safe fallback

        # Defensive clipping for exponential to avoid overflow in extreme cases
        # e^500 is huge, e^-500 is tiny. Clipping at 50 to 100 is usually enough for sigmoid.
        exp_input = -k * (x - x0)
        if not math.isfinite(exp_input):
            exp_input = 0.0

        # Clip to prevent math.exp overflow (e^700 ~ 1e304, near float64 max)
        exp_input = max(-500.0, min(500.0, exp_input))

        try:
            sigmoid = 1.0 / (1.0 + math.exp(exp_input))
        except OverflowError:
            # If exp_input is very negative, math.exp(exp_input) -> 0, sigmoid -> 1
            # If exp_input is very positive, math.exp(exp_input) -> inf, sigmoid -> 0
            sigmoid = 0.0 if exp_input > 0 else 1.0

        creativity = lam * uncertainty
        if not math.isfinite(creativity):
            creativity = 0.0

        res = float(sigmoid + creativity)
        # Final result check
        if not math.isfinite(res):
            return 0.5

        return res

    def decide(self, x: float, uncertainty: float = 0.0, threshold: float = 0.5) -> dict:
        """
        Decides whether to act and in which mode.

        Returns:
            dict with:
            - 'act': bool
            - 'will': float
            - 'mode': 'D_fast' | 'D_delib' | 'zona_gris'
        """
        w = self.calculate(x, uncertainty)

        if w > 0.8:
            mode = "D_fast"  # Fast moral reflex
        elif w > threshold:
            mode = "D_delib"  # Deep deliberation
        else:
            mode = "gray_zone"  # Requires more information or DAO

        return {
            "act": w > threshold,
            "will": round(w, 4),
            "mode": mode,
        }
