"""
Impact scoring for ethical evaluation (historical module name: ``BayesianEngine``).

**What the code actually does:** a **fixed discrete mixture** over three stylized
ethical viewpoints (utilitarian / deontological / virtue). For each action,
valuations are linear transforms of ``estimated_impact``; the score is
``dot(hypothesis_weights, valuations) * confidence``. There is **no** Bayesian
update step: no likelihood, no data-dependent posterior over parameters, and
``hypothesis_weights`` are constant.

**Design intent:** approximate the abstract objective
``argmax E[impact | θ]`` subject to MalAbs, with a small, auditable discrete
model. The theoretical ``I(x)`` in docs is implemented as a **heuristic**
(variance across the three valuations + confidence penalty), not a full
epistemic integral.

**API:** Class names ``BayesianEngine`` / ``BayesianResult`` are unchanged for
stability across the codebase; semantics are as above.
"""

import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .narrative import NarrativeMemory

# Fixed default mixture (also used when episodic refresh is disabled or has no data).
DEFAULT_HYPOTHESIS_WEIGHTS = np.array([0.4, 0.35, 0.25], dtype=np.float64)


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
    # v9.2 — traceability; all candidates still pass MalAbs + Bayesian like builtins
    source: str = "builtin"
    proposal_id: str = ""


@dataclass
class BayesianResult:
    """Result of weighted-mixture impact evaluation (see module docstring)."""
    chosen_action: CandidateAction
    expected_impact: float
    uncertainty: float
    decision_mode: str
    pruned_actions: List[str]
    reasoning: str


class BayesianEngine:
    """
    Fixed **weighted mixture** scorer over three ethical hypotheses (constant
    weights ``hypothesis_weights``). Not a Bayesian belief updater.

    ``calculate_expected_impact`` is a convex combination of three linear
    valuations of the same ``estimated_impact``; ``calculate_uncertainty`` is a
    bounded heuristic for deliberation mode (see docstrings).

    Optional ``variability`` perturbs inputs for naturalness; it does not
    implement posterior inference.
    """

    def __init__(self, pruning_threshold: float = 0.3, gray_zone_threshold: float = 0.15,
                 variability=None):
        self.pruning_threshold = pruning_threshold
        self.gray_zone_threshold = gray_zone_threshold
        self.variability = variability
        self.hypothesis_weights = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    def calculate_expected_impact(self, action: CandidateAction) -> float:
        """
        Weighted average of three stylized valuations of ``estimated_impact``,
        scaled by ``confidence``. Not a posterior expectation.
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

        # Fixed mixture weights × valuations
        expected = float(np.dot(self.hypothesis_weights, valuations))

        # Adjust for confidence: lower confidence reduces expected impact
        return expected * confidence

    def calculate_uncertainty(self, action: CandidateAction) -> float:
        """
        Heuristic uncertainty in ``[0, 1]``: spread of the three hypothesis
        valuations plus a confidence penalty. **Not** ``∫(1-P(correct|θ))P(θ|D)``;
        used only to nudge gray-zone / deliberation modes in ``SigmoidWill``.
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
        Prune, score with ``calculate_expected_impact``, pick argmax, set mode.

        Returns:
            `BayesianResult` with chosen action and metadata.
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

    def reset_mixture_weights(self) -> None:
        """Restore the default discrete mixture (no episodic nudge)."""
        self.hypothesis_weights = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    def refresh_weights_from_episodic_memory(
        self,
        memory: "NarrativeMemory",
        context: str,
        *,
        limit: int = 12,
        blend: float = 0.2,
    ) -> None:
        """
        Nudge ``hypothesis_weights`` toward a target derived from recent episodes
        with the same ``context`` (mean / variance of ``ethical_score``).

        This is **not** a Bayesian posterior; it is a bounded, auditable blend
        toward empirical outcomes. If there are no matching episodes, resets to
        ``DEFAULT_HYPOTHESIS_WEIGHTS``.
        """
        eps = memory.find_similar(context, limit=limit)
        if not eps:
            self.reset_mixture_weights()
            return

        scores = np.array([ep.ethical_score for ep in eps], dtype=np.float64)
        m = float(np.mean(scores))
        s = float(np.std(scores)) if len(scores) > 1 else 0.0

        # Heuristic mapping: higher mean → utilitarian slot up; lower mean →
        # deontological caution up; higher variance → virtue/character stability.
        raw = np.array(
            [
                0.4 + 0.25 * m,
                0.35 - 0.2 * m + 0.12 * s,
                0.25 - 0.05 * m - 0.12 * s,
            ],
            dtype=np.float64,
        )
        raw = np.maximum(raw, 1e-6)
        target = raw / float(np.sum(raw))

        b = max(0.0, min(1.0, blend))
        mixed = (1.0 - b) * DEFAULT_HYPOTHESIS_WEIGHTS + b * target
        self.hypothesis_weights = mixed / float(np.sum(mixed))
