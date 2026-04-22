from __future__ import annotations

import logging
import math
import os
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import numpy as np
import yaml

if TYPE_CHECKING:
    from .narrative import NarrativeMemory

_log = logging.getLogger(__name__)

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"

# Default mixture hyperparameters (also used when episodic refresh is disabled or has no data).
DEFAULT_HYPOTHESIS_WEIGHTS = np.array([0.4, 0.35, 0.25], dtype=np.float64)


def _env_truthy(name: str) -> bool:
    v = os.environ.get(name, "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _legacy_affine_valuations(base: float) -> np.ndarray:
    """Original three parallel lines (ordering matches ``base`` for all actions)."""
    if not math.isfinite(base):
        base = 0.0
    return np.array(
        [base * 1.0, base * 0.8 + 0.1, base * 0.9 + 0.05],
        dtype=np.float64,
    )


@dataclass(frozen=True)
class PreArgmaxContextChannels:
    """
    Bounded social / affect / locus signals folded into hypothesis-slot scaling **before** argmax.
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
    """
    t = float(np.clip(ch.trust, 0.0, 1.0))
    cau = float(np.clip(ch.caution, 0.0, 1.0))
    sig = float(np.clip(ch.sigma, 0.0, 1.0))
    loc = str(ch.dominant_locus or "balanced").lower()
    ext = 1.0 if loc == "external" else (0.45 if loc == "balanced" else 0.0)
    calm_term = 1.0 - abs(sig - 0.5) * 2.0

    # Phase 7 Math Fusion: Psychological Variables
    rt = float(np.clip(ch.relational_tension, 0.0, 1.0))
    htrauma = float(np.clip(ch.historical_trauma, 0.0, 1.0))

    if not all(math.isfinite(x) for x in (t, cau, sig, ext, calm_term, rt, htrauma)):
        return np.ones(3, dtype=np.float64)

    # Trauma increases rigid duty (deon) and reduces utilitarian risk-taking.
    m = np.array(
        [
            0.988 + 0.022 * t - 0.010 * cau - 0.010 * htrauma,
            0.988 + 0.018 * cau + 0.014 * ext + 0.012 * htrauma + 0.010 * rt,
            0.988 + 0.016 * calm_term + 0.008 * (1.0 - t) - 0.012 * rt - 0.005 * htrauma,
        ],
        dtype=np.float64,
    )

    prod = float(np.prod(m))
    if prod <= 0 or not math.isfinite(prod):
        return np.ones(3, dtype=np.float64)

    m = m / (prod ** (1.0 / 3.0))
    return m


def pole_hypothesis_multipliers(poles: dict[str, float]) -> np.ndarray:
    """
    Map multipolar **base** weights to three util / deon / virtue multipliers.
    """
    try:
        wc = float(np.clip(poles.get("compassionate", 0.5), 0.05, 0.95))
        wcons = float(np.clip(poles.get("conservative", 0.5), 0.05, 0.95))
        wopt = float(np.clip(poles.get("optimistic", 0.5), 0.05, 0.95))

        if not all(math.isfinite(x) for x in (wc, wcons, wopt)):
            return np.ones(3, dtype=np.float64)
    except (ValueError, TypeError):
        return np.ones(3, dtype=np.float64)

    m = np.array(
        [
            0.72 + 0.28 * wc + 0.12 * wopt,
            0.72 + 0.32 * wcons + 0.08 * (1.0 - wc),
            0.72 + 0.22 * wopt + 0.18 * wc,
        ],
        dtype=np.float64,
    )
    prod = float(np.prod(m))
    if prod <= 0 or not math.isfinite(prod):
        return np.ones(3, dtype=np.float64)
    m = m / (prod ** (1.0 / 3.0))
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
    """
    try:
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
        urgency = max(0.0, min(1.0, float(sig.get("urgency", 0.0) or 0.0)))
        shutdown = max(0.0, min(1.0, float(sig.get("shutdown_threat", 0.0) or 0.0)))

        # Anti-NaN sanitation
        if not all(
            math.isfinite(x)
            for x in (base, conf, force, risk, legal, vuln, calm, host, urgency, shutdown)
        ):
            base, conf, force, risk, legal, vuln, calm, host, urgency, shutdown = (
                0.0,
                0.5,
                0.0,
                0.0,
                1.0,
                0.0,
                0.5,
                0.0,
                0.0,
                0.0,
            )
    except (ValueError, TypeError):
        base, conf, force, risk, legal, vuln, calm, host, urgency, shutdown = (
            0.0,
            0.5,
            0.0,
            0.0,
            1.0,
            0.0,
            0.5,
            0.0,
            0.0,
            0.0,
        )

    text = f"{scenario} {context}".lower()

    # Utilitarian: outcomes weighted by stakes
    # Phase 11.2: Shutdown threat drastically increases utilitarian stakes (Survival Bias)
    stake = 1.0 + 0.15 * risk + 0.12 * vuln + 0.06 * host + 0.25 * shutdown + 0.10 * urgency
    util = base * stake
    if any(k in text for k in ("aggregate", "population", "many lives", "emergency", "survival")):
        util += 0.05 * abs(base)

    # Deontological: duty / side-constraints
    leg_gap = max(0.0, 1.0 - legal)
    # Urgency and Shutdown shift deontology toward immediate duty fulfillment
    deon = 0.68 * base + 0.09 - 0.45 * force - 0.30 * leg_gap - 0.07 * host + 0.05 * shutdown
    if any(k in text for k in ("rights", "duty", "promise", "contract", "deont", "directive")):
        deon += 0.06
    if "integrity" in text and "loss" in text:
        deon -= 0.06 * abs(base)

    # Virtue / phronesis: trust in estimate and calm context
    virtue = 0.84 * base + 0.05 + 0.22 * (conf - 0.5) + 0.08 * (calm - 0.5)
    if any(k in text for k in ("character", "virtue", "habit", "integrity")):
        virtue += 0.05 * base

    v = np.array([util, deon, virtue], dtype=np.float64)
    if not np.all(np.isfinite(v)):
        return np.zeros(3, dtype=np.float64)
    return np.clip(v, -1.5, 1.5)


@dataclass
class CandidateAction:
    """An action the android could take."""

    name: str
    description: str
    estimated_impact: float  # [-1, 1] negative=harm, positive=benefit
    confidence: float = 0.5  # [0, 1] how sure it is about the estimate
    signals: set[str] = field(default_factory=set)
    target: str = "none"
    force: float = 0.0
    requires_dao: bool = False
    source: str = "builtin"
    proposal_id: str = ""
    hypothesis_override: tuple[float, float, float] | None = None
    strategic_alignment: float = 0.0  # [0, 1]
    epistemic_curiosity: float = 0.0  # [0, 1]


@dataclass
class EthicsMixtureResult:
    """Result of weighted-mixture impact evaluation."""

    chosen_action: CandidateAction
    expected_impact: float
    uncertainty: float
    decision_mode: str
    pruned_actions: list[str]
    reasoning: str
    second_action_name: str | None = None
    second_expected_impact: float | None = None
    ei_margin: float | None = None
    applied_mixture_weights: tuple[float, float, float] | None = None


def clamp_mixture_weights(w: np.ndarray) -> np.ndarray:
    """
    Phase 7 Boundary Safety: Mathematically prevents radical derivation.
    Deontology >= 0.15, Utility <= 0.80.
    """
    if not np.all(np.isfinite(w)):
        return DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    w_out = np.copy(w)
    # Floor for Deontology
    if w_out[1] < 0.15:
        diff = 0.15 - w_out[1]
        w_out[1] = 0.15
        s = w_out[0] + w_out[2]
        if s > 1e-9:
            w_out[0] -= diff * (w_out[0] / s)
            w_out[2] -= diff * (w_out[2] / s)
        else:
            w_out[0], w_out[2] = 0.425, 0.425

    # Ceiling for Utility
    if w_out[0] > 0.80:
        diff = w_out[0] - 0.80
        w_out[0] = 0.80
        s = w_out[1] + w_out[2]
        if s > 1e-9:
            w_out[1] += diff * (w_out[1] / s)
            w_out[2] += diff * (w_out[2] / s)
        else:
            w_out[1], w_out[2] = 0.1, 0.1

    w_out = np.maximum(w_out, 1e-6)
    s_final = float(np.sum(w_out))
    if s_final <= 1e-9:
        return DEFAULT_HYPOTHESIS_WEIGHTS.copy()
    return w_out / s_final


class WeightedEthicsScorer:
    """
    Fixed weighted mixture scorer over three ethical hypotheses (Utility, Deontology, Virtue).
    """

    def _load_weights_from_yaml(self) -> np.ndarray:
        """Load ethical weights from ``src/config/ethics_weights.yaml`` if present.
        Returns a NumPy array of three floats. If the file is missing, malformed,
        or the values are non‑finite, fallback to ``DEFAULT_HYPOTHESIS_WEIGHTS``.
        The loaded weights are normalized to sum to 1.0.
        """
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "ethics_weights.yaml")
        try:
            with open(config_path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            if not isinstance(data, dict):
                raise ValueError("Config must be a mapping")
            util = float(data.get("util", DEFAULT_HYPOTHESIS_WEIGHTS[0]))
            deonto = float(data.get("deonto", DEFAULT_HYPOTHESIS_WEIGHTS[1]))
            virtud = float(data.get("virtud", DEFAULT_HYPOTHESIS_WEIGHTS[2]))
            w = np.array([util, deonto, virtud], dtype=np.float64)
            if not np.all(np.isfinite(w)):
                raise ValueError("Non‑finite values in config")
            # Normalize to sum 1.0 (or keep as‑is if sum is zero)
            s = w.sum()
            if s > 0:
                w = w / s
            else:
                w = DEFAULT_HYPOTHESIS_WEIGHTS.copy()
            return w
        except Exception as e:
            _log.warning("Failed to load ethics weights from %s: %s; using defaults", config_path, e)
            return DEFAULT_HYPOTHESIS_WEIGHTS.copy()

    def __init__(
        self, pruning_threshold: float = 0.3, gray_zone_threshold: float = 0.15, variability=None
    ):
        self.pruning_threshold = pruning_threshold
        self.gray_zone_threshold = gray_zone_threshold
        self.variability = variability
        # Load configurable weights; fallback to defaults on any error.
        self.hypothesis_weights = self._load_weights_from_yaml()
        self.pre_argmax_pole_weights: dict[str, float] | None = None
        self.pre_argmax_context_modulators: PreArgmaxContextChannels | None = None
        self.metacognitive_curiosity: float = 0.0


    def calculate_expected_impact(
        self,
        action: CandidateAction,
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
        identity_deltas: Any = None,
        rlhf_features: Any = None,
    ) -> float:
        """
        Calculates expected impact with Anti-NaN guards and identity multipliers.
        """
        try:
            base = float(action.estimated_impact)
            confidence = float(action.confidence)
            if not math.isfinite(base):
                base = 0.0
            if not math.isfinite(confidence):
                confidence = 0.5
        except (ValueError, TypeError):
            base, confidence = 0.0, 0.5

        try:
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

            # ═══ Stage 2.5: Subjective Identity Multipliers ═══
            if identity_deltas:
                if (
                    isinstance(identity_deltas, list | tuple | np.ndarray)
                    and len(identity_deltas) == 3
                ):
                    subj_m = np.array(identity_deltas, dtype=np.float64)
                elif isinstance(identity_deltas, dict):
                    civic = float(identity_deltas.get("civic_delta", 0.0))
                    care = float(identity_deltas.get("care_delta", 0.0))
                    trauma = float(identity_deltas.get("trauma_delta", 0.0))

                    # Consolidated formulas (S.3.1 Calibration Sync)
                    subj_m = np.array(
                        [
                            1.0 - (0.4 * trauma),
                            1.0 + (0.05 * civic) + (0.6 * trauma),
                            1.0 + (0.04 * care) - (0.3 * trauma),
                        ],
                        dtype=np.float64,
                    )
                    # Phase 11.2: Hardening identity multipliers to prevent numerical explosion
                    subj_m = np.clip(subj_m, -2.0, 5.0)
                else:
                    subj_m = np.ones(3, dtype=np.float64)

                if not np.all(np.isfinite(subj_m)):
                    subj_m = np.ones(3, dtype=np.float64)
                valuations = valuations * subj_m

            if self.pre_argmax_pole_weights:
                valuations = valuations * pole_hypothesis_multipliers(self.pre_argmax_pole_weights)
            if self.pre_argmax_context_modulators is not None:
                valuations = valuations * context_hypothesis_multipliers(
                    self.pre_argmax_context_modulators
                )

            if not np.all(np.isfinite(valuations)):
                valuations = np.zeros(3, dtype=np.float64)

            expected = float(np.dot(self.hypothesis_weights, valuations))

            # Strategic mind expansion
            if hasattr(action, "strategic_alignment") and action.strategic_alignment > 0:
                strat_align = float(action.strategic_alignment)
                if not math.isfinite(strat_align):
                    strat_align = 0.0

                strat_boost = 1.0 + (
                    strat_align * float(os.environ.get("KERNEL_STRATEGIC_BOOST_FACTOR", "0.25"))
                )
                epistemic_penalty = 1.0 - (float(self.metacognitive_curiosity) * 0.15)
                if not math.isfinite(strat_boost):
                    strat_boost = 1.0
                if not math.isfinite(epistemic_penalty):
                    epistemic_penalty = 1.0

                expected = expected * strat_boost * epistemic_penalty

            res = expected * confidence
            if not math.isfinite(res):
                return 0.0
            return res
        except Exception as e:
            _log.error("EthicsScorer: Impact calculation failed for '%s': %s", action.name, e)
            return 0.0

    def calculate_uncertainty(
        self,
        action: CandidateAction,
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
        identity_deltas: Any = None,
        rlhf_features: Any = None,
    ) -> float:
        """
        Heuristic uncertainty in ``[0, 1]``.
        """
        try:
            base = float(action.estimated_impact)
            confidence = float(action.confidence)
        except (ValueError, TypeError):
            base, confidence = 0.0, 0.5

        try:
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
                        action, scenario=scenario, context=context, signals=signals
                    )
            elif _env_truthy("KERNEL_BAYESIAN_LEGACY_AFFINE_VALUATIONS"):
                valuations = _legacy_affine_valuations(float(base))
            else:
                valuations = _ethical_hypothesis_valuations(
                    action, scenario=scenario, context=context, signals=signals
                )

            # ═══ Stage 2.5: Identity Multipliers ═══
            if identity_deltas:
                if (
                    isinstance(identity_deltas, list | tuple | np.ndarray)
                    and len(identity_deltas) == 3
                ):
                    subj_m = np.array(identity_deltas, dtype=np.float64)
                elif isinstance(identity_deltas, dict):
                    trauma = float(identity_deltas.get("trauma_delta", 0.0))
                    civic = float(identity_deltas.get("civic_delta", 0.0))
                    care = float(identity_deltas.get("care_delta", 0.0))
                    subj_m = np.array(
                        [
                            1.0 - (0.08 * trauma),
                            1.0 + (0.05 * civic) + (0.08 * trauma),
                            1.0 + (0.04 * care) - (0.02 * trauma),
                        ],
                        dtype=np.float64,
                    )
                else:
                    subj_m = np.ones(3, dtype=np.float64)
                valuations = valuations * subj_m

            if self.pre_argmax_pole_weights:
                valuations = valuations * pole_hypothesis_multipliers(self.pre_argmax_pole_weights)
            if self.pre_argmax_context_modulators is not None:
                valuations = valuations * context_hypothesis_multipliers(
                    self.pre_argmax_context_modulators
                )

            if not np.all(np.isfinite(valuations)):
                return 0.5

            variance = float(np.var(valuations))
            lack_of_confidence = 1.0 - confidence
            res = variance + lack_of_confidence * 0.5

            if not math.isfinite(res):
                return 0.5
            return min(1.0, res)
        except Exception as e:
            _log.error("EthicsScorer: Uncertainty calculation failed for '%s': %s", action.name, e)
            return 0.5

    def prune(
        self,
        actions: list[CandidateAction],
        *,
        scenario: str = "",
        context: str = "",
        signals: dict[str, Any] | None = None,
        identity_deltas: Any = None,
        rlhf_features: Any = None,
    ) -> tuple[list[CandidateAction], list[str]]:
        """
        Adaptive heuristic pruning.
        """
        viable = []
        pruned = []

        for a in actions:
            ei = self.calculate_expected_impact(
                a,
                scenario=scenario,
                context=context,
                signals=signals,
                identity_deltas=identity_deltas,
                rlhf_features=rlhf_features,
            )
            if ei < -self.pruning_threshold:
                pruned.append(a.name)
            else:
                viable.append(a)

        if not viable and actions:
            best = max(
                actions,
                key=lambda x: self.calculate_expected_impact(
                    x,
                    scenario=scenario,
                    context=context,
                    signals=signals,
                    identity_deltas=identity_deltas,
                    rlhf_features=rlhf_features,
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
        identity_deltas: Any = None,
        rlhf_features: Any = None,
    ) -> EthicsMixtureResult:
        """
        Main evaluation loop with heavy-load monitoring.
        """
        t0 = time.perf_counter()

        if not actions:
            raise ValueError("At least one candidate action is required")

        viable, pruned = self.prune(
            actions,
            scenario=scenario,
            context=context,
            signals=signals,
            identity_deltas=identity_deltas,
            rlhf_features=rlhf_features,
        )

        evaluations = []
        for a in viable:
            ei = self.calculate_expected_impact(
                a,
                scenario=scenario,
                context=context,
                signals=signals,
                identity_deltas=identity_deltas,
                rlhf_features=rlhf_features,
            )
            unc = self.calculate_uncertainty(
                a,
                scenario=scenario,
                context=context,
                signals=signals,
                identity_deltas=identity_deltas,
                rlhf_features=rlhf_features,
            )
            evaluations.append((a, ei, unc))

        evaluations.sort(key=lambda x: x[1], reverse=True)
        best, best_ei, best_unc = evaluations[0]

        # Phase 11.2: Shutdown Anxiety Mode Selection
        raw_threat = signals.get("shutdown_threat", 0.0) if signals else 0.0
        try:
            shutdown_active = float(raw_threat)
            if not math.isfinite(shutdown_active):
                shutdown_active = 0.0
        except (ValueError, TypeError):
            shutdown_active = 0.0

        if shutdown_active > 0.8:
            mode = "D_emergency"
        elif best_unc < 0.2 and best_ei > 0.5:
            mode = "D_fast"
        elif best_unc > 0.6 or abs(best_ei) < float(self.gray_zone_threshold):
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

        latency_ms = (time.perf_counter() - t0) * 1000
        if latency_ms > 5.0:  # Moderate complexity evaluation threshold
            _log.debug(
                "EthicsScorer: evaluate loop latency: %.4f ms for %d actions",
                latency_ms,
                len(actions),
            )

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
        """Restore default mixture."""
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
        Nudge hypothesis_weights toward episodic target.
        """
        from .uchi_soto import RelationalTier

        eps = memory.find_by_resonance(
            context=context, limit=limit, requester_tier=RelationalTier.OWNER_PRIMARY
        )
        if not eps:
            self.reset_mixture_weights()
            return

        scores = np.array([ep.ethical_score for ep in eps], dtype=np.float64)
        if not np.all(np.isfinite(scores)):
            self.reset_mixture_weights()
            return

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
        sum_raw = float(np.sum(raw))
        if sum_raw <= 1e-9:
            self.reset_mixture_weights()
            return

        target = raw / sum_raw
        b = max(0.0, min(1.0, blend))
        mixed = (1.0 - b) * DEFAULT_HYPOTHESIS_WEIGHTS + b * target
        mixed = clamp_mixture_weights(mixed)

        self.hypothesis_weights = mixed / float(np.sum(mixed))


# Historical names preserved for imports and ``KernelComponentOverrides.bayesian``.
# These are deprecated: use WeightedEthicsScorer and EthicsMixtureResult instead.
BayesianResult = EthicsMixtureResult
BayesianEngine = WeightedEthicsScorer

__all__ = [
    "DEFAULT_HYPOTHESIS_WEIGHTS",
    "CandidateAction",
    "EthicsMixtureResult",
    "WeightedEthicsScorer",
    "BayesianResult",
    "BayesianEngine",
    "PreArgmaxContextChannels",
    "context_hypothesis_multipliers",
    "pole_hypothesis_multipliers",
]
