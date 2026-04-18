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
        self.ollama_host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        if self.model_name:
            _log.info("TurnPrefetcher: Active with local model %s via %s", self.model_name, self.ollama_host)
        else:
            _log.info("TurnPrefetcher: Running in Heuristic Fallback mode (no micro-LLM).")

    async def predict_bridge(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Predice una frase corta basada en el estado semántico, ético y armónico.
        Intenta usar un micro-LLM local si está disponible.
        """
        tension = ethics.social_tension_locus
        h = ethics.morals.get("harmonics", {})
        warmth = float(h.get("warmth", 0.5))
        mystery = float(h.get("mystery", 0.5))
        
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
                        f"{self.ollama_host}/api/generate",
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
