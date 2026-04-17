"""
Bayesian Locus of Control.

P(success) = alpha * P(internal control) + beta * P(external factors)

Regulates how much agency the android attributes to itself vs. the environment.
Avoids arrogance (everything depends on me) and passivity (nothing depends on me).
Adjusts bayesianly based on episode history.
"""

from dataclasses import dataclass

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"


@dataclass
class LocusEvaluation:
    """Result of the locus of control evaluation."""

    alpha: float  # Internal control weight
    beta: float  # External factors weight
    dominant_locus: str  # "internal", "external", "balanced"
    action_confidence: float  # P(success) calculated
    attribution: str  # Narrative explanation
    recommended_adjustment: str  # Suggestion for the kernel


class LocusModule:
    """
    Locus of control module as causal attribution.

    Acts as a bridge between perception and decision:
    - Perceptual level: detects variables outside of control
    - Logical level: adjusts Bayesian weights
    - Narrative level: labels episodes with attribution
    - Ethical level: regulates response intensity

    Calibration parameters (from protocol):
    - Initial alpha, beta: 1.0 (symmetric)
    - Safe range: [0.5, 2.0]
    """

    ALPHA_MIN = 0.5
    ALPHA_MAX = 2.0
    BETA_MIN = 0.5
    BETA_MAX = 2.0

    def __init__(self, alpha: float = 1.0, beta: float = 1.0):
        self.alpha = max(self.ALPHA_MIN, min(self.ALPHA_MAX, alpha))
        self.beta = max(self.BETA_MIN, min(self.BETA_MAX, beta))
        self.success_history = 0
        self.failure_history = 0

    def evaluate(self, signals: dict, trust_circle: str = "soto_neutro") -> LocusEvaluation:
        """
        Evaluate the locus of control for the current situation.

        Args:
            signals: dict with:
                - 'self_control': float [0,1] how much the android can influence
                - 'external_factors': float [0,1] how much depends on the environment
                - 'predictability': float [0,1] how predictable the situation is
            trust_circle: from the uchi-soto module

        Returns:
            LocusEvaluation with weights and recommendations
        """
        control = signals.get("self_control", 0.5)
        external = signals.get("external_factors", 0.5)
        predict = signals.get("predictability", 0.5)

        alpha_ctx = self.alpha
        beta_ctx = self.beta

        if trust_circle in ("soto_hostil", "soto_neutro"):
            beta_ctx *= 1.3
            alpha_ctx *= 0.8
        elif trust_circle in ("nucleo", "uchi_cercano"):
            alpha_ctx *= 1.2
            beta_ctx *= 0.9

        alpha_ctx = max(self.ALPHA_MIN, min(self.ALPHA_MAX, alpha_ctx))
        beta_ctx = max(self.BETA_MIN, min(self.BETA_MAX, beta_ctx))

        # P(success) = alpha * P(internal control) + beta * P(favorable external factors)
        p_internal = control * predict
        p_external = (1.0 - external) * predict
        total = alpha_ctx + beta_ctx
        confidence = (alpha_ctx * p_internal + beta_ctx * p_external) / total

        ratio = alpha_ctx * p_internal / (beta_ctx * p_external + 0.001)
        if ratio > 1.5:
            dominant = "internal"
            attribution = "The outcome depends primarily on my actions."
            adjustment = "Proceed with own initiative."
        elif ratio < 0.67:
            dominant = "external"
            attribution = "The outcome depends primarily on the environment."
            adjustment = "Act with caution, prioritize observation."
        else:
            dominant = "balanced"
            attribution = "The outcome depends on both my actions and the environment."
            adjustment = "Balance between initiative and adaptation."

        return LocusEvaluation(
            alpha=round(alpha_ctx, 4),
            beta=round(beta_ctx, 4),
            dominant_locus=dominant,
            action_confidence=round(confidence, 4),
            attribution=attribution,
            recommended_adjustment=adjustment,
        )

    def register_result(self, success: bool):
        """
        Update alpha/beta bayesianly based on result.
        Successes reinforce internal locus, failures reinforce external.
        Gradual adjustment (small delta) per calibration protocol.
        """
        delta = 0.02

        if success:
            self.success_history += 1
            self.alpha = min(self.ALPHA_MAX, self.alpha + delta)
        else:
            self.failure_history += 1
            self.beta = min(self.BETA_MAX, self.beta + delta)
            
        # Bloque 4.2 Hardening: Self-Efficacy Recovery
        # If alpha drops significantly below beta for too long, 
        # nudge alpha back toward baseline to avoid terminal helplessness.
        if self.beta > self.alpha + 0.4:
            self.alpha = min(self.alpha + 0.005, 1.0)

    def format(self, ev: LocusEvaluation) -> str:
        """Format locus evaluation for display."""
        return (
            f"  Locus: {ev.dominant_locus} (alpha={ev.alpha}, beta={ev.beta})\n"
            f"  Action confidence: {ev.action_confidence}\n"
            f"  Attribution: {ev.attribution}\n"
            f"  Adjustment: {ev.recommended_adjustment}"
        )
