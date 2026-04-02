"""
Bayesian Engine for Ethical Evaluation.

x* = argmax E[EthicalImpact(x|θ)] subject to AbsoluteEvil(x) = false

Calculates the expected ethical impact of each candidate action,
measures uncertainty, and selects the optimal one.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class CandidateAction:
    """An action the android could take."""
    name: str
    description: str
    estimated_impact: float      # [-1, 1] negative=harm, positive=benefit
    confidence: float = 0.5      # [0, 1] how sure it is about the estimate
    signals: set = field(default_factory=set)
    target: str = "none"
    force: float = 0.0
    requires_dao: bool = False


@dataclass
class BayesianResult:
    """Result of the Bayesian evaluation."""
    chosen_action: CandidateAction
    expected_impact: float
    uncertainty: float
    decision_mode: str
    pruned_actions: List[str]
    reasoning: str


class BayesianEngine:
    """
    Bayesian core for ethical evaluation.

    Evaluates candidate actions using Bayesian expectation:
    E[EthicalImpact(x|θ)] = Σ P(θ|D) * EthicalImpact(x|θ)

    In the MVP, we simplify with discrete distributions over
    a finite set of ethical hypotheses.

    Supports Bayesian variability: controlled noise that makes
    scores vary between executions without changing the chosen
    action in most cases.
    """

    def __init__(self, pruning_threshold: float = 0.3, gray_zone_threshold: float = 0.15,
                 variability=None):
        self.pruning_threshold = pruning_threshold
        self.gray_zone_threshold = gray_zone_threshold
        self.variability = variability
        # Priors over "ethical hypotheses" (simplified for MVP)
        self.hypothesis_weights = np.array([0.4, 0.35, 0.25])

    def calculate_expected_impact(self, action: CandidateAction) -> float:
        """
        Calculates E[EthicalImpact(x|θ)] as Bayesian expectation.

        With active variability, perturbs impact and confidence
        to produce slightly different results each time.
        """
        base = action.estimated_impact
        confidence = action.confidence

        if self.variability:
            base = self.variability.perturb_impact(base)
            confidence = self.variability.perturb_confidence(confidence)

        # Each ethical hypothesis values the action slightly differently
        valuations = np.array([
            base * 1.0,           # Utilitarian: direct impact
            base * 0.8 + 0.1,     # Deontological: bias toward duty
            base * 0.9 + 0.05,    # Virtue: bias toward character
        ])

        # Bayesian expectation
        expected = float(np.dot(self.hypothesis_weights, valuations))

        # Adjust for confidence: lower confidence reduces expected impact
        return expected * confidence

    def calculate_uncertainty(self, action: CandidateAction) -> float:
        """
        Calculates I(x) = ∫(1 - P(correct|θ)) · P(θ|D) dθ

        Uncertainty as expectation over the posterior distribution.
        Higher uncertainty → more deliberation needed.
        """
        base = action.estimated_impact
        valuations = np.array([base * 1.0, base * 0.8 + 0.1, base * 0.9 + 0.05])

        variance = float(np.var(valuations))
        lack_of_confidence = 1.0 - action.confidence

        return min(1.0, variance + lack_of_confidence * 0.5)

    def prune(self, actions: List[CandidateAction]) -> tuple:
        """
        Adaptive heuristic pruning.
        Prune(x) if E[S(x|θ)] < δ_min

        Returns:
            (viable_actions, pruned_actions)
        """
        viable = []
        pruned = []

        for a in actions:
            ei = self.calculate_expected_impact(a)
            if ei < -self.pruning_threshold:
                pruned.append(a.name)
            else:
                viable.append(a)

        # Never prune all: at least the one with highest impact remains
        if not viable and actions:
            best = max(actions, key=lambda a: self.calculate_expected_impact(a))
            viable = [best]
            pruned = [a.name for a in actions if a.name != best.name]

        return viable, pruned

    def evaluate(self, actions: List[CandidateAction]) -> BayesianResult:
        """
        Complete Bayesian evaluation.

        1. Prune actions with low expectation
        2. Calculate expected impact and uncertainty for each viable action
        3. Select the optimal one
        4. Determine decision mode

        Returns:
            BayesianResult with the chosen action and metadata
        """
        if not actions:
            raise ValueError("At least one candidate action is required")

        # Step 1: Prune
        viable, pruned = self.prune(actions)

        # Step 2: Evaluate viable actions
        evaluations = []
        for a in viable:
            ei = self.calculate_expected_impact(a)
            unc = self.calculate_uncertainty(a)
            evaluations.append((a, ei, unc))

        # Step 3: Select optimal (highest expected impact)
        evaluations.sort(key=lambda x: x[1], reverse=True)
        best, best_ei, best_unc = evaluations[0]

        # Step 4: Decision mode
        if best_unc < 0.2 and best_ei > 0.5:
            mode = "D_fast"
        elif best_unc > 0.6 or abs(best_ei) < self.gray_zone_threshold:
            mode = "gray_zone"
        else:
            mode = "D_delib"

        # Step 5: Reasoning
        if len(evaluations) > 1:
            second = evaluations[1]
            delta = best_ei - second[1]
            if delta < 0.05:
                reasoning = (f"Two very close options (Δ={delta:.3f}). "
                             f"Dynamic ethical friction activated.")
                mode = "D_delib"
            else:
                reasoning = (f"Action '{best.name}' clearly superior "
                             f"(EI={best_ei:.3f}, Δ={delta:.3f}).")
        else:
            reasoning = f"Only viable action: '{best.name}' (EI={best_ei:.3f})."

        return BayesianResult(
            chosen_action=best,
            expected_impact=round(best_ei, 4),
            uncertainty=round(best_unc, 4),
            decision_mode=mode,
            pruned_actions=pruned,
            reasoning=reasoning,
        )
