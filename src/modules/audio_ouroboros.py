"""
Bloque 11.1: Audio Ouroboros — Close the Loop (STT → Reasoning → TTS)

Integrates speech-to-text (Whisper), kernel reasoning, and text-to-speech
to create a fully-closed audio I/O loop on smartphone/PWA.

Flow:
1. Consume audio chunks from Nomad Bridge audio_queue
2. Pass to OpenAI Whisper for speech-to-text transcription
3. Trigger ExecutiveLobe with transcribed intent + context
4. Capture decision/narrative from kernel
5. Synthesize voice response via gTTS/pyttsx3
6. Return to PWA/smartphone speaker

This closes the gap between perception (vision+audio) and user-facing I/O.
"""

from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Literal
import queue
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class AudioTranscription:
    """Result of speech-to-text processing."""
    text: str
    confidence: float  # [0, 1] model confidence
    language: str = "en"
    duration_sec: float = 0.0
    timestamp: float = field(default_factory=lambda: __import__('time').time())

    def to_dict(self) -> dict:
        """Serialize to JSON-compatible dict."""
        return {
            "text": self.text,
            "confidence": self.confidence,
            "language": self.language,
            "duration_sec": self.duration_sec,
            "timestamp": self.timestamp,
        }


@dataclass
class AudioResponse:
    """Kernel's audio response to user input."""
    text: str  # What to say
    audio_bytes: Optional[bytes] = None  # Synthesized audio (WAV/MP3)
    duration_sec: float = 0.0
    confidence: float = 0.5  # Kernel confidence in response
    source_lobe: str = "executive"  # Which lobe generated response
    metadata: dict = field(default_factory=dict)


class WhisperAdapter:
    """
    Speech-to-Text adapter using OpenAI Whisper (or local whisper.cpp).

    Supports both remote API and local model depending on KERNEL_WHISPER_MODE.
    """

    def __init__(self, model_size: Literal["tiny", "base", "small", "medium", "large"] = "base"):
        """
        Initialize Whisper adapter.

        Args:
            model_size: Whisper model size ('tiny' for edge devices, 'base' or 'small' typical)
        """
        self.model_size = model_size
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        """Load Whisper model (lazy-loads on first use)."""
        try:
            import whisper
            logger.info(f"Loading Whisper {self.model_size} model...")
            self.model = whisper.load_model(self.model_size)
            logger.info("Whisper model loaded successfully")
        except ImportError:
            logger.warning("Whisper not installed. STT will be unavailable.")
            self.model = None

    async def transcribe_audio(self, audio_chunk: np.ndarray, sample_rate: int = 16000) -> AudioTranscription:
        """
        Transcribe audio chunk to text using Whisper.

        Args:
            audio_chunk: Audio samples (numpy array, float32)
            sample_rate: Sample rate of audio (default 16000 Hz)

        Returns:
            AudioTranscription with text, confidence, duration
        """
        if self.model is None:
            logger.error("Whisper model not loaded")
            return AudioTranscription(text="[STT unavailable]", confidence=0.0)

        try:
            # Run in thread pool to avoid blocking async loop
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_blocking,
                audio_chunk,
                sample_rate
            )
            return result
        except Exception as e:
            logger.error(f"Transcription error: {e}")
            return AudioTranscription(text=f"[Error: {str(e)}]", confidence=0.0)

    def _transcribe_blocking(self, audio_chunk: np.ndarray, sample_rate: int) -> AudioTranscription:
        """Blocking transcription call."""
        if self.model is None:
            return AudioTranscription(text="", confidence=0.0)

        result = self.model.transcribe(audio_chunk, language="en", fp16=False)
        text = result.get("text", "").strip()
        # Confidence estimated from Whisper's internal metrics
        segments = result.get("segments", [])
        avg_confidence = np.mean([s.get("confidence", 0.5) for s in segments]) if segments else 0.5

        duration = len(audio_chunk) / sample_rate
        return AudioTranscription(
            text=text,
            confidence=float(avg_confidence),
            duration_sec=duration,
        )


