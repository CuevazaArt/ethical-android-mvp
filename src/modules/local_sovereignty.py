"""
Local sovereignty (planned) — veto DAO- or swarm-proposed calibration that breaks biographic continuity.

**Status:** stub — always accept; future: compare proposed ML weight deltas against
``NarrativeMemory`` / owner trajectory and return ``reject`` + audit reason.

See ``docs/discusion/PROPUESTA_VERIFICACION_REALIDAD_V11.md`` (pillar 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class SovereigntyEvaluation:
    accept: bool
    reason: str
    audit_hint: str = ""


def evaluate_calibration_update(
    proposed: Optional[Dict[str, Any]] = None,
    *,
    narrative_episode_count: int = 0,
) -> SovereigntyEvaluation:
    """
    Placeholder: no veto until threat model and persistence hooks are defined.

    Future: if a DAO-pushed calibration contradicts immutable L0 or local trajectory,
    return ``accept=False`` and log ``audit_hint`` for the owner.
    """
    return SovereigntyEvaluation(
        accept=True,
        reason="stub: local sovereignty veto not yet wired to DAO payloads",
        audit_hint="",
    )
