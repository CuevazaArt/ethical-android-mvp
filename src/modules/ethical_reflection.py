"""
Second-order ethical reflection (metacognition layer).

Reads multipolar scores + Bayesian uncertainty + will mode. Does not alter
which action wins or any veto — only exposes structured state for explanation,
logs, and downstream LLM/monologue.

See docs/proposals/PROPUESTA_INTEGRACION_APORTES_V6.md (Fase 1).
"""

from __future__ import annotations

from dataclasses import dataclass

from .bayesian_engine import BayesianResult
from .ethical_poles import TripartiteMoral


@dataclass(frozen=True)
class ReflectionSnapshot:
    """Compact view of pole tension vs uncertainty (second order)."""

    pole_spread: float
    """max(score) - min(score) over poles, in [0, 2]."""

    pole_scores: tuple[float, ...]
    """Scores in evaluation order (compassionate, conservative, optimistic in default poles)."""

    conflict_level: str
    """Discrete bucket: \"low\" | \"medium\" | \"high\"."""

    strain_index: float
    """[0, 1] — combines spread with Bayesian uncertainty (higher = harder call)."""

    will_mode: str
    """Mode from SigmoidWill.decide (before kernel fusion with sympathetic/locus)."""

    uncertainty: float
    """Bayesian I(x)."""

    note: str
    """One-line hint for logs / optional LLM context."""


def reflection_to_llm_context(snapshot: ReflectionSnapshot | None) -> str:
    """
    Compact string for LLM communication layer: explains internal tension without
    changing the committed decision (policy: style / transparency only).
    """
    if snapshot is None:
        return ""
    return (
        f"Pole tension: {snapshot.conflict_level} "
        f"(spread={snapshot.pole_spread}, strain={snapshot.strain_index}, "
        f"Bayesian uncertainty={snapshot.uncertainty}). {snapshot.note}"
    )


class EthicalReflection:
    """
    Pure second-order monitor: no side effects, no calls to MalAbs or poles.evaluate.
    """

    # Thresholds on spread (empirical defaults; DAO-calibratable later)
    LOW_MAX = 0.4
    MEDIUM_MAX = 0.75

    def reflect(
        self,
        moral: TripartiteMoral,
        bayes_result: BayesianResult,
        will_decision: dict,
    ) -> ReflectionSnapshot:
        scores = [ev.score for ev in moral.evaluations]
        if not scores:
            spread = 0.0
        else:
            spread = max(scores) - min(scores)

        if spread < self.LOW_MAX:
            level = "low"
        elif spread < self.MEDIUM_MAX:
            level = "medium"
        else:
            level = "high"

        u = float(bayes_result.uncertainty)
        # strain: poles disagree more AND model is unsure → harder epistemic load
        strain = min(1.0, (spread / 2.0) * (0.5 + u))

        note = self._compose_note(level, u)

        wm = str(will_decision.get("mode", ""))

        return ReflectionSnapshot(
            pole_spread=round(spread, 4),
            pole_scores=tuple(round(s, 4) for s in scores),
            conflict_level=level,
            strain_index=round(strain, 4),
            will_mode=wm,
            uncertainty=round(u, 4),
            note=note,
        )

    @staticmethod
    def _compose_note(level: str, uncertainty: float) -> str:
        if level == "high" and uncertainty > 0.4:
            return "Strong pole tension with elevated uncertainty — deliberation load is high."
        if level == "high":
            return "Strong disagreement between ethical poles on this action."
        if level == "medium":
            return "Moderate tension between poles; evaluation was not unanimous."
        return "Poles largely aligned on this evaluation."
