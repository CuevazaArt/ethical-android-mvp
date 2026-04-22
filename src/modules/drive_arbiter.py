"""
Proactive drive intents — off hot path; advisory only.

Emits discrete suggestions for governance, learning, and identity consolidation.
Does not execute hardware, contracts, or actions that bypass DAO / policy.

See docs/proposals/README.md (Fase 3).
"""

from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING

from .strategy_engine import MissionStatus

_log = logging.getLogger(__name__)

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
        t0 = time.perf_counter()
        out: list[DriveIntent] = []

        try:
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

            if (
                n_ep >= 1
                and hasattr(kernel, "immortality")
                and hasattr(kernel.immortality, "layers")
            ):
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
                try:
                    report = kernel.metacognition.evaluate(kernel.memory)
                    out.extend(kernel.metacognition.suggest_intents(report))
                except Exception as e:
                    _log.warning("DriveArbiter: Metacognition expansion failed: %s", e)

            # Strategic Mind expansion (Phase 4.1): Mission advancement
            if hasattr(kernel, "strategist"):
                try:
                    active = [
                        m
                        for m in kernel.strategist.missions.values()
                        if m.status == MissionStatus.ACTIVE
                    ]
                    if active:
                        # Defensive sort in case mission priorities are unstable
                        active_sorted = sorted(
                            active,
                            key=lambda x: -float(x.priority)
                            if math.isfinite(float(x.priority))
                            else 0.0,
                        )
                        top_m = active_sorted[0]
                        mp = float(top_m.priority)
                        if not math.isfinite(mp):
                            mp = 0.5
                        out.append(
                            DriveIntent(
                                suggest="advance_active_mission",
                                reason=f"Current mission '{top_m.title}' requires active focus.",
                                priority=max(0.0, min(1.0, 0.4 + (mp * 0.4))),
                            )
                        )
                except Exception as e:
                    _log.warning("DriveArbiter: Strategist expansion failed: %s", e)

            # Final sanitation pass for all intents before sorting
            sanitized: list[DriveIntent] = []
            for di in out:
                p = float(di.priority)
                if not math.isfinite(p):
                    p = 0.25  # Safe low priority
                sanitized.append(DriveIntent(di.suggest, di.reason, max(0.0, min(1.0, p))))

            sanitized.sort(key=lambda x: -x.priority)
            out = sanitized[: self.MAX_INTENTS]

            # v9.4 — optional metaplan-aware filtering / extra hint (advisory only)
            from .metaplan_registry import (
                apply_drive_intent_metaplan_filter,
                maybe_append_metaplan_drive_extra,
            )

            goals = kernel.metaplan.goals()
            out = apply_drive_intent_metaplan_filter(out, goals, max_intents=self.MAX_INTENTS)
            out = maybe_append_metaplan_drive_extra(out, goals, max_intents=self.MAX_INTENTS)

        except Exception as e:
            _log.error("DriveArbiter: Critical evaluation error: %s", e)
            if not out:
                out = [DriveIntent("system_check", "Arbiter failure fallback.", 0.1)]

        latency = (time.perf_counter() - t0) * 1000
        if latency > 1.0:
            _log.debug("DriveArbiter: evaluate latency = %.2fms", latency)

        return out
