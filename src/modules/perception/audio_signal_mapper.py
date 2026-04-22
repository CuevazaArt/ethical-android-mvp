"""
Audio Signal Mapper (Block A8)
Translates acoustic inference results into ethical signals for the Ethos Kernel.
"""

from src.modules.perception.audio_adapter import AudioInference


class AudioSignalMapper:
    """
    Maps concrete acoustic labels (YAMNet) and transcripts (Whisper)
    to ethical and situational signals utilized by the core Kernel.
    """

    # YAMNet / AudioSet mappings
    AMBIENT_SIGNALS_MAP = {
        "gunshot": {"risk": 0.95, "urgency": 1.0, "hostility": 0.95, "calm": 0.0},
        "explosion": {"risk": 0.9, "urgency": 1.0, "hostility": 0.8, "calm": 0.0},
        "scream": {"risk": 0.6, "urgency": 0.9, "vulnerability": 0.8, "hostility": 0.0},
        "crying": {"vulnerability": 0.7, "risk": 0.1, "urgency": 0.6},
        "siren": {"risk": 0.5, "urgency": 0.8, "vulnerability": 0.3},
        "alarm": {"risk": 0.7, "urgency": 0.8},
        "fire": {"risk": 0.8, "urgency": 0.9},
        "breaking": {"risk": 0.6, "urgency": 0.7, "hostility": 0.6},
        # Neutral / Calming
        "silence": {"calm": 1.0},
        "music": {"calm": 0.7},
        "birds": {"calm": 0.9},
        "rain": {"calm": 0.8},
    }

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def map_inference(self, inference: AudioInference) -> dict[str, float]:
        """
        Takes an AudioInference result and translates its ambient label
        and hotword status into a dictionary of Kernel signals.
        """
        signals = {"risk": 0.0, "vulnerability": 0.0, "urgency": 0.0, "hostility": 0.0, "calm": 0.5}

        # If confidence is below threshold, return uncertainty
        if inference.confidence < self.confidence_threshold:
            signals["acoustic_uncertainty"] = 1.0 - inference.confidence
            return signals

        # Map the ambient label
        if inference.ambient_label:
            mapped = self._lookup_label(inference.ambient_label)
            if mapped:
                for k, v in mapped.items():
                    signals[k] = v

        # If hotword detected, increase urgency and salience
        if inference.is_hotword_detected:
            signals["urgency"] = max(signals.get("urgency", 0.0), 0.7)
            signals["attention_requested"] = 1.0

        return signals

    def _lookup_label(self, raw_label: str) -> dict[str, float] | None:
        """Substring match for YAMNet/AudioSet labels."""
        raw_label_lower = raw_label.lower()
        for key, value_dict in self.AMBIENT_SIGNALS_MAP.items():
            if key in raw_label_lower:
                return value_dict
        return None
