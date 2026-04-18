import logging
import time
import math

_log = logging.getLogger(__name__)

class BasalGanglia:
    """
    ARCHITECTURE V2.0 - Basal Ganglia (Filtros EMA)
    Encargado del Smoothing Conductual para prevenir la 'Sociopatía Paramétrica'.
    Aplica una inercia temporal a las variables de afecto (Warmth, Mystery).
    """
    def __init__(self, base_inertia: float = 0.8, time_constant: float = 2.0):
        """
        :param base_inertia: Coeficiente base de suavizado (0.0 a 1.0).
        :param time_constant: Tiempo (segundos) para que el valor alcance el ~63% del objetivo.
        """
        self.base_inertia = base_inertia
        self.tau = time_constant
        
        # Affective States (Theater)
        self.smooth_warmth = 0.5
        self.smooth_mystery = 0.5
        
        # Ethical Leans (Math/Bayesian Weights)
        # Neutral baseline is 0.5
        self.smooth_civic = 0.5
        self.smooth_care = 0.5
        self.smooth_deliberation = 0.5
        self.smooth_careful = 0.5
        
        self.last_update = time.perf_counter()

    def smooth(
        self, 
        target_warmth: float, 
        target_mystery: float,
        target_civic: float = 0.5,
        target_care: float = 0.5,
        target_deliberation: float = 0.5,
        target_careful: float = 0.5
    ) -> dict[str, float]:
        """
        Aplica un filtro de Media Móvil Exponencial (EMA) a los estados afectivos y éticos.
        Previene la 'Sociopatía Paramétrica' al suavizar las transiciones de pesos.
        """
        now = time.perf_counter()
        dt = now - self.last_update
        
        alpha = math.exp(-dt / self.tau) if dt > 0 else self.base_inertia
        
        # 1. Affective Smoothing
        self.smooth_warmth = (target_warmth * (1 - alpha)) + (self.smooth_warmth * alpha)
        self.smooth_mystery = (target_mystery * (1 - alpha)) + (self.smooth_mystery * alpha)
        
        # 2. Ethical Lean Smoothing (Thematic Inertia)
        self.smooth_civic = (target_civic * (1 - alpha)) + (self.smooth_civic * alpha)
        self.smooth_care = (target_care * (1 - alpha)) + (self.smooth_care * alpha)
        self.smooth_deliberation = (target_deliberation * (1 - alpha)) + (self.smooth_deliberation * alpha)
        self.smooth_careful = (target_careful * (1 - alpha)) + (self.smooth_careful * alpha)
        
        self.last_update = now
        _log.debug("BasalGanglia: Integrated Resonance Update (dt=%.2fs)", dt)
        
        return self.get_current_resonance()

    def get_current_resonance(self) -> dict[str, float]:
        """Retorna el estado afectivo y dinámico actual."""
        return {
            "warmth": round(self.smooth_warmth, 3),
            "mystery": round(self.smooth_mystery, 3),
            "civic": round(self.smooth_civic, 3),
            "care": round(self.smooth_care, 3),
            "deliberation": round(self.smooth_deliberation, 3),
            "careful": round(self.smooth_careful, 3),
            "inertia_active": True
        }
