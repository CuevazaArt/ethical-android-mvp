import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import numpy as np
from src.modules.perception.vision_adapter import MobileNetV2Adapter


def test_inference():
    adapter = MobileNetV2Adapter()
    print("Loading model...")
    adapter.load_model()

    # Create a dummy image (RGB 224x224)
    dummy_frame = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)

    print("Running inference...")
    res = adapter.infer(dummy_frame)

    print(f"Result: {res.primary_label}")
    print(f"Confidence: {res.confidence:.4f}")
    print(f"Top 5: {list(res.raw_scores.keys())}")


if __name__ == "__main__":
    test_inference()
