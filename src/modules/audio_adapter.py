"""
Audio Perception Pipeline — Blocks A1 & A2 (Capture & RingBuffer)
This module provides the low-level acoustic stream ingestion framework.
"""

import queue
import threading
import time
from dataclasses import dataclass

import numpy as np

from ..observability.metrics import (
    observe_audio_ai_inference_seconds,
    record_audio_ai_hotword_detection,
)


class AudioRingBuffer:
    """
    Block A2: Maintains a continuous, thread-safe queue of incoming audio chunks.
    Overwrites the oldest data if the buffer overflows to keep the feed real-time.
    """

    def __init__(self, capacity_chunks: int = 100):
        self.capacity = capacity_chunks
        self.buffer: queue.Queue[np.ndarray] = queue.Queue(maxsize=capacity_chunks)
        self.lock = threading.Lock()

    def append(self, chunk: np.ndarray) -> None:
        """Appends a new PCM audio chunk. Evicts oldest if full."""
        with self.lock:
            if self.buffer.full():
                try:
                    self.buffer.get_nowait()
                except queue.Empty:
                    pass
            self.buffer.put_nowait(chunk)

    def get_next(self) -> np.ndarray | None:
        """Pulls the oldest unread chunk from the buffer."""
        try:
            return self.buffer.get_nowait()
        except queue.Empty:
            return None

    def flush(self) -> list[np.ndarray]:
        """Returns all currently buffered chunks and empties the queue."""
        frames = []
        with self.lock:
            while not self.buffer.empty():
                frames.append(self.buffer.get_nowait())
        return frames


class AudioCaptureInterface:
    """
    Block A1: Interface for the microphone/ADC.
    Continuously samples audio and pushes it to the RingBuffer.
    """

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024):
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.ring_buffer = AudioRingBuffer()

        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        """Starts the asynchronous capture thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Halts the capture thread."""
        self._running = False
        if self._thread:
            self._thread.join()

    def _capture_loop(self) -> None:
        """
        Hardware acquisition loop.
        Currently implemented as a mock generator to fulfill the contract framework.
        TODO (Hardware Integration): Replace `np.zeros` with `sounddevice` or `pyaudio` read calls.
        """
        # Duration of one chunk in seconds
        chunk_duration = self.chunk_size / self.sample_rate

        while self._running:
            # Simulate picking up a block of audio data (silence for now)
            # Future edge implementations will bind directly to the ADC stream here.
            simulated_pcm = np.zeros(self.chunk_size, dtype=np.float32)
            self.ring_buffer.append(simulated_pcm)

            # Wait precisely the time it takes to "record" the chunk to avoid flooding
            time.sleep(chunk_duration)


class AudioPreprocessor:
    """
    Block A3 & A4: Signal processing and feature extraction.
    Handles Voice Activity Detection (VAD) and feature transformations (Spectrograms).
    """

    def __init__(self, sample_rate: int = 16000, energy_threshold: float = 0.01):
        self.sample_rate = sample_rate
        self.energy_threshold = energy_threshold

    def normalize(self, pcm: np.ndarray) -> np.ndarray:
        """Normalizes audio to -1.0 to 1.0 range."""
        max_val = np.max(np.abs(pcm))
        if max_val > 0:
            return pcm / max_val
        return pcm

    def detect_voice(self, pcm: np.ndarray) -> bool:
        """
        Block A3: Simple energy-based Voice Activity Detection.
        Returns True if the audio chunk likely contains human speech or significant noise.
        """
        energy = np.mean(pcm**2)
        return energy > self.energy_threshold

    def compute_mel_spectrogram(self, pcm: np.ndarray) -> np.ndarray:
        """
        Block A4: Generates a Mel-Spectrogram snapshot (simplified for the contract).
        Real implementations would use Librosa or TorchAudio.
        For now, returns a dummy feature vector to maintain pipeline flow.
        """
        # Placeholder for 128 Mel bands over the chunk
        return np.random.rand(128, 10).astype(np.float32)


@dataclass
class AudioInference:
    """Consolidated result of an acoustic inference turn."""

    transcript: str | None = None
    ambient_label: str | None = None
    confidence: float = 0.0
    is_hotword_detected: bool = False
    timestamp: float = 0.0


