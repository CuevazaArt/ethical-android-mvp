import logging
from typing import TYPE_CHECKING
from src.kernel_lobes.models import SemanticState, EthicalSentence

if TYPE_CHECKING:
    from src.modules.llm_layer import LLMModule
    from src.modules.motivation_engine import MotivationEngine

_log = logging.getLogger(__name__)

class ExecutiveLobe:
    """
    Lóbulo Frontal: Generates the Narrative Monologue and Motor Plans.
    Triggered only if LimbicEthicalLobe outputs a Safe/Valid sentence.
    """
    def __init__(self, llm: 'LLMModule', motivation: 'MotivationEngine'):
        self.llm = llm
        self.motivation = motivation
        _log.info("ExecutiveLobe initialized.")

    def formulate_response(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Generates actual output (speech or motor intent).
        """
        if not ethics.is_safe:
            return "Veto Triggered: " + (ethics.veto_reason or "Unsafe intent")
            
        # 1. Check for proactive internal purpose if the prompt was empty
        if not state.raw_prompt.strip():
            proactive = self.motivation.get_proactive_actions()
            if proactive:
                return f"Internal Motivation Triggered: {proactive[0]['description']}"

        # 2. Verbal Communication via LLM
        # This is the "communicate" step. 
        # Since this lobe is called via asyncio.to_thread, we use the sync version.
        response = self.llm.communicate(
            action=state.candidate_actions[0].name if state.candidate_actions else "neutral_observation",
            mode="D_fast" if ethics.social_tension_locus < 0.5 else "D_delib",
            state="stable", # Sympathetic state placeholder
            sigma=0.5,
            circle="neutral_soto",
            verdict="Safe" if ethics.is_safe else "Blocked",
            score=1.0,
            scenario=state.scenario_summary,
        )

        return response.message
