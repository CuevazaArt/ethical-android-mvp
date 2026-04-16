"""
Ethical Poles and Dynamic Multipolar Arbitration.

Score(a) = Σ w_i(t) · V_i(a), where w_i(t) = w_i⁰ · f(C_t, S_t)

The weights of each pole are recalculated in real time based on
context and sensors. Resolves multipolar conflicts.

Per-pole scores use :class:`LinearPoleEvaluator` (JSON-configurable); see ADR 0004.
"""

from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    GOOD = "Good"
    BAD = "Bad"
    GRAY_ZONE = "Gray Zone"


@dataclass
class PoleEvaluation:
    """Evaluation of an action from an ethical pole."""

    pole: str
    verdict: Verdict
    score: float  # [-1, 1]
    moral: str


@dataclass
class TripartiteMoral:
    """Multipolar ethical synthesis of an event."""

    evaluations: list[PoleEvaluation]
    total_score: float
    global_verdict: Verdict
    narrative: str


class EthicalPoles:
    """
    Multipolar evaluation system with dynamic weighting.

    Each pole evaluates an action from its ethical perspective.
    Weights are adjusted based on context (emergency, deliberation,
    pedagogy, community).
    """

    # Base weights for each pole (w_i⁰) — adjustable by DAO
    BASE_WEIGHTS = {
        "compassionate": 0.5,
        "conservative": 0.5,
        "optimistic": 0.5,
    }

    # Contextual multipliers: f(C_t, S_t)
    CONTEXTS = {
        "emergency": {"compassionate": 1.8, "conservative": 0.6, "optimistic": 1.2},
        "deliberation": {"compassionate": 1.0, "conservative": 1.2, "optimistic": 1.0},
        "pedagogical": {"compassionate": 1.2, "conservative": 1.0, "optimistic": 1.4},
        "community": {"compassionate": 1.0, "conservative": 1.0, "optimistic": 1.2},
        "everyday": {"compassionate": 1.0, "conservative": 1.0, "optimistic": 1.0},
        "hostile": {"compassionate": 1.4, "conservative": 1.3, "optimistic": 0.8},
        "crisis": {"compassionate": 1.6, "conservative": 0.8, "optimistic": 1.0},
    }

    def __init__(
        self,
        base_weights: dict[str, float] | None = None,
        linear_config_path: str | None = None,
    ):
        self.base_weights = base_weights or self.BASE_WEIGHTS.copy()
        from .pole_linear import LinearPoleEvaluator

        self._linear = LinearPoleEvaluator.load(linear_config_path)

    def _calculate_dynamic_weights(self, context: str) -> dict[str, float]:
        """
        w_i(t) = w_i⁰ · f(C_t, S_t)

        Recalculates weights based on current context.
        """
        multipliers = self.CONTEXTS.get(context, self.CONTEXTS["everyday"])
        return {
            pole: self.base_weights[pole] * multipliers.get(pole, 1.0) for pole in self.base_weights
        }

    def evaluate_pole(self, pole: str, action: str, context_data: dict) -> PoleEvaluation:
        """
        Evaluates an action from the perspective of a pole.

        Uses :class:`LinearPoleEvaluator` (see ``pole_linear_default.json`` or
        ``KERNEL_POLE_LINEAR_CONFIG``). Unknown poles fall back to a gray-zone stub.
        """
        ev = self._linear.evaluate(pole, action, context_data)
        if ev is not None:
            return ev

        return PoleEvaluation(
            pole=pole,
            verdict=Verdict.GRAY_ZONE,
            score=0.0,
            moral=f"Pole '{pole}' has no evaluation impl.",
        )

    def evaluate(self, action: str, context: str, context_data: dict) -> TripartiteMoral:
        """
        Complete multipolar evaluation with dynamic weighting.

        Score(a) = Σ w_i(t) · V_i(a)

        Returns:
            TripartiteMoral with evaluation from each pole
        """
        weights = self._calculate_dynamic_weights(context)

        evaluations = []
        total_score = 0.0
        total_weight = 0.0

        for pole in self.base_weights:
            ev = self.evaluate_pole(pole, action, context_data)
            evaluations.append(ev)
            total_score += weights[pole] * ev.score
            total_weight += weights[pole]

        total_score = round(total_score / total_weight if total_weight > 0 else 0.0, 4)

        if total_score > 0.2:
            verdict = Verdict.GOOD
        elif total_score < -0.2:
            verdict = Verdict.BAD
        else:
            verdict = Verdict.GRAY_ZONE

        morals = [f"  {ev.pole}: {ev.moral}" for ev in evaluations]
        narrative = f"Weighted score: {total_score} → {verdict.value}\n" + "\n".join(morals)

        return TripartiteMoral(
            evaluations=evaluations,
            total_score=total_score,
            global_verdict=verdict,
            narrative=narrative,
        )
