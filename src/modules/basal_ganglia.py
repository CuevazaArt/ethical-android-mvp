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
        
        # Estados internos suavizados (Baseline neutro)
        self.smooth_warmth = 0.5
        self.smooth_mystery = 0.5
        self.last_update = time.perf_counter()

    def smooth(self, target_warmth: float, target_mystery: float) -> tuple[float, float]:
        """
        Aplica un filtro de Media Móvil Exponencial (EMA) ponderado por tiempo (dt).
        Previene saltos bruscos en el tono emocional del androide.
        """
        now = time.perf_counter()
        dt = now - self.last_update
        
        # Calcular Alpha dinámico según el tiempo transcurrido
        # Si dt es muy pequeño (ráfaga), la inercia es alta.
        # Si dt es muy grande (pausa), la inercia baja para permitir cambios frescos.
        alpha = math.exp(-dt / self.tau) if dt > 0 else self.base_inertia
        
        # Limitar la velocidad de cambio (Slew Rate Limit opcional)
        self.smooth_warmth = (target_warmth * (1 - alpha)) + (self.smooth_warmth * alpha)
        self.smooth_mystery = (target_mystery * (1 - alpha)) + (self.smooth_mystery * alpha)
        
        self.last_update = now
        _log.debug("BasalGanglia: Resonance Update (dt=%.2fs) -> W:%.2f, M:%.2f", 
                   dt, self.smooth_warmth, self.smooth_mystery)
        
        return self.smooth_warmth, self.smooth_mystery

    def get_current_resonance(self) -> dict:
        """Retorna el estado afectivo actual listo para el prompt o modulación de voz."""
        return {
            "warmth": round(self.smooth_warmth, 3),
            "mystery": round(self.smooth_mystery, 3),
            "inertia_active": True
        }
