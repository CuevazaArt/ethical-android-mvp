"""
GWT-lite salience: read-only attention weights over existing signal axes.

Does not reorder the kernel pipeline (phase 1). Produces a normalized vector
for telemetry, UI, and optional LLM nuance — not a policy change.

See docs/proposals/README.md (Fase 2).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from .ethical_reflection import ReflectionSnapshot
from .sympathetic import InternalState
from .uchi_soto import SocialEvaluation

__all__ = ("SalienceMap", "SalienceSnapshot", "salience_to_llm_context")


def _fin_unit_interval(x: Any, *, default: float = 0.0) -> float:
    """Map unknown / non-finite input to a finite value in ``[0, 1]`` (salience pre-normalization)."""
    try:
        v = float(x)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(v):
        return default
    return max(0.0, min(1.0, v))


@dataclass(frozen=True)
class SalienceSnapshot:
    """
    Non-negative weights over axes that sum to 1 (attention budget).
    `dominant_focus` is the axis with largest weight (ties: lexicographic).
    """

    weights: dict[str, float]
    """Keys: risk, social, body, ethical_conflict, epistemic_curiosity."""

    dominant_focus: str
    """Which axis 'wins' the competition for salience this tick."""

    raw_scores: dict[str, float]
    """Pre-normalization [0,1] scores for audit."""


class SalienceMap:
    """
    Maps environment + reflection into a salience distribution. Pure; no side effects.
    """

    AXIS_ORDER = ("risk", "social", "body", "ethical_conflict", "epistemic_curiosity")

    def compute(
        self,
        signals: dict[str, float],
        state: InternalState,
        social_eval: SocialEvaluation,
        reflection: ReflectionSnapshot | None,
        curiosity: float = 0.0,
    ) -> SalienceSnapshot:
        """
        Calculates the current salience distribution across ethical and somatic axes.

        Args:
            signals: The environmental signals (risk, urgency, etc.).
            state: The current internal autonomic state (sympathetic/parasympathetic).
            social_eval: The social context and trust evaluation.
            reflection: The results of the internal ethical reflection Lobe.
            curiosity: The current epistemic drive/curiosity coefficient.

        Returns:
            A SalienceSnapshot containing normalized attention weights.
        """
        risk = _fin_unit_interval(signals.get("risk", 0.0))

        # Social salience: hostility + defensive posture + dialectic tension
        hostility = _fin_unit_interval(signals.get("hostility", 0.0))
        caution = _fin_unit_interval(social_eval.caution_level)
        dialectic = 1.0 if social_eval.dialectic_active else 0.0
        social_mix = 0.45 * hostility + 0.35 * caution + 0.2 * dialectic
        social_raw = _fin_unit_interval(social_mix)

        # Body / autonomic: sympathetic load proxy
        body_raw = _fin_unit_interval(state.sigma)

        if reflection is not None:
            eth_raw = _fin_unit_interval(getattr(reflection, "strain_index", 0.0))
        else:
            eth_raw = 0.0

        raw = {
            "risk": risk,
            "social": social_raw,
            "body": body_raw,
            "ethical_conflict": eth_raw,
            "epistemic_curiosity": _fin_unit_interval(curiosity),
        }

        ssum = sum(raw.values())
        if not math.isfinite(ssum):
            ssum = 0.0
        if ssum <= 1e-9:
            u = 1.0 / float(len(self.AXIS_ORDER))
            weights = {k: round(u, 4) for k in self.AXIS_ORDER}
        else:
            weights = {k: round(raw[k] / ssum, 4) for k in self.AXIS_ORDER}

        mx = max(weights[k] for k in self.AXIS_ORDER)
        dominant = next(k for k in self.AXIS_ORDER if weights[k] == mx)

        return SalienceSnapshot(
            weights=weights,
            dominant_focus=dominant,
            raw_scores=raw,
        )


def salience_to_llm_context(snapshot: SalienceSnapshot | None) -> str:
    """One line for communicate() — tone only."""
    if snapshot is None:
        return ""
    w = snapshot.weights
    return (
        f"Attention focus (read-only): dominant={snapshot.dominant_focus} "
        f"(risk={w['risk']}, social={w['social']}, body={w['body']}, "
        f"ethical_tension={w['ethical_conflict']}, curiosity={w['epistemic_curiosity']})."
    )
