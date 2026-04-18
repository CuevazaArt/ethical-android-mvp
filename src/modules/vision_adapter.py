"""
Vision Adapter Contract — Interface for Computer Vision models.

This module defines the abstract base class and data structures for
converting visual streams into ethical signals for the kernel.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

_log = logging.getLogger(__name__)


@dataclass
class VisionInference:
    """Consolidated result of a visual inference turn."""

    primary_label: str
    confidence: float
    detected_objects: list[str] = field(default_factory=list)
    raw_scores: dict[str, float] = field(default_factory=dict)
    timestamp: float = 0.0


class VisionAdapter(ABC):
    """
    Abstract base class for all vision models (CNN/Transformers).

    Implementations must provide logic for loading weights and
    running inference on raw image data.
    """

    @abstractmethod
    def load_model(self, path: str = None) -> None:
        """Initialize the model and load weights."""
        pass

    @abstractmethod
    def infer(self, frame: Any) -> VisionInference:
        """
        Run inference on a single video frame or image.

        Args:
            frame: Image data (typically numpy array from OpenCV).

        Returns:
            VisionInference object with detected classes and confidence.
        """
        pass


import os

def from_env_vision_adapter() -> VisionAdapter:
    """
    Factory method to create a VisionAdapter using 
    KERNEL_VISION_DEVICE environment variable (cpu/cuda).
    Prefers ONNX if available, falls back to MobileNetV2Adapter (Torch).
    """
    device = os.environ.get("KERNEL_VISION_DEVICE", "cpu").lower()
    
    try:
        import onnxruntime as ort
        _log.info("ONNX Runtime detected. Initializing OnnxVisionAdapter.")
        return OnnxVisionAdapter(device=device)
    except ImportError:
        _log.info("ONNX Runtime not found. Initializing MobileNetV2Adapter (Torch).")
        return MobileNetV2Adapter(device=device)


class OnnxVisionAdapter(VisionAdapter):
    """
    High-performance MobileNetV2 implementation using ONNX Runtime.
    Optimized for CPU inference in Phase 9.
    """
    def __init__(self, device: str = "cpu"):
        self.session = None
        self.device = device
        self.categories = []
        self._is_ready = False

    def load_model(self, path: str = None) -> None:
        """Loads the ONNX model and category metadata."""
        if path is None:
            # Placeholder for default bundled ONNX model path
            path = os.environ.get("KERNEL_VISION_ONNX_PATH", "models/mobilenet_v2.onnx")
        
        if not os.path.exists(path):
            _log.warning("ONNX model file not found at %s. Standing by in MOCK mode.", path)
            return

        try:
            import onnxruntime as ort
            providers = ["CPUExecutionProvider"]
            if self.device == "cuda":
                providers = ["CUDAExecutionProvider"]
            
            self.session = ort.InferenceSession(path, providers=providers)
            
            # Categories normally bundled in a separate JSON or extracted from Torchvision weights
            # For simplicity, we assume a standard MobileNetV2 category list exists
            self.categories = [f"category_{i}" for i in range(1000)] 
            self._is_ready = True
            _log.info("OnnxVisionAdapter ready (provider: %s).", providers[0])
        except Exception as e:
            _log.error("Failed to load ONNX model: %s", e)

    def infer(self, frame: Any) -> VisionInference:
        if not self._is_ready or self.session is None:
            return VisionInference(primary_label="unknown (onnx-mock)", confidence=0.0)

        import numpy as np
        import cv2

        try:
            # Standard Preprocessing for MobileNetV2 (224x224, normalized)
            # frame is BGR (OpenCV)
            resized = cv2.resize(frame, (224, 224))
            rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            img_data = rgb.astype(np.float32) / 255.0
            
            # Normalize with ImageNet mean/std
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            img_data = (img_data - mean) / std
            
            # HWC -> CHW and Batch dimension
            input_data = np.transpose(img_data, (2, 0, 1))
            input_data = np.expand_dims(input_data, axis=0)

            # Execution
            input_name = self.session.get_inputs()[0].name
            output = self.session.run(None, {input_name: input_data})[0]
            
            # Post-processing (Softmax)
            exp_scores = np.exp(output[0] - np.max(output[0]))
            probs = exp_scores / exp_scores.sum()
            
            idx = np.argmax(probs)
            label = self.categories[idx]
            conf = probs[idx]

            return VisionInference(
                primary_label=label,
                confidence=float(conf),
                detected_objects=[label],
                raw_scores={label: float(conf)},
                timestamp=0.0
            )
        except Exception as e:
            _log.error("ONNX Inference error: %s", e)
            return VisionInference(primary_label="error", confidence=0.0)


class MobileNetV2Adapter(VisionAdapter):
    """
    MobileNetV2 implementation using torchvision.

    This adapter handles image preprocessing, model execution, and
    label mapping for ethical signal extraction.
    """
    def __init__(self, device: str = "cpu"):
        self.model = None
        self.transform = None
        self.categories = []
        self.device = device
        self._is_ready = False
        self._torch_device = None

    def load_model(self, path: str = None) -> None:
        """
        Loads the pre-trained MobileNetV2 model and prepares the transform pipeline.
        """
        try:
            import torch
            from torchvision import models
            from torchvision.models import MobileNet_V2_Weights

            # Use recommended weights and categories from torchvision
            weights = MobileNet_V2_Weights.DEFAULT
            self.model = models.mobilenet_v2(weights=weights)
            
            # Map device strings to torch devices
            if self.device == "cuda" and torch.cuda.is_available():
                actual_device = torch.device("cuda")
            elif self.device == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                actual_device = torch.device("mps")
            else:
                actual_device = torch.device("cpu")
                
            self.model = self.model.to(actual_device)
            self.model.eval()
            
            self._torch_device = actual_device
            self.categories = weights.meta["categories"]
            self.transform = weights.transforms()
            self._is_ready = True
            _log.info("MobileNetV2 loaded successfully on %s.", actual_device)

        except ImportError:
            _log.warning("torch/torchvision not found. MobileNetV2Adapter will run in MOCK mode.")
            self._is_ready = False

    def infer(self, frame: Any) -> VisionInference:
        """
        Runs inference on the provided frame.
        Expects a numpy array (BGR from OpenCV) or a PIL Image.
        """
        if not self._is_ready or self.model is None:
            # Fallback mock logic for development without heavy ML environment
            return VisionInference(primary_label="unknown (mock)", confidence=0.0)

        import numpy as np
        import torch
        from PIL import Image

        try:
            # Convert OpenCV BGR to RGB PIL Image if necessary
            if isinstance(frame, np.ndarray):
                # OpenCV handles BGR, torchvision expects RGB
                frame_rgb = frame[:, :, ::-1]
                img = Image.fromarray(frame_rgb)
            else:
                img = frame

            # Preprocess and add batch dimension
            img_t = self.transform(img).unsqueeze(0).to(self._torch_device)

            with torch.no_grad():
                output = self.model(img_t)

            # Get probabilities via softmax
            probabilities = torch.nn.functional.softmax(output[0], dim=0)

            # Find the top prediction
            conf, index = torch.max(probabilities, 0)
            label = self.categories[index.item()]

            # Extract top 5 scores for the detailed report
            top5_conf, top5_idx = torch.topk(probabilities, 5)
            raw_scores = {
                self.categories[idx.item()]: float(c) for c, idx in zip(top5_conf, top5_idx)
            }

            return VisionInference(
                primary_label=label,
                confidence=float(conf),
                detected_objects=list(raw_scores.keys()),
                raw_scores=raw_scores,
                timestamp=0.0,  # To be filled by the caller based on capture time
            )

        except Exception as e:
            _log.error("Inference error: %s", e)
            return VisionInference(primary_label="error", confidence=0.0)

import asyncio

class NomadVisionConsumer:
    """
    Consumes frames from NomadBridge asynchronously and dispatches them 
    to the underlying VisionAdapter.
    """
    def __init__(self, adapter: VisionAdapter):
        # Phase 9: B.4.2 Dedicated Process offloading
        from .vision_multiprocess import MultiprocessVisionInference
        self.worker = MultiprocessVisionInference()
        self.adapter = adapter
        self._task: asyncio.Task | None = None
        self.latest_inference: VisionInference | None = None

    def start(self):
        self.worker.start()
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        from .nomad_bridge import get_nomad_bridge
        import numpy as np
        
        # We assume cv2 or PIL is used inside the adapter, we can decode using cv2 here 
        # or pass bytes to the adapter if it handles it. 
        # Since adapter expects numpy array (OpenCV BGR), we decode here.
        try:
            import cv2
        except ImportError:
            _log.error("cv2 is required for NomadVisionConsumer")
            return

        bridge = get_nomad_bridge()
        while True:
            try:
                frame_bytes = await bridge.vision_queue.get()
                np_arr = np.frombuffer(frame_bytes, np.uint8)
                img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is not None:
                    # Submit to independent process
                    self.worker.submit_frame(img)
                    # Poll for last available result (non-blocking)
                    self.latest_inference = self.worker.poll_result()
                    
                    if self.latest_inference:
                        _log.debug("Nomad vision (MP) infered: %s", self.latest_inference.primary_label)
            except asyncio.CancelledError:
                break
            except Exception as e:
                _log.error("Error in NomadVisionConsumer: %s", e)

    async def stop(self) -> None:
        self.worker.stop()
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


_nomad_vision_consumer: NomadVisionConsumer | None = None


def get_nomad_vision_consumer_optional() -> NomadVisionConsumer | None:
    """Return the active consumer, if :func:`start_nomad_vision_consumer_from_env` has run."""
    return _nomad_vision_consumer


def start_nomad_vision_consumer_from_env() -> NomadVisionConsumer | None:
    """
    When ``KERNEL_NOMAD_VISION_CONSUMER`` is set, start draining ``NomadBridge.vision_queue``
    into the default MobileNet adapter (Module S.1 — hardware-in-the-loop vision path).

    Idempotent: returns existing consumer if already started.
    """
    global _nomad_vision_consumer
    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_VISION_CONSUMER"):
        return None
    if _nomad_vision_consumer is not None:
        return _nomad_vision_consumer
    adapter = from_env_vision_adapter()
    adapter.load_model()
    _nomad_vision_consumer = NomadVisionConsumer(adapter)
    _nomad_vision_consumer.start()
    _log.info("NomadVisionConsumer started (KERNEL_NOMAD_VISION_CONSUMER=1).")
    return _nomad_vision_consumer


async def stop_nomad_vision_consumer_async() -> None:
    """Cancel background vision consumption (chat server / process shutdown)."""
    global _nomad_vision_consumer
    c = _nomad_vision_consumer
    _nomad_vision_consumer = None
    if c is not None:
        await c.stop()
        _log.info("NomadVisionConsumer stopped.")
