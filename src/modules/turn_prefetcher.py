import logging
import random
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

    def predict_bridge(self, state: SemanticState, ethics: EthicalSentence) -> str:
        """
        Predice una frase corta basada en el estado semántico, ético y armónico.
        """
        tension = ethics.social_tension_locus
        h = ethics.morals.get("harmonics", {})
        warmth = float(h.get("warmth", 0.5))
        mystery = float(h.get("mystery", 0.5))
        
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
