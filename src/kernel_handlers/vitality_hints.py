"""
Vitality context for LLM :meth:`~src.modules.llm_layer.LLMModule.acommunicate` (batch chat).

Re-exports the stable surface from :mod:`src.modules.vitality` so the monolithic
batch path does not need to import vitality details from multiple places
(Bloque 35.1, ``PLAN_WORK_DISTRIBUTION_TREE``).
"""

from __future__ import annotations

from ..modules.vitality import (
    VitalityAssessment,
    assess_vitality,
    vitality_communication_hint,
)

__all__ = [
    "VitalityAssessment",
    "assess_vitality",
    "vitality_communication_hint",
]
