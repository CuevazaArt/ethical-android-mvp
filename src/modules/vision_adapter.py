from __future__ import annotations
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
import os

if TYPE_CHECKING:
    import torch
    from PIL.Image import Image as PILImage

_log = logging.getLogger(__name__)


@dataclass
class VisionInference:
    """Consolidated result of a visual inference turn."""

    primary_label: str
    confidence: float
    detected_objects: List[str] = field(default_factory=list)
    raw_scores: Dict[str, float] = field(default_factory=dict)
    timestamp: float = 0.0


class VisionAdapter(ABC):
    """
    Abstract base class for all vision models (CNN/Transformers).
    """

    @abstractmethod
    def load_model(self, path: Optional[str] = None) -> None:
        """Initialize the model and load weights."""
        pass

    @abstractmethod
    def infer(self, frame: Any) -> VisionInference:
        """
        Run inference on a single video frame or image.
        """
        pass


def from_env_vision_adapter() -> MobileNetV2Adapter:
    """
    Factory method to create a MobileNetV2Adapter using 
    KERNEL_VISION_DEVICE environment variable (cpu/cuda).
    """
    device: str = os.environ.get("KERNEL_VISION_DEVICE", "cpu").lower()
    return MobileNetV2Adapter(device=device)


class MobileNetV2Adapter(VisionAdapter):
    """
    MobileNetV2 implementation using torchvision.
    """
    def __init__(self, device: str = "cpu") -> None:
        self.model: Optional[Any] = None # torch.nn.Module
        self.transform: Optional[Any] = None # Callable
        self.categories: List[str] = []
        self.device: str = device
        self._is_ready: bool = False
        self._torch_device: Optional[Any] = None # torch.device

    def load_model(self, path: Optional[str] = None) -> None:
        """
        Loads the pre-trained MobileNetV2 model and prepares the transform pipeline.
        """
        try:
            import torch
            from torchvision import models
            from torchvision.models import MobileNet_V2_Weights

            weights = MobileNet_V2_Weights.DEFAULT
            self.model = models.mobilenet_v2(weights=weights)
            
            if self.device == "cuda" and torch.cuda.is_available():
                actual_device = torch.device("cuda")
            elif self.device == "mps" and hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                actual_device = torch.device("mps")
            else:
                actual_device = torch.device("cpu")
                
            if self.model is not None:
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
        """
        if not self._is_ready or self.model is None:
            return VisionInference(primary_label="unknown (mock)", confidence=0.0)

        import numpy as np
        import torch
        from PIL import Image

        try:
            if isinstance(frame, np.ndarray):
                frame_rgb = frame[:, :, ::-1]
                img: PILImage = Image.fromarray(frame_rgb)
            else:
                img = frame

            if self.transform is not None and self._torch_device is not None:
                img_t: torch.Tensor = self.transform(img).unsqueeze(0).to(self._torch_device)

                with torch.no_grad():
                    output: torch.Tensor = self.model(img_t)

                probabilities: torch.Tensor = torch.nn.functional.softmax(output[0], dim=0)

                conf_tensor, index_tensor = torch.max(probabilities, 0)
                conf: float = float(conf_tensor.item())
                label: str = self.categories[int(index_tensor.item())]

                top5_conf, top5_idx = torch.topk(probabilities, 5)
                raw_scores: Dict[str, float] = {
                    self.categories[int(idx.item())]: float(c) for c, idx in zip(top5_conf, top5_idx)
                }

                return VisionInference(
                    primary_label=label,
                    confidence=conf,
                    detected_objects=list(raw_scores.keys()),
                    raw_scores=raw_scores,
                    timestamp=0.0,
                )
            
            return VisionInference(primary_label="unconfigured", confidence=0.0)

        except Exception as e:
            _log.error("Inference error: %s", e)
            return VisionInference(primary_label="error", confidence=0.0)

import asyncio


def jpeg_bytes_from_vision_queue_item(item: Any) -> Optional[bytes]:
    """
    Normalize items from :attr:`NomadBridge.vision_queue`.
    """
    if item is None:
        return None
    if isinstance(item, (bytes, bytearray)):
        return bytes(item)
    if isinstance(item, dict):
        rb = item.get("raw_bytes")
        if rb is None:
            return None
        if isinstance(rb, (bytes, bytearray)):
            return bytes(rb)
    return None


class NomadVisionConsumer:
    """
    Consumes frames from NomadBridge asynchronously and dispatches them 
    """
    def __init__(self, adapter: VisionAdapter) -> None:
        self.adapter: VisionAdapter = adapter
        self._task: Optional[asyncio.Task[None]] = None
        self.latest_inference: Optional[VisionInference] = None

    def start(self) -> None:
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self) -> None:
        from .nomad_bridge import get_nomad_bridge
        import numpy as np
        
        try:
            import cv2
        except ImportError:
            _log.error("cv2 is required for NomadVisionConsumer")
            return

        from src.modules.nomad_bridge import NomadBridge
        bridge: NomadBridge = get_nomad_bridge()
        while True:
            try:
                raw: Any = await bridge.vision_queue.get()
                frame_bytes: Optional[bytes] = jpeg_bytes_from_vision_queue_item(raw)
                if not frame_bytes:
                    _log.debug("Nomad vision: skipped queue item (no raw JPEG bytes)")
                    continue
                np_arr: np.ndarray = np.frombuffer(frame_bytes, np.uint8)
                img: Optional[np.ndarray] = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                if img is not None:
                    infer_result: VisionInference = await asyncio.to_thread(self.adapter.infer, img)
                    self.latest_inference = infer_result
                    _log.debug("Nomad vision inferred: %s", infer_result.primary_label)
            except asyncio.CancelledError:
                break
            except Exception as e:
                _log.error("Error in NomadVisionConsumer: %s", e)

    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


_nomad_vision_consumer: Optional[NomadVisionConsumer] = None


def get_nomad_vision_consumer_optional() -> Optional[NomadVisionConsumer]:
    """Return the active consumer, if :func:`start_nomad_vision_consumer_from_env` has run."""
    return _nomad_vision_consumer


def start_nomad_vision_consumer_from_env() -> Optional[NomadVisionConsumer]:
    """
    Start draining NomadBridge.vision_queue into the default adapter.
    """
    global _nomad_vision_consumer
    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_VISION_CONSUMER"):
        return None
    if _nomad_vision_consumer is not None:
        return _nomad_vision_consumer
    adapter: MobileNetV2Adapter = from_env_vision_adapter()
    adapter.load_model()
    _nomad_vision_consumer = NomadVisionConsumer(adapter)
    _nomad_vision_consumer.start()
    _log.info("NomadVisionConsumer started (KERNEL_NOMAD_VISION_CONSUMER=1).")
    return _nomad_vision_consumer


async def stop_nomad_vision_consumer_async() -> None:
    """Cancel background vision consumption."""
    global _nomad_vision_consumer
    c: Optional[NomadVisionConsumer] = _nomad_vision_consumer
    _nomad_vision_consumer = None
    if c is not None:
        await c.stop()
        _log.info("NomadVisionConsumer stopped.")
