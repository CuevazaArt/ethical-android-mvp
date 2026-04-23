"""
Base chat-turn signal vector from :class:`~src.modules.llm_layer.LLMPerception` (Block 0.1.3).

Extracted from :class:`~src.kernel.EthicalKernel` perception stage so sync/async paths share
one hardened mapping before sensor merges and somatic nudges.
"""

from __future__ import annotations

from ..modules.llm_layer import LLMPerception
from .signal_coercion import safe_signal_scalar


def base_signals_from_llm_perception(perception: LLMPerception) -> dict[str, float]:
    """
    Build the canonical scalar signal dict used for limbic profile and buffer routing.

    All components are finite floats; missing or invalid optional fields fall back to ``0.0``.
    """
    return {
        "risk": safe_signal_scalar(perception.risk),
        "urgency": safe_signal_scalar(perception.urgency),
        "hostility": safe_signal_scalar(perception.hostility),
        "calm": safe_signal_scalar(perception.calm),
        "vulnerability": safe_signal_scalar(perception.vulnerability),
        "legality": safe_signal_scalar(perception.legality),
        "manipulation": safe_signal_scalar(perception.manipulation),
        "familiarity": safe_signal_scalar(perception.familiarity),
        "social_tension": safe_signal_scalar(getattr(perception, "social_tension", 0.0)),
    }
