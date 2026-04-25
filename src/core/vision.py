"""
Ethos Core — Vision Engine (V2 Minimal)

Procesa frames JPEG del Nomad PWA y extrae señales contextuales.

Lo que hace:
1. Decodifica JPEG base64 → imagen numpy
2. Extrae señales simples: brillo, movimiento (diff inter-frame), detección de rostros
3. Devuelve VisionSignals para que el kernel adapte su comportamiento

Sin modelos pesados. Sin GPU. Solo OpenCV + PIL para máxima compatibilidad.
"""

from __future__ import annotations

import base64
import logging
import math
import time
from dataclasses import dataclass

import cv2
import numpy as np

_log = logging.getLogger(__name__)


@dataclass
class VisionSignals:
    """Señales extraídas de un frame de video."""

    brightness: float = 0.5  # 0.0 oscuro → 1.0 brillante
    motion: float = 0.0  # 0.0 estático → 1.0 movimiento intenso
    faces_detected: int = 0  # número de rostros visibles
    face_present: bool = False  # hay al menos un rostro
    low_light: bool = False  # condición de poca luz
    latency_ms: float = 0.0  # tiempo de procesamiento

    def to_dict(self) -> dict:
        return {
            "brightness": round(self.brightness, 3),
            "motion": round(self.motion, 3),
            "faces_detected": self.faces_detected,
            "face_present": self.face_present,
            "low_light": self.low_light,
            "latency_ms": round(self.latency_ms, 1),
        }


class VisionEngine:
    """
    Procesador de frames de video. Stateful — mantiene el frame anterior
    para calcular movimiento entre frames.
    """

    # Detector de rostros de Haar (incluido en OpenCV, sin descarga)
    _face_cascade: cv2.CascadeClassifier | None = None

    def __init__(self) -> None:
        self._prev_gray: np.ndarray | None = None
        self._frame_count: int = 0
        self._load_face_cascade()

    def _load_face_cascade(self) -> None:
        """Carga el clasificador Haar de rostros incluido en OpenCV."""
        if VisionEngine._face_cascade is not None:
            return
        try:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            VisionEngine._face_cascade = cv2.CascadeClassifier(cascade_path)
            _log.info("Face cascade loaded from %s", cascade_path)
        except Exception as e:
            _log.warning("Could not load face cascade: %s", e)
            VisionEngine._face_cascade = None

    def process_b64(self, image_b64: str) -> VisionSignals | None:
        """
        Procesa un frame JPEG codificado en base64.

        Args:
            image_b64: Frame JPEG en base64 (del Nomad PWA).

        Returns:
            VisionSignals o None si el frame es inválido.
        """
        t0 = time.perf_counter()

        try:
            jpeg_bytes = base64.b64decode(image_b64)
        except Exception as e:
            _log.warning("Vision: base64 decode failed: %s", e)
            return None

        try:
            nparr = np.frombuffer(jpeg_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if frame is None or frame.size == 0:
                return None
        except Exception as e:
            _log.warning("Vision: JPEG decode failed: %s", e)
            return None

        signals = VisionSignals()

        # 1. Brillo (media del canal V en HSV)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        brightness_raw = float(np.mean(hsv[:, :, 2])) / 255.0
        signals.brightness = brightness_raw if math.isfinite(brightness_raw) else 0.5
        signals.low_light = signals.brightness < 0.15

        # 2. Movimiento (diff con frame anterior)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if self._prev_gray is not None and self._prev_gray.shape == gray.shape:
            diff = cv2.absdiff(gray, self._prev_gray)
            motion_raw = float(np.mean(diff)) / 255.0
            signals.motion = motion_raw if math.isfinite(motion_raw) else 0.0
        self._prev_gray = gray

        # 3. Detección de rostros (solo cada 5 frames para no saturar CPU)
        self._frame_count += 1
        if VisionEngine._face_cascade is not None and self._frame_count % 5 == 0:
            faces = VisionEngine._face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=4,
                minSize=(40, 40),
            )
            signals.faces_detected = len(faces)
            signals.face_present = len(faces) > 0

        elapsed_ms = (time.perf_counter() - t0) * 1000
        signals.latency_ms = elapsed_ms if math.isfinite(elapsed_ms) else 0.0
        _log.debug(
            "Vision: frame %d | bright=%.2f motion=%.3f faces=%d latency=%.0fms",
            self._frame_count,
            signals.brightness,
            signals.motion,
            signals.faces_detected,
            signals.latency_ms,
        )
        return signals


# === Self-test ===
if __name__ == "__main__":
    import sys

    engine = VisionEngine()

    # Genera un frame de prueba sintético (gris uniforme 320x240)
    test_frame = np.ones((240, 320, 3), dtype=np.uint8) * 128
    _, jpeg_bytes = cv2.imencode(".jpg", test_frame)
    b64 = base64.b64encode(jpeg_bytes.tobytes()).decode()

    sig = engine.process_b64(b64)
    if sig:
        print("[OK] Frame procesado:")
        for k, v in sig.to_dict().items():
            print(f"     {k}: {v}")
        assert math.isfinite(sig.brightness), "brightness no finito"
        assert math.isfinite(sig.motion), "motion no finito"
        print("\n[OK] Anti-NaN: todos los valores son finitos")
    else:
        print("[FAIL] proceso de frame fallido")
        sys.exit(1)
