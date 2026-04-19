from __future__ import annotations

import logging
import math
import time
from typing import Any
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

    def transmit(self, projection: AffectProjection) -> None:
        """
        Envía el estado PAD al puente Nomad para su transmisión final al smartphone.
        """
        t0 = time.perf_counter()
        
        try:
            # 0. Anti-NaN Hardening
            p = float(projection.pad[0]) if math.isfinite(projection.pad[0]) else 0.5
            a = float(projection.pad[1]) if math.isfinite(projection.pad[1]) else 0.5
            d = float(projection.pad[2]) if math.isfinite(projection.pad[2]) else 0.5
            
            # 1. Mapeo de Color (P: Valence)
            hex_color = self._map_valence_to_color(p)
            
            # 2. Mapeo de Pulso (A: Arousal)
            pulse_duration = round(3.0 - (a * 2.5), 2) # Range 0.5s to 3s
            
            # 3. Mapeo de Tamaño/Brillo (D: Dominance)
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
            
            latency = (time.perf_counter() - t0) * 1000
            
            # 4. Bridge Integration with safety checks
            if self.bridge and hasattr(self.bridge, "charm_feedback_queue") and self.bridge.charm_feedback_queue:
                # Purgar cola si está llena para asegurar tiempo real
                if self.bridge.charm_feedback_queue.full():
                    try:
                        self.bridge.charm_feedback_queue.get_nowait()
                    except Exception: 
                        pass
                    
                # Note: put_nowait is used because transmit is sync. 
                # If kernel is multi-threaded, this remains a best-effort non-blocking op.
                self.bridge.charm_feedback_queue.put_nowait(payload)
                
                if latency > 2.0:
                    _log.debug("AffectVesselRelay: transmitted orb_update (Arch: %s, lat: %.2fms)", 
                               projection.dominant_archetype_id, latency)
            else:
                _log.warning("AffectVesselRelay: Nomad Bridge or queue unavailable. Expression dropped.")

        except Exception as e:
            _log.error("AffectVesselRelay: Failed to transmit affect: %s", e)

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
