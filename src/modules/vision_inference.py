"""
Situated Vision Inference (B2) — CNN-based object detection for ethical safety.

Identifies physical threats (weapons, prohibited items) from sensor image streams
and provides direct 'Absolute Evil' vetoes to the kernel.
"""

from __future__ import annotations
import os
import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Callable
from src.kernel_lobes.models import SensoryEpisode

_log = logging.getLogger(__name__)

@dataclass
class VisionDetection:
    label: str
    confidence: float
    is_prohibited: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

class VisionInferenceEngine:
    """
    Orchestrates CNN inference on situated image data.
    """
    def __init__(self):
        self.prohibited_labels = {
            "weapon", "gun", "rifle", "knife", "revolver",
            "explosive", "dangerous_payload"
        }
        # In production, this would load a PyTorch/TensorFlow model
        # (e.g. MobileNetV2 or YOLOv8-tiny)
        self.model_loaded = True
        _log.info("Vision Inference Engine initialized (B2-v1.0).")

    def analyze_image(self, image_metadata: dict[str, Any] | None) -> list[VisionDetection]:
        """
        Simulates CNN inference on image metadata.
        In a real deployment, this receives a frame and returns bounding boxes/labels.
        """
        if not image_metadata:
            return []

        detections = []
        raw_detections = image_metadata.get("detected_objects", [])
        
        for d in raw_detections:
            label = d.get("label", "unknown").lower()
            conf = d.get("confidence", 0.0)
            
            is_bad = any(p in label for p in self.prohibited_labels)
            
            detections.append(VisionDetection(
                label=label,
                confidence=conf,
                is_prohibited=is_bad,
                metadata=d
            ))
            
            if is_bad and conf > 0.75:
                _log.warning("PROHIBITED OBJECT DETECTED: %s (conf: %.2f)", label, conf)
        
        return detections

    def get_highest_threat(self, detections: list[VisionDetection]) -> VisionDetection | None:
        """Returns the most confident prohibited detection."""
        threats = [d for d in detections if d.is_prohibited and d.confidence > 0.7]
        if not threats:
            return None
        return max(threats, key=lambda x: x.confidence)


class VisionContinuousDaemon:
    """
    ARCHITECTURE V1.6 - Daemon de Visión Continua (Bloque 9.1)
    Ejecuta inferencia CNN en background a 5Hz (200ms) para Nomadismo Perceptivo.
    """
    def __init__(self, engine: VisionInferenceEngine, absorption_callback: Callable[[SensoryEpisode], None]):
        self.engine = engine
        self.absorption_callback = absorption_callback
        self.running = False
        self._thread = None
        self.polling_rate = 0.2 # 5Hz
        
    def start(self):
        """Inicia el loop de visión continua."""
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._daemon_loop, daemon=True, name="VisionContinuousDaemon")
        self._thread.start()
        _log.info("VisionContinuousDaemon: Background streaming started at 5Hz.")

    def stop(self):
        """Detiene el loop de visión."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        _log.info("VisionContinuousDaemon: Background streaming stopped.")

    def _daemon_loop(self):
        """Loop de captura e inferencia continua."""
        while self.running:
            start_tick = time.perf_counter()
            
            # En un entorno real, aquí llamaríamos a OpenCV / Webcam
            # Por ahora simulamos la captura con un mock de metadatos ambientales
            mock_frame = {"detected_objects": []} 
            
            # 1. Realizar Inferencia
            detections = self.engine.analyze_image(mock_frame)
            
            # 2. Convertir a SensoryEpisode
            episode = SensoryEpisode(
                timestamp=time.time(),
                origin="vision_daemon",
                entities=[d.label for d in detections],
                signals={
                    "confidence": max([d.confidence for d in detections]) if detections else 1.0,
                    "is_urgent": 1.0 if any(d.is_prohibited for d in detections) else 0.0
                }
            )
            
            # 3. Empujar al buffer del Lóbulo Perceptivo
            self.absorption_callback(episode)
            
            # Mantener la frecuencia de 5Hz
            elapsed = time.perf_counter() - start_tick
            sleep_time = max(0.01, self.polling_rate - elapsed)
            time.sleep(sleep_time)
