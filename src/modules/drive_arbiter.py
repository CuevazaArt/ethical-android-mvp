"""
Proactive drive intents — off hot path; advisory only.

Emits discrete suggestions for governance, learning, and identity consolidation.
Does not execute hardware, contracts, or actions that bypass DAO / policy.

See docs/discusion/PROPUESTA_INTEGRACION_APORTES_V6.md (Fase 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    pass  # EthicalKernel imported at runtime to avoid circular imports


@dataclass(frozen=True)
class DriveIntent:
    suggest: str
    reason: str
    priority: float  # 0..1 relative ranking only


class DriveArbiter:
    """
    Evaluated after Ψ Sleep / backup cycle so narrative and DAO state are fresh.
    """

    MAX_INTENTS = 4
    DAO_RECORDS_SOFT_THRESHOLD = 22
    EPISODES_FOR_IDENTITY_HINT = 6
    EPISODES_FOR_LEARNING_HINT = 10

    def evaluate(self, kernel) -> List[DriveIntent]:
        out: List[DriveIntent] = []

        n_ep = len(kernel.memory.episodes)
        n_aud = len(kernel.dao.records)

        if n_ep >= self.EPISODES_FOR_LEARNING_HINT:
            out.append(
                DriveIntent(
                    suggest="schedule_simulation_or_field_observation",
                    reason="Buffer-aligned curiosity: diversify ethical contexts within MalAbs.",
                    priority=0.28,
                )
            )

        if n_aud >= self.DAO_RECORDS_SOFT_THRESHOLD:
            out.append(
                DriveIntent(
                    suggest="dao_audit_sampling_review",
                    reason="Audit ledger depth suggests periodic human/DAO review of calibrations.",
                    priority=0.36,
                )
            )

        id_eps = kernel.memory.identity.state.episode_count
        if id_eps >= self.EPISODES_FOR_IDENTITY_HINT:
            out.append(
                DriveIntent(
                    suggest="narrative_identity_consolidation",
                    reason="Self-model has enough registered episodes to reflect arc in reporting.",
                    priority=0.32,
                )
            )

        if n_ep >= 1 and hasattr(kernel.immortality, "layers"):
            local_n = len(kernel.immortality.layers.get("local", []))
            if local_n > 0:
                out.append(
                    DriveIntent(
                        suggest="verify_backup_divergence",
                        reason="Identity preservation: cross-check last snapshot vs current episode count.",
                        priority=0.27,
                    )
                )

        out.sort(key=lambda x: -x.priority)
        out = out[: self.MAX_INTENTS]

        # v9.4 — optional metaplan-aware filtering / extra hint (advisory only)
        from .metaplan_registry import (
            apply_drive_intent_metaplan_filter,
            maybe_append_metaplan_drive_extra,
        )

        goals = kernel.metaplan.goals()
        out = apply_drive_intent_metaplan_filter(out, goals, max_intents=self.MAX_INTENTS)
        out = maybe_append_metaplan_drive_extra(out, goals, max_intents=self.MAX_INTENTS)
        return out
