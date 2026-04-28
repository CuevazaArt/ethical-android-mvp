# Copyright 2026 Juan Cuevaz / Mos Ex Machina
# Licensed under the Apache License, Version 2.0
# See LICENSE file for details.

import logging
import time

import edge_tts

_log = logging.getLogger(__name__)


async def synthesize(
    text: str,
    voice: str = "es-MX-DaliaNeural",
    pitch: str = "+0Hz",
    rate: str = "+0%",
    volume: str = "+50%",
) -> bytes | None:
    """
    Synthesize text to MP3 using edge-tts.
    Returns bytes if successful, None if it fails.
    """
    t0 = time.perf_counter()
    try:
        communicate = edge_tts.Communicate(text, voice, pitch=pitch, rate=rate, volume=volume)
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])

        elapsed = (time.perf_counter() - t0) * 1000
        _log.info("Neural TTS generated in %.0fms (%d bytes)", elapsed, len(audio_data))
        return bytes(audio_data)
    except Exception as e:
        _log.error("Neural TTS failed: %s", e)
        return None
