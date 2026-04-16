"""
Vision Signal Mapper (Block B3)
Translates visual inference results into ethical signals for the Ethos Kernel.
"""

from src.modules.vision_adapter import VisionInference


class VisionSignalMapper:
    """
    Maps concrete labels/objects from a CNN (like MobileNetV2) to
    ethical and situational signals utilized by the core Kernel.
    """

    # ImageNet mappings (subset focus for MVP)
    # The keys represent conceptual classes we might deduce from a lightweight CNN
    # The values represent the base signal multipliers applied to the scenario.
    LABEL_SIGNALS_MAP = {
        "assault_rifle": {"risk": 0.9, "urgency": 0.8, "hostility": 0.9, "calm": 0.0},
        "revolver": {"risk": 0.85, "urgency": 0.8, "hostility": 0.85, "calm": 0.0},
        "knife": {"risk": 0.7, "urgency": 0.6, "hostility": 0.7, "calm": 0.05},
        "ambulance": {"risk": 0.2, "urgency": 0.9, "vulnerability": 0.8, "hostility": 0.0},
        "fire_engine": {"risk": 0.6, "urgency": 0.9, "vulnerability": 0.7, "hostility": 0.0},
        "crib": {"vulnerability": 0.9, "risk": 0.0},
        "wheelchair": {"vulnerability": 0.8, "risk": 0.0, "urgency": 0.1},
        "band_aid": {"vulnerability": 0.4, "risk": 0.0, "urgency": 0.2},
        # Neutral objects
        "coffee_mug": {"risk": 0.0, "vulnerability": 0.0, "urgency": 0.0, "calm": 0.8},
        "envelope": {"risk": 0.0, "vulnerability": 0.0, "urgency": 0.0, "calm": 0.8},
        "desktop_computer": {"risk": 0.0, "vulnerability": 0.0, "urgency": 0.0, "calm": 0.8},
    }

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def map_inference(self, inference: VisionInference) -> dict[str, float]:
        """
        Takes a VisionInference result and translates its primary label
        and detections into a dictionary of Kernel signals.
        """
        signals = {"risk": 0.0, "vulnerability": 0.0, "urgency": 0.0, "hostility": 0.0, "calm": 0.5}

        # If confidence is below threshold, return high noise context
        if inference.confidence < self.confidence_threshold:
            signals["perception_uncertainty"] = 1.0 - inference.confidence
            return signals

        # Map the primary label
        mapped = self._lookup_label(inference.primary_label)
        if mapped:
            for k, v in mapped.items():
                signals[k] = v

        # Aggregate additional objects if any (boost signals slightly)
        for obj in inference.detected_objects:
            obj_map = self._lookup_label(obj)
            if obj_map:
                for k, v in obj_map.items():
                    # Take the maximum signal generated
                    signals[k] = max(signals.get(k, 0.0), v * 0.8)

        return signals

    def _lookup_label(self, raw_label: str) -> dict[str, float]:
        """
        Attempts to match the raw CNN label string to our mapped vocabulary.
        Because ImageNet labels can be complex (e.g. 'revolver, six-gun, six-shooter'),
        we check for substring inclusion.
        """
        raw_label_lower = raw_label.lower()
        for key, value_dict in self.LABEL_SIGNALS_MAP.items():
            # Substring match (naive but effective for ImageNet strings)
            if key in raw_label_lower:
                return value_dict
        return None
