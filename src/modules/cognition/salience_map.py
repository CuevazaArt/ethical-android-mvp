"""
GWT-lite salience: read-only attention weights over existing signal axes.

Does not reorder the kernel pipeline (phase 1). Produces a normalized vector
for telemetry, UI, and optional LLM nuance ΓÇö not a policy change.

See docs/proposals/README.md (Fase 2).
"""

from __future__ import annotations

from dataclasses import dataclass

from src.modules.ethics.ethical_reflection import ReflectionSnapshot
from src.modules.somatic.sympathetic import InternalState
from src.modules.social.uchi_soto import SocialEvaluation


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
    Maps environment signals, internal state, social evaluation, and ethical reflection
    into a normalized salience distribution over predefined axes. Pure; no side effects.
    """

    AXIS_ORDER: tuple[str, ...] = (
        "risk",
        "social",
        "body",
        "ethical_conflict",
        "epistemic_curiosity",
    )

    def compute(
        self,
        signals: dict[str, float],
        state: InternalState,
        social_eval: SocialEvaluation,
        reflection: ReflectionSnapshot | None,
        curiosity: float = 0.0,
    ) -> SalienceSnapshot:
        """
        Compute the salience (attention) distribution over axes for the current tick.

        Args:
            signals (dict[str, float]): Input signals, e.g., risk, hostility.
            state (InternalState): Internal state snapshot (e.g., body load).
            social_eval (SocialEvaluation): Social context and posture.
            reflection (ReflectionSnapshot | None): Optional ethical reflection.
            curiosity (float, optional): Epistemic curiosity signal. Defaults to 0.0.

        Returns:
            SalienceSnapshot: Normalized weights and dominant axis.
        """
        risk: float = float(signals.get("risk", 0.0))
        risk = max(0.0, min(1.0, risk))

        # Social salience: hostility + defensive posture + dialectic tension
        hostility: float = float(signals.get("hostility", 0.0))
        caution: float = float(social_eval.caution_level)
        dialectic: float = 1.0 if social_eval.dialectic_active else 0.0
        social_raw: float = max(
            0.0,
            min(
                1.0,
                0.45 * hostility + 0.35 * caution + 0.2 * dialectic,
            ),
        )

        # Body / autonomic: sympathetic load proxy
        body_raw: float = max(0.0, min(1.0, float(state.sigma)))

        eth_raw: float = float(reflection.strain_index) if reflection is not None else 0.0

        raw: dict[str, float] = {
            "risk": risk,
            "social": social_raw,
            "body": body_raw,
            "ethical_conflict": eth_raw,
            "epistemic_curiosity": max(0.0, min(1.0, curiosity)),
        }

        ssum: float = sum(raw.values())
        if ssum <= 1e-9:
            weights: dict[str, float] = {k: 0.25 for k in self.AXIS_ORDER}
        else:
            weights = {k: round(raw[k] / ssum, 4) for k in self.AXIS_ORDER}

        mx: float = max(weights[k] for k in self.AXIS_ORDER)
        dominant: str = next(k for k in self.AXIS_ORDER if weights[k] == mx)

        return SalienceSnapshot(
            weights=weights,
            dominant_focus=dominant,
            raw_scores=raw,
        )


def salience_to_llm_context(snapshot: SalienceSnapshot | None) -> str:
    """
    Format a one-line summary of the current salience snapshot for LLM context or logs.

    Args:
        snapshot (SalienceSnapshot | None): The current salience snapshot.

    Returns:
        str: Human-readable summary string, or empty if snapshot is None.
    """
    if snapshot is None:
        return ""
    w = snapshot.weights
    return (
        f"Attention focus (read-only): dominant={snapshot.dominant_focus} "
        f"(risk={w['risk']}, social={w['social']}, body={w['body']}, "
        f"ethical_tension={w['ethical_conflict']}, curiosity={w['epistemic_curiosity']})."
    )