class AudioAIProcessor:
    """
    Blocks A5, A6 & A7: AI-driven acoustic understanding.
    Wraps models like Whisper, YAMNet, and KWS (Keyword Spotting).
    """

    def __init__(self):
        self._whisper_model = None
        self._vad = None
        self._yamnet_session = None
        self._yamnet_classes = []
        self._is_initialized = False

    def initialize_models(self) -> None:
        """Loads lightweight ML models if available."""
        if self._is_initialized:
            return
        
        try:
            import whisper
            # Use tiny/base model for real-time LAN pipeline
            self._whisper_model = whisper.load_model("tiny", device="cpu")
        except ImportError:
            import logging
            logging.getLogger(__name__).warning("openai-whisper not installed. STT disabled.")
            
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(2)  # Level 2 aggressiveness
        except ImportError:
            self._vad = None
            
        # Phase 9: A.1.2 YAMNet Integration (ONNX)
        try:
            import onnxruntime as ort
            yamnet_path = os.environ.get("KERNEL_AUDIO_YAMNET_ONNX", "models/yamnet.onnx")
            if os.path.exists(yamnet_path):
                self._yamnet_session = ort.InferenceSession(yamnet_path)
                # Placeholder for YAMNet's 521 classes
                self._yamnet_classes = [f"class_{i}" for i in range(521)]
                _log.info("YAMNet (Acoustic Event Detection) initialized via ONNX.")
            else:
                _log.warning("YAMNet model not found at %s. Ambient detection will use fallback peaks.", yamnet_path)
        except ImportError:
            _log.warning("onnxruntime not found. YAMNet disabled.")
            
        self._is_initialized = True

    def run_inference(self, pcm: np.ndarray, features: np.ndarray) -> AudioInference:
        """Runs the triple-path AI inference on the audio signal."""
        if not self._is_initialized:
            self.initialize_models()
            
        transcript = None
        ambient_label = "calm"
        confidence = 0.9
        is_hotword = False
        
        # 1. Whisper Transcription (STT) 
        # Block A.1.3: Intelligent VAD Segmenter (webrtcvad)
        # only runs if we have 16-bit PCM at 8k, 16k, 32k or 48k.
        # Whisper uses 16k mono.
        needs_transcription = False
        if self._vad is not None:
            try:
                # Convert float32 back to int16 for webrtcvad
                # webrtcvad expects frames of 10, 20, or 30 ms
                # 16000Hz * 0.030s = 480 samples
                pcm_int16 = (pcm * 32768).astype(np.int16)
                # Take a 30ms sample from the middle
                frame = pcm_int16[len(pcm_int16)//2 : len(pcm_int16)//2 + 480].tobytes()
                if self._vad.is_speech(frame, 16000):
                    needs_transcription = True
            except Exception:
                # Fallback to energy if vad fails
                needs_transcription = np.mean(pcm**2) > 0.005
        else:
            needs_transcription = np.mean(pcm**2) > 0.005
        
        if needs_transcription and self._whisper_model is not None:
            start_t = time.time()
            try:
                # Whisper expects float32 from -1 to 1 at 16kHz.
                import torch
                # Suppress FP16 warnings on CPU
                with torch.no_grad():
                    result = self._whisper_model.transcribe(pcm, fp16=False)
                text = result.get("text", "").strip()
                if text:
                    transcript = text
            except Exception as e:
                import logging
                logging.getLogger(__name__).debug("Whisper inference failed: %s", e)
            finally:
                observe_audio_ai_inference_seconds("whisper", time.time() - start_t)

        # 2. Ambient Event Analysis (YAMNet + Fallback)
        # Block A.1.2: Specialized classifier for non-speech sounds
        if self._yamnet_session is not None:
            start_t = time.time()
            try:
                # YAMNet expects float32 [1, waveform_len] at 16kHz
                y_input = pcm.astype(np.float32).reshape(1, -1)
                y_output = self._yamnet_session.run(None, {"input": y_input})[0]
                idx = np.argmax(np.mean(y_output, axis=0))
                ambient_label = self._yamnet_classes[idx]
                confidence = float(np.max(np.mean(y_output, axis=0)))
            except Exception as e:
                _log.debug("YAMNet inference failed: %s", e)
            finally:
                observe_audio_ai_inference_seconds("yamnet", time.time() - start_t)
        else:
            # Fallback for development (peak-based)
            peak = np.max(np.abs(pcm))
            if peak > 0.85:
                ambient_label = "loud_noise_or_shout"
                confidence = 0.85
            elif peak > 0.4:
                ambient_label = "active_environment"
                confidence = 0.70
        
        # 3. Hotword Spotting (KWS Placeholder)
        if transcript and "ethos" in transcript.lower():
            is_hotword = True
            record_audio_ai_hotword_detection()
        
        return AudioInference(
            transcript=transcript,
            ambient_label=ambient_label,
            confidence=confidence,
            is_hotword_detected=is_hotword,
            timestamp=time.time(),
        )

import asyncio

class NomadAudioConsumer:
    """
    Consumes raw PCM streams from the NomadBridge and injects them 
    into the Ethos Kernel's AudioRingBuffer asynchronously.
    """
    def __init__(self, ring_buffer: AudioRingBuffer):
        self.ring_buffer = ring_buffer
        self._task: asyncio.Task | None = None

    def start(self):
        self._task = asyncio.create_task(self._consume_loop())

    async def _consume_loop(self):
        from .nomad_bridge import get_nomad_bridge
        
        bridge = get_nomad_bridge()
        while True:
            try:
                pcm_bytes = await bridge.audio_queue.get()
                
                # We expect float32 PCM data from the smartphone 
                # (matching the interface of simulated_pcm)
                np_pcm = np.frombuffer(pcm_bytes, dtype=np.float32)
                
                # Offload append to not block the current loop
                self.ring_buffer.append(np_pcm)
            except asyncio.CancelledError:
                break
            except Exception as e:
                import logging
                logging.getLogger(__name__).error("Error in NomadAudioConsumer: %s", e)
    async def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None


_nomad_audio_consumer: NomadAudioConsumer | None = None


def get_nomad_audio_consumer_optional() -> NomadAudioConsumer | None:
    """Return the active consumer, if started."""
    return _nomad_audio_consumer


def start_nomad_audio_consumer_from_env(ring_buffer: AudioRingBuffer) -> NomadAudioConsumer | None:
    """
    When ``KERNEL_NOMAD_AUDIO_CONSUMER`` is set, start draining ``NomadBridge.audio_queue``.
    """
    global _nomad_audio_consumer
    from ..kernel_utils import kernel_env_truthy

    if not kernel_env_truthy("KERNEL_NOMAD_AUDIO_CONSUMER"):
        return None
    if _nomad_audio_consumer is not None:
        return _nomad_audio_consumer
    
    _nomad_audio_consumer = NomadAudioConsumer(ring_buffer)
    _nomad_audio_consumer.start()
    import logging
    logging.getLogger(__name__).info("NomadAudioConsumer started (KERNEL_NOMAD_AUDIO_CONSUMER=1).")
    return _nomad_audio_consumer


async def stop_nomad_audio_consumer_async() -> None:
    """Cancel background audio consumption."""
    global _nomad_audio_consumer
    c = _nomad_audio_consumer
    _nomad_audio_consumer = None
    if c is not None:
        await c.stop()
        import logging
        logging.getLogger(__name__).info("NomadAudioConsumer stopped.")


_SHARED_AUDIO_CAPTURE: AudioCaptureInterface | None = None

def get_shared_audio_capture() -> AudioCaptureInterface | None:
    """
    Returns the global shared audio capture interface.
    Initialized only if KERNEL_AUDIO_CAPTURE=1 or if explicitly started.
    """
    global _SHARED_AUDIO_CAPTURE
    from ..kernel_utils import kernel_env_truthy
    
    if _SHARED_AUDIO_CAPTURE is not None:
        return _SHARED_AUDIO_CAPTURE
        
    if kernel_env_truthy("KERNEL_AUDIO_CAPTURE"):
        _SHARED_AUDIO_CAPTURE = AudioCaptureInterface()
        _SHARED_AUDIO_CAPTURE.start()
        import logging
        logging.getLogger(__name__).info("Shared AudioCaptureInterface started.")
        
    return _SHARED_AUDIO_CAPTURE

