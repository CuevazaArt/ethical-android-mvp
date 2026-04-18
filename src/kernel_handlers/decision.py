"""
Decision Handlers — Isolated logic for the second stage of the Ethical Kernel pipeline.
Part of Bloque 0.1.3: De-monolithization of EthicalKernel.
"""

from __future__ import annotations
import logging
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from ..kernel import EthicalKernel
    from ..modules.sensor_contracts import SensorSnapshot
    from ..kernel_lobes.models import PerceptionStageResult, KernelDecision

_log = logging.getLogger(__name__)

async def run_decision_pipeline(
    kernel: EthicalKernel,
    stage: PerceptionStageResult,
    user_input: str,
    place: str,
    agent_id: str,
    sensor_snapshot: Optional[SensorSnapshot]
) -> KernelDecision:
    """
    Executes the decision stage:
    1. Assess if scenario is 'heavy' vs 'light'
    2. Candidate action generation
    3. Bayesian + Multipolar deliberation (process)
    """
    # 3. Decision Stage
    heavy = kernel._chat_is_heavy(stage.perception)
    actions = kernel._actions_for_chat(stage.perception, heavy)
    
    decision = await kernel.aprocess(
        scenario=stage.perception.summary or user_input[:240],
        place=place, 
        signals=stage.signals, 
        context=stage.perception.suggested_context if heavy else "everyday",
        actions=actions, 
        agent_id=agent_id, 
        message_content=user_input, 
        register_episode=heavy,
        sensor_snapshot=sensor_snapshot, 
        multimodal_assessment=stage.multimodal_trust,
    )
    
    return decision
