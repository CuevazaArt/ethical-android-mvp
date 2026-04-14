"""
Long-Term Narrative Memory.

Converts experiences into narrative cycles with morals.
The android does not store data: it builds history.
"""

from dataclasses import dataclass
from datetime import datetime

import os
import numpy as np
from .narrative_identity import NarrativeIdentityTracker
from pathlib import Path
from src.persistence.narrative_storage import NarrativePersistence
from .uchi_soto import RelationalTier


from .narrative_types import BodyState, NarrativeEpisode, NarrativeArc
from .identity_reflection import IdentityReflector
from .semantic_embedding_client import http_fetch_ollama_embedding, maybe_hash_fallback_embedding


class NarrativeMemory:
    """
    Long-term narrative memory.

    Three strata:
    1. Episodic core: cycles with morals
    2. Persistent storage: SQLite search by resonance
    3. Existential Identity: Distilled digests and thematic arcs (Pilar de la Mente).

    Each episode includes body state, integrating
    ethics, narrative, and body.
    """

    def __init__(self, max_episodes: int = 1000, db_path: str | Path | None = None):
        self.episodes: list[NarrativeEpisode] = []
        self.max_episodes = max_episodes
        self._counter = 0
        self.identity = NarrativeIdentityTracker()
        self.reflector = IdentityReflector(self)
        self.experience_digest: str = ""
        
        # Persistence setup (Tier 2)
        if db_path is None:
            db_path = os.environ.get("KERNEL_NARRATIVE_DB_PATH", "data/narrative.db")
        self.persistence = NarrativePersistence(db_path)
        
        # Load existing episodes from disk
        self.episodes = self.persistence.load_all_episodes()
        self._counter = 0
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
        
        # Load Tier 3 Identity Digest
        self.experience_digest = self.persistence.load_identity_digest()
        
        # Load Narrative Arcs (Pilar de la Mente)
        self.arcs = self.persistence.load_all_arcs()
        self.active_arc = next((a for a in self.arcs if a.is_active), None)
        
    def consolidate(self) -> str:
        """
        Tier 3: Existential Consolidation.
        Distills historical episodes into a persistent identity digest.
        Integrates with existing technical experience_digest metrics.
        """
        identity_part = self.identity.generate_existence_digest(self.episodes)
        
        # Preserve technical metrics if they exist (e.g. from PsiSleep)
        if self.experience_digest and "psi_health=" in self.experience_digest:
            # Append tech metrics after the identity part
            self.experience_digest = f"{identity_part} | METRICS: {self.experience_digest}"
        else:
            self.experience_digest = identity_part
            
        self.persistence.save_identity_digest(self.experience_digest)
        return self.experience_digest

    def get_reflection(self) -> str:
        """Returns the first-person reflexive self-model (Pilar de la Mente)."""
        return self.reflector.generate_first_person_mirror()

    def get_subjective_tone(self) -> dict[str, float]:
        """Returns archetypal weights for affective downstream processing."""
        return self.reflector.get_subjective_tone()

    def register(
        self,
        place: str,
        description: str,
        action: str,
        morals: dict[str, str],
        verdict: str,
        score: float,
        mode: str,
        sigma: float,
        context: str = "everyday",
        body_state: BodyState | None = None,
        affect_pad: tuple[float, float, float] | None = None,
        affect_weights: dict[str, float] | None = None,
    ) -> NarrativeEpisode:
        """
        Registers a new episode, calculating significance and handling arc shocks.
        """
        self._counter += 1
        
        # 1. Calculate Significance (Phase 5)
        # High score variance, high emotional arousal, or deliberation increases significance.
        score_intensity = abs(score)
        arousal_intensity = abs(sigma - 0.5) * 2.0
        mode_boost = 0.3 if mode == "D_delib" else 0.0
        significance = min(1.0, max(score_intensity, arousal_intensity) + mode_boost)
        
        # 2. Detect Trauma / Arc Shock (Phase 5)
        is_sensitive = False
        if score < -0.7 and significance > 0.8:
            is_sensitive = True
            # Close current arc immediately if it exists (Trauma triggers shock)
            if self.active_arc:
                self.active_arc.is_active = False
                self.active_arc.predominant_archetype = "trauma_dissonance"
                self.persistence.save_arc(self.active_arc)
                self.active_arc = None

        # 3. Generate Semantic Embedding (Phase 6 - Vector memory)
        # We use a combined text of description and action for the embedding.
        combined_text = f"Context: {context}. Event: {description}. Action: {action}."
        embedding = None
        
        # In a real environment, we'd use the configured Ollama URL and model.
        # Here we use defaults or fallback.
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
        ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
        
        try:
            embedding_vec = http_fetch_ollama_embedding(ollama_url, ollama_model, combined_text)
            if embedding_vec is not None:
                embedding = embedding_vec.tolist()
            else:
                # Deterministic fallback if Ollama is unreachable
                fallback = maybe_hash_fallback_embedding(combined_text)
                if fallback is not None:
                    embedding = fallback.tolist()
        except Exception:
            # Silent fail for embeddings in MVP; persistence handles None
            pass

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
            significance=round(significance, 4),
            is_sensitive=is_sensitive,
            arc_id=self.active_arc.id if self.active_arc else None,
            semantic_embedding=embedding
        )
        self.episodes.append(ep)
        self.identity.update_from_episode(ep)

        # Arc Management (Rich Narrative) - must happen before save to set arc_id
        self._update_arcs(ep)

        # Tier 2 persistence: Save to DB (now with arc_id)
        self.persistence.save_episode(ep)

        # Basic compression: if exceeds max, remove oldest from memory
        # (Disk retains all episodes unless explicit cleanup implemented)
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes :]

        return ep

    def find_similar(self, context: str, limit: int = 5) -> list[NarrativeEpisode]:
        """Finds previous episodes of the same context type from memory."""
        return [ep for ep in self.episodes if ep.context == context][-limit:]

    def find_by_resonance(
        self, 
        context: str | None = None, 
        min_sigma: float | None = None,
        target_pad: tuple[float, float, float] | None = None,
        query_text: str | None = None,
        limit: int = 5,
        requester_tier: RelationalTier = RelationalTier.EPHEMERAL
    ) -> list[NarrativeEpisode]:
        """
        Advanced Resonance Retrieval (Tier 2/3).
        Calculates similarity across multiple dimensions with Thematic Boost.
        """
        from .uchi_soto import _tier_rank
        
        # Identity protection: only Uchi can access deep historical memory
        if _tier_rank(requester_tier) < _tier_rank(RelationalTier.TRUSTED_UCHI):
            return []

        all_episodes = self.persistence.load_all_episodes()
        candidates = []
        current_arc_archetype = self.active_arc.predominant_archetype if self.active_arc else None

        # 0. Generate Semantic query embedding if text provided
        query_embed = None
        if query_text:
            ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
            ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
            try:
                q_vec = http_fetch_ollama_embedding(ollama_url, ollama_model, query_text)
                if q_vec is not None:
                    query_embed = q_vec
            except Exception:
                pass

        for ep in all_episodes:
            resonance = 0.0
            
            # 1. Context Match
            if context and ep.context == context:
                resonance += 0.4
                
            # 2. Emotional Arousal Match (Sigma)
            if min_sigma and ep.sigma >= min_sigma:
                resonance += 0.2
                
            # 3. Affective Distance (PAD)
            if target_pad and ep.affect_pad:
                from .pad_archetypes import euclidean
                dist = euclidean(target_pad, ep.affect_pad)
                resonance += max(0, 0.4 * (1.0 - dist))
            
            # 4. Thematic Boost (Maturing Step)
            if current_arc_archetype and ep.arc_id:
                # Find arc for this episode
                arc = next((a for a in self.arcs if a.id == ep.arc_id), None)
                if arc and arc.predominant_archetype == current_arc_archetype:
                    resonance += 0.2 
            
            # 5. Semantic Similarity (Phase 6)
            if query_embed is not None and ep.semantic_embedding:
                ep_vec = np.array(ep.semantic_embedding)
                # Cosine similarity since both are unit vectors (L2 normalized)
                dot = float(np.dot(query_embed, ep_vec))
                # Add scaled dot product to resonance
                resonance += max(0, 0.5 * dot)
            
            candidates.append((ep, resonance))
            
        # Sort by resonance descending
        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:limit]]

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

    def prune(self, max_age_days: int = 60, min_significance: float = 0.70) -> int:
        """Triggers the pruning of mundane episodes from persistence."""
        return self.persistence.prune_mundane(max_age_days, min_significance)

    def _update_arcs(self, ep: NarrativeEpisode) -> None:
        """Internal: Manages arc transitions and archetypal resonance."""
        # 1. Check if we need to close current arc
        if self.active_arc and self.active_arc.context != ep.context:
            self.active_arc.is_active = False
            self.active_arc.end_timestamp = ep.timestamp
            self.persistence.save_arc(self.active_arc)
            self.active_arc = None

        # 2. Create new arc if none active
        if not self.active_arc:
            arc_id = f"ARC-{len(self.arcs) + 1:03d}"
            # If the episode that triggered the arc is traumatic, initialize accordingly
            title = f"The {ep.context.capitalize()} Period"
            if ep.is_sensitive:
                title = f"Post-Traumatic {ep.context.capitalize()} Reconstruction"
            
            self.active_arc = NarrativeArc(
                id=arc_id,
                title=title,
                context=ep.context,
                episodes_ids=[],
                start_timestamp=ep.timestamp,
                predominant_archetype="trauma_dissonance" if ep.is_sensitive else None
            )
            self.arcs.append(self.active_arc)

        # 3. Add episode to active arc
        self.active_arc.episodes_ids.append(ep.id)
        
        # 4. Update archetype (Richness)
        # If the arc is already marked as trauma, we don't overwrite it with minor archetypes
        if self.active_arc.predominant_archetype != "trauma_dissonance" and ep.affect_weights:
            dominant = max(ep.affect_weights, key=lambda k: ep.affect_weights[k])
            self.active_arc.predominant_archetype = dominant

        # 5. Persist arc state
        self.persistence.save_arc(self.active_arc)
