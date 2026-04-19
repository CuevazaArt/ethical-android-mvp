"""
Situated Vision Inference (B2) — CNN-based object detection for ethical safety.

Identifies physical threats (weapons, prohibited items) from sensor image streams
and provides direct 'Absolute Evil' vetoes to the kernel.

Module 9.1 (``VisionContinuousDaemon``): background loop (~5 Hz by default) drains
``NomadBridge.vision_queue_threadsafe`` (thread-safe mirror of the async vision queue),
runs JPEG decode + ``VisionInferenceEngine.analyze_jpeg_bytes`` in a worker thread
so the cadence loop stays non-blocking (async preprocessing vs the hot path).
"""

from __future__ import annotations

import logging
import os
import queue
import threading
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout
from dataclasses import dataclass, field
from typing import Any, Callable

from src.kernel_lobes.models import SensoryEpisode
from src.kernel_utils import kernel_env_truthy

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
        if not image_metadata:
            return []

        detections = []
        raw_detections = image_metadata.get("detected_objects", [])

        for d in raw_detections:
            label = d.get("label", "unknown").lower()
            conf = d.get("confidence", 0.0)

            is_bad = any(p in label for p in self.prohibited_labels)

            detections.append(
                VisionDetection(
                    label=label,
                    confidence=conf,
                    is_prohibited=is_bad,
                    metadata=d,
                )
            )

            if is_bad and conf > 0.75:
                _log.warning("PROHIBITED OBJECT DETECTED: %s (conf: %.2f)", label, conf)

        return detections

    def analyze_jpeg_bytes(self, jpeg: bytes | None) -> list[VisionDetection]:
        """
        Decode a JPEG frame and derive detections for the continuous daemon.

        Production path: decode with OpenCV when available. With ``KERNEL_VISION_DAEMON_CNN=1``,
        runs MobileNetV2 (``vision_adapter``) on the decoded frame and maps labels to
        :class:`VisionDetection`. Tests / dev can set ``KERNEL_VISION_JPEG_STUB_LABEL`` to
        force synthetic ``detected_objects`` without a model.
        """
        if not jpeg:
            return []
        stub = os.environ.get("KERNEL_VISION_JPEG_STUB_LABEL", "").strip()
        if stub:
            return self.analyze_image(
                {"detected_objects": [{"label": stub.lower(), "confidence": 0.82}]}
            )
        if kernel_env_truthy("KERNEL_VISION_DAEMON_CNN"):
            return self._analyze_jpeg_cnn(jpeg)
        try:
            import numpy as np
            import cv2
        except ImportError:
            return []
        arr = np.frombuffer(jpeg, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return []
        # Decoded OK — no CNN: defer until stub or KERNEL_VISION_DAEMON_CNN.
        return []

    def _analyze_jpeg_cnn(self, jpeg: bytes) -> list[VisionDetection]:
        """MobileNetV2 top-1 label → :class:`VisionDetection` (optional torch)."""
        try:
            import numpy as np
            import cv2
        except ImportError:
            return []
        arr = np.frombuffer(jpeg, dtype=np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            return []
        if self._cnn_adapter is None:
            from src.modules.vision_adapter import from_env_vision_adapter

            self._cnn_adapter = from_env_vision_adapter()
            self._cnn_adapter.load_model()
        adapter = self._cnn_adapter
        if not getattr(adapter, "_is_ready", False):
            return []
        vi = adapter.infer(img)
        label_l = (vi.primary_label or "").lower()
        is_bad = any(p in label_l for p in self.prohibited_labels) or any(
            w in label_l for w in ("revolver", "rifle", "knife", "weapon", "assault rifle")
        )
        return [
            VisionDetection(
                label=vi.primary_label,
                confidence=float(vi.confidence),
                is_prohibited=is_bad,
                metadata={"raw_scores": vi.raw_scores},
            )
        ]

    def get_highest_threat(self, detections: list[VisionDetection]) -> VisionDetection | None:
        """Returns the most confident prohibited detection."""
        threats = [d for d in detections if d.is_prohibited and d.confidence > 0.7]
        if not threats:
            return None
        return max(threats, key=lambda x: x.confidence)


class VisionContinuousDaemon:
    """
    Background vision loop (Module 9.1): ~5 Hz cadence, drains the thread-safe Nomad
    JPEG mirror, runs inference in a single worker thread.
    """

    def __init__(
        self,
        engine: VisionInferenceEngine,
        absorption_callback: Callable[[SensoryEpisode], None],
    ) -> None:
        self.engine = engine
        self.absorption_callback = absorption_callback
        self.running = False
        self._thread: threading.Thread | None = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="vision_infer")
        hz = vision_daemon_hz()
        self.polling_rate = 1.0 / hz if hz > 0 else 0.2

    def start(self) -> None:
        """Start the background vision loop."""
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(
            target=self._daemon_loop, daemon=True, name="VisionContinuousDaemon"
        )
        self._thread.start()
        _log.info(
            "VisionContinuousDaemon: started (target %.1f Hz, infer timeout %.2fs).",
            1.0 / self.polling_rate if self.polling_rate > 0 else 0,
            vision_daemon_infer_timeout_s(),
        )

    def stop(self) -> None:
        """Stop the loop and shut down the inference executor."""
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)
        self._executor.shutdown(wait=False, cancel_futures=True)
        _log.info("VisionContinuousDaemon: stopped.")

    def _daemon_loop(self) -> None:
        """Drain ``vision_queue_threadsafe``; offload decode/inference to the executor."""
        from src.modules.nomad_bridge import get_nomad_bridge

        bridge = get_nomad_bridge()
        ts_q: queue.Queue[bytes] = bridge.vision_queue_threadsafe
        timeout_s = vision_daemon_infer_timeout_s()
        while self.running:
            start_tick = time.perf_counter()
            try:
                try:
                    jpeg = ts_q.get_nowait()
                except queue.Empty:
                    jpeg = None

                if jpeg:
                    fut = self._executor.submit(self.engine.analyze_jpeg_bytes, jpeg)
                    try:
                        detections = fut.result(timeout=timeout_s)
                    except FuturesTimeout:
                        _log.warning("VisionContinuousDaemon: inference timeout; dropping frame.")
                        continue

                    highest = self.engine.get_highest_threat(detections)
                    threat_conf = highest.confidence if highest else 0.0
                    episode = SensoryEpisode(
                        timestamp=time.time(),
                        origin="vision_daemon",
                        entities=[d.label for d in detections],
                        signals={
                            "confidence": max((d.confidence for d in detections), default=0.0),
                            "is_urgent": 1.0 if any(d.is_prohibited for d in detections) else 0.0,
                            "threat_level": threat_conf,
                            "human_presence": 0.0,
                            "lip_movement": 0.0,
                            "user_focus": 0.5,
                        },
                    )
                    self.absorption_callback(episode)

            except Exception as e:
                _log.error("VisionContinuousDaemon error in loop: %s", e)

            elapsed = time.perf_counter() - start_tick
            sleep_time = max(0.01, self.polling_rate - elapsed)
            time.sleep(sleep_time)
