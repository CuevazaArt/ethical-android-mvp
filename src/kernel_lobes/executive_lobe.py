from __future__ import annotations

from dataclasses import dataclass

from src.kernel_lobes.models import EthicalSentence, SemanticState
from src.modules.internal_monologue import compose_monologue_line
from src.modules.motivation_engine import MotivationEngine


class ExecutiveLobe:
    """
    Lóbulo Frontal: Generates the Narrative Monologue and Motor Plans.
    Triggered only if LimbicEthicalLobe outputs a Safe/Valid sentence.
    """

    def __init__(self, motivation_engine: MotivationEngine | None = None):
        self._motivation_engine = motivation_engine or MotivationEngine()

    def formulate_response(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Generates actual output (speech or motor intent).
        """
        if not ethics.is_safe:
            return "Veto Triggered: " + (ethics.veto_reason or "Unsafe intent")

        self._motivation_engine.update_drives(
            {
                "social_tension": ethics.social_tension_locus,
                "uncertainty": max(0.0, 1.0 - state.perception_confidence),
            }
        )
        proactive_actions = self._motivation_engine.get_proactive_actions()

        final_action = "respond_to_prompt"
        base_message = state.raw_prompt.strip() or "Ambient silence detected."
        if not state.raw_prompt.strip() and proactive_actions:
            top_action = proactive_actions[0]
            final_action = top_action.name
            base_message = top_action.description

        monologue = compose_monologue_line(
            _ExecutiveMonologueDecision(
                blocked=False,
                final_action=final_action,
                decision_mode="executive_safe_path",
            )
        )

        return f"Response generated: {base_message}\n{monologue}"


@dataclass
class _ExecutiveMonologueDecision:
    blocked: bool
    final_action: str
    decision_mode: str
    salience: None = None
    reflection: None = None
    affect: None = None
