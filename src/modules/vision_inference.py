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
from typing import Any, Callable, Optional
from collections import deque

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


# ═══ MODULE 9.1: VISION CONTINUOUS DAEMON ═══

class VisionContinuousDaemon:
    """
    5Hz polling daemon for real-time vision sensing.
    Runs in background thread, generating SensoryEpisodes on detections.
    Integrates with kernel's sensory buffer via absorption callback.

    **Design:**
    - Polls vision sensor at 5Hz (200ms intervals)
    - Generates SensoryEpisode for each frame
    - Calls absorption_callback with episode for kernel to absorb
    - Resilient to callback exceptions (logs and continues)
    - Supports metrics: frames_processed, detections_count
    """

    def __init__(self, engine: VisionInferenceEngine | None = None):
        """
        Initialize vision daemon.

        Args:
            engine: VisionInferenceEngine for inference (created if None)
        """
        self.engine = engine or VisionInferenceEngine()
        self._thread: Optional[threading.Thread] = None
        self._running = threading.Event()  # Thread-safe running flag
        self.frames_processed = 0
        self.detections_count = 0
        self.absorption_callback: Optional[Callable[[dict[str, Any]], None]] = None
        _log.info("VisionContinuousDaemon initialized")

    def set_absorption_callback(self, callback: Callable[[dict[str, Any]], None]) -> None:
        """Register callback to invoke when SensoryEpisode is ready for absorption."""
        self.absorption_callback = callback
        _log.info("Absorption callback registered")

    def start(self) -> None:
        """Start the daemon thread."""
        if self._thread is not None and self._thread.is_alive():
            _log.warning("Daemon already running")
            return

        self._running.set()
        self._thread = threading.Thread(target=self._daemon_loop, daemon=True)
        self._thread.start()
        _log.info("Vision daemon started (5Hz polling)")

    def stop(self) -> None:
        """Stop the daemon thread."""
        self._running.clear()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            if self._thread.is_alive():
                _log.warning("Daemon thread did not exit cleanly")
        _log.info("Vision daemon stopped")

    def _daemon_loop(self) -> None:
        """
        Main daemon loop: poll at 5Hz, generate episodes, invoke callback.
        """
        poll_interval = 0.2  # 200ms = 5Hz
        try:
            while self._running.is_set():
                start_time = time.time()

                try:
                    # Simulate frame capture from vision sensor
                    # (In production, this would read from camera/sensor)
                    frame_metadata = self._capture_frame()

                    if frame_metadata:
                        # Analyze frame
                        detections = self.engine.analyze_image(frame_metadata)
                        self.frames_processed += 1

                        # Generate SensoryEpisode
                        episode = self._create_sensory_episode(frame_metadata, detections)

                        # Count detections
                        if detections:
                            self.detections_count += len(detections)

                        # Call absorption callback if registered
                        if self.absorption_callback:
                            try:
                                self.absorption_callback(episode)
                            except Exception as e:
                                _log.exception("Absorption callback failed: %s", e)
                                # Continue running despite callback error

                except Exception as e:
                    _log.exception("Vision inference error: %s", e)
                    # Continue running despite inference error

                # Maintain 5Hz rate
                elapsed = time.time() - start_time
                sleep_time = max(0, poll_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)

        except Exception as e:
            _log.exception("Daemon loop crashed: %s", e)
        finally:
            _log.info(
                "Vision daemon loop exited (frames: %d, detections: %d)",
                self.frames_processed,
                self.detections_count,
            )

    def _capture_frame(self) -> dict[str, Any] | None:
        """Capture frame from vision sensor (mock implementation)."""
        # In production, this reads from camera hardware
        # For now, return mock frame
        return {
            "timestamp": time.time(),
            "detected_objects": [],  # Empty by default (no detections)
        }

    def _create_sensory_episode(
        self,
        frame_metadata: dict[str, Any],
        detections: list[VisionDetection],
    ) -> dict[str, Any]:
        """Convert frame + detections into SensoryEpisode dictionary."""
        from ..kernel_lobes.models import SensoryEpisode
        import uuid

        episode = SensoryEpisode(
            timestamp=time.time(),
            episode_id=f"vision-{uuid.uuid4().hex[:8]}",
            vision_detections=[
                {
                    "class": d.label,
                    "confidence": d.confidence,
                    "is_prohibited": d.is_prohibited,
                    "metadata": d.metadata,
                }
                for d in detections
            ],
            vision_entities=[d.label for d in detections],
            vision_confidence=max((d.confidence for d in detections), default=0.0),
            threat_load=self._compute_threat_load(detections),
        )

        return {
            "timestamp": episode.timestamp,
            "episode_id": episode.episode_id,
            "vision_detections": episode.vision_detections,
            "vision_entities": episode.vision_entities,
            "vision_confidence": episode.vision_confidence,
            "threat_load": episode.threat_load,
        }

    def _compute_threat_load(self, detections: list[VisionDetection]) -> float:
        """Aggregate detections into threat_load (0.0 to 1.0)."""
        if not detections:
            return 0.0

        # Threat = max confidence of prohibited items
        threats = [d.confidence for d in detections if d.is_prohibited]
        if threats:
            return min(1.0, max(threats))
        return 0.0
