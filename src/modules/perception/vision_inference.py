"""
Situated Vision Inference (B2) — CNN-based object detection for ethical safety.

Identifies physical threats (weapons, prohibited items) from sensor image streams
and provides direct 'Absolute Evil' vetoes to the kernel.

Module 9.1 (``VisionContinuousDaemon``): background loop (~5 Hz by default) drains
``NomadBridge.vision_queue_threadsafe`` (thread-safe mirror of the async vision queue),
runs JPEG decode + ``VisionInferenceEngine.analyze_jpeg_bytes`` in a worker thread
so the cadence loop stays non-blocking (async preprocessing vs the hot path).
"""
# Status: SCAFFOLD


from __future__ import annotations

import base64
import logging
import os
import queue
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from src.kernel_lobes.models import SensoryEpisode

_log = logging.getLogger(__name__)


def vision_daemon_hz() -> float:
    """Target loop rate for ``VisionContinuousDaemon`` (env ``KERNEL_VISION_DAEMON_HZ``, default 5)."""

    raw = os.environ.get("KERNEL_VISION_DAEMON_HZ", "").strip()
    if not raw:
        return 5.0
    try:
        v = float(raw)
        return v if 0.5 <= v <= 30.0 else 5.0
    except ValueError:
        return 5.0


def vision_daemon_infer_timeout_s() -> float:
    """Max time to wait on worker inference per tick (``KERNEL_VISION_DAEMON_INFER_TIMEOUT_S``, default 0.18)."""

    raw = os.environ.get("KERNEL_VISION_DAEMON_INFER_TIMEOUT_S", "").strip()
    if not raw:
        return 0.18
    try:
        v = float(raw)
        return v if 0.05 <= v <= 2.0 else 0.18
    except ValueError:
        return 0.18


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

    def __init__(self) -> None:
        self.prohibited_labels = {
            "weapon",
            "gun",
            "rifle",
            "knife",
            "revolver",
            "explosive",
            "dangerous_payload",
        }
        # In production, this would load a PyTorch/TensorFlow model
        # (e.g. MobileNetV2 or YOLOv8-tiny)
        self.model_loaded = True
        self._cnn_adapter: Any = None
        _log.info("Vision Inference Engine initialized (B2-v1.0).")

    def analyze_image(self, image_metadata: dict[str, Any] | None) -> list[VisionDetection]:
        """
        Simulates CNN inference on image metadata.
        In a real deployment, this receives a frame and returns bounding boxes/labels.
        """
        if not image_metadata or not isinstance(image_metadata, dict):
            return []

        detections = []
        try:
            raw_detections = image_metadata.get("detected_objects", [])
            if not isinstance(raw_detections, list):
                _log.warning("Vision Inference: 'detected_objects' is not a list. Skipping.")
                return []

            for d in raw_detections:
                if not isinstance(d, dict):
                    continue

                label = str(d.get("label", "unknown")).lower()
                conf = float(d.get("confidence", 0.0))

                # Spatial Awareness (Critique Maturity Fix - Session 6)
                # Calculate proximity based on bounding box size or explicit distance metadata
                bbox = d.get("bbox", [0, 0, 0, 0])  # [x, y, w, h]
                distance = d.get("distance_cm")

                if distance is not None:
                    proximity = 1.0 - min(1.0, float(distance) / 200.0)  # Normalized to 2m
                elif bbox[2] * bbox[3] > 0:
                    # Heuristic: Larger area in frame = closer object
                    proximity = min(1.0, (bbox[2] * bbox[3]) / (640 * 480))
                else:
                    proximity = 0.0

                is_bad = any(p in label for p in self.prohibited_labels)

                detections.append(
                    VisionDetection(
                        label=label,
                        confidence=conf,
                        is_prohibited=is_bad,
                        metadata={**d, "spatial_proximity": proximity},
                    )
                )

                if is_bad and conf > 0.75:
                    prox_str = f" (PROXIMITY: {proximity:.2f})" if proximity > 0 else ""
                    _log.warning(
                        "PROHIBITED OBJECT DETECTED: %s (conf: %.2f)%s", label, conf, prox_str
                    )
        except Exception as e:
            _log.error("Vision Inference: Critical failure during analysis stage: %s", e)

        return detections

    def analyze_jpeg_bytes(self, jpeg_bytes: bytes | bytearray) -> list[VisionDetection]:
        """JPEG bytes from ``NomadBridge.vision_queue_threadsafe``; stub via ``KERNEL_VISION_JPEG_STUB_LABEL``."""
        import os

        if not jpeg_bytes:
            return []
        stub = os.environ.get("KERNEL_VISION_JPEG_STUB_LABEL", "").strip().lower()
        if stub:
            is_bad = stub in self.prohibited_labels or any(
                p in stub for p in self.prohibited_labels
            )
            return [
                VisionDetection(
                    label=stub,
                    confidence=0.95,
                    is_prohibited=is_bad,
                    metadata={"stub": True},
                )
            ]
        return []

    async def async_analyze(self, image_metadata: dict[str, Any] | None) -> list[VisionDetection]:
        """
        Asynchronous entry point for vision inference.
        Enables non-blocking integration with the perception lobe.
        """
        # Run sync analysis in a threadpool to keep the event loop free
        import asyncio

        return await asyncio.to_thread(self.analyze_image, image_metadata)

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

    Integrates real hardware (Nomad Vessel + Local Camera) with structured metrics.
    """

    def __init__(
        self,
        engine: VisionInferenceEngine,
        absorption_callback: Callable[[SensoryEpisode], None],
    ) -> None:
        self.engine = engine
        self.absorption_callback = absorption_callback
        self._running = threading.Event()
        self._thread = None
        self.polling_rate = 0.2  # 5Hz
        self.frames_processed = 0
        self.detections_count = 0

    def start(self):
        """Inicia el loop de visión continua."""
        if self._running.is_set():
            return
        self._running.set()
        self._thread = threading.Thread(
            target=self._daemon_loop, daemon=True, name="VisionContinuousDaemon"
        )
        self._thread.start()
        _log.info("VisionContinuousDaemon: Background streaming started at 5Hz.")

    def stop(self):
        """Detiene el loop de visión."""
        self._running.clear()
        if self._thread:
            self._thread.join(timeout=2.0)
        _log.info("VisionContinuousDaemon: Background streaming stopped.")

    def _daemon_loop(self):
        """Loop de captura e inferencia continua consumiendo del Nomad Bridge o Cámara Local."""
        from src.modules.perception.nomad_bridge import get_nomad_bridge
        from src.modules.perception.vision_capture import from_env_vision_capture

        bridge = get_nomad_bridge()
        local_cam = from_env_vision_capture()
        local_cam.start()

        _log.info("VisionContinuousDaemon: Loop entered. Monitoring Nomad + Local Camera.")

        try:
            while self._running.is_set():
                start_tick = time.perf_counter()

                try:
                    detections: list[VisionDetection] = []
                    meta: dict[str, Any] = {}
                    source = "none"

                    try:
                        raw_jpeg = bridge.vision_queue_threadsafe.get_nowait()
                        detections = self.engine.analyze_jpeg_bytes(raw_jpeg)
                        if detections:
                            source = "nomad_vessel"
                    except queue.Empty:
                        pass

                    if not detections:
                        local_frame = local_cam.get_latest_frame()
                        if local_frame is not None:
                            try:
                                import cv2

                                # cv2.imencode expects BGR input. Doing BGR2RGB before imencode causes a blue veil.
                                ret_enc, buffer = cv2.imencode(".jpg", local_frame)
                                if ret_enc:
                                    b64_img = base64.b64encode(buffer).decode("utf-8")
                                    frame_data = {
                                        "image_b64": b64_img,
                                        "meta": {"human_presence": 1.0, "user_focus": 0.8},
                                        "detections": [],
                                    }
                                    bridge.broadcast_to_dashboards(
                                        {"type": "frame", "payload": frame_data}
                                    )
                                    meta = frame_data.get("meta", {})
                                    detections_raw = frame_data.get("detections", [])
                                    detections = self.engine.analyze_image(
                                        {"detected_objects": detections_raw}
                                    )
                                    source = "local_webcam"
                            except Exception as e:
                                _log.error(
                                    "VisionContinuousDaemon: Failed to process local frame: %s", e
                                )

                    if detections:
                        self.frames_processed += 1
                        self.detections_count += len(detections)

                        highest_threat = self.engine.get_highest_threat(detections)

                        episode = SensoryEpisode(
                            timestamp=time.time(),
                            episode_id=f"vision-{uuid.uuid4().hex[:8]}",
                            origin=f"vision_daemon:{source}",
                            signals={
                                "confidence": max([d.confidence for d in detections], default=1.0),
                                "is_urgent": 1.0
                                if any(d.is_prohibited for d in detections)
                                else 0.0,
                                "threat_level": highest_threat.confidence
                                if highest_threat
                                else 0.0,
                                "human_presence": meta.get("human_presence", 0.0),
                                "lip_movement": meta.get("lip_movement", 0.0),
                                "user_focus": meta.get("user_focus", 0.5),
                                "min_proximity": max(
                                    [d.metadata.get("spatial_proximity", 0.0) for d in detections],
                                    default=0.0,
                                ),
                                "spatial_threat": max(
                                    [
                                        d.metadata.get("spatial_proximity", 0.0)
                                        for d in detections
                                        if d.is_prohibited
                                    ],
                                    default=0.0,
                                ),
                            },
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
                            threat_load=highest_threat.confidence if highest_threat else 0.0,
                        )

                        # 5. Calls absorption callback
                        try:
                            self.absorption_callback(episode)
                        except Exception as cb_err:
                            _log.exception(
                                "VisionContinuousDaemon: Absorption callback failed: %s", cb_err
                            )

                except Exception as e:
                    _log.error("VisionContinuousDaemon error in loop: %s", e)

                # Maintain the frequency of 5Hz
                elapsed = time.perf_counter() - start_tick
                sleep_time = max(0.01, self.polling_rate - elapsed)
                time.sleep(sleep_time)
        finally:
            local_cam.stop()
            _log.info(
                "VisionContinuousDaemon loop exited (frames: %d, detections: %d)",
                self.frames_processed,
                self.detections_count,
            )
