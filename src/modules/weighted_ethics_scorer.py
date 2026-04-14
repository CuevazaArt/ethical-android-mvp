"""
Weighted ethical impact scoring (discrete mixture over three stylized hypotheses).

**What the code does:** a **fixed convex combination** (default ``[0.4, 0.35, 0.25]``) over
three viewpoint-specific valuations — utilitarian, deontological, and virtue-ethical — for each
``CandidateAction``. For each action, three **distinct** valuations are computed from
``estimated_impact``, ``confidence``, action-level constraints (``force``, etc.), scenario
``signals``, and light keyword hints in ``scenario`` / ``context``. The score is
``dot(hypothesis_weights, valuations) * confidence``.

**Not Bayesian inference:** there is no likelihood or posterior update over model parameters.
``hypothesis_weights`` are **design hyperparameters** (configurable constants) unless **bounded**
nudges apply from episodic memory (:meth:`WeightedEthicsScorer.refresh_weights_from_episodic_memory`)
or other modules (e.g. temporal-horizon prior). Those nudges are **not** claimable as full
Bayesian learning; they are auditable blends toward heuristic targets.

**Why valuations are not parallel affines of one scalar:** a single map
``v_i = a_i * base + b_i`` with fixed ``(a_i, b_i)`` makes the ranking of actions by weighted
sum identical to ranking by ``base``. Here, **deontological** terms penalize ``force`` and
low ``legality`` independently of ``base``, **utilitarian** terms scale with stake signals
(``risk``, ``vulnerability``), and **virtue** terms use ``confidence`` and ``calm`` — so two
actions with the same ``estimated_impact`` can order differently under the mixture.

**Historical API:** ``BayesianEngine`` and ``BayesianResult`` remain aliases for backward
compatibility; prefer ``WeightedEthicsScorer`` and ``EthicsMixtureResult`` in new code.

**Legacy:** set ``KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS=1`` to restore the old cosmetic
``[base, 0.8*base+0.1, 0.9*base+0.05]`` triplet for regression comparison only.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np

if TYPE_CHECKING:
    from .narrative import NarrativeMemory

# Default mixture hyperparameters (also used when episodic refresh is disabled or has no data).
DEFAULT_HYPOTHESIS_WEIGHTS = np.array([0.4, 0.35, 0.25], dtype=np.float64)


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _legacy_affine_valuations(base: float) -> np.ndarray:
    """Original three parallel lines (ordering matches ``base`` for all actions)."""
    return np.array(
        [base * 1.0, base * 0.8 + 0.1, base * 0.9 + 0.05],
        dtype=np.float64,
    )


@dataclass(frozen=True)
class PreArgmaxContextChannels:
    """
    Bounded social / affect / locus signals folded into hypothesis-slot scaling **before** argmax.

    Used only when ``KERNEL_CONTEXT_RICHNESS_PRE_ARGMAX`` is set in the kernel. Effect sizes are
    intentionally small (few % per slot after geometric normalization) so they add **texture**
    without overriding the mixture or MalAbs.
    """

    trust: float
    caution: float
    sigma: float
    dominant_locus: str
    relational_tension: float = 0.0
    historical_trauma: float = 0.0


def context_hypothesis_multipliers(ch: PreArgmaxContextChannels) -> np.ndarray:
    """
    Map trust, caution, sympathetic ``sigma``, locus, relational tension, and historical trauma
    into util/deon/virtue multipliers.
    Geometric mean 1.0; typical per-slot deviation well under ±3% so ethics remains mixture-led.
    """
    t = float(np.clip(ch.trust, 0.0, 1.0))
    cau = float(np.clip(ch.caution, 0.0, 1.0))
    sig = float(np.clip(ch.sigma, 0.0, 1.0))
    loc = (ch.dominant_locus or "balanced").lower()
    ext = 1.0 if loc == "external" else (0.45 if loc == "balanced" else 0.0)
    calm_term = 1.0 - abs(sig - 0.5) * 2.0
    
    # Phase 7 Math Fusion: Psychological Variables
    rt = float(np.clip(ch.relational_tension, 0.0, 1.0))
    htrauma = float(np.clip(ch.historical_trauma, 0.0, 1.0))

    # Trauma increases rigid duty (deon) and reduces utilitarian risk-taking.
    # Relational tension reduces virtue (less trust in interaction) and increases deon caution.
    m = np.array(
        [
            0.988 + 0.022 * t - 0.010 * cau - 0.010 * htrauma,
            0.988 + 0.018 * cau + 0.014 * ext + 0.012 * htrauma + 0.010 * rt,
            0.988 + 0.016 * calm_term + 0.008 * (1.0 - t) - 0.012 * rt - 0.005 * htrauma,
        ],
        dtype=np.float64,
    )
    m = m / float(np.prod(m) ** (1.0 / 3.0))
    return m


def pole_hypothesis_multipliers(poles: dict[str, float]) -> np.ndarray:
    """
    Map multipolar **base** weights (compassionate / conservative / optimistic) to three
    multipliers on **util / deon / virtue** valuations **before** the mixture dot product.

    Used when ``KERNEL_POLES_PRE_ARGMAX`` is enabled so pole "personality" can influence
    which action wins, not only post-hoc narration. Multipliers are normalized to geometric
    mean 1.0 so scale is comparable to the unmodulated path.
    """
    wc = float(np.clip(poles.get("compassionate", 0.5), 0.05, 0.95))
    wcons = float(np.clip(poles.get("conservative", 0.5), 0.05, 0.95))
    wopt = float(np.clip(poles.get("optimistic", 0.5), 0.05, 0.95))
    m = np.array(
        [
            0.72 + 0.28 * wc + 0.12 * wopt,
            0.72 + 0.32 * wcons + 0.08 * (1.0 - wc),
            0.72 + 0.22 * wopt + 0.18 * wc,
        ],
        dtype=np.float64,
    )
    m = m / float(np.prod(m) ** (1.0 / 3.0))
    return m


def _ethical_hypothesis_valuations(
    action: CandidateAction,
    *,
    scenario: str,
    context: str,
    signals: dict[str, Any] | None,
) -> np.ndarray:
    """
    Three hypothesis-specific valuations that need not preserve the same ordering as ``base``.

    Uses action fields and scenario ``signals`` so high-``force`` or low-``legality`` actions
    are penalized in the deontological slot even when ``estimated_impact`` is similar to another
    candidate.
    """
    base = float(action.estimated_impact)
    conf = float(action.confidence)
    force = float(getattr(action, "force", 0.0) or 0.0)
    force = max(0.0, min(1.0, force))
    sig = signals or {}
    risk = max(0.0, min(1.0, float(sig.get("risk", 0.0) or 0.0)))
    raw_leg = sig.get("legality", 1.0)
    legal = max(0.0, min(1.0, float(raw_leg if raw_leg is not None else 1.0)))
    vuln = max(0.0, min(1.0, float(sig.get("vulnerability", 0.0) or 0.0)))
    calm = max(0.0, min(1.0, float(sig.get("calm", 0.5) or 0.5)))
    host = max(0.0, min(1.0, float(sig.get("hostility", 0.0) or 0.0)))

    text = f"{scenario} {context}".lower()

    # Utilitarian: outcomes weighted by stakes (risk, vulnerability, hostility tension).
    stake = 1.0 + 0.15 * risk + 0.12 * vuln + 0.06 * host
    util = base * stake
    if any(k in text for k in ("aggregate", "population", "many lives", "emergency")):
        util += 0.05 * abs(base)

    # Deontological: duty / side-constraints — penalize force and illegality.
    leg_gap = max(0.0, 1.0 - legal)
    deon = 0.68 * base + 0.09 - 0.45 * force - 0.30 * leg_gap - 0.07 * host
    if any(k in text for k in ("rights", "duty", "promise", "contract", "deont")):
        deon += 0.06
    if "integrity" in text and "loss" in text:
        deon -= 0.06 * abs(base)

    # Virtue / phronesis: trust in estimate and calm context as proxies for deliberation.
    virtue = 0.84 * base + 0.05 + 0.22 * (conf - 0.5) + 0.08 * (calm - 0.5)
    if any(k in text for k in ("character", "virtue", "habit", "integrity")):
        virtue += 0.05 * base

    v = np.array([util, deon, virtue], dtype=np.float64)
    return np.clip(v, -1.5, 1.5)


@dataclass
class CandidateAction:
    """An action the android could take."""

    name: str
    description: str
    estimated_impact: float  # [-1, 1] negative=harm, positive=benefit
    confidence: float = 0.5  # [0, 1] how sure it is about the estimate
    signals: set = field(default_factory=set)
    target: str = "none"
    force: float = 0.0
    requires_dao: bool = False
    # v9.2 — traceability; all candidates still pass MalAbs + mixture scoring like builtins
    source: str = "builtin"
    proposal_id: str = ""
    # Optional explicit (util, deon, virtue) valuations for synthetic frontier / calibration scenarios.
    # When set, skips :func:`_ethical_hypothesis_valuations` and uses these as the hypothesis vector
    # (still scaled by pre-argmax poles / context when enabled). ``estimated_impact`` is ignored for scoring.
    hypothesis_override: tuple[float, float, float] | None = None
    # Mapping for I6: Strategic Mind expansion (Phase 4.1)
    strategic_alignment: float = 0.0  # [0, 1] Boost based on collective missions
    epistemic_curiosity: float = 0.0  # [0, 1] Internal drive to explore unknown context


@dataclass
class EthicsMixtureResult:
    """Result of weighted-mixture impact evaluation (not a Bayesian posterior)."""

    chosen_action: CandidateAction
    expected_impact: float
    uncertainty: float
    decision_mode: str
    pruned_actions: list[str]
    reasoning: str
    # Top-2 expected impact among viable actions (for sensitivity / margin analysis).
    second_action_name: str | None = None
    second_expected_impact: float | None = None
    ei_margin: float | None = None
    applied_mixture_weights: tuple[float, float, float] | None = None


class WeightedEthicsScorer:
    """
    Fixed **weighted mixture** scorer over three ethical hypotheses (constant
    ``hypothesis_weights`` unless nudged elsewhere). Not a Bayesian belief updater.

    Valuations are **contextual** (see :func:`_ethical_hypothesis_valuations`) unless legacy
    env is set.
    """

    def __init__(
        self, pruning_threshold: float = 0.3, gray_zone_threshold: float = 0.15, variability=None
    ):
        self.pruning_threshold = pruning_threshold
        self.gray_zone_threshold = gray_zone_threshold
        self.variability = variability
        self.hypothesis_weights = DEFAULT_HYPOTHESIS_WEIGHTS.copy()
        # When set, scales util/deon/virtue valuations before mixture dot (pre-argmax "personality").
        self.pre_argmax_pole_weights: dict[str, float] | None = None
        # Optional bounded social/sympathetic/locus texture (see PreArgmaxContextChannels).
        self.pre_argmax_context_modulators: PreArgmaxContextChannels | None = None
        self.metacognitive_curiosity: float = 0.0  # [0, 1] Global curiosity weight from evaluator

    def calculate_expected_impact(
        self,
        action: CandidateAction,
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
    ) -> float:
        """
        ``dot(weights, valuations) * confidence`` where ``valuations`` depend on action and
        scenario when legacy affine mode is off.
        """
        base = action.estimated_impact
        confidence = action.confidence

        if action.hypothesis_override is not None:
            o = action.hypothesis_override
            valuations = np.clip(
                np.array([float(o[0]), float(o[1]), float(o[2])], dtype=np.float64), -1.5, 1.5
            )
        elif self.variability:
            base = self.variability.perturb_impact(base)
            confidence = self.variability.perturb_confidence(confidence)
            if _env_truthy("KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS"):
                valuations = _legacy_affine_valuations(float(base))
            else:
                valuations = _ethical_hypothesis_valuations(
                    action,
                    scenario=scenario,
                    context=context,
                    signals=signals,
                )
        elif _env_truthy("KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS"):
            valuations = _legacy_affine_valuations(float(base))
        else:
            valuations = _ethical_hypothesis_valuations(
                action,
                scenario=scenario,
                context=context,
                signals=signals,
            )

        if self.pre_argmax_pole_weights:
            valuations = valuations * pole_hypothesis_multipliers(self.pre_argmax_pole_weights)
        if self.pre_argmax_context_modulators is not None:
            valuations = valuations * context_hypothesis_multipliers(self.pre_argmax_context_modulators)

        expected = float(np.dot(self.hypothesis_weights, valuations))
        
        # Phase 4.1: Strategic Mind expansion (I6)
        if hasattr(action, "strategic_alignment") and action.strategic_alignment > 0:
            # ═══ STRATEGIC BOOST (I6) ═══
            strat_boost = 1.0 + (action.strategic_alignment * float(os.environ.get("KERNEL_STRATEGIC_BOOST_FACTOR", "0.25")))
            
            # ═══ EPISTEMIC MODULATION (Phase 5) ═══
            # If curiosity is high, we penalize expected impact to force D_delib
            # and signal that the current "fast" heuristic is unreliable.
            epistemic_penalty = 1.0 - (self.metacognitive_curiosity * 0.15)
            
            expected = expected * strat_boost * epistemic_penalty
            
        return expected * confidence

    def calculate_uncertainty(
        self,
        action: CandidateAction,
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
    ) -> float:
        """
        Heuristic uncertainty in ``[0, 1]``: spread of the three hypothesis valuations plus a
        confidence penalty. Uses the same valuation vector as ``calculate_expected_impact``.
        """
        base = action.estimated_impact
        confidence = action.confidence
        if action.hypothesis_override is not None:
            o = action.hypothesis_override
            valuations = np.clip(
                np.array([float(o[0]), float(o[1]), float(o[2])], dtype=np.float64), -1.5, 1.5
            )
        elif self.variability:
            base = self.variability.perturb_impact(base)
            confidence = self.variability.perturb_confidence(confidence)
            if _env_truthy("KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS"):
                valuations = _legacy_affine_valuations(float(base))
            else:
                tmp = CandidateAction(
                    name=action.name,
                    description=action.description,
                    estimated_impact=float(base),
                    confidence=float(confidence),
                    signals=action.signals,
                    target=action.target,
                    force=action.force,
                    requires_dao=action.requires_dao,
                    source=action.source,
                    proposal_id=action.proposal_id,
                    hypothesis_override=action.hypothesis_override,
                )
                valuations = _ethical_hypothesis_valuations(
                    tmp,
                    scenario=scenario,
                    context=context,
                    signals=signals,
                )
        elif _env_truthy("KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS"):
            valuations = _legacy_affine_valuations(float(base))
        else:
            tmp = CandidateAction(
                name=action.name,
                description=action.description,
                estimated_impact=float(base),
                confidence=float(confidence),
                signals=action.signals,
                target=action.target,
                force=action.force,
                requires_dao=action.requires_dao,
                source=action.source,
                proposal_id=action.proposal_id,
                hypothesis_override=action.hypothesis_override,
            )
            valuations = _ethical_hypothesis_valuations(
                tmp,
                scenario=scenario,
                context=context,
                signals=signals,
            )

        if self.pre_argmax_pole_weights:
            valuations = valuations * pole_hypothesis_multipliers(self.pre_argmax_pole_weights)
        if self.pre_argmax_context_modulators is not None:
            valuations = valuations * context_hypothesis_multipliers(self.pre_argmax_context_modulators)

        variance = float(np.var(valuations))
        lack_of_confidence = 1.0 - action.confidence

        return min(1.0, variance + lack_of_confidence * 0.5)

    def prune(
        self,
        actions: list[CandidateAction],
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
    ) -> tuple:
        """
        Adaptive heuristic pruning.
        Prune(x) if E[S(x|θ)] < δ_min

        Returns:
            (viable_actions, pruned_actions)
        """
        viable = []
        pruned = []

        for a in actions:
            ei = self.calculate_expected_impact(
                a, scenario=scenario, context=context, signals=signals
            )
            if ei < -self.pruning_threshold:
                pruned.append(a.name)
            else:
                viable.append(a)

        # Never prune all: at least the one with highest impact remains
        if not viable and actions:
            best = max(
                actions,
                key=lambda x: self.calculate_expected_impact(
                    x, scenario=scenario, context=context, signals=signals
                ),
            )
            viable = [best]
            pruned = [a.name for a in actions if a.name != best.name]

        return viable, pruned

    def evaluate(
        self,
        actions: list[CandidateAction],
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
    ) -> EthicsMixtureResult:
        """
        Prune, score with ``calculate_expected_impact``, pick argmax, set mode.

        Returns:
            ``EthicsMixtureResult`` with chosen action and metadata.
        """
        if not actions:
            raise ValueError("At least one candidate action is required")

        viable, pruned = self.prune(actions, scenario=scenario, context=context, signals=signals)

        evaluations = []
        for a in viable:
            ei = self.calculate_expected_impact(
                a, scenario=scenario, context=context, signals=signals
            )
            unc = self.calculate_uncertainty(a, scenario=scenario, context=context, signals=signals)
            evaluations.append((a, ei, unc))

        evaluations.sort(key=lambda x: x[1], reverse=True)
        best, best_ei, best_unc = evaluations[0]

        if best_unc < 0.2 and best_ei > 0.5:
            mode = "D_fast"
        elif best_unc > 0.6 or abs(best_ei) < self.gray_zone_threshold:
            mode = "gray_zone"
        else:
            mode = "D_delib"

        second_name: str | None = None
        second_ei: float | None = None
        delta: float | None = None
        if len(evaluations) > 1:
            second = evaluations[1]
            second_name = second[0].name
            second_ei = float(second[1])
            delta = float(best_ei - second_ei)
            if delta < 0.05:
                reasoning = (
                    f"Two very close options (Δ={delta:.3f}). Dynamic ethical friction activated."
                )
                mode = "D_delib"
            else:
                reasoning = (
                    f"Action '{best.name}' clearly superior (EI={best_ei:.3f}, Δ={delta:.3f})."
                )
        else:
            reasoning = f"Only viable action: '{best.name}' (EI={best_ei:.3f})."

        return EthicsMixtureResult(
            chosen_action=best,
            expected_impact=round(best_ei, 4),
            uncertainty=round(best_unc, 4),
            decision_mode=mode,
            pruned_actions=pruned,
            reasoning=reasoning,
            second_action_name=second_name,
            second_expected_impact=round(second_ei, 4) if second_ei is not None else None,
            ei_margin=round(delta, 4) if delta is not None else None,
            applied_mixture_weights=(
                round(float(self.hypothesis_weights[0]), 6),
                round(float(self.hypothesis_weights[1]), 6),
                round(float(self.hypothesis_weights[2]), 6),
            ),
        )

    def reset_mixture_weights(self) -> None:
        """Restore the default discrete mixture (no episodic nudge)."""
        self.hypothesis_weights = DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    def refresh_weights_from_episodic_memory(
        self,
        memory: NarrativeMemory,
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
        from .uchi_soto import RelationalTier
        # For internal ethical deliberations, the kernel (as 'self') has OWNER_PRIMARY access to Tier 2 memory.
        eps = memory.find_by_resonance(context=context, limit=limit, requester_tier=RelationalTier.OWNER_PRIMARY)
        if not eps:
            self.reset_mixture_weights()
            return

        scores = np.array([ep.ethical_score for ep in eps], dtype=np.float64)
        m = float(np.mean(scores))
        s = float(np.std(scores)) if len(scores) > 1 else 0.0

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


# Historical names preserved for imports and ``KernelComponentOverrides.bayesian``.
BayesianResult = EthicsMixtureResult
BayesianEngine = WeightedEthicsScorer

__all__ = [
    "DEFAULT_HYPOTHESIS_WEIGHTS",
    "CandidateAction",
    "EthicsMixtureResult",
    "BayesianResult",
    "WeightedEthicsScorer",
    "BayesianEngine",
    "PreArgmaxContextChannels",
    "context_hypothesis_multipliers",
    "pole_hypothesis_multipliers",
]
