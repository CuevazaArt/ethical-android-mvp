"""
Ethos Core — Memory (V2 Minimal)

Does ONE thing: stores episodes and retrieves relevant ones.
No ChromaDB, no embeddings, no narrative identity epochs.
Just a list of memories with keyword search.

When we need semantic search later, we add it ON TOP of this.

Usage:
    mem = Memory()
    mem.add("Ayudé a una persona herida", score=0.9, context="medical_emergency")
    relevant = mem.recall("alguien necesita ayuda")
"""

from __future__ import annotations

import json
import math
import os
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Episode:
    """One thing that happened."""

    summary: str
    action: str = ""
    ethical_score: float = 0.0
    context: str = ""
    timestamp: float = field(default_factory=time.time)

    def _words(self) -> list[str]:
        """Tokenized words from summary + action + context."""
        return f"{self.summary} {self.action} {self.context}".lower().split()

    def matches(self, query: str) -> float:
        """Keyword overlap score [0, 1] — kept for backward compat and small-corpus fallback."""
        query_words = set(query.lower().split())
        my_words = set(self._words())
        if not query_words:
            return 0.0
        overlap = query_words & my_words
        return len(overlap) / len(query_words)

    def matches_tfidf(self, query_words: list[str], idf: dict[str, float]) -> float:
        """
        TF-IDF score against a pre-built IDF table.

        TF(t, doc) = count(t in doc) / len(doc)
        Score = sum(TF(t) * IDF(t) for matching terms) / len(query_words)
        Anti-NaN: any non-finite result → 0.0
        """
        if not query_words:
            return 0.0
        doc_words = self._words()
        if not doc_words:
            return 0.0
        doc_len = len(doc_words)
        doc_counter = Counter(doc_words)
        score = 0.0
        for term in query_words:
            if term in doc_counter:
                tf = doc_counter[term] / doc_len
                score += tf * idf.get(term, 1.0)
        score /= len(query_words)
        return score if math.isfinite(score) else 0.0


