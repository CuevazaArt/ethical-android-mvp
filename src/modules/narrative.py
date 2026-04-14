"""
Long-Term Narrative Memory.

Converts experiences into narrative cycles with morals.
The android does not store data: it builds history.
"""

from dataclasses import dataclass
from datetime import datetime

import os
from .narrative_identity import NarrativeIdentityTracker
from pathlib import Path
from src.persistence.narrative_storage import NarrativePersistence


from .narrative_types import BodyState, NarrativeEpisode


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

    def __init__(self, max_episodes: int = 1000, db_path: str | Path | None = None):
        self.episodes: list[NarrativeEpisode] = []
        self.max_episodes = max_episodes
        self._counter = 0
        self.identity = NarrativeIdentityTracker()
        self.experience_digest: str = ""
        
        # Persistence setup (Tier 2)
        if db_path is None:
            db_path = os.environ.get("KERNEL_NARRATIVE_DB_PATH", "data/narrative.db")
        self.persistence = NarrativePersistence(db_path)
        
        # Load existing episodes from disk
        self.episodes = self.persistence.load_all_episodes()
        if self.episodes:
            # Sync counter with last episode ID
            last_id = self.episodes[-1].id
            if last_id.startswith("EP-"):
                try:
                    self._counter = int(last_id.split("-")[1])
                except (ValueError, IndexError):
                    self._counter = len(self.episodes)
            else:
                self._counter = len(self.episodes)
            
            # Sync identity from existing history
            for ep in self.episodes:
                self.identity.update_from_episode(ep)
        
        # Load identity digest (Tier 3)
        self.experience_digest = self.persistence.load_identity_digest()

    def register(
        self,
        place: str,
        description: str,
        action: str,
        morals: dict,
        verdict: str,
        score: float,
        mode: str,
        sigma: float,
        context: str,
        body_state: BodyState | None = None,
        affect_pad: tuple[float, float, float] | None = None,
        affect_weights: dict[str, float] | None = None,
    ) -> NarrativeEpisode:
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
        self.identity.update_from_episode(ep)

        # Tier 2 persistence: Save to DB
        self.persistence.save_episode(ep)

        # Basic compression: if exceeds max, remove oldest from memory
        # (Disk retains all episodes unless explicit cleanup implemented)
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes :]

        return ep

    def find_similar(self, context: str, limit: int = 5) -> list[NarrativeEpisode]:
        """Finds previous episodes of the same context type from memory."""
        return [ep for ep in self.episodes if ep.context == context][-limit:]

    def find_by_resonance(self, context: str | None = None, min_sigma: float | None = None) -> list[NarrativeEpisode]:
        """Tier 2: Search all historical episodes by resonance/context from disk."""
        return self.persistence.search_by_resonance(context, min_sigma)

    def save_identity_digest(self, digest: str) -> None:
        """Tier 3: Persist a new existential digest/lesson."""
        self.experience_digest = digest
        self.persistence.save_identity_digest(digest)

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
        morals_txt = "\n".join(f"    {pole}: {moral}" for pole, moral in ep.morals.items())
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
