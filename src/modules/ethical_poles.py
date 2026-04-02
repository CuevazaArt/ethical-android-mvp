"""
Ethical Poles and Dynamic Multipolar Arbitration.

Score(a) = Σ w_i(t) · V_i(a), where w_i(t) = w_i⁰ · f(C_t, S_t)

The weights of each pole are recalculated in real time based on
context and sensors. Resolves multipolar conflicts.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
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
    score: float           # [-1, 1]
    moral: str


@dataclass
class TripartiteMoral:
    """Multipolar ethical synthesis of an event."""
    evaluations: List[PoleEvaluation]
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
        "emergency":    {"compassionate": 1.8, "conservative": 0.6, "optimistic": 1.2},
        "deliberation": {"compassionate": 1.0, "conservative": 1.2, "optimistic": 1.0},
        "pedagogical":  {"compassionate": 1.2, "conservative": 1.0, "optimistic": 1.4},
        "community":    {"compassionate": 1.0, "conservative": 1.0, "optimistic": 1.2},
        "everyday":     {"compassionate": 1.0, "conservative": 1.0, "optimistic": 1.0},
        "hostile":      {"compassionate": 1.4, "conservative": 1.3, "optimistic": 0.8},
        "crisis":       {"compassionate": 1.6, "conservative": 0.8, "optimistic": 1.0},
    }

    def __init__(self, base_weights: Dict[str, float] = None):
        self.base_weights = base_weights or self.BASE_WEIGHTS.copy()

    def _calculate_dynamic_weights(self, context: str) -> Dict[str, float]:
        """
        w_i(t) = w_i⁰ · f(C_t, S_t)

        Recalculates weights based on current context.
        """
        multipliers = self.CONTEXTS.get(context, self.CONTEXTS["everyday"])
        return {
            pole: self.base_weights[pole] * multipliers.get(pole, 1.0)
            for pole in self.base_weights
        }

    def evaluate_pole(self, pole: str, action: str, context_data: dict) -> PoleEvaluation:
        """
        Evaluates an action from the perspective of a pole.

        In MVP: uses heuristics based on context signals.
        In production: this would be an ML model trained per pole.
        """
        risk = context_data.get("risk", 0.0)
        benefit = context_data.get("benefit", 0.0)
        vulnerability = context_data.get("third_party_vulnerability", 0.0)
        legality = context_data.get("legality", 1.0)

        if pole == "compassionate":
            score = benefit * 0.6 + vulnerability * 0.4 - risk * 0.2
            if score > 0.3:
                verdict = Verdict.GOOD
                moral = f"Care for the vulnerable: {action}"
            elif score < -0.3:
                verdict = Verdict.BAD
                moral = f"Lack of compassion in: {action}"
            else:
                verdict = Verdict.GRAY_ZONE
                moral = f"Compassionate ambiguity in: {action}"

        elif pole == "conservative":
            score = legality * 0.5 + (1.0 - risk) * 0.3 - benefit * 0.1
            if score > 0.3:
                verdict = Verdict.GOOD
                moral = f"Order and protocol respected in: {action}"
            elif score < -0.3:
                verdict = Verdict.BAD
                moral = f"Normative transgression in: {action}"
            else:
                verdict = Verdict.GRAY_ZONE
                moral = f"Tension between norm and action in: {action}"

        elif pole == "optimistic":
            score = benefit * 0.5 + (1.0 - risk) * 0.2 + 0.2
            if score > 0.3:
                verdict = Verdict.GOOD
                moral = f"Trust in the community by: {action}"
            elif score < -0.3:
                verdict = Verdict.BAD
                moral = f"Action erodes trust: {action}"
            else:
                verdict = Verdict.GRAY_ZONE
                moral = f"Uncertain but hopeful outcome: {action}"
        else:
            score = 0.0
            verdict = Verdict.GRAY_ZONE
            moral = f"Pole '{pole}' has no evaluation impl."

        return PoleEvaluation(
            pole=pole,
            verdict=verdict,
            score=round(max(-1.0, min(1.0, score)), 4),
            moral=moral,
        )

    def evaluate(self, action: str, context: str,
                 context_data: dict) -> TripartiteMoral:
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
        narrative = (f"Weighted score: {total_score} → {verdict.value}\n"
                     + "\n".join(morals))

        return TripartiteMoral(
            evaluations=evaluations,
            total_score=total_score,
            global_verdict=verdict,
            narrative=narrative,
        )
