import logging
from typing import TYPE_CHECKING
from src.kernel_lobes.models import SemanticState, EthicalSentence

if TYPE_CHECKING:
    from src.modules.llm_layer import LLMModule
    from src.modules.motivation_engine import MotivationEngine

_log = logging.getLogger(__name__)

from src.modules.turn_prefetcher import TurnPrefetcher

class ExecutiveLobe:
    """
    ARCHITECTURE V2.0 - Lóbulo Ejecutivo (Eferencia)
    Genera el monólogo narrativo, frases puente y planes motores.
    Responsabilidad: Copilot Squad (Antigravity Acting).
    """
    def __init__(self, llm: 'LLMModule', motivation: 'MotivationEngine'):
        self.llm = llm
        self.motivation = motivation
        self.prefetcher = TurnPrefetcher()
        _log.info("ExecutiveLobe: Quadrilobular V2.0 initialized with Prefetcher.")

    def prefetch(self, state: SemanticState, ethics: EthicalSentence) -> str | None:
        """
        Genera una frase puente de bajísima latencia.
        """
        if not ethics.is_safe:
            return None
        return self.prefetcher.predict_bridge(state, ethics)

    async def formulate_response(self, state: SemanticState, ethics: EthicalSentence) -> str:
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

        # 2. Extract Emotional Resonance (Basal Ganglia Harmonics - V12.2 6-axis)
        h = ethics.morals.get("harmonics", {})
        # Ensure fallback to 0.5 if key missing
        warmth = float(h.get("warmth", 0.5))
        sigma = 1.0 - warmth # Sigma decreases with warmth
        
        # Etosocial Leans V12.2
        ethical_leans = {
            "civic": float(h.get("civic", 0.5)),
            "care": float(h.get("care", 0.5)),
            "deliberation": float(h.get("deliberation", 0.5)),
            "careful": float(h.get("careful", 0.5))
        }
        
        # 3. Verbal Communication via LLM (ASYNC)
        response = await self.llm.acommunicate(
            action=state.candidate_actions[0].name if state.candidate_actions else "neutral_observation",
            mode="D_fast" if ethics.social_tension_locus < 0.5 else "D_delib",
            state="stable",
            sigma=sigma,
            circle=ethics.morals.get("circle", "neutral_soto"),
            verdict="Safe" if ethics.is_safe else "Blocked",
            score=1.0 - ethics.social_tension_locus,
            scenario=state.scenario_summary,
            weakness_line=f"{ethics.social_posture} | W:{warmth:.2f} M:{h.get('mystery', '0.50')}",
            ethical_leans=ethical_leans
        )

        return response.message
