"""
PAD affect projection + archetype mixture (post-decision layer).

Maps sympathetic σ, multipolar total_score, and locus dominance into
v = (P, A, D) ∈ [0,1]³, then softmax weights over fixed prototypes.

Does not influence MalAbs, buffer, Bayesian choice, poles, or will — only
records tone for narrative / downstream presentation (see docs §7).
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass

from .locus import LocusEvaluation
from .sympathetic import SympatheticModule

Vec3 = tuple[float, float, float]


@dataclass(frozen=True)
class AffectArchetype:
    """Single PAD prototype in [0,1]³."""

    id: str
    center: Vec3
    label: str = ""


@dataclass
class AffectProjection:
    """Result of PAD vector + archetype mixture (auditable side channel)."""

    pad: Vec3
    weights: dict[str, float]
    dominant_archetype_id: str
    beta: float


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def activation_from_sigma(sigma: float) -> float:
    """A from σ using SympatheticModule range (spec §7.1)."""
    smin = SympatheticModule.SIGMA_MIN
    smax = SympatheticModule.SIGMA_MAX
    if smax <= smin:
        return 0.5
    return _clamp01((sigma - smin) / (smax - smin))


def valence_from_moral_score(total_score: float, score_lambda: float = 1.0) -> float:
    """P from weighted ethical score: 0.5 + 0.5 * tanh(λ·score) (spec §7.1)."""
    return _clamp01(0.5 + 0.5 * math.tanh(score_lambda * total_score))


def dominance_from_locus(locus_eval: LocusEvaluation) -> float:
    """D from dominant_locus (spec §7.1)."""
    m = {
        "internal": 1.0,
        "balanced": 0.5,
        "external": 0.0,
    }
    return m.get(locus_eval.dominant_locus, 0.5)


def euclidean(a: Vec3, b: Vec3) -> float:
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def softmax_weights_over_prototypes(
    v: Vec3, archetypes: Sequence[AffectArchetype], beta: float
) -> dict[str, float]:
    """
    w_k = exp(-β · d_k) / Σ_j exp(-β · d_j), d_k = ||v - c_k||₂ (spec §7.3).
    """
    if not archetypes:
        return {}
    distances = [euclidean(v, a.center) for a in archetypes]
    logits = [-beta * d for d in distances]
    m = max(logits)
    exps = [math.exp(x - m) for x in logits]
    s = sum(exps)
    if s <= 0:
        n = len(archetypes)
        return {a.id: 1.0 / n for a in archetypes}
    return {a.id: e / s for a, e in zip(archetypes, exps)}


# Default library: six separated points in the unit cube (spec §7.2, N≈6–8).
DEFAULT_ARCHETYPES: list[AffectArchetype] = [
    AffectArchetype("calma_deliberativa", (0.62, 0.22, 0.55), "calm deliberation"),
    AffectArchetype("alerta_compasiva", (0.72, 0.82, 0.42), "alert compassion"),
    AffectArchetype("tension_externa", (0.38, 0.78, 0.18), "external tension"),
    AffectArchetype("agencia_interna", (0.58, 0.48, 0.92), "internal agency"),
    AffectArchetype("tono_sombrio", (0.28, 0.40, 0.22), "bleak / low valence"),
    AffectArchetype("equilibrio", (0.50, 0.50, 0.50), "balanced mix"),
]


class PADArchetypeEngine:
    """
    Computes PAD + prototype weights after the ethical core has decided.
    """

    def __init__(
        self,
        archetypes: Sequence[AffectArchetype] = None,
        beta: float = 4.0,
        score_lambda: float = 1.0,
    ):
        self.archetypes: list[AffectArchetype] = (
            list(archetypes) if archetypes is not None else list(DEFAULT_ARCHETYPES)
        )
        self.beta = beta
        self.score_lambda = score_lambda

    def project(
        self,
        sigma: float,
        total_score: float,
        locus_eval: LocusEvaluation,
    ) -> AffectProjection:
        p = valence_from_moral_score(total_score, self.score_lambda)
        a = activation_from_sigma(sigma)
        d = dominance_from_locus(locus_eval)
        v: Vec3 = (p, a, d)
        weights = softmax_weights_over_prototypes(v, self.archetypes, self.beta)
        dominant = max(weights, key=lambda k: weights[k]) if weights else ""
        return AffectProjection(
            pad=v,
            weights=weights,
            dominant_archetype_id=dominant,
            beta=self.beta,
        )
