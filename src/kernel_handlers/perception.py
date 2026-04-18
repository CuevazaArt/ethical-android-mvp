"""
Perception Handlers — Isolated logic for the first stage of the Ethical Kernel pipeline.
Part of Bloque 0.1.3: De-monolithization of EthicalKernel.
"""

from __future__ import annotations
import asyncio
import logging
import time
from typing import TYPE_CHECKING, Any, Dict, Optional, Tuple

if TYPE_CHECKING:
    from ..kernel import EthicalKernel
    from ..modules.sensor_contracts import SensorSnapshot
    from ..kernel_lobes.models import PerceptionStageResult

_log = logging.getLogger(__name__)

async def run_perception_pipeline(
    kernel: EthicalKernel,
    user_input: str,
    conversation_context: str,
    sensor_snapshot: Optional[SensorSnapshot],
    turn_start_mono: float,
    precomputed: Optional[Tuple]
) -> Tuple[PerceptionStageResult, Any]:
    """
    Executes the layered perception pipeline:
    1. Thalamus fusion (if available)
    2. Parallel LLM Perception & Semantic MalAbs
    3. RLHF Feature extraction and Bayesian modulation
    """
    from ..modules.semantic_chat_gate import arun_semantic_malabs_after_lexical
    from ..modules.rlhf_reward_model import FeatureVector
    
    # 1. Thalamus Sensory Fusion (Integration from Bloque 10.1)
    if kernel.thalamus and sensor_snapshot:
        try:
            _thal = kernel.thalamus.fuse_sensory_stream(sensor_snapshot)
            
            sensor_snapshot.thalamus_attention = _thal.get("attention_locus", 0.0)
            sensor_snapshot.thalamus_tension = _thal.get("sensory_tension", 0.0)
            sensor_snapshot.thalamus_cross_modal_trust = _thal.get("cross_modal_trust", 0.5)
        except Exception as _th_err:
            _log.debug("perception_handler: thalamus fusion skipped: %s", _th_err)
            _thal = None
    else:
        _thal = None

    # 2. Parallel Perception & Layer 2 MalAbs (Semantic)
    perception_task = kernel.perceptive_lobe.run_perception_stage_async(
        user_input, 
        conversation_context=conversation_context, 
        sensor_snapshot=sensor_snapshot,
        turn_start_mono=turn_start_mono, 
        precomputed=precomputed,
    )
    
    mal_semantic_task = arun_semantic_malabs_after_lexical(
        user_input,
        llm_backend=kernel._malabs_text_backend(),
        aclient=kernel.aclient,
    )
    
    stage, mal_semantic = await asyncio.gather(perception_task, mal_semantic_task)
    
    # 3. RLHF Bayesian Modulation
    if kernel.rlhf.reward_model.is_trained and mal_semantic.rlhf_features:
        try:
            fv = FeatureVector.from_dict(mal_semantic.rlhf_features)
            score, conf = kernel.rlhf.reward_model.predict(fv)
            kernel.bayesian.apply_rlhf_modulation(score, conf)
        except Exception as _rlhf_err:
            _log.warning("perception_handler: RLHF modulation failed: %s", _rlhf_err)

    return stage, mal_semantic, _thal
