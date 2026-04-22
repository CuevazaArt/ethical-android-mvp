"""
Post-perception decision adapter for streaming chat (``process_chat_turn_stream`` / ``aprocess``).

Delegates to :meth:`src.kernel.EthosKernel.aprocess` with chat-stage candidates and sensor context.
The batch simulation path (``process`` in ``kernel_legacy_v12``) does not use this module.
"""

from __future__ import annotations

from typing import Any


async def run_decision_pipeline(
    kernel: Any,
    stage: Any,
    user_input: str,
    place: str,
    agent_id: str,
    sensor_snapshot: Any,
) -> Any:
    perception = stage.perception
    mm = stage.multimodal_trust
    signals = stage.signals
    heavy = kernel._chat_is_heavy(perception) or (stage.tier == "high")
    eth_context = perception.suggested_context if heavy else "everyday"

    actions = kernel._actions_for_chat(perception, heavy)
    ctx = perception.suggested_context or ""
    from ..kernel_utils import enrich_chat_turn_signals_for_bayesian
    from ..modules.generative_candidates import augment_generative_candidates

    actions = augment_generative_candidates(
        actions,
        user_input,
        ctx,
        heavy,
        getattr(perception, "generative_candidates", None),
    )
    signals = enrich_chat_turn_signals_for_bayesian(signals, perception)

    return await kernel.aprocess(
        scenario=perception.summary or user_input[:240],
        place=place,
        signals=signals,
        context=eth_context,
        actions=actions,
        agent_id=agent_id,
        message_content=user_input,
        register_episode=heavy,
        sensor_snapshot=sensor_snapshot,
        multimodal_assessment=mm,
    )
