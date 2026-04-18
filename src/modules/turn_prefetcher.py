"""
Turn Prefetcher — Pre-emptive linguistic responses.
Part of Phase 10.4 Infrastructure for <300ms latency.

Speculates on probable user closure or simple affirmations
using micro-models or template-matchers to avoid perceived 
sociopathic lag while the main LLM delibierates.
"""

from __future__ import annotations
import random
from typing import Optional

class TurnPrefetcher:
    """
    Anticipates user turns to provide near-instant feedback.
    """
    AFFIRMATIONS = [
        "Entiendo...",
        "Te escucho.",
        "Mmm, comprendo.",
        "Sigue...",
        "Interesante."
    ]
    
    SURPRISE_REACTIONS = [
        "¡Oh!",
        "Vaya...",
        "No esperaba eso."
    ]

    def __init__(self, mode: str = "template"):
        self.mode = mode

    async def predict_bridge(
        self,
        partial_text: str,
        signals: dict,
        warmth: float = 0.5,
        mystery: float = 0.5,
        ethics: Optional[Any] = None
    ) -> Optional[str]:
        """
        Phase 10.4: Predicts a fast bridge phrase (<300ms).
        Combines deterministic heuristics (Antigravity) with 
        semantic-aware prefetching (Copilot).
        """
        text = partial_text.lower().strip()
        
        # 1. Heuristic Fallback (Antigravity)
        if len(text) < 10 and signals.get("trust", 0.5) > 0.6:
            return random.choice(self.AFFIRMATIONS)
            
        if "!" in text or signals.get("risk", 0.0) > 0.8:
            return random.choice(self.SURPRISE_REACTIONS)

        # 2. Semantic Context (Copilot logic placeholder)
        if ethics and hasattr(ethics, "social_tension_locus"):
            if ethics.social_tension_locus > 0.7:
                 return "Entiendo la gravedad de esto..."
        
        return None

    def should_prefetch(self, context: str, sigma: float) -> bool:
        """Determines if the current emotional state (Sigma) allows prefetching."""
        # Don't prefetch during high-stress ethical dilemmas (Sociopath risk)
        return sigma < 0.7 
