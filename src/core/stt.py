"""
Ethos Core — STT Engine (V2 Minimal)

Transcribe audio PCM a texto.

Estrategia:
1. Si faster-whisper está instalado y el modelo cargado → usa Whisper.
2. Si no → devuelve None (el cliente usa Web Speech API como fallback).

No falla, no bloquea. Si Whisper no está disponible, simplemente retorna None
y el cliente sigue usando su STT nativo (que ya funciona).

Uso:
    from src.core.stt import transcribe_pcm
    text = await transcribe_pcm(pcm_bytes, sample_rate=16000)
    # text es str si hubo transcripción, None si no hay STT disponible
"""

from __future__ import annotations

import logging
import math
import time
from typing import Optional

_log = logging.getLogger(__name__)

# Intenta cargar faster-whisper. Si no está instalado, todo sigue funcionando.
try:
    from faster_whisper import WhisperModel as _WhisperModel
    _WHISPER_AVAILABLE = True
except ImportError:
    _WhisperModel = None
    _WHISPER_AVAILABLE = False

# Singleton del modelo (se carga una sola vez al primer uso)
_model: object | None = None
_MODEL_SIZE = "tiny"  # tiny=39MB, base=74MB, small=244MB


def _get_model() -> object | None:
    """Carga el modelo Whisper al primer uso. Retorna None si no disponible."""
    global _model
    if _model is not None:
        return _model
    if not _WHISPER_AVAILABLE:
        _log.info("faster-whisper no instalado — STT server-side no disponible")
        return None
    try:
        t0 = time.perf_counter()
        _model = _WhisperModel(_MODEL_SIZE, device="cpu", compute_type="int8")
        elapsed_ms = (time.perf_counter() - t0) * 1000
        _log.info("Whisper '%s' cargado en %.0fms", _MODEL_SIZE, elapsed_ms)
        return _model
    except Exception as e:
        _log.warning("Error cargando Whisper: %s", e)
        return None


async def transcribe_pcm(
    pcm_bytes: bytes,
    sample_rate: int = 16000,
    language: str = "es",
) -> Optional[str]:
    """
    Transcribe bytes de audio PCM a texto.

    Args:
        pcm_bytes: Audio crudo int16 little-endian mono.
        sample_rate: Frecuencia de muestreo (default 16kHz).
        language: Idioma para Whisper (default 'es').

    Returns:
        Texto transcrito, o None si STT no está disponible.
    """
    model = _get_model()
    if model is None:
        return None

    if len(pcm_bytes) < 512:
        return None  # Frame demasiado corto

    try:
        import io
        import struct
        import numpy as np

        # Convertir int16 PCM → float32 numpy [-1.0, 1.0]
        num_samples = len(pcm_bytes) // 2
        samples = struct.unpack(f"<{num_samples}h", pcm_bytes[:num_samples * 2])
        audio = np.array(samples, dtype=np.float32) / 32768.0

        # Anti-NaN: verificar que el audio es finito
        if not np.all(np.isfinite(audio)):
            _log.warning("STT: frame contiene NaN/Inf, ignorando")
            return None

        t0 = time.perf_counter()
        segments, info = model.transcribe(
            audio,
            language=language,
            beam_size=1,           # Mínimo para latencia baja
            vad_filter=True,       # Filtra silencio automáticamente
            vad_parameters={"min_silence_duration_ms": 300},
        )
        text = " ".join(seg.text for seg in segments).strip()
        elapsed_ms = (time.perf_counter() - t0) * 1000
        _log.info("Whisper STT: %.0fms → '%s'", elapsed_ms, text[:80])
        return text if text else None

    except Exception as e:
        _log.error("STT transcription failed: %s", e)
        return None


def is_available() -> bool:
    """Retorna True si Whisper está instalado y el modelo está listo."""
    return _get_model() is not None


# === Self-test ===
if __name__ == "__main__":
    if _WHISPER_AVAILABLE:
        print("[OK] faster-whisper instalado")
        m = _get_model()
        print(f"[OK] Modelo '{_MODEL_SIZE}' {'cargado' if m else 'fallido'}")
    else:
        print("[!]  faster-whisper no instalado")
        print("     Instala con: pip install faster-whisper")
        print("     Sin Whisper, el sistema usa Web Speech API del browser (ya funciona).")
    print("\nSTT server-side es OPCIONAL. El sistema es funcional sin el.")
