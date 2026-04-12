"""
GWT-lite salience: read-only attention weights over existing signal axes.

Does not reorder the kernel pipeline (phase 1). Produces a normalized vector
for telemetry, UI, and optional LLM nuance — not a policy change.

See docs/proposals/PROPOSAL_CONTRIBUTION_INTEGRATION_V6.md (Fase 2).
"""

from __future__ import annotations

from dataclasses import dataclass

from .ethical_reflection import ReflectionSnapshot
from .sympathetic import InternalState
from .uchi_soto import SocialEvaluation


@dataclass(frozen=True)
class SalienceSnapshot:
    """
    Non-negative weights over axes that sum to 1 (attention budget).
    `dominant_focus` is the axis with largest weight (ties: lexicographic).
    """

    weights: dict[str, float]
    """Keys: risk, social, body, ethical_conflict."""

    dominant_focus: str
    """Which axis 'wins' the competition for salience this tick."""

    raw_scores: dict[str, float]
    """Pre-normalization [0,1] scores for audit."""


class SalienceMap:
    """
    Maps environment + reflection into a salience distribution. Pure; no side effects.
    """

    AXIS_ORDER = ("risk", "social", "body", "ethical_conflict")

    def compute(
        self,
        signals: dict,
        state: InternalState,
        social_eval: SocialEvaluation,
        reflection: ReflectionSnapshot | None,
    ) -> SalienceSnapshot:
        risk = float(signals.get("risk", 0.0))
        risk = max(0.0, min(1.0, risk))

        # Social salience: hostility + defensive posture + dialectic tension
        hostility = float(signals.get("hostility", 0.0))
        caution = float(social_eval.caution_level)
        dialectic = 1.0 if social_eval.dialectic_active else 0.0
        social_raw = max(
            0.0,
            min(
                1.0,
                0.45 * hostility + 0.35 * caution + 0.2 * dialectic,
            ),
        )

        # Body / autonomic: sympathetic load proxy
        body_raw = max(0.0, min(1.0, float(state.sigma)))

        if reflection is not None:
            eth_raw = float(reflection.strain_index)
        else:
            eth_raw = 0.0

        raw = {
            "risk": risk,
            "social": social_raw,
            "body": body_raw,
            "ethical_conflict": eth_raw,
        }

        ssum = sum(raw.values())
        if ssum <= 1e-9:
            weights = {k: 0.25 for k in self.AXIS_ORDER}
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
        f"ethical_tension={w['ethical_conflict']})."
    )
