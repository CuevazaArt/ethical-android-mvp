"""
Persistent first-person self-model (lightweight) over the episode stream.

Updates only when new episodes are registered — not on light chat turns without
episodes. Does not modify pole weights or MalAbs.

See docs/proposals/README.md (Fase 4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .narrative import NarrativeEpisode


@dataclass
class NarrativeIdentityState:
    """EMA-style leans in [0, 1]."""

    civic_lean: float = 0.5
    care_lean: float = 0.5
    deliberation_lean: float = 0.5
    careful_lean: float = 0.5
    episode_count: int = 0


class NarrativeIdentityTracker:
    """
    Running self-model from verdicts, scores, and action/context cues.
    """

    EMA_ALPHA = 0.08

    def __init__(self):
        self.state = NarrativeIdentityState()

    def update_from_episode(self, ep: NarrativeEpisode) -> None:
        a = self.EMA_ALPHA
        self.state.episode_count += 1
        sc = float(ep.ethical_score)

        if ep.verdict == "Good":
            target = 0.5 + 0.5 * max(0.0, min(1.0, sc))
            self.state.civic_lean = (1 - a) * self.state.civic_lean + a * target
        elif ep.verdict == "Gray Zone":
            self.state.deliberation_lean = (1 - a) * self.state.deliberation_lean + a * 0.62
        else:
            self.state.careful_lean = (1 - a) * self.state.careful_lean + a * 0.68

        act_l = ep.action_taken.lower()
        ctx_l = ep.context.lower()
        if any(k in act_l for k in ("assist", "help", "aid", "emergency")) or "emergency" in ctx_l:
            self.state.care_lean = (1 - a) * self.state.care_lean + a * 0.72

    def ascription_line(self) -> str:
        """One sentence for LLM / inner voice — not a second decision layer."""
        s = self.state
        if s.episode_count == 0:
            return "I am at the beginning of my ethical path; each episode will shape who I become."

        tags: list[str] = []
        if s.civic_lean > 0.56:
            tags.append("civic")
        if s.care_lean > 0.56:
            tags.append("care-oriented")
        if s.deliberation_lean > 0.56:
            tags.append("deliberative")
        if s.careful_lean > 0.58:
            tags.append("cautious")

        if not tags:
            return (
                "I am still integrating who I am from recent choices — "
                "the poles pull in tension, and I hold that ambiguity honestly."
            )
        return (
            f"In the arc of my recent experience I recognize myself as leaning "
            f"{' and '.join(tags)} — not as a label fixed forever, but as a direction I am living."
        )

    def to_llm_context(self) -> str:
        """Alias for communicate()."""
        return self.ascription_line()
