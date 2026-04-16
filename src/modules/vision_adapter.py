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


class MobileNetV2Adapter(VisionAdapter):
    """
    MobileNetV2 implementation using torchvision.

    This adapter handles image preprocessing, model execution, and
    label mapping for ethical signal extraction.
    """

    def __init__(self):
        self.model = None
        self.transform = None
        self.categories = []
        self._is_ready = False

    def load_model(self, path: str = None) -> None:
        """
        Loads the pre-trained MobileNetV2 model and prepares the transform pipeline.
        """
        try:
            from torchvision import models
            from torchvision.models import MobileNet_V2_Weights

            # Use recommended weights and categories from torchvision
            weights = MobileNet_V2_Weights.DEFAULT
            self.model = models.mobilenet_v2(weights=weights)
            self.model.eval()

            self.categories = weights.meta["categories"]
            self.transform = weights.transforms()
            self._is_ready = True
            _log.info("MobileNetV2 loaded successfully (CPU mode).")
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
            img_t = self.transform(img).unsqueeze(0)

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
