from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.modules.internal_monologue import compose_monologue_line
from src.modules.motivation_engine import MotivationEngine
from src.modules.weighted_ethics_scorer import CandidateAction


class _SalienceLike(Protocol):
    dominant_focus: str


class _ReflectionLike(Protocol):
    conflict_level: float


class _AffectLike(Protocol):
    dominant_archetype_id: str


@dataclass(frozen=True)
class _ExecutiveDecisionView:
    """Minimal decision-shaped object expected by ``compose_monologue_line``."""

    blocked: bool
    final_action: str
    decision_mode: str = "executive_safe"
    salience: _SalienceLike | None = None
    reflection: _ReflectionLike | None = None
    affect: _AffectLike | None = None


class ExecutiveLobe:
    """
    Frontal lobe for final response assembly.

    Narrative monologue is emitted only when the limbic judgment is safe.
    """

    def __init__(self) -> None:
        self.motivation_engine = MotivationEngine()

    def formulate_response(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Build the final response after limbic judgment.
        """
        if not ethics.is_safe:
            return "Veto Triggered: " + (ethics.veto_reason or "Unsafe intent")

        self.motivation_engine.update_drives(
            {
                "social_tension": max(0.0, min(1.0, ethics.social_tension_locus)),
                "uncertainty": max(0.0, min(1.0, 1.0 - state.perception_confidence)),
                "energy": 1.0,
            }
        )
        proactive_actions: list[CandidateAction] = self.motivation_engine.get_proactive_actions()

        prompt = state.raw_prompt.strip() or "unspecified intent"
        response = f"Response generated for intent: {prompt}"
        if proactive_actions:
            response = f"{response} | proactive_focus={proactive_actions[0].name}"

        monologue = compose_monologue_line(
            _ExecutiveDecisionView(
                blocked=False,
                final_action=response,
            )
        )
        return f"{response} | {monologue}"
