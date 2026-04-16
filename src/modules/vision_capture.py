"""
Vision Capture Interface (Block B4)
Handles real-time video stream acquisition from local hardware.
"""

import logging
import threading
import time
from typing import Any

_log = logging.getLogger(__name__)

try:
    import cv2

    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False

import os

def from_env_vision_capture() -> "VideoCaptureInterface":
    """
    Factory method to create a VideoCaptureInterface using 
    KERNEL_VISION_CAMERA_ID environment variable.
    """
    cam_id_str = os.environ.get("KERNEL_VISION_CAMERA_ID", "0").strip()
    try:
        cam_id = int(cam_id_str)
    except ValueError:
        cam_id = 0
    return VideoCaptureInterface(camera_id=cam_id)

class VideoCaptureInterface:
    """
    Interface for local camera hardware.
    Maintains a dedicated thread to ensure 'get_latest_frame' is always non-blocking.
    """

    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap: Any = None  # cv2.VideoCapture when OpenCV is available
        self._running = False
        self._thread: threading.Thread | None = None
        self._last_frame: Any = None
        self.lock = threading.Lock()

    def start(self) -> None:
        """Starts the capture thread if OpenCV is available."""
        if not HAS_CV2:
            _log.warning("opencv-python not found. CaptureInterface will run in MOCK mode.")
            return

        if self._running:
            return

        self.cap = cv2.VideoCapture(self.camera_id)
        if not self.cap.isOpened():
            _log.error("Could not open camera %d", self.camera_id)
            return

        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()
        _log.info("Camera %d capture started.", self.camera_id)

    def stop(self) -> None:
        """Stops the capture thread and releases the hardware."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
        if self.cap:
            self.cap.release()
            self.cap = None
        _log.info("Camera capture stopped.")

    def _capture_loop(self) -> None:
        """Dedicated thread loop for reading frames at maximum hardware rate."""
        while self._running and self.cap:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self._last_frame = frame
            else:
                # Brief sleep to prevent CPU pegging if camera drops or slows
                time.sleep(0.01)

    def get_latest_frame(self) -> Any | None:
        """Provides the most recent frame captured by the thread."""
        with self.lock:
            return self._last_frame
