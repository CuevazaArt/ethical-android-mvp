"""
Affective Projection Relay (Módulo 10.5)
Transmisión de estados PAD hacia el hardware (Nomad Vessel) vía WebSocket.
"""

import logging
from typing import Any, Dict
from src.modules.pad_archetypes import AffectProjection
from src.modules.nomad_bridge import get_nomad_bridge

_log = logging.getLogger(__name__)

class AffectVesselRelay:
    """
    Orquesta el envío de la proyección afectiva hacia el Orbe Nomad.
    Mapea el espacio vectorial PAD [0,1]^3 a comandos visuales (Color, Pulso, Tamaño).
    """
    
    def __init__(self):
        self.bridge = get_nomad_bridge()

    def transmit(self, projection: AffectProjection):
        """
        Envía el estado PAD al puente Nomad para su transmisión final al smartphone.
        """
        p, a, d = projection.pad
        
        # 1. Mapeo de Color (P: Valence)
        # 1.0 (Muy positivo) -> Verde Esmeralda / Cian
        # 0.5 (Neutral) -> Blanco Azulado
        # 0.0 (Muy negativo) -> Rojo Profundo / Naranja
        hex_color = self._map_valence_to_color(p)
        
        # 2. Mapeo de Pulso (A: Arousal)
        # 1.0 (Muy activo/tenso) -> Pulso rápido (0.5s)
        # 0.0 (Calma total) -> Pulso lento / Estático
        pulse_duration = round(3.0 - (a * 2.5), 2) # Range 0.5s to 3s
        
        # 3. Mapeo de Tamaño/Brillo (D: Dominance)
        # 1.0 (Interno/Poderoso) -> Glow grande / Escala 1.5
        # 0.0 (Sumiso/Externo) -> Glow pequeño / Escala 0.7
        glow_size = round(0.7 + (d * 0.8), 2)
        
        payload = {
            "type": "orb_update",
            "pad": [round(p, 3), round(a, 3), round(d, 3)],
            "archetype": projection.dominant_archetype_id,
            "visuals": {
                "color": hex_color,
                "pulse_s": pulse_duration,
                "scale": glow_size
            }
        }
        
        _log.debug("AffectVesselRelay: Transmitting orb_update (Arch: %s)", projection.dominant_archetype_id)
        
        # Purgar cola si está llena para asegurar tiempo real
        if self.bridge.charm_feedback_queue.full():
            try:
                self.bridge.charm_feedback_queue.get_nowait()
            except: pass
            
        self.bridge.charm_feedback_queue.put_nowait(payload)

    def _map_valence_to_color(self, p: float) -> str:
        """
        Interpola entre Rojo (0.0), Gris (0.5) y Turquesa (1.0).
        """
        if p > 0.5:
            # Neutral a Positivo: Blanco (255,255,255) a Cian/Verde (0, 255, 200)
            ratio = (p - 0.5) * 2
            r = int(255 * (1 - ratio))
            g = 255
            b = int(255 * (1 - ratio * 0.2))
        else:
            # Negativo a Neutral: Rojo (255, 0, 0) a Blanco (255, 255, 255)
            ratio = p * 2
            r = 255
            g = int(255 * ratio)
            b = int(255 * ratio)
            
        return f"#{r:02x}{g:02x}{b:02x}"

_RELAY = AffectVesselRelay()

def get_affect_relay() -> AffectVesselRelay:
    return _RELAY
