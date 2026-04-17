import logging
import threading
import time
from typing import TYPE_CHECKING
from src.kernel_lobes.models import SemanticState, EthicalSentence

if TYPE_CHECKING:
    from src.modules.bayesian_engine import BayesianEngine
    from src.modules.identity_integrity import IdentityIntegrityManager

_log = logging.getLogger(__name__)

from src.modules.basal_ganglia import BasalGanglia

class LimbicLobe:
    """
    ARCHITECTURE V2.0 - Lóbulo Límbico (Ganglios Basales)
    Encargado de la Resonancia Afectiva y el Smoothing Conductual.
    Responsabilidad: Antigravity (Acting for Claude Squad).
    """
    def __init__(self, bayesian: 'BayesianEngine', identity: 'IdentityIntegrityManager'):
        self.bayesian = bayesian
        self.identity = identity
        # Inicializar Ganglios Basales con inercia nominal (V2.0 EMA con dt)
        self.basal_ganglia = BasalGanglia(base_inertia=0.85, time_constant=2.5)
        
        # Bloque 9.2: Acumulación de Tensión Límbica Estática
        self._static_tension_offset: float = 0.0
        self._entity_timers: dict[str, float] = {}
        self._danger_keywords = {"weapon", "aggressive", "threat", "gun", "knife", "intruder"}
        self._running = True
        self._tension_daemon = threading.Thread(target=self._static_tension_loop, daemon=True, name="LimbicTensionDaemon")
        self._tension_daemon.start()

        _log.info("LimbicLobe: BasalGanglia smoothing active with Static Tension Daemon.")

    def _static_tension_loop(self):
        """
        Daemon en background que escala la tensión si un peligro visual persiste.
        No requiere interacción de texto (Nomadismo Perceptivo).
        """
        while self._running:
            time.sleep(1.0)
            
            # En V2 completo, leería del ThalamusNode/SensoryBuffer.
            # Por ahora, simulamos el agotamiento del timer si existen entidades peligrosas registradas.
            current_time = time.time()
            max_persistence = 0.0
            
            # Limpieza y cálculo de persistencia máxima
            expired = []
            for entity, first_seen in self._entity_timers.items():
                duration = current_time - first_seen
                if duration > 10.0:
                    expired.append(entity) # Olvidar tras 10 segundos sin reactivacion
                else:
                    max_persistence = max(max_persistence, duration)
                    
            for e in expired:
                del self._entity_timers[e]
                
            # Si un peligro persite más de 5 segundos, la tensión sube exponencialmente
            if max_persistence >= 5.0:
                stress_factor = (max_persistence - 5.0) * 0.1 # Sube 0.1 por segundo extra
                self._static_tension_offset = min(1.0, stress_factor)
                if self._static_tension_offset > 0.3:
                    _log.warning("LimbicLobe [DAEMON]: Static Tension escalating due to persistent threat: %.2f", self._static_tension_offset)
            else:
                # Decaimiento natural si el peligro desaparece
                self._static_tension_offset = max(0.0, self._static_tension_offset - 0.05)

    def shutdown(self):
        self._running = False

    def update_perceptive_field(self, visual_entities: list[str]):
        """Callback para que el ThalamusNode/PerceptiveLobe inyecte entidades vistas continuamente."""
        current_time = time.time()
        for e in visual_entities:
            if any(danger in e.lower() for danger in self._danger_keywords):
                if e not in self._entity_timers:
                    self._entity_timers[e] = current_time
                # Actualiza el timer si ya existía (mantiene el first_seen original)

    def resonant_state(self, state: SemanticState, ethical_advisory: EthicalSentence) -> EthicalSentence:
        """
        Aplica inercia conductual a las señales éticas/sociales.
        Registra el episodio en la identidad persistente.
        """
        # 0. Registro biográfico del episodio
        impact = 0.5 - ethical_advisory.social_tension_locus
        self.identity.register_episode(impact=impact)

        # 1. Extraer targets de la tensión social, sumando la tensión estática acumulada
        effective_tension = min(1.0, ethical_advisory.social_tension_locus + self._static_tension_offset)
        target_warmth = 1.0 - effective_tension
        # El misterio aumenta si la tensión es baja o hay señales de 'misterio'
        target_mystery = state.signals.get("mystery_index", 0.5)

        # 2. Aplicar Smoothing
        smooth_w, smooth_m = self.basal_ganglia.smooth(target_warmth, target_mystery)
        
        # 3. Penalizar por trauma sensorial (Sensory Lag)
        applied_trauma = 0.0
        if state.timeout_trauma:
            applied_trauma = state.timeout_trauma.severity * 0.2
            _log.info("LimbicLobe: Applying trauma weight (Lag): %.2f", applied_trauma)

        # Enriquecer la sentencia ética
        resonance = ethical_advisory
        resonance.applied_trauma_weight = applied_trauma
        resonance.social_tension_locus = effective_tension
        
        # Inyectar el estado armónico en la sentencia para que el Ejecutivo lo use
        resonance.morals["harmonics"] = {
            "warmth": f"{smooth_w:.2f}",
            "mystery": f"{smooth_m:.2f}",
            "posture": ethical_advisory.social_posture
        }
        
        return resonance
