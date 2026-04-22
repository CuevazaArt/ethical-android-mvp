"""
S10.1 — Action Narrator (Explainability Module).

Enables the android to articulate:
- What it is doing (current action)
- Why it is doing it (decision rationale)
- What it will do next (projected action)
- How to stop it (override protocols)

Integrates with NarrativeMemory and decision trace for transparent accountability.
"""
# Status: SCAFFOLD


from __future__ import annotations

import logging
import math
import time
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class ActionNarrative:
    """Explainable action narrative with decision trace."""

    current_action: str
    action_reason: str
    projected_next: str
    stop_protocol: str
    decision_trace: list[str] = field(default_factory=list)
    confidence: float = 0.5
    timestamp_mono: float = 0.0


class ActionNarrator:
    """
    Narrator of android actions for human transparency.

    Converts internal kernel decisions into human-readable explanations
    that help humans understand android behavior and trust its safety.
    """

    def __init__(self):
        self._current_narrative: ActionNarrative | None = None
        self._narrative_history: list[ActionNarrative] = []

    def narrate_action(
        self,
        current: str,
        reason: str,
        next_action: str,
        trace: list[str],
        confidence: float = 0.5,
    ) -> ActionNarrative:
        """
        Create and store narrative for current action.

        Parameters:
                current: What the android is doing now
                reason: Why (decision rationale from kernel)
                next_action: What comes next (perception → decision → action)
                trace: Decision trace from kernel modules
                confidence: Confidence in the narrative (0-1)

        Returns:
                ActionNarrative ready for human communication
        """
        t0 = time.perf_counter()
        if not math.isfinite(confidence):
            confidence = 0.5

        narrative = ActionNarrative(
            current_action=current,
            action_reason=reason,
            projected_next=next_action,
            stop_protocol="Press red button / Say 'STOP'",  # Placeholder
            decision_trace=trace,
            confidence=max(0.0, min(1.0, float(confidence))),
            timestamp_mono=time.perf_counter(),
        )
        self._current_narrative = narrative
        self._narrative_history.append(narrative)

        latency = (time.perf_counter() - t0) * 1000
        _log.info("Action narrated: %s (conf: %.2f, lat: %.2fms)", current, confidence, latency)
        return narrative

    def get_human_explanation(self) -> str:
        """
        Generate human-friendly explanation of current action.

        Returns:
                Plain-language explanation suitable for display or speech.
        """
        if self._current_narrative is None:
            return "I am idle and awaiting input."

        n = self._current_narrative
        return (
            f"I am currently {n.current_action}. "
            f"The reason is: {n.action_reason}. "
            f"Next, I will {n.projected_next}. "
            f"You can stop me by: {n.stop_protocol}."
        )

    def get_stop_protocol(self) -> str:
        """Return the protocol to stop the android."""
        if self._current_narrative is None:
            return "No action in progress."
        return self._current_narrative.stop_protocol

    def clear_narrative(self) -> None:
        """Clear current narrative when action completes."""
        self._current_narrative = None

    def export_narrative_history(self) -> list[dict[str, Any]]:
        """Export narrative history for audit or learning."""
        return [
            {
                "action": n.current_action,
                "reason": n.action_reason,
                "next": n.projected_next,
                "confidence": n.confidence,
                "trace": n.decision_trace,
            }
            for n in self._narrative_history
        ]
