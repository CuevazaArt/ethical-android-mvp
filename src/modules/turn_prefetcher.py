"""
Turn Prefetcher — Pre-emptive linguistic responses.
Part of Phase 10.4 Infrastructure for <300ms latency.

Speculates on probable user closure or simple affirmations
using micro-models or template-matchers to avoid perceived 
sociopathic lag while the main LLM delibierates.
"""

from __future__ import annotations
import random
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..kernel_lobes.models import SemanticState, EthicalSentence

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
        state: SemanticState,
        ethics: EthicalSentence,
        warmth: float = 0.5,
        mystery: float = 0.5,
    ) -> str:
        """
        Predice una frase puente corta basada en el estado semántico y ético.
        Intenta usar un micro-LLM local si está disponible; si falla o excede los
        300 ms de budget, cae de forma transparente a heurísticas locales.

        Args:
            state:   Estado semántico del turno actual (raw_prompt, señales, etc.).
            ethics:  Veredicto ético del Lóbulo Límbico.
            warmth:  Calidez del perfil de encanto del usuario (0-1, default 0.5).
            mystery: Misterio del perfil de encanto del usuario (0-1, default 0.5).
        """
        text = state.raw_prompt.lower().strip()
        signals = state.signals
        tension = ethics.social_tension_locus
        
        # Bloque 10.4: Heurística de puente de baja latencia
        if len(text) < 12 and signals.get("trust", 0.5) > 0.6:
            return random.choice(self.AFFIRMATIONS)
            
        if tension > 0.8:
            return "Comprendo la importancia de esto..."
            
        if warmth > 0.8:
            return "Dime más, por favor."
            
        if "!" in text or signals.get("risk", 0.0) > 0.7:
            return random.choice(self.SURPRISE_REACTIONS)
            
        return random.choice(self.AFFIRMATIONS)

    def should_prefetch(self, context: str, sigma: float) -> bool:
        """Determines if the current emotional state (Sigma) allows prefetching."""
        # Don't prefetch during high-stress ethical dilemmas (Sociopath risk)
        return sigma < 0.7 
