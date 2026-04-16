"""
Communication Handlers — Isolated logic for the third stage of the Ethical Kernel pipeline.
Part of Bloque 0.1.3: De-monolithization of EthicalKernel.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, AsyncGenerator

if TYPE_CHECKING:
    from ..kernel import EthicalKernel
    from ..modules.sensor_contracts import SensorSnapshot
    from ..kernel_lobes.models import PerceptionStageResult, KernelDecision

_log = logging.getLogger(__name__)

async def get_bridge_phrase(
    kernel: EthicalKernel,
    stage: PerceptionStageResult,
    decision: KernelDecision,
    user_input: str,
    agent_id: str
) -> Optional[str]:
    """
    Bloque 10.4: Bridge phrase prefetch (<300ms).
    """
    try:
        from ..kernel_lobes.models import EthicalSentence as _EthSentence, SemanticState as _SemState
        _sem = _SemState(
            raw_prompt=user_input,
            perception_confidence=float(stage.perception.calm) if hasattr(stage.perception, "calm") else 0.5,
            scenario_summary=stage.perception.summary or "",
            suggested_context=stage.perception.suggested_context or "everyday",
            signals=stage.signals,
        )
        _eth = _EthSentence(
            is_safe=not decision.blocked,
            social_tension_locus=float(
                decision.social_evaluation.relational_tension
                if decision.social_evaluation else 0.0
            ),
        )
        
        # Accessing private members carefully or via public API if available
        # In this context, we assume the handler has reasonable access during refactor
        _profile = kernel.user_model.profiles.get(agent_id)
        _warmth = float(_profile.charm_warmth) if _profile else 0.5
        _mystery = float(_profile.charm_mystery) if _profile else 0.5
        
        bridge = await kernel.turn_prefetcher.predict_bridge(_sem, _eth, warmth=_warmth, mystery=_mystery)
        return bridge
    except Exception as _bp_err:
        _log.debug("communication_handler: bridge prefetch skipped: %s", _bp_err)
        return None

async def run_communication_stream(
    kernel: EthicalKernel,
    decision: KernelDecision,
    user_input: str,
    conv: str,
    **kwargs
) -> AsyncGenerator[str, None]:
    """
    Pipes the LLM communication stream.
    """
    async for chunk in kernel.llm.acommunicate_stream(
        action=decision.final_action, 
        mode=decision.decision_mode,
        state=decision.sympathetic_state.mode, 
        sigma=decision.sympathetic_state.sigma,
        circle=decision.social_evaluation.circle.value if decision.social_evaluation else "neutral_soto",
        verdict=decision.moral.global_verdict.value if decision.moral else "Gray Zone",
        score=decision.moral.total_score if decision.moral else 0.0,
        scenario=user_input, 
        conversation_context=conv,
        affect_pad=decision.affect.pad if decision.affect else None,
        dominant_archetype=decision.affect.dominant_archetype_id if decision.affect else "",
        identity_context=kernel.memory.identity.to_llm_context(),
        vitality_context=kwargs.get("vitality_context", ""),
        ethical_leans=kwargs.get("ethical_leans"),
    ):
        yield chunk
