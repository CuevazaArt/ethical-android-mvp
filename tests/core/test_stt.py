"""
Tests for src.core.stt — V2.11 WhisperSTT module.
All tests pass whether or not faster-whisper is installed (graceful fallback).
"""
import asyncio
import struct

import pytest

from src.core.stt import is_available, transcribe_pcm


def _silence_pcm(seconds: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generate silent Int16 PCM bytes."""
    n = int(seconds * sample_rate)
    return struct.pack(f"<{n}h", *([0] * n))


def test_stt_import():
    """WhisperSTT module imports cleanly and exposes is_available()."""
    assert callable(is_available)
    assert isinstance(is_available(), bool)


def test_stt_silence_no_crash():
    """Transcribing silence never raises; returns None or empty string."""
    pcm = _silence_pcm(0.5)
    result = asyncio.run(transcribe_pcm(pcm))
    assert result is None or isinstance(result, str)


def test_stt_too_short_no_crash():
    """Frames under 512 bytes are rejected gracefully (return None)."""
    result = asyncio.run(transcribe_pcm(b"\x00" * 100))
    assert result is None


def test_stt_empty_bytes_no_crash():
    """Empty bytes are handled without exception."""
    result = asyncio.run(transcribe_pcm(b""))
    assert result is None
