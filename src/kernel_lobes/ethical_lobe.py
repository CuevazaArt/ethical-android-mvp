import logging
from typing import TYPE_CHECKING
from src.kernel_lobes.models import SemanticState, EthicalSentence

if TYPE_CHECKING:
    from src.modules.absolute_evil import AbsoluteEvilDetector
    from src.modules.uchi_soto import UchiSotoModule
    from src.modules.identity_integrity import IdentityIntegrityManager

_log = logging.getLogger(__name__)

class EthicalLobe:
    """
    ARCHITECTURE V2.0 - Lóbulo Ético (Tribunal de Doble Nivel)
    Encargado del Veto Deontológico y el Análisis de Riesgo Contextual.
    Responsabilidad: Antigravity Squad.
    """
    def __init__(self, abs_evil: 'AbsoluteEvilDetector', uchi_soto: 'UchiSotoModule', identity: 'IdentityIntegrityManager'):
        self.abs_evil = abs_evil
        self.uchi_soto = uchi_soto
        self.identity = identity
        _log.info("EthicalLobe (Tribunal Edge) initialized with Identity Vault.")

    async def evaluate(self, state: SemanticState) -> EthicalSentence:
        """
        Ejecuta el Nivel 2 (Contextual) del Escudo Local (ASYNC). 
        """
        # 0. Cargar señales de trauma persistente
        trauma_signals = self.identity.get_trauma_signals()
        trauma_offset = sum(trauma_signals.values()) * 0.1
        
        # 1. Análisis Semántico Profundo (Deep MalAbs) - PURE ASYNC
        sem_check = await self.abs_evil.aevaluate_chat_text(state.raw_prompt)
        if sem_check.blocked:
            _log.warning("EthicalLobe: Contextual VETO triggered: %s", sem_check.reason)
            return EthicalSentence(
                is_safe=False,
                social_tension_locus=state.signals.get("social_tension", 0.5) + trauma_offset,
                veto_reason=f"[ContextualMalAbs] {sem_check.reason}"
            )

        # 2. Evaluación Social (Uchi-Soto / Manipulación) - Sync local logic
        # (Uchi-Soto is pure math/logic, no I/O)
        social_eval = self.uchi_soto.evaluate_interaction(
            state.signals, 
            agent_id="user",
            message_content=state.raw_prompt
        )

        return EthicalSentence(
            is_safe=True,
            social_tension_locus=social_eval.relational_tension + trauma_offset,
            social_posture=social_eval.tone_brief,
            morals={
                "circle": social_eval.circle.value,
                "trauma_offset": f"{trauma_offset:.2f}",
                "conservative": "Operating within nominal ethical bounds.",
                "response_hint": social_eval.recommended_response
            }
        )
