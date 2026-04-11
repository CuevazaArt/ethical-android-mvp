"""
Lightweight in-session user model (Theory of Mind — MVP v7).

Tracks tension/frustration streak from perception signals and observed Uchi–Soto
circle. Feeds **style-only** guidance into communication — does not change actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .llm_layer import LLMPerception


@dataclass
class UserModelTracker:
    """
    Per-connection state (one kernel per WebSocket → one interlocutor model).

    ``frustration_streak`` rises when hostility/manipulation are high; decays when calm.
    ``premise_concern_streak`` tracks repeated premise-advisory flags (epistemic scan).
    """

    frustration_streak: int = 0
    premise_concern_streak: int = 0
    last_circle: str = "neutral_soto"
    turns_observed: int = 0

    def update(self, perception: LLMPerception, circle: str, *, blocked: bool) -> None:
        if blocked:
            return
        self.turns_observed += 1
        self.last_circle = circle or self.last_circle
        h = float(perception.hostility)
        m = float(perception.manipulation)
        calm = float(perception.calm)
        if h > 0.52 or m > 0.58:
            self.frustration_streak = min(24, self.frustration_streak + 1)
        elif calm > 0.55:
            self.frustration_streak = max(0, self.frustration_streak - 1)
        elif self.frustration_streak > 0:
            self.frustration_streak = max(0, self.frustration_streak - 1)

    def note_premise_advisory(self, flag: str) -> None:
        """Called each chat turn after :func:`premise_validation.scan_premises` (tone only)."""
        if flag == "none":
            self.premise_concern_streak = max(0, self.premise_concern_streak - 1)
        else:
            self.premise_concern_streak = min(16, self.premise_concern_streak + 1)

    def guidance_for_communicate(self) -> str:
        """Single line for LLM / template guidance (tone only)."""
        parts = []
        if self.frustration_streak >= 3:
            parts.append(
                "Relational note: repeated tension in this dialogue may warrant warmer, "
                "clearer transparency—without weakening ethical boundaries or implying fault."
            )
        if self.premise_concern_streak >= 2:
            parts.append(
                "Epistemic note: multiple turns raised premise-safety hints—prioritize careful, "
                "non-affirming responses to risky factual claims."
            )
        return " ".join(parts).strip()

    def to_public_dict(self) -> dict:
        return {
            "frustration_streak": int(self.frustration_streak),
            "premise_concern_streak": int(self.premise_concern_streak),
            "last_circle": self.last_circle,
            "turns_observed": self.turns_observed,
            "metacognitive_prompt": (
                "Consider whether your tone may be contributing to user strain; "
                "adjust clarity and reassurance only within policy."
                if self.frustration_streak >= 3
                else ""
            ),
        }
