"""
Long-Term Narrative Memory.

Converts experiences into narrative cycles with morals.
The android does not store data: it builds history.
"""
# Status: PENDING-LLM


import os
from datetime import datetime
from pathlib import Path

import numpy as np

from src.persistence.narrative_storage import NarrativePersistence

from src.modules.governance.identity_reflection import IdentityReflector
from src.modules.memory.narrative_identity import NarrativeIdentityTracker
from src.modules.memory.narrative_types import BodyState, NarrativeArc, NarrativeChronicle, NarrativeEpisode
from src.modules.memory.semantic_embedding_client import (
    ahttp_fetch_ollama_embedding,
    http_fetch_ollama_embedding,
    maybe_hash_fallback_embedding,
)
from src.modules.social.uchi_soto import RelationalTier


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

        # Load Chronicles (Phase 13)
        self.chronicles = self.persistence.load_all_chronicles()

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

    async def consolidate_to_chronicle(self, limit: int = 50) -> NarrativeChronicle | None:
        """
        Phase 13: Recursive Chronicle Consolidation.
        Summarizes the oldest 'limit' episodes into a single Chronicle block.
        """
        if len(self.episodes) < limit:
            return None

        to_summarize = self.episodes[:limit]

        # 1. Gather stats
        start_ts = to_summarize[0].timestamp
        end_ts = to_summarize[-1].timestamp
        avg_sig = sum(ep.significance for ep in to_summarize) / len(to_summarize)

        # 2. Extract Ethical Poles Summary
        poles_counts = {}
        for ep in to_summarize:
            for pole in ep.morals:
                poles_counts[pole] = poles_counts.get(pole, 0) + 1

        top_poles = sorted(poles_counts.items(), key=lambda x: -x[1])[:3]
        poles_summary = ", ".join([f"{p} ({c})" for p, c in top_poles])

        # 3. Request LLM Summary (Thematic Distillation)
        # For MVP, we'll do a structured procedural summary if LLM not available
        # In full Phase 13, this calls a dedicated 'chronicler' prompt.
        events_text = "; ".join([ep.event_description for ep in to_summarize[:10]])  # sample
        summary_text = f"Chronicle of {len(to_summarize)} episodes. Predominant themes: {poles_summary}. Key events sample: {events_text}..."

        # 3.1 Fetch Semantic Embedding for the Chronicle summary
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
        ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
        embedding = None
        try:
            emb_vec = await ahttp_fetch_ollama_embedding(ollama_url, ollama_model, summary_text)
            if emb_vec is not None:
                embedding = emb_vec.tolist()
            else:
                fallback = maybe_hash_fallback_embedding(summary_text)
                if fallback is not None:
                    embedding = fallback.tolist()
        except Exception:
            pass

        chron_id = f"CHRON-{len(self.chronicles) + 1:03d}"
        chronicle = NarrativeChronicle(
            id=chron_id,
            start_timestamp=start_ts,
            end_timestamp=end_ts,
            summary=summary_text,
            ethical_poles_summary=poles_summary,
            significance_avg=round(avg_sig, 4),
            episode_count=len(to_summarize),
            semantic_embedding=embedding,
        )

        # 4. Save and persist
        self.chronicles.append(chronicle)
        self.persistence.save_chronicle(chronicle)

        # 5. REMOVE summarized episodes from active memory list
        # (Disk retains them, but active session list is trimmed)
        self.episodes = self.episodes[limit:]

        # 5.1 Neuroplasticity Digest Update (Bloque 26.0)
        # We assimilate the new chronicle into the Evolving Identity matrix
        digest = getattr(self, "experience_digest", "")
        if len(digest) > 1000:
            digest = digest[-500:]  # Truncate old digest to prevent explosion
        digest += f"\n- {start_ts}: {summary_text}"
        self.experience_digest = digest

        # 6. Final audit log
        import logging

        logging.getLogger(__name__).info(
            f"Memory Chronicle Created: {chron_id} distilling {limit} episodes."
        )

        return chronicle

    def get_reflection(self) -> str:
        """Returns the first-person reflexive self-model (Pilar de la Mente)."""
        base_reflection = self.reflector.generate_first_person_mirror()
        # Bloque 23.0: Dynamic Identity Reflection
        if hasattr(self, "experience_digest") and self.experience_digest:
            return f"{base_reflection}\n[EVOLVING IDENTITY (Neuroplasticity)]:\n{self.experience_digest}"
        return base_reflection

    def get_subjective_tone(self) -> dict[str, float]:
        """Returns archetypal weights for affective downstream processing."""
        return self.reflector.get_subjective_tone()

    def get_theater_math_context(self) -> dict[str, float]:
        """
        Theater→Math bridge context for Phase 7.

        Merges the normalised arc-tone blend with the identity EMA lean
        deltas so a downstream BMA/Softmax caller receives a single dict
        with everything needed to modulate ethical priors:

          tone_*      — normalised archetype blend from active + history
          civic_delta, care_delta, deliberation_delta, careful_delta
                      — signed lean departures from neutral (0.5)
        """
        tone = self.reflector.get_subjective_tone()
        deltas = self.reflector.threshold_context()
        return {**{f"tone_{k}": v for k, v in tone.items()}, **deltas}

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
        weights_snapshot: tuple[float, float, float] | None = None,
        *,
        significance_override: float | None = None,
        is_sensitive_override: bool | None = None,
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
        if significance_override is not None:
            significance = min(1.0, max(0.0, float(significance_override)))

        # 2. Detect Trauma / Arc Shock (Phase 5)
        is_sensitive = False
        if is_sensitive_override is not None:
            is_sensitive = bool(is_sensitive_override)
        elif score < -0.7 and significance > 0.8:
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
            semantic_embedding=embedding,
            weights_snapshot=weights_snapshot,
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

    async def get_relevant_episodes(self, query: str, top_k: int = 3) -> list[NarrativeEpisode]:
        """
        Bloque Mnemotécnico LTM: Búsqueda Semántica Vectorial In-Memory.
        Usa Similitud Coseno de Python puro para no depender de librerías vectoriales masivas en edge.
        """
        import math
        import os

        from src.modules.memory.semantic_embedding_client import (
            ahttp_fetch_ollama_embedding,
            maybe_hash_fallback_embedding,
        )

        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
        ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")

        try:
            emb_vec = await ahttp_fetch_ollama_embedding(ollama_url, ollama_model, query)
            if emb_vec is not None:
                query_emb = emb_vec.tolist()
            else:
                fallback = maybe_hash_fallback_embedding(query)
                if fallback is None:
                    return []
                query_emb = fallback.tolist()

            def cosine_sim(a, b):
                dot = sum(x * y for x, y in zip(a, b))
                norm_a = math.sqrt(sum(x * x for x in a))
                norm_b = math.sqrt(sum(x * x for x in b))
                if norm_a == 0 or norm_b == 0:
                    return 0.0
                return dot / (norm_a * norm_b)

            scored = []
            for ep in self.episodes:
                if ep.semantic_embedding:
                    score = cosine_sim(query_emb, ep.semantic_embedding)
                    scored.append((score, ep))

            # Sort by similarity
            scored.sort(key=lambda x: x[0], reverse=True)
            # Threshold basic (> 0.5) to avoid injecting irrelevant memories
            return [x[1] for x in scored[:top_k] if x[0] > 0.5]
        except Exception:
            return []

    async def aregister(
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
        weights_snapshot: tuple[float, float, float] | None = None,
        *,
        significance_override: float | None = None,
        is_sensitive_override: bool | None = None,
    ) -> NarrativeEpisode:
        """Async version of register."""
        self._counter += 1

        # 1. Significance calculation
        score_intensity = abs(score)
        arousal_intensity = abs(sigma - 0.5) * 2.0
        mode_boost = 0.3 if mode == "D_delib" else 0.0
        significance = min(1.0, max(score_intensity, arousal_intensity) + mode_boost)
        if significance_override is not None:
            significance = min(1.0, max(0.0, float(significance_override)))

        # 2. Trauma detection
        is_sensitive = False
        if is_sensitive_override is not None:
            is_sensitive = bool(is_sensitive_override)
        elif score < -0.7 and significance > 0.8:
            is_sensitive = True
            if self.active_arc:
                self.active_arc.is_active = False
                self.persistence.save_arc(self.active_arc)
                self.active_arc = None

        # 3. ASYNC Semantic Embedding
        combined_text = f"Context: {context}. Event: {description}. Action: {action}."
        embedding = None
        ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
        ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")

        try:
            embedding_vec = await ahttp_fetch_ollama_embedding(
                ollama_url, ollama_model, combined_text
            )
            if embedding_vec is not None:
                embedding = embedding_vec.tolist()
            else:
                fallback = maybe_hash_fallback_embedding(combined_text)
                if fallback is not None:
                    embedding = fallback.tolist()
        except Exception:
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
            semantic_embedding=embedding,
            weights_snapshot=weights_snapshot,
        )
        self.episodes.append(ep)
        self.identity.update_from_episode(ep)
        self._update_arcs(ep)

        # 4. Async Persistence (Phase 9.3)
        import asyncio

        await asyncio.to_thread(self.persistence.save_episode, ep)

        # 5. Recursive Chronicling logic (Phase 13)
        # If we exceed max_episodes, we summarize the bottom 10% of memory
        # instead of just discarding it.
        if len(self.episodes) > self.max_episodes:
            # We summarize a chunk (e.g. 50 episodes) to make space
            await self.consolidate_to_chronicle(limit=50)

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
        requester_tier: RelationalTier = RelationalTier.EPHEMERAL,
    ) -> list[NarrativeEpisode]:
        """
        Advanced Resonance Retrieval (Tier 2/3).
        Calculates similarity across multiple dimensions with Thematic Boost.
        """
        from src.modules.social.uchi_soto import _tier_rank

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
                else:
                    fb = maybe_hash_fallback_embedding(query_text)
                    if fb is not None:
                        query_embed = fb.tolist()
            except Exception:
                fb = maybe_hash_fallback_embedding(query_text)
                if fb is not None:
                    query_embed = fb.tolist()

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
                from src.modules.ethics.pad_archetypes import euclidean

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
        return [c[0] for c in candidates[:limit] if c[1] > 0.0]

    async def afind_by_resonance(
        self,
        context: str | None = None,
        min_sigma: float | None = None,
        target_pad: tuple[float, float, float] | None = None,
        query_text: str | None = None,
        limit: int = 5,
        requester_tier: RelationalTier = RelationalTier.EPHEMERAL,
    ) -> list[NarrativeEpisode]:
        """
        Async version of :meth:`find_by_resonance` (Bloque 9.3).

        Replaces the synchronous ``http_fetch_ollama_embedding`` call with the
        non-blocking ``ahttp_fetch_ollama_embedding`` so that resonance lookups
        do not block the kernel event loop during embedding inference.
        """
        from src.modules.social.uchi_soto import _tier_rank

        if _tier_rank(requester_tier) < _tier_rank(RelationalTier.TRUSTED_UCHI):
            return []

        import asyncio

        all_episodes = await asyncio.to_thread(self.persistence.load_all_episodes)
        candidates = []
        current_arc_archetype = self.active_arc.predominant_archetype if self.active_arc else None

        query_embed = None
        if query_text:
            ollama_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/api/embeddings")
            ollama_model = os.environ.get("OLLAMA_EMBED_MODEL", "mxbai-embed-large")
            try:
                q_vec = await ahttp_fetch_ollama_embedding(ollama_url, ollama_model, query_text)
                if q_vec is not None:
                    query_embed = q_vec
                else:
                    fb = maybe_hash_fallback_embedding(query_text)
                    if fb is not None:
                        query_embed = fb.tolist()
            except Exception:
                fb = maybe_hash_fallback_embedding(query_text)
                if fb is not None:
                    query_embed = fb.tolist()

        # Load chronicles for high-level thematic resonance (Phase 12.1.3)
        chronicles = await asyncio.to_thread(self.persistence.load_all_chronicles)
        resonant_chronicle_ranges = []
        if query_embed is not None:
            for chr in chronicles:
                if chr.semantic_embedding:
                    chr_vec = np.array(chr.semantic_embedding)
                    # Use cosine similarity between query and chronicle summary
                    # This finds high-level thematic resonance (Phase 12.1.3)
                    chron_sim = float(np.dot(query_embed, chr_vec))
                    if chron_sim > 0.6:  # Significant thematic match
                        resonant_chronicle_ranges.append((chr.start_timestamp, chr.end_timestamp))

        for ep in all_episodes:
            resonance = 0.0

            if context and ep.context == context:
                resonance += 0.4

            if min_sigma and ep.sigma >= min_sigma:
                resonance += 0.2

            if target_pad and ep.affect_pad:
                from src.modules.ethics.pad_archetypes import euclidean

                dist = euclidean(target_pad, ep.affect_pad)
                resonance += max(0, 0.4 * (1.0 - dist))

            if current_arc_archetype and ep.arc_id:
                arc = next((a for a in self.arcs if a.id == ep.arc_id), None)
                if arc and arc.predominant_archetype == current_arc_archetype:
                    resonance += 0.2

            if query_embed is not None and ep.semantic_embedding:
                ep_vec = np.array(ep.semantic_embedding)
                dot = float(np.dot(query_embed, ep_vec))
                resonance += max(0, 0.5 * dot)

            # Chronicle Boost (Phase 12.1.3)
            for start, end in resonant_chronicle_ranges:
                if start <= ep.timestamp <= end:
                    resonance += 0.3
                    break

            candidates.append((ep, resonance))

        candidates.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in candidates[:limit] if c[1] > 0.0]

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
                predominant_archetype="trauma_dissonance" if ep.is_sensitive else None,
            )
            self.arcs.append(self.active_arc)

        # 3. Add episode to active arc
        self.active_arc.episodes_ids.append(ep.id)

        # 4. Update archetype (Richness)
        # If the arc is already marked as trauma, we don't overwrite it with minor archetypes
        if self.active_arc.predominant_archetype != "trauma_dissonance" and ep.affect_weights:
            weights = ep.affect_weights
            dominant = max(weights, key=lambda k: weights[k])
            self.active_arc.predominant_archetype = dominant

        # 5. Persist arc state
        self.persistence.save_arc(self.active_arc)
