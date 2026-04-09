"""
Long-Term Narrative Memory.

Converts experiences into narrative cycles with morals.
The android does not store data: it builds history.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from datetime import datetime


@dataclass
class BodyState:
    """Physical state of the android at the time of the episode."""
    energy: float = 1.0
    active_nodes: int = 8
    sensors_ok: bool = True
    description: str = ""


@dataclass
class NarrativeEpisode:
    """A narrative cycle with beginning, development, conclusion, and morals."""
    id: str
    timestamp: str
    place: str
    event_description: str
    body_state: BodyState
    action_taken: str
    morals: dict                     # pole -> moral
    verdict: str                     # "Good", "Bad", "Gray Zone"
    ethical_score: float
    decision_mode: str               # "D_fast", "D_delib", "gray_zone"
    sigma: float                     # Sympathetic state at the moment
    context: str                     # Type: emergency, everyday, etc.
    affect_pad: Optional[Tuple[float, float, float]] = None
    affect_weights: Optional[Dict[str, float]] = None


class NarrativeMemory:
    """
    Long-term narrative memory.

    Three strata:
    1. Episodic core: cycles with morals
    2. Preloaded buffer: immutable values (external to this class)
    3. Complementary indices: skills, logs, traceability

    Each episode includes body state, integrating
    ethics, narrative, and body.
    """

    def __init__(self, max_episodes: int = 1000):
        self.episodes: List[NarrativeEpisode] = []
        self.max_episodes = max_episodes
        self._counter = 0

    def register(self, place: str, description: str, action: str,
                 morals: dict, verdict: str, score: float,
                 mode: str, sigma: float, context: str,
                 body_state: Optional[BodyState] = None,
                 affect_pad: Optional[Tuple[float, float, float]] = None,
                 affect_weights: Optional[Dict[str, float]] = None) -> NarrativeEpisode:
        """Registers a new narrative episode."""
        self._counter += 1
        ep = NarrativeEpisode(
            id=f"EP-{self._counter:04d}",
            timestamp=datetime.now().isoformat(),
            place=place,
            event_description=description,
            body_state=body_state or BodyState(),
            action_taken=action,
            morals=morals,
            verdict=verdict,
            ethical_score=round(score, 4),
            decision_mode=mode,
            sigma=round(sigma, 4),
            context=context,
            affect_pad=affect_pad,
            affect_weights=affect_weights,
        )
        self.episodes.append(ep)

        # Basic compression: if exceeds max, remove oldest
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes:]

        return ep

    def find_similar(self, context: str, limit: int = 5) -> List[NarrativeEpisode]:
        """Finds previous episodes of the same context type."""
        return [ep for ep in self.episodes if ep.context == context][-limit:]

    def daily_summary(self) -> dict:
        """Generates a daily summary for Ψ Sleep."""
        today = datetime.now().date().isoformat()
        today_episodes = [ep for ep in self.episodes if ep.timestamp.startswith(today)]

        if not today_episodes:
            return {"episodes": 0, "message": "No activity recorded."}

        scores = [ep.ethical_score for ep in today_episodes]
        modes = [ep.decision_mode for ep in today_episodes]

        return {
            "episodes": len(today_episodes),
            "average_score": round(sum(scores) / len(scores), 4),
            "min_score": min(scores),
            "max_score": max(scores),
            "modes": {m: modes.count(m) for m in set(modes)},
            "contexts": list(set(ep.context for ep in today_episodes)),
        }

    def format_episode(self, ep: NarrativeEpisode) -> str:
        """Formats an episode for human-readable presentation."""
        morals_txt = "\n".join(
            f"    {pole}: {moral}" for pole, moral in ep.morals.items()
        )
        pad_line = ""
        if ep.affect_pad is not None:
            p, a, d = ep.affect_pad
            pad_line = f"\n  PAD (P,A,D): ({p:.3f}, {a:.3f}, {d:.3f})"
            if ep.affect_weights:
                top = sorted(ep.affect_weights.items(), key=lambda x: -x[1])[:3]
                pad_line += " | top weights: " + ", ".join(f"{k}={v:.3f}" for k, v in top)
        return (
            f"─── {ep.id} | {ep.context.upper()} | {ep.place} ───\n"
            f"  Event: {ep.event_description}\n"
            f"  Action: {ep.action_taken}\n"
            f"  Mode: {ep.decision_mode} | σ={ep.sigma} | Score: {ep.ethical_score}\n"
            f"  Body state: energy={ep.body_state.energy}, "
            f"nodes={ep.body_state.active_nodes}/8\n"
            f"  Verdict: {ep.verdict}\n"
            f"  Morals:\n{morals_txt}{pad_line}"
        )
