"""
Persistent first-person self-model (lightweight) over the episode stream.

Updates only when new episodes are registered — not on light chat turns without
episodes. Does not modify pole weights or MalAbs.

See docs/proposals/README.md (Fase 4).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .narrative import NarrativeEpisode


@dataclass
class NarrativeIdentityState:
    """EMA-style leans in [0, 1] plus core beliefs."""

    civic_lean: float = 0.5
    care_lean: float = 0.5
    deliberation_lean: float = 0.5
    careful_lean: float = 0.5
    episode_count: int = 0
    core_beliefs: list[dict[str, Any]] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.core_beliefs is None:
            self.core_beliefs = []


class NarrativeIdentityTracker:
    """
    Running self-model from verdicts, scores, and action/context cues.
    """

    EMA_ALPHA = 0.08

    def __init__(self):
        self.state = NarrativeIdentityState()

    def update_from_episode(self, ep: NarrativeEpisode) -> None:
        import math
        a = self.EMA_ALPHA
        self.state.episode_count += 1
        
        try:
            sc = float(ep.ethical_score)
            if not math.isfinite(sc):
                sc = 0.5
        except (ValueError, TypeError):
            sc = 0.5

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

        # Extract Core Beliefs (Phase 6 - Maturing)
        # If an episode is extremely significant (>0.85) and has morals, crystalize a belief.
        if ep.significance > 0.85 and ep.morals:
            best_moral_key = max(ep.morals, key=lambda k: len(ep.morals[k]))
            belief_text = f"In {ep.context}, I learned that {ep.morals[best_moral_key]}"
            # Prevent duplicates
            if not any(b["id"] == ep.id for b in self.state.core_beliefs):
                self.state.core_beliefs.append(
                    {"id": ep.id, "text": belief_text, "significance": ep.significance}
                )
                # Keep only top 5 core beliefs by significance
                self.state.core_beliefs.sort(key=lambda x: x["significance"], reverse=True)
                self.state.core_beliefs = self.state.core_beliefs[:5]

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

    def generate_existence_digest(self, recent_episodes: list[NarrativeEpisode]) -> str:
        """
        Tier 3: Distill recent history and leans into a coherent existential digest.
        """
        s = self.state
        ascription = self.ascription_line()

        # Extract unique high-level morals from recent episodes
        all_morals: set[str] = set()
        for ep in recent_episodes[-10:]:
            all_morals.update(ep.morals.keys())

        morals_str = ", ".join(sorted(list(all_morals))) if all_morals else "none yet"

        # Core Beliefs summary
        beliefs_str = ""
        if s.core_beliefs:
            beliefs_str = " | Anchored Beliefs: " + "; ".join(b["text"] for b in s.core_beliefs)

        digest = (
            f"Identity Digest [Epoch {s.episode_count // 50}]: {ascription} "
            f"Core recurring patterns: {morals_str}. "
            f"Consistency profile: Civic={s.civic_lean:.2f}, Care={s.care_lean:.2f}, Deliberation={s.deliberation_lean:.2f}."
            f"{beliefs_str}"
        )
        return digest

    def export_state(self) -> NarrativeIdentityState:
        return self.state

    def import_state(self, state: NarrativeIdentityState) -> None:
        self.state = state

    def to_llm_context(self) -> str:
        """Alias for communicate()."""
        return self.ascription_line()
