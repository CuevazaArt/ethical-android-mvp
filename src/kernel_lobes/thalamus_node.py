import logging
import time
from typing import Dict, Any, List
from src.kernel_lobes.models import SensoryEpisode

_log = logging.getLogger(__name__)

class ThalamusNode:
    """
    ARCHITECTURE V2.0 - Thalamus (Fusión Sensorial - Bloque 10.1)
    Responsable de unificar los streams de VVAD (Visual) y VAD (Audio).
    Actúa como el filtro de atención del Lóbulo Perceptivo.
    Responsabilidad: Team Cursor.
    """
    def __init__(self):
        self.sensory_buffer: List[SensoryEpisode] = []
        _log.info("ThalamusNode: Sensory Fusion engine initialized.")

    def fuse_signals(self, 
                     vision_data: Dict[str, Any], 
                     audio_data: Dict[str, Any],
                     environmental_stress: float = 0.0) -> Dict[str, Any]:
        """
        Calcula la probabilidad de interacción humana real cruzando audio y visión.
        Evita falsos positivos de VAD mediante verificación visual (Lip Reading/Presence).
        """
        # 1. VVAD (Visual Voice Activity Detection)
        lip_movement = float(vision_data.get("lip_movement", 0.0))
        presence = float(vision_data.get("human_presence", 0.0))
        
        # 2. VAD (Audio Voice Activity Detection)
        vad_confidence = float(audio_data.get("vad_confidence", 0.0))
        
        # 3. Fusión Multimodal (Anti-Spoofing & Attention)
        # Si hay habla pero no movimiento de labios, tratamos como 'Voz de Fondo'
        voice_focal_match = (presence > 0.5 and lip_movement > 0.3 and vad_confidence > 0.5)
        
        attention_locus = 0.0
        if presence > 0.5:
            # Atención proporcional al habla y al contacto visual (lip sync)
            attention_locus = (vad_confidence * 0.7) + (lip_movement * 0.3)
        
        # 4. Cálculo de Tensión Social Percibida
        # La tensión sube con ruidos fuertes o falta de coherencia visión/audio
        sensory_dissonance = 0.0
        if vad_confidence > 0.8 and lip_movement < 0.2:
             sensory_dissonance = 0.4 # Alguien grita pero no lo vemos (Alerta)

        total_tension = (environmental_stress * 0.5) + (sensory_dissonance * 0.5)

        return {
            "attention_locus": round(attention_locus, 3),
            "presence_confidence": round(presence, 3),
            "is_focal_address": voice_focal_match,
            "sensory_tension": round(total_tension, 3),
            "cross_modal_trust": 1.0 if voice_focal_match else 0.4
        }

    def push_episode(self, episode: SensoryEpisode):
        """Mantiene el buffer circular de episodios sensoriales."""
        self.sensory_buffer.append(episode)
        if len(self.sensory_buffer) > 50:
            self.sensory_buffer.pop(0)
