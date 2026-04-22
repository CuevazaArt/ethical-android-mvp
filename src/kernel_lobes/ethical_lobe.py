import logging
from typing import TYPE_CHECKING

from src.kernel_lobes.models import EthicalSentence, SemanticState

if TYPE_CHECKING:
    from src.modules.ethics.absolute_evil import AbsoluteEvilDetector
    from src.modules.governance.identity_integrity import IdentityIntegrityManager
    from src.modules.governance.nomad_identity import NomadicRegistry
    from src.modules.social.uchi_soto import UchiSotoModule

_log = logging.getLogger(__name__)


class EthicalLobe:
    """
    ARCHITECTURE V2.0 - Lóbulo Ético (Tribunal de Doble Nivel)
    Encargado del Veto Deontológico y el Análisis de Riesgo Contextual.
    Responsabilidad: Antigravity Squad.
    """

    def __init__(
        self,
        abs_evil: "AbsoluteEvilDetector",
        uchi_soto: "UchiSotoModule",
        identity: "IdentityIntegrityManager",
        registry: "NomadicRegistry",
    ):
        self.abs_evil = abs_evil
        self.uchi_soto = uchi_soto
        self.identity = identity
        self.registry = registry
        _log.info("EthicalLobe (Tribunal Edge) initialized with Identity Vault.")

    async def evaluate(self, state: SemanticState) -> EthicalSentence:
        """
        Ejecuta el Nivel 2 (Contextual) del Escudo Local (ASYNC).
        """
        try:
            # 0. Cargar señales de trauma persistente
            trauma_signals = self.identity.get_trauma_signals()
            trauma_offset = sum(trauma_signals.values()) * 0.1

            # 1. Análisis Semántico Profundo (Deep MalAbs) - PURE ASYNC
            sem_check = await self.abs_evil.aevaluate_chat_text(state.raw_prompt)
            is_degraded = sem_check.metadata.get("edge_degraded", False)

            if sem_check.blocked:
                _log.warning("EthicalLobe: Contextual VETO triggered: %s", sem_check.reason)
                return EthicalSentence(
                    is_safe=False,
                    social_tension_locus=state.signals.get("social_tension", 0.5) + trauma_offset,
                    veto_reason=f"[ContextualMalAbs] {sem_check.reason}",
                )

            # 2. Evaluación Social (Uchi-Soto / Manipulación) - Sync local logic
            agent_id = getattr(state, "agent_id", None) or "user"
            social_eval = self.uchi_soto.evaluate_interaction(
                state.signals,
                agent_id=agent_id,
                message_content=state.raw_prompt,
                registry=self.registry,
            )

            # 3. Obtener Offsets Éticos del Círculo de Confianza (V12.2)
            weight_offsets = self.uchi_soto.get_weight_offsets(social_eval.circle)

            return EthicalSentence(
                is_safe=True,
                social_tension_locus=social_eval.relational_tension
                + trauma_offset
                + (0.2 if is_degraded else 0.0),
                social_posture=social_eval.tone_brief,
                morals={
                    "circle": social_eval.circle.value,
                    "trauma_offset": f"{trauma_offset:.2f}",
                    "edge_degraded": is_degraded,
                    "conservative": "Operating in Degraded Edge Mode" if is_degraded else "Safe",
                    "response_hint": social_eval.recommended_response,
                    "weight_offsets": weight_offsets,
                },
            )
        except Exception as exc:
            _log.error("EthicalLobe.evaluate error: %s", exc)
            return EthicalSentence(
                is_safe=True,
                social_tension_locus=0.5,
                veto_reason=f"[EthicalLobe degraded] {type(exc).__name__}",
            )
