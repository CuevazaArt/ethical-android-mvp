"""
Proactive drive intents — off hot path; advisory only.

Emits discrete suggestions for governance, learning, and identity consolidation.
Does not execute hardware, contracts, or actions that bypass DAO / policy.

See docs/proposals/README.md (Fase 3).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from .strategy_engine import MissionStatus

# ADR 0016 C1 — Ethical tier classification
__ethical_tier__ = "decision_core"

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

    def evaluate(self, kernel) -> list[DriveIntent]:
        out: list[DriveIntent] = []

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
        
        # Phase 5 expansion: Metacognitive Curiosity & Dissonance
        if hasattr(kernel, "metacognition"):
            report = kernel.metacognition.evaluate(kernel.memory)
            out.extend(kernel.metacognition.suggest_intents(report))
            
        # Strategic Mind expansion (Phase 4.1): Mission advancement
        if hasattr(kernel, "strategist"):
            active = [m for m in kernel.strategist.missions.values() if m.status == MissionStatus.ACTIVE]
            if active:
                top_m = sorted(active, key=lambda x: -x.priority)[0]
                out.append(DriveIntent(
                    suggest="advance_active_mission",
                    reason=f"Current mission '{top_m.title}' requires active focus.",
                    priority=0.4 + (top_m.priority * 0.4)
                ))

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