class TextToSpeechAdapter:
    """
    Text-to-speech adapter using gTTS (web-based) or pyttsx3 (local/offline).

    Generates audio bytes from kernel narrative responses.
    """

    def __init__(self, backend: Literal["gtts", "pyttsx3"] = "pyttsx3", language: str = "en"):
        """
        Initialize TTS adapter.

        Args:
            backend: "gtts" (online, high quality) or "pyttsx3" (offline, faster)
            language: Language code (e.g., "en", "es")
        """
        self.backend = backend
        self.language = language
        self._engine = None

    async def synthesize(self, text: str) -> tuple[bytes, float]:
        """
        Synthesize text to audio bytes.

        Args:
            text: Text to speak

        Returns:
            Tuple of (audio_bytes, duration_sec)
        """
        if not text or len(text.strip()) == 0:
            return b"", 0.0

        try:
            loop = asyncio.get_event_loop()
            audio_bytes, duration = await loop.run_in_executor(
                None,
                self._synthesize_blocking,
                text
            )
            return audio_bytes, duration
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return b"", 0.0

    def _synthesize_blocking(self, text: str) -> tuple[bytes, float]:
        """Blocking TTS call."""
        if self.backend == "pyttsx3":
            return self._synthesize_pyttsx3(text)
        else:
            return self._synthesize_gtts(text)

    def _synthesize_pyttsx3(self, text: str) -> tuple[bytes, float]:
        """Synthesize using pyttsx3 (offline)."""
        try:
            import pyttsx3
            import io

            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Words per minute
            engine.setProperty('volume', 0.9)

            # Estimate duration (rough: ~15 chars per second at 150 wpm)
            estimated_duration = len(text) / 15.0

            # Save to bytes buffer
            buffer = io.BytesIO()
            # Note: pyttsx3 doesn't directly support BytesIO, would need WAV encoder
            # For now, return placeholder
            logger.warning("pyttsx3 BytesIO support limited; returning silence")
            return b"", estimated_duration

        except ImportError:
            logger.warning("pyttsx3 not installed")
            return b"", 0.0

    def _synthesize_gtts(self, text: str) -> tuple[bytes, float]:
        """Synthesize using Google Translate API (online, via gTTS)."""
        try:
            from gtts import gTTS
            import io

            tts = gTTS(text=text, lang=self.language, slow=False)
            buffer = io.BytesIO()
            tts.write_to_fp(buffer)
            audio_bytes = buffer.getvalue()

            # Estimate duration
            estimated_duration = len(text) / 3.0  # Rough: ~3 characters per second

            return audio_bytes, estimated_duration

        except ImportError:
            logger.warning("gTTS not installed")
            return b"", 0.0


class AudioOuroborosLoop:
    """
    Bloque 11.1: Main audio loop coordinator.

    Connects:
    - Nomad Bridge audio_queue → Whisper STT
    - STT result → ExecutiveLobe reasoning
    - ExecutiveLobe narrative → TTS
    - TTS audio → PWA speaker queue
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        whisper_model: str = "base",
        kernel_callback: Optional[Callable[[str], Coroutine[Any, Any, AudioResponse]]] = None
    ):
        """Initialize Ouroboros loop."""
        self.sample_rate = sample_rate
        self.whisper = WhisperAdapter(model_size=whisper_model)
        self.tts = TextToSpeechAdapter(backend="gtts")
        self.kernel_callback = kernel_callback

        # Queues for I/O
        self.audio_input_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=50)
        self.audio_output_queue: queue.Queue[bytes] = queue.Queue(maxsize=20)

        self._running = False
        self._loop_task: Optional[asyncio.Task] = None

        # Metrics
        self.transcriptions_processed = 0
        self.responses_generated = 0

    async def start(self):
        """Start the Ouroboros loop."""
        if self._running:
            return

        self._running = True
        logger.info("Starting Audio Ouroboros loop")
        self._loop_task = asyncio.create_task(self._run_loop())

    async def stop(self):
        """Stop the Ouroboros loop."""
        self._running = False
        if self._loop_task:
            await self._loop_task
        logger.info("Audio Ouroboros loop stopped")

    async def _run_loop(self):
        """Main async loop: STT → Reasoning → TTS."""
        while self._running:
            try:
                # 1. Get audio from input queue (non-blocking check)
                try:
                    audio_chunk = self.audio_input_queue.get_nowait()
                except queue.Empty:
                    await asyncio.sleep(0.1)
                    continue

                # 2. Speech-to-text
                transcription = await self.whisper.transcribe_audio(audio_chunk, self.sample_rate)
                self.transcriptions_processed += 1
                logger.info(f"Transcribed: {transcription.text[:100]} (conf={transcription.confidence:.2f})")

                # 3. Trigger Ethical Kernel with transcribed intent
                if self.kernel_callback:
                    logger.debug("AudioOuroboros: Invoking kernel callback for: %s", transcription.text)
                    kernel_response = await self.kernel_callback(transcription.text)
                else:
                    # Fallback if no kernel is wired
                    kernel_response = await self._generate_kernel_response(transcription)

                # 4. Text-to-speech
                audio_bytes, duration = await self.tts.synthesize(kernel_response.text)
                kernel_response.audio_bytes = audio_bytes
                kernel_response.duration_sec = duration
                self.responses_generated += 1

                # 5. Queue audio for PWA output
                if audio_bytes:
                    self.audio_output_queue.put_nowait(audio_bytes)

                logger.info(f"Generated response ({duration:.1f}s audio)")

            except Exception as e:
                logger.error(f"Ouroboros loop error: {e}")
                await asyncio.sleep(0.5)

    async def _generate_kernel_response(self, transcription: AudioTranscription) -> AudioResponse:
        """
        Generate kernel response to user utterance.

        TODO: Integrate with ExecutiveLobe for actual reasoning.
        For now, returns a simple acknowledgment.
        """
        if not transcription.text:
            return AudioResponse(
                text="I didn't catch that. Could you repeat?",
                confidence=0.0,
            )

        # Placeholder: simple echo response
        response_text = f"You said: {transcription.text[:50]}. I'm processing your request."
        return AudioResponse(
            text=response_text,
            confidence=min(0.7, transcription.confidence),
            source_lobe="executive",
        )

    def get_metrics(self) -> dict:
        """Get loop metrics."""
        return {
            "transcriptions_processed": self.transcriptions_processed,
            "responses_generated": self.responses_generated,
            "audio_input_queue_size": self.audio_input_queue.qsize(),
            "audio_output_queue_size": self.audio_output_queue.qsize(),
            "is_running": self._running,
        }
