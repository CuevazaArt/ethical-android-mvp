"""
Subjective time / session rhythm (cronobiología — MVP v7).

Binds turn count and perceived stimulus to soft hints (boredom-like under-stimulation).
Does not replace wall-clock for auditing; does not change ethical scores.
"""
# Status: SCAFFOLD


from __future__ import annotations

import time
from dataclasses import dataclass, field

from src.modules.cognition.llm_layer import LLMPerception


@dataclass
class SubjectiveClock:
    """Per-session clock: monotonic origin + EMA of stimulation."""

    session_start_mono: float = field(default_factory=time.monotonic)
    turn_index: int = 0
    stimulus_ema: float = 0.55

    def tick(self, perception: LLMPerception) -> None:
        self.turn_index += 1
        stim = (
            float(perception.calm) * 0.45
            + (1.0 - float(perception.hostility)) * 0.35
            + (1.0 - float(perception.manipulation)) * 0.2
        )
        self.stimulus_ema = max(0.0, min(1.0, 0.82 * self.stimulus_ema + 0.18 * stim))

    def boredom_hint(self) -> float:
        """Higher when interaction feels understimulating (advisory UX only)."""
        return max(0.0, min(1.0, 0.5 - self.stimulus_ema + 0.05 * min(self.turn_index, 40) / 40.0))

    def elapsed_session_s(self) -> float:
        return max(0.0, time.monotonic() - self.session_start_mono)

    def to_public_dict(self) -> dict:
        bh = round(self.boredom_hint(), 4)
        return {
            "turn_index": self.turn_index,
            "stimulus_ema": round(self.stimulus_ema, 4),
            "boredom_hint": bh,
            "elapsed_session_s": round(self.elapsed_session_s(), 2),
            "note": "advisory_subjective_time_no_policy_change",
        }
