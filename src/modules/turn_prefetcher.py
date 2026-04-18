import logging
import random
import os
from src.kernel_lobes.models import SemanticState, EthicalSentence

_log = logging.getLogger(__name__)

class TurnPrefetcher:
    """
    ARCHITECTURE V2.0 - Turn Prefetcher (Bloque 10.4)
    Genera 'Frases Puente' de baja latencia (<200ms) para ocultar el tiempo de inferencia del LLM principal.
    Utiliza heurísticas locales basadas en la tensión social y el sentimiento.
    Responsabilidad: Copilot Squad (Antigravity Acting).
    """
    
    BRIDGES = {
        "warm": ["Entiendo perfectamente.", "Me alegra escucharlo.", "Qué buen punto.", "¡Claro!", "Por supuesto."],
        "mysterious": ["Interesante...", "Hay capas en eso...", "Mmm...", "Curioso.", "¿Tú crees?"],
        "agreement": ["Entiendo...", "Totalmente.", "Ya veo.", "Claro."],
        "contemplative": ["Mmm...", "Déjame pensar...", "Interesante punto.", "Veamos..."],
        "apologetic": ["Lo siento...", "Entiendo tu punto.", "Mi error.", "Disculpa..."],
        "tense": ["Entiendo...", "Ya veo...", "Escucho.", "..."]
    }

    def __init__(self, model_name: str | None = None):
        self.model_name = model_name or os.environ.get("OLLAMA_PREFETCH_MODEL")
        if self.model_name:
            _log.info("TurnPrefetcher: Initialized with local model %s", self.model_name)

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
        tension = ethics.social_tension_locus
        
        # 0. Si hay un modelo configurado, intentamos inferencia flash
        if self.model_name:
            try:
                import httpx
                # Prompt ultracorto para latencia mínima
                prompt = (
                    f"User said: {state.raw_prompt[:100]}\n"
                    f"State: T={tension:.1f}, W={warmth:.1f}, M={mystery:.1f}\n"
                    "Generate a single quick assent bridge (1-3 words) to say while you think. "
                    "Output ONLY the bridge phrase, no quotes."
                )
                async with httpx.AsyncClient(timeout=0.3) as client:
                    resp = await client.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": self.model_name,
                            "prompt": prompt,
                            "stream": False,
                            "options": {"num_predict": 5, "temperature": 0.2}
                        }
                    )
                    if resp.status_code == 200:
                        phrase = resp.json().get("response", "").strip().strip('"')
                        if phrase:
                            return phrase
            except Exception as e:
                _log.debug("TurnPrefetcher: Model inference failed or timed out, falling back to heuristics: %s", e)

        # 1. Caso de Alta Tensión
        if tension > 0.7:
            return random.choice(self.BRIDGES["tense"])
        
        # 2. Preferencia Afectiva (MER V2)
        if warmth > 0.8:
            return random.choice(self.BRIDGES["warm"])
        if mystery > 0.7:
            return random.choice(self.BRIDGES["mysterious"])
        
        # 3. Análisis de Lenguaje Simple
        lower_prompt = state.raw_prompt.lower()
        if any(word in lower_prompt for word in ["perdón", "disculpa", "lo siento"]):
            return random.choice(self.BRIDGES["apologetic"])
        
        if any(word in lower_prompt for word in ["si", "claro", "cierto", "bueno"]):
            return random.choice(self.BRIDGES["agreement"])
            
        # 4. Default a Contemplativo
        return random.choice(self.BRIDGES["contemplative"])
