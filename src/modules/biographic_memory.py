"""
Biographic Memory Tracker (Block 21.2) — Persistent Chat Milestones.
Converts chat turns and executive decisions into biographic episodes.
"""

from __future__ import annotations
import logging
import time
from typing import TYPE_CHECKING, Any, Optional

if TYPE_CHECKING:
    from src.modules.narrative import NarrativeMemory
    from src.kernel_lobes.models import MotorCommandDispatch

_log = logging.getLogger(__name__)

class BiographicMemoryTracker:
    """
    Subsystem that monitors the nervous system outcomes and promotes them
    to long-term biographic episodes in the NarrativeMemory.
    """
    def __init__(self, memory: NarrativeMemory):
        self.memory = memory

    def register_dispatch(self, dispatch: MotorCommandDispatch, context_data: Optional[dict[str, Any]] = None):
        """
        Converts a MotorCommandDispatch into a NarrativeEpisode.
        """
        try:
            # Extract metadata from context if available
            ctx = context_data or {}
            user_input = ctx.get("text", "Unknown stimulus")
            
            # Determine ethical score and significance
            is_blocked = getattr(dispatch, "is_vetoed", False)
            score = -0.95 if is_blocked else 0.5
            mode = "D_veto" if is_blocked else "D_nomad"
            
            # Register in NarrativeMemory
            self.memory.register(
                place="Nervous Hub",
                description=f"Stimulus: {user_input[:100]}",
                action=dispatch.action_id,
                morals={"sovereignty": "active", "safety": "vetoed" if is_blocked else "pass"},
                verdict="Ethical Guard Active" if is_blocked else "Distributed Convergence",
                score=score,
                mode=mode,
                sigma=0.5, # Baseline arousal for chat
                context="conversational_biography"
            )
            _log.info("BiographicMemoryTracker: Event %s promoted to narrative episode.", dispatch.ref_pulse_id)
        except Exception as e:
            _log.error("BiographicMemoryTracker: Promotion failed: %s", e)
