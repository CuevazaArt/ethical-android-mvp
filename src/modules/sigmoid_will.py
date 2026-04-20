"""
Sigmoid Will — Dynamic decision core.

W(x) = 1/(1 + e^(-k*(x - x0))) + λ * I(x)

Will is a smooth curve, not a switch.
Avoids numerical explosions and allows gradual transitions.
"""

from dataclasses import dataclass

import numpy as np

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
        \"\"\"
        Calculates the will to act.

        Args:
            x: input stimulus (estimated ethical impact)
            uncertainty: heuristic I(x) from impact scoring (see ``weighted_ethics_scorer``)

        Returns:
            float [0, 1+λ] where values > 0.5 incline toward acting
        \"\"\"
        import math
        # Phase 13 Hardening: Anti-NaN guard
        if not math.isfinite(x): x = 0.0
        if not math.isfinite(uncertainty): uncertainty = 0.0

        k = self.params.k
        x0 = self.params.x0
        lam = self.params.lambda_i

        # Defensive clipping for exponential to avoid overflow in extreme cases
        exp_input = -k * (x - x0)
        exp_input = max(-500, min(500, exp_input))

        sigmoid = 1.0 / (1.0 + np.exp(exp_input))
        creativity = lam * uncertainty

        res = float(sigmoid + creativity)
        return res if math.isfinite(res) else 0.5

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
