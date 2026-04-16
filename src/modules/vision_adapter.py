"""
Vision Adapter Contract — Interface for Computer Vision models.

This module defines the abstract base class and data structures for 
converting visual streams into ethical signals for the kernel.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


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
    Placeholder for MobileNetV2 implementation.
    
    TASK (B2): Implement the logic here using torchvision.
    """
    
    def load_model(self, path: str = None) -> None:
        # TODO: Implement weight loading (Block B2)
        pass

    def infer(self, frame: Any) -> VisionInference:
        # TODO: Implement inference pipeline (Block B2)
        return VisionInference(primary_label="unknown", confidence=0.0)