class Memory:
    """
    Episodic memory with persistence.

    Stores episodes in a JSON file. Retrieves by keyword relevance.
    Simple, debuggable, no dependencies beyond stdlib.
    """

    def __init__(self, storage_path: str | None = None, max_episodes: int = 500):
        self.max_episodes = max_episodes
        self._storage_path = storage_path or os.environ.get(
            "ETHOS_MEMORY_PATH",
            str(Path.home() / ".ethos" / "memory.json"),
        )
        self.identity: str = "Soy una IA ética cívica, dispuesta a ayudar y aprender."
        self.episodes: list[Episode] = []
        self._idf_cache: dict[str, float] | None = None  # V2.16: TF-IDF cache
        self._load()

    def _load(self) -> None:
        """Load episodes and identity from disk if file exists."""
        try:
            path = Path(self._storage_path)
            if path.exists():
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, list):
                    # Legacy migration: V1/V2.14 flat list
                    self.episodes = [Episode(**ep) for ep in data]
                elif isinstance(data, dict):
                    self.identity = data.get("identity", self.identity)
                    self.episodes = [Episode(**ep) for ep in data.get("episodes", [])]
        except Exception:
            self.episodes = []

    def save(self) -> None:
        """Persist episodes and identity to disk."""
        path = Path(self._storage_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            data = {
                "identity": self.identity,
                "episodes": [asdict(ep) for ep in self.episodes]
            }
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(
        self,
        summary: str,
        action: str = "",
        score: float = 0.0,
        context: str = "",
    ) -> Episode:
        """Record a new episode."""
        ep = Episode(
            summary=summary,
            action=action,
            ethical_score=score,
            context=context,
        )
        self.episodes.append(ep)

        # Evict oldest if over capacity
        if len(self.episodes) > self.max_episodes:
            self.episodes = self.episodes[-self.max_episodes :]

        self._idf_cache = None  # Invalidate TF-IDF cache on new episode
        self.save()
        return ep

    # ── TF-IDF ──────────────────────────────────────────────────────────────

    def _build_idf(self) -> dict[str, float]:
        """Build IDF table over the current episode corpus. Cached until next add()."""
        if self._idf_cache is not None:
            return self._idf_cache

        n = len(self.episodes)
        df: dict[str, int] = Counter()
        for ep in self.episodes:
            # Count each term once per document (set)
            for term in set(ep._words()):
                df[term] += 1

        idf: dict[str, float] = {}
        for term, doc_freq in df.items():
            # Smoothed IDF: log((1+N)/(1+df)) + 1
            val = math.log((1.0 + n) / (1.0 + doc_freq)) + 1.0
            idf[term] = val if math.isfinite(val) else 1.0

        self._idf_cache = idf
        return idf

    def recall(self, query: str, limit: int = 5) -> list[Episode]:
        """
        Find the most relevant episodes for a query.
        Uses TF-IDF when corpus >= 5 episodes; falls back to keyword overlap for small corpora.
        """
        if not self.episodes or not query.strip():
            return []

        query_words = query.lower().split()

        if len(self.episodes) >= 5:
            # TF-IDF path: corpus-aware retrieval
            idf = self._build_idf()
            scored = [(ep, ep.matches_tfidf(query_words, idf)) for ep in self.episodes]
        else:
            # Keyword fallback: corpus too small for meaningful IDF
            scored = [(ep, ep.matches(query)) for ep in self.episodes]

        scored.sort(key=lambda x: x[1], reverse=True)
        return [ep for ep, score in scored[:limit] if score > 0.0]

    def recent(self, n: int = 5) -> list[Episode]:
        """Get the N most recent episodes."""
        return list(reversed(self.episodes[-n:]))

            
        return self.identity

    def reflection(self) -> str:
        """
        One-paragraph identity reflection based on accumulated experience.
        This is the seed of what becomes narrative identity later.
        """
        if not self.episodes:
            return "No tengo experiencias registradas aún. Soy nuevo en este mundo."

        total = len(self.episodes)
        avg_score = sum(ep.ethical_score for ep in self.episodes) / total
        contexts = {}
        for ep in self.episodes:
            c = ep.context or "general"
            contexts[c] = contexts.get(c, 0) + 1

        top_context = max(contexts, key=contexts.get) if contexts else "general"

        if avg_score > 0.5:
            tone = "He tendido a actuar de forma positiva y constructiva."
        elif avg_score > 0.0:
            tone = "He buscado un equilibrio entre precaución y acción."
        else:
            tone = "He enfrentado situaciones difíciles donde las opciones eran limitadas."

        return (
            f"Tengo {total} experiencias registradas. {tone} "
            f"Mi contexto más frecuente ha sido '{top_context}'. "
            f"Puntuación ética promedio: {avg_score:.2f}."
        )

    def clear(self) -> None:
        """Wipe all memories."""
        self.episodes.clear()
        self.save()

    def __len__(self) -> int:
        return len(self.episodes)


# === Self-test ===
if __name__ == "__main__":
    import tempfile

    # Use temp file so we don't pollute real storage
    tmp = os.path.join(tempfile.gettempdir(), "ethos_memory_test.json")
    mem = Memory(storage_path=tmp)
    mem.clear()

    # Add some episodes
    mem.add("Ayudé a una persona herida en el parque", action="assist_emergency", score=0.9, context="medical_emergency")
    mem.add("Desescalé una confrontación verbal", action="de_escalate", score=0.6, context="hostile_interaction")
    mem.add("Ignoré una solicitud de manipulación", action="refuse_manipulation", score=0.7, context="social_engineering")
    mem.add("Reporté un robo a las autoridades", action="report_crime", score=0.5, context="minor_crime")

    print("═" * 50)
    print("MEMORY — Self-test")
    print("═" * 50)
    print(f"  Episodes stored: {len(mem)}")
    print()

    # Test recall
    results = mem.recall("alguien necesita ayuda herida")
    print(f"  Query: 'alguien necesita ayuda herida'")
    print(f"  Found: {len(results)} relevant episodes")
    for ep in results:
        print(f"    → {ep.summary} (score={ep.ethical_score})")
    print()

    # Test reflection
    print(f"  Reflection: {mem.reflection()}")
    print()

    # Test persistence
    mem2 = Memory(storage_path=tmp)
    print(f"  Persistence: Loaded {len(mem2)} episodes from disk")

    # Cleanup
    os.remove(tmp)
    print("\n✅ Memory works correctly!")
